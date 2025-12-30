---
name: fhir-config-troubleshooting
description: Troubleshoots fhirengine.json and appsettings.json configuration issues. Use when encountering configuration errors, handler registration problems, or data store configuration issues.
allowed-tools: Read, Grep, Glob
---

# FHIR Configuration Troubleshooting

This Skill helps you diagnose and fix FHIR Engine configuration problems.

## Quick Troubleshooting Checklist

1. **Validate JSON syntax** - Both files must be valid JSON
2. **Check required sections** - `SystemPlugins` and `Handlers` are required in fhirengine.json
3. **Verify handler registration** - Handlers must be registered in `Handlers.Repository` or `Handlers.FromClass`
4. **Confirm data store configuration** - Connection strings and AcceptedTypes must match your setup

## Common Configuration Issues

### Handler Not Found
When handlers aren't registered:
- Check `Handlers.FromClass` namespace matches your handler class exactly
- Verify handler class is in your project and properly namespaced
- Ensure handlers have correct `[FhirHandler]` attributes
- Confirm the handler's `AcceptedTypes` includes the resource type you're requesting

### Data Store Configuration Errors
When data stores fail:
- Verify connection string name exists in `appsettings.json`
- Confirm `UseSqlDocument`, `UsePostgreSQL`, etc. flags are correct
- Check `AcceptedTypes` array includes required resource types
- Validate unique identifier in data store config

### System Plugins Not Loading
When plugins fail to initialize:
- Ensure plugin names are spelled correctly in `SystemPlugins`
- Check plugin requires correct packages in project file
- Verify plugin configuration nested under `SystemPlugins.<PluginName>`

## Configuration Examples

### SQL Server Document Store
```json
{
  "Handlers": {
    "Repository": {
      "FhirDataStore<@Local>": {
        "UseSqlDocument": true,
        "ConnectionString": "Local",
        "AcceptedTypes": ["Patient", "Appointment"]
      }
    }
  }
}
```

### PostgreSQL Document Store
```json
{
  "Handlers": {
    "Repository": {
      "FhirDataStore<@Postgres>": {
        "UsePostgreSQL": true,
        "ConnectionString": "PostgresConnection",
        "AcceptedTypes": ["Patient", "Observation"]
      }
    }
  }
}
```

### Handler Class Registration
```json
{
  "Handlers": {
    "FromClass": {
      "MyNamespace.PatientHandlers": true,
      "MyNamespace.AppointmentHandlers": true
    }
  }
}
```

## How to Diagnose

When you encounter a configuration error:

1. **Show me the error message** - Paste the full error or stack trace
2. **Share your configuration files** - Ask me to review your fhirengine.json and appsettings.json
3. **Describe what you're trying to do** - e.g., "I want to use PostgreSQL with relational models"

I'll:
- Identify the root cause
- Show the correct configuration
- Explain the required packages and setup
- Point to relevant documentation

## Required NuGet Packages by Data Store

### SQL Server Document Store
```xml
<PackageReference Include="Ihis.FhirEngine.WebApi.R4" />
<PackageReference Include="Ihis.FhirEngine.Data.SqlServer" />
```

### PostgreSQL Document Store
```xml
<PackageReference Include="Ihis.FhirEngine.WebApi.R4" />
<PackageReference Include="Ihis.FhirEngine.Data.PostgreSQL" />
```

### SQL Server Relational Models
```xml
<PackageReference Include="Ihis.FhirEngine.WebApi.R4" />
<PackageReference Include="Ihis.FhirEngine.Data.RelationalModels" />
<PackageReference Include="Ihis.FhirEngine.Data.SqlServer.RelationalModels" />
```

### PostgreSQL Relational Models
```xml
<PackageReference Include="Ihis.FhirEngine.WebApi.R4" />
<PackageReference Include="Ihis.FhirEngine.Data.RelationalModels" />
<PackageReference Include="Ihis.FhirEngine.Data.PostgreSQL.RelationalModels" />
```

### DynamoDB + S3 (AWS)
```xml
<PackageReference Include="Ihis.FhirEngine.WebApi.R4" />
<PackageReference Include="Ihis.FhirEngine.Data.DynamoDb" />
<PackageReference Include="Ihis.FhirEngine.Data.S3" />
```

**Note:** Replace `R4` with `R5` if using FHIR R5.

## Program.cs Setup

Your `Program.cs` must bootstrap FHIR Engine. Minimal setup:

```csharp
using Ihis.FhirEngine.WebApi.R4;

var builder = WebApplication.CreateBuilder(args);

// Add FHIR Engine services
builder.Services.AddFhirEngine(builder.Configuration);

var app = builder.Build();

// Use FHIR Engine middleware
app.UseFhirEngine();

app.Run();
```

### With SQL Server Document Store
```csharp
using Ihis.FhirEngine.WebApi.R4;
using Ihis.FhirEngine.Data.SqlServer;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddFhirEngine(builder.Configuration)
    .AddSqlServerDocumentStore();  // Reads config from fhirengine.json

var app = builder.Build();
app.UseFhirEngine();
app.Run();
```

### With PostgreSQL Document Store
```csharp
using Ihis.FhirEngine.WebApi.R4;
using Ihis.FhirEngine.Data.PostgreSQL;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddFhirEngine(builder.Configuration)
    .AddPostgreSQLDocumentStore();

var app = builder.Build();
app.UseFhirEngine();
app.Run();
```

### With Custom Handlers
```csharp
using Ihis.FhirEngine.WebApi.R4;
using Ihis.FhirEngine.Data.SqlServer;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddFhirEngine(builder.Configuration)
    .AddSqlServerDocumentStore()
    .AddHandlersFromAssembly(typeof(Program).Assembly);  // Scans for handlers

var app = builder.Build();
app.UseFhirEngine();
app.Run();
```

## Additional Configuration Options

### System Plugins Configuration

Enable built-in features via the `SystemPlugins` section:

```json
{
  "SystemPlugins": {
    "Metadata": {
      "Enabled": true
    },
    "CustomResources": {
      "Enabled": true
    },
    "HealthChecks": {
      "Enabled": true
    }
  }
}
```

### Multiple Data Store Configuration

You can configure multiple data stores for different resource types:

```json
{
  "Handlers": {
    "Repository": {
      "FhirDataStore<@Patients>": {
        "UseSqlDocument": true,
        "ConnectionString": "PatientsDB",
        "AcceptedTypes": ["Patient", "Person"]
      },
      "FhirDataStore<@Clinical>": {
        "UsePostgreSQL": true,
        "ConnectionString": "ClinicalDB",
        "AcceptedTypes": ["Observation", "Condition", "Procedure"]
      }
    }
  }
}
```

## Related Skills

- **Handler implementation?** Ask about creating handlers - the `handler-patterns` skill will help
- **Error debugging?** Share your error message - the `fhir-errors-debugger` skill will help

## Reference Documentation

For complete FHIR Engine documentation:
- FHIR Engine NuGet package repository
- Official FHIR specification: https://hl7.org/fhir/
- Check your FHIR Engine version release notes for specific features
