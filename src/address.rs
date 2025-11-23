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

//! Utility for building HCL address expressions.
//!
//! `AddressBuilder` is a pure utility with no state. It builds HCL traversal
//! expressions from string segments.

use hcl::edit::expr::Expression;
use hcl::edit::parser::parse_body;

/// Utility for building HCL address expressions from string segments
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
    use hcl::edit::structure::Body;

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
}
