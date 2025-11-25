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

use anyhow::Result;
use clap::Parser;
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[command(name = "moved_maker")]
#[command(about = "Generate moved blocks for Terraform resources and data sources")]
pub struct Args {
    /// Source directory containing Terraform files
    #[arg(long)]
    pub src: PathBuf,

    /// Name of the module to move resources/data into
    #[arg(long)]
    pub module_name: String,
}

impl Args {
    /// Validate arguments and return error on invalid input
    pub fn validate(&self) -> Result<()> {
        // Validate src exists and is a directory
        if !self.src.exists() {
            anyhow::bail!("Source directory does not exist: {}", self.src.display());
        }
        if !self.src.is_dir() {
            anyhow::bail!("Source path is not a directory: {}", self.src.display());
        }

        // Validate module_name is non-empty
        if self.module_name.is_empty() {
            anyhow::bail!("Module name cannot be empty");
        }

        // Validate module_name is a valid Terraform identifier
        // Must start with letter or underscore, followed by alphanumeric, underscore, or hyphen
        let chars: Vec<char> = self.module_name.chars().collect();
        if chars.is_empty() {
            anyhow::bail!("Module name cannot be empty");
        }

        let first_char = chars[0];
        if !first_char.is_alphabetic() && first_char != '_' {
            anyhow::bail!(
                "Module name must start with a letter or underscore, got: {}",
                first_char
            );
        }

        for c in chars.iter().skip(1) {
            if !c.is_alphanumeric() && *c != '_' && *c != '-' {
                anyhow::bail!(
                    "Module name contains invalid character: {}. Only alphanumeric characters, underscores, and hyphens are allowed",
                    c
                );
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_args_struct_creation() {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: "test_module".to_string(),
        };
        assert_eq!(args.module_name, "test_module");
    }

    #[test]
    fn test_valid_cli_arguments() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: "test_module".to_string(),
        };
        args.validate()?;
        Ok(())
    }

    #[test]
    fn test_missing_src_argument() {
        let args = Args {
            src: PathBuf::from("/nonexistent/path"),
            module_name: "test_module".to_string(),
        };
        let result = args.validate();
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Source directory does not exist"));
    }

    #[test]
    fn test_missing_module_name_argument() {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: String::new(),
        };
        let result = args.validate();
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Module name cannot be empty"));
    }

    #[test]
    fn test_non_directory_path() {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("file.txt");
        fs::write(&file_path, "test").unwrap();

        let args = Args {
            src: file_path,
            module_name: "test_module".to_string(),
        };
        let result = args.validate();
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Source path is not a directory"));
    }

    #[test]
    fn test_module_name_starts_with_number() {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: "123invalid".to_string(),
        };
        let result = args.validate();
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Module name must start with a letter or underscore"));
    }

    #[test]
    fn test_module_name_with_invalid_characters() {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: "test@module".to_string(),
        };
        let result = args.validate();
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Module name contains invalid character"));
    }

    #[test]
    fn test_valid_module_name_formats() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();

        let valid_names = vec![
            "test_module",
            "test-module",
            "test123",
            "_test",
            "TestModule",
        ];
        for name in valid_names {
            let args = Args {
                src: temp_dir.path().to_path_buf(),
                module_name: name.to_string(),
            };
            args.validate()?;
        }
        Ok(())
    }
}
