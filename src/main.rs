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
#![forbid(unsafe_code)]

mod cli;
mod file_discovery;
mod output;
mod parser;
mod processor;

use anyhow::Result;
use clap::Parser;
use cli::Args;
use file_discovery::find_terraform_files;
use output::build_output_body;
use parser::parse_terraform_file;
use processor::{build_resource_moved_block, extract_blocks};

fn main() {
    if let Err(e) = run() {
        eprintln!("Error: {:#}", e);
        std::process::exit(1);
    }
}

fn run() -> Result<()> {
    let args = Args::parse();
    args.validate()?;

    let files = find_terraform_files(&args.src)?;
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

                    match build_resource_moved_block(
                        &block_type,
                        &block_name,
                        &args.module_name,
                        &file,
                    ) {
                        Ok(moved_block) => {
                            moved_blocks.push(moved_block);
                        }
                        Err(e) => {
                            eprintln!(
                                "Warning: Failed to build moved block for {}.{} in {}: {}",
                                block_type,
                                block_name,
                                file.display(),
                                e
                            );
                        }
                    }
                }
            }
            Err(e) => {
                eprintln!("Warning: Failed to parse {}: {}", file.display(), e);
            }
        }
    }

    let output_body = build_output_body(&moved_blocks);
    println!("{}", output_body);
    Ok(())
}
