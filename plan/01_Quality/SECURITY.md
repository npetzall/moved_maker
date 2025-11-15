# Security: Vulnerability Scanning and Secure Practices

## Purpose
Implement security scanning, vulnerability detection, and secure coding practices to ensure the codebase and dependencies are secure.

## Features
- Dependency vulnerability scanning
- License compliance checking
- Unsafe code detection
- Binary dependency auditing
- Secure coding guidelines
- Automated security checks in CI/CD

## Compatibility
- ✅ Apple Silicon (ARM): Fully supported
- ✅ Linux (GitHub Actions): Fully supported

## Security Tools

### Option 1: cargo-deny ✅ Selected

**Overview**: Comprehensive tool for checking licenses, vulnerabilities, and banned dependencies

**Compatibility**:
- ✅ Apple Silicon (ARM): Fully supported
- ✅ Linux (GitHub Actions): Fully supported

**Installation**:
```bash
cargo install cargo-deny
```

**Usage**:
```bash
# Check all issues (licenses, vulnerabilities, banned deps)
cargo deny check --config .config/deny.toml

# Check only licenses
cargo deny check --config .config/deny.toml licenses

# Check only vulnerabilities
cargo deny check --config .config/deny.toml advisories

# Check only banned dependencies
cargo deny check --config .config/deny.toml bans
```

**Configuration**:
Create `.config/deny.toml` in the `.config` directory:
```toml
[advisories]
# Vulnerability database sources
vulnerability = "deny"
unmaintained = "warn"
notice = "warn"
ignore = [
    # Ignore specific advisories if needed (with justification)
]

[licenses]
# License policy
default = "deny"
copyleft = "deny"
# Allow specific licenses
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
]
# Exceptions for specific crates
exceptions = [
    # { name = "crate-name", allow = ["license"] }
]

[bans]
# Ban specific crates or versions
multiple-versions = "warn"
wildcards = "deny"
# Specific crate bans
deny = [
    # { name = "insecure-crate", reason = "Security vulnerability" }
]
```

**Pros**:
- ✅ **Comprehensive**: Handles licenses, vulnerabilities, and banned deps in one tool
- ✅ **Configurable**: Fine-grained control over policies
- ✅ **Fast**: Efficient scanning
- ✅ **CI-friendly**: Easy to integrate into workflows
- ✅ **Well-maintained**: Active development, widely used

**Cons**:
- ⚠️ Requires configuration file setup
- ⚠️ May need periodic policy updates

**CI Integration Example**:
```yaml
- name: Install cargo-deny
  run: cargo install cargo-deny

- name: Run security checks
  run: cargo deny check --config .config/deny.toml
```

---

### Option 2: cargo-audit ✅ Selected

**Overview**: Scans dependencies for known vulnerabilities using RustSec Advisory Database

**Compatibility**:
- ✅ Apple Silicon (ARM): Fully supported
- ✅ Linux (GitHub Actions): Fully supported

**Installation**:
```bash
cargo install cargo-audit
```

**Usage**:
```bash
# Scan for vulnerabilities (automatically updates database)
cargo audit

# Output JSON format
cargo audit --json

# Check only for critical vulnerabilities (automatically updates database)
cargo audit --deny warnings
```

**Pros**:
- ✅ **Focused**: Specialized for vulnerability scanning
- ✅ **Simple**: Easy to use, minimal configuration
- ✅ **Up-to-date**: Uses RustSec Advisory Database
- ✅ **Fast**: Quick vulnerability checks

**Cons**:
- ⚠️ **Limited scope**: Only checks vulnerabilities, not licenses
- ⚠️ **Less configurable**: Fewer policy options than cargo-deny

**CI Integration Example**:
```yaml
- name: Install cargo-audit
  run: cargo install cargo-audit

- name: Check for vulnerabilities (automatically updates database)
  run: cargo audit --deny warnings
```

---

### Option 3: cargo-geiger ✅ Selected

**Overview**: Detects unsafe code usage in dependencies

**Compatibility**:
- ✅ Apple Silicon (ARM): Compatible
- ✅ Linux (GitHub Actions): Compatible

**Installation**:
```bash
cargo install cargo-geiger
```

**Usage**:
```bash
# Scan for unsafe code
cargo geiger

# Output JSON
cargo geiger --output-format json

# Exclude test dependencies
cargo geiger --exclude-tests
```

**Pros**:
- ✅ **Unsafe detection**: Identifies unsafe code usage
- ✅ **Dependency analysis**: Shows unsafe code in dependencies
- ✅ **Visual output**: Clear reporting of unsafe usage

**Cons**:
- ⚠️ **Informational**: Unsafe code isn't necessarily bad, but good to be aware
- ⚠️ **Slower**: Can be slower on large projects

**CI Integration Example**:
```yaml
- name: Install cargo-geiger
  run: cargo install cargo-geiger

- name: Check unsafe code usage (blocking)
  run: cargo geiger --output-format json > geiger-report.json
```

---

### Option 6: cargo-auditable ✅ Selected

**Overview**: Embeds dependency information into compiled binaries, enabling vulnerability scanning of production binaries

**Compatibility**:
- ✅ Apple Silicon (ARM): Fully supported
- ✅ Linux (GitHub Actions): Fully supported
- ✅ Windows: Fully supported
- ✅ WebAssembly: Supported (v0.6.3+)

**Installation**:
```bash
cargo install cargo-auditable
```

**Usage**:
```bash
# Build with embedded dependency information
cargo auditable build --release

# Audit a compiled binary
cargo audit bin target/release/your_binary

# Build normally (without embedding)
cargo build --release
```

**Pros**:
- ✅ **Production binary auditing**: Audit deployed binaries without source code access
- ✅ **Supply chain transparency**: Verify exact dependencies in production binaries
- ✅ **Minimal overhead**: Typically adds less than 4KB to binary size
- ✅ **Complements cargo-audit**: Extends vulnerability scanning to binaries
- ✅ **Release security**: Enables post-deployment vulnerability checks

**Cons**:
- ⚠️ **Build-time requirement**: Must use `cargo auditable build` instead of `cargo build`
- ⚠️ **Release-focused**: Most valuable for production/release builds
- ⚠️ **Requires cargo-audit**: Needs cargo-audit to scan the embedded data

**When to Use**:
- Building release/production binaries
- Distributing binaries to users
- Need to audit production deployments
- Want supply chain transparency in releases
- Post-deployment vulnerability verification

**CI Integration Example**:
```yaml
- name: Install cargo-auditable
  run: cargo install cargo-auditable

- name: Build with embedded dependency info
  run: cargo auditable build --release

- name: Audit release binary
  run: cargo audit bin target/release/move_maker
```

---

## Recommendation

### ✅ Selected Tools

Four security tools are selected and will be used together to provide comprehensive security coverage:

### Security Tool Status Summary

| Tool | Status | Blocking | Use Case |
|------|--------|----------|----------|
| **cargo-deny** | ✅ Selected | ✅ Blocking | Comprehensive security gate (licenses, vulnerabilities, banned deps) |
| **cargo-audit** | ✅ Selected | ✅ Blocking | Vulnerability scanning with RustSec Advisory Database |
| **cargo-geiger** | ✅ Selected | ✅ Blocking | Unsafe code detection in dependencies |
| **cargo-auditable** | ✅ Selected | ✅ Blocking | Binary dependency auditing for release builds |

**Note**: All selected security tools are **blocking** in all workflows. They must pass before builds or releases proceed.

### Primary: cargo-deny ✅ Selected

**Rationale**:
1. **Comprehensive**: Handles vulnerabilities, licenses, and banned dependencies
2. **Configurable**: Fine-grained policy control
3. **CI-friendly**: Easy integration with clear exit codes
4. **Well-maintained**: Active development and wide adoption
5. **Primary security gate**: Blocks on vulnerabilities and license violations

### Secondary: cargo-audit ✅ Selected

**Use for**:
- Redundancy and verification of vulnerability scanning
- Additional vulnerability database coverage
- Complementary checks alongside cargo-deny
- Blocking on critical vulnerabilities

### Unsafe Code Detection: cargo-geiger ✅ Selected

**Use for**:
- Understanding unsafe code usage in dependencies
- Security auditing and awareness
- Visibility into unsafe code patterns
- Blocking on unsafe code detection

### Release Builds: cargo-auditable ✅ Selected

**Use for**:
- Embedding dependency information in release binaries
- Production binary vulnerability auditing
- Supply chain transparency in deployed artifacts
- Post-deployment security verification
- Enabling `cargo audit bin` to scan compiled binaries

---

## Implementation Strategy

### Phase 1: Comprehensive Security (cargo-deny) ✅ Selected
1. Install `cargo-deny`
2. Create `.config/deny.toml` configuration
3. Configure license policy
4. Configure vulnerability policy
5. Run initial checks
6. Address any issues
7. Add to CI workflow (blocking on failures)

### Phase 2: Vulnerability Verification (cargo-audit) ✅ Selected
1. Install `cargo-audit`
2. Update vulnerability database
3. Run initial scan
4. Address any found vulnerabilities
5. Add to CI workflow (blocking on vulnerabilities)

### Phase 3: Unsafe Code Awareness (cargo-geiger) ✅ Selected
1. Install `cargo-geiger`
2. Run initial scan
3. Review unsafe code usage
4. Add to CI workflow (blocking)

### Phase 4: Binary Auditing (cargo-auditable) ✅ Selected
1. Install `cargo-auditable`
2. Update release build process to use `cargo auditable build`
3. Test binary auditing with `cargo audit bin`
4. Add to release/CI workflow for production builds
5. Verify embedded dependency information in release binaries

---

## Secure Coding Practices

### 1. Input Validation
- Validate all user inputs (file paths, module names)
- Sanitize file paths to prevent directory traversal
- Validate HCL input before parsing

### 2. Error Handling
- Use `anyhow` for error handling (already planned)
- Avoid exposing sensitive information in error messages
- Log errors appropriately without leaking data

### 3. File Operations
- Validate file paths before operations
- Use safe file reading methods
- Handle file system errors gracefully

### 4. Dependency Management
- Keep dependencies up to date
- Review new dependencies before adding
- Use `cargo audit` or `cargo-deny` regularly
- Prefer well-maintained crates

### 5. Memory Safety
- Leverage Rust's memory safety guarantees
- Minimize unsafe code usage
- Review any unsafe blocks carefully

---

## CI/CD Integration

### Security Checks Workflow

Add to `.github/workflows/quality.yml`:

```yaml
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install security tools
        run: cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable

      - name: Run cargo-deny checks (blocking)
        run: cargo deny check --config .config/deny.toml

      - name: Run cargo-audit checks (blocking)
        run: cargo audit --deny warnings

      - name: Run cargo-geiger scan (blocking)
        run: cargo geiger --output-format json > geiger-report.json

      - name: Build with embedded dependency info
        run: cargo auditable build --release

      - name: Audit release binary
        run: cargo audit bin target/release/move_maker
```

### Integration with Release Process

Security checks should block releases if vulnerabilities are found:

```yaml
# In cd.yml workflow
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      # ... security checks ...

  build-and-release:
    needs: security  # Only build if security checks pass
    # ... build steps ...
```

---

## Local Development Setup

### Apple Silicon (macOS)

```bash
# Install security tools
cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable

# Initialize cargo-deny
cargo deny init

# Move deny.toml to .config directory
mkdir -p .config
mv deny.toml .config/deny.toml

# Edit .config/deny.toml to configure policies

# Run security checks
cargo deny check --config .config/deny.toml
cargo audit
cargo geiger

# Build release with embedded dependency info
cargo auditable build --release

# Audit the compiled binary
cargo audit bin target/release/move_maker
```

### Linux

```bash
# Install security tools
cargo install cargo-deny cargo-audit cargo-geiger cargo-auditable

# Initialize cargo-deny
cargo deny init

# Move deny.toml to .config directory
mkdir -p .config
mv deny.toml .config/deny.toml

# Edit .config/deny.toml to configure policies

# Run security checks
cargo deny check --config .config/deny.toml
cargo audit
cargo geiger

# Build release with embedded dependency info
cargo auditable build --release

# Audit the compiled binary
cargo audit bin target/release/move_maker
```

---

## Security Goals

### Initial Goals
- ✅ Zero known vulnerabilities in dependencies
- ✅ License compliance verified
- ✅ Security checks in CI/CD pipeline
- ✅ Regular dependency updates

### Target Goals (Long-term)
- ✅ Automated dependency updates (Dependabot)
- ✅ Security advisories monitoring
- ✅ Regular security audits
- ✅ Binary signing for releases

---

## Dependabot Integration

Enable GitHub Dependabot for automated dependency updates:

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "your-username"
    labels:
      - "dependencies"
      - "security"
```

---

## References

### Selected Tools
- [cargo-deny Documentation](https://github.com/EmbarkStudios/cargo-deny)
- [cargo-audit Documentation](https://github.com/rustsec/rustsec/tree/main/cargo-audit)
- [cargo-geiger Documentation](https://github.com/rust-secure-code/cargo-geiger)
- [cargo-auditable Documentation](https://github.com/rust-secure-code/cargo-auditable)

### General Security Resources
- [RustSec Advisory Database](https://github.com/rustsec/advisory-db)
- [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Rust Security Guidelines](https://rustsec.org/)
