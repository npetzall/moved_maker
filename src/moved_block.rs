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

//! Enum wrapper for moved blocks.
//!
//! `MovedBlock` provides a unified interface for different types of moved blocks
//! (resources, modules, etc.) and includes a factory method for creating instances
//! from HCL blocks.

use crate::moved_module::MovedModule;
use crate::moved_resource::MovedResource;
use crate::to_moved_block::ToMovedBlock;
use anyhow::Result;
use hcl::edit::structure::Block;
use std::path::Path;

/// Enum wrapper for moved blocks (Resource or Module)
///
/// This enum does not implement the `ToMovedBlock` trait because no code requires it as a trait bound.
/// The `from_block()` method encapsulates the logic for creating a `MovedBlock` from an HCL `Block`,
/// making it reusable and keeping the creation logic in one place.
#[derive(Debug, Clone)]
pub enum MovedBlock {
    Resource(MovedResource),
    Module(MovedModule),
}

impl MovedBlock {
    /// Create a `MovedBlock` from an HCL Block
    ///
    /// Determines the block type from the block's identifier and creates
    /// the appropriate variant (Resource or Module)
    ///
    /// Returns:
    /// - `None` if the block type is not supported (resource/module) - should be skipped silently
    /// - `Some(Ok(MovedBlock))` if successfully converted
    /// - `Some(Err(e))` if supported type but conversion failed (e.g., invalid labels)
    pub fn from_block(block: &Block, file_path: &Path, module_name: &str) -> Option<Result<Self>> {
        let ident = block.ident.value().to_string();
        let labels: Vec<String> = block
            .labels
            .iter()
            .map(|l| l.as_str().to_string())
            .collect();

        match ident.as_str() {
            "resource" => {
                if labels.len() < 2 {
                    return Some(Err(anyhow::anyhow!(
                        "Resource block in {} has fewer than 2 labels",
                        file_path.display()
                    )));
                }
                Some(
                    MovedResource::new(labels, file_path.to_path_buf(), module_name.to_string())
                        .map(Self::Resource),
                )
            }
            "module" => {
                if labels.is_empty() {
                    return Some(Err(anyhow::anyhow!(
                        "Module block in {} has no labels",
                        file_path.display()
                    )));
                }
                Some(
                    MovedModule::new(labels, file_path.to_path_buf(), module_name.to_string())
                        .map(Self::Module),
                )
            }
            _ => None, // Unsupported block type, skip silently
        }
    }

    /// Convert to HCL Block by delegating to the inner type
    pub fn to_block(&self) -> Result<Block> {
        match self {
            MovedBlock::Resource(r) => r.to_block(),
            MovedBlock::Module(m) => m.to_block(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::moved_module::MovedModule;
    use crate::moved_resource::MovedResource;
    use anyhow::Result;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_moved_block_resource_variant() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let moved_block = MovedBlock::Resource(resource);
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_moved_block_module_variant() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let moved_block = MovedBlock::Module(module);
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_resource() -> Result<()> {
        use crate::parser::parse_terraform_file;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"resource "aws_instance" "web" {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "compute");
        assert!(result.is_some());
        let moved_block = result.unwrap()?;

        match moved_block {
            MovedBlock::Resource(r) => {
                assert_eq!(r.resource_type(), "aws_instance");
                assert_eq!(r.resource_name(), "web");
            }
            _ => panic!("Expected Resource variant"),
        }
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_module() -> Result<()> {
        use crate::parser::parse_terraform_file;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"module "web_server" {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "a");
        assert!(result.is_some());
        let moved_block = result.unwrap()?;

        match moved_block {
            MovedBlock::Module(m) => {
                assert_eq!(m.module_name_local(), "web_server");
            }
            _ => panic!("Expected Module variant"),
        }
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_invalid_resource() -> Result<()> {
        use crate::parser::parse_terraform_file;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"resource "aws_instance" {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "compute");
        assert!(result.is_some());
        assert!(result.unwrap().is_err()); // Should return Some(Err)
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_invalid_module() -> Result<()> {
        use crate::parser::parse_terraform_file;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"module {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "a");
        assert!(result.is_some());
        assert!(result.unwrap().is_err()); // Should return Some(Err)
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_unsupported_type() -> Result<()> {
        use crate::parser::parse_terraform_file;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"variable "test" {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "compute");
        assert!(result.is_none()); // Unsupported type should return None
        Ok(())
    }

    #[test]
    fn test_moved_block_to_block_resource() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let moved_block = MovedBlock::Resource(resource);
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_moved_block_to_block_module() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let moved_block = MovedBlock::Module(module);
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        Ok(())
    }
}
