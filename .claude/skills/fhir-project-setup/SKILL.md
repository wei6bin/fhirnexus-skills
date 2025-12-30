---
name: fhir-project-setup
displayName: FHIR Project Setup
description: Create new FHIR Engine Web API projects or add features to existing projects (Redis, OpenAPI, Audit, etc.)
version: 1.0.0
triggers:
  - "create a new fhir project"
  - "setup fhir web api"
  - "new fhir engine project"
  - "scaffold fhir api"
  - "initialize fhir project"
  - "enable redis in fhir project"
  - "add swagger to fhir api"
  - "enable openapi in fhir project"
  - "add audit logging to fhir project"
  - "enable cors in fhir api"
  - "add opentelemetry to fhir project"
  - "enable cache in fhir project"
  - "add test project to fhir"
examples:
  - query: "I want to create a FHIR web API project with PostgreSQL data store, use R4B FHIR version"
    description: "Creates a FHIR R4B project with PostgreSQL document store"
  - query: "Setup a new FHIR R5 project with SQL Server"
    description: "Creates a FHIR R5 project with SQL Server relational store"
  - query: "Create a FHIR project for testing"
    description: "Creates a minimal FHIR project with in-memory storage"
  - query: "Enable Redis caching in my FHIR project"
    description: "Adds Redis caching to existing FHIR Engine project"
  - query: "Add OpenAPI/Swagger documentation to my FHIR API"
    description: "Adds Swagger UI to existing FHIR project"
  - query: "Enable audit logging and CORS in my FHIR project"
    description: "Adds audit logging and CORS to existing FHIR project"
---

# FHIR Project Setup Skill

This skill helps you with FHIR Engine projects in two ways:
1. **Create new projects** - Scaffold a new FHIR Engine Web API project with your preferred configuration
2. **Add features to existing projects** - Enable Redis, OpenAPI, Audit logging, CORS, OpenTelemetry, or add test projects

## What This Skill Does

### Mode A: Create New Project
1. **Gathers Requirements**: Asks about your project preferences (database, FHIR version, features)
2. **Shows Configuration**: Displays a summary for confirmation
3. **Generates Script**: Creates a bash script based on your choices
4. **Creates Project**: Executes the dotnet template with your configuration
5. **Initializes Git**: Sets up version control with initial commit

### Mode B: Add Features to Existing Project
1. **Detects Current Setup**: Scans your project to identify enabled features
2. **Shows Available Features**: Lists features you can add (Redis, OpenAPI, Audit, CORS, etc.)
3. **Displays Planned Changes**: Shows what files will be modified
4. **Applies Changes**: Adds NuGet packages and updates configuration
5. **Verifies Build**: Ensures project still compiles after changes

## Prerequisites

Before using this skill, ensure you have:

1. **.NET 8.0 SDK** or later installed

2. **Synapxe NuGet Source** configured:
   ```bash
   dotnet nuget add source https://packages.hip.synapxe.sg/artifactory/api/nuget/v3/nuget-main/index.json --name SynapxeNuGet
   ```

   Verify with:
   ```bash
   dotnet nuget list source
   ```

3. **FHIR Engine WebAPI Template** installed:

   Latest stable version:
   ```bash
   dotnet new install Ihis.FhirEngine.WebApiTemplate.CSharp
   ```

   Or specific version (e.g., 5.0.1):
   ```bash
   dotnet new install Ihis.FhirEngine.WebApiTemplate.CSharp@5.0.1
   ```

   Verify with:
   ```bash
   dotnet new list | grep fhirengine
   ```

4. **Git** installed (for version control)

## Instructions for Claude

This skill supports **two modes**:
1. **Create New Project**: Scaffold a new FHIR Engine Web API project from scratch
2. **Add Features**: Add features to an existing FHIR Engine project (e.g., enable Redis, OpenAPI, etc.)

When the user requests FHIR project setup, follow these steps:

### Step 0: Detect Project Mode

First, determine if the user wants to create a new project or modify an existing one:

**Detection Logic:**
1. Check current directory for FHIR Engine project indicators:
   - Look for `*.csproj` files with `Ihis.FhirEngine` package references
   - Look for `fhirengine.json` configuration file
   - Look for `Program.cs` with FHIR Engine setup code

2. If FHIR Engine project detected:
   - **Mode**: Add Features to Existing Project
   - Scan project to detect currently enabled features
   - Ask user which features to add
   - Skip to **Step 1B: Add Features Mode**

3. If no FHIR Engine project detected:
   - **Mode**: Create New Project
   - Proceed to **Step 1A: New Project Mode**

---

## Mode A: Create New Project

### Step 1A: Gather Project Configuration

Use the `AskUserQuestion` tool to collect project preferences. Ask the following questions:

**Question 1: Solution Name**
- Header: "Project Name"
- Question: "What is the base name for your FHIR API project?"
- Options:
  - label: "Use default name"
    description: "Will use 'MyFhirApi' as the base name"
  - label: "Custom name"
    description: "Specify your own project name"
- Multi-select: false

**Question 2: Database Store**
- Header: "Data Store"
- Question: "Which database store do you want to use?"
- Options:
  - label: "DocumentPg (Recommended)"
    description: "PostgreSQL with JSONB document storage - best for cloud-native FHIR APIs"
  - label: "RelationalPg"
    description: "PostgreSQL with relational schema - normalized table structure"
  - label: "Document"
    description: "Azure Cosmos DB / DynamoDB document store"
  - label: "Relational"
    description: "SQL Server with relational schema"
- Multi-select: false

**Question 3: FHIR Version**
- Header: "FHIR Version"
- Question: "Which FHIR version should the API support?"
- Options:
  - label: "R5 (Recommended)"
    description: "Latest FHIR specification with new features like subscriptions"
  - label: "R4 (R4B)"
    description: "FHIR Release 4B - most widely adopted for maximum interoperability"
- Multi-select: false

**Question 4: Framework & Aspire**
- Header: "Framework"
- Question: "Which .NET framework version and Aspire setup?"
- Options:
  - label: ".NET 8.0 with Aspire 9.5.2 (Recommended)"
    description: "Latest stable framework with Aspire orchestration for containers"
  - label: ".NET 8.0 without Aspire"
    description: "Standard .NET 8.0 without Aspire orchestration"
  - label: ".NET 9.0 with Aspire 9.5.2"
    description: "Latest .NET 9 preview with Aspire orchestration"
- Multi-select: false

**Question 5: Additional Features**
- Header: "Features"
- Question: "Which additional features would you like to enable?"
- Options:
  - label: "Include Test Project (Recommended)"
    description: "Add BDD integration test project with sample tests"
  - label: "Enable Redis Caching"
    description: "Add Redis for distributed caching and performance"
  - label: "Enable OpenAPI/Swagger"
    description: "Add Swagger UI for API documentation and testing"
  - label: "Enable OpenTelemetry"
    description: "Add distributed tracing and observability"
  - label: "Enable Audit Logging"
    description: "Track all FHIR resource operations for compliance"
  - label: "Enable CORS"
    description: "Configure Cross-Origin Resource Sharing for web clients"
- Multi-select: true

### Step 2: Process Answers

Extract the user's choices from the answers:

1. **Solution Name**:
   - If "Custom name", prompt for the actual name
   - Default: "MyFhirApi"

2. **Database Store**:
   - Map selection to parameter value (e.g., "DocumentPg (Recommended)" → "DocumentPg")
   - Default: "DocumentPg"

3. **FHIR Version**:
   - Extract version (R4 or R5)
   - Default: "R5"
   - Note: Template only supports R4 and R5 (R4 is R4B in the template)

4. **Framework & Aspire**:
   - Extract framework version: "net8.0" or "net9.0"
   - Extract Aspire version: "9.5.2" or "Disable"
   - Default: net8.0 with Aspire 9.5.2

5. **Additional Features** (multi-select):
   - **Include Test**: `--includetest` (true/false, default: true)
   - **Redis Caching**: `--redis` (true/false)
   - **OpenAPI/Swagger**: `--openapi` (true/false)
   - **OpenTelemetry**: `--otel` (true/false)
   - **Audit Logging**: `--audit` (true/false)
   - **CORS**: `--cors` (true/false)

### Step 3: Display Configuration Summary

Show the user a clear summary of their configuration:

```
📋 FHIR Project Configuration Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project Name:      {SolutionName}.{FhirVersion}.{DbStore}
Base Name:         {SolutionName}
Database Store:    {DbStore}
FHIR Version:      {FhirVersion}
Framework:         {Framework}
Aspire Version:    {AspireVersion}

Features Enabled:
  • Test Project:     {Yes/No}
  • Redis Caching:    {Yes/No}
  • OpenAPI/Swagger:  {Yes/No}
  • OpenTelemetry:    {Yes/No}
  • Audit Logging:    {Yes/No}
  • CORS:             {Yes/No}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This will create the project in:
  {current_directory}/{SolutionName}.{FhirVersion}.{DbStore}
```

Ask the user: "Does this configuration look correct? Should I proceed with creating the project?"

### Step 4: Generate and Execute Script

If the user confirms:

1. **Read the template**: Read `templates/setup-project.sh.md` from this skill directory

2. **Replace placeholders**:
   - `{SOLUTION_NAME}` → User's solution name
   - `{DB_STORE}` → Selected database store
   - `{FHIR_VERSION}` → Selected FHIR version (R4 or R5)
   - `{FRAMEWORK}` → Framework version (net8.0 or net9.0)
   - `{ASPIRE_VERSION}` → "9.5.2" or "Disable"
   - `{INCLUDE_TEST}` → "true" or "false"
   - `{REDIS}` → "true" or "false"
   - `{OPENAPI}` → "true" or "false"
   - `{OTEL}` → "true" or "false"
   - `{AUDIT}` → "true" or "false"
   - `{CORS}` → "true" or "false"

3. **Write the script**: Save to `/tmp/fhir-setup-{timestamp}.sh`

4. **Make executable**: Run `chmod +x /tmp/fhir-setup-{timestamp}.sh`

5. **Execute**: Run the script using the Bash tool

6. **Monitor output**: Watch for errors, especially:
   - "dotnet template creation failed" → Templates not installed
   - Permission errors → Check directory permissions
   - Git errors → Git not configured

### Step 5: Post-Creation Guidance

After successful creation, provide next steps:

```
✅ Project created successfully!

📁 Location: ./{ProjectName}

Next steps:
1. Navigate to the project:
   cd {ProjectName}

2. Review the configuration:
   - Check appsettings.json for database connection strings
   - Review fhirengine.json for handler registration

3. Build and run:
   dotnet build
   dotnet run

4. Access the FHIR API:
   - Base URL: http://localhost:5000 (or https://localhost:5001)
   - Metadata: http://localhost:5000/metadata
   - Swagger UI: http://localhost:5000/swagger

5. For custom implementations:
   - Add handlers in Handlers/ directory
   - Register handlers in fhirengine.json
   - Implement custom data store (if using DbStore=Custom)

6. For logging to SQS or other services:
   - Add AWS SDK packages: dotnet add package AWSSDK.SQS
   - Configure logging in appsettings.json
   - Add custom middleware in Program.cs
```

### Step 6: Troubleshooting

If errors occur:

**Template Not Found**
```
Error: Could not find template 'fhirengine-webapi'

Solution: Install FHIR Engine WebAPI template:
  dotnet new install Ihis.FhirEngine.WebApiTemplate.CSharp
  dotnet new list | grep fhir
```

**R4B Not Supported**
```
Error: Invalid FHIR version 'R4B'

Solution: Check template version. You may need to use R4 instead:
  dotnet new fhirengine-webapi --help
  # Check available --fhirversion options
```

**Permission Denied**
```
Solution: Ensure you have write permissions in the current directory:
  ls -la
  # Run from a directory where you have write access
```

---

## Mode B: Add Features to Existing Project

When an existing FHIR Engine project is detected, follow the detailed instructions in **[mode-b-add-features.md](mode-b-add-features.md)**.

**Quick Overview:**
1. Scan project to detect currently enabled features
2. Ask which features to add (Redis, OpenAPI, Audit, CORS, OpenTelemetry, Test Project)
3. Display planned changes for confirmation
4. Read `templates/add-features.sh.md` template
5. Replace placeholders with selected features
6. Execute script to add packages and update configuration
7. Verify build succeeds
8. Provide feature-specific next steps

See [mode-b-add-features.md](mode-b-add-features.md) for complete step-by-step implementation details.

---

## Configuration Options Reference

### Database Store Options

| Value | Description | Use Case |
|-------|-------------|----------|
| `None` | In-memory (no persistence) | Testing, prototypes |
| `Document` | Cosmos DB / DynamoDB | Azure cloud, document-oriented |
| `Relational` | SQL Server | Enterprise, relational data |
| `DocumentPg` | PostgreSQL JSONB | AWS/GCP, document-oriented |
| `RelationalPg` | PostgreSQL | AWS/GCP, relational data |
| `Custom` | Custom implementation | Legacy systems, SQS logging |
| `Remote` | Proxy to remote server | FHIR gateway |

### FHIR Versions

- **R4**: Maximum compatibility, most implementations
- **R4B**: R4 + bug fixes (limited support)
- **R5**: Latest features, subscriptions, obligations

### Aspire Versions

- **9.5.2**: Latest, recommended for new projects
- **9.3.1**: Stable LTS version
- **Disable**: No Aspire (traditional deployment)

## Example Usage

### Example 1: Quick Start
```
User: "Create a new FHIR project"
Claude: [Asks configuration questions]
User: [Selects DocumentPg, R5, enable Aspire]
Claude: [Shows summary, creates project]
```

### Example 2: Specific Requirements
```
User: "I want to create a FHIR web API project with PostgreSQL data store, use R4B FHIR version, enable logging to SQS"

Claude:
1. [Collects configuration via AskUserQuestion]
2. [Sets DbStore=DocumentPg or Custom, FhirVersion=R4B]
3. [Shows summary including SQS logging note]
4. [Creates project]
5. [Provides post-setup guide for SQS integration]
```

### Example 3: Custom Data Store
```
User: "Setup a FHIR project with custom data store"
Claude: [Sets DbStore=Custom, proceeds with setup]
Post-setup guidance includes:
  - Implement IDataStore interface
  - Add custom logging (SQS, CloudWatch, etc.)
  - Configure in DI container
```

## Advanced Customization

After project creation, users can customize:

### 1. Custom Logging (SQS, CloudWatch, etc.)

Add logging middleware in `Program.cs`:
```csharp
builder.Services.AddSingleton<ILoggerProvider, SqsLoggerProvider>();
```

### 2. Custom Handlers

Create handlers in `Handlers/` directory and register in `fhirengine.json`:
```json
{
  "handlers": [
    {
      "name": "CustomPatientHandler",
      "type": "MyFhirApi.Handlers.CustomPatientHandler",
      "category": "CRUD",
      "resource": "Patient"
    }
  ]
}
```

### 3. Custom Data Store

For `DbStore=Custom`, implement `IDataStore`:
```csharp
public class CustomDataStore : IDataStore
{
    // Implement CRUD operations
    // Add SQS logging, legacy system integration, etc.
}
```

## Notes

- **Platform**: This skill generates bash scripts (Linux/macOS/WSL). For Windows PowerShell, use the original fhir-new.ps1 script.
- **Documentation Files**: Copying .github/prompts is optional and requires the source path to exist.
- **Solution File**: Automatically opens in default .sln handler on Linux (typically Rider or VS Code with extensions).
- **Template Versions**: Always check `dotnet new fhirengine-webapi --help` for supported options in your installed template version.

## Related Skills

- **fhir-handler-generator**: Generate specific FHIR handlers after project setup
- **fhir-custom-resource**: Create custom FHIR resources
- **fhir-config-troubleshooting**: Debug configuration issues
- **fhir-errors-debugger**: Troubleshoot runtime errors
