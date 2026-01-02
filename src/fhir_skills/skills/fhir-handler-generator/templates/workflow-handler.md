# Workflow Handler Templates

Templates for cross-cutting concerns in the FHIR request pipeline.

## PreInteraction Handler Templates

### Authentication Handler

```csharp
[FhirHandlerClass]
public class AuthenticationHandler
{
    private readonly IAuthenticationService _authService;

    public AuthenticationHandler(IAuthenticationService authService)
    {
        _authService = authService;
    }

    [FhirHandler("Authenticate", HandlerCategory.PreInteraction)]
    public async Task AuthenticateAsync(
        IFhirContext context,
        CancellationToken cancellationToken)
    {
        var token = context.Request.Headers.Authorization;

        if (string.IsNullOrEmpty(token))
            throw new UnauthorizedFhirActionException("Authorization header missing");

        var user = await _authService.ValidateTokenAsync(token, cancellationToken);

        if (user == null)
            throw new UnauthorizedFhirActionException("Invalid token");

        // Store user in context for downstream handlers
        context.Items["User"] = user;
    }
}
```

### Format Validation Handler

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Patient) })]
public class PatientFormatValidationHandler
{
    [FhirHandler("ValidateFormat", HandlerCategory.PreInteraction,
        FhirInteractionType.Create, FhirInteractionType.Update)]
    public Task ValidateFormatAsync(
        Patient patient,
        CancellationToken cancellationToken)
    {
        // NRIC format validation
        var nric = patient.Identifier?
            .FirstOrDefault(i => i.System == "https://sg.gov.sg/nric")?.Value;

        if (!string.IsNullOrEmpty(nric) && !NricValidator.TryValidate(nric))
            throw new ResourceNotValidException($"Invalid NRIC format: {nric}");

        // Birth date validation
        if (patient.BirthDate != null)
        {
            if (!DateTime.TryParse(patient.BirthDate, out var birthDate))
                throw new ResourceNotValidException("Invalid birthDate format");

            if (birthDate > DateTime.Now)
                throw new ResourceNotValidException("birthDate cannot be in the future");
        }

        return Task.CompletedTask;
    }
}
```

## PreCRUD Handler Templates

### Reference Resolution Handler

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(CarePlan) })]
public class CarePlanReferenceResolutionHandler
{
    private readonly ISearchService<Patient> _patientSearchService;

    public CarePlanReferenceResolutionHandler(
        ISearchService<Patient> patientSearchService)
    {
        _patientSearchService = patientSearchService;
    }

    [FhirHandler("ResolveReferences", HandlerCategory.PreCRUD,
        FhirInteractionType.Create)]
    public async Task ResolveReferencesAsync(
        CarePlan carePlan,
        CancellationToken cancellationToken)
    {
        // Resolve patient reference from identifier
        if (carePlan.Subject?.Identifier != null)
        {
            var nric = carePlan.Subject.Identifier.Value;
            var patients = await _patientSearchService.SearchAsync<Patient>(
                $"identifier={nric}", cancellationToken);

            if (!patients.Entry.Any())
                throw new ResourceNotFoundException($"Patient with NRIC {nric} not found");

            var patient = patients.Entry.First().Resource.ToResource<Patient>();
            carePlan.Subject.Reference = $"Patient/{patient.Id}";
            carePlan.Subject.Identifier = null; // Remove identifier after resolution
        }
    }
}
```

### Duplicate Prevention Handler

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(CarePlan) })]
public class CarePlanDuplicatePreventionHandler
{
    private readonly ISearchService<CarePlan> _searchService;

    [FhirHandler("PreventDuplicate", HandlerCategory.PreCRUD,
        FhirInteractionType.Create)]
    public async Task PreventDuplicateAsync(
        CarePlan carePlan,
        CancellationToken cancellationToken)
    {
        // Check for active care plan for same patient
        var existing = await _searchService.SearchAsync<CarePlan>(
            $"patient={carePlan.Subject.Reference}&status=active",
            cancellationToken);

        if (existing.Entry.Any())
        {
            throw new BusinessRuleException(
                "Patient already has an active care plan");
        }
    }
}
```

### Business Validation Handler

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Appointment) })]
public class AppointmentBusinessValidationHandler
{
    private readonly IDataService<Slot> _slotDataService;
    private readonly IDataService<Practitioner> _practitionerDataService;

    [FhirHandler("ValidateBusinessRules", HandlerCategory.PreCRUD,
        FhirInteractionType.Create)]
    public async Task ValidateBusinessRulesAsync(
        Appointment appointment,
        CancellationToken cancellationToken)
    {
        // Validate time slot is available
        if (appointment.Slot?.Any() == true)
        {
            var slotRef = appointment.Slot.First().Reference;
            var slot = await _slotDataService.GetAsync<Slot>(
                slotRef, cancellationToken);

            if (slot == null)
                throw new ResourceNotFoundException($"Slot {slotRef} not found");

            if (slot.Status != Slot.SlotStatus.Free)
                throw new BusinessRuleException($"Slot {slotRef} is not available");
        }

        // Validate practitioner is active
        var practitionerRef = appointment.Participant
            ?.FirstOrDefault(p => p.Actor?.Reference?.StartsWith("Practitioner/") == true)
            ?.Actor?.Reference;

        if (practitionerRef != null)
        {
            var practitioner = await _practitionerDataService.GetAsync<Practitioner>(
                practitionerRef, cancellationToken);

            if (practitioner == null)
                throw new ResourceNotFoundException(
                    $"Practitioner {practitionerRef} not found");

            if (practitioner.Active == false)
                throw new BusinessRuleException(
                    $"Practitioner {practitionerRef} is not active");
        }

        // Validate appointment time is in the future
        if (appointment.Start < DateTimeOffset.Now)
            throw new BusinessRuleException("Appointment start time must be in the future");
    }
}
```

## PostCRUD Handler Templates

### Related Resource Update Handler

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Appointment) })]
public class AppointmentSlotUpdateHandler
{
    private readonly IDataService<Slot> _slotDataService;

    [FhirHandler("UpdateSlot", HandlerCategory.PostCRUD,
        FhirInteractionType.Create)]
    public async Task UpdateSlotAfterCreateAsync(
        Appointment appointment,
        CancellationToken cancellationToken)
    {
        if (appointment.Slot?.Any() != true)
            return;

        var slotRef = appointment.Slot.First().Reference;
        var slot = await _slotDataService.GetAsync<Slot>(
            slotRef, cancellationToken);

        if (slot != null)
        {
            slot.Status = Slot.SlotStatus.Busy;
            await _slotDataService.UpsertAsync(
                slot, null, false, true, true, cancellationToken);
        }
    }

    [FhirHandler("UpdateSlot", HandlerCategory.PostCRUD,
        FhirInteractionType.Delete)]
    public async Task UpdateSlotAfterDeleteAsync(
        Appointment appointment,
        CancellationToken cancellationToken)
    {
        if (appointment.Slot?.Any() != true)
            return;

        var slotRef = appointment.Slot.First().Reference;
        var slot = await _slotDataService.GetAsync<Slot>(
            slotRef, cancellationToken);

        if (slot != null)
        {
            slot.Status = Slot.SlotStatus.Free;
            await _slotDataService.UpsertAsync(
                slot, null, false, true, true, cancellationToken);
        }
    }
}
```

### Cache Invalidation Handler

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Patient) })]
public class PatientCacheInvalidationHandler
{
    private readonly ICacheService _cacheService;

    [FhirHandler("InvalidateCache", HandlerCategory.PostCRUD,
        FhirInteractionType.Update, FhirInteractionType.Delete)]
    public async Task InvalidateCacheAsync(
        Patient patient,
        CancellationToken cancellationToken)
    {
        // Invalidate patient cache
        await _cacheService.RemoveAsync($"patient:{patient.Id}", cancellationToken);

        // Invalidate related caches
        await _cacheService.RemoveAsync($"patient:nric:{patient.GetNric()}",
            cancellationToken);
    }
}
```

## PostInteraction Handler Templates

### Audit Logging Handler

```csharp
[FhirHandlerClass]
public class AuditLoggingHandler
{
    private readonly IAuditService _auditService;

    [AsyncFhirHandler("AuditLog", HandlerCategory.PostInteraction)]
    public async Task AuditLogAsync(
        IFhirContext context,
        CancellationToken cancellationToken)
    {
        var audit = new AuditEvent
        {
            Type = new Coding
            {
                System = "http://terminology.hl7.org/CodeSystem/audit-event-type",
                Code = "rest",
                Display = "RESTful Operation"
            },
            Action = MapInteractionToAction(context.Request.Interaction),
            Recorded = DateTimeOffset.Now,
            Outcome = context.Response.StatusCode.IsSuccessStatusCode()
                ? AuditEvent.AuditEventOutcome.Success
                : AuditEvent.AuditEventOutcome.MinorFailure,
            Agent = new List<AuditEvent.AgentComponent>
            {
                new()
                {
                    Who = new ResourceReference
                    {
                        Display = context.Items.Get<User>("User")?.Username ?? "Anonymous"
                    },
                    RequestHeader = context.Request.Headers.Authorization
                }
            },
            Entity = new List<AuditEvent.EntityComponent>
            {
                new()
                {
                    What = new ResourceReference
                    {
                        Reference = $"{context.Request.ResourceType}/{context.Request.Id}"
                    },
                    Type = new Coding { Code = context.Request.ResourceType }
                }
            }
        };

        await _auditService.LogAuditEventAsync(audit, cancellationToken);
    }

    private AuditEvent.AuditEventAction MapInteractionToAction(
        FhirInteractionType interaction)
    {
        return interaction switch
        {
            FhirInteractionType.Create => AuditEvent.AuditEventAction.C,
            FhirInteractionType.Read => AuditEvent.AuditEventAction.R,
            FhirInteractionType.Update => AuditEvent.AuditEventAction.U,
            FhirInteractionType.Delete => AuditEvent.AuditEventAction.D,
            _ => AuditEvent.AuditEventAction.E
        };
    }
}
```

### Notification Handler

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(CarePlan) })]
public class CarePlanNotificationHandler
{
    private readonly INotificationService _notificationService;
    private readonly IDataService<Patient> _patientDataService;

    [AsyncFhirHandler("SendNotification", HandlerCategory.PostInteraction)]
    public async Task SendNotificationAsync(
        IFhirContext context,
        CarePlan carePlan,
        CancellationToken cancellationToken)
    {
        // Only send notification for create operation
        if (context.Request.Interaction != FhirInteractionType.Create)
            return;

        // Get patient details
        var patient = await _patientDataService.GetAsync<Patient>(
            carePlan.Subject.Reference, cancellationToken);

        if (patient == null)
            return;

        var email = patient.Telecom?
            .FirstOrDefault(t => t.System == ContactPoint.ContactPointSystem.Email)
            ?.Value;

        if (string.IsNullOrEmpty(email))
            return;

        // Send enrollment confirmation
        await _notificationService.SendEmailAsync(
            to: email,
            subject: "Care Plan Enrollment Confirmation",
            body: $"You have been enrolled in care plan {carePlan.Id}",
            cancellationToken: cancellationToken);
    }
}
```

### Event Publishing Handler

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Patient) })]
public class PatientEventPublishingHandler
{
    private readonly IEventBus _eventBus;

    [AsyncFhirHandler("PublishEvent", HandlerCategory.PostInteraction)]
    public async Task PublishEventAsync(
        IFhirContext context,
        Patient patient,
        CancellationToken cancellationToken)
    {
        var eventType = context.Request.Interaction switch
        {
            FhirInteractionType.Create => "PatientCreated",
            FhirInteractionType.Update => "PatientUpdated",
            FhirInteractionType.Delete => "PatientDeleted",
            _ => null
        };

        if (eventType == null)
            return;

        var @event = new PatientEvent
        {
            EventType = eventType,
            PatientId = patient.Id,
            Timestamp = DateTimeOffset.UtcNow,
            CorrelationId = context.CorrelationId
        };

        await _eventBus.PublishAsync(@event, cancellationToken);
    }
}
```

## Multi-Category Handler Example

Handlers can implement multiple categories:

```csharp
[FhirHandlerClass(AcceptedTypes = new[] { nameof(Appointment) })]
public class AppointmentWorkflowHandler
{
    private readonly IDataService<Appointment> _dataService;
    private readonly IDataService<Slot> _slotDataService;
    private readonly INotificationService _notificationService;

    // PreCRUD: Validate slot availability
    [FhirHandler("ValidateSlot", HandlerCategory.PreCRUD,
        FhirInteractionType.Create)]
    public async Task ValidateSlotAsync(
        Appointment appointment,
        CancellationToken ct)
    {
        var slot = await _slotDataService.GetAsync<Slot>(
            appointment.Slot.First().Reference, ct);

        if (slot?.Status != Slot.SlotStatus.Free)
            throw new BusinessRuleException("Slot not available");
    }

    // PostCRUD: Update slot status
    [FhirHandler("UpdateSlot", HandlerCategory.PostCRUD,
        FhirInteractionType.Create)]
    public async Task UpdateSlotAsync(
        Appointment appointment,
        CancellationToken ct)
    {
        var slot = await _slotDataService.GetAsync<Slot>(
            appointment.Slot.First().Reference, ct);

        if (slot != null)
        {
            slot.Status = Slot.SlotStatus.Busy;
            await _slotDataService.UpsertAsync(slot, null, false, true, true, ct);
        }
    }

    // PostInteraction: Send confirmation
    [AsyncFhirHandler("SendConfirmation", HandlerCategory.PostInteraction)]
    public async Task SendConfirmationAsync(
        Appointment appointment,
        CancellationToken ct)
    {
        await _notificationService.SendAppointmentConfirmationAsync(
            appointment.Id, ct);
    }
}
```

## Configuration

```json
{
  "Handlers": {
    "FromClass": {
      "MyProject.Handlers.AuthenticationHandler": true,
      "MyProject.Handlers.PatientFormatValidationHandler": true,
      "MyProject.Handlers.CarePlanReferenceResolutionHandler": true,
      "MyProject.Handlers.AuditLoggingHandler": true
    }
  }
}
```

## Important Rules

### SetIsHandled Rule

**CRITICAL:** Only the LAST handler in the pipeline should call `SetIsHandled(true)`.

```csharp
// ❌ WRONG - PreCRUD handler calls SetIsHandled
[FhirHandler("Validate", HandlerCategory.PreCRUD, FhirInteractionType.Create)]
public Task ValidateAsync(Patient patient, CancellationToken ct)
{
    // Validation logic
    context.Response.SetIsHandled(true);  // ❌ Stops pipeline!
    return Task.CompletedTask;
}

// ✅ CORRECT - PreCRUD handler doesn't call SetIsHandled
[FhirHandler("Validate", HandlerCategory.PreCRUD, FhirInteractionType.Create)]
public Task ValidateAsync(Patient patient, CancellationToken ct)
{
    // Validation logic
    return Task.CompletedTask;  // ✅ Pipeline continues
}

// ✅ CORRECT - CRUD handler returns resource (framework calls SetIsHandled)
[FhirHandler(FhirInteractionType.Create)]
public async Task<Patient> CreateAsync(Patient patient, CancellationToken ct)
{
    var result = await _dataService.UpsertAsync(patient, null, true, true, false, ct);
    return (Patient)result.Resource;  // ✅ Framework handles response
}
```

### Async Handler Attribute

Use `[AsyncFhirHandler]` for PostInteraction handlers that may fail:

```csharp
// ✅ CORRECT - PostInteraction uses AsyncFhirHandler
[AsyncFhirHandler("SendEmail", HandlerCategory.PostInteraction)]
public async Task SendEmailAsync(Patient patient, CancellationToken ct)
{
    await _emailService.SendAsync(patient.GetEmail(), ct);
    // If this fails, it won't affect the main operation
}

// ❌ WRONG - Regular FhirHandler in PostInteraction
[FhirHandler("SendEmail", HandlerCategory.PostInteraction)]
public async Task SendEmailAsync(Patient patient, CancellationToken ct)
{
    await _emailService.SendAsync(patient.GetEmail(), ct);
    // If this fails, entire operation fails
}
```
