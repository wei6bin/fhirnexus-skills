# Examples: Adding Features to Existing FHIR Engine Projects

This document shows real-world scenarios for adding features to existing FHIR Engine projects.

## Example 1: Enable Redis Caching

**Scenario**: You have a FHIR R5 API in production experiencing performance issues. You want to add Redis caching.

**User Prompt**:
```
Enable Redis caching in my FHIR project
```

**Skill Behavior**:
1. Detects existing FHIR Engine project in current directory
2. Scans project and shows current configuration:
   ```
   📋 Current FHIR Engine Project Configuration
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Project Name:      PatientAPI.R5.DocumentPg
   FHIR Version:      R5
   Framework:         net8.0

   Currently Enabled Features:
     • Redis Caching:    No
     • OpenAPI/Swagger:  Yes
     • OpenTelemetry:    No
     • Audit Logging:    Yes
     • CORS:             Yes
     • Test Project:     Yes
   ```

3. Offers to add Redis (already knows only Redis is missing)
4. Shows planned changes:
   ```
   📝 Planned Changes
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Features to add:
     • Redis Caching

   Files that will be modified:
     • PatientAPI.R5.DocumentPg.csproj (add NuGet packages)
     • Program.cs (add Redis services)
     • appsettings.json (add Redis connection string)
   ```

5. After confirmation, executes changes:
   - Adds `Ihis.FhirEngine.Caching.Redis` package
   - Adds `StackExchange.Redis` package
   - Updates Program.cs with Redis configuration
   - Adds Redis connection string to appsettings.json
   - Runs `dotnet build` to verify

6. Shows next steps:
   ```
   ✅ Redis caching enabled!

   Next steps:
   1. Update Redis connection string in appsettings.json:
      "ConnectionStrings": {
        "Redis": "your-redis-server:6379"
      }

   2. Test caching:
      dotnet run
      # Query the same resource twice - second request should be faster

   3. Commit changes:
      git add .
      git commit -m "Add Redis caching for performance"
   ```

---

## Example 2: Add Multiple Features at Once

**Scenario**: You have a basic FHIR project without monitoring. You want to add OpenTelemetry and OpenAPI for better observability and documentation.

**User Prompt**:
```
Add OpenTelemetry and Swagger documentation to my FHIR API
```

**Skill Behavior**:
1. Detects project and shows current state
2. Asks which features to add (multi-select):
   ```
   Which features would you like to add?
   [ ] Enable Redis Caching
   [x] Enable OpenAPI/Swagger
   [x] Enable OpenTelemetry
   [ ] Enable Audit Logging
   [ ] Enable CORS
   [ ] Add Test Project
   ```

3. Shows planned changes for both features
4. After confirmation:
   - Adds OpenAPI packages and Swagger configuration
   - Adds OpenTelemetry packages and instrumentation
   - Updates Program.cs with both sets of services
   - Builds project to verify

5. Provides feature-specific guidance:
   ```
   ✅ Features added successfully!

   Added features:
     • OpenAPI/Swagger
     • OpenTelemetry

   Next steps:
   1. Access Swagger UI at: http://localhost:5000/swagger

   2. Configure OpenTelemetry exporter in appsettings.json:
      "OpenTelemetry": {
        "Exporter": "Console"  // or "Jaeger", "Zipkin", etc.
      }

   3. Test the API and view traces in console output
   ```

---

## Example 3: Add Test Project to Existing API

**Scenario**: You have a FHIR API in production but no automated tests. You want to add a test project.

**User Prompt**:
```
Add test project to my FHIR Engine API
```

**Skill Behavior**:
1. Detects existing project
2. Shows current configuration (no test project)
3. Asks for confirmation
4. Creates test project:
   ```bash
   dotnet new fhirengine-test -n PatientAPI.R5.DocumentPg.Tests
   dotnet sln add PatientAPI.R5.DocumentPg.Tests/PatientAPI.R5.DocumentPg.Tests.csproj
   ```

5. Provides guidance:
   ```
   ✅ Test project created!

   Test project: PatientAPI.R5.DocumentPg.Tests

   Next steps:
   1. Navigate to test project:
      cd PatientAPI.R5.DocumentPg.Tests

   2. Review sample tests in Features/ directory

   3. Run tests:
      dotnet test

   4. Add your own tests:
      - Create .feature files for BDD scenarios
      - Implement step definitions
   ```

---

## Example 4: Incremental Feature Addition

**Scenario**: You're building a FHIR API iteratively. You start minimal and add features as needed.

### Step 1: Create minimal project
```
User: Create a minimal FHIR R5 project for development
Skill: Creates project with None database, no features
```

### Step 2: Add database
```
User: I want to switch to PostgreSQL
Skill: [This would require fhir-migration skill or manual migration]
       Suggests: "For database migration, manually update packages and connection strings"
```

### Step 3: Add OpenAPI for testing
```
User: Add Swagger to my FHIR project
Skill: Adds OpenAPI/Swagger packages and configuration
```

### Step 4: Add observability before production
```
User: Enable OpenTelemetry and audit logging
Skill: Adds both features with configuration
```

### Step 5: Add caching for performance
```
User: Enable Redis caching
Skill: Adds Redis packages and configuration
```

**Result**: Incrementally built a production-ready FHIR API

---

## Example 5: Enable CORS for Web Client

**Scenario**: You built a FHIR API for backend use. Now you need to call it from a web browser.

**User Prompt**:
```
Enable CORS in my FHIR project for my React app running on localhost:3000
```

**Skill Behavior**:
1. Detects project and shows CORS is not enabled
2. Offers to add CORS
3. After confirmation:
   - Updates Program.cs with CORS policy
   - Adds CORS configuration to appsettings.json with default origins
   - Builds project

4. Provides customization guidance:
   ```
   ✅ CORS enabled!

   Default configuration allows:
     • http://localhost:3000
     • https://localhost:3001

   To customize:
   1. Edit appsettings.json:
      "Cors": {
        "AllowedOrigins": [
          "http://localhost:3000",
          "https://your-production-domain.com"
        ]
      }

   2. Restart the API:
      dotnet run

   3. Test from your React app - API calls should now work!
   ```

---

## Example 6: Compliance Requirements - Add Audit Logging

**Scenario**: Your FHIR API needs to comply with healthcare regulations requiring audit trails.

**User Prompt**:
```
Add audit logging to my FHIR project for compliance
```

**Skill Behavior**:
1. Detects project
2. Offers to add audit logging feature
3. After confirmation:
   - Adds `Ihis.FhirEngine.Audit` package
   - Updates Program.cs with audit services
   - Adds audit configuration to appsettings.json
   - Builds project

4. Provides compliance guidance:
   ```
   ✅ Audit logging enabled!

   Configuration:
     • Audit log enabled: true
     • Log to console: true

   To customize for compliance:
   1. Update appsettings.json:
      "FhirEngine": {
        "Audit": {
          "Enabled": true,
          "LogToConsole": false,
          "LogToFile": true,
          "LogFilePath": "/var/log/fhir-audit/",
          "IncludeRequestBody": true,
          "IncludeResponseBody": false
        }
      }

   2. Audit logs will include:
      • User identity
      • Resource type and ID
      • Operation (Create, Read, Update, Delete)
      • Timestamp
      • IP address

   3. Review audit logs regularly for compliance
   ```

---

## Feature Combination Matrix

Common feature combinations for different scenarios:

| Scenario | Features to Enable |
|----------|-------------------|
| **Development** | OpenAPI/Swagger |
| **Testing** | OpenAPI, Test Project |
| **Staging** | OpenAPI, OpenTelemetry, Audit |
| **Production** | Redis, OpenTelemetry, Audit, CORS |
| **Enterprise** | All features |
| **Compliance** | Audit, OpenTelemetry |
| **High Performance** | Redis, OpenTelemetry |
| **Web Client Integration** | CORS, OpenAPI |

---

## Troubleshooting Feature Addition

### Issue: Build Fails After Adding Feature

**Symptom**: `dotnet build` fails with package conflicts

**Solution**:
1. Check package versions:
   ```bash
   dotnet list package
   ```

2. Update conflicting packages:
   ```bash
   dotnet add package [PackageName] --version [LatestVersion]
   ```

3. Rebuild:
   ```bash
   dotnet build
   ```

### Issue: Feature Not Working After Addition

**Symptom**: Redis/OTEL/etc. not actually functioning

**Common Causes**:
1. **Missing configuration**: Update appsettings.json with required settings
2. **Service order**: Services might be registered in wrong order in Program.cs
3. **Middleware order**: Middleware must be in correct order (e.g., CORS before routing)

**Solution**: Review Program.cs and compare with template documentation

### Issue: Duplicate Configuration

**Symptom**: Skill says "already configured" but feature not working

**Solution**:
1. Check if configuration is incomplete:
   ```bash
   git diff Program.cs
   ```

2. Manually complete the configuration
3. Or remove existing configuration and re-run skill

---

## Best Practices

1. **Add features incrementally**: Test each feature before adding the next
2. **Commit after each addition**: Easier to roll back if needed
3. **Update configuration**: Default values might not suit your environment
4. **Test thoroughly**: Verify feature works as expected
5. **Document changes**: Update README with enabled features and configuration
