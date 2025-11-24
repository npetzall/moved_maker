# TODO - Remaining Items

This checklist contains only the remaining incomplete items. All completed items have been archived in `DONE.md`.

## Final Verification

- [ ] **Check test coverage**
  - [ ] Run test coverage tool (e.g., `cargo tarpaulin` or `cargo llvm-cov`)
  - [ ] Review coverage report
  - [ ] Identify any gaps in test coverage

- [ ] **Manual testing**
  - [ ] Test with real Terraform configuration
  - [ ] Verify output can be pasted into Terraform file
  - [ ] Test with `terraform plan` to verify moved blocks are valid
