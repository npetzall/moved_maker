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

//! Module block model for moved blocks.
//!
//! `MovedModule` encapsulates all logic related to module blocks,
//! including validation, expression building, and block conversion.

use crate::address::AddressBuilder;
use crate::to_moved_block::ToMovedBlock;
use anyhow::Result;
use hcl::edit::expr::Expression;
use std::path::{Path, PathBuf};

/// Represents a module block that needs to be moved to a module
#[derive(Debug, Clone)]
pub struct MovedModule {
    labels: Vec<String>,
    file_path: PathBuf,
    target_module_name: String,
}

impl MovedModule {
    /// Create a new MovedModule
    ///
    /// # Arguments
    /// * `labels` - All labels from the block (must have at least 1 for modules)
    /// * `file_path` - Source file path (for comment)
    /// * `target_module_name` - Target module name
    pub fn new(
        labels: Vec<String>,
        file_path: PathBuf,
        target_module_name: String,
    ) -> Result<Self> {
        if labels.is_empty() {
            return Err(anyhow::anyhow!("Module blocks must have at least 1 label"));
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

    /// Convenience accessor for module name (labels[0])
    #[allow(dead_code)] // Used in tests
    pub fn module_name_local(&self) -> &str {
        &self.labels[0]
    }

    /// Build the "from" expression (private method)
    fn build_from_expression(&self) -> Expression {
        AddressBuilder::new().build(&["module", &self.labels[0]])
    }

    /// Build the "to" expression (private method)
    fn build_to_expression(&self) -> Expression {
        AddressBuilder::new().build(&[
            "module",
            &self.target_module_name,
            "module",
            &self.labels[0],
        ])
    }
}

impl ToMovedBlock for MovedModule {
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
    fn test_moved_module_new() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels.clone(), path, "a".to_string())?;
        assert_eq!(module.labels(), &labels);
        assert_eq!(module.module_name_local(), "web_server");
        Ok(())
    }

    #[test]
    fn test_moved_module_new_invalid_labels() {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec![]; // No labels, need at least 1
        let result = MovedModule::new(labels, path, "a".to_string());
        assert!(result.is_err());
    }

    #[test]
    fn test_moved_module_build_from_expression() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let expr = module.from_expression();
        assert!(matches!(expr, Expression::Traversal(_)));
        Ok(())
    }

    #[test]
    fn test_moved_module_build_to_expression() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let expr = module.to_expression();
        assert!(matches!(expr, Expression::Traversal(_)));
        Ok(())
    }

    #[test]
    fn test_moved_module_to_block() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let block = module.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_moved_module_to_block_has_comment() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let block = module.to_block()?;
        if let Some(prefix) = block.decor().prefix() {
            assert!(prefix.contains("# From: main.tf"));
        } else {
            panic!("Expected prefix to be set");
        }
        Ok(())
    }

    #[test]
    fn test_moved_module_to_block_has_indented_attributes() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let block = module.to_block()?;
        let body = Body::builder().block(block).build();
        let output = body.to_string();
        assert!(output.contains("  from"));
        assert!(output.contains("  to"));
        Ok(())
    }

    #[test]
    fn test_moved_module_to_block_output_format() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let block = module.to_block()?;
        let body = Body::builder().block(block).build();
        let output = body.to_string();
        assert!(output.contains("# From: main.tf"));
        assert!(output.contains("moved {"));
        assert!(output.contains("from = module.web_server"));
        assert!(output.contains("to = module.a.module.web_server"));
        Ok(())
    }
}
