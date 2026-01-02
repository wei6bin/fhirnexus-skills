---
name: fhir-custom-resource
description: Creates custom FHIR resources using FHIR Engine's code-first POCO approach. Use when creating new domain-specific resources, implementing custom resource types, or extending FHIR with organization-specific structures.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# FHIR Custom Resource Generator

This skill helps you create custom FHIR resources using FHIR Engine's code-first approach.

## When to Create Custom Resources

### Use Custom Resources When:
- ✅ Completely new domain concept not covered by existing FHIR resources
- ✅ Complex data structure requiring multiple nested components
- ✅ Organization-specific workflows requiring specialized resources
- ✅ No standard FHIR resource fits your use case

### Use Extensions Instead When:
- ✅ Adding fields to existing FHIR resources
- ✅ Critical interoperability with external systems required
- ✅ Standard extensions available for your use case
- ✅ Simple data additions to standard resources

## Quick Start

When you ask me to create a custom resource, I'll guide you through:

1. **Resource Design** - Data fields and structure
2. **Entity Class Creation** - C# POCO with attributes
3. **Build & Generation** - Auto-generate StructureDefinition
4. **Configuration** - Register in fhirengine.json
5. **Sample Requests** - HTTP examples for testing

## Critical Standards

### File Locations
- **Entity Classes:** `/Data/{ResourceType}Entity.cs`
- **StructureDefinitions:** Copy from `/Generated` to `/Conformance`
- **Sample Requests:** `/Sample Requests/{resource_type}.http` (lowercase)

### Required Attributes
```csharp
[CustomFhirResource]
[FhirType("ResourceType", "https://domain/StructureDefinition/ResourceType", IsResource = true)]
public class ResourceTypeEntity : ResourceEntity
```

### FHIR Version
- **Default:** R5 (5.0.0)
- **Also Supported:** R4B (4.3.0)
- Use R5 data types (e.g., `CodeableReferenceEntity` not `CodeableConceptEntity` for manifestations)

### Package Versions
**CRITICAL:** Match existing project versions:
- `Ihis.FhirEngine.Data.Models`
- `Ihis.FhirEngine.Msbuild.Tasks`

## Resource Naming - GOLDEN RULE

⭐ **The resource type name must be EXACTLY THE SAME across all contexts:**

| Context | Format | Example |
|:--------|:-------|:--------|
| **Entity Class** | `{RESOURCE_TYPE}Entity` | `InventoryEntity` |
| **FhirType Attribute** | `"{RESOURCE_TYPE}"` | `"Inventory"` |
| **StructureDefinition URL** | `.../StructureDefinition/{RESOURCE_TYPE}` | `.../StructureDefinition/Inventory` |
| **Configuration** | `namespace.{RESOURCE_TYPE}` | `MyProject.Data.Inventory` |
| **File Names** | `{RESOURCE_TYPE}.StructureDefinition.json` | `Inventory.StructureDefinition.json` |

**⭐ C# NAMING OVERRIDE:** Use resource names EXACTLY as specified, ignoring C# conventions:

| Given Name | ❌ Don't Change | ✅ Use Exactly |
|:-----------|:----------------|:---------------|
| `ACCAllergy` | `AccAllergy` | `ACCAllergyEntity` |
| `EDVisit` | `EdVisit` | `EDVisitEntity` |
| `CPTCode` | `CptCode` | `CPTCodeEntity` |

## Entity Class Template

```csharp
using Hl7.Fhir.Introspection;
using Ihis.FhirEngine.Data.Models;

namespace MyProject.Data;

[CustomFhirResource]
[FhirType("Inventory", "https://fhir.synapxe.sg/StructureDefinition/Inventory", IsResource = true)]
public class InventoryEntity : ResourceEntity
{
    // Standard FHIR fields
    public List<IdentifierEntity> Identifier { get; set; } = new();
    public bool? Active { get; set; }
    public string? Description { get; set; }

    // Resource-specific fields
    public ResourceReferenceEntity? Location { get; set; }
    public CodeableConceptEntity? ItemType { get; set; }
    public QuantityEntity? Quantity { get; set; }
    public DateTimeEntity? ExpiryDate { get; set; }

    // Nested components
    public List<StockLevelComponent> StockLevels { get; set; } = new();
}

// Nested component
[FhirType("Inventory#StockLevel", IsNestedType = true)]
public partial class StockLevelComponent : BackboneEntity
{
    public string? Level { get; set; }  // low, normal, high
    public QuantityEntity? Threshold { get; set; }
}
```

**Full templates:** See [templates/entity-class-template.md](templates/entity-class-template.md)

## Supported Data Types

| Entity Type | FHIR Type | Example |
|:------------|:----------|:--------|
| `bool?` | `boolean` | `public bool? Active { get; set; }` |
| `string?` | `string` | `public string? Description { get; set; }` |
| `int?` | `integer` | `public int? Count { get; set; }` |
| `decimal?` | `decimal` | `public decimal? Price { get; set; }` |
| `DateEntity` | `date` | `public DateEntity? BirthDate { get; set; }` |
| `DateTimeEntity` | `dateTime` | `public DateTimeEntity CreatedDate { get; set; }` |
| `IdentifierEntity` | `Identifier` | `public IdentifierEntity PatientId { get; set; }` |
| `List<IdentifierEntity>` | `Identifier` (0..*) | `public List<IdentifierEntity> Identifiers { get; set; }` |
| `ResourceReferenceEntity` | `Reference` | `public ResourceReferenceEntity? Patient { get; set; }` |
| `CodeableConceptEntity` | `CodeableConcept` | `public CodeableConceptEntity Type { get; set; }` |
| `CodeableReferenceEntity` | `CodeableReference` (R5) | `public CodeableReferenceEntity Manifestation { get; set; }` |
| `QuantityEntity` | `Quantity` | `public QuantityEntity Weight { get; set; }` |
| `PeriodEntity` | `Period` | `public PeriodEntity ValidPeriod { get; set; }` |
| `AddressEntity` | `Address` | `public AddressEntity HomeAddress { get; set; }` |

**Complete reference:** See [data-types-reference.md](data-types-reference.md)

## Component Classes (Nested Structures)

For complex nested data, create component classes:

```csharp
[FhirType("Inventory#StockLevel", IsNestedType = true)]
public partial class StockLevelComponent : BackboneEntity
{
    public string? Level { get; set; }
    public QuantityEntity? Threshold { get; set; }
    public DateTimeEntity? LastChecked { get; set; }
}

// Usage in parent resource
public List<StockLevelComponent> StockLevels { get; set; } = new();
```

**Key Points:**
- Class name ends with `Component`
- Inherits from `BackboneEntity`
- Uses `#{ComponentName}` in FhirType URL
- `IsNestedType = true` flag required
- `partial` modifier for extensibility

**Full component templates:** See [templates/component-class-template.md](templates/component-class-template.md)

## Implementation Workflow

### Step 1: Create Entity Class

```bash
# Create in /Data folder
touch Data/InventoryEntity.cs
```

```csharp
[CustomFhirResource]
[FhirType("Inventory", "https://fhir.synapxe.sg/StructureDefinition/Inventory", IsResource = true)]
public class InventoryEntity : ResourceEntity
{
    // Define properties using supported data types
}
```

### Step 2: Build & Generate

```bash
# Build project to trigger MSBuild tasks
dotnet build

# StructureDefinition auto-generated in /Generated folder
```

### Step 3: Copy StructureDefinition

```bash
# Copy from /Generated to /Conformance
cp Generated/Inventory.StructureDefinition.json Conformance/
```

### Step 4: Create Search Parameters

**⭐ ROOT LEVEL ONLY:** Create search parameters ONLY for root-level queryable properties.

```json
{
  "resourceType": "SearchParameter",
  "id": "Inventory-identifier",
  "url": "https://fhir.synapxe.sg/SearchParameter/Inventory-identifier",
  "name": "InventoryIdentifier",
  "status": "active",
  "code": "identifier",
  "base": ["Inventory"],
  "type": "token",
  "expression": "Inventory.identifier",
  "description": "Search Inventory by identifier"
}
```

**❌ DON'T create search parameters for:**
- Nested component properties (`Item.code`, `Detail.value`)
- Complex nested structures
- BackboneElement fields

**✅ DO create search parameters for:**
- `identifier`, `active`, `status`
- Direct resource properties like `patient`, `type`, `date`

### Step 5: Update Configuration

**fhirengine.json:**

```json
{
  "SystemPlugins": {
    "CustomResources": [
      "MyProject.Data.Inventory"  // NO "Entity" suffix
    ]
  },
  "Handlers": {
    "Repository": {
      "FhirDataStore<@Local>": {
        "AcceptedTypes": ["Inventory"]  // Resource type only
      }
    }
  }
}
```

**Key Rules:**
- `CustomResources`: Full namespace WITHOUT "Entity" suffix
- `AcceptedTypes`: Resource type name only

### Step 6: Update Capability Statement

```json
{
  "rest": [{
    "resource": [{
      "type": "Inventory",
      "profile": "https://fhir.synapxe.sg/StructureDefinition/Inventory",
      "interaction": [
        {"code": "create"},
        {"code": "read"},
        {"code": "update"},
        {"code": "delete"},
        {"code": "search-type"}
      ],
      "searchParam": [{
        "name": "identifier",
        "type": "token",
        "definition": "https://fhir.synapxe.sg/SearchParameter/Inventory-identifier"
      }]
    }]
  }]
}
```

### Step 7: Create Sample Requests

**File:** `/Sample Requests/inventory.http`

```http
@baseUrl = https://localhost:7001

### Create Inventory
POST {{baseUrl}}/Inventory
Content-Type: application/fhir+json

{
  "resourceType": "Inventory",
  "identifier": [{
    "system": "https://hospital.org/inventory",
    "value": "INV-001"
  }],
  "active": true,
  "description": "Surgical masks - Box of 50",
  "location": {
    "reference": "Location/ward-a"
  },
  "itemType": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "409528009",
      "display": "Surgical mask"
    }]
  },
  "quantity": {
    "value": 100,
    "unit": "boxes"
  },
  "expiryDate": "2025-12-31",
  "stockLevels": [{
    "level": "normal",
    "threshold": {
      "value": 20,
      "unit": "boxes"
    }
  }]
}

### Read Inventory
GET {{baseUrl}}/Inventory/{{inventoryId}}

### Search Inventory
GET {{baseUrl}}/Inventory?identifier=INV-001
```

**⭐ R5 COMPLIANCE:** Ensure JSON structures follow FHIR R5 specifications.

## R5 vs R4B Differences

**Key R5 Changes Affecting Custom Resources:**

| Field | R4B Type | R5 Type |
|:------|:---------|:--------|
| `AllergyIntolerance.reaction.manifestation` | `CodeableConcept` | `CodeableReference` |
| `Condition.evidence.detail` | `Reference` | `CodeableReference` |
| `Medication.ingredient.item[x]` | `CodeableConcept` or `Reference` | `CodeableReference` |

**Use `CodeableReferenceEntity` in R5:**
```csharp
// R5 (CORRECT)
public CodeableReferenceEntity? Manifestation { get; set; }

// R4B (OLD)
public CodeableConceptEntity? Manifestation { get; set; }
```

## Validation Checklist

Before completing custom resource generation, verify:

- ✅ Entity class in `/Data` as `{ResourceType}Entity.cs`
- ✅ `[CustomFhirResource]` and `[FhirType]` attributes present
- ✅ Supported data types only (see reference table)
- ✅ Build generates StructureDefinition in `/Generated`
- ✅ StructureDefinition copied to `/Conformance`
- ✅ **Search Parameters:** Created ONLY for root-level queryable fields
- ✅ **FhirEngine Configuration:** Full namespace (no Entity suffix) in `CustomResources`
- ✅ **Capability Statement:** Resource type with profile URL
- ✅ **Package Versions:** All FhirEngine packages match project versions
- ✅ Sample `.http` requests with all CRUD operations
- ✅ **R5 Compliance:** HTTP samples follow FHIR R5 specifications
- ✅ **Build Verification:** Solution builds without errors
- ✅ **URL Alignment:** Consistent URLs across entity, config, and capability statement

## Common Patterns

### Minimal Resource (3-6 Properties)

```csharp
[CustomFhirResource]
[FhirType("Alert", "https://fhir.synapxe.sg/StructureDefinition/Alert", IsResource = true)]
public class AlertEntity : ResourceEntity
{
    public ResourceReferenceEntity? Patient { get; set; }
    public CodeableConceptEntity? AlertType { get; set; }
    public string? Message { get; set; }
    public DateTimeEntity? Timestamp { get; set; }
}
```

### Standard Resource (8-15 Properties)

```csharp
[CustomFhirResource]
[FhirType("Enrollment", "https://fhir.synapxe.sg/StructureDefinition/Enrollment", IsResource = true)]
public class EnrollmentEntity : ResourceEntity
{
    public List<IdentifierEntity> Identifier { get; set; } = new();
    public bool? Active { get; set; }
    public ResourceReferenceEntity? Patient { get; set; }
    public ResourceReferenceEntity? Program { get; set; }
    public CodeableConceptEntity? Status { get; set; }
    public PeriodEntity? EnrollmentPeriod { get; set; }
    public DateTimeEntity? EnrolledDate { get; set; }
    public List<ParticipantComponent> Participants { get; set; } = new();
}
```

### Complex Resource (15+ Properties with Components)

```csharp
[CustomFhirResource]
[FhirType("CareBundle", "https://fhir.synapxe.sg/StructureDefinition/CareBundle", IsResource = true)]
public class CareBundleEntity : ResourceEntity
{
    public List<IdentifierEntity> Identifier { get; set; } = new();
    public bool? Active { get; set; }
    public string? Title { get; set; }
    public ResourceReferenceEntity? Patient { get; set; }
    public CodeableConceptEntity? BundleType { get; set; }
    public PeriodEntity? Period { get; set; }
    public List<ResourceReferenceEntity> CareTeam { get; set; } = new();
    public List<ServiceComponent> Services { get; set; } = new();
    public List<GoalComponent> Goals { get; set; } = new();
    public List<NoteComponent> Notes { get; set; } = new();
}
```

## Common Mistakes to Avoid

❌ **Wrong namespace in CustomResources** - Must be without "Entity" suffix
❌ **Mismatched resource type names** - Must be identical across all files
❌ **Creating search parameters for nested fields** - Only root-level properties
❌ **Adding Entity suffix in configuration** - Use `MyProject.Data.Inventory`, not `InventoryEntity`
❌ **Using R4B data types in R5** - Use `CodeableReferenceEntity` for manifestations
❌ **Package version mismatch** - Must match existing project versions
❌ **Forgetting to copy StructureDefinition** - Must copy from `/Generated` to `/Conformance`

## What to Tell Me

When requesting custom resource creation:

1. **Resource Name**: "Create a resource called Inventory"
2. **Purpose**: "To track hospital inventory items"
3. **Data Fields**: List the fields you need
   - "identifier, active, description"
   - "location (reference to Location)"
   - "itemType (coded concept)"
   - "quantity, expiryDate"
4. **Nested Components** (if any): "StockLevel component with level and threshold"

**Example:**
```
"Create a custom FHIR resource called Inventory to track hospital inventory items.
It should have:
- identifier (list of identifiers)
- active (boolean)
- description (string)
- location (reference to Location resource)
- itemType (CodeableConcept for the type of item)
- quantity (Quantity with value and unit)
- expiryDate (dateTime)
- stockLevels component with level (string) and threshold (Quantity)"
```

I'll generate:
- Complete entity class with component classes
- StructureDefinition (via build)
- Search parameter definitions
- Configuration updates
- Capability statement entry
- Sample HTTP requests

## Related Skills

- **Handler implementation?** → Use `fhir-handler-generator` skill
- **Configuration issues?** → Use `fhir-config-troubleshooting` skill
- **Error debugging?** → Use `fhir-errors-debugger` skill
