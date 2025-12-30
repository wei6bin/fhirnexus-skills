# Changelog

All notable changes to FHIR Engine Claude Skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-15

### Added

#### Troubleshooting & Help Skills (3)
- **fhir-config-troubleshooting** - Diagnose configuration issues in fhirengine.json and appsettings.json
- **handler-patterns** - Handler implementation patterns and best practices
- **fhir-errors-debugger** - Error debugging and translation

#### Code Generation Skills (4)
- **fhir-handler-generator** - Generate CRUD handlers, custom operations, and workflows
  - CRUD handler templates (Create, Read, Update, Delete, Search)
  - Custom operation handlers ($cancel, $validate, etc.)
  - Workflow handlers (PreCRUD, PostInteraction, etc.)
  - Decision matrix for handler category selection
- **fhir-custom-resource** - Generate custom FHIR resource entities
  - Entity class templates with proper attributes
  - Component classes for nested structures
  - Comprehensive data types reference
- **fhir-custom-datastore** - Generate custom data stores with relational models
  - DbContext classes
  - IResourceEntity models
  - Search service implementations
  - Data mapper classes
- **fhir-structuredefinition** - Generate FHIR StructureDefinition conformance resources
  - Profile definitions
  - Extension definitions
  - FHIRPath validation constraints
  - Slicing patterns

#### Analysis & Mapping Tasks (1)
- **fhir-data-mapping** - Analyze and map custom data models to FHIR
  - Resource selection recommendations
  - Field-level mapping specifications
  - Transformation logic documentation
  - Comprehensive mapping patterns reference

### Features
- **CLI Tool** - `fhir-skills` command-line interface
  - `install` - Install skills to project
  - `list` - List available skills
  - `update` - Update existing installation
  - `info` - Show package information
- **UV Tool Support** - Install via `uv tool install`
- **One-Time Usage** - Use via `uvx` without permanent installation
- **Auto-Activation** - Skills trigger automatically in Claude Code
- **FHIR R5 Default** - Support for FHIR R5 (5.0.0) with R4B fallback
- **Singapore Context** - Regional healthcare context (no US Core)
- **Framework Alignment** - Synchronized with FHIR Engine 1.0.x

### Documentation
- Comprehensive README with installation instructions
- DISTRIBUTION.md for maintainers
- Skill-specific documentation and templates
- Code examples and patterns
- Troubleshooting guides

### Technical
- Total 8,853 lines of documentation
- 19 markdown files across all skills
- Progressive disclosure pattern (main SKILL.md + detailed templates)
- No external dependencies (Python stdlib only)

---

## [Unreleased]

### Planned for v1.1.0
- Enhanced batch operation handlers
- Advanced search patterns
- Performance optimization templates
- Additional error patterns

### Planned for v2.0.0
- FHIR R6 support (when available)
- Multi-tenancy patterns
- GraphQL integration skills
- Advanced caching strategies

---

[1.0.0]: https://github.com/wei6bin/fhirnexus-skills/releases/tag/v1.0.0
