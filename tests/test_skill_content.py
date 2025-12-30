"""Tests for FHIR Engine skill content verification."""

import subprocess
import sys
import re
from pathlib import Path


def test_project_setup_skill_exists(temp_install_dir):
    """Test that the fhir-project-setup skill is installed."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find the skill
    skills_dir = temp_install_dir / ".claude" / "skills"
    skill_file = None

    # Search for the skill in both root and codegen folders
    for skill_path in skills_dir.rglob("fhir-project-setup/SKILL.md"):
        skill_file = skill_path
        break

    assert skill_file is not None, "fhir-project-setup skill not found"
    assert skill_file.exists(), f"SKILL.md not found at {skill_file}"


def test_project_setup_has_required_sections(temp_install_dir):
    """Test that fhir-project-setup SKILL.md has all required sections."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find and read the skill
    skills_dir = temp_install_dir / ".claude" / "skills"
    skill_file = None
    for skill_path in skills_dir.rglob("fhir-project-setup/SKILL.md"):
        skill_file = skill_path
        break

    assert skill_file is not None, "fhir-project-setup skill not found"

    content = skill_file.read_text()

    # Check for required sections (updated for dual-mode structure)
    required_sections = [
        "name: fhir-project-setup",
        "Question 1:",
        "Question 2:",
        "Question 3:",
        "Question 4:",
        "Question 5:",
        "Step 0: Detect Project Mode",
        "Step 1A: Gather Project Configuration",
        "Step 2: Process Answers",
        "Step 3: Display Configuration Summary",
        "Step 4: Generate and Execute Script",
        "Mode A: Create New Project",
        "Mode B: Add Features",
    ]

    for section in required_sections:
        assert section in content, f"Required section '{section}' not found in SKILL.md"


def test_project_setup_has_trigger_phrases(temp_install_dir, project_setup_skill_triggers):
    """Test that fhir-project-setup has trigger phrases in frontmatter."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find and read the skill
    skills_dir = temp_install_dir / ".claude" / "skills"
    skill_file = None
    for skill_path in skills_dir.rglob("fhir-project-setup/SKILL.md"):
        skill_file = skill_path
        break

    assert skill_file is not None, "fhir-project-setup skill not found"

    content = skill_file.read_text()

    # Extract frontmatter
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match, "YAML frontmatter not found"

    frontmatter = frontmatter_match.group(1)

    # Check for triggers section
    assert "triggers:" in frontmatter, "Triggers section not found in frontmatter"

    # Check that at least one trigger phrase is present
    trigger_found = False
    for trigger in project_setup_skill_triggers:
        if trigger.lower() in content.lower():
            trigger_found = True
            break

    assert trigger_found, f"None of the expected trigger phrases found: {project_setup_skill_triggers}"


def test_project_setup_has_template_file(temp_install_dir):
    """Test that fhir-project-setup has the bash script template."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find the template
    skills_dir = temp_install_dir / ".claude" / "skills"
    template_file = None
    for template_path in skills_dir.rglob("fhir-project-setup/templates/setup-project.sh.md"):
        template_file = template_path
        break

    assert template_file is not None, "Bash script template not found"
    assert template_file.exists(), f"Template file not found at {template_file}"

    # Verify template content
    content = template_file.read_text()

    # Check for required template variables
    required_vars = [
        "{SOLUTION_NAME}",
        "{DB_STORE}",
        "{FHIR_VERSION}",
        "{FRAMEWORK}",
        "{ASPIRE_VERSION}",
        "{INCLUDE_TEST}",
        "{REDIS}",
        "{OPENAPI}",
        "{OTEL}",
        "{AUDIT}",
        "{CORS}",
    ]

    for var in required_vars:
        assert var in content, f"Required template variable '{var}' not found in template"


def test_project_setup_has_examples(temp_install_dir):
    """Test that fhir-project-setup has example configurations."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find the examples
    skills_dir = temp_install_dir / ".claude" / "skills"
    examples_file = None
    for examples_path in skills_dir.rglob("fhir-project-setup/examples/sample-configurations.md"):
        examples_file = examples_path
        break

    assert examples_file is not None, "Examples file not found"
    assert examples_file.exists(), f"Examples file not found at {examples_file}"

    # Verify examples content
    content = examples_file.read_text()

    # Check for example configurations
    assert "Example 1:" in content, "Example 1 not found"
    assert "Example 2:" in content, "Example 2 not found"
    assert "Database Store:" in content or "Database store:" in content, "Database store configuration not found"
    assert "FHIR Version:" in content, "FHIR version not found"


def test_project_setup_has_new_features(temp_install_dir):
    """Test that fhir-project-setup includes the new feature options."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find and read the skill
    skills_dir = temp_install_dir / ".claude" / "skills"
    skill_file = None
    for skill_path in skills_dir.rglob("fhir-project-setup/SKILL.md"):
        skill_file = skill_path
        break

    assert skill_file is not None, "fhir-project-setup skill not found"

    content = skill_file.read_text()

    # Check for new features
    new_features = [
        "Include Test Project",
        "Redis Caching",
        "OpenAPI/Swagger",
        "OpenTelemetry",
        "Audit Logging",
        "CORS",
    ]

    for feature in new_features:
        assert feature in content, f"New feature '{feature}' not found in SKILL.md"


def test_no_removed_options(temp_install_dir):
    """Test that removed options are not present in the skill."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find and read the skill
    skills_dir = temp_install_dir / ".claude" / "skills"
    skill_file = None
    for skill_path in skills_dir.rglob("fhir-project-setup/SKILL.md"):
        skill_file = skill_path
        break

    assert skill_file is not None, "fhir-project-setup skill not found"

    content = skill_file.read_text()

    # Check that old options are removed from questions
    # Note: These might still appear in other contexts, so we check the Questions section
    # Updated to use new section name "Step 1A: Gather Project Configuration"
    if "### Step 1A: Gather Project Configuration" in content and "### Step 2:" in content:
        questions_section = content.split("### Step 1A: Gather Project Configuration")[1].split("### Step 2:")[0]
    else:
        # If sections not found, test passes (structure might have changed)
        questions_section = content

    # These should NOT be in the questions section
    removed_options = [
        "Copy documentation templates",
        "Open in VS Code",
    ]

    for option in removed_options:
        assert option not in questions_section, f"Removed option '{option}' still found in questions section"
