use std::fs;
use std::path::{Path, PathBuf};

/// Find all `.tf` files in the source directory (non-recursive, only direct children)
pub fn find_terraform_files(src: &Path) -> Vec<PathBuf> {
    let mut files = Vec::new();

    let entries = fs::read_dir(src).unwrap_or_else(|e| {
        panic!("Failed to read directory {}: {}", src.display(), e);
    });

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
        if let Some(ext) = path.extension() {
            if ext == "tf" {
                files.push(path);
            }
        }
    }

    files
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_find_tf_files_in_directory() {
        let temp_dir = TempDir::new().unwrap();
        let file1 = temp_dir.path().join("main.tf");
        let file2 = temp_dir.path().join("variables.tf");
        fs::write(&file1, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&file2, "variable \"test\" {}").unwrap();

        let files = find_terraform_files(temp_dir.path());
        assert_eq!(files.len(), 2);
        assert!(files.contains(&file1));
        assert!(files.contains(&file2));
    }

    #[test]
    #[should_panic(expected = "Failed to read directory")]
    fn test_file_discovery_panic_on_fatal_errors() {
        find_terraform_files(Path::new("/nonexistent/directory"));
    }

    #[test]
    fn test_ignore_non_tf_files() {
        let temp_dir = TempDir::new().unwrap();
        let tf_file = temp_dir.path().join("main.tf");
        let txt_file = temp_dir.path().join("readme.txt");
        fs::write(&tf_file, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&txt_file, "some text").unwrap();

        let files = find_terraform_files(temp_dir.path());
        assert_eq!(files.len(), 1);
        assert_eq!(files[0], tf_file);
    }

    #[test]
    fn test_ignore_subdirectories() {
        let temp_dir = TempDir::new().unwrap();
        let file1 = temp_dir.path().join("main.tf");
        let subdir = temp_dir.path().join("subdir");
        fs::create_dir(&subdir).unwrap();
        let file2 = subdir.join("nested.tf");
        fs::write(&file1, "resource \"aws_instance\" \"test\" {}").unwrap();
        fs::write(&file2, "resource \"aws_s3_bucket\" \"test\" {}").unwrap();

        let files = find_terraform_files(temp_dir.path());
        assert_eq!(files.len(), 1);
        assert_eq!(files[0], file1);
    }

    #[test]
    fn test_empty_directory() {
        let temp_dir = TempDir::new().unwrap();
        let files = find_terraform_files(temp_dir.path());
        assert_eq!(files.len(), 0);
    }

    #[test]
    fn test_directory_with_no_tf_files() {
        let temp_dir = TempDir::new().unwrap();
        let txt_file = temp_dir.path().join("readme.txt");
        fs::write(&txt_file, "some text").unwrap();

        let files = find_terraform_files(temp_dir.path());
        assert_eq!(files.len(), 0);
    }
}

