// Copyright 2025 Nils Petzall
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//! Processing pipeline from files to moved blocks.
//!
//! This module provides iterator adapters and a builder that orchestrate
//! the transformation from Terraform files to moved blocks.

use crate::moved_block::MovedBlock;
use crate::parser::parse_terraform_file;
use crate::terraform_files::TerraformFiles;
use anyhow::Result;
use hcl::edit::structure::{Block, Body};
use std::path::PathBuf;

/// Adapter that converts file results to parsed bodies
/// Owns TerraformFiles
pub struct ParsedFiles {
    files: Box<dyn Iterator<Item = Result<PathBuf>>>,
}

impl ParsedFiles {
    pub fn new(files: TerraformFiles) -> Self {
        Self {
            files: Box::new(files.into_iter()),
        }
    }
}

impl Iterator for ParsedFiles {
    type Item = Result<(PathBuf, Body)>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let file_result = self.files.next()?;

            let file = match file_result {
                Ok(f) => f,
                Err(e) => {
                    eprintln!("Warning: Failed to discover file: {}", e);
                    continue; // Skip this file and try next
                }
            };

            match parse_terraform_file(&file) {
                Ok(body) => return Some(Ok((file, body))),
                Err(e) => {
                    eprintln!("Warning: Failed to parse {}: {}", file.display(), e);
                    continue; // Skip this file and try next
                }
            }
        }
    }
}

/// Adapter that converts blocks to MovedBlocks, managing body iteration internally
/// Owns ParsedFiles
pub struct MovedBlocks {
    parsed: ParsedFiles,
    module_name: String,
    current_file: Option<PathBuf>,
    current_body: Option<Body>, // Keeps body alive for block references
    current_blocks: Vec<Block>, // Store blocks as owned values to avoid lifetime issues
    current_block_index: usize,
}

impl MovedBlocks {
    pub fn new(parsed: ParsedFiles, module_name: String) -> Self {
        Self {
            parsed,
            module_name,
            current_file: None,
            current_body: None,
            current_blocks: Vec::new(),
            current_block_index: 0,
        }
    }

    /// Load blocks from the next body into current_blocks vector
    /// Sets up iteration over all blocks (filtering happens in Iterator::next())
    fn load_next_body(&mut self) -> bool {
        loop {
            match self.parsed.next() {
                Some(Ok((file_path, body))) => {
                    self.current_file = Some(file_path);
                    self.current_body = Some(body); // Store body to keep it alive
                    // Collect blocks into a vector (cloning them)
                    self.current_blocks = self
                        .current_body
                        .as_ref()
                        .unwrap()
                        .blocks()
                        .cloned()
                        .collect();
                    self.current_block_index = 0;
                    return true;
                }
                Some(Err(e)) => {
                    eprintln!("Warning: {}", e);
                    continue; // Try next file instead of recursing
                }
                None => {
                    return false;
                }
            }
        }
    }
}

impl Iterator for MovedBlocks {
    type Item = Result<MovedBlock>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            // If we have current blocks, try to get next one
            while self.current_block_index < self.current_blocks.len() {
                let block = &self.current_blocks[self.current_block_index];
                self.current_block_index += 1;

                let file_path = self
                    .current_file
                    .as_ref()
                    .expect("file_path should be set when blocks exist");

                match MovedBlock::from_block(block, file_path, &self.module_name) {
                    None => continue, // Unsupported block type, skip silently
                    Some(Ok(moved_block)) => return Some(Ok(moved_block)),
                    Some(Err(e)) => {
                        eprintln!("Warning: {}", e);
                        continue; // Invalid block, warn and skip
                    }
                }
            }

            // Current blocks exhausted, clear and load next body
            self.current_file = None;
            self.current_body = None;
            self.current_blocks.clear();
            self.current_block_index = 0;

            // Load next body
            if !self.load_next_body() {
                return None; // No more bodies
            }
        }
    }
}

/// Main builder that composes the pipeline
pub struct MovedBlockBuilder {
    src: PathBuf,
    module_name: String,
}

impl MovedBlockBuilder {
    pub fn new(src: PathBuf, module_name: String) -> Self {
        Self { src, module_name }
    }

    pub fn moved_blocks(self) -> MovedBlocks {
        let files = TerraformFiles::new(self.src);
        let parsed = ParsedFiles::new(files);
        MovedBlocks::new(parsed, self.module_name)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::Result;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_moved_block_builder_new() {
        let path = std::path::PathBuf::from("/tmp");
        let builder = MovedBlockBuilder::new(path, "test".to_string());
        // Just verify it can be constructed
        drop(builder);
    }

    #[test]
    fn test_moved_block_builder_moved_blocks() -> Result<()> {
        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web" {}
resource "aws_s3_bucket" "data" {}
"#,
        )?;

        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "compute".to_string());
        let mut moved_blocks = builder.moved_blocks();
        let first = moved_blocks.next().expect("Expected first block")?;
        let second = moved_blocks.next().expect("Expected second block")?;
        assert!(moved_blocks.next().is_none());
        drop(first);
        drop(second);
        Ok(())
    }

    #[test]
    fn test_moved_blocks_empty_dir() -> Result<()> {
        let temp_dir = TempDir::new()?;
        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "compute".to_string());
        let mut moved_blocks = builder.moved_blocks();
        assert!(moved_blocks.next().is_none());
        Ok(())
    }

    #[test]
    fn test_moved_blocks_single_resource() -> Result<()> {
        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"resource "aws_instance" "web" {}"#)?;

        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "compute".to_string());
        let mut moved_blocks = builder.moved_blocks();
        let moved_block = moved_blocks.next().expect("Expected a block")?;
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        assert!(moved_blocks.next().is_none());
        Ok(())
    }

    #[test]
    fn test_moved_blocks_single_module() -> Result<()> {
        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"module "web_server" {}"#)?;

        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "a".to_string());
        let mut moved_blocks = builder.moved_blocks();
        let moved_block = moved_blocks.next().expect("Expected a block")?;
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        assert!(moved_blocks.next().is_none());
        Ok(())
    }

    #[test]
    fn test_moved_blocks_mixed() -> Result<()> {
        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web" {}
module "web_server" {}
resource "aws_s3_bucket" "data" {}
"#,
        )?;

        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "compute".to_string());
        let moved_blocks = builder.moved_blocks();
        let count = moved_blocks.count();
        assert_eq!(count, 3);
        Ok(())
    }
}
