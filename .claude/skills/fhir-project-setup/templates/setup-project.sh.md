# FHIR Engine Project Setup Script

This template generates a bash script to create a new FHIR Engine Web API project.

## Template Variables

- `{SOLUTION_NAME}`: Base name of the solution (e.g., "MyFhirApi")
- `{DB_STORE}`: Database store type (None, Document, Relational, Custom, Remote, RemoteCustom, DocumentPg, RelationalPg, CustomPg)
- `{FHIR_VERSION}`: FHIR version (R4, R5)
- `{FRAMEWORK}`: Target framework (net8.0, net9.0, net10.0)
- `{ASPIRE_VERSION}`: .NET Aspire version (9.5.2, 9.3.1, Disable)
- `{INCLUDE_TEST}`: Include test project (true/false)
- `{REDIS}`: Enable Redis caching (true/false)
- `{OPENAPI}`: Enable OpenAPI/Swagger (true/false)
- `{OTEL}`: Enable OpenTelemetry (true/false)
- `{AUDIT}`: Enable audit logging (true/false)
- `{CORS}`: Enable CORS (true/false)

## Generated Script

```bash
#!/bin/bash
set -e  # Exit on error

# Configuration
SOLUTION_NAME="{SOLUTION_NAME}"
DB_STORE="{DB_STORE}"
FHIR_VERSION="{FHIR_VERSION}"
FRAMEWORK="{FRAMEWORK}"
ASPIRE_VERSION="{ASPIRE_VERSION}"
INCLUDE_TEST={INCLUDE_TEST}
REDIS={REDIS}
OPENAPI={OPENAPI}
OTEL={OTEL}
AUDIT={AUDIT}
CORS={CORS}

# Derived values
FINAL_SOLUTION_NAME="${SOLUTION_NAME}.${FHIR_VERSION}.${DB_STORE}"
BASE_PATH=$(pwd)
PROJECT_PATH="${BASE_PATH}/${FINAL_SOLUTION_NAME}"

echo "📂 Creating FHIR Engine project: $FINAL_SOLUTION_NAME"
echo "   Database Store: $DB_STORE"
echo "   FHIR Version: $FHIR_VERSION"
echo "   Framework: $FRAMEWORK"
echo "   Aspire Version: $ASPIRE_VERSION"
echo "   Include Test: $INCLUDE_TEST"
echo "   Redis: $REDIS | OpenAPI: $OPENAPI | OpenTelemetry: $OTEL"
echo "   Audit: $AUDIT | CORS: $CORS"
echo ""

# Step 0: Check Prerequisites
echo "🔍 Checking prerequisites..."

# Check .NET SDK
if ! command -v dotnet &> /dev/null; then
    echo "❌ Error: .NET SDK not found"
    echo "Please install .NET 8.0 SDK or later from https://dotnet.microsoft.com/download"
    exit 1
fi

# Check NuGet source
echo "   Checking Synapxe NuGet source..."
NUGET_SOURCES=$(dotnet nuget list source 2>&1)
if ! echo "$NUGET_SOURCES" | grep -q "packages.hip.synapxe.sg"; then
    echo "⚠️  Warning: Synapxe NuGet source not configured"
    echo ""
    echo "To add the NuGet source, run:"
    echo "  dotnet nuget add source https://packages.hip.synapxe.sg/artifactory/api/nuget/v3/nuget-main/index.json --name SynapxeNuGet"
    echo ""
    read -p "Continue without Synapxe NuGet source? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check FHIR Engine template
echo "   Checking FHIR Engine template..."
TEMPLATE_CHECK=$(dotnet new list 2>&1 | grep -i "fhirengine-webapi" || true)
if [ -z "$TEMPLATE_CHECK" ]; then
    echo "❌ Error: FHIR Engine WebAPI template not found"
    echo ""
    echo "Please install the template:"
    echo "  Latest version:"
    echo "    dotnet new install Ihis.FhirEngine.WebApiTemplate.CSharp"
    echo ""
    echo "  Specific version (e.g., 5.0.1):"
    echo "    dotnet new install Ihis.FhirEngine.WebApiTemplate.CSharp@5.0.1"
    echo ""
    exit 1
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo "⚠️  Warning: Git not found - repository initialization will be skipped"
    GIT_AVAILABLE=false
else
    GIT_AVAILABLE=true
fi

echo "✅ Prerequisites check completed"
echo ""

# Step 1: Create project folder
echo "📂 Creating project folder at $PROJECT_PATH ..."
mkdir -p "$PROJECT_PATH"
cd "$PROJECT_PATH"

# Step 2: Run dotnet template
echo "🚀 Running dotnet template..."

# Build dotnet command with parameters
DOTNET_CMD="dotnet new fhirengine-webapi --dbstore=\"$DB_STORE\" --fhirversion=\"$FHIR_VERSION\" --framework=\"$FRAMEWORK\" --aspireversion=\"$ASPIRE_VERSION\""

# Add optional parameters
if [ "$INCLUDE_TEST" = true ]; then
    DOTNET_CMD="$DOTNET_CMD --includetest"
else
    DOTNET_CMD="$DOTNET_CMD --includetest=false"
fi

if [ "$REDIS" = true ]; then
    DOTNET_CMD="$DOTNET_CMD --redis"
fi

if [ "$OPENAPI" = true ]; then
    DOTNET_CMD="$DOTNET_CMD --openapi"
fi

if [ "$OTEL" = true ]; then
    DOTNET_CMD="$DOTNET_CMD --otel"
fi

if [ "$AUDIT" = true ]; then
    DOTNET_CMD="$DOTNET_CMD --audit"
fi

if [ "$CORS" = true ]; then
    DOTNET_CMD="$DOTNET_CMD --cors"
fi

# Execute the command
eval $DOTNET_CMD

if [ $? -ne 0 ]; then
    echo "❌ Error: dotnet template creation failed"
    echo ""
    echo "Please ensure:"
    echo "  1. FHIR Engine WebAPI template is installed:"
    echo "     dotnet new install Ihis.FhirEngine.WebApiTemplate.CSharp"
    echo ""
    echo "  2. Synapxe NuGet source is configured:"
    echo "     dotnet nuget add source https://packages.hip.synapxe.sg/artifactory/api/nuget/v3/nuget-main/index.json --name SynapxeNuGet"
    echo ""
    exit 1
fi

# Step 3: Create solution and add projects
echo "🎯 Creating solution and adding projects..."
if [ ! -f "$FINAL_SOLUTION_NAME.sln" ]; then
    dotnet new sln -n "$FINAL_SOLUTION_NAME"
fi

# Add all csproj files to the solution
find "$PROJECT_PATH" -name "*.csproj" | while read csproj; do
    dotnet sln "$FINAL_SOLUTION_NAME.sln" add "$csproj"
done

# Step 4: Initialize Git
if [ "$GIT_AVAILABLE" = true ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: FHIR Engine project setup"
else
    echo "⏭️  Skipping Git initialization (Git not available)"
fi

# Return to original directory
cd "$BASE_PATH"

echo ""
echo "✅ Project $FINAL_SOLUTION_NAME created successfully!"
echo "📁 Location: $PROJECT_PATH"
echo ""
echo "Configuration:"
echo "   Database Store: $DB_STORE"
echo "   FHIR Version: $FHIR_VERSION"
echo "   Framework: $FRAMEWORK"
echo "   Aspire Version: $ASPIRE_VERSION"
echo ""
echo "Features Enabled:"
echo "   Test Project: $INCLUDE_TEST"
echo "   Redis: $REDIS"
echo "   OpenAPI/Swagger: $OPENAPI"
echo "   OpenTelemetry: $OTEL"
echo "   Audit Logging: $AUDIT"
echo "   CORS: $CORS"
echo ""
echo "Next steps:"
echo "  cd $FINAL_SOLUTION_NAME"
echo "  dotnet build"
echo "  dotnet run"
echo ""
echo "Access the API:"
echo "  Metadata: http://localhost:5000/metadata"
echo "  Swagger:  http://localhost:5000/swagger (if enabled)"
```

## Usage Notes

1. **Prerequisites**:

   a. **Synapxe NuGet Source** must be configured:
   ```bash
   dotnet nuget add source https://packages.hip.synapxe.sg/artifactory/api/nuget/v3/nuget-main/index.json --name SynapxeNuGet
   ```

   b. **FHIR Engine WebAPI Template** must be installed:
   ```bash
   # Latest stable version
   dotnet new install Ihis.FhirEngine.WebApiTemplate.CSharp

   # Specific version (e.g., 5.0.1)
   dotnet new install Ihis.FhirEngine.WebApiTemplate.CSharp@5.0.1
   ```

   c. **Git** (optional): For version control initialization

   The script automatically checks for these prerequisites and provides helpful error messages if they are missing.

2. **Database Store Options**:
   - `None`: In-memory store (testing only)
   - `Document`: Azure Cosmos DB / DynamoDB (document store)
   - `Relational`: SQL Server (relational)
   - `DocumentPg`: PostgreSQL (document store with JSONB)
   - `RelationalPg`: PostgreSQL (relational)
   - `Custom`: Custom data store implementation
   - `Remote`: Remote FHIR server

3. **FHIR Version**: R4 (R4B) or R5

4. **Framework Versions**:
   - `net8.0`: .NET 8.0 LTS (recommended)
   - `net9.0`: .NET 9.0 STS
   - `net10.0`: .NET 10.0 (if available)

5. **Aspire Integration**:
   - `9.5.2` or `9.3.1`: Include .NET Aspire orchestration
   - `Disable`: No Aspire integration

6. **Optional Features**:
   - **Test Project** (`--includetest`): BDD integration tests
   - **Redis** (`--redis`): Distributed caching
   - **OpenAPI** (`--openapi`): Swagger documentation
   - **OpenTelemetry** (`--otel`): Distributed tracing
   - **Audit** (`--audit`): Audit logging for compliance
   - **CORS** (`--cors`): Cross-origin resource sharing
