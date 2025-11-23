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

//! Output formatting for moved blocks.
//!
//! This module provides functions to format the final output from moved blocks.

use hcl::edit::structure::{Block, Body};

/// Build the output Body from collected moved blocks
pub fn build_output_body(blocks: &[Block]) -> Body {
    let mut builder = Body::builder();
    for block in blocks {
        builder = builder.block(block.clone());
    }
    builder.build()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::moved_resource::MovedResource;
    use crate::to_moved_block::ToMovedBlock;
    use anyhow::Result;
    use std::path::PathBuf;

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
