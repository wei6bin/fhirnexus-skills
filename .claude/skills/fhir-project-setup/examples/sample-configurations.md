# Sample FHIR Engine Project Configurations

This document provides example project configurations for common use cases.

## Example 1: Production-Ready API with Full Features

**Use Case**: Modern FHIR R5 API with all enterprise features

```
Solution Name: HealthcareAPI
Database Store: DocumentPg
FHIR Version: R5
Framework: net8.0
Aspire Version: 9.5.2
Features:
  - Include Test Project: Yes
  - Redis Caching: Yes
  - OpenAPI/Swagger: Yes
  - OpenTelemetry: Yes
  - Audit Logging: Yes
  - CORS: Yes
```

**Generated Project**: `HealthcareAPI.R5.DocumentPg`

**Features Enabled**:
- FHIR R5 compliance
- PostgreSQL with JSONB document storage
- .NET 8.0 LTS with Aspire orchestration
- BDD integration tests
- Redis distributed caching
- Swagger API documentation
- OpenTelemetry distributed tracing
- Audit logging for compliance
- CORS for web clients

---

## Example 2: Minimal Testing/Development API

**Use Case**: Quick prototype or local development

```
Solution Name: DevAPI
Database Store: None
FHIR Version: R5
Framework: net8.0
Aspire Version: Disable
Features:
  - Include Test Project: No
  - All other features: No
```

**Generated Project**: `DevAPI.R5.None`

**Features Enabled**:
- FHIR R5 compliance
- In-memory data store (no persistence)
- .NET 8.0 without Aspire
- Fast startup for testing
- Minimal dependencies

---

## Example 3: SQL Server Enterprise API with Audit

**Use Case**: Enterprise FHIR R4 API with compliance requirements

```
Solution Name: EnterpriseEHR
Database Store: Relational
FHIR Version: R4
Framework: net8.0
Aspire Version: Disable
Features:
  - Include Test Project: Yes
  - Audit Logging: Yes
  - OpenAPI/Swagger: Yes
  - All other features: No
```

**Generated Project**: `EnterpriseEHR.R4.Relational`

**Features Enabled**:
- FHIR R4 (R4B) compliance
- SQL Server relational storage
- No Aspire (traditional deployment)
- BDD integration tests
- Audit logging for compliance
- Swagger API documentation

---

## Example 4: API with Redis Caching & Observability

**Use Case**: High-performance FHIR API with distributed caching and monitoring

```
Solution Name: PerformanceAPI
Database Store: DocumentPg
FHIR Version: R5
Framework: net9.0
Aspire Version: 9.5.2
Features:
  - Include Test Project: Yes
  - Redis Caching: Yes
  - OpenTelemetry: Yes
  - OpenAPI/Swagger: Yes
  - Audit Logging: No
  - CORS: No
```

**Generated Project**: `PerformanceAPI.R5.DocumentPg`

**Features Enabled**:
- FHIR R5 compliance
- PostgreSQL JSONB document storage
- .NET 9.0 with Aspire orchestration
- Redis distributed caching for performance
- OpenTelemetry distributed tracing
- Swagger API documentation
- BDD integration tests

---

## Example 5: Custom Data Store with SQS Logging

**Use Case**: Custom backend integration with AWS SQS logging

```
Solution Name: CustomFhirAPI
Database Store: Custom
FHIR Version: R5
Framework: net8.0
Aspire Version: 9.5.2
Features:
  - Include Test Project: Yes
  - Audit Logging: Yes
  - OpenAPI/Swagger: Yes
  - CORS: Yes
  - Redis: No
  - OpenTelemetry: No
```

**Generated Project**: `CustomFhirAPI.R5.Custom`

**Features Enabled**:
- FHIR R5 compliance
- Custom IDataStore skeleton
- Audit logging foundation
- Swagger documentation
- CORS enabled
- BDD tests

**Post-Setup for SQS**:
1. Add AWS SDK: `dotnet add package AWSSDK.SQS`
2. Implement custom IDataStore with SQS integration
3. Configure SQS queue URL in appsettings.json
4. Add SQS logging middleware

---

## Configuration Matrix

| Database Store | Best For | Persistence | Cloud Provider |
|---------------|----------|-------------|----------------|
| `None` | Testing, prototypes | In-memory only | Any |
| `Document` | Azure Cosmos DB | JSON documents | Azure |
| `Relational` | SQL Server | Relational tables | Azure, On-prem |
| `DocumentPg` | PostgreSQL JSONB | JSON documents | AWS, GCP, On-prem |
| `RelationalPg` | PostgreSQL | Relational tables | AWS, GCP, On-prem |
| `Custom` | Legacy systems, custom backends | Custom implementation | Any |
| `Remote` | FHIR proxy/gateway | Remote FHIR server | Any |

## FHIR Version Selection

- **R4 (R4B)**: Most widely adopted, maximum interoperability (template uses R4 parameter for R4B)
- **R5**: Latest specification, new features (subscriptions, obligations)

## Framework Selection

- **net8.0** (Recommended): .NET 8.0 LTS - long-term support
- **net9.0**: .NET 9.0 STS - latest features
- **net10.0**: .NET 10.0 (if template supports it)

## Optional Features Guide

| Feature | Use When | Impact |
|---------|----------|--------|
| **Test Project** | Always recommended | Adds BDD integration tests, increases project size |
| **Redis** | Need caching, distributed scenarios | Requires Redis server, improves performance |
| **OpenAPI/Swagger** | API documentation, testing | Adds Swagger UI endpoint |
| **OpenTelemetry** | Need observability, tracing | Adds telemetry overhead, enables distributed tracing |
| **Audit Logging** | Compliance, security | Logs all FHIR operations, increases storage |
| **CORS** | Web/browser clients | Enables cross-origin requests |

## Aspire Integration

- **9.5.2** (latest): Best local dev experience, latest features
- **9.3.1**: Stable version
- **Disable**: Traditional deployment, no orchestration overhead
