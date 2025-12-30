# Testing Guide for FHIR Engine Skills

This guide shows how to test the FHIR Engine skills installation and verify the project setup skill works correctly.

## Quick Start

### 1. Install Package in Development Mode

```bash
# From repository root
pip install -e .
```

### 2. Install Test Dependencies

```bash
pip install pytest
```

### 3. Run All Tests

```bash
pytest tests/ -v
```

**Expected Output:**
```
============================== test session starts ==============================
...
tests/test_installation.py::test_skills_source_directory_exists PASSED   [  4%]
tests/test_installation.py::test_all_skills_have_skill_md PASSED         [  9%]
tests/test_installation.py::test_cli_install_command PASSED              [ 14%]
tests/test_installation.py::test_skills_installed_to_correct_location PASSED [ 19%]
tests/test_installation.py::test_all_expected_skills_installed PASSED    [ 23%]
tests/test_installation.py::test_skill_count_matches PASSED              [ 28%]
tests/test_installation.py::test_readme_installed PASSED                 [ 33%]
tests/test_installation.py::test_cli_list_command PASSED                 [ 38%]
tests/test_installation.py::test_cli_info_command PASSED                 [ 42%]
tests/test_integration.py::test_bash_script_template_is_valid_bash PASSED [ 47%]
tests/test_integration.py::test_generated_script_can_run_with_mock_template PASSED [ 52%]
tests/test_integration.py::test_template_parameters_are_documented PASSED [ 57%]
tests/test_integration.py::test_trigger_phrases_match_examples PASSED    [ 61%]
tests/test_integration.py::test_dotnet_template_parameter_compatibility PASSED [ 66%]
tests/test_skill_content.py::test_project_setup_skill_exists PASSED      [ 71%]
tests/test_skill_content.py::test_project_setup_has_required_sections PASSED [ 76%]
tests/test_skill_content.py::test_project_setup_has_trigger_phrases PASSED [ 80%]
tests/test_skill_content.py::test_project_setup_has_template_file PASSED [ 85%]
tests/test_skill_content.py::test_project_setup_has_examples PASSED      [ 90%]
tests/test_skill_content.py::test_project_setup_has_new_features PASSED  [ 95%]
tests/test_skill_content.py::test_no_removed_options PASSED              [100%]

============================== 21 passed in 0.95s ==============================
```

## Test Coverage

✅ **21 tests** covering:
- **9 tests** for installation verification
- **7 tests** for skill content verification
- **5 tests** for integration and script generation

### Installation Tests

Verify that:
- Skills source directory exists
- All skills have SKILL.md files
- CLI commands work (install, list, info)
- Skills are installed to `.claude/skills`
- All 9 expected skills are present
- README is included

### Skill Content Tests

Verify that `fhir-project-setup` skill:
- Exists after installation
- Has all 5 questions in SKILL.md
- Has all 4 steps (Gather, Process, Display, Execute)
- Has trigger phrases in YAML frontmatter
- Has bash script template with all variables
- Has example configurations
- Includes new features (Redis, OpenAPI, etc.)
- Does NOT include removed options (Copy docs, Open VS Code)

### Integration Tests

Verify that:
- Bash script template has valid syntax
- Generated script can run successfully
- Project directory and files are created
- Git repository is initialized
- Template parameters match documentation
- Parameters compatible with actual dotnet template

## Sample Usage Demonstration

After installing skills, here's how a user would trigger the skill:

### Example 1: Basic Project Setup

**User Prompt:**
```
Create a new FHIR project with PostgreSQL data store
```

**Expected Skill Behavior:**
1. Claude recognizes trigger phrase "create a new fhir project"
2. Activates `fhir-project-setup` skill
3. Asks 5 questions:
   - Project name
   - Database store (user selects DocumentPg)
   - FHIR version
   - Framework & Aspire
   - Additional features
4. Shows configuration summary
5. Generates and executes bash script
6. Creates project successfully

### Example 2: Full-Featured Project

**User Prompt:**
```
I want to create a FHIR web API project with PostgreSQL, use R4 FHIR version,
enable Redis caching, OpenAPI/Swagger, and audit logging
```

**Expected Skill Behavior:**
1. Claude activates `fhir-project-setup` skill
2. Asks questions (with defaults from user prompt)
3. Shows summary with:
   - Database: DocumentPg
   - FHIR Version: R4
   - Features: Redis ✓, OpenAPI ✓, Audit ✓
4. Generates script with parameters:
   ```bash
   dotnet new fhirengine-webapi \
     --dbstore="DocumentPg" \
     --fhirversion="R4" \
     --framework="net8.0" \
     --aspireversion="9.5.2" \
     --includetest \
     --redis \
     --openapi \
     --audit
   ```
5. Creates project successfully

### Example 3: Testing/Development Project

**User Prompt:**
```
Setup a minimal FHIR R5 project for testing
```

**Expected Skill Behavior:**
1. Claude activates `fhir-project-setup` skill
2. Suggests minimal configuration:
   - Database: None (in-memory)
   - FHIR Version: R5
   - Aspire: Disable
   - Features: None
3. Creates lightweight project for quick testing

## Verifying Skill Installation

### Step 1: Install Skills to a Test Project

```bash
# Create test directory
mkdir -p /tmp/test-fhir-project
cd /tmp/test-fhir-project

# Install skills
fhir-skills install --path .

# Verify installation
ls .claude/skills/
```

**Expected Output:**
```
GETTING_STARTED.md
LICENSE
README.md
VERSION
codegen/
fhir-config-troubleshooting/
fhir-errors-debugger/
fhir-project-setup/
handler-patterns/
tasks/
```

### Step 2: Verify Skill Content

```bash
# Check skill exists
ls .claude/skills/fhir-project-setup/

# View skill file
cat .claude/skills/fhir-project-setup/SKILL.md | head -20
```

**Expected Output:**
```yaml
---
name: fhir-project-setup
displayName: FHIR Project Setup
description: Interactive wizard to create a new FHIR Engine Web API project...
version: 1.0.0
triggers:
  - "create a new fhir project"
  - "setup fhir web api"
  ...
```

### Step 3: Verify Template

```bash
# Check template file
cat .claude/skills/fhir-project-setup/templates/setup-project.sh.md | grep "{REDIS}"
```

**Expected Output:**
```
REDIS={REDIS}
...
if [ "$REDIS" = true ]; then
```

## Manual Integration Test

If you have .NET SDK and FHIR Engine templates installed:

```bash
# Create actual project using the skill's bash script template

# 1. Extract bash script from template
cat .claude/skills/fhir-project-setup/templates/setup-project.sh.md | \
  sed -n '/^```bash$/,/^```$/p' | \
  grep -v '```' > /tmp/test-setup.sh

# 2. Replace placeholders
sed -i 's/{SOLUTION_NAME}/MyTestAPI/g' /tmp/test-setup.sh
sed -i 's/{DB_STORE}/None/g' /tmp/test-setup.sh
sed -i 's/{FHIR_VERSION}/R5/g' /tmp/test-setup.sh
sed -i 's/{FRAMEWORK}/net8.0/g' /tmp/test-setup.sh
sed -i 's/{ASPIRE_VERSION}/Disable/g' /tmp/test-setup.sh
sed -i 's/{INCLUDE_TEST}/true/g' /tmp/test-setup.sh
sed -i 's/{REDIS}/false/g' /tmp/test-setup.sh
sed -i 's/{OPENAPI}/true/g' /tmp/test-setup.sh
sed -i 's/{OTEL}/false/g' /tmp/test-setup.sh
sed -i 's/{AUDIT}/false/g' /tmp/test-setup.sh
sed -i 's/{CORS}/false/g' /tmp/test-setup.sh

# 3. Make executable and run
chmod +x /tmp/test-setup.sh
cd /tmp && ./test-setup.sh

# 4. Verify project created
ls MyTestAPI.R5.None/
```

**Expected Output:**
```
MyTestAPI.R5.None/
├── MyTestAPI.R5.None.sln
├── MyTestAPI.R5.None.csproj
├── Program.cs
├── appsettings.json
├── fhirengine.json
└── .git/
```

## Troubleshooting Tests

### Issue: ModuleNotFoundError: No module named 'fhir_skills'

**Solution:** Install package in development mode
```bash
pip install -e .
```

### Issue: Tests fail with "dotnet template not found"

**Solution:** The `test_dotnet_template_parameter_compatibility` test requires FHIR Engine templates. Install them:
```bash
dotnet new install Ihis.FhirEngine.Templates
```

Or skip this specific test:
```bash
pytest tests/ -v -k "not dotnet_template"
```

### Issue: Permission errors in temp directories

**Solution:** This is normal on Windows. Tests will still pass. Cleanup warnings can be ignored.

## Continuous Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Test FHIR Engine Skills

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install package and dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest tests/ -v --cov=fhir_skills --cov-report=term-missing

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Next Steps

After tests pass:

1. **Commit changes**:
   ```bash
   git add tests/ TESTING.md pyproject.toml
   git commit -m "Add comprehensive test suite for skills"
   ```

2. **Push to repository**:
   ```bash
   git push origin main
   ```

3. **Test installation from GitHub**:
   ```bash
   uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install
   ```

4. **Use in Claude Code**:
   - Open project in Claude Code
   - Type: "Create a new FHIR project with PostgreSQL"
   - Verify skill activates and guides project creation

## Summary

✅ **21 automated tests** verify:
- Skills install correctly
- All required skills are present
- fhir-project-setup skill has correct structure
- Bash script template is valid
- New features are included (Redis, OpenAPI, etc.)
- Old features are removed (Copy docs, Open VS Code)
- Template parameters match dotnet CLI

All tests passing means the skills package is ready for distribution! 🎉
