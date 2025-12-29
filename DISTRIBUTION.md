# Distribution Guide for FHIR Engine Skills

This guide explains how to publish and distribute FHIR Engine Claude skills using the `uv tool` installation method.

## Publishing to GitHub

### 1. Create GitHub Repository

```bash
# Create new repository on GitHub: fhir-engine-skills
# Then push the package

cd /path/to/skills-package
git init
git add .
git commit -m "Initial release: FHIR Engine Claude Skills v1.0.0"
git remote add origin https://github.com/ihis/fhir-engine-skills.git
git push -u origin main
```

### 2. Create Release Tags

Tag releases for version management:

```bash
# Tag initial release
git tag -a v1.0.0 -m "Release v1.0.0 - Initial FHIR Engine Skills"
git push origin v1.0.0

# Create GitHub release from tag
# Go to GitHub → Releases → Draft a new release
# Select tag v1.0.0
# Add release notes
```

## User Installation

Users can install skills using several methods:

### Method 1: One-Time Installation (Recommended)

No permanent installation required:

```bash
uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install
```

### Method 2: Install Tool Globally

For repeated use across multiple projects:

```bash
# Install once
uv tool install fhir-engine-skills --from git+https://github.com/ihis/fhir-engine-skills.git

# Use in any project
cd my-project
fhir-skills install

# Update tool later
uv tool upgrade fhir-engine-skills
```

### Method 3: Install Specific Version

```bash
# Install from specific tag
uvx --from git+https://github.com/ihis/fhir-engine-skills.git@v1.0.0 fhir-skills install

# Or with permanent installation
uv tool install fhir-engine-skills --from git+https://github.com/ihis/fhir-engine-skills.git@v1.0.0
```

### Method 4: Install from Branch

For testing pre-release versions:

```bash
# Install from develop branch
uvx --from git+https://github.com/ihis/fhir-engine-skills.git@develop fhir-skills install
```

## Repository Structure

```
fhir-engine-skills/              # GitHub repository
├── README.md                    # Main documentation
├── LICENSE                      # MIT License
├── DISTRIBUTION.md              # This file
├── pyproject.toml              # Python package configuration
│
├── src/
│   └── fhir_skills/
│       ├── __init__.py         # Package version
│       ├── cli.py              # CLI tool implementation
│       └── skills/             # Embedded skills content
│           ├── README.md
│           ├── GETTING_STARTED.md
│           ├── codegen/
│           │   ├── fhir-handler-generator/
│           │   ├── fhir-custom-resource/
│           │   ├── fhir-custom-datastore/
│           │   └── fhir-structuredefinition/
│           ├── tasks/
│           │   └── fhir-data-mapping/
│           ├── fhir-config-troubleshooting/
│           ├── handler-patterns/
│           └── fhir-errors-debugger/
│
└── .github/
    └── workflows/
        └── release.yml          # Automated releases
```

## Version Management

### Semantic Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes in skills or FHIR Engine compatibility
- **MINOR**: New skills added, non-breaking enhancements
- **PATCH**: Bug fixes, documentation updates

### Version Alignment

Align skills versions with FHIR Engine:

| Skills Version | FHIR Engine Version | Changes |
|:--------------|:-------------------|:--------|
| 1.0.0 | 1.0.x | Initial release |
| 1.1.0 | 1.1.x | New skills for v1.1 features |
| 2.0.0 | 2.0.x | Updated for v2.0 breaking changes |

### Updating Versions

**1. Update `pyproject.toml`:**
```toml
[project]
name = "fhir-engine-skills"
version = "1.1.0"  # Update this
```

**2. Update `__init__.py`:**
```python
__version__ = "1.1.0"  # Update this
```

**3. Commit and tag:**
```bash
git add pyproject.toml src/fhir_skills/__init__.py
git commit -m "Bump version to 1.1.0"
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin main --tags
```

## Release Process

### 1. Prepare Release

```bash
# Create release branch
git checkout -b release/v1.1.0

# Update version numbers (see above)

# Update CHANGELOG
echo "## v1.1.0 - 2025-01-15" >> CHANGELOG.md
echo "- Added fhir-data-mapping skill" >> CHANGELOG.md
echo "- Improved error messages" >> CHANGELOG.md

# Commit changes
git add .
git commit -m "Prepare release v1.1.0"
```

### 2. Test Release

```bash
# Test installation locally
uvx --from . fhir-skills install --path /tmp/test-project

# Verify skills work
ls /tmp/test-project/.claude/skills
```

### 3. Create GitHub Release

```bash
# Merge to main
git checkout main
git merge release/v1.1.0
git push origin main

# Create and push tag
git tag -a v1.1.0 -m "Release v1.1.0 - Enhanced data mapping"
git push origin v1.1.0

# On GitHub:
# 1. Go to Releases → Draft a new release
# 2. Choose tag v1.1.0
# 3. Title: "v1.1.0 - Enhanced Data Mapping"
# 4. Description: Paste from CHANGELOG
# 5. Publish release
```

### 4. Announce Release

**Email to users:**
```
Subject: FHIR Engine Skills v1.1.0 Released

New version available with enhanced data mapping capabilities!

What's New:
- New fhir-data-mapping skill for legacy system migration
- Improved error debugging
- Better PostgreSQL configuration guidance

Update Now:
uv tool upgrade fhir-engine-skills

Or fresh install:
uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install

Full changelog: https://github.com/ihis/fhir-engine-skills/releases/tag/v1.1.0
```

## Promoting Skills

### 1. FHIR Engine Documentation

Add to FHIR Engine docs:

```markdown
## Development Tools

### Claude Code Skills

AI-powered assistance for FHIR Engine development:

**Quick Install:**
```bash
uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install
```

**Features:**
- Auto-generate handlers and resources
- Fix configuration errors
- Map legacy data to FHIR

Learn more: https://github.com/ihis/fhir-engine-skills
```

### 2. NuGet Package README

Include in FHIR Engine NuGet package description:

```markdown
## Accelerate Development with Claude Skills

Install AI-powered development assistance:
`uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install`

Skills help you troubleshoot, generate code, and follow best practices.
```

### 3. Quickstart Templates

Include in project templates:

```bash
# In template initialization
dotnet new fhir-api -n MyFhirService
cd MyFhirService

# Offer skills installation
echo "Install Claude Code skills for AI assistance? [y/N]"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install
fi
```

### 4. Video Tutorials

Create video showing:
1. Installing skills
2. Generating first handler
3. Fixing configuration error
4. Mapping database schema

Upload to YouTube/documentation site.

## Support and Maintenance

### GitHub Issues

Use labels for organization:
- `bug` - Skills not working correctly
- `enhancement` - New skill suggestions
- `documentation` - Docs improvements
- `question` - User questions

### Discussions

Enable GitHub Discussions:
- **General** - Usage questions
- **Ideas** - New skill proposals
- **Show and Tell** - User success stories
- **Q&A** - Technical questions

### Roadmap

Maintain public roadmap in GitHub Projects:

**v1.2.0 (Planned):**
- [ ] Enhanced custom operation templates
- [ ] Batch operation handlers
- [ ] Advanced search patterns

**v2.0.0 (Future):**
- [ ] FHIR R6 support
- [ ] Multi-tenancy patterns
- [ ] Performance optimization skills

## Analytics

### Track Adoption

**GitHub metrics:**
- Stars (popularity)
- Forks (community engagement)
- Clone counts (installation attempts)
- Release downloads

**Usage analytics:**
```bash
# In CLI, add optional telemetry
# src/fhir_skills/cli.py
import uuid
import json
from pathlib import Path

def track_install(anonymous=True):
    """Track anonymous installation stats (opt-in)."""
    if not anonymous:
        return

    analytics = {
        "event": "install",
        "version": __version__,
        "timestamp": datetime.now().isoformat(),
        "anonymous_id": str(uuid.uuid4())
    }
    # Send to analytics endpoint (if configured)
```

## Security

### Review Contributions

Before merging skill updates:
1. Review all code changes
2. Test in isolated environment
3. Ensure no malicious content
4. Verify SKILL.md frontmatter is valid

### Dependency Management

Keep dependencies minimal:
- No external dependencies for skills content
- Only standard library for CLI tool
- Regular security audits

## Legal Compliance

### License Headers

All skill files include:
```markdown
---
name: skill-name
description: Skill description
license: MIT
copyright: Copyright (c) 2025 FHIR Engine Team
---
```

### Trademark Notices

Include in README:
```
HL7® and FHIR® are registered trademarks of Health Level Seven International.
Claude is a trademark of Anthropic PBC.
```

## Troubleshooting Distribution

### Issue: Users can't install

**Check:**
1. Repository is public
2. pyproject.toml is valid
3. Package structure is correct

**Test:**
```bash
# Validate locally
python -m build
pip install dist/*.whl

# Test CLI
fhir-skills info
```

### Issue: Skills not copied

**Check:**
1. `skills/` directory exists in package
2. `pyproject.toml` includes skills in wheel
3. File permissions are correct

**Debug:**
```bash
# Inspect installed package
uv tool install --verbose fhir-engine-skills --from git+...

# Check package contents
python -c "import fhir_skills; print(fhir_skills.__file__)"
ls -R $(dirname $(python -c "import fhir_skills; print(fhir_skills.__file__)"))
```

### Issue: Old version installed

**Solution:**
```bash
# Uninstall completely
uv tool uninstall fhir-engine-skills

# Clear cache
rm -rf ~/.cache/uv/

# Reinstall
uv tool install fhir-engine-skills --from git+https://github.com/ihis/fhir-engine-skills.git
```

## Summary

**Distribution Workflow:**

1. **Develop** → Update skills in `src/fhir_skills/skills/`
2. **Version** → Update `pyproject.toml` and `__init__.py`
3. **Test** → `uvx --from . fhir-skills install --path /tmp/test`
4. **Release** → Tag and push to GitHub
5. **Announce** → Email, docs, social media
6. **Support** → Monitor issues and discussions

**User Installation:**
```bash
uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install
```

Simple, fast, and version-controlled!
