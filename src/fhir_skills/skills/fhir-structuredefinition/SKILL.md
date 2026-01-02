---
name: fhir-structuredefinition
description: Generates FHIR StructureDefinition conformance resources including profiles, extensions, and custom resource definitions. Use when creating FHIR profiles with constraints, defining extensions, or generating conformance resources.
allowed-tools: Read, Grep, Glob, Write, Edit, WebFetch
---

# FHIR StructureDefinition Generator

This skill generates FHIR conformance resources following official FHIR specifications.

## What This Skill Generates

When you ask me to create a StructureDefinition, I'll generate:

1. **Profile** - Constraints on existing FHIR resources
2. **Extension** - Additional data fields for resources
3. **Custom Resource** - New resource type definitions
4. **Slicing** - Multiple types of same element (e.g., identifiers)
5. **Sample Requests** - HTTP examples for validation

## When to Create Each Type

### Profile (derivation: "constraint")
**Use when:** Constraining existing FHIR resource

**Examples:**
- "Make Patient.name required"
- "Restrict Patient to Singapore NRIC only"
- "Add must-support flags for specific fields"

### Extension (complex-type)
**Use when:** Adding data fields to existing resource

**Examples:**
- "Add race extension to Patient"
- "Add override-capacity flag to Slot"
- "Add preferred-language to Patient"

### Custom Resource (derivation: "specialization")
**Use when:** Creating new resource type

**Examples:**
- "Create Inventory resource type"
- "Define custom Enrollment resource"

## Quick Start

**Example request:**
```
"Create a Patient profile for Singapore that:
- Makes name required
- Requires NRIC identifier
- Adds validation for NRIC format
- Uses FHIR R5"
```

## FHIR Version Detection

**Auto-Detection Priority:**
1. Check .csproj for FHIR library versions
2. Ask user if ambiguous
3. Default to R5 (5.0.0)

**Version Values:**
- **R5:** `"fhirVersion": "5.0.0"`
- **R4B:** `"fhirVersion": "4.3.0"`

**Note:** In FHIR Engine, R4 package targets R4B.

## Profile Template

### Basic Profile

```json
{
  "resourceType": "StructureDefinition",
  "id": "profile-patient-singapore",
  "url": "https://fhir.synapxe.sg/StructureDefinition/profile-Patient-Singapore",
  "version": "1.0.0",
  "name": "ProfilePatientSingapore",
  "title": "Singapore Patient Profile",
  "status": "active",
  "experimental": false,
  "date": "2024-01-15",
  "publisher": "Synapxe",
  "description": "Patient profile for Singapore healthcare with NRIC validation",
  "fhirVersion": "5.0.0",
  "kind": "resource",
  "abstract": false,
  "type": "Patient",
  "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient",
  "derivation": "constraint",
  "differential": {
    "element": [
      {
        "id": "Patient.identifier",
        "path": "Patient.identifier",
        "slicing": {
          "discriminator": [{
            "type": "pattern",
            "path": "system"
          }],
          "rules": "open"
        },
        "min": 1,
        "mustSupport": true
      },
      {
        "id": "Patient.identifier:nric",
        "path": "Patient.identifier",
        "sliceName": "nric",
        "min": 1,
        "max": "1",
        "patternIdentifier": {
          "system": "https://fhir.synapxe.sg/NamingSystem/nric"
        }
      },
      {
        "id": "Patient.identifier:nric.system",
        "path": "Patient.identifier.system",
        "fixedUri": "https://fhir.synapxe.sg/NamingSystem/nric"
      },
      {
        "id": "Patient.identifier:nric.value",
        "path": "Patient.identifier.value",
        "min": 1,
        "constraint": [{
          "key": "nric-1",
          "severity": "error",
          "human": "NRIC must follow Singapore format",
          "expression": "matches('[STFG]\\\\d{7}[A-Z]')"
        }]
      },
      {
        "id": "Patient.name",
        "path": "Patient.name",
        "min": 1,
        "mustSupport": true
      }
    ]
  }
}
```

## Extension Template

### Simple Extension

```json
{
  "resourceType": "StructureDefinition",
  "id": "extension-race",
  "url": "https://fhir.synapxe.sg/StructureDefinition/extension-race",
  "version": "1.0.0",
  "name": "ExtensionRace",
  "title": "Race Extension",
  "status": "active",
  "experimental": false,
  "date": "2024-01-15",
  "publisher": "Synapxe",
  "description": "Extension for patient race classification",
  "fhirVersion": "5.0.0",
  "kind": "complex-type",
  "abstract": false,
  "context": [{
    "type": "element",
    "expression": "Patient"
  }],
  "type": "Extension",
  "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Extension",
  "derivation": "constraint",
  "differential": {
    "element": [
      {
        "id": "Extension.url",
        "path": "Extension.url",
        "fixedUri": "https://fhir.synapxe.sg/StructureDefinition/extension-race"
      },
      {
        "id": "Extension.value[x]",
        "path": "Extension.value[x]",
        "type": [{
          "code": "CodeableConcept"
        }],
        "binding": {
          "strength": "required",
          "valueSet": "https://fhir.synapxe.sg/ValueSet/race-codes"
        }
      }
    ]
  }
}
```

### Complex Extension (Multiple Sub-Extensions)

```json
{
  "resourceType": "StructureDefinition",
  "id": "extension-contact-details",
  "url": "https://fhir.synapxe.sg/StructureDefinition/extension-contact-details",
  "version": "1.0.0",
  "name": "ExtensionContactDetails",
  "title": "Contact Details Extension",
  "status": "active",
  "fhirVersion": "5.0.0",
  "kind": "complex-type",
  "abstract": false,
  "context": [{
    "type": "element",
    "expression": "Patient"
  }],
  "type": "Extension",
  "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Extension",
  "derivation": "constraint",
  "differential": {
    "element": [
      {
        "id": "Extension",
        "path": "Extension"
      },
      {
        "id": "Extension.extension:email",
        "path": "Extension.extension",
        "sliceName": "email",
        "min": 0,
        "max": "1"
      },
      {
        "id": "Extension.extension:email.url",
        "path": "Extension.extension.url",
        "fixedUri": "email"
      },
      {
        "id": "Extension.extension:email.value[x]",
        "path": "Extension.extension.value[x]",
        "type": [{"code": "string"}]
      },
      {
        "id": "Extension.extension:phone",
        "path": "Extension.extension",
        "sliceName": "phone",
        "min": 0,
        "max": "1"
      },
      {
        "id": "Extension.extension:phone.url",
        "path": "Extension.extension.url",
        "fixedUri": "phone"
      },
      {
        "id": "Extension.extension:phone.value[x]",
        "path": "Extension.extension.value[x]",
        "type": [{"code": "string"}]
      },
      {
        "id": "Extension.url",
        "path": "Extension.url",
        "fixedUri": "https://fhir.synapxe.sg/StructureDefinition/extension-contact-details"
      },
      {
        "id": "Extension.value[x]",
        "path": "Extension.value[x]",
        "max": "0"
      }
    ]
  }
}
```

## Element Constraint Patterns

### Make Field Required

```json
{
  "id": "Patient.name",
  "path": "Patient.name",
  "min": 1,
  "mustSupport": true
}
```

### Fixed Value

```json
{
  "id": "Patient.active",
  "path": "Patient.active",
  "fixedBoolean": true
}
```

### Pattern Matching

```json
{
  "id": "Patient.identifier.system",
  "path": "Patient.identifier.system",
  "patternUri": "https://fhir.synapxe.sg/NamingSystem/nric"
}
```

### Prohibit Field

```json
{
  "id": "Patient.photo",
  "path": "Patient.photo",
  "max": "0"
}
```

### Cardinality Changes

```json
// Make optional field required
{
  "id": "Patient.gender",
  "path": "Patient.gender",
  "min": 1
}

// Limit to single value (was 0..*)
{
  "id": "Patient.name",
  "path": "Patient.name",
  "max": "1"
}
```

## Slicing Patterns

### Identifier Slicing (Multiple Identifier Types)

```json
// Base element with discriminator
{
  "id": "Patient.identifier",
  "path": "Patient.identifier",
  "slicing": {
    "discriminator": [{
      "type": "pattern",
      "path": "system"
    }],
    "rules": "open"
  },
  "min": 1
},

// NRIC slice
{
  "id": "Patient.identifier:nric",
  "path": "Patient.identifier",
  "sliceName": "nric",
  "min": 1,
  "max": "1",
  "patternIdentifier": {
    "system": "https://fhir.synapxe.sg/NamingSystem/nric"
  }
},
{
  "id": "Patient.identifier:nric.system",
  "path": "Patient.identifier.system",
  "fixedUri": "https://fhir.synapxe.sg/NamingSystem/nric"
},
{
  "id": "Patient.identifier:nric.value",
  "path": "Patient.identifier.value",
  "min": 1
},

// Passport slice
{
  "id": "Patient.identifier:passport",
  "path": "Patient.identifier",
  "sliceName": "passport",
  "min": 0,
  "max": "1",
  "patternIdentifier": {
    "system": "https://fhir.synapxe.sg/NamingSystem/passport"
  }
},
{
  "id": "Patient.identifier:passport.system",
  "path": "Patient.identifier.system",
  "fixedUri": "https://fhir.synapxe.sg/NamingSystem/passport"
}
```

## Validation Constraints

### FHIRPath Expression

```json
{
  "id": "Patient.identifier:nric.value",
  "path": "Patient.identifier.value",
  "constraint": [{
    "key": "nric-1",
    "severity": "error",
    "human": "NRIC must follow Singapore NRIC format (S/T/F/G + 7 digits + checksum)",
    "expression": "matches('[STFG]\\\\d{7}[A-Z]')"
  }]
}
```

### Terminology Binding

```json
{
  "id": "Patient.gender",
  "path": "Patient.gender",
  "binding": {
    "strength": "required",
    "valueSet": "http://hl7.org/fhir/ValueSet/administrative-gender"
  }
}
```

**⚠️ CRITICAL:** Use canonical ValueSet URLs, NOT documentation URLs:

```json
// ✅ CORRECT - Canonical URL
"valueSet": "http://hl7.org/fhir/ValueSet/request-status"

// ❌ WRONG - Documentation URL
"valueSet": "http://hl7.org/fhir/valueset-request-status.html"
```

### Binding Strength

- **required** - Must use code from ValueSet
- **extensible** - Should use code from ValueSet
- **preferred** - Recommended to use ValueSet
- **example** - Example codes provided

## URL Construction Rules

### FHIR Core Resources

```json
"baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient"
"baseDefinition": "http://hl7.org/fhir/StructureDefinition/Extension"
```

### FHIR Core ValueSets

```json
"valueSet": "http://hl7.org/fhir/ValueSet/administrative-gender"
"valueSet": "http://hl7.org/fhir/ValueSet/request-status"
"valueSet": "http://hl7.org/fhir/ValueSet/care-plan-intent"
```

### Custom Resources (Organization-Specific)

```json
"url": "https://fhir.synapxe.sg/StructureDefinition/profile-Patient-Singapore"
"url": "https://fhir.synapxe.sg/StructureDefinition/extension-race"
"valueSet": "https://fhir.synapxe.sg/ValueSet/race-codes"
```

**User-Specified URLs:** Use exactly as provided by user

## File Naming Conventions

### StructureDefinitions

```
/Conformance/
  profile-patient-singapore.StructureDefinition.json
  extension-race.StructureDefinition.json
  extension-override-capacity.StructureDefinition.json
```

**Patterns:**
- **Profiles:** `profile-[ResourceType]-[Name].StructureDefinition.json`
- **Extensions:** `extension-[name].StructureDefinition.json`
- **Custom Resources:** `[ResourceType].StructureDefinition.json`

### Sample Requests

```
/Sample Requests/
  patient-profile-validation.http
  patient-with-race-extension.http
```

**Pattern:** `[resourcetype]-[operation].http`

## Sample HTTP Requests

### Profile Validation

```http
@baseUrl = https://localhost:7001

### Create Patient with Profile
POST {{baseUrl}}/Patient
Content-Type: application/fhir+json

{
  "resourceType": "Patient",
  "meta": {
    "profile": [
      "https://fhir.synapxe.sg/StructureDefinition/profile-Patient-Singapore"
    ]
  },
  "identifier": [{
    "system": "https://fhir.synapxe.sg/NamingSystem/nric",
    "value": "S1234567D"
  }],
  "name": [{
    "family": "Tan",
    "given": ["John"]
  }],
  "gender": "male",
  "birthDate": "1990-01-01"
}

### Validate Against Profile
POST {{baseUrl}}/Patient/$validate
Content-Type: application/fhir+json

{
  "resourceType": "Parameters",
  "parameter": [{
    "name": "resource",
    "resource": {
      "resourceType": "Patient",
      "meta": {
        "profile": [
          "https://fhir.synapxe.sg/StructureDefinition/profile-Patient-Singapore"
        ]
      },
      "identifier": [{
        "system": "https://fhir.synapxe.sg/NamingSystem/nric",
        "value": "S1234567D"
      }],
      "name": [{
        "family": "Tan",
        "given": ["John"]
      }]
    }
  }, {
    "name": "profile",
    "valueCanonical": "https://fhir.synapxe.sg/StructureDefinition/profile-Patient-Singapore"
  }]
}
```

### Extension Usage

```http
### Create Patient with Extension
POST {{baseUrl}}/Patient
Content-Type: application/fhir+json

{
  "resourceType": "Patient",
  "extension": [{
    "url": "https://fhir.synapxe.sg/StructureDefinition/extension-race",
    "valueCodeableConcept": {
      "coding": [{
        "system": "https://fhir.synapxe.sg/CodeSystem/race",
        "code": "chinese",
        "display": "Chinese"
      }]
    }
  }],
  "identifier": [{
    "system": "https://fhir.synapxe.sg/NamingSystem/nric",
    "value": "S1234567D"
  }],
  "name": [{
    "family": "Tan",
    "given": ["John"]
  }]
}
```

## Configuration Integration

### capability-statement.json

```json
{
  "rest": [{
    "resource": [{
      "type": "Patient",
      "profile": "https://fhir.synapxe.sg/StructureDefinition/profile-Patient-Singapore",
      "supportedProfile": [
        "https://fhir.synapxe.sg/StructureDefinition/profile-Patient-Singapore"
      ],
      "interaction": [
        {"code": "create"},
        {"code": "read"}
      ]
    }]
  }]
}
```

## Validation Checklist

Before completing StructureDefinition generation:

- ✅ `fhirVersion` field present (5.0.0 or 4.3.0)
- ✅ `url` follows organizational pattern or user specification
- ✅ `derivation` correct ("constraint" for profiles, "specialization" for custom)
- ✅ Element paths accurate (e.g., "Patient.identifier")
- ✅ Slicing implemented for multiple identifier types
- ✅ Constraints use FHIRPath expressions
- ✅ ValueSet bindings use canonical URLs (not .html)
- ✅ Sample HTTP requests included
- ✅ File naming follows conventions

## Common Patterns

### Pattern: Singapore Patient Profile

```
"Create Singapore Patient profile that:
- Requires NRIC identifier
- Makes name required
- Adds NRIC format validation
- Adds race extension
- Uses FHIR R5"
```

### Pattern: Appointment Constraints

```
"Create Appointment profile that:
- Requires start and end times
- Makes patient participant required
- Restricts status to allowed values
- Adds must-support flags"
```

### Pattern: Multi-Value Extension

```
"Create contact-preferences extension with:
- Preferred contact method (phone/email/mail)
- Best time to contact
- Language preference
- Apply to Patient resource"
```

## What to Tell Me

When requesting StructureDefinition generation:

1. **Type**: Profile, Extension, or Custom Resource
2. **Base Resource**: Which FHIR resource (for profiles/extensions)
3. **Constraints**: Required fields, fixed values, restrictions
4. **FHIR Version**: R5 or R4B (defaults to R5)
5. **Organization URL**: Custom URL prefix (defaults to https://fhir.synapxe.sg/)

**Example:**
```
"Create a Patient profile for Singapore that:
- Requires NRIC identifier with format validation
- Makes name and gender required
- Adds race extension (CodeableConcept)
- Prohibits photo field
- Use FHIR R5"
```

I'll generate:
- Complete StructureDefinition JSON
- Extension definition if needed
- Sample HTTP requests for validation
- Configuration updates

## Related Skills

- **Custom resource entity?** → Use `fhir-custom-resource` skill
- **Handler implementation?** → Use `fhir-handler-generator` skill
- **Configuration issues?** → Use `fhir-config-troubleshooting` skill
