# FHIR Engine Skills Test Suite

This directory contains automated tests for the FHIR Engine Claude Skills package.

## Test Coverage

### 1. Installation Tests (`test_installation.py`)

Tests for skill installation functionality:
- ✅ Skills source directory exists
- ✅ All skills have SKILL.md files
- ✅ CLI install command works
- ✅ Skills installed to correct location (.claude/skills)
- ✅ All expected skills are installed
- ✅ Skill count matches
- ✅ README.md is installed
- ✅ CLI list command works
- ✅ CLI info command works

### 2. Skill Content Tests (`test_skill_content.py`)

Tests for fhir-project-setup skill content:
- ✅ Skill exists after installation
- ✅ Has all required sections (Questions 1-5, Steps 1-4)
- ✅ Has trigger phrases in frontmatter
- ✅ Has bash script template file
- ✅ Template has all required variables
- ✅ Has example configurations
- ✅ Includes new feature options (Redis, OpenAPI, etc.)
- ✅ Removed old options (Copy docs, Open VS Code)

### 3. Integration Tests (`test_integration.py`)

End-to-end tests for project creation:
- ✅ Bash script template has valid syntax
- ✅ Generated script can run successfully
- ✅ Project directory is created
- ✅ Solution and project files are created
- ✅ Git repository is initialized
- ✅ Template parameters are documented
- ✅ Trigger phrases match examples
- ✅ Parameters compatible with actual dotnet template (requires dotnet CLI)

## Running Tests

### Prerequisites

1. **Python 3.8+** installed
2. **pytest** installed:
   ```bash
   pip install pytest
   ```

3. **Optional**: .NET SDK and FHIR Engine templates (for full integration tests):
   ```bash
   dotnet new install Ihis.FhirEngine.Templates
   ```

### Run All Tests

```bash
# From repository root
pytest tests/ -v
```

### Run Specific Test Files

```bash
# Installation tests only
pytest tests/test_installation.py -v

# Content verification tests only
pytest tests/test_skill_content.py -v

# Integration tests only
pytest tests/test_integration.py -v
```

### Run Specific Tests

```bash
# Run a single test
pytest tests/test_installation.py::test_cli_install_command -v

# Run tests matching a pattern
pytest tests/ -k "project_setup" -v
```

### Skip Integration Tests

Integration tests that require dotnet CLI are automatically skipped if dotnet is not available:

```bash
# Run without dotnet CLI
pytest tests/ -v
# (dotnet-dependent tests will be skipped)
```

### Test with Coverage

```bash
# Install coverage
pip install pytest-cov

# Run with coverage report
pytest tests/ --cov=fhir_skills --cov-report=html -v

# View coverage report
open htmlcov/index.html
```

## Expected Test Results

### Minimal Environment (Python only)

```
tests/test_installation.py .............. [100%]    (9 tests)
tests/test_skill_content.py ........... [100%]      (9 tests)
tests/test_integration.py ....ss [83%]              (4 passed, 2 skipped)

=================== 22 passed, 2 skipped in 5.42s ===================
```

### Full Environment (Python + .NET SDK + FHIR Templates)

```
tests/test_installation.py .............. [100%]    (9 tests)
tests/test_skill_content.py ........... [100%]      (9 tests)
tests/test_integration.py ...... [100%]             (6 tests)

=================== 24 passed in 8.15s ===================
```

## Test Fixtures

Defined in `conftest.py`:

- **`temp_install_dir`**: Temporary directory for testing skill installation
- **`skills_source_dir`**: Path to source skills directory
- **`expected_skills`**: List of expected skill names
- **`project_setup_skill_triggers`**: Sample prompts that trigger the skill
- **`temp_project_dir`**: Temporary directory for project creation tests

## Continuous Integration

These tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest
      - name: Run tests
        run: pytest tests/ -v
```

## Adding New Tests

When adding new skills or features:

1. **Update fixtures** in `conftest.py`:
   - Add skill name to `expected_skills`
   - Add trigger phrases if applicable

2. **Add skill-specific tests** in `test_skill_content.py`:
   - Test skill exists
   - Test has required sections
   - Test has trigger phrases

3. **Add integration tests** if applicable in `test_integration.py`:
   - Test generated outputs
   - Test end-to-end workflows

## Troubleshooting

### Tests fail with "Skills source directory not found"

The package may not be installed. Install in development mode:
```bash
pip install -e .
```

### Tests fail with "dotnet: command not found"

Dotnet-dependent tests will be skipped. To run them:
1. Install .NET SDK: https://dotnet.microsoft.com/download
2. Install FHIR Engine templates:
   ```bash
   dotnet new install Ihis.FhirEngine.Templates
   ```

### Permission errors during cleanup

On Windows, temporary directories may be locked. Tests will continue, but cleanup warnings may appear. This is normal and can be ignored.

## Test Maintenance

- **Update test fixtures** when adding/removing skills
- **Keep trigger phrases** in sync with SKILL.md frontmatter
- **Update parameter lists** when template parameters change
- **Run tests locally** before committing changes
- **Check CI results** after pushing
