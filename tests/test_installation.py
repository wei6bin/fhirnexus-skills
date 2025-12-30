"""Tests for FHIR Engine skills installation."""

import subprocess
import sys
from pathlib import Path


def test_skills_source_directory_exists(skills_source_dir):
    """Test that the skills source directory exists in the package."""
    assert skills_source_dir.exists(), f"Skills source directory not found: {skills_source_dir}"
    assert skills_source_dir.is_dir(), "Skills source path is not a directory"


def test_all_skills_have_skill_md(skills_source_dir):
    """Test that all skill directories contain a SKILL.md file."""
    skill_files = list(skills_source_dir.rglob("SKILL.md"))
    assert len(skill_files) >= 9, f"Expected at least 9 skills, found {len(skill_files)}"

    # Verify each SKILL.md is in a skill directory
    for skill_file in skill_files:
        assert skill_file.name == "SKILL.md", f"Expected SKILL.md, got {skill_file.name}"
        assert skill_file.exists(), f"SKILL.md not found: {skill_file}"


def test_cli_install_command(temp_install_dir):
    """Test that the CLI install command works."""
    # Run the install command
    result = subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True
    )

    # Check command succeeded
    assert result.returncode == 0, f"Install failed: {result.stderr}"

    # Check expected output
    assert "Successfully installed" in result.stdout
    assert ".claude/skills" in result.stdout


def test_skills_installed_to_correct_location(temp_install_dir):
    """Test that skills are installed to .claude/skills directory."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Check .claude/skills directory exists
    skills_dir = temp_install_dir / ".claude" / "skills"
    assert skills_dir.exists(), f"Skills directory not created: {skills_dir}"
    assert skills_dir.is_dir(), "Skills path is not a directory"


def test_all_expected_skills_installed(temp_install_dir, expected_skills):
    """Test that all expected skills are installed."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find all SKILL.md files
    skills_dir = temp_install_dir / ".claude" / "skills"
    skill_files = list(skills_dir.rglob("SKILL.md"))
    installed_skills = sorted(set(f.parent.name for f in skill_files))

    # Check all expected skills are present
    for skill in expected_skills:
        assert skill in installed_skills, f"Expected skill '{skill}' not found in installed skills: {installed_skills}"


def test_skill_count_matches(temp_install_dir):
    """Test that the correct number of skills are installed."""
    # Install skills
    result = subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find all SKILL.md files
    skills_dir = temp_install_dir / ".claude" / "skills"
    skill_files = list(skills_dir.rglob("SKILL.md"))

    # Verify count in output matches actual count
    assert f"Successfully installed {len(skill_files)} skills!" in result.stdout


def test_readme_installed(temp_install_dir):
    """Test that README.md is installed with the skills."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Check README exists
    readme = temp_install_dir / ".claude" / "skills" / "README.md"
    assert readme.exists(), f"README.md not found: {readme}"
    assert readme.stat().st_size > 0, "README.md is empty"


def test_cli_list_command():
    """Test that the CLI list command works."""
    result = subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "list"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"List command failed: {result.stderr}"
    assert "FHIR Engine Claude Skills" in result.stdout
    assert "fhir-project-setup" in result.stdout
    assert "Total:" in result.stdout


def test_cli_info_command():
    """Test that the CLI info command works."""
    result = subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "info"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Info command failed: {result.stderr}"
    assert "FHIR Engine Claude Skills" in result.stdout
    assert "Commands:" in result.stdout
