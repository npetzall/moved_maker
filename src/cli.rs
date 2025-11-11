use clap::Parser;
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[command(name = "move_maker")]
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
    /// Validate arguments and panic on invalid input
    pub fn validate(&self) {
        // Validate src exists and is a directory
        if !self.src.exists() {
            panic!("Source directory does not exist: {}", self.src.display());
        }
        if !self.src.is_dir() {
            panic!("Source path is not a directory: {}", self.src.display());
        }

        // Validate module_name is non-empty
        if self.module_name.is_empty() {
            panic!("Module name cannot be empty");
        }

        // Validate module_name is a valid Terraform identifier
        // Must start with letter or underscore, followed by alphanumeric, underscore, or hyphen
        let chars: Vec<char> = self.module_name.chars().collect();
        if chars.is_empty() {
            panic!("Module name cannot be empty");
        }

        let first_char = chars[0];
        if !first_char.is_alphabetic() && first_char != '_' {
            panic!(
                "Module name must start with a letter or underscore, got: {}",
                first_char
            );
        }

        for c in chars.iter().skip(1) {
            if !c.is_alphanumeric() && *c != '_' && *c != '-' {
                panic!(
                    "Module name contains invalid character: {}. Only alphanumeric characters, underscores, and hyphens are allowed",
                    c
                );
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
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
    fn test_valid_cli_arguments() {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: "test_module".to_string(),
        };
        args.validate();
    }

    #[test]
    #[should_panic(expected = "Source directory does not exist")]
    fn test_missing_src_argument() {
        let args = Args {
            src: PathBuf::from("/nonexistent/path"),
            module_name: "test_module".to_string(),
        };
        args.validate();
    }

    #[test]
    #[should_panic(expected = "Module name cannot be empty")]
    fn test_missing_module_name_argument() {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: String::new(),
        };
        args.validate();
    }

    #[test]
    #[should_panic(expected = "Source path is not a directory")]
    fn test_non_directory_path() {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("file.txt");
        fs::write(&file_path, "test").unwrap();

        let args = Args {
            src: file_path,
            module_name: "test_module".to_string(),
        };
        args.validate();
    }

    #[test]
    #[should_panic(expected = "Module name must start with a letter or underscore")]
    fn test_module_name_starts_with_number() {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: "123invalid".to_string(),
        };
        args.validate();
    }

    #[test]
    #[should_panic(expected = "Module name contains invalid character")]
    fn test_module_name_with_invalid_characters() {
        let temp_dir = TempDir::new().unwrap();
        let args = Args {
            src: temp_dir.path().to_path_buf(),
            module_name: "test@module".to_string(),
        };
        args.validate();
    }

    #[test]
    fn test_valid_module_name_formats() {
        let temp_dir = TempDir::new().unwrap();
        
        let valid_names = vec!["test_module", "test-module", "test123", "_test", "TestModule"];
        for name in valid_names {
            let args = Args {
                src: temp_dir.path().to_path_buf(),
                module_name: name.to_string(),
            };
            args.validate();
        }
    }
}

