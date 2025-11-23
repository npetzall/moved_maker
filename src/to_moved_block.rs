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

//! Trait for converting moved blocks to HCL blocks.
//!
//! This trait provides a shared interface for different types of moved blocks
//! (resources, modules, etc.) to convert themselves into HCL block structures.

use anyhow::{Context, Result};
use hcl::edit::expr::Expression;
use hcl::edit::structure::{Attribute, Block};
use hcl::edit::{Decorate, Ident};
use std::path::Path;

/// Trait for converting moved block types to HCL Block
///
/// This trait follows the Template Method pattern - the default `to_block()` implementation
/// handles the common structure (attribute creation, indentation, block building, comment),
/// while implementors provide the block-specific expression-building logic.
pub trait ToMovedBlock {
    /// Build the "from" expression (block-specific logic)
    #[allow(clippy::wrong_self_convention)]
    fn from_expression(&self) -> Expression;

    /// Build the "to" expression (block-specific logic)
    fn to_expression(&self) -> Expression;

    /// Get the file path for the comment (block-specific)
    fn file_path(&self) -> &Path;

    /// Default implementation that builds the moved block
    /// This handles the common logic: attribute creation, indentation, block building, and comment
    fn to_block(&self) -> Result<Block> {
        let from_expr = self.from_expression();
        let to_expr = self.to_expression();

        // Create attributes with indentation
        let mut from_attr = Attribute::new(Ident::new("from"), from_expr);
        from_attr.decor_mut().set_prefix("  ");

        let mut to_attr = Attribute::new(Ident::new("to"), to_expr);
        to_attr.decor_mut().set_prefix("  ");

        let mut block = Block::builder(Ident::new("moved"))
            .attribute(from_attr)
            .attribute(to_attr)
            .build();

        // Add comment with filename
        let filename = self
            .file_path()
            .file_name()
            .with_context(|| format!("Path must have filename: {}", self.file_path().display()))?
            .to_string_lossy();
        let comment = format!("# From: {}\n", filename);
        block.decor_mut().set_prefix(comment.as_str());

        Ok(block)
    }
}
