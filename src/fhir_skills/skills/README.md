# FHIR Engine Claude Skills

This directory contains Claude Code skills that provide specialized help when building FHIR APIs using the FHIR Engine framework (Ihis.FhirEngine NuGet packages).

## What Are Skills?

Skills are specialized knowledge modules that Claude automatically uses when you ask relevant questions or encounter issues. They embed framework expertise directly into Claude Code to help you:

- Troubleshoot configuration issues
- Understand error messages
- Implement handlers correctly
- Follow best practices

## Available Skills

### Troubleshooting & Help Skills

#### 1. fhir-config-troubleshooting

**Triggers:** Configuration errors, handler registration problems, data store setup issues

**What it helps with:**
- Diagnosing fhirengine.json and appsettings.json issues
- Fixing handler registration problems
- Configuring data stores (SQL Server, PostgreSQL, DynamoDB, etc.)
- Validating system plugin configuration

**Example questions:**
- "My handler isn't being found, what's wrong?"
- "How do I configure PostgreSQL as my data store?"
- "I'm getting a configuration exception, can you help?"

### 2. handler-patterns

**Triggers:** Creating handlers, implementing FHIR operations, handler signature errors

**What it helps with:**
- Writing CRUD handlers (Create, Read, Update, Delete, Search)
- Implementing custom operations (e.g., `$cancel`)
- Understanding the handler pipeline
- Choosing the right handler category
- Proper handler signatures and return types

**Example questions:**
- "How do I create a Read handler for Patient?"
- "What's the correct signature for a Search handler?"
- "How do I implement a custom operation?"
- "My handler signature is invalid, what's wrong?"

#### 3. fhir-errors-debugger

**Triggers:** Runtime errors, exceptions, stack traces, unexpected behavior

**What it helps with:**
- Translating misleading error messages into root causes
- Debugging handler execution errors
- Fixing data store errors
- Resolving FHIR validation issues
- Understanding pipeline errors

**Example questions:**
- "I'm getting 'No handler found' error"
- "What does this ResourceNotFoundException mean?"
- "My application crashes with a NullReferenceException"
- "How do I fix this validation error?"

---

### Code Generation Skills

#### 4. fhir-project-setup ⭐ NEW

**Triggers:** Questions about creating new projects, setting up FHIR APIs, project scaffolding

**What it generates:**
- New FHIR Engine Web API projects with custom configuration
- Dotnet solution files and project structure
- Git repository initialization
- Optional .NET Aspire orchestration setup

**Example questions:**
- "Create a new FHIR project with PostgreSQL data store"
- "Setup a FHIR Web API with R4B version and enable logging to SQS"
- "I want to create a FHIR R5 project for testing"
- "Initialize a new FHIR Engine project with custom data store"

**Configuration options:**
- Database store (PostgreSQL, SQL Server, Cosmos DB, Custom, etc.)
- FHIR version (R4, R4B, R5)
- .NET Aspire integration (9.5.2, 9.3.1, or disabled)
- Documentation templates
- IDE integration (VS Code auto-open)

**Outputs:**
- Complete project structure with .csproj files
- Solution file with all projects added
- Git repository with initial commit
- appsettings.json and fhirengine.json templates
- Ready-to-build FHIR API

---

#### 5. fhir-handler-generator ⭐ NEW

**Triggers:** Questions about creating handlers, implementing FHIR interactions, custom operations

**What it generates:**
- CRUD handlers (Create, Read, Update, Delete, Search)
- Custom operations ($cancel, $validate, etc.)
- Workflow handlers (validation, enrichment, notifications)
- Complete handler pipeline implementations

**Example questions:**
- "Create CRUD handlers for Patient resource"
- "Add a $mark-deceased operation to Patient"
- "Create a PreCRUD validation handler for appointments"
- "Implement a search handler with custom filtering"

**Outputs:**
- Complete handler class with dependency injection
- Exception handling patterns
- OperationDefinition conformance resources
- Configuration updates
- Sample HTTP requests

---

#### 6. fhir-custom-resource ⭐ NEW

**Triggers:** Questions about custom resources, new resource types, domain-specific models

**What it generates:**
- Custom FHIR resource entity classes
- Component classes for nested structures
- StructureDefinition resources (via MSBuild)
- Search parameter definitions
- Complete configuration

**Example questions:**
- "Create a custom Inventory resource for tracking hospital supplies"
- "Build an Enrollment resource for care program management"
- "Create AlertNotification custom resource with nested components"

**Outputs:**
- Entity class with proper FHIR attributes
- Component/BackboneElement classes
- StructureDefinition (auto-generated on build)
- Search parameters
- Configuration updates
- Sample HTTP requests

---

#### 7. fhir-custom-datastore

**Triggers:** Questions about custom data stores, relational models, database mapping

**What it generates:**
- Custom data store implementations with relational models
- IResourceEntity models with proper attributes
- Search service implementations
- Data mapper classes (FHIR ↔ Database)
- EF Core DbContext configuration

**Example questions:**
- "Create a custom data store for Appointment with relational models"
- "Map Appointment resource to SQL database tables"
- "Generate data store with search service for custom resource"

**Outputs:**
- DbContext class with proper configuration
- Entity models with EF Core attributes
- Search service implementation
- Data mapper service
- Configuration updates

---

#### 8. fhir-structuredefinition

**Triggers:** Questions about StructureDefinitions, profiles, extensions, constraints

**What it generates:**
- FHIR StructureDefinition conformance resources
- Profile definitions (constraints on existing resources)
- Extension definitions (additional data fields)
- Validation constraints using FHIRPath
- Slicing patterns for complex structures

**Example questions:**
- "Create a Singapore Patient profile with NRIC validation"
- "Generate an extension for patient birth time"
- "Create StructureDefinition for custom Inventory resource"
- "Add validation constraint for appointment date"

**Outputs:**
- Complete StructureDefinition JSON files
- Profile with differential elements
- Extension definitions with proper context
- Slicing patterns for identifiers
- Validation constraints

---

### Analysis & Mapping Tasks

#### 9. fhir-data-mapping

**Triggers:** Questions about mapping custom data models to FHIR, database schema conversion

**What it provides:**
- Detailed field-level mapping analysis
- FHIR resource selection guidance
- Transformation specifications
- Extension recommendations
- Primary key handling for custom data stores

**Example questions:**
- "Map this database schema to FHIR resources"
- "What FHIR resource should I use for this data?"
- "How do I map this custom patient data to FHIR?"
- "Analyze my legacy system data model"

**Outputs:**
- Use case summary and resource recommendations
- Detailed field mapping table
- Transformation logic specifications
- Extension definitions for unmappable fields
- Sample FHIR instances
- Implementation considerations

## How to Use Skills

Skills work automatically - just ask Claude your question naturally:

```
You: "I'm getting an error that my handler isn't found"
Claude: [Automatically uses fhir-errors-debugger skill to help diagnose]

You: "How do I set up a Patient handler?"
Claude: [Automatically uses handler-patterns skill to provide examples]

You: "My fhirengine.json seems wrong"
Claude: [Automatically uses fhir-config-troubleshooting skill to help fix]
```

## Skills Reference Documentation

The skills contain embedded knowledge about:

- FHIR Engine configuration (fhirengine.json and appsettings.json)
- Handler patterns and implementation
- Data store setup (SQL Server, PostgreSQL, DynamoDB+S3)
- Common error messages and their solutions
- NuGet package requirements
- Program.cs bootstrapping

**Additional Resources:**
- Official FHIR specification: https://hl7.org/fhir/
- FHIR Engine NuGet package documentation
- Your FHIR Engine version release notes

## Extending Skills

To add more skills for your team:

1. Create a new directory under `.claude/skills/`
2. Add a `SKILL.md` file with YAML frontmatter and instructions
3. Commit and push to share with the team

See the [Claude Code Skills Documentation](https://docs.anthropic.com/claude/docs/claude-code-skills) for details.

## Common Workflows

### Troubleshooting a Configuration Error

1. Copy the error message
2. Ask Claude: "I'm getting this error: [paste error]"
3. Share your fhirengine.json or appsettings.json if requested
4. Claude will identify the issue and provide the fix

### Implementing a New Handler

1. Ask: "How do I create a [operation] handler for [resource]?"
2. Claude will provide the complete handler code
3. Ask: "How do I register this handler?"
4. Claude will show the fhirengine.json configuration

### Understanding an Error

1. Paste the full error message and stack trace
2. Claude will translate it into plain language
3. Claude will provide the fix and explain why it works

## Team Benefits

These skills help your team:

- **Self-service troubleshooting** - Fix issues without escalating
- **Faster onboarding** - New developers get expert help immediately
- **Consistent patterns** - Everyone follows framework best practices
- **Less frustration** - Misleading errors are explained clearly
- **Better productivity** - Spend less time debugging, more time building

## Support

If you encounter issues not covered by these skills or need additional help:

1. Ask Claude for more detailed guidance on specific topics
2. Consult the official FHIR specification: https://hl7.org/fhir/
3. Check FHIR Engine package release notes and documentation
4. Review your specific FHIR Engine version's breaking changes and migration guides

## Skill Maintenance

These skills are maintained alongside the FHIR Engine framework. When updating:

- Keep skills aligned with latest framework features
- Update examples when patterns change
- Add new skills for new capabilities
- Review and update documentation references
