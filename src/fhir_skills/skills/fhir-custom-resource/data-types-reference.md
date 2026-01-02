# Supported Data Types Reference

Complete reference for FHIR Engine custom resource data types.

## Primitive Types

| Entity Data Type | FHIR Type | Cardinality | Description | Example Usage |
|:-----------------|:----------|:------------|:------------|:--------------|
| `bool?` | `boolean` | 0..1 | Boolean values | `public bool? Active { get; set; }` |
| `string?` | `string` | 0..1 | String values | `public string? Description { get; set; }` |
| `int?` | `integer` | 0..1 | Integer values | `public int? Count { get; set; }` |
| `decimal?` | `decimal` | 0..1 | Decimal values | `public decimal? Price { get; set; }` |

## Date/Time Types

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `DateEntity` | `date` | Date values (YYYY-MM-DD) | `public DateEntity? BirthDate { get; set; }` |
| `DateTimeEntity` | `dateTime` | DateTime with timezone | `public DateTimeEntity CreatedDate { get; set; }` |

**Usage in JSON:**
```json
{
  "birthDate": "1990-01-15",
  "createdDate": "2024-01-15T14:30:00+08:00"
}
```

## Identifier Types

| Entity Data Type | FHIR Type | Cardinality | Example |
|:-----------------|:----------|:------------|:--------|
| `IdentifierEntity` | `Identifier` | 0..1 | `public IdentifierEntity PatientId { get; set; }` |
| `List<IdentifierEntity>` | `Identifier` | 0..* | `public List<IdentifierEntity> Identifiers { get; set; } = new();` |

**JSON Structure:**
```json
{
  "identifier": [{
    "system": "https://hospital.org/patient-id",
    "value": "12345",
    "use": "official"
  }]
}
```

## Reference Types

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `ResourceReferenceEntity` | `Reference` | Single resource reference | `public ResourceReferenceEntity? Patient { get; set; }` |
| `List<ResourceReferenceEntity>` | `Reference` | Multiple references | `public List<ResourceReferenceEntity> Subjects { get; set; } = new();` |

**JSON Structure:**
```json
{
  "patient": {
    "reference": "Patient/123",
    "display": "John Doe"
  }
}
```

## CodeableConcept Types

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `CodeableConceptEntity` | `CodeableConcept` | Coded concepts | `public CodeableConceptEntity Type { get; set; }` |
| `List<CodeableConceptEntity>` | `CodeableConcept` | Multiple coded concepts | `public List<CodeableConceptEntity> Categories { get; set; } = new();` |

**JSON Structure:**
```json
{
  "type": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "386661006",
      "display": "Fever"
    }],
    "text": "Fever"
  }
}
```

## CodeableReference (R5 Only)

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `CodeableReferenceEntity` | `CodeableReference` | R5: Coded concept + reference | `public CodeableReferenceEntity Manifestation { get; set; }` |

**JSON Structure (R5):**
```json
{
  "manifestation": {
    "concept": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "271807003",
        "display": "Rash"
      }]
    },
    "reference": {
      "reference": "Observation/rash-001"
    }
  }
}
```

**⚠️ R4B Uses CodeableConceptEntity:**
```csharp
// R5
public CodeableReferenceEntity Manifestation { get; set; }

// R4B
public CodeableConceptEntity Manifestation { get; set; }
```

## Quantity Types

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `QuantityEntity` | `Quantity` | Numeric value with unit | `public QuantityEntity Weight { get; set; }` |
| `List<QuantityEntity>` | `Quantity` | Multiple quantities | `public List<QuantityEntity> Measurements { get; set; } = new();` |

**JSON Structure:**
```json
{
  "weight": {
    "value": 75.5,
    "unit": "kg",
    "system": "http://unitsofmeasure.org",
    "code": "kg"
  }
}
```

## Period Type

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `PeriodEntity` | `Period` | Time period with start/end | `public PeriodEntity ValidPeriod { get; set; }` |

**JSON Structure:**
```json
{
  "validPeriod": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  }
}
```

## Address Type

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `AddressEntity` | `Address` | Postal address | `public AddressEntity HomeAddress { get; set; }` |
| `List<AddressEntity>` | `Address` | Multiple addresses | `public List<AddressEntity> Addresses { get; set; } = new();` |

**JSON Structure:**
```json
{
  "homeAddress": {
    "use": "home",
    "type": "physical",
    "line": ["123 Main Street", "Apt 4B"],
    "city": "Singapore",
    "postalCode": "123456",
    "country": "SG"
  }
}
```

## ContactPoint Type

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `ContactPointEntity` | `ContactPoint` | Contact information | `public ContactPointEntity Phone { get; set; }` |
| `List<ContactPointEntity>` | `ContactPoint` | Multiple contact points | `public List<ContactPointEntity> Telecoms { get; set; } = new();` |

**JSON Structure:**
```json
{
  "phone": {
    "system": "phone",
    "value": "+65-6123-4567",
    "use": "work"
  }
}
```

## HumanName Type

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `HumanNameEntity` | `HumanName` | Person name | `public HumanNameEntity Name { get; set; }` |
| `List<HumanNameEntity>` | `HumanName` | Multiple names | `public List<HumanNameEntity> Names { get; set; } = new();` |

**JSON Structure:**
```json
{
  "name": [{
    "use": "official",
    "family": "Tan",
    "given": ["John", "Wei"],
    "prefix": ["Mr"]
  }]
}
```

## Backbone Elements (Components)

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `{Name}Component` | `BackboneElement` | Custom nested structure (single) | `public ItemComponent Item { get; set; }` |
| `List<{Name}Component>` | `BackboneElement` | Custom nested structure (multiple) | `public List<ItemComponent> Items { get; set; } = new();` |

**Definition:**
```csharp
[FhirType("Inventory#Item", IsNestedType = true)]
public partial class ItemComponent : BackboneEntity
{
    public CodeableConceptEntity? Code { get; set; }
    public QuantityEntity? Quantity { get; set; }
}
```

**JSON Structure:**
```json
{
  "items": [{
    "code": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "123456",
        "display": "Surgical mask"
      }]
    },
    "quantity": {
      "value": 100,
      "unit": "boxes"
    }
  }]
}
```

## Native FHIR Resources

| Entity Data Type | FHIR Type | Description | Example |
|:-----------------|:----------|:------------|:--------|
| `Medication` | `Medication` | FHIR resource (direct) | `public Medication MedicationDetail { get; set; }` |
| `Observation` | `Observation` | FHIR resource (direct) | `public Observation ObservationDetail { get; set; }` |

**Note:** Use sparingly - usually better to use ResourceReferenceEntity

## Type Selection Guide

### Simple Values → Primitives
```csharp
public bool? Active { get; set; }
public string? Description { get; set; }
public int? Count { get; set; }
public decimal? Price { get; set; }
```

### Dates → Date/DateTime Entities
```csharp
public DateEntity? BirthDate { get; set; }
public DateTimeEntity CreatedAt { get; set; }
```

### Identifiers → IdentifierEntity
```csharp
// Single identifier
public IdentifierEntity PatientId { get; set; }

// Multiple identifiers
public List<IdentifierEntity> Identifiers { get; set; } = new();
```

### References to Other Resources → ResourceReferenceEntity
```csharp
// Single reference
public ResourceReferenceEntity? Patient { get; set; }

// Multiple references
public List<ResourceReferenceEntity> Practitioners { get; set; } = new();
```

### Coded Values → CodeableConceptEntity
```csharp
public CodeableConceptEntity? Status { get; set; }
public CodeableConceptEntity? Type { get; set; }
```

### R5 Coded Values with References → CodeableReferenceEntity
```csharp
// R5 only - combines code and reference
public CodeableReferenceEntity? Manifestation { get; set; }
```

### Measurements → QuantityEntity
```csharp
public QuantityEntity? Weight { get; set; }
public QuantityEntity? Height { get; set; }
```

### Time Ranges → PeriodEntity
```csharp
public PeriodEntity? ValidPeriod { get; set; }
public PeriodEntity? EnrollmentPeriod { get; set; }
```

### Complex Nested Data → Components
```csharp
[FhirType("Resource#ComponentName", IsNestedType = true)]
public partial class ComponentNameComponent : BackboneEntity
{
    // Component properties
}

// Usage
public List<ComponentNameComponent> Components { get; set; } = new();
```

## Cardinality Patterns

### 0..1 (Optional Single)
```csharp
public string? Description { get; set; }
public CodeableConceptEntity? Type { get; set; }
```

### 1..1 (Required Single)
```csharp
public string Description { get; set; } = string.Empty;
public CodeableConceptEntity Type { get; set; } = new();
```

### 0..* (Optional Multiple)
```csharp
public List<IdentifierEntity> Identifiers { get; set; } = new();
public List<ResourceReferenceEntity> Participants { get; set; } = new();
```

### 1..* (Required Multiple)
```csharp
[Required]
public List<IdentifierEntity> Identifiers { get; set; } = new();
```

## Nullable vs Non-Nullable Guidelines

**Use Nullable (`?`) When:**
- ✅ Field is optional (cardinality 0..1)
- ✅ Value may not be present
- ✅ Following FHIR specification optionality

**Use Non-Nullable When:**
- ✅ Field is required (cardinality 1..1)
- ✅ Initialize with `= new()` or `= string.Empty`
- ✅ FHIR spec requires the field

**Collections:**
- ✅ Always initialize with `= new()` even if optional
- ✅ Empty list represents 0 items (valid state)

## Validation Attributes

While not part of FHIR spec, you can add validation attributes:

```csharp
using System.ComponentModel.DataAnnotations;

public class InventoryEntity : ResourceEntity
{
    [Required]
    public List<IdentifierEntity> Identifier { get; set; } = new();

    [MaxLength(500)]
    public string? Description { get; set; }

    [Range(0, int.MaxValue)]
    public int? Quantity { get; set; }
}
```

**Use sparingly** - FHIR validation should be primary mechanism
