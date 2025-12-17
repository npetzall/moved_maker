# REQ: Manual Trust Verification Tools

**Status**: 📋 Planned

## Overview
Evaluate and implement manual code review and trust verification tools (cargo vet or cargo crev) to complement automated security scanning and add supply chain trust verification.

## Motivation
Currently, the project relies on automated vulnerability scanning tools (e.g., cargo audit, Dependabot) to identify known security issues in dependencies. However, automated tools cannot verify:
- Code quality and trustworthiness of dependencies
- Supply chain integrity beyond known CVEs
- Whether dependencies have been manually reviewed by trusted entities
- Personal or organizational trust relationships with dependency maintainers

Manual trust verification tools provide an additional layer of security by enabling:
- Verification that dependencies have been audited by trusted organizations or individuals
- Building a web of trust with other developers and organizations
- Defense-in-depth security strategy beyond automated scanning
- Supply chain trust verification for critical dependencies

## Current Behavior
The project currently uses automated security scanning tools:
- `cargo audit` for vulnerability detection
- Dependabot for automated dependency updates and security alerts
- Automated CI/CD checks for known CVEs

There is no mechanism for manual trust verification or auditing of dependencies beyond automated vulnerability scanning.

## Proposed Behavior
Evaluate and implement one of two manual trust verification tools:

### Option 1: cargo vet
Shared auditing system that allows projects to import audit records from trusted entities (developed by Mozilla). Well-suited for enterprise/organizational projects.

**Key Features**:
- Import audits from trusted sources (e.g., Mozilla)
- Verify that dependencies have been audited by trusted organizations
- Certify dependencies as audited
- Check audit status of all dependencies

### Option 2: cargo crev
Decentralized code review system that enables developers to review and sign off on Rust crates, building a web of trust. Well-suited for individual developers or small teams.

**Key Features**:
- Review and sign off on crates
- Build trust relationships with other developers
- Verify trust status of dependencies
- Publish reviews to the community

Both tools add supply chain trust verification beyond automated vulnerability scanning but require manual maintenance and active participation.

## Use Cases
- Verify that critical dependencies have been audited by trusted organizations
- Build trust relationships with other developers in the Rust ecosystem
- Add defense-in-depth security beyond automated vulnerability scanning
- Certify dependencies as manually reviewed and trusted
- Contribute to community security efforts by publishing reviews
- Import and leverage audits from trusted organizations (cargo vet)
- Make personalized trust decisions based on web of trust (cargo crev)

## Implementation Considerations

### Tool Selection
- **cargo vet**: Better for enterprise/organizational projects that can leverage shared audits from trusted entities
- **cargo crev**: Better for individual developers or small teams wanting decentralized, peer-to-peer trust verification

### Compatibility
Both tools are fully compatible with:
- ✅ Apple Silicon (ARM): Fully supported
- ✅ Linux (GitHub Actions): Fully supported

### Installation
```bash
# Option 1: cargo vet
cargo install cargo-vet

# Option 2: cargo crev
cargo install cargo-crev
```

### CI Integration
Both tools can be integrated into CI/CD workflows:

**cargo vet**:
```yaml
- name: Install cargo-vet
  run: cargo install cargo-vet

- name: Import audits from trusted sources
  run: cargo vet import

- name: Check audit status
  run: cargo vet check
```

**cargo crev**:
```yaml
- name: Install cargo-crev
  run: cargo install cargo-crev

- name: Verify trust status
  run: cargo crev verify
  continue-on-error: true  # May not have trust relationships established
```

### Maintenance Requirements
- **cargo vet**: Requires identifying and trusting auditing organizations, maintaining audit records
- **cargo crev**: Requires building and maintaining trust relationships, performing manual reviews

### Prerequisites
- Decision on which tool to use (vet vs crev)
- For cargo vet: Identification of trusted auditing organizations
- For cargo crev: Willingness to invest time in building trust relationships

## Alternatives Considered

### Option 1: cargo vet
**Pros**:
- Shared auditing from trusted organizations (e.g., Mozilla)
- Reduced redundancy in auditing efforts
- Organization-friendly approach
- Well-established for enterprise use

**Cons**:
- Requires trusted sources to be identified
- Manual process requiring human reviewers
- Maintenance overhead for audit records
- Less useful for small projects

**When to Choose**: Enterprise or organizational projects with ability to leverage audits from trusted organizations

### Option 2: cargo crev
**Pros**:
- Decentralized, peer-to-peer trust model
- Personalized trust decisions
- Cryptographically verifiable reviews
- Community-driven approach

**Cons**:
- Requires active participation and trust relationship building
- Manual reviews required
- Smaller ecosystem adoption
- Time investment to build useful web of trust
- Less suitable for organizations

**When to Choose**: Individual developers or small teams with preference for decentralized approach

### Alternative: Do Nothing
Continue relying solely on automated vulnerability scanning without manual trust verification.

**Why Rejected**: While automated tools are essential, manual trust verification adds an important layer of supply chain security that complements automated scanning.

## Impact
- **Breaking Changes**: No breaking changes expected
- **Documentation**:
  - Update security documentation to include manual trust verification process
  - Document tool selection decision and rationale
  - Add usage instructions for chosen tool
  - Update CI/CD documentation with integration steps
- **Testing**:
  - Test CI integration with chosen tool
  - Verify tool works in both local and CI environments
  - Test with existing dependency set
- **Dependencies**:
  - No new runtime dependencies
  - Development tool dependency: `cargo-vet` or `cargo-crev` (installed via `cargo install`)
  - May require additional CI time for trust verification checks

## References
- [cargo vet Documentation](https://mozilla.github.io/cargo-vet/)
- [cargo crev Documentation](https://github.com/crev-dev/cargo-crev)
