"""Pytest configuration and fixtures for FHIR Engine skills tests."""

import tempfile
import shutil
from pathlib import Path
import pytest


@pytest.fixture
def temp_install_dir():
    """Create a temporary directory for testing skill installation."""
    temp_dir = tempfile.mkdtemp(prefix="fhir_skills_test_")
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def skills_source_dir():
    """Get the path to the skills source directory."""
    return Path(__file__).parent.parent / "src" / "fhir_skills" / "skills"


@pytest.fixture
def expected_skills():
    """List of expected skill names."""
    return [
        "fhir-config-troubleshooting",
        "fhir-errors-debugger",
        "handler-patterns",
        "fhir-handler-generator",
        "fhir-custom-resource",
        "fhir-custom-datastore",
        "fhir-structuredefinition",
        "fhir-data-mapping",
        "fhir-project-setup",
    ]


@pytest.fixture
def project_setup_skill_triggers():
    """Sample prompts that should trigger the fhir-project-setup skill."""
    return [
        "create a new fhir project",
        "setup fhir web api",
        "I want to create a FHIR web API project with PostgreSQL",
        "initialize a new FHIR Engine project",
        "scaffold fhir api",
    ]
