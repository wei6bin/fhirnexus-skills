# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python package that distributes **Claude Code skills** for FHIR Engine development. It provides AI-powered assistance for building FHIR APIs using the FHIR Engine framework (Ihis.FhirEngine NuGet packages).

**Purpose:** Enable developers to install specialized Claude Code skills that help with:
- Generating FHIR handlers (CRUD, custom operations, workflows)
- Creating custom FHIR resources and StructureDefinitions
- Troubleshooting configuration errors
- Debugging FHIR Engine issues
- Mapping legacy data to FHIR resources

## Project Structure

```
fhir-engine-skills/
├── src/fhir_skills/           # Python package
│   ├── __init__.py            # Package version (__version__)
│   ├── cli.py                 # CLI tool implementation
│   └── skills/                # Embedded Claude skills content
│       ├── README.md          # Skills documentation
│       ├── GETTING_STARTED.md # User onboarding
│       ├── codegen/           # Code generation skills
│       │   ├── fhir-handler-generator/
│       │   ├── fhir-custom-resource/
│       │   ├── fhir-custom-datastore/
│       │   └── fhir-structuredefinition/
│       ├── tasks/
│       │   └── fhir-data-mapping/
│       ├── fhir-config-troubleshooting/
│       ├── fhir-errors-debugger/
│       └── handler-patterns/
├── pyproject.toml             # Package configuration
├── README.md                  # User-facing documentation
├── SETUP.md                   # Maintainer setup guide
└── DISTRIBUTION.md            # Release and distribution guide
```

## Key Architecture Concepts

### 1. Distribution Model

This package uses **git-based distribution** via `uv tool`:
- Skills content is embedded in `src/fhir_skills/skills/`
- CLI tool (`fhir-skills`) copies skills to target projects' `.claude/skills/` directory
- Users install via: `uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install`
- No PyPI publication required - distributed directly from GitHub

### 2. CLI Tool Architecture

The `cli.py` implements a simple file copier:
- `install` command: Copies `src/fhir_skills/skills/` → `.claude/skills/` in target project
- `list` command: Lists available skills by category
- `update` command: Overwrites existing installation
- `info` command: Shows package information

The CLI uses `shutil.copytree()` to copy the entire skills directory tree.

### 3. Skills Content Structure

Each skill directory contains:
- `SKILL.md` - Main skill definition with YAML frontmatter (triggers, instructions, examples)
- `templates/` - Code generation templates
- `examples/` - Reference implementations
- Additional reference files (e.g., `decision-matrix.md`, `mapping-patterns.md`)

Skills are categorized:
- **Troubleshooting & Help** (3 skills): Config troubleshooting, error debugging, handler patterns
- **Code Generation** (4 skills): Handler generator, custom resources, custom datastores, StructureDefinitions
- **Analysis & Mapping** (1 skill): Data mapping analysis

### 4. Version Management

Version must be updated in **two files** when releasing:
1. `pyproject.toml` - `[project] version = "x.y.z"`
2. `src/fhir_skills/__init__.py` - `__version__ = "x.y.z"`

Skills versions align with FHIR Engine framework versions (e.g., skills v1.0.0 supports FHIR Engine 1.0.x).

## Common Development Tasks

### Testing CLI Installation Locally

```bash
# Install package in development mode
pip install -e .

# Test installation to a temporary directory
mkdir -p /tmp/test-project
fhir-skills install --path /tmp/test-project

# Verify skills were copied
ls /tmp/test-project/.claude/skills/

# Test with uvx (from local directory)
uvx --from . fhir-skills install --path /tmp/test
```

### Updating Skills Content

1. Edit skill files in `src/fhir_skills/skills/*/SKILL.md`
2. Test locally (see above)
3. No build step required - skills are plain markdown files

### Creating a New Skill

1. Create directory: `src/fhir_skills/skills/<category>/<skill-name>/`
2. Add `SKILL.md` with YAML frontmatter
3. Add supporting files (templates/, examples/)
4. Update `src/fhir_skills/skills/README.md` to document the new skill

### Releasing a New Version

1. Update version in `pyproject.toml` and `src/fhir_skills/__init__.py`
2. Update `CHANGELOG.md`
3. Commit changes: `git commit -m "Bump version to x.y.z"`
4. Tag release: `git tag -a vx.y.z -m "Release vx.y.z"`
5. Push: `git push origin main --tags`

### Testing GitHub Installation

```bash
# Test installation from GitHub (after pushing)
uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install --path /tmp/test

# Test specific version
uvx --from git+https://github.com/ihis/fhir-engine-skills.git@v1.0.0 fhir-skills install
```

## Important Technical Details

### Skills Are Not Executed

The Python package **does not execute or interpret skills**. It only:
1. Bundles skills content as package data
2. Copies skills to target `.claude/skills/` directories
3. Claude Code reads and uses the skills automatically

### Package Data Inclusion

`pyproject.toml` uses `[tool.hatch.build.targets.wheel]` to include skills:
```toml
packages = ["src/fhir_skills"]
[tool.hatch.build.targets.wheel.force-include]
"skills" = "fhir_skills/skills"
```

This ensures `src/fhir_skills/skills/` is packaged and accessible via `Path(__file__).parent / "skills"` in `cli.py`.

### CLI Entry Point

The `fhir-skills` command is defined in `pyproject.toml`:
```toml
[project.scripts]
fhir-skills = "fhir_skills.cli:main"
```

### No External Dependencies

The package uses **only Python standard library**:
- `pathlib` for path operations
- `shutil` for file copying
- `argparse` for CLI

This minimizes installation issues and maintains simplicity.

## FHIR Engine Context

### What is FHIR Engine?

FHIR Engine is a .NET framework (NuGet packages: `Ihis.FhirEngine.*`) for building FHIR R5/R4B APIs. Key concepts:

- **Handlers**: Classes that process FHIR interactions (Create, Read, Update, Delete, Search, custom operations)
- **HandlerCategory**: Pipeline phases (PreInteraction → PreCRUD → CRUD → PostCRUD → PostInteraction)
- **Data Stores**: Configurable backends (SQL Server, PostgreSQL, DynamoDB+S3)
- **Configuration**: `fhirengine.json` (handler registration) and `appsettings.json` (connections, settings)

### Skills Target Audience

Developers building FHIR APIs who:
- Use FHIR Engine NuGet packages
- Work in .NET 8.0+ environments
- Need to implement FHIR R5/R4B conformance
- Operate in Singapore healthcare context (no US Core)

## Testing and Validation

### Manual Testing Checklist

Before releasing:

1. **CLI works**: `fhir-skills list`, `fhir-skills info`
2. **Installation works**: `fhir-skills install --path /tmp/test`
3. **Skills copied correctly**: Verify all 8 skill directories present
4. **Count correct**: CLI shows "Successfully installed 8 skills"
5. **Version correct**: `fhir-skills info` shows updated version

### Automated Testing

Currently no automated tests. Consider adding:
- Unit tests for CLI functions
- Integration tests for install workflow
- Validation of SKILL.md YAML frontmatter

## Common Issues and Solutions

### Skills Not Found After Installation

Check `pyproject.toml` package data configuration. Verify skills path with:
```python
from pathlib import Path
import fhir_skills
print(Path(fhir_skills.__file__).parent / "skills")
```

### CLI Tool Not Available

After `pip install -e .`, if `fhir-skills` command not found:
- Check `[project.scripts]` in `pyproject.toml`
- Ensure virtual environment is activated
- Try `python -m fhir_skills.cli` directly

### Version Mismatch

If `fhir-skills info` shows wrong version:
- Check both `pyproject.toml` and `__init__.py` match
- Reinstall: `pip uninstall fhir-engine-skills && pip install -e .`

## File Naming Conventions

- Skill directories: `kebab-case` (e.g., `fhir-handler-generator`)
- Skill files: `SKILL.md` (uppercase, required)
- Supporting files: Descriptive names (`decision-matrix.md`, `mapping-patterns.md`)
- Templates: `<name>.md` in `templates/` subdirectory

## Documentation Guidelines

When updating README.md or skills documentation:
- Keep installation instructions concise (one-liner preferred)
- Include version compatibility table
- Provide copy-paste ready commands
- Use concrete examples over abstract descriptions
- Maintain consistency with FHIR Engine terminology

## Related Resources

- **FHIR Engine**: .NET framework these skills support
- **Claude Code**: IDE that executes these skills
- **FHIR R5**: https://hl7.org/fhir/ (target specification)
- **uv tool**: https://github.com/astral-sh/uv (distribution mechanism)
