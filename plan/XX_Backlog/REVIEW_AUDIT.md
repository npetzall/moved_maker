# Review and Audit Tools: Manual Trust Verification

## Purpose
Document tools for manual code review and trust verification that complement automated security scanning. These tools require active participation and maintenance, making them suitable for future consideration when project needs and resources allow.

## Tools

### Option 1: cargo vet 🔮 For Future Consideration

**Overview**: Shared auditing system that allows projects to import audit records from trusted entities (developed by Mozilla)

**Compatibility**:
- ✅ Apple Silicon (ARM): Fully supported
- ✅ Linux (GitHub Actions): Fully supported

**Installation**:
```bash
cargo install cargo-vet
```

**Usage**:
```bash
# Import audits from trusted sources
cargo vet import

# Check if dependencies are audited
cargo vet check

# Generate audit requirements
cargo vet generate

# Certify a dependency as audited
cargo vet certify <crate-name> <version>
```

**Pros**:
- ✅ **Shared auditing**: Leverage audits from trusted organizations (e.g., Mozilla)
- ✅ **Reduced redundancy**: Avoid duplicate auditing efforts across the ecosystem
- ✅ **Trust verification**: Verify that dependencies have been audited by trusted entities
- ✅ **Supply chain security**: Adds layer of trust verification beyond automated checks
- ✅ **Organization-friendly**: Well-suited for enterprise/organizational use

**Cons**:
- ⚠️ **Requires trusted sources**: Need to identify and trust auditing organizations
- ⚠️ **Manual process**: Requires human reviewers to perform audits
- ⚠️ **Maintenance overhead**: Need to maintain audit records and trust relationships
- ⚠️ **Less useful for small projects**: More valuable for organizations with shared audit needs

**When to Consider**:
- Enterprise or organizational projects
- Need for supply chain trust verification
- Ability to leverage audits from trusted organizations (e.g., Mozilla)
- Resources available for maintaining manual audit processes
- Need for defense-in-depth beyond automated vulnerability scanning

**CI Integration Example**:
```yaml
- name: Install cargo-vet
  run: cargo install cargo-vet

- name: Import audits from trusted sources
  run: cargo vet import

- name: Check audit status
  run: cargo vet check
```

---

### Option 2: cargo crev 🔮 For Future Consideration

**Overview**: Decentralized code review system that enables developers to review and sign off on Rust crates, building a web of trust

**Compatibility**:
- ✅ Apple Silicon (ARM): Fully supported
- ✅ Linux (GitHub Actions): Fully supported

**Installation**:
```bash
cargo install cargo-crev
```

**Usage**:
```bash
# Review a crate
cargo crev review <crate-name>

# Check trust status of dependencies
cargo crev verify

# Trust another developer's reviews
cargo crev trust <identity>

# Publish your reviews
cargo crev publish
```

**Pros**:
- ✅ **Decentralized**: No central authority, peer-to-peer trust model
- ✅ **Web of trust**: Build trust relationships with other developers
- ✅ **Personalized**: Make trust decisions based on your own criteria
- ✅ **Cryptographically verifiable**: Reviews are signed and verifiable
- ✅ **Community-driven**: Leverage the Rust community's collective knowledge

**Cons**:
- ⚠️ **Requires active participation**: Need to build and maintain trust relationships
- ⚠️ **Manual reviews**: Requires developers to actually review code
- ⚠️ **Smaller ecosystem**: Less widely adopted than automated tools
- ⚠️ **Time investment**: Building a useful web of trust takes time
- ⚠️ **Less suitable for organizations**: More suited for individual developers

**When to Consider**:
- Individual developers or small teams
- Preference for decentralized, trust-based approach
- Willingness to invest time in building trust relationships
- Need for personalized trust decisions
- Working with less common or niche crates
- Desire to contribute to community security efforts

**CI Integration Example**:
```yaml
- name: Install cargo-crev
  run: cargo install cargo-crev

- name: Verify trust status
  run: cargo crev verify
  continue-on-error: true  # May not have trust relationships established
```

---

## Summary

These tools provide manual auditing and trust verification capabilities that complement automated tools:

- **cargo vet**: Consider for enterprise/organizational projects that need shared auditing from trusted entities
- **cargo crev**: Consider for individual developers or teams wanting decentralized, peer-to-peer trust verification

Both tools add supply chain trust verification beyond automated vulnerability scanning, but require manual maintenance and active participation. Evaluate based on project needs and available resources.

---

## References

- [cargo vet Documentation](https://mozilla.github.io/cargo-vet/)
- [cargo crev Documentation](https://github.com/crev-dev/cargo-crev)
