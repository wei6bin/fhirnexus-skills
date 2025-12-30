---
name: fhir-custom-datastore
description: Generates custom data stores with relational models, data mappers, and search services for FHIR Engine. Use when mapping FHIR resources to relational database tables, creating custom search services, or building data persistence layers.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# FHIR Custom Data Store Generator

This skill generates complete data store implementations for mapping FHIR resources to relational databases.

## What This Skill Generates

When you ask me to create a custom data store, I'll generate:

1. **Data Model** - Entity classes for database tables
2. **Data Mapper** - Bidirectional FHIR ↔ Database mapping
3. **Search Service** - FHIR search parameter implementation
4. **Configuration** - fhirengine.json setup
5. **DbContext** - Entity Framework configuration

## When to Use Custom Data Stores

### Use Custom Data Stores When:
- ✅ Need relational database tables (normalized data)
- ✅ Complex search requirements
- ✅ Existing database schema to integrate with
- ✅ Custom business logic in data layer
- ✅ Performance optimization with indexes
- ✅ Integration with legacy systems

### Use Document Store Instead When:
- ✅ Simple CRUD operations sufficient
- ✅ No complex search requirements
- ✅ Prefer JSON storage
- ✅ Quick prototyping

## Quick Start

**Example request:**
```
"Create a custom data store for Appointment resource with properties:
- id, status, description
- start, end times
- patient reference, practitioner reference
- specialty (coded concept)
- support searching by patient, date, and specialty"
```

I'll generate complete boilerplate code following FHIR Engine patterns.

## Data Model Generation

### Entity Class Pattern

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Hl7.Fhir.Introspection;
using Ihis.FhirEngine.Data.Models;
using Microsoft.EntityFrameworkCore;

namespace MyProject.Data;

[FhirType("Appointment", IsResource = true)]
[PrimaryKey(nameof(Id), nameof(VersionId))]
public class AppointmentModel : IResourceEntity<Guid>, IAuditedEntity
{
    // Primary Key
    public Guid Id { get; set; }
    public int? VersionId { get; set; }

    // Resource-specific properties
    public string? Status { get; set; }

    [MaxLength(500)]
    public string? Description { get; set; }

    public DateTimeOffset? Start { get; set; }
    public DateTimeOffset? End { get; set; }

    public string? Patient { get; set; }  // Reference as string
    public string? Practitioner { get; set; }

    // CodeableConcept - store BOTH code AND display
    public string? SpecialtyCode { get; set; }
    public string? SpecialtyDisplay { get; set; }

    // Standard audit properties (ALWAYS include)
    public byte[]? TimeStamp { get; set; }
    public string? CreatedBy { get; set; }
    public DateTimeOffset? CreationDateTime { get; set; }
    public string? ModifiedBy { get; set; }

    [Column(nameof(ModificationDateTime))]
    public DateTimeOffset? LastUpdated { get; set; }

    [NotMapped]
    public DateTimeOffset? ModificationDateTime
    {
        get => LastUpdated;
        set => LastUpdated = value;
    }

    [Column(nameof(IsDeleted))]
    public bool IsHistory { get; set; }

    [NotMapped]
    public bool IsDeleted
    {
        get => IsHistory;
        set => IsHistory = value;
    }
}
```

### Id Type Selection

**CRITICAL:** Choose Id type based on source system:

| Source System Id Type | Entity Id Type | Attribute Needed |
|:----------------------|:---------------|:-----------------|
| **GUID/UUID** | `Guid` | None (client-generated) |
| **Integer** | `int` | `[DatabaseGenerated(DatabaseGeneratedOption.Identity)]` |
| **Long** | `long` | `[DatabaseGenerated(DatabaseGeneratedOption.Identity)]` |

**Example with int Id:**
```csharp
public class AppointmentModel : IResourceEntity<int>, IAuditedEntity
{
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }
    public int? VersionId { get; set; }
    // ...
}
```

## FHIR Type Mappings

| FHIR Type | C# Type | Example |
|:----------|:--------|:--------|
| `code`, `string`, `uri` | `string?` | `public string? Status { get; set; }` |
| `boolean` | `bool?` | `public bool? Active { get; set; }` |
| `integer` | `int?` | `public int? Count { get; set; }` |
| `decimal` | `decimal?` | `public decimal? Price { get; set; }` |
| `dateTime`, `instant` | `DateTimeOffset?` | `public DateTimeOffset? Start { get; set; }` |
| `date` | `DateTimeOffset?` | `public DateTimeOffset? BirthDate { get; set; }` |
| `Reference` | `string?` | `public string? Patient { get; set; }` (store as "Patient/123") |
| `CodeableConcept` (single) | Two `string?` properties | Code + Display |
| `Identifier` | `string?` | `public string? Identifier { get; set; }` |

### CodeableConcept Pattern

**CRITICAL:** CodeableConcept requires BOTH code AND display:

```csharp
// CodeableConcept mapping
public string? SpecialtyCode { get; set; }      // Stores coding[0].code
public string? SpecialtyDisplay { get; set; }   // Stores coding[0].display

// In mapper:
// FHIR → Model
model.SpecialtyCode = resource.Specialty?.Coding?.FirstOrDefault()?.Code;
model.SpecialtyDisplay = resource.Specialty?.Coding?.FirstOrDefault()?.Display;

// Model → FHIR
resource.Specialty = new CodeableConcept
{
    Coding = new List<Coding>
    {
        new()
        {
            Code = model.SpecialtyCode,
            Display = model.SpecialtyDisplay
        }
    }
};
```

## Complex Types and Backbone Elements

For repeating elements (0..* cardinality), create separate entity classes:

### Child Entity Pattern

```csharp
[Owned]
public class AppointmentParticipantEntity
{
    public string? ActorReference { get; set; }
    public string? ActorDisplay { get; set; }
    public string? Status { get; set; }
    public bool? Required { get; set; }
}
```

### Parent with Navigation Property

```csharp
[FhirType("Appointment", IsResource = true)]
public class AppointmentModel : IResourceEntity<Guid>, IAuditedEntity
{
    public Guid Id { get; set; }
    public int? VersionId { get; set; }

    // Navigation property for child entities
    public List<AppointmentParticipantEntity> Participants { get; set; } = new();

    // Standard audit properties...
}
```

## Data Mapper Generation

### Mapper Pattern

```csharp
using Hl7.Fhir.Model;
using Ihis.FhirEngine.Core.Handlers.Data;
using Ihis.FhirEngine.Core.Utility;

namespace MyProject.Data;

public sealed class AppointmentDataMapper
    : IFhirDataMapper<AppointmentModel, Appointment>
{
    // Model → FHIR Resource
    public Appointment Map(AppointmentModel data)
    {
        var appointment = new Appointment
        {
            Id = data.Id.ToString(),
            Status = EnumHelper.ParseLiteral<Appointment.AppointmentStatus>(data.Status),
            Description = data.Description,
            Start = data.Start,
            End = data.End
        };

        // Map references
        if (data.Patient != null)
        {
            appointment.Participant.Add(new Appointment.ParticipantComponent
            {
                Actor = new ResourceReference(data.Patient),
                Status = Appointment.ParticipationStatus.Accepted
            });
        }

        // Map CodeableConcept (BOTH code and display)
        if (data.SpecialtyCode != null || data.SpecialtyDisplay != null)
        {
            appointment.Specialty = new List<CodeableConcept>
            {
                new()
                {
                    Coding = new List<Coding>
                    {
                        new()
                        {
                            Code = data.SpecialtyCode,
                            Display = data.SpecialtyDisplay
                        }
                    }
                }
            };
        }

        return appointment;
    }

    // FHIR Resource → Model
    public AppointmentModel ReverseMap(Appointment resource)
    {
        var model = new AppointmentModel
        {
            Id = Guid.Parse(resource.Id),
            Status = EnumHelper.GetLiteral(resource.Status),
            Description = resource.Description,
            Start = resource.Start,
            End = resource.End
        };

        // Extract patient reference
        model.Patient = resource.Participant?
            .FirstOrDefault(p => p.Actor?.Reference?.StartsWith("Patient/") == true)
            ?.Actor?.Reference;

        model.Practitioner = resource.Participant?
            .FirstOrDefault(p => p.Actor?.Reference?.StartsWith("Practitioner/") == true)
            ?.Actor?.Reference;

        // Extract CodeableConcept (BOTH code and display)
        var specialty = resource.Specialty?.FirstOrDefault();
        if (specialty != null)
        {
            var coding = specialty.Coding?.FirstOrDefault();
            model.SpecialtyCode = coding?.Code;
            model.SpecialtyDisplay = coding?.Display;
        }

        return model;
    }
}
```

### Mapper with Child Entities

```csharp
public Appointment Map(AppointmentModel data)
{
    var appointment = new Appointment { /* ... */ };

    // Map child entities to FHIR complex types
    appointment.Participant = data.Participants?.Select(p =>
        new Appointment.ParticipantComponent
        {
            Actor = new ResourceReference(p.ActorReference)
            {
                Display = p.ActorDisplay
            },
            Status = EnumHelper.ParseLiteral<Appointment.ParticipationStatus>(p.Status),
            Required = p.Required.HasValue
                ? EnumHelper.ParseLiteral<Appointment.ParticipantRequired>(p.Required.Value.ToString())
                : null
        }).ToList();

    return appointment;
}

public AppointmentModel ReverseMap(Appointment resource)
{
    var model = new AppointmentModel { /* ... */ };

    // Map FHIR complex types to child entities
    model.Participants = resource.Participant?.Select(p =>
        new AppointmentParticipantEntity
        {
            ActorReference = p.Actor?.Reference,
            ActorDisplay = p.Actor?.Display,
            Status = EnumHelper.GetLiteral(p.Status),
            Required = p.Required.HasValue
        }).ToList() ?? new();

    return model;
}
```

## Search Service Generation

### Search Service Pattern

```csharp
using Ihis.FhirEngine.Core;
using Ihis.FhirEngine.Core.Extensions;
using Ihis.FhirEngine.Core.Handlers.Data;
using Ihis.FhirEngine.Core.Search;
using Ihis.FhirEngine.Data.Relational.Search;

namespace MyProject.Data;

public record class FhirModelSearchService(
    FhirModelDbContext Context,
    IFhirDataMapperFactory DataMapperFactory,
    ILogger<FhirModelSearchService> Logger)
    : IContextRelationalSearchService<FhirModelSearchService, FhirModelDbContext>
{
    public static FhirRelationalQueryBuilder<FhirModelDbContext> CreateRelationalQueryBuilder(
        FhirRelationalQueryBuilder<FhirModelDbContext> queryBuilder)
        => queryBuilder
            .AddResource(
                ctx => ctx.Appointments,
                apt => apt
                    // Token search - exact match
                    .AddSearchParam("_tag", static (query, args) =>
                        query.WhereAny(args, str => x => x.Tag == str))

                    // Reference search - exact match
                    .AddSearchParam("patient", static (query, args) =>
                        query.WhereAny(args, str => x => x.Patient == str))

                    // Composite reference search (actor = patient OR practitioner)
                    .AddSearchParam("actor", static (query, args) =>
                        query.WhereAny(args, str => x =>
                            x.Patient == str || x.Practitioner == str))

                    // Date range search
                    .AddSearchParam("date", static (query, args) =>
                        query.WherePartialDateTimeMatch(args, x => x.Start, x => x.End))

                    // String search - exact match or contains
                    .AddSearchParam("specialty", static (query, args) =>
                        query.WhereAny(args, str => x => x.SpecialtyCode == str))

                    // Status token search
                    .AddSearchParam("status", static (query, args) =>
                        query.WhereAny(args, str => x => x.Status == str)));
}
```

### Available Query Methods

| Method | Use For | Example |
|:-------|:--------|:--------|
| `WhereAny(args, str => x => x.Property == str)` | Token, Reference, String exact match | Patient, Status, Code |
| `WherePartialDateTimeMatch(args, x => x.Start, x => x.End)` | Date range queries | Appointment date |
| Standard LINQ | Complex queries | Custom business logic |

## DbContext Configuration

### Add DbSet Properties

```csharp
using Microsoft.EntityFrameworkCore;

namespace MyProject.Data;

public class FhirModelDbContext : DbContext
{
    public FhirModelDbContext(DbContextOptions<FhirModelDbContext> options)
        : base(options)
    {
    }

    // Add DbSet for your resource model
    public DbSet<AppointmentModel> Appointments => Set<AppointmentModel>();

    // If using child entities, add DbSets for them too
    public DbSet<AppointmentParticipantEntity> AppointmentParticipants => Set<AppointmentParticipantEntity>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure relationships if needed
        modelBuilder.Entity<AppointmentModel>()
            .HasMany(a => a.Participants)
            .WithOne()
            .OnDelete(DeleteBehavior.Cascade);

        // Add indexes for search performance
        modelBuilder.Entity<AppointmentModel>()
            .HasIndex(a => a.Patient);

        modelBuilder.Entity<AppointmentModel>()
            .HasIndex(a => a.Start);

        modelBuilder.Entity<AppointmentModel>()
            .HasIndex(a => a.SpecialtyCode);
    }
}
```

## Configuration (fhirengine.json)

```json
{
  "Handlers": {
    "Repository": {
      "FhirDataStore<@Custom>": {
        "ContextType": "MyProject.Data.FhirModelDbContext",
        "UseSqlRelationalModels": {
          "SearchServiceType": "MyProject.Data.FhirModelSearchService"
        },
        "UseDataMapper": [
          "MyProject.Data.AppointmentDataMapper"
        ],
        "ConnectionString": "data",
        "AllowedInteractions": [
          "Create",
          "Read",
          "Vread",
          "Update",
          "Delete",
          "SearchType",
          "OperationType",
          "OperationInstance"
        ],
        "AcceptedTypes": [
          "Appointment"
        ]
      }
    }
  }
}
```

### Configuration Elements

- **ContextType**: Fully qualified DbContext class name
- **SearchServiceType**: Fully qualified search service class name
- **UseDataMapper**: Array of fully qualified mapper class names
- **AcceptedTypes**: FHIR resource type names
- **ConnectionString**: Key from appsettings.json

## Database Migration

### Create Migration

```bash
# Add migration
dotnet ef migrations add AddAppointment --context FhirModelDbContext

# Update database
dotnet ef database update --context FhirModelDbContext
```

### Connection String (appsettings.json)

```json
{
  "ConnectionStrings": {
    "data": "Server=localhost;Database=FhirDb;Trusted_Connection=True;TrustServerCertificate=True"
  }
}
```

## Complete Example

**Request:**
```
"Create custom data store for Patient resource with:
- id (GUID), identifier, name, gender, birthDate
- Support searching by identifier, name, and birthDate"
```

**I'll generate:**

1. **PatientModel.cs** - Entity with all properties
2. **PatientDataMapper.cs** - Bidirectional mapping
3. **FhirModelSearchService.cs** - Search implementation
4. **DbContext updates** - Add DbSet<PatientModel>
5. **fhirengine.json** - Configuration entries

## Data Annotations for Validation

```csharp
using System.ComponentModel.DataAnnotations;

public class AppointmentModel : IResourceEntity<Guid>, IAuditedEntity
{
    public Guid Id { get; set; }

    [Required]
    [MaxLength(50)]
    public string? Status { get; set; }

    [MaxLength(500)]
    public string? Description { get; set; }

    [Range(typeof(DateTimeOffset), "2020-01-01", "2099-12-31")]
    public DateTimeOffset? Start { get; set; }

    [Index]  // Add database index
    public string? Patient { get; set; }

    // Standard audit properties...
}
```

## Common Patterns

### Pattern: Simple Flat Table

**Use when:** Resource has few properties, no complex types

```csharp
public class ObservationModel : IResourceEntity<Guid>, IAuditedEntity
{
    public Guid Id { get; set; }
    public int? VersionId { get; set; }

    public string? Status { get; set; }
    public string? Code { get; set; }
    public string? CodeDisplay { get; set; }
    public decimal? ValueQuantity { get; set; }
    public string? ValueUnit { get; set; }
    public string? Subject { get; set; }
    public DateTimeOffset? EffectiveDateTime { get; set; }

    // Audit properties...
}
```

### Pattern: With Child Entities

**Use when:** Resource has repeating elements (0..* cardinality)

```csharp
// Parent
public class PatientModel : IResourceEntity<Guid>, IAuditedEntity
{
    public Guid Id { get; set; }
    public string? Gender { get; set; }
    public DateTimeOffset? BirthDate { get; set; }

    public List<PatientNameEntity> Names { get; set; } = new();
    public List<PatientAddressEntity> Addresses { get; set; } = new();

    // Audit properties...
}

// Child entities
[Owned]
public class PatientNameEntity
{
    public string? Use { get; set; }
    public string? Family { get; set; }
    public string? Given { get; set; }
}
```

## Validation Checklist

Before completing data store generation:

- ✅ Data model inherits from `IResourceEntity<T>` and `IAuditedEntity`
- ✅ `[FhirType]` and `[PrimaryKey]` attributes present
- ✅ Standard audit properties included
- ✅ CodeableConcept mapped to BOTH code AND display
- ✅ Mapper implements `IFhirDataMapper<TModel, TResource>`
- ✅ Search service implements `IContextRelationalSearchService`
- ✅ DbSet added to DbContext
- ✅ Configuration updated in fhirengine.json
- ✅ Connection string in appsettings.json

## What to Tell Me

When requesting data store generation:

1. **Resource Type**: "Create data store for Appointment"
2. **Properties**: List the fields needed
3. **Search Parameters**: Which fields should be searchable
4. **Id Type**: GUID, int, or long (default: GUID)
5. **Child Entities**: Any repeating elements

**Example:**
```
"Create custom data store for Appointment resource with:
- id (GUID), status, description, start time, end time
- patient reference, practitioner reference
- specialty (CodeableConcept)
- participants as child entities with actor and status
- Support searching by patient, date, specialty, and status"
```

## Related Skills

- **Custom resource creation?** → Use `fhir-custom-resource` skill
- **Handler implementation?** → Use `fhir-handler-generator` skill
- **Configuration issues?** → Use `fhir-config-troubleshooting` skill
