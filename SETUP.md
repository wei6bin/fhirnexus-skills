# Setup Guide for Package Maintainers

This guide is for maintainers who need to set up the repository for distribution.

## Prerequisites

- Python 3.8 or later
- Git
- `uv` tool (for testing)
- GitHub account with repository access

## Initial Setup

### 1. Create GitHub Repository

```bash
# On GitHub, create new repository: fhir-engine-skills
# Make it public for easy distribution
# Initialize with: None (we'll push existing code)
```

### 2. Clone and Push Package

```bash
# Navigate to the package directory
cd /home/weibin/repo/FhirEngine/.claude/skills-package

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial release: FHIR Engine Claude Skills v1.0.0"

# Add remote (replace with your org/repo)
git remote add origin https://github.com/wei6bin/fhirnexus-skills.git

# Push to GitHub
git branch -M main
git push -u origin main

# Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0 - Initial FHIR Engine Skills"
git push origin v1.0.0
```

### 3. Configure GitHub Repository

**Settings to configure:**

1. **About** (top right)
   - Description: "Claude Code skills for FHIR Engine development"
   - Website: Link to FHIR Engine docs
   - Topics: `fhir`, `claude`, `ai`, `healthcare`, `skills`

2. **General Settings**
   - ✅ Issues enabled
   - ✅ Discussions enabled
   - ✅ Projects enabled (for roadmap)

3. **Branch Protection** (Settings → Branches)
   - Protect `main` branch
   - Require pull request reviews
   - Require status checks to pass

## Local Development Setup

### 1. Install in Development Mode

```bash
cd /home/weibin/repo/FhirEngine/.claude/skills-package

# Install in editable mode
pip install -e .

# Or with uv
uv pip install -e .

# Verify installation
fhir-skills info
```

### 2. Test CLI Commands

```bash
# List skills
fhir-skills list

# Test installation to temp directory
mkdir -p /tmp/test-fhir-project
fhir-skills install --path /tmp/test-fhir-project

# Verify installation
ls -R /tmp/test-fhir-project/.claude/skills/

# Test update
fhir-skills update --path /tmp/test-fhir-project

# Clean up
rm -rf /tmp/test-fhir-project
```

### 3. Test UV Tool Installation

```bash
# Test one-time usage
uvx --from . fhir-skills info

# Test from local directory
uvx --from . fhir-skills install --path /tmp/test

# Clean up
rm -rf /tmp/test
```

## Updating Skills

### 1. Modify Skills Content

Skills are located in: `src/fhir_skills/skills/`

```bash
# Edit a skill
nano src/fhir_skills/skills/fhir-config-troubleshooting/SKILL.md

# Add new skill
mkdir -p src/fhir_skills/skills/new-skill
nano src/fhir_skills/skills/new-skill/SKILL.md
```

### 2. Update Version

**Update 3 files:**

1. `pyproject.toml`:
```toml
[project]
version = "1.1.0"  # Change this
```

2. `src/fhir_skills/__init__.py`:
```python
__version__ = "1.1.0"  # Change this
```

3. `CHANGELOG.md`:
```markdown
## [1.1.0] - 2025-02-01

### Added
- New skill for batch operations
- Enhanced error patterns

### Changed
- Improved PostgreSQL configuration guidance
```

### 3. Test Changes

```bash
# Install locally
pip install -e .

# Test
fhir-skills install --path /tmp/test

# Verify new content
cat /tmp/test/.claude/skills/README.md

# Clean up
rm -rf /tmp/test
```

### 4. Commit and Release

```bash
# Commit changes
git add .
git commit -m "Release v1.1.0"

# Tag release
git tag -a v1.1.0 -m "Release v1.1.0 - Batch operations and improvements"

# Push
git push origin main --tags
```

### 5. Create GitHub Release

1. Go to GitHub repository
2. Click "Releases" → "Draft a new release"
3. Choose tag: `v1.1.0`
4. Title: `v1.1.0 - Batch Operations and Improvements`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

## Testing Installation from GitHub

After pushing to GitHub, test that users can install:

```bash
# Test one-time usage
uvx --from git+https://github.com/wei6bin/fhirnexus-skills.git fhir-skills install --path /tmp/test

# Verify
ls /tmp/test/.claude/skills/

# Test permanent installation
uv tool install fhir-engine-skills --from git+https://github.com/wei6bin/fhirnexus-skills.git

# Use it
fhir-skills info

# Uninstall
uv tool uninstall fhir-engine-skills

# Clean up
rm -rf /tmp/test
```

## Syncing with Main Repository

If skills are maintained in the main FHIR Engine repository:

```bash
# In main repo: /home/weibin/repo/FhirEngine/.claude/skills
cd /home/weibin/repo/FhirEngine/.claude/skills

# Make changes to skills...
nano fhir-config-troubleshooting/SKILL.md

# Copy to package
cd /home/weibin/repo/FhirEngine/.claude/skills-package
rm -rf src/fhir_skills/skills/*
cp -r /home/weibin/repo/FhirEngine/.claude/skills/* src/fhir_skills/skills/

# Remove package-specific files
rm -f src/fhir_skills/skills/DISTRIBUTION.md
rm -f src/fhir_skills/skills/PACKAGE_README.md

# Commit and release (see steps above)
```

## Automation (Optional)

### GitHub Actions for Releases

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build

      - name: Build package
        run: python -m build

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Testing Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install package
        run: pip install -e .

      - name: Test CLI
        run: |
          fhir-skills info
          fhir-skills list

      - name: Test installation
        run: |
          mkdir -p /tmp/test-project
          fhir-skills install --path /tmp/test-project --force
          ls /tmp/test-project/.claude/skills/
```

## Troubleshooting Setup

### Issue: Import errors

```bash
# Verify package structure
tree src/

# Should see:
# src/
#   fhir_skills/
#     __init__.py
#     cli.py
#     skills/
#       [all skills]

# Reinstall
pip uninstall fhir-engine-skills
pip install -e .
```

### Issue: Skills not found

```bash
# Check skills are in package
ls -R src/fhir_skills/skills/

# Verify in installed package
python -c "from pathlib import Path; import fhir_skills; print(Path(fhir_skills.__file__).parent / 'skills')"
```

### Issue: UV tool install fails

```bash
# Check pyproject.toml is valid
python -m build  # Should succeed

# Check git is initialized
git status

# Push to GitHub
git push origin main
```

## Support

For setup issues:
1. Check this guide
2. Review DISTRIBUTION.md
3. Test with minimal example
4. Open issue if problem persists

## Summary

**Quick Setup:**
```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial release v1.0.0"
git remote add origin https://github.com/wei6bin/fhirnexus-skills.git
git push -u origin main
git tag v1.0.0
git push --tags

# 2. Test installation
uvx --from git+https://github.com/wei6bin/fhirnexus-skills.git fhir-skills install

# 3. Create GitHub release
# (via web interface)
```

Done! Users can now install via `uv tool install`.
