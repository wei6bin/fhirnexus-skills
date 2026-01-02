# Custom Operation Templates

Templates for implementing FHIR custom operations ($cancel, $validate, etc.)

## Instance Operation Template

Instance operations work on specific resource instances: `POST /Patient/123/$operation`

```csharp
using Hl7.Fhir.Model;
using Ihis.FhirEngine.Core;
using Ihis.FhirEngine.Core.Data;
using Ihis.FhirEngine.Core.Exceptions;
using Ihis.FhirEngine.Core.Handlers;

namespace MyProject.Handlers;

[FhirHandlerClass(AcceptedTypes = new[] { nameof(Patient) })]
public class PatientMarkDeceasedHandler
{
    private readonly IDataService<Patient> _dataService;
    private readonly ILogger<PatientMarkDeceasedHandler> _logger;

    public PatientMarkDeceasedHandler(
        IDataService<Patient> dataService,
        ILogger<PatientMarkDeceasedHandler> logger)
    {
        _dataService = dataService;
        _logger = logger;
    }

    // POST /Patient/{id}/$mark-deceased
    [FhirHandler(FhirInteractionType.OperationInstance,
        CustomOperation = "mark-deceased")]
    public async Task MarkDeceasedAsync(
        IFhirContext context,
        ResourceKey key,
        DateTimeOffset? timeOfDeath,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Marking patient {Id} as deceased", key.Id);

        // Fetch existing patient
        var patient = await _dataService.GetAsync<Patient>(
            key, cancellationToken);

        if (patient == null)
            throw new ResourceNotFoundException(key);

        // Business validation
        if (patient.Deceased != null)
            throw new BusinessRuleException("Patient already marked as deceased");

        // Update patient
        patient.Deceased = new FhirDateTime(
            timeOfDeath?.DateTime ?? DateTime.UtcNow);

        var result = await _dataService.UpsertAsync(
            patient, null, false, true, true, cancellationToken);

        // Set response
        context.Response.SetResourceResponse(result.Resource);
    }
}
```

## Type Operation Template

Type operations work at the resource type level: `POST /Patient/$operation`

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Patient) })]
public class PatientValidateHandler
{
    private readonly ISearchService<Patient> _searchService;
    private readonly IValidator<Patient> _validator;

    public PatientValidateHandler(
        ISearchService<Patient> searchService,
        IValidator<Patient> validator)
    {
        _searchService = searchService;
        _validator = validator;
    }

    // POST /Patient/$validate
    [FhirHandler(FhirInteractionType.OperationType,
        CustomOperation = "validate")]
    public async Task ValidateAsync(
        IFhirContext context,
        Parameters parameters,
        CancellationToken cancellationToken)
    {
        // Extract patient from parameters
        if (!parameters.TryGetValue("patient", out Patient patient))
            throw new BadRequestException("Patient parameter required");

        // Perform validation
        var validationResult = await _validator.ValidateAsync(
            patient, cancellationToken);

        if (!validationResult.IsValid)
        {
            var issues = validationResult.Errors.Select(e =>
                new OperationOutcome.IssueComponent
                {
                    Severity = OperationOutcome.IssueSeverity.Error,
                    Code = OperationOutcome.IssueType.Invalid,
                    Diagnostics = e.ErrorMessage
                }).ToArray();

            throw new MultipleValidationException(
                System.Net.HttpStatusCode.BadRequest, issues);
        }

        // Return success
        var outcome = new OperationOutcome
        {
            Issue = new List<OperationOutcome.IssueComponent>
            {
                new()
                {
                    Severity = OperationOutcome.IssueSeverity.Information,
                    Code = OperationOutcome.IssueType.Informational,
                    Diagnostics = "Patient is valid"
                }
            }
        };

        context.Response.AddResource(outcome);
        context.Response.StatusCode = System.Net.HttpStatusCode.OK;
        context.Response.SetIsHandled(true);
    }
}
```

## System Operation Template

System operations work at the system level: `POST /$operation`

```csharp
[FhirHandlerClass]
public class SystemProcessBatchHandler
{
    private readonly IDataService<Patient> _patientDataService;
    private readonly IDataService<Observation> _observationDataService;

    // POST /$process-batch
    [FhirHandler(FhirInteractionType.OperationSystem,
        CustomOperation = "process-batch")]
    public async Task ProcessBatchAsync(
        IFhirContext context,
        Parameters parameters,
        CancellationToken cancellationToken)
    {
        if (!parameters.TryGetValue("batchId", out string batchId))
            throw new BadRequestException("batchId parameter required");

        // Process batch logic
        var results = await ProcessBatchInternal(batchId, cancellationToken);

        // Return result parameters
        var resultParams = new Parameters();
        resultParams.Add("processedCount", new Integer(results.Count));
        resultParams.Add("status", new FhirString("completed"));

        context.Response.SetResourceResponse(resultParams);
    }

    private async Task<List<string>> ProcessBatchInternal(
        string batchId,
        CancellationToken ct)
    {
        // Implementation
        return new List<string>();
    }
}
```

## Operation with Complex Parameters

```csharp
// POST /Appointment/$book
[FhirHandler(FhirInteractionType.OperationType,
    CustomOperation = "book")]
public async Task BookAppointmentAsync(
    IFhirContext context,
    Parameters parameters,
    CancellationToken cancellationToken)
{
    // Extract complex parameters
    if (!parameters.TryGetValue("patient", out ResourceReference patientRef))
        throw new BadRequestException("patient parameter required");

    if (!parameters.TryGetValue("practitioner", out ResourceReference practitionerRef))
        throw new BadRequestException("practitioner parameter required");

    if (!parameters.TryGetValue("slot", out ResourceReference slotRef))
        throw new BadRequestException("slot parameter required");

    if (!parameters.TryGetValue("appointmentType", out CodeableConcept appointmentType))
        throw new BadRequestException("appointmentType parameter required");

    parameters.TryGetValue("comment", out string? comment);

    // Business logic
    var appointment = new Appointment
    {
        Status = Appointment.AppointmentStatus.Booked,
        AppointmentType = appointmentType,
        Participant = new List<Appointment.ParticipantComponent>
        {
            new()
            {
                Actor = patientRef,
                Required = Appointment.ParticipantRequired.Required,
                Status = Appointment.ParticipationStatus.Accepted
            },
            new()
            {
                Actor = practitionerRef,
                Required = Appointment.ParticipantRequired.Required,
                Status = Appointment.ParticipationStatus.Accepted
            }
        },
        Slot = new List<ResourceReference> { slotRef },
        Comment = comment
    };

    var result = await _dataService.UpsertAsync(
        appointment, null, true, true, false, cancellationToken);

    context.Response.SetResourceResponse(result.Resource);
}
```

## OperationDefinition Example

Create in `/Conformance/operation-patient-mark-deceased.json`:

```json
{
  "resourceType": "OperationDefinition",
  "id": "Patient-mark-deceased",
  "url": "https://fhir.synapxe.sg/OperationDefinition/Patient-mark-deceased",
  "name": "MarkDeceasedPatient",
  "title": "Mark Patient as Deceased",
  "status": "active",
  "kind": "operation",
  "code": "mark-deceased",
  "resource": ["Patient"],
  "system": false,
  "type": false,
  "instance": true,
  "description": "Marks a patient as deceased with optional time of death",
  "parameter": [
    {
      "name": "timeOfDeath",
      "use": "in",
      "min": 0,
      "max": "1",
      "documentation": "The date and time of death. Defaults to current time if not provided.",
      "type": "dateTime"
    },
    {
      "name": "return",
      "use": "out",
      "min": 1,
      "max": "1",
      "documentation": "The updated Patient resource",
      "type": "Patient"
    }
  ]
}
```

## Type Operation OperationDefinition

```json
{
  "resourceType": "OperationDefinition",
  "id": "Patient-validate",
  "url": "https://fhir.synapxe.sg/OperationDefinition/Patient-validate",
  "name": "ValidatePatient",
  "title": "Validate Patient Resource",
  "status": "active",
  "kind": "operation",
  "code": "validate",
  "resource": ["Patient"],
  "system": false,
  "type": true,
  "instance": false,
  "description": "Validates a Patient resource against business rules",
  "parameter": [
    {
      "name": "patient",
      "use": "in",
      "min": 1,
      "max": "1",
      "documentation": "The Patient resource to validate",
      "type": "Patient"
    },
    {
      "name": "return",
      "use": "out",
      "min": 1,
      "max": "1",
      "documentation": "Validation result as OperationOutcome",
      "type": "OperationOutcome"
    }
  ]
}
```

## Capability Statement Integration

Update `/Conformance/capability-statement.json`:

```json
{
  "rest": [{
    "resource": [{
      "type": "Patient",
      "interaction": [
        {"code": "read"},
        {"code": "update"}
      ],
      "operation": [
        {
          "name": "mark-deceased",
          "definition": "https://fhir.synapxe.sg/OperationDefinition/Patient-mark-deceased"
        },
        {
          "name": "validate",
          "definition": "https://fhir.synapxe.sg/OperationDefinition/Patient-validate"
        }
      ]
    }]
  }]
}
```

## Sample HTTP Requests

```http
### Instance Operation - Mark Deceased
POST {{baseUrl}}/Patient/patient-123/$mark-deceased
Content-Type: application/fhir+json

{
  "resourceType": "Parameters",
  "parameter": [{
    "name": "timeOfDeath",
    "valueDateTime": "2024-01-15T14:30:00Z"
  }]
}

### Type Operation - Validate
POST {{baseUrl}}/Patient/$validate
Content-Type: application/fhir+json

{
  "resourceType": "Parameters",
  "parameter": [{
    "name": "patient",
    "resource": {
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
  }]
}

### System Operation - Process Batch
POST {{baseUrl}}/$process-batch
Content-Type: application/fhir+json

{
  "resourceType": "Parameters",
  "parameter": [{
    "name": "batchId",
    "valueString": "batch-2024-001"
  }]
}

### Complex Operation - Book Appointment
POST {{baseUrl}}/Appointment/$book
Content-Type: application/fhir+json

{
  "resourceType": "Parameters",
  "parameter": [
    {
      "name": "patient",
      "valueReference": {
        "reference": "Patient/patient-123"
      }
    },
    {
      "name": "practitioner",
      "valueReference": {
        "reference": "Practitioner/prac-456"
      }
    },
    {
      "name": "slot",
      "valueReference": {
        "reference": "Slot/slot-789"
      }
    },
    {
      "name": "appointmentType",
      "valueCodeableConcept": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
          "code": "ROUTINE",
          "display": "Routine appointment"
        }]
      }
    },
    {
      "name": "comment",
      "valueString": "Patient requested morning slot"
    }
  ]
}
```

## Parameters Helper Class

For complex operations, create a parameters helper:

```csharp
public static class ParametersExtensions
{
    public static bool TryGetValue<T>(
        this Parameters parameters,
        string name,
        out T value) where T : class
    {
        var param = parameters.Parameter?
            .FirstOrDefault(p => p.Name == name);

        if (param == null)
        {
            value = null!;
            return false;
        }

        // Handle different parameter types
        value = param.Value as T
            ?? param.Resource as T
            ?? null!;

        return value != null;
    }

    public static void AddParameter(
        this Parameters parameters,
        string name,
        Base value)
    {
        parameters.Parameter ??= new List<Parameters.ParameterComponent>();
        parameters.Parameter.Add(new Parameters.ParameterComponent
        {
            Name = name,
            Value = value as DataType,
            Resource = value as Resource
        });
    }
}

// Usage
parameters.AddParameter("status", new FhirString("completed"));
parameters.AddParameter("patient", patientResource);
```

## Common Operation Patterns

### Cancel Operation

```csharp
[FhirHandler(FhirInteractionType.OperationInstance,
    CustomOperation = "cancel")]
public async Task CancelAsync(
    IFhirContext context,
    ResourceKey key,
    string? reason,
    CancellationToken cancellationToken)
{
    var appointment = await _dataService.GetAsync<Appointment>(key, cancellationToken);
    if (appointment == null) throw new ResourceNotFoundException(key);

    if (appointment.Status == Appointment.AppointmentStatus.Cancelled)
        throw new BusinessRuleException("Appointment already cancelled");

    appointment.Status = Appointment.AppointmentStatus.Cancelled;
    appointment.CancellationReason = new CodeableConcept
    {
        Text = reason ?? "Cancelled by user"
    };

    var result = await _dataService.UpsertAsync(
        appointment, null, false, true, true, cancellationToken);

    context.Response.SetResourceResponse(result.Resource);
}
```

### Match Operation (Return Bundle)

```csharp
[FhirHandler(FhirInteractionType.OperationType,
    CustomOperation = "match")]
public async Task MatchPatientsAsync(
    IFhirContext context,
    Parameters parameters,
    CancellationToken cancellationToken)
{
    if (!parameters.TryGetValue("criteria", out Patient criteria))
        throw new BadRequestException("criteria parameter required");

    // Perform matching logic
    var matches = await FindMatchingPatients(criteria, cancellationToken);

    // Return as searchset Bundle
    var bundle = new Bundle
    {
        Type = Bundle.BundleType.Searchset,
        Total = matches.Count,
        Entry = matches.Select(p => new Bundle.EntryComponent
        {
            Resource = p,
            Search = new Bundle.SearchComponent
            {
                Mode = Bundle.SearchEntryMode.Match,
                Score = CalculateMatchScore(criteria, p)
            }
        }).ToList()
    };

    context.Response.SetResourceResponse(bundle);
}
```
