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

mod address;
mod cli;
mod moved_block;
mod moved_module;
mod moved_resource;
mod output;
mod parser;
mod pipeline;
mod terraform_files;
mod to_moved_block;

use anyhow::Result;
use clap::Parser;
use cli::Args;
use output::build_output_body;
use pipeline::MovedBlockBuilder;

fn main() {
    if let Err(e) = run() {
        eprintln!("Error: {:#}", e);
        std::process::exit(1);
    }
}

fn run() -> Result<()> {
    let args = Args::parse();
    args.validate()?;

    let builder = MovedBlockBuilder::new(args.src, args.module_name);
    let mut moved_blocks = Vec::new();

    for moved_block_result in builder.moved_blocks() {
        match moved_block_result {
            Ok(moved_block) => match moved_block.to_block() {
                Ok(block) => moved_blocks.push(block),
                Err(e) => {
                    eprintln!("Warning: Failed to convert moved block: {}", e);
                }
            },
            Err(e) => {
                eprintln!("Warning: {}", e);
            }
        }
    }

    let output_body = build_output_body(&moved_blocks);
    println!("{}", output_body);
    Ok(())
}
