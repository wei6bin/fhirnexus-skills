---
name: fhir-errors-debugger
description: Debugs FHIR Engine runtime errors, exceptions, and stack traces. Use when your application crashes, you get error messages, or handlers are not working as expected.
allowed-tools: Read, Grep, Glob
---

# FHIR Engine Error Debugging

This Skill helps you understand and fix FHIR Engine errors that may be misleading or unclear.

## Common Error Categories

### 1. Configuration Errors

#### ConfigurationException
**What it means:** Invalid fhirengine.json or appsettings.json structure

**How to fix:**
- Validate JSON syntax (use JSON validator)
- Check required sections exist: `SystemPlugins`, `Handlers`
- Verify connection string names match between files

**Example Error:**
```
System.InvalidOperationException: Unable to resolve service for type 'IFhirDataStore'
```
**Root Cause:** Data store not configured in `Handlers.Repository`

---

#### HandlerNotRegisteredException
**What it means:** FHIR Engine can't find a handler for the requested operation

**How to fix:**
- Register handler class in `Handlers.FromClass`
- Ensure `[FhirHandler]` attribute has correct `AcceptedTypes`
- Verify handler method signature matches expected pattern
- Check handler category matches the operation phase

**Example Error:**
```
No handler found for interaction type 'Read' on resource type 'Patient'
```
**Root Cause:** Either no handler registered, or `AcceptedTypes` doesn't include "Patient"

---

#### InvalidHandlerSignatureException
**What it means:** Handler method signature doesn't match FHIR Engine expectations

**How to fix:**
- Return type must match interaction (Task<Resource> for Read, IAsyncEnumerable for Search)
- Include IFhirContext parameter
- Include CancellationToken parameter
- For Read/Update/Delete, include string id parameter
- For Create/Update, include Resource parameter

**Example Error:**
```
Handler method 'ReadPatient' has invalid signature
```
**Root Cause:** Missing parameters or wrong return type

---

### 2. Handler Execution Errors

#### ResourceNotFoundException
**What it means:** Requested resource ID doesn't exist

**How to fix:**
- Verify the resource ID is correct
- Check database connectivity
- Ensure data store is configured for the resource type

**Example Error:**
```
Patient/123 not found
```
**Root Cause:** Resource doesn't exist or wrong database

---

#### InvalidResourceStateException
**What it means:** Resource violates FHIR constraints or business rules

**How to fix:**
- Check required fields are populated
- Validate data types match FHIR specification
- Ensure references point to existing resources
- Review custom validation logic

**Example Error:**
```
Patient.birthDate is not a valid FHIR date
```
**Root Cause:** Invalid data format

---

#### ConflictException (409)
**What it means:** Resource version mismatch (ETag conflict)

**How to fix:**
- Fetch latest version of resource
- Include correct If-Match header with current version
- Handle concurrent updates appropriately

**Example Error:**
```
Version mismatch: expected '3' but got '2'
```
**Root Cause:** Resource was updated by another process

---

### 3. Data Store Errors

#### ConnectionStringNotFoundException
**What it means:** Connection string name in fhirengine.json doesn't exist in appsettings.json

**How to fix:**
```json
// fhirengine.json
{
  "Handlers": {
    "Repository": {
      "FhirDataStore<@Local>": {
        "ConnectionString": "Local"  // Must match appsettings.json key
      }
    }
  }
}

// appsettings.json
{
  "ConnectionStrings": {
    "Local": "Server=localhost;Database=FhirDb;..."
  }
}
```

---

#### DocumentStoreException
**What it means:** NoSQL document store operation failed

**Common causes:**
- Database doesn't exist or isn't deployed
- Schema migration not run
- Permissions issue
- Invalid JSON in stored document

**How to fix:**
- Run database deployment/migration
- Check connection string has correct permissions
- Verify database exists

---

#### RepositoryException
**What it means:** Data access layer error (general)

**How to fix:**
- Check database connectivity
- Review SQL logs for actual error
- Verify EF Core migrations applied
- Check database user permissions

---

### 4. FHIR Validation Errors

#### ValidationException
**What it means:** Resource violates FHIR profile or schema

**How to fix:**
- Review FHIR specification for the resource type
- Check required fields are present
- Validate data types (dates, codes, etc.)
- Ensure cardinality constraints met (min/max occurrences)

**Example Error:**
```
Validation failed: Patient.identifier is required
```
**Root Cause:** Missing required field

---

#### UnsupportedMediaType (415)
**What it means:** Content-Type header not supported

**How to fix:**
- Use `Content-Type: application/fhir+json` for JSON
- Use `Content-Type: application/fhir+xml` for XML
- Ensure Accept header matches response format

---

### 5. Pipeline and Middleware Errors

#### NullReferenceException in Handler
**What it means:** Accessing null object in handler

**How to fix:**
- Check context.Request properties exist before using
- Validate resource parameters aren't null
- Use null-conditional operators (?.)
- Check injected dependencies are registered

---

#### TimeoutException
**What it means:** Operation took too long

**How to fix:**
- Optimize database queries
- Add indexes to frequently searched fields
- Increase timeout settings
- Use async streaming for large result sets

---

## How to Get Help

When posting an error, include:

### 1. The Full Error Message and Stack Trace
```
System.InvalidOperationException: No handler found for interaction type 'Read'
   at Ihis.FhirEngine.Core.Pipeline.HandlerResolver.Resolve(...)
   at Ihis.FhirEngine.Core.Pipeline.FhirPipeline.ExecuteAsync(...)
```

### 2. The HTTP Request
```
GET /Patient/123
Accept: application/fhir+json
```

### 3. Relevant Configuration
```json
{
  "Handlers": {
    "FromClass": {
      "MyNamespace.PatientHandlers": true
    }
  }
}
```

### 4. Handler Code (if applicable)
```csharp
[FhirHandler(HandlerCategory.CRUD, FhirInteractionType.Read, AcceptedTypes = new[] { "Patient" })]
public async Task<Patient> ReadPatient(IFhirContext context, string id, CancellationToken ct)
{
    // handler code
}
```

### 5. Any Relevant Logs
Include application logs, SQL logs, or diagnostic output

## Error Message Translation Guide

| You See This | It Actually Means | Fix This |
|:-------------|:------------------|:---------|
| "Unable to resolve service" | Missing dependency registration | Add service in Program.cs or fhirengine.json |
| "No handler found" | Handler not registered or wrong AcceptedTypes | Register in FromClass or check AcceptedTypes |
| "Invalid signature" | Handler method parameters wrong | Match expected signature pattern |
| "Version mismatch" | Concurrent update conflict | Use If-Match header correctly |
| "Connection string not found" | Name mismatch between configs | Match ConnectionString name in both files |
| "Validation failed" | Resource doesn't meet FHIR spec | Add required fields or fix data types |

## Common Root Causes and Solutions

### "Unable to resolve service" Errors

**Root Causes:**
1. Missing `AddFhirEngine()` in Program.cs
2. Missing data store registration (e.g., `AddSqlServerDocumentStore()`)
3. Handler class not registered in DI container
4. Missing NuGet package

**Solution Pattern:**
```csharp
// Program.cs must have:
builder.Services.AddFhirEngine(builder.Configuration)
    .AddSqlServerDocumentStore()  // Or your data store
    .AddHandlersFromAssembly(typeof(Program).Assembly);
```

### Version Conflicts

**Root Cause:** Multiple FHIR versions or incompatible package versions

**Solution:**
1. Ensure all `Ihis.FhirEngine.*` packages use same version
2. Use either R4 or R5 consistently, not mixed
3. Check `Directory.Packages.props` if using Central Package Management

### Database Connection Issues

**Common Errors:**
- "Connection string not found"
- "Cannot connect to database"
- "Login failed for user"

**Checklist:**
1. Connection string name in fhirengine.json matches appsettings.json
2. Connection string format is valid
3. Database server is accessible
4. Database exists (or auto-deploy is enabled)
5. User has correct permissions

### FHIR Validation Resources

When validation fails, check:
- Resource conforms to FHIR spec for your version (R4/R4B/R5)
- Required fields are present
- Data types are correct (e.g., dates in YYYY-MM-DD format)
- Cardinality constraints met (min/max occurrences)
- CodeableConcepts use valid codes if binding strength is "required"

**FHIR Spec References:**
- R4: https://hl7.org/fhir/R4/
- R4B: https://hl7.org/fhir/R4B/
- R5: https://hl7.org/fhir/R5/

## Debugging Tools Available

When you ask for help, I can use:
- **Grep** - Search through handler code and configs for patterns
- **Glob** - Find files by pattern (e.g., all handler files)
- **Read** - View entire files to understand context

I'll use these to:
1. Find the root cause of your error
2. Identify configuration issues
3. Suggest the correct fix
4. Provide working code examples

## Related Skills

- **Configuration help?** Ask about fhirengine.json or appsettings.json - the `fhir-config-troubleshooting` skill will help
- **Handler implementation?** Ask about creating handlers - the `handler-patterns` skill will help

## Common Debugging Steps

1. **Check configuration files** - fhirengine.json and appsettings.json
2. **Verify handler registration** - Is the handler class registered?
3. **Review handler signature** - Does it match expected pattern?
4. **Check database connectivity** - Can you connect to the database?
5. **Look for typos** - Resource type names are case-sensitive
6. **Review logs** - Enable detailed logging for more context

## Example: Full Debugging Session

**Error Message:**
```
System.InvalidOperationException: No handler found for interaction type 'Read' on resource type 'Patient'
```

**Debugging Steps:**

1. Check if handler is registered:
   ```bash
   # Search for PatientHandlers registration
   grep -r "PatientHandlers" fhirengine.json
   ```

2. Check handler signature:
   ```bash
   # Find the handler method
   grep -r "FhirHandler.*Read.*Patient" --include="*.cs"
   ```

3. Verify AcceptedTypes:
   ```csharp
   // Should include "Patient"
   [FhirHandler(..., AcceptedTypes = new[] { "Patient" })]
   ```

4. Check handler class namespace:
   ```json
   // Must match actual namespace
   "Handlers": {
     "FromClass": {
       "Correct.Namespace.PatientHandlers": true
     }
   }
   ```

**Resolution:** Handler class namespace didn't match registration. Fixed by updating fhirengine.json.

---

When you encounter an error, share the details with me and I'll help you find the root cause and fix it!
