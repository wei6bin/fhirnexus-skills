---
name: fhir-handler-generator
description: Generates FHIR Engine handlers for CRUD operations, custom operations, and workflows. Use when creating handlers, implementing FHIR interactions, or adding custom operations to FHIR resources.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# FHIR Handler Code Generator

This skill generates production-ready FHIR Engine handlers following framework patterns and best practices.

## Quick Start

When you ask me to create a handler, I'll guide you through:

1. **Handler Type** - CRUD, Custom Operation, or Workflow
2. **Resource Type** - Which FHIR resource (Patient, Appointment, etc.)
3. **Business Logic** - What the handler should do
4. **Code Generation** - Complete implementation with configuration

## Handler Types

### CRUD Handlers
Standard FHIR operations on resources:
- **Create** - POST /Patient
- **Read** - GET /Patient/123
- **Update** - PUT /Patient/123
- **Delete** - DELETE /Patient/123
- **Search** - GET /Patient?name=Smith

**When to use:** Standard resource operations

### Custom Operations
FHIR operations beyond CRUD:
- **Instance** - POST /Patient/123/$mark-deceased
- **Type** - POST /Patient/$validate
- **System** - POST /$process-batch

**When to use:** Domain-specific business logic

### Workflow Handlers
Cross-cutting concerns in the request pipeline:
- **PreInteraction** - Auth, format validation
- **PreCRUD** - Business validation, reference resolution
- **PostCRUD** - Related updates within transaction
- **PostInteraction** - Notifications, audit logging

**When to use:** Validation, enrichment, side effects

## Handler Category Selection

**Quick Decision Tree:**

```
Need external notifications/audit?
  → PostInteraction

Need to update related resources after main operation?
  → PostCRUD

Main data operation (Create/Read/Update/Delete)?
  → CRUD

Need database lookup for validation/enrichment?
  → PreCRUD

Only format validation or authorization?
  → PreInteraction
```

**Detailed Guide:** See [decision-matrix.md](decision-matrix.md)

## Code Templates

### CRUD Handler Template

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Patient) })]
public class PatientFhirHandler
{
    private readonly IDataService<Patient> _dataService;
    private readonly ISearchService<Patient> _searchService;

    public PatientFhirHandler(
        IDataService<Patient> dataService,
        ISearchService<Patient> searchService)
    {
        _dataService = dataService;
        _searchService = searchService;
    }

    [FhirHandler(FhirInteractionType.Create)]
    public async Task<Patient> CreateAsync(
        Patient patient,
        CancellationToken cancellationToken)
    {
        var result = await _dataService.UpsertAsync(
            patient, null, true, true, false, cancellationToken);
        return (Patient)result.Resource;
    }

    [FhirHandler(FhirInteractionType.Read)]
    public async Task<Patient?> ReadAsync(
        ResourceKey key,
        CancellationToken cancellationToken)
        => await _dataService.GetAsync<Patient>(key, cancellationToken);

    [FhirHandler(FhirInteractionType.Update)]
    public async Task<Patient> UpdateAsync(
        Patient patient,
        IFhirContext context,
        CancellationToken cancellationToken)
    {
        if (patient?.Id == null)
            throw new BadRequestException("Patient ID is required");

        var existing = await _dataService.GetAsync<Patient>(
            ResourceKey.Create<Patient>(patient.Id), cancellationToken);
        if (existing == null)
            throw new ResourceNotFoundException(
                ResourceKey.Create<Patient>(patient.Id));

        // ETag validation
        var ifMatchHeader = context.Request.Headers.IfMatch;
        if (ifMatchHeader != null)
        {
            var expectedETag = WeakETag.FromVersionId(existing.VersionId);
            if (!ifMatchHeader.Equals(expectedETag))
                throw new PreconditionFailedException("ETag mismatch");
        }

        var etag = WeakETag.FromVersionId(existing.VersionId);
        var result = await _dataService.UpsertAsync(
            patient, etag, false, true, true, cancellationToken);
        return (Patient)result.Resource;
    }
}
```

**Full CRUD templates:** See [templates/crud-handler.md](templates/crud-handler.md)

### Custom Operation Template

```csharp
// Instance Operation: POST /Patient/123/$mark-deceased
[FhirHandler(FhirInteractionType.OperationInstance,
    CustomOperation = "mark-deceased")]
public async Task MarkDeceasedAsync(
    IFhirContext context,
    ResourceKey key,
    DateTimeOffset? timeOfDeath,
    CancellationToken cancellationToken)
{
    var patient = await _dataService.GetAsync<Patient>(key, cancellationToken);
    if (patient == null) throw new ResourceNotFoundException(key);

    patient.Deceased = new FhirDateTime(
        timeOfDeath?.DateTime ?? DateTime.UtcNow);
    var result = await _dataService.UpsertAsync(
        patient, null, false, true, true, cancellationToken);

    context.Response.SetResourceResponse(result.Resource);
}

// Type Operation: POST /Patient/$validate
[FhirHandler(FhirInteractionType.OperationType,
    CustomOperation = "validate")]
public async Task ValidateAsync(
    IFhirContext context,
    Parameters parameters,
    CancellationToken cancellationToken)
{
    if (!parameters.TryGetValue("patient", out Patient patient))
        throw new ResourceNotValidException("Patient parameter required");

    var validationErrors = new List<string>();
    if (patient.Name?.Any() != true)
        validationErrors.Add("Patient name is required");

    if (validationErrors.Any())
        throw new PatientValidationException(validationErrors);

    context.Response.StatusCode = HttpStatusCode.OK;
    context.Response.SetIsHandled(true);
}
```

**Full custom operation templates:** See [templates/custom-operation.md](templates/custom-operation.md)

### Workflow Handler Template

```csharp
// PreCRUD Validation
[FhirHandler("ValidatePatient", HandlerCategory.PreCRUD,
    FhirInteractionType.Create)]
public async Task ValidateCreateAsync(
    Patient patient,
    CancellationToken cancellationToken)
{
    if (patient == null)
        throw new BadRequestException("Patient resource is required");

    var nric = patient.Identifier?
        .FirstOrDefault(i => i.System == "https://sg.gov.sg/nric")?.Value;
    if (string.IsNullOrEmpty(nric))
        throw new ResourceNotValidException("Patient NRIC is required");

    if (!await _authService.CanCreatePatient(nric, cancellationToken))
        throw new UnauthorizedFhirActionException("Insufficient permissions");
}

// PostInteraction Audit
[AsyncFhirHandler("AuditChange", HandlerCategory.PostInteraction)]
public async Task AuditAsync(
    IFhirContext context,
    Patient patient,
    CancellationToken cancellationToken)
{
    await _auditService.LogChange(
        patient.Id, context.Request.Interaction, cancellationToken);
}
```

**Full workflow templates:** See [templates/workflow-handler.md](templates/workflow-handler.md)

## Handler Execution Pipeline

Handlers execute in this order:

```
1. PreInteraction  → Request validation, auth
2. PreTransaction  → Begin transaction
3. PreCRUD         → Business validation, enrichment
4. CRUD            → Main data operation
5. PostCRUD        → Related updates (same transaction)
6. PostTransaction → Commit/rollback transaction
7. PostInteraction → Notifications, audit (outside transaction)
```

## Critical Patterns

### Exception Handling

**NEVER manually create OperationOutcome** - Use framework exceptions:

```csharp
// ✅ CORRECT - Use framework exceptions
throw new BadRequestException("Patient ID is required");
throw new ResourceNotFoundException(ResourceKey.Create<Patient>(id));
throw new PreconditionFailedException("ETag mismatch");

// ❌ WRONG - Don't create OperationOutcome manually
var outcome = new OperationOutcome { /* ... */ };
context.Response.AddResource(outcome);
```

### Custom Exceptions

```csharp
public class PatientValidationException : FhirEngineException
{
    public PatientValidationException(
        HttpStatusCode responseStatusCode,
        string message,
        OperationOutcome.IssueSeverity? severity,
        OperationOutcome.IssueType? code,
        string? location = null,
        Exception? innerException = null)
        : base(responseStatusCode, message, severity, code, location, innerException)
    {
    }
}

// Usage
throw new PatientValidationException(
    HttpStatusCode.BadRequest,
    "Invalid NRIC format",
    OperationOutcome.IssueSeverity.Error,
    OperationOutcome.IssueType.Invalid);
```

### SearchResult Extraction

**⭐ CRITICAL:** Always use `.ToResource()` when processing search results:

```csharp
// ✅ CORRECT
var patients = await _searchService.SearchAsync<Patient>(
    "identifier=123", cancellationToken);
foreach (var entry in patients.Entry)
{
    var patient = entry.Resource.ToResource<Patient>();  // ✅ Use .ToResource()
    // Process patient...
}

// ❌ WRONG - Causes serialization issues
var patient = entry.Resource;  // ❌ Don't use directly
```

### Response Handling

```csharp
// Simple resource response
context.Response.SetResourceResponse(patient);
// Equivalent to:
// context.Response.AddResource(patient);
// context.Response.StatusCode = HttpStatusCode.OK;
// context.Response.SetIsHandled(true);

// SetIsHandled Rule: Only LAST handler in pipeline should call it
[FhirHandler(FhirInteractionType.Create)]
public async Task<Patient> CreateAsync(...)
{
    // Return resource - framework calls SetIsHandled automatically
    return patient;
}

[FhirHandler("Validate", HandlerCategory.PreCRUD, FhirInteractionType.Create)]
public Task ValidateAsync(...)
{
    // Don't call SetIsHandled - let CRUD handler finish
    return Task.CompletedTask;
}
```

## Configuration Integration

After creating a handler, update these files:

### 1. fhirengine.json

```json
{
  "Handlers": {
    "FromClass": {
      "MyNamespace.PatientFhirHandler": true
    },
    "Repository": {
      "FhirDataStore<@Local>": {
        "AcceptedTypes": ["Patient"]
      }
    }
  }
}
```

### 2. capability-statement.json

```json
{
  "rest": [{
    "resource": [{
      "type": "Patient",
      "interaction": [
        {"code": "create"},
        {"code": "read"},
        {"code": "update"}
      ],
      "operation": [{
        "name": "mark-deceased",
        "definition": "https://fhir.synapxe.sg/OperationDefinition/Patient-mark-deceased"
      }]
    }]
  }]
}
```

### 3. OperationDefinition (Custom Operations Only)

Create in `/Conformance/operation-patient-mark-deceased.json`:

```json
{
  "resourceType": "OperationDefinition",
  "id": "Patient-mark-deceased",
  "url": "https://fhir.synapxe.sg/OperationDefinition/Patient-mark-deceased",
  "name": "MarkDeceasedPatient",
  "status": "active",
  "kind": "operation",
  "code": "mark-deceased",
  "resource": ["Patient"],
  "system": false,
  "type": false,
  "instance": true,
  "parameter": [{
    "name": "timeOfDeath",
    "use": "in",
    "min": 0,
    "max": "1",
    "type": "dateTime"
  }]
}
```

## File Structure

```
/Handlers/
  PatientCreateFhirHandler.cs      # CRUD handlers
  PatientMarkDeceasedHandler.cs    # Custom operations
  PatientValidationHandler.cs      # Workflow handlers

/Conformance/
  operation-patient-mark-deceased.json

/Sample Requests/
  patient.http
```

## Validation Checklist

Before completing handler generation, verify:

- ✅ `[FhirHandlerClass]` attribute with correct AcceptedTypes
- ✅ `[FhirHandler]` attributes with correct interaction types
- ✅ Resource types in fhirengine.json AcceptedTypes
- ✅ Framework exceptions used (never manual OperationOutcome)
- ✅ `.ToResource()` used for all SearchResult processing
- ✅ SetIsHandled only in final handler or when stopping pipeline
- ✅ Strongly-typed services (IDataService<T>, ISearchService<T>)
- ✅ File naming: `{ResourceType}{Operation}FhirHandler.cs`
- ✅ Configuration updated (fhirengine.json, capability-statement.json)
- ✅ OperationDefinition created for custom operations

## Common Mistakes to Avoid

❌ **Missing Handler Attributes** - Handler won't be discovered
❌ **Wrong AcceptedTypes** - Handler won't match requests
❌ **Manual OperationOutcome** - Breaks framework error handling
❌ **SetIsHandled Too Early** - Stops pipeline prematurely
❌ **Missing .ToResource()** - Causes serialization errors
❌ **Missing Configuration** - Resource type not in AcceptedTypes

## What to Tell Me

When requesting handler generation:

1. **Operation Type**: "Create a CRUD handler" or "Add custom operation $cancel"
2. **Resource**: "For Patient resource" or "For Appointment"
3. **Business Logic**: "Validate NRIC before creation" or "Mark patient as deceased"
4. **Interaction**: Instance, Type, or System level (for custom operations)

**Example:**
```
"Create a custom operation $mark-deceased for Patient that sets the deceased date.
It should be an instance operation (POST /Patient/123/$mark-deceased) that accepts
an optional timeOfDeath parameter."
```

I'll generate:
- Complete handler class
- OperationDefinition conformance resource
- Configuration updates
- Sample HTTP requests
- Validation and error handling

## Related Skills

- **Custom resource creation?** → Use `fhir-custom-resource` skill
- **Configuration issues?** → Use `fhir-config-troubleshooting` skill
- **Error debugging?** → Use `fhir-errors-debugger` skill
