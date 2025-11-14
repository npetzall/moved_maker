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

use anyhow::{Context, Result};
use std::fs;
use std::path::{Path, PathBuf};

/// Find all `.tf` files in the source directory (non-recursive, only direct children)
pub fn find_terraform_files(src: &Path) -> Result<Vec<PathBuf>> {
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

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_find_tf_files_in_directory() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file1 = temp_dir.path().join("main.tf");
        let file2 = temp_dir.path().join("variables.tf");
        fs::write(&file1, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&file2, "variable \"test\" {}").unwrap();

        let files = find_terraform_files(temp_dir.path())?;
        assert_eq!(files.len(), 2);
        assert!(files.contains(&file1));
        assert!(files.contains(&file2));
        Ok(())
    }

    #[test]
    fn test_file_discovery_error_on_fatal_errors() {
        let result = find_terraform_files(Path::new("/nonexistent/directory"));
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Failed to read directory"));
    }

    #[test]
    fn test_ignore_non_tf_files() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let tf_file = temp_dir.path().join("main.tf");
        let txt_file = temp_dir.path().join("readme.txt");
        fs::write(&tf_file, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&txt_file, "some text").unwrap();

        let files = find_terraform_files(temp_dir.path())?;
        assert_eq!(files.len(), 1);
        assert_eq!(files[0], tf_file);
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

        let files = find_terraform_files(temp_dir.path())?;
        assert_eq!(files.len(), 1);
        assert_eq!(files[0], file1);
        Ok(())
    }

    #[test]
    fn test_empty_directory() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let files = find_terraform_files(temp_dir.path())?;
        assert_eq!(files.len(), 0);
        Ok(())
    }

    #[test]
    fn test_directory_with_no_tf_files() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let txt_file = temp_dir.path().join("readme.txt");
        fs::write(&txt_file, "some text").unwrap();

        let files = find_terraform_files(temp_dir.path())?;
        assert_eq!(files.len(), 0);
        Ok(())
    }
}
