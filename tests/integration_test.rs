use pretty_assertions::assert_eq;
use std::fs;
use std::path::PathBuf;
use std::process::Command;
use tempfile::TempDir;

fn get_binary_path() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_move_maker"))
}

#[test]
fn test_single_resource_file() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("single_resource.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(
        output.status.success(),
        "Command failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("# From: main.tf"));
    assert!(stdout.contains("moved"));
    assert!(stdout.contains("from = aws_instance.web"));
    assert!(stdout.contains("to = module.compute.aws_instance.web"));
}

#[test]
fn test_multiple_resources() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("multiple_resources.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    // Should have 3 moved blocks
    let moved_count = stdout.matches("moved").count();
    assert_eq!(moved_count, 3);

    assert!(stdout.contains("aws_instance.web1"));
    assert!(stdout.contains("aws_instance.web2"));
    assert!(stdout.contains("aws_s3_bucket.data"));
}

#[test]
fn test_mixed_resources_and_data() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("mixed_blocks.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    // Should have 1 moved block (resource only, data blocks are ignored)
    let moved_count = stdout.matches("moved").count();
    assert_eq!(moved_count, 1);

    assert!(stdout.contains("aws_instance.web"));
    // Data blocks should not be processed
    assert!(!stdout.contains("data.aws_ami.example"));
}

#[test]
fn test_multiple_files() {
    let temp_dir = TempDir::new().unwrap();
    let fixtures_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures");

    fs::copy(
        fixtures_dir.join("single_resource.tf"),
        temp_dir.path().join("main.tf"),
    )
    .unwrap();
    fs::copy(
        fixtures_dir.join("single_data.tf"),
        temp_dir.path().join("data.tf"),
    )
    .unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    // Should have 1 moved block (only from main.tf, data.tf is ignored)
    let moved_count = stdout.matches("moved").count();
    assert_eq!(moved_count, 1);

    assert!(stdout.contains("# From: main.tf"));
    // Data blocks should not be processed
    assert!(!stdout.contains("# From: data.tf"));
}

#[test]
fn test_invalid_hcl_file() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("invalid_syntax.tf");

    fs::copy(&fixture_file, temp_dir.path().join("invalid.tf")).unwrap();
    // Also add a valid file to ensure it still processes
    fs::copy(
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("tests")
            .join("fixtures")
            .join("single_resource.tf"),
        temp_dir.path().join("valid.tf"),
    )
    .unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    // Should still succeed (warnings go to stderr)
    assert!(output.status.success());

    // Should have warning about invalid file
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("Warning") || stderr.contains("invalid.tf"));

    // Should still process valid file
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("aws_instance.web"));
}

#[test]
fn test_empty_directory() {
    let temp_dir = TempDir::new().unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    // Should have no output or empty output
    assert!(stdout.trim().is_empty() || !stdout.contains("moved"));
}

#[test]
fn test_resource_with_count() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("count_resource.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    // Count doesn't affect the address, should still generate moved block
    assert!(stdout.contains("moved"));
    assert!(stdout.contains("from = aws_instance.web"));
    assert!(stdout.contains("to = module.compute.aws_instance.web"));
}

#[test]
fn test_resource_with_for_each() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("for_each_resource.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    // for_each doesn't affect the address, should still generate moved block
    assert!(stdout.contains("moved"));
    assert!(stdout.contains("from = aws_instance.web"));
    assert!(stdout.contains("to = module.compute.aws_instance.web"));
}

#[test]
fn test_module_name_with_hyphens() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("single_resource.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("my-module")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("module.my-module.aws_instance.web"));
}

#[test]
fn test_module_name_with_underscores() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("single_resource.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("my_module")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("module.my_module.aws_instance.web"));
}

#[test]
fn test_single_module_file() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("single_module.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("a")
        .output()
        .expect("Failed to execute command");

    assert!(
        output.status.success(),
        "Command failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("# From: main.tf"));
    assert!(stdout.contains("moved"));
    assert!(stdout.contains("from = module.web_server"));
    assert!(stdout.contains("to = module.a.module.web_server"));
}

#[test]
fn test_multiple_modules() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("multiple_modules.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    // Should have 3 moved blocks
    let moved_count = stdout.matches("moved").count();
    assert_eq!(moved_count, 3);

    assert!(stdout.contains("module.web_server"));
    assert!(stdout.contains("module.database"));
    assert!(stdout.contains("module.cache"));
    assert!(stdout.contains("from = module.web_server"));
    assert!(stdout.contains("to = module.compute.module.web_server"));
    assert!(stdout.contains("from = module.database"));
    assert!(stdout.contains("to = module.compute.module.database"));
    assert!(stdout.contains("from = module.cache"));
    assert!(stdout.contains("to = module.compute.module.cache"));
}

#[test]
fn test_mixed_resources_and_modules() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("mixed_resources_and_modules.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("compute")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    // Should have 4 moved blocks (2 resources + 2 modules, data blocks are ignored)
    let moved_count = stdout.matches("moved").count();
    assert_eq!(moved_count, 4);

    // Verify resources
    assert!(stdout.contains("aws_instance.web"));
    assert!(stdout.contains("aws_s3_bucket.data"));
    assert!(stdout.contains("from = aws_instance.web"));
    assert!(stdout.contains("to = module.compute.aws_instance.web"));
    assert!(stdout.contains("from = aws_s3_bucket.data"));
    assert!(stdout.contains("to = module.compute.aws_s3_bucket.data"));

    // Verify modules
    assert!(stdout.contains("module.web_server"));
    assert!(stdout.contains("module.database"));
    assert!(stdout.contains("from = module.web_server"));
    assert!(stdout.contains("to = module.compute.module.web_server"));
    assert!(stdout.contains("from = module.database"));
    assert!(stdout.contains("to = module.compute.module.database"));

    // Data blocks should not be processed
    assert!(!stdout.contains("data.aws_ami.example"));
}

#[test]
fn test_module_name_with_hyphens_for_modules() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("single_module.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("my-module")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("module.my-module.module.web_server"));
}

#[test]
fn test_module_name_with_underscores_for_modules() {
    let temp_dir = TempDir::new().unwrap();
    let fixture_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("single_module.tf");

    fs::copy(&fixture_file, temp_dir.path().join("main.tf")).unwrap();

    let binary = get_binary_path();
    let output = Command::new(&binary)
        .arg("--src")
        .arg(temp_dir.path())
        .arg("--module-name")
        .arg("my_module")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("module.my_module.module.web_server"));
}
