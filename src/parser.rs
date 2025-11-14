use anyhow::{Context, Result};
use hcl::edit::parser::parse_body;
use hcl::edit::structure::Body;
use std::fs;
use std::path::Path;

/// Parse a Terraform file and return the HCL Body structure
pub fn parse_terraform_file(path: &Path) -> Result<Body> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path.display()))?;

    parse_body(&content).with_context(|| format!("Failed to parse HCL file: {}", path.display()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_parse_valid_terraform_file() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, "resource \"aws_instance\" \"test\" {}").unwrap();

        let result = parse_terraform_file(&file);
        assert!(result.is_ok());
        let body = result.unwrap();
        assert_eq!(body.blocks().count(), 1);
    }

    #[test]
    fn test_parse_file_with_resource_block() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web" {
  ami = "ami-12345"
}
"#,
        )
        .unwrap();

        let result = parse_terraform_file(&file);
        assert!(result.is_ok());
        let body = result.unwrap();
        let blocks: Vec<_> = body.blocks().collect();
        assert_eq!(blocks.len(), 1);
        assert_eq!(blocks[0].ident.value().to_string(), "resource");
    }

    #[test]
    fn test_parse_file_with_data_block() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("data.tf");
        fs::write(
            &file,
            r#"
data "aws_ami" "example" {
  most_recent = true
}
"#,
        )
        .unwrap();

        let result = parse_terraform_file(&file);
        assert!(result.is_ok());
        let body = result.unwrap();
        let blocks: Vec<_> = body.blocks().collect();
        assert_eq!(blocks.len(), 1);
        assert_eq!(blocks[0].ident.value().to_string(), "data");
    }

    #[test]
    fn test_handle_invalid_hcl_syntax() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("invalid.tf");
        fs::write(
            &file,
            "resource \"aws_instance\" \"test\" { invalid syntax }",
        )
        .unwrap();

        let result = parse_terraform_file(&file);
        assert!(result.is_err());
    }

    #[test]
    fn test_handle_empty_file() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("empty.tf");
        fs::write(&file, "").unwrap();

        let result = parse_terraform_file(&file);
        assert!(result.is_ok());
        let body = result.unwrap();
        assert_eq!(body.blocks().count(), 0);
    }

    #[test]
    fn test_handle_file_with_only_comments() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("comments.tf");
        fs::write(&file, "# This is a comment\n# Another comment").unwrap();

        let result = parse_terraform_file(&file);
        assert!(result.is_ok());
        let body = result.unwrap();
        assert_eq!(body.blocks().count(), 0);
    }
}
