# FHIR Data Mapping Patterns Reference

Comprehensive patterns and examples for mapping custom data models to FHIR resources.

## Table of Contents
- [Common Resource Selections](#common-resource-selections)
- [Data Type Transformations](#data-type-transformations)
- [Primary Key Patterns](#primary-key-patterns)
- [Child Table Patterns](#child-table-patterns)
- [Extension Patterns](#extension-patterns)
- [Complete Mapping Examples](#complete-mapping-examples)

## Common Resource Selections

### Patient-Related Data
```
Use Case: Patient demographics, contact info, identifiers
FHIR Resource: Patient
Alternative: Person (for non-patient individuals)
```

### Clinical Observations
```
Use Case: Lab results, vital signs, measurements
FHIR Resource: Observation
Alternative: DiagnosticReport (for grouped results)
```

### Scheduling Data
```
Use Case: Appointment bookings, availability
FHIR Resource: Appointment
Related: Schedule, Slot, AppointmentResponse
```

### Medication Data
```
Use Case: Prescriptions, dispensing, administration
FHIR Resource: MedicationRequest, MedicationDispense, MedicationAdministration
Related: Medication (the drug itself)
```

### Procedures and Interventions
```
Use Case: Surgeries, treatments, interventions
FHIR Resource: Procedure
Alternative: ServiceRequest (for orders/requests)
```

### Document/Reports
```
Use Case: Clinical documents, reports
FHIR Resource: DocumentReference, Composition
Alternative: DiagnosticReport (for structured reports)
```

### Billing/Claims
```
Use Case: Invoices, claims, payments
FHIR Resource: Claim, Invoice, PaymentNotice
Related: Coverage, ExplanationOfBenefit
```

### Care Planning
```
Use Case: Care plans, goals, activities
FHIR Resource: CarePlan, Goal
Related: ServiceRequest, Task
```

## Data Type Transformations

### Date/Time Conversions

**Pattern 1: Date Format Conversion**
```
Source: DD/MM/YYYY (string)
Target: YYYY-MM-DD (FHIR date)

Transformation Logic:
1. Parse source date string
2. Reformat to ISO 8601 format (YYYY-MM-DD)
3. Validate date is valid

Example:
Source: "15/06/1990"
Target: "1990-06-15"
```

**Pattern 2: DateTime with Timezone**
```
Source: Unix timestamp (integer)
Target: FHIR dateTime (ISO 8601 with timezone)

Transformation Logic:
1. Convert Unix timestamp to DateTime
2. Apply appropriate timezone (Singapore: +08:00)
3. Format as ISO 8601: YYYY-MM-DDThh:mm:ss+08:00

Example:
Source: 1642492800 (Unix timestamp)
Target: "2022-01-18T14:00:00+08:00"
```

**Pattern 3: Date with Additional Time Component**
```
Source: birthDate (date) + birthTime (time)
Target: Patient.birthDate + birthTime extension

Mapping:
- birthDate → Patient.birthDate (FHIR date)
- birthTime → Extension at https://fhir.synapxe.sg/StructureDefinition/patient-birth-time

FHIR JSON:
{
  "birthDate": "1990-06-15",
  "_birthDate": {
    "extension": [{
      "url": "https://fhir.synapxe.sg/StructureDefinition/patient-birth-time",
      "valueTime": "14:30:00"
    }]
  }
}
```

### String/Text Transformations

**Pattern 1: Full Name Parsing**
```
Source: fullName (string) - "Dr. John Wei Tan"
Target: Patient.name (HumanName)

Transformation Logic:
1. Split by whitespace
2. Identify prefix (Dr., Mr., Mrs., etc.)
3. Identify given names (first, middle)
4. Identify family name (last)

FHIR JSON:
{
  "name": [{
    "use": "official",
    "prefix": ["Dr"],
    "given": ["John", "Wei"],
    "family": "Tan"
  }]
}
```

**Pattern 2: Address Parsing**
```
Source: fullAddress (string) - "123 Main St, Apt 4B, Singapore 123456"
Target: Patient.address (Address)

Transformation Logic:
1. Parse address components
2. Split by commas
3. Extract postal code
4. Extract city/country

FHIR JSON:
{
  "address": [{
    "use": "home",
    "type": "physical",
    "line": ["123 Main St", "Apt 4B"],
    "city": "Singapore",
    "postalCode": "123456",
    "country": "SG"
  }]
}
```

### Coded Value Transformations

**Pattern 1: Enum to CodeableConcept**
```
Source: status (enum) - "active", "inactive", "pending"
Target: Patient.active (boolean) + status extension

Transformation Logic:
1. Map enum values to FHIR codes
2. Use appropriate code system
3. Handle unmapped values

Value Set Mapping:
- "active" → true (Patient.active)
- "inactive" → false (Patient.active)
- "pending" → Extension with custom code
```

**Pattern 2: Code + Display Text**
```
Source: diagnosisCode (string), diagnosisText (string)
Target: Condition.code (CodeableConcept)

FHIR JSON:
{
  "code": {
    "coding": [{
      "system": "http://hl7.org/fhir/sid/icd-10",
      "code": "E11.9",
      "display": "Type 2 diabetes mellitus without complications"
    }],
    "text": "Type 2 diabetes mellitus without complications"
  }
}
```

### Numeric Transformations

**Pattern 1: Unit Conversion**
```
Source: weightPounds (decimal)
Target: Observation.valueQuantity (kg)

Transformation Logic:
1. Convert pounds to kilograms (divide by 2.20462)
2. Round to appropriate precision
3. Set UCUM unit code

FHIR JSON:
{
  "valueQuantity": {
    "value": 68.2,
    "unit": "kg",
    "system": "http://unitsofmeasure.org",
    "code": "kg"
  }
}
```

**Pattern 2: Precision Handling**
```
Source: temperature (float, 2 decimal places)
Target: Observation.valueQuantity

Transformation Logic:
1. Preserve original precision
2. Set appropriate unit (Celsius for Singapore)

FHIR JSON:
{
  "valueQuantity": {
    "value": 36.75,
    "unit": "°C",
    "system": "http://unitsofmeasure.org",
    "code": "Cel"
  }
}
```

## Primary Key Patterns

### Pattern 1: Integer Auto-Increment PK
```
Source Schema:
CREATE TABLE Patients (
  PatientId INT PRIMARY KEY IDENTITY(1,1),
  ...
)

Mapping Analysis:
- Field: PatientId
- Type: Integer (auto-increment)
- Purpose: Database primary key only
- FHIR Mapping: NOT mapped to FHIR resource
- Code Generation Use: IResourceEntity<int>

Data Store Entity:
public class PatientModel : IResourceEntity<int>
{
    public int Id { get; set; }  // Maps to PatientId
    public int? VersionId { get; set; }
    ...
}
```

### Pattern 2: GUID/UUID PK
```
Source Schema:
CREATE TABLE Appointments (
  AppointmentId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
  ...
)

Mapping Analysis:
- Field: AppointmentId
- Type: GUID/UUID
- Purpose: Database primary key
- FHIR Mapping: NOT mapped (resource.id is separate)
- Code Generation Use: IResourceEntity<Guid>

Data Store Entity:
public class AppointmentModel : IResourceEntity<Guid>
{
    public Guid Id { get; set; }  // Maps to AppointmentId
    public int? VersionId { get; set; }
    ...
}
```

### Pattern 3: String PK (Business Identifier)
```
Source Schema:
CREATE TABLE Locations (
  LocationCode VARCHAR(50) PRIMARY KEY,
  ...
)

Mapping Analysis:
- Field: LocationCode
- Type: String (business identifier)
- Purpose: Database primary key + business key
- FHIR Mapping:
  - As PK: NOT mapped to FHIR
  - As Business ID: Map to Location.identifier
- Code Generation Use: IResourceEntity<string>

Data Store Entity:
public class LocationModel : IResourceEntity<string>
{
    public string Id { get; set; }  // Maps to LocationCode (PK)
    public int? VersionId { get; set; }

    // Also map to identifier for business use
    public string? IdentifierSystem { get; set; }
    public string? IdentifierValue { get; set; }  // Can duplicate Id
}

FHIR Mapping:
LocationCode → Both IResourceEntity<string>.Id AND Location.identifier
```

### Pattern 4: Composite PK
```
Source Schema:
CREATE TABLE ObservationComponents (
  ObservationId INT,
  ComponentId INT,
  PRIMARY KEY (ObservationId, ComponentId)
)

Mapping Analysis:
- This is a child table pattern (see Child Table Patterns)
- Maps to Observation.component[] (BackboneElement)
- Primary key used for database relationships only
- NOT mapped to FHIR
```

## Child Table Patterns

### Pattern 1: One-to-Many → Identifier Array
```
Source Schema:
Patients (PatientId PK)
PatientIdentifiers (Id PK, PatientId FK, System, Value)

Mapping:
- PatientIdentifiers table → Patient.identifier[] (IdentifierEntity[])
- Cardinality: 0..*

FHIR JSON:
{
  "resourceType": "Patient",
  "identifier": [
    {
      "system": "https://hospital.org/patient-id",
      "value": "12345"
    },
    {
      "system": "https://nric.gov.sg",
      "value": "S1234567D"
    }
  ]
}

Data Store Mapping:
PatientModel.IdentifierSystem (string) - stores first identifier system
PatientModel.IdentifierValue (string) - stores first identifier value
Additional identifiers stored as JSON or separate join table
```

### Pattern 2: One-to-Many → BackboneElement Array
```
Source Schema:
Patients (PatientId PK)
PatientContacts (Id PK, PatientId FK, Name, Relationship, Phone)

Mapping:
- PatientContacts table → Patient.contact[] (BackboneElement)
- Each row becomes an element in the array

FHIR JSON:
{
  "resourceType": "Patient",
  "contact": [
    {
      "relationship": [{
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
          "code": "N",
          "display": "Next-of-Kin"
        }]
      }],
      "name": {
        "text": "Jane Tan"
      },
      "telecom": [{
        "system": "phone",
        "value": "+65-9123-4567"
      }]
    }
  ]
}

Data Store Options:
1. Store as JSON column in PatientModel
2. Create separate ContactModel with FK to PatientModel
3. Use EF Core owned entities
```

### Pattern 3: One-to-Many → CodeableConcept Array
```
Source Schema:
Observations (ObservationId PK)
ObservationCategories (Id PK, ObservationId FK, System, Code, Display)

Mapping:
- ObservationCategories table → Observation.category[] (CodeableConcept[])

FHIR JSON:
{
  "resourceType": "Observation",
  "category": [
    {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "code": "vital-signs",
        "display": "Vital Signs"
      }]
    },
    {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "code": "laboratory",
        "display": "Laboratory"
      }]
    }
  ]
}
```

### Pattern 4: Nested BackboneElement (Multi-Level)
```
Source Schema:
Observations (ObservationId PK)
ObservationComponents (ComponentId PK, ObservationId FK, Code, Value)
ComponentReferenceRanges (RangeId PK, ComponentId FK, Low, High)

Mapping:
- ObservationComponents → Observation.component[]
- ComponentReferenceRanges → Observation.component.referenceRange[]

FHIR JSON:
{
  "resourceType": "Observation",
  "component": [
    {
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "8480-6",
          "display": "Systolic blood pressure"
        }]
      },
      "valueQuantity": {
        "value": 120,
        "unit": "mmHg"
      },
      "referenceRange": [{
        "low": {
          "value": 90,
          "unit": "mmHg"
        },
        "high": {
          "value": 120,
          "unit": "mmHg"
        }
      }]
    }
  ]
}
```

## Extension Patterns

### Pattern 1: Simple Field-Level Extension
```
Use Case: Add birth time to Patient.birthDate

Extension Definition:
{
  "url": "https://fhir.synapxe.sg/StructureDefinition/patient-birth-time",
  "title": "Patient Birth Time",
  "status": "active",
  "description": "Time of birth in addition to date of birth",
  "context": [{
    "type": "element",
    "expression": "Patient.birthDate"
  }],
  "type": "Extension",
  "valueType": "time"
}

FHIR Usage:
{
  "birthDate": "1990-06-15",
  "_birthDate": {
    "extension": [{
      "url": "https://fhir.synapxe.sg/StructureDefinition/patient-birth-time",
      "valueTime": "14:30:00"
    }]
  }
}

Source Mapping:
birthDateTime (datetime) →
  - birthDate: "1990-06-15" (extract date)
  - birthTime extension: "14:30:00" (extract time)
```

### Pattern 2: Resource-Level Extension (Simple Value)
```
Use Case: Add loyalty membership ID to Patient

Extension Definition:
{
  "url": "https://fhir.synapxe.sg/StructureDefinition/loyalty-membership",
  "title": "Loyalty Membership",
  "status": "active",
  "description": "Patient loyalty program membership identifier",
  "context": [{
    "type": "element",
    "expression": "Patient"
  }],
  "type": "Extension",
  "valueType": "string"
}

FHIR Usage:
{
  "resourceType": "Patient",
  "extension": [{
    "url": "https://fhir.synapxe.sg/StructureDefinition/loyalty-membership",
    "valueString": "GOLD-12345"
  }]
}

Source Mapping:
loyaltyMemberId (varchar) → extension.valueString
```

### Pattern 3: Complex Extension with Nested Structure
```
Use Case: Store patient insurance details

Extension Definition:
{
  "url": "https://fhir.synapxe.sg/StructureDefinition/insurance-details",
  "title": "Insurance Details",
  "status": "active",
  "description": "Detailed insurance information",
  "context": [{
    "type": "element",
    "expression": "Patient"
  }],
  "type": "Extension",
  "elements": [
    {
      "id": "Extension.extension:provider",
      "path": "Extension.extension",
      "sliceName": "provider",
      "type": "string"
    },
    {
      "id": "Extension.extension:policyNumber",
      "path": "Extension.extension",
      "sliceName": "policyNumber",
      "type": "string"
    },
    {
      "id": "Extension.extension:validUntil",
      "path": "Extension.extension",
      "sliceName": "validUntil",
      "type": "date"
    }
  ]
}

FHIR Usage:
{
  "resourceType": "Patient",
  "extension": [{
    "url": "https://fhir.synapxe.sg/StructureDefinition/insurance-details",
    "extension": [
      {
        "url": "provider",
        "valueString": "AIA Singapore"
      },
      {
        "url": "policyNumber",
        "valueString": "POL-123456"
      },
      {
        "url": "validUntil",
        "valueDate": "2025-12-31"
      }
    ]
  }]
}

Source Mapping:
insuranceProvider → extension.extension[provider].valueString
insurancePolicyNumber → extension.extension[policyNumber].valueString
insuranceValidUntil → extension.extension[validUntil].valueDate
```

### Pattern 4: Extension with CodeableConcept
```
Use Case: Add custom allergy severity classification

Extension Definition:
{
  "url": "https://fhir.synapxe.sg/StructureDefinition/allergy-severity-custom",
  "title": "Custom Allergy Severity",
  "status": "active",
  "description": "Organization-specific allergy severity classification",
  "context": [{
    "type": "element",
    "expression": "AllergyIntolerance"
  }],
  "type": "Extension",
  "valueType": "CodeableConcept"
}

FHIR Usage:
{
  "resourceType": "AllergyIntolerance",
  "extension": [{
    "url": "https://fhir.synapxe.sg/StructureDefinition/allergy-severity-custom",
    "valueCodeableConcept": {
      "coding": [{
        "system": "https://hospital.org/allergy-severity",
        "code": "level-3",
        "display": "Level 3 - Severe Reaction"
      }]
    }
  }]
}
```

## Complete Mapping Examples

### Example 1: Simple Patient Demographics

**Source Schema:**
```sql
CREATE TABLE Patients (
  PatientId INT PRIMARY KEY IDENTITY(1,1),
  FirstName NVARCHAR(100) NOT NULL,
  LastName NVARCHAR(100) NOT NULL,
  DateOfBirth DATE NOT NULL,
  Gender CHAR(1),  -- M/F/O
  PhoneNumber VARCHAR(20),
  Email VARCHAR(100),
  NRIC VARCHAR(9) UNIQUE
)
```

**Mapping Analysis:**

| Custom Field | FHIR Element Path | Mapping Type | Transformation/Notes | Confidence |
|--------------|-------------------|--------------|---------------------|------------|
| PatientId | N/A | PrimaryKey | Integer PK for IResourceEntity<int> | High |
| FirstName | Patient.name.given | Direct | Array element | High |
| LastName | Patient.name.family | Direct | String value | High |
| DateOfBirth | Patient.birthDate | Direct | Date format | High |
| Gender | Patient.gender | Transformed | M→male, F→female, O→other | High |
| PhoneNumber | Patient.telecom | Transformed | System=phone, use=mobile | High |
| Email | Patient.telecom | Transformed | System=email | High |
| NRIC | Patient.identifier | Direct | System=https://nric.gov.sg | High |

**Sample FHIR Instance:**
```json
{
  "resourceType": "Patient",
  "id": "patient-123",
  "identifier": [{
    "system": "https://nric.gov.sg",
    "value": "S1234567D"
  }],
  "name": [{
    "use": "official",
    "family": "Tan",
    "given": ["John"]
  }],
  "telecom": [
    {
      "system": "phone",
      "value": "+65-9123-4567",
      "use": "mobile"
    },
    {
      "system": "email",
      "value": "john.tan@example.com"
    }
  ],
  "gender": "male",
  "birthDate": "1990-06-15"
}
```

### Example 2: Appointment with Child Table

**Source Schema:**
```sql
CREATE TABLE Appointments (
  AppointmentId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
  PatientId INT NOT NULL,
  AppointmentDate DATETIME NOT NULL,
  Status VARCHAR(20) NOT NULL,
  ServiceType VARCHAR(50),
  Duration INT  -- in minutes
)

CREATE TABLE AppointmentParticipants (
  ParticipantId INT PRIMARY KEY IDENTITY(1,1),
  AppointmentId UNIQUEIDENTIFIER NOT NULL,
  PractitionerId INT,
  Role VARCHAR(50),
  Status VARCHAR(20)
)
```

**Mapping Analysis:**

**Appointments Table:**
| Custom Field | FHIR Element Path | Mapping Type | Transformation/Notes | Confidence |
|--------------|-------------------|--------------|---------------------|------------|
| AppointmentId | N/A | PrimaryKey | GUID for IResourceEntity<Guid> | High |
| PatientId | Appointment.participant.actor | Transformed | Reference to Patient/{id} | High |
| AppointmentDate | Appointment.start | Direct | DateTime with timezone | High |
| Status | Appointment.status | Transformed | Map to FHIR status codes | High |
| ServiceType | Appointment.serviceType | Transformed | CodeableConcept | Medium |
| Duration | Appointment.minutesDuration | Direct | Positive integer | High |

**AppointmentParticipants Table:**
| Custom Field | FHIR Element Path | Mapping Type | Transformation/Notes | Confidence |
|--------------|-------------------|--------------|---------------------|------------|
| ParticipantId | N/A | ChildTable | Not mapped - internal DB use | High |
| AppointmentId | N/A | ChildTable | FK for joining | High |
| PractitionerId | Appointment.participant.actor | Transformed | Reference to Practitioner/{id} | High |
| Role | Appointment.participant.type | Transformed | CodeableConcept | Medium |
| Status | Appointment.participant.status | Transformed | FHIR participant status | High |

**Sample FHIR Instance:**
```json
{
  "resourceType": "Appointment",
  "id": "appt-456",
  "status": "booked",
  "serviceType": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/service-type",
      "code": "124",
      "display": "General Practice"
    }]
  }],
  "start": "2024-02-15T10:00:00+08:00",
  "minutesDuration": 30,
  "participant": [
    {
      "actor": {
        "reference": "Patient/123",
        "display": "John Tan"
      },
      "status": "accepted"
    },
    {
      "actor": {
        "reference": "Practitioner/789",
        "display": "Dr. Sarah Lim"
      },
      "type": [{
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
          "code": "PPRF",
          "display": "Primary Performer"
        }]
      }],
      "status": "accepted"
    }
  ]
}
```

### Example 3: Lab Results with Extensions

**Source Schema:**
```sql
CREATE TABLE LabResults (
  ResultId INT PRIMARY KEY IDENTITY(1,1),
  PatientId INT NOT NULL,
  TestCode VARCHAR(20) NOT NULL,
  TestName NVARCHAR(200),
  ResultValue DECIMAL(18, 4),
  ResultUnit VARCHAR(20),
  ReferenceRangeLow DECIMAL(18, 4),
  ReferenceRangeHigh DECIMAL(18, 4),
  ObservedDateTime DATETIME NOT NULL,
  Status VARCHAR(20),
  -- Custom fields
  LabEquipmentId VARCHAR(50),
  TechnicianId INT,
  VerifiedDateTime DATETIME,
  InternalNotes NVARCHAR(MAX)
)
```

**Mapping Analysis:**

| Custom Field | FHIR Element Path | Mapping Type | Transformation/Notes | Confidence |
|--------------|-------------------|--------------|---------------------|------------|
| ResultId | N/A | PrimaryKey | Integer PK for IResourceEntity<int> | High |
| PatientId | Observation.subject | Transformed | Reference to Patient/{id} | High |
| TestCode | Observation.code.coding.code | Direct | LOINC code | High |
| TestName | Observation.code.text | Direct | Display text | High |
| ResultValue | Observation.valueQuantity.value | Direct | Decimal value | High |
| ResultUnit | Observation.valueQuantity.unit | Direct | UCUM unit | High |
| ReferenceRangeLow | Observation.referenceRange.low | Direct | Quantity | High |
| ReferenceRangeHigh | Observation.referenceRange.high | Direct | Quantity | High |
| ObservedDateTime | Observation.effectiveDateTime | Direct | DateTime with TZ | High |
| Status | Observation.status | Transformed | Map to FHIR status | High |
| LabEquipmentId | Extension | Extension | Custom extension for device | Medium |
| TechnicianId | Observation.performer | Transformed | Reference to Practitioner | High |
| VerifiedDateTime | Extension | Extension | Custom verification extension | Medium |
| InternalNotes | N/A | NotMappable | Internal use only | High |

**Extension Definitions Needed:**
```json
{
  "url": "https://fhir.synapxe.sg/StructureDefinition/lab-equipment-id",
  "title": "Lab Equipment Identifier",
  "valueType": "string"
}

{
  "url": "https://fhir.synapxe.sg/StructureDefinition/result-verified-datetime",
  "title": "Result Verification DateTime",
  "valueType": "dateTime"
}
```

**Sample FHIR Instance:**
```json
{
  "resourceType": "Observation",
  "id": "obs-789",
  "extension": [
    {
      "url": "https://fhir.synapxe.sg/StructureDefinition/lab-equipment-id",
      "valueString": "EQUIP-12345"
    },
    {
      "url": "https://fhir.synapxe.sg/StructureDefinition/result-verified-datetime",
      "valueDateTime": "2024-01-15T16:30:00+08:00"
    }
  ],
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "2339-0",
      "display": "Glucose [Mass/volume] in Blood"
    }],
    "text": "Blood Glucose"
  },
  "subject": {
    "reference": "Patient/123"
  },
  "effectiveDateTime": "2024-01-15T14:00:00+08:00",
  "performer": [{
    "reference": "Practitioner/tech-456"
  }],
  "valueQuantity": {
    "value": 5.6,
    "unit": "mmol/L",
    "system": "http://unitsofmeasure.org",
    "code": "mmol/L"
  },
  "referenceRange": [{
    "low": {
      "value": 3.9,
      "unit": "mmol/L"
    },
    "high": {
      "value": 6.1,
      "unit": "mmol/L"
    }
  }]
}
```

**Unmappable Fields:**
- **InternalNotes**: Contains technical/administrative notes not suitable for clinical interoperability
- **Recommendation**: Store in separate audit table or use Provenance resource for full audit trail

## Common Pitfalls and Solutions

### Pitfall 1: Treating Primary Keys as Identifiers
**Problem:** Mapping database PK to FHIR identifier
**Solution:** Use PK only for IResourceEntity<T>, create separate identifier fields

### Pitfall 2: Ignoring Cardinality
**Problem:** Mapping single field to array type without considering 0..1 vs 0..*
**Solution:** Analyze source data cardinality, use appropriate FHIR element

### Pitfall 3: Over-using Extensions
**Problem:** Creating extensions for data that fits standard elements
**Solution:** Thoroughly check FHIR spec before creating extensions

### Pitfall 4: Losing Data Precision
**Problem:** Truncating decimals, losing timezone information
**Solution:** Document precision requirements, preserve original data

### Pitfall 5: Incorrect CodeableConcept Mapping
**Problem:** Storing only code without system or display
**Solution:** Always include system, code, and display in coding array

### Pitfall 6: Forgetting Regional Context
**Problem:** Using US Core profiles in Singapore deployment
**Solution:** Use base FHIR resources, avoid region-specific profiles

---

**This reference complements the main SKILL.md and provides detailed patterns for complex mapping scenarios.**
