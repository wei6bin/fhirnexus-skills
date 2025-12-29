# CRUD Handler Templates

Complete templates for standard FHIR CRUD operations.

## Full CRUD Handler Example

```csharp
using Hl7.Fhir.Model;
using Ihis.FhirEngine.Core;
using Ihis.FhirEngine.Core.Data;
using Ihis.FhirEngine.Core.Exceptions;
using Ihis.FhirEngine.Core.Handlers;
using Ihis.FhirEngine.Core.Models;

namespace MyProject.Handlers;

[FhirHandlerClass(AcceptedTypes = new[] { nameof(Patient) })]
public class PatientFhirHandler
{
    private readonly IDataService<Patient> _dataService;
    private readonly ISearchService<Patient> _searchService;
    private readonly ILogger<PatientFhirHandler> _logger;

    public PatientFhirHandler(
        IDataService<Patient> dataService,
        ISearchService<Patient> searchService,
        ILogger<PatientFhirHandler> logger)
    {
        _dataService = dataService;
        _searchService = searchService;
        _logger = logger;
    }

    [FhirHandler(FhirInteractionType.Create)]
    public async Task<Patient> CreateAsync(
        Patient patient,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Creating patient");

        var result = await _dataService.UpsertAsync(
            resource: patient,
            etag: null,
            create: true,
            updateMetadata: true,
            updateVersion: false,
            cancellationToken: cancellationToken);

        return (Patient)result.Resource;
    }

    [FhirHandler(FhirInteractionType.Read)]
    public async Task<Patient?> ReadAsync(
        ResourceKey key,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Reading patient {Id}", key.Id);

        return await _dataService.GetAsync<Patient>(key, cancellationToken);
    }

    [FhirHandler(FhirInteractionType.Update)]
    public async Task<Patient> UpdateAsync(
        Patient patient,
        IFhirContext context,
        CancellationToken cancellationToken)
    {
        if (patient?.Id == null)
            throw new BadRequestException("Patient ID is required");

        _logger.LogInformation("Updating patient {Id}", patient.Id);

        // Check if resource exists
        var existing = await _dataService.GetAsync<Patient>(
            ResourceKey.Create<Patient>(patient.Id),
            cancellationToken);

        if (existing == null)
            throw new ResourceNotFoundException(
                ResourceKey.Create<Patient>(patient.Id));

        // ETag validation for conditional updates
        var ifMatchHeader = context.Request.Headers.IfMatch;
        if (ifMatchHeader != null)
        {
            var expectedETag = WeakETag.FromVersionId(existing.VersionId);
            if (!ifMatchHeader.Equals(expectedETag))
            {
                throw new PreconditionFailedException(
                    $"ETag mismatch: expected {expectedETag}, got {ifMatchHeader}");
            }
        }

        var etag = WeakETag.FromVersionId(existing.VersionId);
        var result = await _dataService.UpsertAsync(
            resource: patient,
            etag: etag,
            create: false,
            updateMetadata: true,
            updateVersion: true,
            cancellationToken: cancellationToken);

        return (Patient)result.Resource;
    }

    [FhirHandler(FhirInteractionType.Delete)]
    public async Task DeleteAsync(
        ResourceKey key,
        IFhirContext context,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Deleting patient {Id}", key.Id);

        // Check if resource exists
        var existing = await _dataService.GetAsync<Patient>(
            key, cancellationToken);

        if (existing == null)
            throw new ResourceNotFoundException(key);

        await _dataService.DeleteAsync(key, cancellationToken);

        context.Response.StatusCode = System.Net.HttpStatusCode.NoContent;
        context.Response.SetIsHandled(true);
    }

    [FhirHandler(FhirInteractionType.SearchType)]
    public async IAsyncEnumerable<Patient> SearchAsync(
        IFhirContext context,
        [EnumeratorCancellation] CancellationToken cancellationToken)
    {
        var searchParams = context.Request.SearchParams;
        _logger.LogInformation("Searching patients with params: {Params}",
            searchParams);

        var searchResult = await _searchService.SearchAsync<Patient>(
            searchParams, cancellationToken);

        foreach (var entry in searchResult.Entry)
        {
            // ⭐ CRITICAL: Always use .ToResource()
            var patient = entry.Resource.ToResource<Patient>();
            yield return patient;
        }
    }
}
```

## Create Handler Only

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Appointment) })]
public class AppointmentFhirHandler
{
    private readonly IDataService<Appointment> _dataService;

    public AppointmentFhirHandler(IDataService<Appointment> dataService)
    {
        _dataService = dataService;
    }

    [FhirHandler(FhirInteractionType.Create)]
    public async Task<Appointment> CreateAsync(
        Appointment appointment,
        CancellationToken cancellationToken)
    {
        // Validation
        if (appointment.Start == null)
            throw new BadRequestException("Appointment start time is required");

        if (appointment.End == null)
            throw new BadRequestException("Appointment end time is required");

        // Create resource
        var result = await _dataService.UpsertAsync(
            appointment, null, true, true, false, cancellationToken);

        return (Appointment)result.Resource;
    }
}
```

## Read Handler with Custom Logic

```csharp
[FhirHandler(FhirInteractionType.Read)]
public async Task<Observation?> ReadAsync(
    ResourceKey key,
    IFhirContext context,
    CancellationToken cancellationToken)
{
    var observation = await _dataService.GetAsync<Observation>(
        key, cancellationToken);

    if (observation == null)
        return null;

    // Apply authorization filter
    var userId = context.Request.Headers.GetUserId();
    if (!await _authService.CanViewObservation(userId, observation.Id))
        throw new UnauthorizedFhirActionException(
            "Insufficient permissions to view this observation");

    // Enrich with additional data
    if (observation.Subject?.Reference != null)
    {
        var patient = await _dataService.GetAsync<Patient>(
            observation.Subject.Reference, cancellationToken);
        // Add patient name to response headers for convenience
        if (patient != null)
        {
            context.Response.Headers.Add(
                "X-Patient-Name",
                patient.Name.FirstOrDefault()?.ToString() ?? "Unknown");
        }
    }

    return observation;
}
```

## Update Handler with Versioning

```csharp
[FhirHandler(FhirInteractionType.Update)]
public async Task<CarePlan> UpdateAsync(
    CarePlan carePlan,
    IFhirContext context,
    CancellationToken cancellationToken)
{
    if (carePlan?.Id == null)
        throw new BadRequestException("CarePlan ID is required");

    var key = ResourceKey.Create<CarePlan>(carePlan.Id);
    var existing = await _dataService.GetAsync<CarePlan>(key, cancellationToken);

    if (existing == null)
        throw new ResourceNotFoundException(key);

    // Business rule: Can't change status from completed to active
    if (existing.Status == RequestStatus.Completed &&
        carePlan.Status == RequestStatus.Active)
    {
        throw new BusinessRuleException(
            "Cannot reactivate completed care plan");
    }

    // Check If-Match header (required for this resource type)
    var ifMatchHeader = context.Request.Headers.IfMatch;
    if (ifMatchHeader == null)
        throw new PreconditionRequiredException("If-Match header required");

    var expectedETag = WeakETag.FromVersionId(existing.VersionId);
    if (!ifMatchHeader.Equals(expectedETag))
    {
        throw new PreconditionFailedException(
            $"Version mismatch: resource has been modified");
    }

    var etag = WeakETag.FromVersionId(existing.VersionId);
    var result = await _dataService.UpsertAsync(
        carePlan, etag, false, true, true, cancellationToken);

    return (CarePlan)result.Resource;
}
```

## Delete Handler with Cascade

```csharp
[FhirHandler(FhirInteractionType.Delete)]
public async Task DeletePatientAsync(
    ResourceKey key,
    IFhirContext context,
    CancellationToken cancellationToken)
{
    // Check if patient exists
    var patient = await _dataService.GetAsync<Patient>(key, cancellationToken);
    if (patient == null)
        throw new ResourceNotFoundException(key);

    // Check for dependent resources
    var appointments = await _searchService.SearchAsync<Appointment>(
        $"patient={key.ToReference()}", cancellationToken);

    if (appointments.Entry.Any(e => e.Resource.ToResource<Appointment>().Status ==
        Appointment.AppointmentStatus.Booked))
    {
        throw new BusinessRuleException(
            "Cannot delete patient with active appointments");
    }

    // Perform soft delete
    await _dataService.DeleteAsync(key, cancellationToken);

    _logger.LogInformation("Deleted patient {Id}", key.Id);

    context.Response.StatusCode = System.Net.HttpStatusCode.NoContent;
    context.Response.SetIsHandled(true);
}
```

## Search Handler with Filtering

```csharp
[FhirHandler(FhirInteractionType.SearchType)]
public async IAsyncEnumerable<Practitioner> SearchActiveAsync(
    IFhirContext context,
    [EnumeratorCancellation] CancellationToken cancellationToken)
{
    var searchParams = context.Request.SearchParams;

    // Add active=true filter if not specified
    if (!searchParams.Contains("active"))
        searchParams += "&active=true";

    var searchResult = await _searchService.SearchAsync<Practitioner>(
        searchParams, cancellationToken);

    foreach (var entry in searchResult.Entry)
    {
        var practitioner = entry.Resource.ToResource<Practitioner>();

        // Additional business logic filtering
        if (IsWithinServiceArea(practitioner))
            yield return practitioner;
    }
}

private bool IsWithinServiceArea(Practitioner practitioner)
{
    // Custom business logic
    return practitioner.Address?.Any(a =>
        a.State == "Singapore") ?? false;
}
```

## UpsertAsync Parameters Explained

```csharp
var result = await _dataService.UpsertAsync(
    resource: patient,           // The FHIR resource to save
    etag: etag,                  // ETag for version checking (null for create)
    create: true,                // true = create, false = update
    updateMetadata: true,        // Update Meta.lastUpdated
    updateVersion: true,         // Increment Meta.versionId
    cancellationToken: ct
);

// Common Patterns:

// CREATE (new resource)
await _dataService.UpsertAsync(patient, null, true, true, false, ct);
// etag: null (no version check)
// create: true (creating new)
// updateMetadata: true (set lastUpdated)
// updateVersion: false (version starts at 1)

// UPDATE (existing resource)
await _dataService.UpsertAsync(patient, etag, false, true, true, ct);
// etag: from existing resource (version check)
// create: false (updating existing)
// updateMetadata: true (update lastUpdated)
// updateVersion: true (increment version)

// UPDATE WITHOUT VERSION CHECK
await _dataService.UpsertAsync(patient, null, false, true, true, ct);
// etag: null (skip version check - use cautiously!)
// create: false
// updateMetadata: true
// updateVersion: true
```

## Common CRUD Patterns

### Pattern: Upsert (Create or Update)

```csharp
[FhirHandler(FhirInteractionType.Create)]
[FhirHandler(FhirInteractionType.Update)]
public async Task<Patient> UpsertAsync(
    Patient patient,
    IFhirContext context,
    CancellationToken cancellationToken)
{
    bool isCreate = context.Request.Interaction == FhirInteractionType.Create;

    WeakETag? etag = null;
    if (!isCreate && patient.Id != null)
    {
        var existing = await _dataService.GetAsync<Patient>(
            ResourceKey.Create<Patient>(patient.Id), cancellationToken);

        if (existing != null)
            etag = WeakETag.FromVersionId(existing.VersionId);
    }

    var result = await _dataService.UpsertAsync(
        patient, etag, isCreate, true, !isCreate, cancellationToken);

    return (Patient)result.Resource;
}
```

### Pattern: Conditional Create (If-None-Exist)

```csharp
[FhirHandler(FhirInteractionType.Create)]
public async Task<Patient> ConditionalCreateAsync(
    Patient patient,
    IFhirContext context,
    CancellationToken cancellationToken)
{
    var ifNoneExist = context.Request.Headers.IfNoneExist;

    if (!string.IsNullOrEmpty(ifNoneExist))
    {
        // Check if resource already exists
        var existing = await _searchService.SearchAsync<Patient>(
            ifNoneExist, cancellationToken);

        if (existing.Entry.Any())
        {
            // Return existing resource with 200 OK
            var existingPatient = existing.Entry.First().Resource.ToResource<Patient>();
            context.Response.StatusCode = System.Net.HttpStatusCode.OK;
            return existingPatient;
        }
    }

    // Create new resource
    var result = await _dataService.UpsertAsync(
        patient, null, true, true, false, cancellationToken);

    context.Response.StatusCode = System.Net.HttpStatusCode.Created;
    return (Patient)result.Resource;
}
```

### Pattern: Conditional Update

```csharp
[FhirHandler(FhirInteractionType.Update)]
public async Task<Patient> ConditionalUpdateAsync(
    Patient patient,
    IFhirContext context,
    CancellationToken cancellationToken)
{
    // Support update by ID or by search criteria
    var resourceId = context.Request.Id;

    if (string.IsNullOrEmpty(resourceId))
    {
        // Conditional update: find resource by search params
        var searchParams = context.Request.SearchParams;
        var results = await _searchService.SearchAsync<Patient>(
            searchParams, cancellationToken);

        if (!results.Entry.Any())
            throw new ResourceNotFoundException("No matching patient found");

        if (results.Entry.Count > 1)
            throw new PreconditionFailedException(
                "Multiple patients match criteria");

        resourceId = results.Entry.First().Resource.Id;
        patient.Id = resourceId;
    }

    var key = ResourceKey.Create<Patient>(resourceId);
    var existing = await _dataService.GetAsync<Patient>(key, cancellationToken);

    if (existing == null)
        throw new ResourceNotFoundException(key);

    var etag = WeakETag.FromVersionId(existing.VersionId);
    var result = await _dataService.UpsertAsync(
        patient, etag, false, true, true, cancellationToken);

    return (Patient)result.Resource;
}
```

## File Naming Convention

```
/Handlers/
  PatientCrudFhirHandler.cs       # All CRUD operations for Patient
  PatientCreateFhirHandler.cs     # Create only
  PatientReadFhirHandler.cs       # Read only
  AppointmentFhirHandler.cs       # All operations for Appointment
```

## Required NuGet Packages

```xml
<PackageReference Include="Ihis.FhirEngine.Core" />
<PackageReference Include="Ihis.FhirEngine.Data" />
<PackageReference Include="Hl7.Fhir.R4" />  <!-- or R5 -->
```

## Sample HTTP Requests

```http
### Variables
@baseUrl = https://localhost:7001
@patientId = patient-123

### Create Patient
POST {{baseUrl}}/Patient
Content-Type: application/fhir+json

{
  "resourceType": "Patient",
  "identifier": [{
    "system": "https://sg.gov.sg/nric",
    "value": "S1234567D"
  }],
  "name": [{
    "family": "Tan",
    "given": ["John"]
  }],
  "gender": "male",
  "birthDate": "1990-01-01"
}

### Read Patient
GET {{baseUrl}}/Patient/{{patientId}}

### Update Patient
PUT {{baseUrl}}/Patient/{{patientId}}
Content-Type: application/fhir+json
If-Match: W/"1"

{
  "resourceType": "Patient",
  "id": "{{patientId}}",
  "identifier": [{
    "system": "https://sg.gov.sg/nric",
    "value": "S1234567D"
  }],
  "name": [{
    "family": "Tan",
    "given": ["John", "Michael"]
  }],
  "gender": "male",
  "birthDate": "1990-01-01"
}

### Delete Patient
DELETE {{baseUrl}}/Patient/{{patientId}}

### Search Patients
GET {{baseUrl}}/Patient?name=Tan&gender=male

### Conditional Create
POST {{baseUrl}}/Patient
Content-Type: application/fhir+json
If-None-Exist: identifier=https://sg.gov.sg/nric|S1234567D

{
  "resourceType": "Patient",
  "identifier": [{
    "system": "https://sg.gov.sg/nric",
    "value": "S1234567D"
  }],
  "name": [{
    "family": "Tan",
    "given": ["John"]
  }]
}
```
