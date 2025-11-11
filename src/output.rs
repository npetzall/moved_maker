use hcl::edit::structure::{Body, Block};

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
    use crate::processor::build_resource_moved_block;
    use std::path::Path;

    #[test]
    fn test_build_body_from_single_block() {
        let path = Path::new("test.tf");
        let block = build_resource_moved_block("aws_instance", "web", "compute", path);
        let body = build_output_body(&[block]);
        
        assert_eq!(body.blocks().count(), 1);
    }

    #[test]
    fn test_build_body_from_multiple_blocks() {
        let path = Path::new("test.tf");
        let block1 = build_resource_moved_block("aws_instance", "web", "compute", path);
        let block2 = build_resource_moved_block("aws_s3_bucket", "data", "compute", path);
        let body = build_output_body(&[block1, block2]);
        
        assert_eq!(body.blocks().count(), 2);
    }

    #[test]
    fn test_body_to_string_conversion() {
        let path = Path::new("test.tf");
        let block = build_resource_moved_block("aws_instance", "web", "compute", path);
        let body = build_output_body(&[block]);
        
        let output = body.to_string();
        assert!(output.contains("moved"));
        assert!(output.contains("from"));
        assert!(output.contains("to"));
    }

    #[test]
    fn test_output_format_single_resource() {
        let path = Path::new("main.tf");
        let block = build_resource_moved_block("aws_instance", "web", "compute", path);
        let body = build_output_body(&[block]);
        let output = body.to_string();
        
        assert!(output.contains("# From: main.tf"));
        assert!(output.contains("moved"));
    }

    #[test]
    fn test_output_format_multiple_blocks() {
        let path1 = Path::new("main.tf");
        let path2 = Path::new("main.tf");
        let block1 = build_resource_moved_block("aws_instance", "web", "compute", path1);
        let block2 = build_resource_moved_block("aws_s3_bucket", "data", "compute", path2);
        let body = build_output_body(&[block1, block2]);
        let output = body.to_string();
        
        assert!(output.contains("# From: main.tf"));
        assert_eq!(output.matches("moved").count(), 2);
    }

    #[test]
    fn test_output_body_has_indented_attributes() {
        let path1 = Path::new("main.tf");
        let path2 = Path::new("main.tf");
        let block1 = build_resource_moved_block("aws_instance", "web", "compute", path1);
        let block2 = build_resource_moved_block("aws_s3_bucket", "data", "compute", path2);
        let body = build_output_body(&[block1, block2]);
        let output = body.to_string();
        
        // Verify all attributes are indented
        assert!(output.contains("  from"), "All from attributes should be indented");
        assert!(output.contains("  to"), "All to attributes should be indented");
        
        // Verify all comments are preserved
        assert!(output.contains("# From: main.tf"), "Resource block comment should be preserved");
        
        // Verify structure
        assert_eq!(output.matches("moved {").count(), 2);
        assert!(output.contains("from = aws_instance.web"));
        assert!(output.contains("to = module.compute.aws_instance.web"));
        assert!(output.contains("from = aws_s3_bucket.data"));
        assert!(output.contains("to = module.compute.aws_s3_bucket.data"));
    }
}

