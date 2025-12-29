---
name: handler-patterns
description: Teaches FHIR Engine handler patterns and best practices. Use when creating handlers, writing CRUD operations, or implementing custom FHIR interactions.
allowed-tools: Read, Grep, Glob
---

# Handler Patterns and Best Practices

This Skill guides you through implementing handlers in FHIR Engine using the correct patterns.

## Handler Basics

Handlers are methods decorated with `[FhirHandler]` that process FHIR interactions. They flow through a pipeline:

**PreInteraction** → **PreTransaction** → **PreCRUD** → **CRUD** → **PostCRUD** → **PostTransaction** → **PostInteraction**

## Handler Signature Components

```csharp
[FhirHandler(
    HandlerCategory.CRUD,           // Which phase in pipeline
    FhirInteractionType.Read,        // FHIR operation type
    AcceptedTypes = new[] { "Patient" }  // FHIR resource types
)]
public async Task<Patient> GetPatient(
    IFhirContext context,            // Current request context
    string id,                       // Resource ID (for Read/Update/Delete)
    CancellationToken cancellationToken)  // Cancellation support
{
    // Handler implementation
}
```

## Handler Categories

- **CRUD** - Create, Read, Update, Delete, Search operations
- **PreInteraction/PostInteraction** - Request/response wrapping
- **PreTransaction/PostTransaction** - Database transaction management
- **PreCRUD/PostCRUD** - Pre/post-processing around data operations
- **Custom Operations** - Special operations like `$cancel`

## Common Patterns

### 1. Simple Read Handler
```csharp
[FhirHandler(HandlerCategory.CRUD, FhirInteractionType.Read,
    AcceptedTypes = new[] { "Patient" })]
public async Task<Patient> ReadPatient(
    IFhirContext context,
    string id,
    CancellationToken ct)
{
    var patient = await _repository.GetByIdAsync(id, ct);
    if (patient == null)
        throw new ResourceNotFoundException($"Patient/{id} not found");
    return patient;
}
```

### 2. Create Handler
```csharp
[FhirHandler(HandlerCategory.CRUD, FhirInteractionType.Create,
    AcceptedTypes = new[] { "Patient" })]
public async Task<Patient> CreatePatient(
    IFhirContext context,
    Patient patient,
    CancellationToken ct)
{
    // Validate and set ID
    patient.Id = Guid.NewGuid().ToString();
    patient.Meta = new Meta
    {
        VersionId = "1",
        LastUpdated = DateTimeOffset.UtcNow
    };

    await _repository.CreateAsync(patient, ct);
    return patient;
}
```

### 3. Search Handler with Filtering
```csharp
[FhirHandler(HandlerCategory.CRUD, FhirInteractionType.Search,
    AcceptedTypes = new[] { "Patient" })]
public async IAsyncEnumerable<Patient> SearchPatients(
    IFhirContext context,
    [EnumeratorCancellation] CancellationToken ct)
{
    var searchParams = context.Request.SearchParams;

    // Use IAsyncEnumerable for streaming results
    await foreach (var patient in _repository.SearchAsync(searchParams, ct))
    {
        yield return patient;
    }
}
```

### 4. Update Handler
```csharp
[FhirHandler(HandlerCategory.CRUD, FhirInteractionType.Update,
    AcceptedTypes = new[] { "Patient" })]
public async Task<Patient> UpdatePatient(
    IFhirContext context,
    string id,
    Patient patient,
    CancellationToken ct)
{
    var existing = await _repository.GetByIdAsync(id, ct);
    if (existing == null)
        throw new ResourceNotFoundException($"Patient/{id} not found");

    // Update version
    patient.Id = id;
    patient.Meta = new Meta
    {
        VersionId = (int.Parse(existing.Meta.VersionId) + 1).ToString(),
        LastUpdated = DateTimeOffset.UtcNow
    };

    await _repository.UpdateAsync(patient, ct);
    return patient;
}
```

### 5. Custom Operation Handler
```csharp
[FhirHandler(HandlerCategory.CRUD, FhirInteractionType.OperationType,
    AcceptedTypes = new[] { "Appointment" },
    CustomOperation = "cancel")]
public async Task CancelAppointment(
    IFhirContext context,
    CancellationToken ct)
{
    var id = context.Request.Id;
    var appointment = await _repository.GetByIdAsync(id, ct);

    if (appointment == null)
        throw new ResourceNotFoundException();

    appointment.Status = AppointmentStatus.Cancelled;
    await _repository.UpdateAsync(appointment, ct);

    context.Response.SetOperationResponse(appointment);
    context.Response.SetIsHandled(true);
}
```

### 6. PreCRUD Validation Handler
```csharp
[FhirHandler(HandlerCategory.PreCRUD, FhirInteractionType.Create,
    AcceptedTypes = new[] { "Patient" })]
public Task ValidatePatientBeforeCreate(
    IFhirContext context,
    Patient patient,
    CancellationToken ct)
{
    // Custom validation logic
    if (string.IsNullOrEmpty(patient.Name?.FirstOrDefault()?.Family))
        throw new ValidationException("Patient must have a family name");

    // Validation passed
    return Task.CompletedTask;
}
```

## Configuring Handlers

### Method 1: Register Handler Class in fhirengine.json
```json
{
  "Handlers": {
    "FromClass": {
      "YourNamespace.PatientHandlers": true,
      "YourNamespace.AppointmentHandlers": true
    }
  }
}
```

### Method 2: Use Data Store Handlers
If using built-in data stores (SQL Server, PostgreSQL, DynamoDB), handlers are automatically registered when you configure the repository:
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

## Handler Return Types

| Interaction Type | Return Type | Example |
|:-----------------|:------------|:--------|
| Read | `Task<Resource>` | `Task<Patient>` |
| Create | `Task<Resource>` | `Task<Patient>` |
| Update | `Task<Resource>` | `Task<Patient>` |
| Delete | `Task` or `Task<OperationOutcome>` | `Task` |
| Search | `IAsyncEnumerable<Resource>` or `Task<List<Resource>>` | `IAsyncEnumerable<Patient>` |
| Custom Operation | `Task` or `Task<Resource>` | `Task` |
| Validation | `Task` | `Task` |

## Testing Your Handler

1. Ensure handler class is registered in `fhirengine.json`
2. Handler must accept correct interaction types
3. Return type must match signature
4. CancellationToken should be respected
5. Test with HTTP client (Postman, curl, etc.)

## Common Mistakes to Avoid

1. **Wrong HandlerCategory** - CRUD handlers must use `HandlerCategory.CRUD`
2. **Missing AcceptedTypes** - Always specify which resource types the handler accepts
3. **Incorrect return type** - Search must return `IAsyncEnumerable` or `Task<List>`
4. **Not handling null resources** - Always check if resource exists for Read/Update/Delete
5. **Forgetting to set Meta** - Create/Update should update `Meta.VersionId` and `Meta.LastUpdated`

## Advanced Handler Patterns

### Accessing HTTP Context
```csharp
[FhirHandler(HandlerCategory.CRUD, FhirInteractionType.Read,
    AcceptedTypes = new[] { "Patient" })]
public async Task<Patient> ReadPatient(
    IFhirContext context,
    IHttpContextAccessor httpContextAccessor,  // Inject HTTP context
    string id,
    CancellationToken ct)
{
    var userId = httpContextAccessor.HttpContext?.User.FindFirst("sub")?.Value;
    // Use userId for authorization logic

    var patient = await _repository.GetByIdAsync(id, ct);
    return patient;
}
```

### Using Dependency Injection in Handlers
```csharp
public class PatientHandlers
{
    private readonly IFhirRepository _repository;
    private readonly ILogger<PatientHandlers> _logger;
    private readonly IValidator<Patient> _validator;

    // Dependencies injected via constructor
    public PatientHandlers(
        IFhirRepository repository,
        ILogger<PatientHandlers> logger,
        IValidator<Patient> validator)
    {
        _repository = repository;
        _logger = logger;
        _validator = validator;
    }

    [FhirHandler(HandlerCategory.CRUD, FhirInteractionType.Create,
        AcceptedTypes = new[] { "Patient" })]
    public async Task<Patient> CreatePatient(
        IFhirContext context,
        Patient patient,
        CancellationToken ct)
    {
        _logger.LogInformation("Creating patient");

        var validationResult = await _validator.ValidateAsync(patient, ct);
        if (!validationResult.IsValid)
            throw new ValidationException(validationResult.Errors);

        return await _repository.CreateAsync(patient, ct);
    }
}
```

### Handler Execution Order

When multiple handlers match a request, they execute in order:

1. **PreInteraction** handlers (all matching)
2. **PreTransaction** handlers (all matching)
3. **PreCRUD** handlers (all matching)
4. **CRUD** handlers (first matching or all if returning IAsyncEnumerable)
5. **PostCRUD** handlers (all matching)
6. **PostTransaction** handlers (all matching)
7. **PostInteraction** handlers (all matching)

**Important:** Only ONE CRUD handler should return data. Use PreCRUD/PostCRUD for additional logic.

### Conditional Handler Execution

Handlers can inspect context and skip execution:

```csharp
[FhirHandler(HandlerCategory.PreCRUD, FhirInteractionType.Create,
    AcceptedTypes = new[] { "Patient" })]
public Task ValidatePatientIdentifier(
    IFhirContext context,
    Patient patient,
    CancellationToken ct)
{
    // Only validate if header present
    if (!context.Request.Headers.ContainsKey("X-Validate-Identifier"))
        return Task.CompletedTask;

    // Validation logic here
    if (string.IsNullOrEmpty(patient.Identifier?.FirstOrDefault()?.Value))
        throw new ValidationException("Identifier required");

    return Task.CompletedTask;
}
```

## Package References for Custom Handlers

Required NuGet packages for handler development:

```xml
<PackageReference Include="Ihis.FhirEngine.Core" />
<PackageReference Include="Ihis.FhirEngine.WebApi.R4" />  <!-- Or R5 -->
<PackageReference Include="Hl7.Fhir.R4" />  <!-- FHIR models -->
```

## Related Skills

- **Configuration issues?** Ask about fhirengine.json or appsettings.json - the `fhir-config-troubleshooting` skill will help
- **Error debugging?** Share your error message - the `fhir-errors-debugger` skill will help

## What to Do When Asking for Help

When you need help with handlers, tell me:
- What FHIR interaction you're implementing (Read, Create, Search, etc.)
- What resource types (Patient, Appointment, etc.)
- Any custom business logic you need
- If you're using data mapping (AutoMapper) or custom models
- Any error messages you're getting

I'll provide the complete handler implementation and configuration.
