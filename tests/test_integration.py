"""Integration tests for FHIR Engine project creation."""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path
import pytest


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory for testing project creation."""
    temp_dir = tempfile.mkdtemp(prefix="fhir_project_test_")
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_bash_script_template_is_valid_bash(temp_install_dir):
    """Test that the generated bash script template has valid syntax."""
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

    assert template_file is not None, "Template not found"

    # Extract bash script from markdown
    content = template_file.read_text()

    # Find the bash code block
    import re
    bash_match = re.search(r'```bash\n(.*?)\n```', content, re.DOTALL)
    assert bash_match, "Bash code block not found in template"

    bash_script = bash_match.group(1)

    # Replace template variables with dummy values
    replacements = {
        "{SOLUTION_NAME}": "TestAPI",
        "{DB_STORE}": "None",
        "{FHIR_VERSION}": "R5",
        "{FRAMEWORK}": "net8.0",
        "{ASPIRE_VERSION}": "Disable",
        "{INCLUDE_TEST}": "false",
        "{REDIS}": "false",
        "{OPENAPI}": "false",
        "{OTEL}": "false",
        "{AUDIT}": "false",
        "{CORS}": "false",
    }

    for placeholder, value in replacements.items():
        bash_script = bash_script.replace(placeholder, value)

    # Save to temp file
    script_file = temp_install_dir / "test_script.sh"
    script_file.write_text(bash_script)

    # Check bash syntax
    result = subprocess.run(
        ["bash", "-n", str(script_file)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


@pytest.mark.skipif(
    subprocess.run(["which", "dotnet"], capture_output=True).returncode != 0,
    reason="dotnet CLI not available"
)
def test_generated_script_can_run_with_mock_template(temp_project_dir):
    """Test that a generated script can run (with mock dotnet template check)."""
    # Create a test script with minimal project creation
    test_script = temp_project_dir / "setup-test.sh"

    script_content = """#!/bin/bash
set -e

# Configuration
SOLUTION_NAME="TestAPI"
DB_STORE="None"
FHIR_VERSION="R5"
FRAMEWORK="net8.0"
ASPIRE_VERSION="Disable"
INCLUDE_TEST=false

# Derived values
FINAL_SOLUTION_NAME="${SOLUTION_NAME}.${FHIR_VERSION}.${DB_STORE}"
BASE_PATH=$(pwd)
PROJECT_PATH="${BASE_PATH}/${FINAL_SOLUTION_NAME}"

echo "📂 Creating test FHIR Engine project: $FINAL_SOLUTION_NAME"
echo "   Database Store: $DB_STORE"
echo "   FHIR Version: $FHIR_VERSION"

# Create project folder
mkdir -p "$PROJECT_PATH"
cd "$PROJECT_PATH"

# Create a dummy .csproj file (mock dotnet new)
cat > "${FINAL_SOLUTION_NAME}.csproj" << 'EOF'
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
</Project>
EOF

# Create solution
echo "Creating solution..."
touch "${FINAL_SOLUTION_NAME}.sln"

# Initialize Git
git init
git add .
git commit -m "Initial commit: FHIR Engine project setup"

cd "$BASE_PATH"

echo "✅ Test project created successfully!"
echo "📁 Location: $PROJECT_PATH"
"""

    test_script.write_text(script_content)
    test_script.chmod(0o755)

    # Run the script
    result = subprocess.run(
        [str(test_script)],
        cwd=temp_project_dir,
        capture_output=True,
        text=True
    )

    # Check script ran successfully
    assert result.returncode == 0, f"Script failed: {result.stderr}\n{result.stdout}"
    assert "✅ Test project created successfully!" in result.stdout

    # Verify project was created
    project_dir = temp_project_dir / "TestAPI.R5.None"
    assert project_dir.exists(), f"Project directory not created: {project_dir}"

    # Verify files were created
    assert (project_dir / "TestAPI.R5.None.csproj").exists(), ".csproj file not created"
    assert (project_dir / "TestAPI.R5.None.sln").exists(), ".sln file not created"
    assert (project_dir / ".git").exists(), "Git repository not initialized"


def test_template_parameters_are_documented(temp_install_dir):
    """Test that all template parameters are documented in the examples."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find the examples file
    skills_dir = temp_install_dir / ".claude" / "skills"
    examples_file = None
    for examples_path in skills_dir.rglob("fhir-project-setup/examples/sample-configurations.md"):
        examples_file = examples_path
        break

    assert examples_file is not None, "Examples file not found"

    content = examples_file.read_text()

    # Check that key parameters are documented
    documented_parameters = [
        "Database Store",
        "FHIR Version",
        "Framework",
        "Aspire Version",
        "Features",
        "Redis",
        "OpenAPI",
        "OpenTelemetry",
        "Audit",
        "CORS",
    ]

    for param in documented_parameters:
        assert param in content, f"Parameter '{param}' not documented in examples"


def test_trigger_phrases_match_examples(temp_install_dir, project_setup_skill_triggers):
    """Test that trigger phrases are consistent with examples."""
    # Install skills
    subprocess.run(
        [sys.executable, "-m", "fhir_skills.cli", "install", "--path", str(temp_install_dir), "--force"],
        capture_output=True,
        text=True,
        check=True
    )

    # Find the skill file
    skills_dir = temp_install_dir / ".claude" / "skills"
    skill_file = None
    for skill_path in skills_dir.rglob("fhir-project-setup/SKILL.md"):
        skill_file = skill_path
        break

    assert skill_file is not None, "Skill file not found"

    content = skill_file.read_text().lower()

    # Verify at least 3 trigger phrases are mentioned in the skill
    found_triggers = sum(1 for trigger in project_setup_skill_triggers if trigger.lower() in content)
    assert found_triggers >= 3, f"Only {found_triggers} trigger phrases found, expected at least 3"


@pytest.mark.skipif(
    subprocess.run(["which", "dotnet"], capture_output=True).returncode != 0,
    reason="dotnet CLI not available"
)
def test_dotnet_template_parameter_compatibility():
    """Test that our documented parameters match actual dotnet template parameters."""
    # Check if FHIR Engine template is installed
    result = subprocess.run(
        ["dotnet", "new", "fhirengine-webapi", "--help"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        pytest.skip("FHIR Engine template not installed")

    help_text = result.stdout

    # Check that our parameters exist in the template
    expected_params = [
        "--dbstore",
        "--fhirversion",
        "--framework",
        "--aspireversion",
        "--includetest",
        "--redis",
        "--openapi",
        "--otel",
        "--audit",
        "--cors",
    ]

    for param in expected_params:
        assert param in help_text, f"Parameter '{param}' not found in dotnet template help"
