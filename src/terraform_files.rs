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

//! Terraform file discovery.
//!
//! `TerraformFiles` encapsulates the logic for finding and iterating over
//! Terraform files in a directory. File discovery is a private implementation
//! detail - external code uses `TerraformFiles::new()` and `into_iter()`.

use anyhow::{Context, Result};
use std::fs;
use std::path::{Path, PathBuf};

/// Encapsulates Terraform file discovery and iteration
pub struct TerraformFiles {
    src: PathBuf,
}

impl TerraformFiles {
    /// Create a new TerraformFiles instance for the given directory
    pub fn new(src: PathBuf) -> Self {
        Self { src }
    }

    /// Convert into an iterator over discovered Terraform files
    pub fn into_iter(self) -> impl Iterator<Item = Result<PathBuf>> {
        match Self::find_terraform_files(&self.src) {
            Ok(files) => files.into_iter().map(Ok).collect::<Vec<_>>().into_iter(),
            Err(e) => vec![Err(e)].into_iter(),
        }
    }

    /// Find all `.tf` files in the source directory (non-recursive, only direct children)
    ///
    /// This is a private method - file discovery is an implementation detail
    /// of the TerraformFiles struct.
    fn find_terraform_files(src: &Path) -> Result<Vec<PathBuf>> {
        let mut files = Vec::new();

        let entries = fs::read_dir(src)
            .with_context(|| format!("Failed to read directory: {}", src.display()))?;

        for entry in entries {
            let entry = match entry {
                Ok(entry) => entry,
                Err(e) => {
                    eprintln!("Warning: Failed to read directory entry: {}", e);
                    continue;
                }
            };

            let path = entry.path();

            // Only process files, not directories
            if !path.is_file() {
                continue;
            }

            // Check if file has .tf extension
            if let Some(ext) = path.extension()
                && ext == "tf"
            {
                files.push(path);
            }
        }

        Ok(files)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_terraform_files_new() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let tf_files = TerraformFiles::new(temp_dir.path().to_path_buf());
        assert_eq!(tf_files.src, temp_dir.path());
        Ok(())
    }

    #[test]
    fn test_terraform_files_into_iter() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file1 = temp_dir.path().join("main.tf");
        let file2 = temp_dir.path().join("variables.tf");
        fs::write(&file1, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&file2, "variable \"test\" {}").unwrap();

        let tf_files = TerraformFiles::new(temp_dir.path().to_path_buf());
        let files: Vec<Result<PathBuf>> = tf_files.into_iter().collect();
        assert_eq!(files.len(), 2);
        let paths: Vec<PathBuf> = files.into_iter().map(|r| r.unwrap()).collect();
        assert!(paths.contains(&file1));
        assert!(paths.contains(&file2));
        Ok(())
    }

    #[test]
    fn test_find_tf_files_in_directory() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file1 = temp_dir.path().join("main.tf");
        let file2 = temp_dir.path().join("variables.tf");
        fs::write(&file1, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&file2, "variable \"test\" {}").unwrap();

        // Test via TerraformFiles::new() and into_iter()
        let tf_files = TerraformFiles::new(temp_dir.path().to_path_buf());
        let files: Vec<Result<PathBuf>> = tf_files.into_iter().collect();
        assert_eq!(files.len(), 2);
        let paths: Vec<PathBuf> = files.into_iter().map(|r| r.unwrap()).collect();
        assert!(paths.contains(&file1));
        assert!(paths.contains(&file2));
        Ok(())
    }

    #[test]
    fn test_file_discovery_error_on_fatal_errors() {
        // TerraformFiles::new() doesn't fail - errors happen during iteration
        let tf_files = TerraformFiles::new(Path::new("/nonexistent/directory").to_path_buf());
        let mut iter = tf_files.into_iter();
        let result = iter.next();
        assert!(result.is_some());
        let err_result = result.unwrap();
        assert!(err_result.is_err());
        let error_msg = err_result.unwrap_err().to_string();
        assert!(error_msg.contains("Failed to read directory"));
    }

    #[test]
    fn test_ignore_non_tf_files() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let tf_file = temp_dir.path().join("main.tf");
        let txt_file = temp_dir.path().join("readme.txt");
        fs::write(&tf_file, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&txt_file, "some text").unwrap();

        let tf_files = TerraformFiles::new(temp_dir.path().to_path_buf());
        let files: Vec<Result<PathBuf>> = tf_files.into_iter().collect();
        assert_eq!(files.len(), 1);
        assert_eq!(files[0].as_ref().unwrap(), &tf_file);
        Ok(())
    }

    #[test]
    fn test_ignore_subdirectories() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file1 = temp_dir.path().join("main.tf");
        let subdir = temp_dir.path().join("subdir");
        fs::create_dir(&subdir).unwrap();
        let file2 = subdir.join("nested.tf");
        fs::write(&file1, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&file2, "resource \"aws_s3_bucket\" \"test\" {}").unwrap();

        let tf_files = TerraformFiles::new(temp_dir.path().to_path_buf());
        let files: Vec<Result<PathBuf>> = tf_files.into_iter().collect();
        assert_eq!(files.len(), 1);
        assert_eq!(files[0].as_ref().unwrap(), &file1);
        Ok(())
    }

    #[test]
    fn test_empty_directory() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let tf_files = TerraformFiles::new(temp_dir.path().to_path_buf());
        let files: Vec<Result<PathBuf>> = tf_files.into_iter().collect();
        assert_eq!(files.len(), 0);
        Ok(())
    }

    #[test]
    fn test_directory_with_no_tf_files() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let txt_file = temp_dir.path().join("readme.txt");
        fs::write(&txt_file, "some text").unwrap();

        let tf_files = TerraformFiles::new(temp_dir.path().to_path_buf());
        let files: Vec<Result<PathBuf>> = tf_files.into_iter().collect();
        assert_eq!(files.len(), 0);
        Ok(())
    }
}
