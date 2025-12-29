# FHIR Engine Claude Skills

AI-powered development assistance for building FHIR APIs with FHIR Engine framework.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## What Are Skills?

Claude Code skills are specialized knowledge modules that automatically activate when you're working with FHIR Engine. They provide:

- 🔧 **Configuration troubleshooting** - Fix fhirengine.json and appsettings.json issues
- 🎯 **Handler generation** - Generate CRUD handlers, custom operations, and workflows
- 🏗️ **Resource creation** - Create custom FHIR resources and data stores
- 🗺️ **Data mapping** - Map legacy systems to FHIR resources
- 🐛 **Error debugging** - Translate misleading errors into solutions
- 📚 **Best practices** - Follow framework patterns automatically

## Installation

### Quick Install (Recommended)

Using `uvx` (no permanent installation):

```bash
# Navigate to your FHIR project
cd my-fhir-project

# Install skills
uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install
```

### Persistent Tool Installation

Install the tool globally for reuse:

```bash
# Install once
uv tool install fhir-engine-skills --from git+https://github.com/ihis/fhir-engine-skills.git

# Use in any project
cd my-fhir-project
fhir-skills install
```

### Manual Installation

If you don't have `uv`, download and extract manually:

```bash
# Clone the repository
git clone https://github.com/ihis/fhir-engine-skills.git temp-skills

# Copy skills to your project
cp -r temp-skills/src/fhir_skills/skills .claude/

# Clean up
rm -rf temp-skills
```

## Usage

Once installed, skills activate automatically in Claude Code when you ask relevant questions:

```bash
# Open your project in Claude Code
code .

# Ask Claude questions - skills activate automatically:
# "Create CRUD handlers for Patient resource"
# "How do I configure PostgreSQL data store?"
# "I'm getting 'No handler found' error"
# "Map this database schema to FHIR resources"
```

## Available Skills

### 🔧 Troubleshooting & Help (3 skills)

**fhir-config-troubleshooting**
- Diagnose fhirengine.json and appsettings.json issues
- Fix handler registration problems
- Configure data stores (SQL Server, PostgreSQL, DynamoDB, etc.)

**handler-patterns**
- Implement CRUD handlers correctly
- Understand handler pipeline phases
- Choose the right handler category

**fhir-errors-debugger**
- Translate misleading error messages
- Debug handler execution errors
- Fix validation issues

### ⚡ Code Generation (4 skills)

**fhir-handler-generator**
- Generate CRUD handlers (Create, Read, Update, Delete, Search)
- Create custom operations ($cancel, $validate, etc.)
- Implement workflow handlers (PreCRUD, PostInteraction, etc.)

**fhir-custom-resource**
- Create custom FHIR resource entities
- Generate component classes for nested structures
- Auto-generate StructureDefinitions via MSBuild

**fhir-custom-datastore**
- Generate relational database models
- Create EF Core DbContext classes
- Implement custom search services
- Build data mappers (FHIR ↔ Database)

**fhir-structuredefinition**
- Generate FHIR StructureDefinition conformance resources
- Create profiles with validation constraints
- Define extensions for custom data
- Add FHIRPath validation rules

### 🗺️ Analysis & Mapping (1 skill)

**fhir-data-mapping**
- Analyze custom data models
- Recommend appropriate FHIR resources
- Create field-level mapping specifications
- Handle data transformations

## CLI Commands

```bash
# Install skills to current project
fhir-skills install

# Install to specific project
fhir-skills install --path /path/to/project

# Force install (no confirmation)
fhir-skills install --force

# List available skills
fhir-skills list

# Update existing installation
fhir-skills update

# Show package info
fhir-skills info
```

## Examples

### Example 1: Create Patient Handlers

```bash
# In Claude Code, ask:
"Create CRUD handlers for Patient resource with validation"
```

Skills activate:
- ✅ `fhir-handler-generator` generates handler code
- ✅ Includes dependency injection setup
- ✅ Adds error handling patterns
- ✅ Updates fhirengine.json configuration
- ✅ Provides sample HTTP requests

### Example 2: Fix Configuration Error

```bash
# In Claude Code, paste error:
"I'm getting: InvalidOperationException: No handler found for Patient.Read"
```

Skills activate:
- ✅ `fhir-errors-debugger` analyzes the error
- ✅ `fhir-config-troubleshooting` checks configuration
- ✅ Provides step-by-step fix
- ✅ Explains root cause

### Example 3: Map Database to FHIR

```bash
# In Claude Code, ask:
"Map this database schema to FHIR resources: [paste schema]"
```

Skills activate:
- ✅ `fhir-data-mapping` analyzes schema
- ✅ Recommends FHIR resources
- ✅ Creates field-level mappings
- ✅ Identifies extensions needed
- ✅ Provides sample FHIR instances

## Requirements

- **Claude Code** (latest version) - [Download](https://claude.com/code)
- **FHIR Engine** 1.0+ NuGet packages
- **.NET 8.0** or later
- **Python 3.8+** (only for installation tool)

## Framework Support

These skills support:
- ✅ FHIR R5 (5.0.0) - Default
- ✅ FHIR R4B (4.3.0)
- ✅ .NET 8.0+
- ✅ SQL Server, PostgreSQL, DynamoDB+S3 data stores
- ✅ Singapore healthcare context (no US Core)

## Updating Skills

Update to latest version:

```bash
# Using uvx
uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills update

# Using installed tool
fhir-skills update
```

Skills are versioned alongside FHIR Engine releases.

## Troubleshooting

### Skills Not Activating

1. Verify skills are installed:
   ```bash
   ls -la .claude/skills/
   ```

2. Check Claude Code is latest version

3. Restart Claude Code

### Permission Errors During Installation

```bash
# Check directory permissions
ls -ld .claude

# Create directory if needed
mkdir -p .claude/skills

# Try installation again
fhir-skills install --force
```

### Wrong Skills Version

```bash
# Check installed version
cat .claude/skills/README.md | grep -i version

# Update to latest
fhir-skills update
```

## Contributing

We welcome contributions! To suggest improvements:

1. **Report Issues**: [GitHub Issues](https://github.com/ihis/fhir-engine-skills/issues)
2. **Suggest Skills**: [Discussions](https://github.com/ihis/fhir-engine-skills/discussions)
3. **Share Feedback**: feedback@ihis.com

## Development

To work on skills locally:

```bash
# Clone repository
git clone https://github.com/ihis/fhir-engine-skills.git
cd fhir-engine-skills

# Install in development mode
pip install -e .

# Test installation
fhir-skills list

# Make changes to skills in src/fhir_skills/skills/

# Test in a project
fhir-skills install --path /path/to/test-project
```

## Version Compatibility

| Skills Version | FHIR Engine Version | Status |
|:--------------|:-------------------|:-------|
| 1.0.x | 1.0.x | ✅ Supported |
| 1.1.x | 1.1.x | 🚧 In Development |

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

**Developed by**: FHIR Engine Team
**Powered by**: [Claude Code](https://claude.com/code) from Anthropic
**FHIR Specification**: [HL7 FHIR®](https://hl7.org/fhir/)

## Support

- 📖 [Documentation](https://github.com/ihis/fhir-engine-skills/wiki)
- 💬 [Discussions](https://github.com/ihis/fhir-engine-skills/discussions)
- 🐛 [Issue Tracker](https://github.com/ihis/fhir-engine-skills/issues)
- 📧 Email: support@ihis.com

## Related Resources

- [FHIR Engine Documentation](https://docs.fhirengine.com)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [HL7 FHIR Specification](https://hl7.org/fhir/)
- [FHIR Engine NuGet Packages](https://www.nuget.org/packages?q=Ihis.FhirEngine)

---

**Quick Start**: `uvx --from git+https://github.com/ihis/fhir-engine-skills.git fhir-skills install`
