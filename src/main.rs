mod cli;
mod file_discovery;
mod parser;
mod processor;
mod output;

use clap::Parser;
use cli::Args;
use file_discovery::find_terraform_files;
use parser::parse_terraform_file;
use processor::{extract_blocks, build_resource_moved_block};
use output::build_output_body;

fn main() {
    let args = Args::parse();
    args.validate();

    let files = find_terraform_files(&args.src);
    let mut moved_blocks = Vec::new();

    for file in files {
        match parse_terraform_file(&file) {
            Ok(body) => {
                let blocks = extract_blocks(&body);
                for block in blocks {
                    let labels: Vec<_> = block.labels.iter().collect();
                    if labels.len() < 2 {
                        eprintln!(
                            "Warning: Block in {} has fewer than 2 labels, skipping",
                            file.display()
                        );
                        continue;
                    }

                    let block_type = labels[0].to_string();
                    let block_name = labels[1].to_string();

                    let moved_block = build_resource_moved_block(&block_type, &block_name, &args.module_name, &file);

                    moved_blocks.push(moved_block);
                }
            }
            Err(e) => {
                eprintln!("Warning: Failed to parse {}: {}", file.display(), e);
            }
        }
    }

    let output_body = build_output_body(&moved_blocks);
    println!("{}", output_body);
}
