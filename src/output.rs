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

use crate::file_discovery::find_terraform_files;
use crate::parser::parse_terraform_file;
use anyhow::{Context, Result};
use hcl::edit::expr::Expression;
use hcl::edit::parser::parse_body;
use hcl::edit::structure::{Attribute, Block, Body};
use hcl::edit::{Decorate, Ident};
use std::path::{Path, PathBuf};

/// Build the output Body from collected moved blocks
pub fn build_output_body(blocks: &[Block]) -> Body {
    let mut builder = Body::builder();
    for block in blocks {
        builder = builder.block(block.clone());
    }
    builder.build()
}

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

/// Represents a resource block that needs to be moved to a module
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
    #[allow(dead_code)]
    pub fn labels(&self) -> &[String] {
        &self.labels
    }

    /// Convenience accessor for resource type (labels[0])
    #[allow(dead_code)]
    pub fn resource_type(&self) -> &str {
        &self.labels[0]
    }

    /// Convenience accessor for resource name (labels[1])
    #[allow(dead_code)]
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

/// Represents a module block that needs to be moved to a module
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
    #[allow(dead_code)]
    pub fn labels(&self) -> &[String] {
        &self.labels
    }

    /// Convenience accessor for module name (labels[0])
    #[allow(dead_code)]
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

/// Enum wrapper for moved blocks (Resource or Module)
///
/// This enum does not implement the `ToMovedBlock` trait because no code requires it as a trait bound.
/// The `from_block()` method encapsulates the logic for creating a `MovedBlock` from an HCL `Block`,
/// making it reusable and keeping the creation logic in one place.
pub enum MovedBlock {
    Resource(MovedResource),
    Module(MovedModule),
}

impl MovedBlock {
    /// Create a `MovedBlock` from an HCL Block
    ///
    /// Determines the block type from the block's identifier and creates
    /// the appropriate variant (Resource or Module)
    ///
    /// Returns:
    /// - `None` if the block type is not supported (resource/module) - should be skipped silently
    /// - `Some(Ok(MovedBlock))` if successfully converted
    /// - `Some(Err(e))` if supported type but conversion failed (e.g., invalid labels)
    pub fn from_block(block: &Block, file_path: &Path, module_name: &str) -> Option<Result<Self>> {
        let ident = block.ident.value().to_string();
        let labels: Vec<String> = block
            .labels
            .iter()
            .map(|l| l.as_str().to_string())
            .collect();

        match ident.as_str() {
            "resource" => {
                if labels.len() < 2 {
                    return Some(Err(anyhow::anyhow!(
                        "Resource block in {} has fewer than 2 labels",
                        file_path.display()
                    )));
                }
                Some(
                    MovedResource::new(labels, file_path.to_path_buf(), module_name.to_string())
                        .map(Self::Resource),
                )
            }
            "module" => {
                if labels.is_empty() {
                    return Some(Err(anyhow::anyhow!(
                        "Module block in {} has no labels",
                        file_path.display()
                    )));
                }
                Some(
                    MovedModule::new(labels, file_path.to_path_buf(), module_name.to_string())
                        .map(Self::Module),
                )
            }
            _ => None, // Unsupported block type, skip silently
        }
    }

    /// Convert to HCL Block by delegating to the inner type
    pub fn to_block(&self) -> Result<Block> {
        match self {
            MovedBlock::Resource(r) => r.to_block(),
            MovedBlock::Module(m) => m.to_block(),
        }
    }
}

/// Wrapper for Terraform file discovery
pub struct TerraformFiles {
    src: PathBuf,
}

impl TerraformFiles {
    pub fn new(src: PathBuf) -> Self {
        Self { src }
    }

    pub fn into_iter(self) -> impl Iterator<Item = Result<PathBuf>> {
        match find_terraform_files(&self.src) {
            Ok(files) => files.into_iter().map(Ok).collect::<Vec<_>>().into_iter(),
            Err(e) => vec![Err(e)].into_iter(),
        }
    }
}

/// Adapter that converts file results to parsed bodies
/// Owns TerraformFiles
pub struct ParsedFiles {
    files: Box<dyn Iterator<Item = Result<PathBuf>>>,
}

impl ParsedFiles {
    pub fn new(files: TerraformFiles) -> Self {
        Self {
            files: Box::new(files.into_iter()),
        }
    }
}

impl Iterator for ParsedFiles {
    type Item = Result<(PathBuf, Body)>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let file_result = self.files.next()?;

            let file = match file_result {
                Ok(f) => f,
                Err(e) => {
                    eprintln!("Warning: Failed to discover file: {}", e);
                    continue; // Skip this file and try next
                }
            };

            match parse_terraform_file(&file) {
                Ok(body) => return Some(Ok((file, body))),
                Err(e) => {
                    eprintln!("Warning: Failed to parse {}: {}", file.display(), e);
                    continue; // Skip this file and try next
                }
            }
        }
    }
}

/// Adapter that converts blocks to MovedBlocks, managing body iteration internally
/// Owns ParsedFiles
pub struct MovedBlocks {
    parsed: ParsedFiles,
    module_name: String,
    current_file: Option<PathBuf>,
    current_body: Option<Body>, // Keeps body alive for block references
    current_blocks: Vec<Block>, // Store blocks as owned values to avoid lifetime issues
    current_block_index: usize,
}

impl MovedBlocks {
    pub fn new(parsed: ParsedFiles, module_name: String) -> Self {
        Self {
            parsed,
            module_name,
            current_file: None,
            current_body: None,
            current_blocks: Vec::new(),
            current_block_index: 0,
        }
    }

    /// Load blocks from the next body into current_blocks vector
    /// Sets up iteration over all blocks (filtering happens in Iterator::next())
    fn load_next_body(&mut self) -> bool {
        loop {
            match self.parsed.next() {
                Some(Ok((file_path, body))) => {
                    self.current_file = Some(file_path);
                    self.current_body = Some(body); // Store body to keep it alive
                    // Collect blocks into a vector (cloning them)
                    self.current_blocks = self
                        .current_body
                        .as_ref()
                        .unwrap()
                        .blocks()
                        .cloned()
                        .collect();
                    self.current_block_index = 0;
                    return true;
                }
                Some(Err(e)) => {
                    eprintln!("Warning: {}", e);
                    continue; // Try next file instead of recursing
                }
                None => {
                    return false;
                }
            }
        }
    }
}

impl Iterator for MovedBlocks {
    type Item = Result<MovedBlock>;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            // If we have current blocks, try to get next one
            while self.current_block_index < self.current_blocks.len() {
                let block = &self.current_blocks[self.current_block_index];
                self.current_block_index += 1;

                let file_path = self
                    .current_file
                    .as_ref()
                    .expect("file_path should be set when blocks exist");

                match MovedBlock::from_block(block, file_path, &self.module_name) {
                    None => continue, // Unsupported block type, skip silently
                    Some(Ok(moved_block)) => return Some(Ok(moved_block)),
                    Some(Err(e)) => {
                        eprintln!("Warning: {}", e);
                        continue; // Invalid block, warn and skip
                    }
                }
            }

            // Current blocks exhausted, clear and load next body
            self.current_file = None;
            self.current_body = None;
            self.current_blocks.clear();
            self.current_block_index = 0;

            // Load next body
            if !self.load_next_body() {
                return None; // No more bodies
            }
        }
    }
}

/// Main builder that composes the pipeline
pub struct MovedBlockBuilder {
    src: PathBuf,
    module_name: String,
}

impl MovedBlockBuilder {
    pub fn new(src: PathBuf, module_name: String) -> Self {
        Self { src, module_name }
    }

    pub fn moved_blocks(self) -> MovedBlocks {
        let files = TerraformFiles::new(self.src);
        let parsed = ParsedFiles::new(files);
        MovedBlocks::new(parsed, self.module_name)
    }
}

/// Pure utility for building address expressions from segments
/// Follows Single Responsibility Principle - only builds expressions, nothing else
pub struct AddressBuilder;

impl AddressBuilder {
    /// Create a new AddressBuilder
    pub fn new() -> Self {
        Self
    }

    /// Build an expression from a slice of string segments
    /// Each segment becomes an attribute in the traversal path
    ///
    /// This uses string parsing to build the expression, which is the most
    /// reliable way to create hcl::edit::expr::Expression from segments.
    pub fn build(&self, segments: &[&str]) -> Expression {
        if segments.is_empty() {
            // Return a simple variable expression if no segments
            let expr_str = "x";
            let attr_str = format!("x = {}", expr_str);
            let body = parse_body(&attr_str).expect("Failed to parse empty expression");
            let attr = body.attributes().next().expect("Expected attribute");
            return attr.value.clone();
        }

        // Build expression string: segment0.segment1.segment2...
        let expr_str = segments.join(".");

        // Parse the expression by wrapping it in an attribute
        let attr_str = format!("x = {}", expr_str);
        let body = parse_body(&attr_str)
            .unwrap_or_else(|_| panic!("Failed to parse expression: {}", expr_str));
        let attr = body
            .attributes()
            .next()
            .expect("Expected attribute in parsed body");
        attr.value.clone()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::Result;
    use pretty_assertions::assert_eq;

    // AddressBuilder tests
    #[test]
    fn test_address_builder_new() {
        let _builder = AddressBuilder::new();
        // Builder is just a utility, no state to verify
        // This test just ensures it can be constructed
    }

    #[test]
    fn test_address_builder_build_single_segment() {
        let builder = AddressBuilder::new();
        let expr = builder.build(&["aws_instance"]);
        // A single segment creates a Variable, not a Traversal
        assert!(matches!(expr, Expression::Variable(_)));
    }

    #[test]
    fn test_address_builder_build_multiple_segments() {
        let builder = AddressBuilder::new();
        let expr = builder.build(&["aws_instance", "web"]);
        assert!(matches!(expr, Expression::Traversal(_)));
    }

    #[test]
    fn test_address_builder_build_resource_expression() {
        let builder = AddressBuilder::new();
        let expr = builder.build(&["aws_instance", "web"]);
        assert!(matches!(expr, Expression::Traversal(_)));
        // Verify it can be converted to string representation
        let body = Body::builder()
            .attribute(hcl::edit::structure::Attribute::new(
                hcl::edit::Ident::new("test"),
                expr,
            ))
            .build();
        let output = body.to_string();
        assert!(output.contains("aws_instance"));
        assert!(output.contains("web"));
    }

    #[test]
    fn test_address_builder_build_module_expression() {
        let builder = AddressBuilder::new();
        let expr = builder.build(&["module", "web_server"]);
        assert!(matches!(expr, Expression::Traversal(_)));
        let body = Body::builder()
            .attribute(hcl::edit::structure::Attribute::new(
                hcl::edit::Ident::new("test"),
                expr,
            ))
            .build();
        let output = body.to_string();
        assert!(output.contains("module"));
        assert!(output.contains("web_server"));
    }

    #[test]
    fn test_address_builder_build_nested_expression() {
        let builder = AddressBuilder::new();
        let expr = builder.build(&["module", "name", "aws_instance", "web"]);
        assert!(matches!(expr, Expression::Traversal(_)));
        let body = Body::builder()
            .attribute(hcl::edit::structure::Attribute::new(
                hcl::edit::Ident::new("test"),
                expr,
            ))
            .build();
        let output = body.to_string();
        assert!(output.contains("module"));
        assert!(output.contains("name"));
        assert!(output.contains("aws_instance"));
        assert!(output.contains("web"));
    }

    // ToMovedBlock trait tests
    #[test]
    #[allow(dead_code)]
    fn test_to_moved_block_trait_exists() {
        // This test just verifies the trait can be defined and used
        // Actual implementations will be tested in MovedResource and MovedModule tests
        trait TestTrait: ToMovedBlock {}
        // If this compiles, the trait exists
    }

    // MovedResource tests
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

    // MovedModule tests
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

    // MovedBlock enum tests
    #[test]
    fn test_moved_block_resource_variant() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let moved_block = MovedBlock::Resource(resource);
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_moved_block_module_variant() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let moved_block = MovedBlock::Module(module);
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_resource() -> Result<()> {
        use crate::parser::parse_terraform_file;
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"resource "aws_instance" "web" {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "compute");
        assert!(result.is_some());
        let moved_block = result.unwrap()?;

        match moved_block {
            MovedBlock::Resource(r) => {
                assert_eq!(r.resource_type(), "aws_instance");
                assert_eq!(r.resource_name(), "web");
            }
            _ => panic!("Expected Resource variant"),
        }
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_module() -> Result<()> {
        use crate::parser::parse_terraform_file;
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"module "web_server" {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "a");
        assert!(result.is_some());
        let moved_block = result.unwrap()?;

        match moved_block {
            MovedBlock::Module(m) => {
                assert_eq!(m.module_name_local(), "web_server");
            }
            _ => panic!("Expected Module variant"),
        }
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_invalid_resource() -> Result<()> {
        use crate::parser::parse_terraform_file;
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"resource "aws_instance" {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "compute");
        assert!(result.is_some());
        assert!(result.unwrap().is_err()); // Should return Some(Err)
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_invalid_module() -> Result<()> {
        use crate::parser::parse_terraform_file;
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"module {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "a");
        assert!(result.is_some());
        assert!(result.unwrap().is_err()); // Should return Some(Err)
        Ok(())
    }

    #[test]
    fn test_moved_block_from_block_unsupported_type() -> Result<()> {
        use crate::parser::parse_terraform_file;
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"variable "test" {}"#)?;

        let body = parse_terraform_file(&file)?;
        let block = body.blocks().next().expect("Expected a block");

        let result = MovedBlock::from_block(block, &file, "compute");
        assert!(result.is_none()); // Should return None for unsupported types
        Ok(())
    }

    #[test]
    fn test_moved_block_to_block_resource() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["aws_instance".to_string(), "web".to_string()];
        let resource = MovedResource::new(labels, path, "compute".to_string())?;
        let moved_block = MovedBlock::Resource(resource);
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        let body = Body::builder().block(block).build();
        let output = body.to_string();
        assert!(output.contains("from = aws_instance.web"));
        assert!(output.contains("to = module.compute.aws_instance.web"));
        Ok(())
    }

    #[test]
    fn test_moved_block_to_block_module() -> Result<()> {
        let path = std::path::PathBuf::from("main.tf");
        let labels = vec!["web_server".to_string()];
        let module = MovedModule::new(labels, path, "a".to_string())?;
        let moved_block = MovedBlock::Module(module);
        let block = moved_block.to_block()?;
        assert_eq!(block.ident.value().to_string(), "moved");
        let body = Body::builder().block(block).build();
        let output = body.to_string();
        assert!(output.contains("from = module.web_server"));
        assert!(output.contains("to = module.a.module.web_server"));
        Ok(())
    }

    // Iterator adapter tests
    #[test]
    fn test_terraform_files_new() {
        let path = std::path::PathBuf::from("/tmp");
        let files = TerraformFiles::new(path);
        // Just verify it can be constructed
        drop(files);
    }

    #[test]
    fn test_moved_block_builder_new() {
        let path = std::path::PathBuf::from("/tmp");
        let builder = MovedBlockBuilder::new(path, "test".to_string());
        // Just verify it can be constructed
        drop(builder);
    }

    #[test]
    fn test_moved_block_builder_moved_blocks() -> Result<()> {
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"resource "aws_instance" "web" {}"#)?;

        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "compute".to_string());
        let mut moved_blocks = builder.moved_blocks();

        // Should find one resource block
        let moved_block = moved_blocks.next();
        assert!(moved_block.is_some());
        let moved_block = moved_block.unwrap()?;

        match moved_block {
            MovedBlock::Resource(r) => {
                assert_eq!(r.resource_type(), "aws_instance");
                assert_eq!(r.resource_name(), "web");
            }
            _ => panic!("Expected Resource variant"),
        }

        // Should be no more blocks
        assert!(moved_blocks.next().is_none());
        Ok(())
    }

    #[test]
    fn test_moved_blocks_empty_dir() -> Result<()> {
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "compute".to_string());
        let mut moved_blocks = builder.moved_blocks();

        // Should return None immediately
        assert!(moved_blocks.next().is_none());
        Ok(())
    }

    #[test]
    fn test_moved_blocks_single_resource() -> Result<()> {
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"resource "aws_instance" "web" {}"#)?;

        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "compute".to_string());
        let moved_blocks: Vec<_> = builder.moved_blocks().collect::<Result<Vec<_>>>()?;

        assert_eq!(moved_blocks.len(), 1);
        match &moved_blocks[0] {
            MovedBlock::Resource(r) => {
                assert_eq!(r.resource_type(), "aws_instance");
                assert_eq!(r.resource_name(), "web");
            }
            _ => panic!("Expected Resource variant"),
        }
        Ok(())
    }

    #[test]
    fn test_moved_blocks_single_module() -> Result<()> {
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(&file, r#"module "web_server" {}"#)?;

        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "a".to_string());
        let moved_blocks: Vec<_> = builder.moved_blocks().collect::<Result<Vec<_>>>()?;

        assert_eq!(moved_blocks.len(), 1);
        match &moved_blocks[0] {
            MovedBlock::Module(m) => {
                assert_eq!(m.module_name_local(), "web_server");
            }
            _ => panic!("Expected Module variant"),
        }
        Ok(())
    }

    #[test]
    fn test_moved_blocks_mixed() -> Result<()> {
        use std::fs;
        use tempfile::TempDir;

        let temp_dir = TempDir::new()?;
        let file = temp_dir.path().join("main.tf");
        fs::write(
            &file,
            r#"
resource "aws_instance" "web" {}
module "web_server" {}
"#,
        )?;

        let builder = MovedBlockBuilder::new(temp_dir.path().to_path_buf(), "compute".to_string());
        let moved_blocks: Vec<_> = builder.moved_blocks().collect::<Result<Vec<_>>>()?;

        assert_eq!(moved_blocks.len(), 2);
        // Order should be preserved (resource first, then module)
        match &moved_blocks[0] {
            MovedBlock::Resource(r) => {
                assert_eq!(r.resource_type(), "aws_instance");
            }
            _ => panic!("Expected Resource as first block"),
        }
        match &moved_blocks[1] {
            MovedBlock::Module(m) => {
                assert_eq!(m.module_name_local(), "web_server");
            }
            _ => panic!("Expected Module as second block"),
        }
        Ok(())
    }

    #[test]
    fn test_build_body_from_single_block() -> Result<()> {
        let path = PathBuf::from("test.tf");
        let resource = MovedResource::new(
            vec!["aws_instance".to_string(), "web".to_string()],
            path,
            "compute".to_string(),
        )?;
        let block = resource.to_block()?;
        let body = build_output_body(&[block]);

        assert_eq!(body.blocks().count(), 1);
        Ok(())
    }

    #[test]
    fn test_build_body_from_multiple_blocks() -> Result<()> {
        let path = PathBuf::from("test.tf");
        let resource1 = MovedResource::new(
            vec!["aws_instance".to_string(), "web".to_string()],
            path.clone(),
            "compute".to_string(),
        )?;
        let resource2 = MovedResource::new(
            vec!["aws_s3_bucket".to_string(), "data".to_string()],
            path,
            "compute".to_string(),
        )?;
        let block1 = resource1.to_block()?;
        let block2 = resource2.to_block()?;
        let body = build_output_body(&[block1, block2]);

        assert_eq!(body.blocks().count(), 2);
        Ok(())
    }

    #[test]
    fn test_body_to_string_conversion() -> Result<()> {
        let path = PathBuf::from("test.tf");
        let resource = MovedResource::new(
            vec!["aws_instance".to_string(), "web".to_string()],
            path,
            "compute".to_string(),
        )?;
        let block = resource.to_block()?;
        let body = build_output_body(&[block]);

        let output = body.to_string();
        assert!(output.contains("moved"));
        assert!(output.contains("from"));
        assert!(output.contains("to"));
        Ok(())
    }

    #[test]
    fn test_output_format_single_resource() -> Result<()> {
        let path = PathBuf::from("main.tf");
        let resource = MovedResource::new(
            vec!["aws_instance".to_string(), "web".to_string()],
            path,
            "compute".to_string(),
        )?;
        let block = resource.to_block()?;
        let body = build_output_body(&[block]);
        let output = body.to_string();

        assert!(output.contains("# From: main.tf"));
        assert!(output.contains("moved"));
        Ok(())
    }

    #[test]
    fn test_output_format_multiple_blocks() -> Result<()> {
        let path = PathBuf::from("main.tf");
        let resource1 = MovedResource::new(
            vec!["aws_instance".to_string(), "web".to_string()],
            path.clone(),
            "compute".to_string(),
        )?;
        let resource2 = MovedResource::new(
            vec!["aws_s3_bucket".to_string(), "data".to_string()],
            path,
            "compute".to_string(),
        )?;
        let block1 = resource1.to_block()?;
        let block2 = resource2.to_block()?;
        let body = build_output_body(&[block1, block2]);
        let output = body.to_string();

        assert!(output.contains("# From: main.tf"));
        assert_eq!(output.matches("moved").count(), 2);
        Ok(())
    }

    #[test]
    fn test_output_body_has_indented_attributes() -> Result<()> {
        let path = PathBuf::from("main.tf");
        let resource1 = MovedResource::new(
            vec!["aws_instance".to_string(), "web".to_string()],
            path.clone(),
            "compute".to_string(),
        )?;
        let resource2 = MovedResource::new(
            vec!["aws_s3_bucket".to_string(), "data".to_string()],
            path,
            "compute".to_string(),
        )?;
        let block1 = resource1.to_block()?;
        let block2 = resource2.to_block()?;
        let body = build_output_body(&[block1, block2]);
        let output = body.to_string();

        // Verify all attributes are indented
        assert!(
            output.contains("  from"),
            "All from attributes should be indented"
        );
        assert!(
            output.contains("  to"),
            "All to attributes should be indented"
        );

        // Verify all comments are preserved
        assert!(
            output.contains("# From: main.tf"),
            "Resource block comment should be preserved"
        );

        // Verify structure
        assert_eq!(output.matches("moved {").count(), 2);
        assert!(output.contains("from = aws_instance.web"));
        assert!(output.contains("to = module.compute.aws_instance.web"));
        assert!(output.contains("from = aws_s3_bucket.data"));
        assert!(output.contains("to = module.compute.aws_s3_bucket.data"));
        Ok(())
    }
}
