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

//! Resource block model for moved blocks.
//!
//! `MovedResource` encapsulates all logic related to resource blocks,
//! including validation, expression building, and block conversion.

use crate::address::AddressBuilder;
use crate::to_moved_block::ToMovedBlock;
use anyhow::Result;
use hcl::edit::expr::Expression;
use std::path::{Path, PathBuf};

/// Represents a resource block that needs to be moved to a module
#[derive(Debug, Clone)]
pub struct MovedResource {
    labels: Vec<String>,
    file_path: PathBuf,
    target_module_name: String,
}

impl MovedResource {
    /// Create a new MovedResource
    ///
    /// # Arguments
    /// * `labels` - All labels from the block (must have at least 2 for resources)
    /// * `file_path` - Source file path (for comment)
    /// * `target_module_name` - Target module name
    pub fn new(
        labels: Vec<String>,
        file_path: PathBuf,
        target_module_name: String,
    ) -> Result<Self> {
        if labels.len() < 2 {
            return Err(anyhow::anyhow!(
                "Resource blocks must have at least 2 labels"
            ));
        }
        Ok(Self {
            labels,
            file_path,
            target_module_name,
        })
    }

    /// Access all labels
    #[allow(dead_code)] // Used in tests
    pub fn labels(&self) -> &[String] {
        &self.labels
    }

    /// Convenience accessor for resource type (labels[0])
    #[allow(dead_code)] // Used in tests
    pub fn resource_type(&self) -> &str {
        &self.labels[0]
    }

    /// Convenience accessor for resource name (labels[1])
    #[allow(dead_code)] // Used in tests
    pub fn resource_name(&self) -> &str {
        &self.labels[1]
    }

    /// Build the "from" expression (private method)
    fn build_from_expression(&self) -> Expression {
        AddressBuilder::new().build(&[&self.labels[0], &self.labels[1]])
    }

    /// Build the "to" expression (private method)
    fn build_to_expression(&self) -> Expression {
        AddressBuilder::new().build(&[
            "module",
            &self.target_module_name,
            &self.labels[0],
            &self.labels[1],
        ])
    }
}

impl ToMovedBlock for MovedResource {
    fn from_expression(&self) -> Expression {
        self.build_from_expression()
    }

    fn to_expression(&self) -> Expression {
        self.build_to_expression()
    }

    fn file_path(&self) -> &Path {
        &self.file_path
    }

    // to_block() uses the default implementation from the trait
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::Result;
    use hcl::edit::Decorate;
    use hcl::edit::structure::Body;
    use pretty_assertions::assert_eq;

    #[test]
    fn test_moved_resource_new() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels.clone(), path, "compute".to_string())?;
        assert_eq!(resource.labels(), &labels);
        assert_eq!(resource.resource_type(), "aws_instance");
        assert_eq!(resource.resource_name(), "web");
        Ok(())
    }

    #[test]
    fn test_moved_resource_new_invalid_labels() {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string()]; // Only 1 label, need 2+
        let result = MovedResource::new(labels, path, "compute".to_string());
        assert!(result.is_err());
    }

    #[test]
    fn test_moved_resource_build_from_expression() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let expr = resource.from_expression();
        assert!(matches!(expr, Expression::Traversal(_)));
        Ok(())
    }

    #[test]
    fn test_moved_resource_build_to_expression() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let expr = resource.to_expression();
        assert!(matches!(expr, Expression::Traversal(_)));
        Ok(())
    }

    #[test]
    fn test_moved_resource_to_block() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let block = resource.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_moved_resource_to_block_has_comment() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let block = resource.to_block()?;
        if let Some(prefix) = block.decor().prefix() {
            assert!(prefix.contains("# From: main.tf"));
        } else {
            panic!("Expected prefix to be set");
        }
        Ok(())
    }

    #[test]
    fn test_moved_resource_to_block_has_indented_attributes() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let block = resource.to_block()?;
        let body = Body::builder().block(block).build();
        let output = body.to_string();
        assert!(output.contains("  from"));
        assert!(output.contains("  to"));
        Ok(())
    }

    #[test]
    fn test_moved_resource_to_block_output_format() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let block = resource.to_block()?;
        let body = Body::builder().block(block).build();
        let output = body.to_string();
        assert!(output.contains("# From: main.tf"));
        assert!(output.contains("moved {"));
        assert!(output.contains("from = aws_instance.web"));
        assert!(output.contains("to = module.compute.aws_instance.web"));
        Ok(())
    }
}
