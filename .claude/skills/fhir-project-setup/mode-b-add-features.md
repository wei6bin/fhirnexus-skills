# Mode B: Add Features to Existing FHIR Engine Project

This document contains detailed instructions for adding features to existing FHIR Engine projects.

## Overview

Use this mode when the user wants to enable features in an existing FHIR Engine project (e.g., "enable Redis caching in my FHIR project").

## Step 1B: Detect Current Project Configuration

1. **Scan the project** to identify:
   - Project name from `*.csproj` file
   - FHIR version from package references (`Hl7.Fhir.R4` or `Hl7.Fhir.R5`)
   - Framework version from `<TargetFramework>` in .csproj
   - Currently enabled features by checking:
     - **Redis**: Package reference `Ihis.FhirEngine.Caching.Redis` or Redis config in appsettings.json
     - **OpenAPI**: Package reference `Swashbuckle.AspNetCore` or Swagger in Program.cs
     - **OpenTelemetry**: Package reference `OpenTelemetry.*` packages
     - **Audit**: Package reference `Ihis.FhirEngine.Audit`
     - **CORS**: CORS configuration in Program.cs
     - **Test Project**: Test project in solution

2. **Display current configuration**:
```
📋 Current FHIR Engine Project Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project Name:      {ProjectName}
FHIR Version:      {R4/R5}
Framework:         {net8.0/net9.0}

Currently Enabled Features:
  • Redis Caching:    {Yes/No}
  • OpenAPI/Swagger:  {Yes/No}
  • OpenTelemetry:    {Yes/No}
  • Audit Logging:    {Yes/No}
  • CORS:             {Yes/No}
  • Test Project:     {Yes/No}
```

## Step 2B: Ask Which Features to Add

Use `AskUserQuestion` to ask which features to enable:

**Question: Add Features**
- Header: "Add Features"
- Question: "Which features would you like to add to your FHIR Engine project?"
- Options (only show features NOT currently enabled):
  - label: "Enable Redis Caching"
    description: "Add distributed caching with Redis for better performance"
  - label: "Enable OpenAPI/Swagger"
    description: "Add API documentation and testing UI"
  - label: "Enable OpenTelemetry"
    description: "Add distributed tracing and observability"
  - label: "Enable Audit Logging"
    description: "Track all FHIR operations for compliance"
  - label: "Enable CORS"
    description: "Configure Cross-Origin Resource Sharing"
  - label: "Add Test Project"
    description: "Add BDD integration test project"
- Multi-select: true

## Step 3B: Display Planned Changes

Show the user what changes will be made:

```
📝 Planned Changes for {ProjectName}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The following features will be added:
  • {Feature 1}
  • {Feature 2}
  ...

Files that will be modified:
  • {ProjectName}.csproj (NuGet packages)
  • Program.cs (service configuration)
  • appsettings.json (feature settings)
  {• Test project files (if test project selected)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Ask: "Should I proceed with adding these features?"

## Step 4B: Apply Feature Additions

For each selected feature, apply the necessary changes:

### Enable Redis Caching

1. **Add NuGet package**:
   ```bash
   dotnet add package Ihis.FhirEngine.Caching.Redis
   dotnet add package StackExchange.Redis
   ```

2. **Update Program.cs** - Add after `builder.Services.AddFhirEngine()`:
   ```csharp
   // Add Redis caching
   builder.Services.AddStackExchangeRedisCache(options =>
   {
       options.Configuration = builder.Configuration.GetConnectionString("Redis");
   });
   ```

3. **Update appsettings.json** - Add connection string:
   ```json
   "ConnectionStrings": {
     "Redis": "localhost:6379"
   }
   ```

### Enable OpenAPI/Swagger

1. **Add NuGet packages**:
   ```bash
   dotnet add package Swashbuckle.AspNetCore
   dotnet add package Ihis.FhirEngine.OpenApi
   ```

2. **Update Program.cs**:
   - Add before `var app = builder.Build();`:
     ```csharp
     // Add OpenAPI/Swagger
     builder.Services.AddEndpointsApiExplorer();
     builder.Services.AddSwaggerGen();
     ```
   - Add after `var app = builder.Build();`:
     ```csharp
     // Enable Swagger UI
     app.UseSwagger();
     app.UseSwaggerUI();
     ```

### Enable OpenTelemetry

1. **Add NuGet packages**:
   ```bash
   dotnet add package OpenTelemetry.Extensions.Hosting
   dotnet add package OpenTelemetry.Instrumentation.AspNetCore
   dotnet add package OpenTelemetry.Exporter.Console
   ```

2. **Update Program.cs** - Add before `builder.Services.AddFhirEngine()`:
   ```csharp
   // Add OpenTelemetry
   builder.Services.AddOpenTelemetry()
       .WithTracing(tracerProviderBuilder =>
       {
           tracerProviderBuilder
               .AddAspNetCoreInstrumentation()
               .AddConsoleExporter();
       });
   ```

### Enable Audit Logging

1. **Add NuGet package**:
   ```bash
   dotnet add package Ihis.FhirEngine.Audit
   ```

2. **Update Program.cs** - Add after `builder.Services.AddFhirEngine()`:
   ```csharp
   // Add Audit logging
   builder.Services.AddFhirAudit(options =>
   {
       options.EnableAuditLog = true;
   });
   ```

3. **Update appsettings.json**:
   ```json
   "FhirEngine": {
     "Audit": {
       "Enabled": true,
       "LogToConsole": true
     }
   }
   ```

### Enable CORS

1. **Update Program.cs**:
   - Add before `var app = builder.Build();`:
     ```csharp
     // Add CORS
     builder.Services.AddCors(options =>
     {
         options.AddDefaultPolicy(policy =>
         {
             policy.WithOrigins(builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>())
                   .AllowAnyMethod()
                   .AllowAnyHeader();
         });
     });
     ```
   - Add after `var app = builder.Build();` (before `app.UseFhirEngine()`):
     ```csharp
     app.UseCors();
     ```

2. **Update appsettings.json**:
   ```json
   "Cors": {
     "AllowedOrigins": ["http://localhost:3000", "https://localhost:3001"]
   }
   ```

### Add Test Project

1. **Create test project** using dotnet template:
   ```bash
   dotnet new fhirengine-test -n {ProjectName}.Tests
   dotnet sln add {ProjectName}.Tests/{ProjectName}.Tests.csproj
   ```

## Step 5B: Execute Changes

1. **Read the template**: Read `templates/add-features.sh.md` from this skill directory

2. **Replace placeholders**:
   - `{PROJECT_DIR}` → Current directory
   - `{PROJECT_NAME}` → Detected project name
   - `{CSPROJ_FILE}` → Path to .csproj file
   - `{ENABLE_REDIS}` → "true" or "false"
   - `{ENABLE_OPENAPI}` → "true" or "false"
   - `{ENABLE_OTEL}` → "true" or "false"
   - `{ENABLE_AUDIT}` → "true" or "false"
   - `{ENABLE_CORS}` → "true" or "false"
   - `{ADD_TEST_PROJECT}` → "true" or "false"

3. **Write the script**: Save to `/tmp/fhir-add-features-{timestamp}.sh`

4. **Make executable**: Run `chmod +x /tmp/fhir-add-features-{timestamp}.sh`

5. **Execute**: Run the script using the Bash tool

6. **Monitor output**: Watch for:
   - Package installation errors
   - File modification errors
   - Build failures

## Step 6B: Post-Modification Guidance

After successful feature addition:

```
✅ Features added successfully!

Added features:
  • {Feature 1}
  • {Feature 2}
  ...

Modified files:
  • {ProjectName}.csproj
  • Program.cs
  • appsettings.json

Next steps:
1. Review the changes:
   git diff

2. Update configuration values in appsettings.json:
   {Feature-specific config instructions}

3. Build and test:
   dotnet build
   dotnet run

4. Commit changes:
   git add .
   git commit -m "Add {features} to FHIR Engine project"
```

**Feature-Specific Guidance:**

- **Redis**: Update connection string in appsettings.json to point to your Redis server
- **OpenAPI**: Access Swagger UI at http://localhost:5000/swagger
- **OpenTelemetry**: Configure exporter (Console, Jaeger, Zipkin) in appsettings.json
- **Audit**: Configure audit log destination (console, file, database)
- **CORS**: Update AllowedOrigins with your frontend URLs
- **Test Project**: Navigate to test project and run `dotnet test`

## Troubleshooting

### Build Fails After Adding Feature

**Cause**: Package version conflicts

**Solution**:
1. Check package versions: `dotnet list package`
2. Update conflicting packages to compatible versions
3. Clear NuGet cache: `dotnet nuget locals all --clear`
4. Rebuild: `dotnet build`

### Feature Not Working

**Cause**: Incomplete configuration

**Solution**:
1. Verify all code changes were applied in Program.cs
2. Check appsettings.json has required configuration
3. Ensure middleware order is correct in Program.cs
4. Check application logs for configuration errors

### Duplicate Configuration Warning

**Cause**: Feature partially configured manually

**Solution**:
1. Review existing configuration: `git diff Program.cs`
2. Either complete manual configuration or remove it and re-run skill
3. Ensure no duplicate service registrations

## Examples

See [examples/add-features-examples.md](examples/add-features-examples.md) for detailed real-world scenarios.
