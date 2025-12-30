# Handler Category Selection Decision Matrix

This guide helps you choose the correct `HandlerCategory` for your FHIR Engine handler.

## Quick Decision Flow

### Step-by-Step Category Selection

**1. Does the logic need database/external service access?**
- **NO** → Consider **PreInteraction**
  - Format validation
  - Authentication/authorization
  - Request sanitization
- **YES** → Continue to step 2

**2. Is this the main business operation (Create/Read/Update/Delete)?**
- **YES** → Use **CRUD** category
- **NO** → Continue to step 3

**3. Should it execute before or after the main operation?**
- **BEFORE** → Use **PreCRUD**
  - Existence checks
  - Reference resolution
  - Duplicate prevention
- **AFTER** → Continue to step 4

**4. Must it complete within the same database transaction?**
- **YES** → Use **PostCRUD**
  - Related updates
  - Cascade operations
  - Cache invalidation
- **NO** → Use **PostInteraction**
  - Notifications
  - Audit logging
  - External sync

## Category Comparison Matrix

| Question | PreInteraction | PreCRUD | CRUD | PostCRUD | PostInteraction |
|:---------|:--------------:|:-------:|:----:|:--------:|:---------------:|
| **Needs database access?** | ❌ | ✅ | ✅ | ✅ | ✅ Optional |
| **Runs within transaction?** | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Can fail main operation?** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Validation/Authorization?** | ✅ Format/Auth | ✅ Business | ❌ | ❌ | ❌ |
| **Modifies main resource?** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Calls external services?** | ⚠️ Fast only | ⚠️ Fast only | ✅ | ⚠️ Fast only | ✅ |
| **Blocks user response?** | ✅ | ✅ | ✅ | ✅ | ❌ |

## Detailed Category Guides

### PreInteraction - Early Validation

**Purpose:** Early-stage validation without accessing external systems
**Transaction:** Outside transaction
**Performance:** Fast, lightweight only

**Use For:**
- ✅ Input format validation (NRIC, dates, required fields)
- ✅ Authentication & authorization (JWT, API keys, roles)
- ✅ Request sanitization (XSS prevention, normalization)
- ✅ Data-independent business rules
- ✅ Rate limiting & throttling
- ✅ Request logging initiation
- ✅ Content negotiation

**Example Scenarios:**
```csharp
// NRIC format validation (no database lookup)
[FhirHandler("ValidateNricFormat", HandlerCategory.PreInteraction,
    FhirInteractionType.Create)]
public Task ValidateNricFormatAsync(Patient patient, CancellationToken ct)
{
    var nric = patient.GetNric();
    if (!NricValidator.TryValidate(nric))
        throw new ResourceNotValidException($"Invalid NRIC format: {nric}");
    return Task.CompletedTask;
}

// JWT authentication
[FhirHandler("Authenticate", HandlerCategory.PreInteraction)]
public Task AuthenticateAsync(IFhirContext context, CancellationToken ct)
{
    var token = context.Request.Headers.Authorization;
    if (!_authService.ValidateToken(token))
        throw new UnauthorizedFhirActionException("Invalid token");
    return Task.CompletedTask;
}
```

### PreCRUD - Business Validation & Enrichment

**Purpose:** Complex validation requiring data lookups and payload enrichment
**Transaction:** Within database transaction
**Performance:** May involve database queries

**Use For:**
- ✅ Resource existence validation
- ✅ Reference resolution (identifier → resource reference)
- ✅ Duplicate prevention checks
- ✅ Cross-resource validation
- ✅ Payload enrichment from database
- ✅ Data transformation before save
- ✅ Constraint validation requiring data

**Example Scenarios:**
```csharp
// Patient existence check and reference resolution
[FhirHandler("ResolvePatientReference", HandlerCategory.PreCRUD,
    FhirInteractionType.Create)]
public async Task ResolvePatientAsync(
    CarePlan carePlan,
    CancellationToken ct)
{
    var nric = carePlan.Subject.Identifier.Value;
    var patient = await _searchService.SearchAsync<Patient>(
        $"identifier={nric}", ct);

    if (!patient.Entry.Any())
        throw new ResourceNotFoundException($"Patient {nric} not found");

    carePlan.Subject.Reference = $"Patient/{patient.Entry.First().Resource.Id}";
}

// Duplicate enrollment prevention
[FhirHandler("PreventDuplicate", HandlerCategory.PreCRUD,
    FhirInteractionType.Create)]
public async Task PreventDuplicateAsync(
    CarePlan carePlan,
    CancellationToken ct)
{
    var existing = await _searchService.SearchAsync<CarePlan>(
        $"patient={carePlan.Subject.Reference}&status=active", ct);

    if (existing.Entry.Any())
        throw new BusinessRuleException("Patient already enrolled");
}
```

### CRUD - Main Data Operations

**Purpose:** Primary data operations and core business logic
**Transaction:** Within database transaction
**Performance:** Main processing operation

**Use For:**
- ✅ Resource persistence (Create/Read/Update/Delete)
- ✅ External service integration
- ✅ Complex search operations
- ✅ Business logic execution
- ✅ Batch operations
- ✅ File processing
- ✅ Calculation operations

**Example Scenarios:**
```csharp
// Main enrollment creation
[FhirHandler(FhirInteractionType.Create)]
public async Task<CarePlan> CreateEnrollmentAsync(
    CarePlan carePlan,
    CancellationToken ct)
{
    // Remove sensitive data before persistence
    carePlan.Subject.Identifier = null;

    var result = await _dataService.UpsertAsync(
        carePlan, null, true, true, false, ct);
    return (CarePlan)result.Resource;
}

// Complex search with business logic
[FhirHandler(FhirInteractionType.SearchType)]
public async IAsyncEnumerable<Patient> SearchActivePatients(
    IFhirContext context,
    [EnumeratorCancellation] CancellationToken ct)
{
    var searchParams = context.Request.SearchParams;
    var results = await _searchService.SearchAsync<Patient>(
        searchParams, ct);

    foreach (var entry in results.Entry)
    {
        var patient = entry.Resource.ToResource<Patient>();
        if (IsActive(patient))  // Business logic filter
            yield return patient;
    }
}
```

### PostCRUD - Related Updates Within Transaction

**Purpose:** Related operations within same transaction
**Transaction:** Within same database transaction as CRUD
**Performance:** Should complete quickly

**Use For:**
- ✅ Related resource updates
- ✅ Cascade operations
- ✅ Index updates
- ✅ Cache invalidation (within transaction)
- ✅ Internal state synchronization
- ✅ Transaction-scoped cleanup
- ✅ Immediate validation

**Example Scenarios:**
```csharp
// Update appointment slots after booking
[FhirHandler("UpdateSlots", HandlerCategory.PostCRUD,
    FhirInteractionType.Create)]
public async Task UpdateSlotsAsync(
    Appointment appointment,
    CancellationToken ct)
{
    var slot = await _dataService.GetAsync<Slot>(
        appointment.Slot.First().Reference, ct);
    slot.Status = Slot.SlotStatus.Busy;
    await _dataService.UpsertAsync(slot, null, false, true, true, ct);
}

// Update patient counter
[FhirHandler("UpdateCounter", HandlerCategory.PostCRUD,
    FhirInteractionType.Create)]
public async Task UpdateCounterAsync(
    Patient patient,
    CancellationToken ct)
{
    var org = await _dataService.GetAsync<Organization>(
        patient.ManagingOrganization.Reference, ct);
    org.Extension.Add(new Extension(
        "patientCount",
        new Integer(GetPatientCount(org) + 1)));
    await _dataService.UpsertAsync(org, null, false, true, true, ct);
}
```

### PostInteraction - External Notifications

**Purpose:** External notifications after transaction completion
**Transaction:** Outside database transaction
**Performance:** Can be slower, may use background processing

**Use For:**
- ✅ External notifications (email, SMS, webhooks)
- ✅ Event publishing (message queues, streaming)
- ✅ Audit & compliance logging
- ✅ Analytics & telemetry
- ✅ External system synchronization
- ✅ Background job scheduling
- ✅ Distributed cache updates

**Example Scenarios:**
```csharp
// Send enrollment confirmation email
[AsyncFhirHandler("SendNotification", HandlerCategory.PostInteraction)]
public async Task SendNotificationAsync(
    IFhirContext context,
    CarePlan carePlan,
    CancellationToken ct)
{
    var patient = await _dataService.GetAsync<Patient>(
        carePlan.Subject.Reference, ct);
    await _emailService.SendEnrollmentConfirmation(
        patient.GetContactEmail(), carePlan.Id);
    await _auditService.LogEnrollmentCreated(
        carePlan.Id, context.Request.RequestId);
}

// Publish to event bus
[AsyncFhirHandler("PublishEvent", HandlerCategory.PostInteraction)]
public async Task PublishEventAsync(
    IFhirContext context,
    Patient patient,
    CancellationToken ct)
{
    await _eventBus.PublishAsync(new PatientCreatedEvent
    {
        PatientId = patient.Id,
        Timestamp = DateTimeOffset.UtcNow
    }, ct);
}
```

## Decision Tree Diagram

```
┌─────────────────────────────────────┐
│  Need external notifications/audit? │
└────────────┬────────────────────────┘
             │ YES
             v
    ┌────────────────┐
    │ PostInteraction│
    └────────────────┘

             │ NO
             v
┌─────────────────────────────────────────┐
│ Update related resources after main op? │
└────────────┬────────────────────────────┘
             │ YES
             v
        ┌──────────┐
        │ PostCRUD │
        └──────────┘

             │ NO
             v
┌──────────────────────────────────────────┐
│ Main data operation (Create/Read/etc.)?  │
└────────────┬─────────────────────────────┘
             │ YES
             v
          ┌──────┐
          │ CRUD │
          └──────┘

             │ NO
             v
┌─────────────────────────────────────────┐
│ Need database lookup for validation?    │
└────────────┬────────────────────────────┘
             │ YES
             v
         ┌─────────┐
         │ PreCRUD │
         └─────────┘

             │ NO
             v
    ┌────────────────┐
    │ PreInteraction │
    └────────────────┘
```

## Common Use Case Examples

### Scenario: Create Patient with Validation

**Requirements:**
1. Validate NRIC format
2. Check if patient already exists
3. Save patient to database
4. Send welcome email

**Handler Breakdown:**
```csharp
// 1. PreInteraction - Format validation (no DB access)
[FhirHandler("ValidateFormat", HandlerCategory.PreInteraction,
    FhirInteractionType.Create)]
public Task ValidateFormatAsync(Patient patient, CancellationToken ct)
{
    if (!NricValidator.TryValidate(patient.GetNric()))
        throw new ResourceNotValidException("Invalid NRIC format");
    return Task.CompletedTask;
}

// 2. PreCRUD - Duplicate check (needs DB access)
[FhirHandler("CheckDuplicate", HandlerCategory.PreCRUD,
    FhirInteractionType.Create)]
public async Task CheckDuplicateAsync(Patient patient, CancellationToken ct)
{
    var existing = await _searchService.SearchAsync<Patient>(
        $"identifier={patient.GetNric()}", ct);
    if (existing.Entry.Any())
        throw new BusinessRuleException("Patient already exists");
}

// 3. CRUD - Main operation
[FhirHandler(FhirInteractionType.Create)]
public async Task<Patient> CreateAsync(Patient patient, CancellationToken ct)
{
    var result = await _dataService.UpsertAsync(
        patient, null, true, true, false, ct);
    return (Patient)result.Resource;
}

// 4. PostInteraction - Welcome email (outside transaction)
[AsyncFhirHandler("SendWelcome", HandlerCategory.PostInteraction)]
public async Task SendWelcomeAsync(Patient patient, CancellationToken ct)
{
    await _emailService.SendWelcomeEmail(patient.GetContactEmail());
}
```

### Scenario: Book Appointment

**Requirements:**
1. Validate patient and practitioner exist
2. Create appointment
3. Update slot status to busy
4. Send confirmation SMS

**Handler Breakdown:**
```csharp
// 1. PreCRUD - Validate references exist
[FhirHandler("ValidateReferences", HandlerCategory.PreCRUD,
    FhirInteractionType.Create)]
public async Task ValidateReferencesAsync(
    Appointment appointment,
    CancellationToken ct)
{
    var patient = await _dataService.GetAsync<Patient>(
        appointment.Participant.First().Actor.Reference, ct);
    if (patient == null)
        throw new ResourceNotFoundException("Patient not found");

    // Similar check for practitioner...
}

// 2. CRUD - Create appointment
[FhirHandler(FhirInteractionType.Create)]
public async Task<Appointment> CreateAsync(
    Appointment appointment,
    CancellationToken ct)
{
    var result = await _dataService.UpsertAsync(
        appointment, null, true, true, false, ct);
    return (Appointment)result.Resource;
}

// 3. PostCRUD - Update slot (same transaction)
[FhirHandler("UpdateSlot", HandlerCategory.PostCRUD,
    FhirInteractionType.Create)]
public async Task UpdateSlotAsync(Appointment appointment, CancellationToken ct)
{
    var slot = await _dataService.GetAsync<Slot>(
        appointment.Slot.First().Reference, ct);
    slot.Status = Slot.SlotStatus.Busy;
    await _dataService.UpsertAsync(slot, null, false, true, true, ct);
}

// 4. PostInteraction - Send SMS (outside transaction)
[AsyncFhirHandler("SendSMS", HandlerCategory.PostInteraction)]
public async Task SendSMSAsync(Appointment appointment, CancellationToken ct)
{
    await _smsService.SendConfirmation(
        appointment.Participant.First().Actor.Reference);
}
```

## Quick Category Hints

**"Can I validate this without database access?"** → **PreInteraction**

**"Do I need to check/enrich data from database before saving?"** → **PreCRUD**

**"Is this the main Create/Read/Update/Delete operation?"** → **CRUD**

**"Do I need to update related data within the same transaction?"** → **PostCRUD**

**"Should I notify external systems or log after completion?"** → **PostInteraction**
