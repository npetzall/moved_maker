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
use hcl::edit::Decorate;
use hcl::edit::Ident;
use hcl::edit::expr::Expression;
use hcl::edit::parser::parse_body;
use hcl::edit::structure::Body;
use hcl::edit::structure::{Attribute, Block};
use std::path::Path;

/// Extract resource blocks from a parsed Body
pub fn extract_blocks(body: &Body) -> Vec<&Block> {
    body.blocks()
        .filter(|block| {
            let ident = block.ident.value().to_string();
            ident == "resource"
        })
        .collect()
}

/// Build a "from" expression for a resource block
pub fn build_from_expression(resource_type: &str, resource_name: &str) -> Result<Expression> {
    let expr_str = format!("{}.{}", resource_type, resource_name);
    // Parse the expression string to get an Expression
    // Wrap in a simple attribute to parse it
    let attr_str = format!("x = {}", expr_str);
    let body = parse_body(&attr_str)
        .with_context(|| format!("Failed to parse expression: {}", expr_str))?;
    // Extract the expression from the attribute
    let attr = body
        .attributes()
        .next()
        .context("Expected attribute in parsed body")?;
    Ok(attr.value.clone())
}

/// Build a "to" expression for a module path
pub fn build_to_expression(
    module_name: &str,
    resource_type: &str,
    resource_name: &str,
) -> Result<Expression> {
    let expr_str = format!("module.{}.{}.{}", module_name, resource_type, resource_name);
    // Parse the expression string to get an Expression
    // Wrap in a simple attribute to parse it
    let attr_str = format!("x = {}", expr_str);
    let body = parse_body(&attr_str)
        .with_context(|| format!("Failed to parse expression: {}", expr_str))?;
    // Extract the expression from the attribute
    let attr = body
        .attributes()
        .next()
        .context("Expected attribute in parsed body")?;
    Ok(attr.value.clone())
}

/// Build a moved block for a resource
pub fn build_resource_moved_block(
    resource_type: &str,
    resource_name: &str,
    module_name: &str,
    path: &Path,
) -> Result<Block> {
    // Create attributes with indentation
    let mut from_attr = Attribute::new(
        Ident::new("from"),
        build_from_expression(resource_type, resource_name)?,
    );
    from_attr.decor_mut().set_prefix("  ");

    let mut to_attr = Attribute::new(
        Ident::new("to"),
        build_to_expression(module_name, resource_type, resource_name)?,
    );
    to_attr.decor_mut().set_prefix("  ");

    let mut block = Block::builder(Ident::new("moved"))
        .attribute(from_attr)
        .attribute(to_attr)
        .build();

    // Add comment with filename
    let filename = path
        .file_name()
        .with_context(|| format!("Path must have filename: {}", path.display()))?
        .to_string_lossy();
    let comment = format!("# From: {}\n", filename);
    block.decor_mut().set_prefix(comment.as_str());

    Ok(block)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser::parse_terraform_file;
    use pretty_assertions::assert_eq;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_extract_resource_blocks() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web" {}
resource "aws_s3_bucket" "data" {}
variable "test" {}
"#,
        )
        .unwrap();

        let body = parse_terraform_file(&file).unwrap();
        let blocks = extract_blocks(&body);
        assert_eq!(blocks.len(), 2);
        assert!(
            blocks
                .iter()
                .all(|b| b.ident.value().to_string() == "resource")
        );
    }

    #[test]
    fn test_ignore_other_block_types() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
variable "test" {}
locals {
  x = 1
}
"#,
        )
        .unwrap();

        let body = parse_terraform_file(&file).unwrap();
        let blocks = extract_blocks(&body);
        assert_eq!(blocks.len(), 0);
    }

    #[test]
    fn test_extract_from_mixed_blocks() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web" {}
data "aws_ami" "example" {}
variable "test" {}
locals {
  x = 1
}
"#,
        )
        .unwrap();

        let body = parse_terraform_file(&file).unwrap();
        let blocks = extract_blocks(&body);
        assert_eq!(blocks.len(), 1);
        assert_eq!(blocks[0].ident.value().to_string(), "resource");
    }

    #[test]
    fn test_build_from_expression_resource() -> Result<()> {
        let expr = build_from_expression("aws_instance", "web")?;
        // We can't easily test the internal structure, but we can verify it's an Expression
        // The actual format will be verified in integration tests
        assert!(matches!(expr, Expression::Traversal(_)));
        Ok(())
    }

    #[test]
    fn test_build_to_expression_resource() -> Result<()> {
        let expr = build_to_expression("compute", "aws_instance", "web")?;
        assert!(matches!(expr, Expression::Traversal(_)));
        Ok(())
    }

    #[test]
    fn test_build_resource_moved_block() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        let block = build_resource_moved_block("aws_instance", "web", "compute", &file)?;

        assert_eq!(block.ident.value().to_string(), "moved");
        assert!(
            block
                .decor()
                .prefix()
                .unwrap_or(&"".into())
                .contains("From: main.tf")
        );
        Ok(())
    }

    #[test]
    fn test_filename_extraction() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("test.tf");
        let block = build_resource_moved_block("aws_instance", "web", "compute", &file)?;

        assert!(
            block
                .decor()
                .prefix()
                .unwrap_or(&"".into())
                .contains("From: test.tf")
        );
        Ok(())
    }

    #[test]
    fn test_filename_extraction_error() {
        let path = Path::new("/");
        let result = build_resource_moved_block("aws_instance", "web", "compute", path);
        assert!(result.is_err());
        let error_msg = result.unwrap_err().to_string();
        assert!(error_msg.contains("Path must have filename"));
    }

    #[test]
    fn test_extract_labels_from_resource_block() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"resource "aws_instance" "web" {}"#).unwrap();

        let body = parse_terraform_file(&file).unwrap();
        let blocks = extract_blocks(&body);
        assert_eq!(blocks.len(), 1);

        let block = blocks[0];
        let labels: Vec<_> = block.labels.iter().collect();
        assert_eq!(labels.len(), 2);
        assert_eq!(labels[0].to_string(), "aws_instance");
        assert_eq!(labels[1].to_string(), "web");
    }

    #[test]
    fn test_handle_multiple_blocks_in_one_file() {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web1" {}
resource "aws_instance" "web2" {}
resource "aws_s3_bucket" "data" {}
"#,
        )
        .unwrap();

        let body = parse_terraform_file(&file).unwrap();
        let blocks = extract_blocks(&body);
        assert_eq!(blocks.len(), 3);
    }

    #[test]
    fn test_resource_with_count_meta_argument() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web" {
  count = 3
  ami = "ami-12345"
}
"#,
        )
        .unwrap();

        let body = parse_terraform_file(&file)?;
        let blocks = extract_blocks(&body);
        assert_eq!(blocks.len(), 1);

        // Count doesn't affect the address, should still be processable
        let block = blocks[0];
        let labels: Vec<_> = block.labels.iter().collect();
        assert_eq!(labels.len(), 2);
        assert_eq!(labels[0].to_string(), "aws_instance");
        assert_eq!(labels[1].to_string(), "web");

        // Should be able to build moved block
        let moved_block = build_resource_moved_block("aws_instance", "web", "compute", &file)?;
        assert_eq!(moved_block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_resource_with_for_each_meta_argument() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web" {
  for_each = {
    "web1" = "ami-12345"
    "web2" = "ami-67890"
  }
  ami = each.value
}
"#,
        )
        .unwrap();

        let body = parse_terraform_file(&file)?;
        let blocks = extract_blocks(&body);
        assert_eq!(blocks.len(), 1);

        // for_each doesn't affect the address, should still be processable
        let block = blocks[0];
        let labels: Vec<_> = block.labels.iter().collect();
        assert_eq!(labels.len(), 2);
        assert_eq!(labels[0].to_string(), "aws_instance");
        assert_eq!(labels[1].to_string(), "web");

        // Should be able to build moved block
        let moved_block = build_resource_moved_block("aws_instance", "web", "compute", &file)?;
        assert_eq!(moved_block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_resource_moved_block_has_indented_attributes() -> Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file = temp_dir.path().join("main.tf");
        let block = build_resource_moved_block("aws_instance", "web", "compute", &file)?;

        // Convert block to string via Body
        let body = Body::builder().block(block).build();
        let output = body.to_string();

        // Assert output contains indented attributes
        assert!(
            output.contains("  from"),
            "from attribute should be indented with 2 spaces"
        );
        assert!(
            output.contains("  to"),
            "to attribute should be indented with 2 spaces"
        );

        // Assert comment is preserved
        assert!(
            output.contains("# From: main.tf"),
            "Comment should be preserved"
        );

        // Verify the structure
        assert!(output.contains("moved {"));
        assert!(output.contains("from = aws_instance.web"));
        assert!(output.contains("to = module.compute.aws_instance.web"));
        Ok(())
    }
}
