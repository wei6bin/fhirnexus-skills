# Add Features to Existing FHIR Engine Project Script

This template generates a bash script to add features to an existing FHIR Engine Web API project.

## Template Variables

- `{PROJECT_DIR}`: Directory containing the FHIR Engine project
- `{PROJECT_NAME}`: Name of the project (from .csproj file)
- `{CSPROJ_FILE}`: Path to the .csproj file
- `{ENABLE_REDIS}`: Enable Redis caching (true/false)
- `{ENABLE_OPENAPI}`: Enable OpenAPI/Swagger (true/false)
- `{ENABLE_OTEL}`: Enable OpenTelemetry (true/false)
- `{ENABLE_AUDIT}`: Enable Audit logging (true/false)
- `{ENABLE_CORS}`: Enable CORS (true/false)
- `{ADD_TEST_PROJECT}`: Add test project (true/false)

## Generated Script

```bash
#!/bin/bash
set -e  # Exit on error

# Configuration
PROJECT_DIR="{PROJECT_DIR}"
PROJECT_NAME="{PROJECT_NAME}"
CSPROJ_FILE="{CSPROJ_FILE}"
ENABLE_REDIS={ENABLE_REDIS}
ENABLE_OPENAPI={ENABLE_OPENAPI}
ENABLE_OTEL={ENABLE_OTEL}
ENABLE_AUDIT={ENABLE_AUDIT}
ENABLE_CORS={ENABLE_CORS}
ADD_TEST_PROJECT={ADD_TEST_PROJECT}

echo "🔧 Adding features to FHIR Engine project: $PROJECT_NAME"
echo "   Project Directory: $PROJECT_DIR"
echo ""
echo "Features to add:"
[ "$ENABLE_REDIS" = true ] && echo "  ✓ Redis Caching"
[ "$ENABLE_OPENAPI" = true ] && echo "  ✓ OpenAPI/Swagger"
[ "$ENABLE_OTEL" = true ] && echo "  ✓ OpenTelemetry"
[ "$ENABLE_AUDIT" = true ] && echo "  ✓ Audit Logging"
[ "$ENABLE_CORS" = true ] && echo "  ✓ CORS"
[ "$ADD_TEST_PROJECT" = true ] && echo "  ✓ Test Project"
echo ""

cd "$PROJECT_DIR"

# Feature: Redis Caching
if [ "$ENABLE_REDIS" = true ]; then
    echo "📦 Adding Redis caching..."

    # Add NuGet packages
    dotnet add "$CSPROJ_FILE" package Ihis.FhirEngine.Caching.Redis
    dotnet add "$CSPROJ_FILE" package StackExchange.Redis

    # Update Program.cs - Add Redis services
    if ! grep -q "AddStackExchangeRedisCache" Program.cs; then
        # Find the line with AddFhirEngine and add Redis after it
        sed -i '/builder\.Services\.AddFhirEngine/a\
\
// Add Redis caching\
builder.Services.AddStackExchangeRedisCache(options =>\
{\
    options.Configuration = builder.Configuration.GetConnectionString("Redis");\
});' Program.cs
        echo "  ✓ Updated Program.cs"
    else
        echo "  ⚠️  Redis already configured in Program.cs"
    fi

    # Update appsettings.json - Add Redis connection string
    if ! grep -q '"Redis"' appsettings.json; then
        # Add Redis connection string to ConnectionStrings section
        if grep -q '"ConnectionStrings"' appsettings.json; then
            # ConnectionStrings section exists, add Redis to it
            sed -i '/"ConnectionStrings": {/a\
    "Redis": "localhost:6379",' appsettings.json
        else
            # Add ConnectionStrings section with Redis
            sed -i '/{/a\
  "ConnectionStrings": {\
    "Redis": "localhost:6379"\
  },' appsettings.json
        fi
        echo "  ✓ Updated appsettings.json"
    else
        echo "  ⚠️  Redis already configured in appsettings.json"
    fi

    echo "  ✅ Redis caching enabled"
    echo ""
fi

# Feature: OpenAPI/Swagger
if [ "$ENABLE_OPENAPI" = true ]; then
    echo "📦 Adding OpenAPI/Swagger..."

    # Add NuGet packages
    dotnet add "$CSPROJ_FILE" package Swashbuckle.AspNetCore
    dotnet add "$CSPROJ_FILE" package Ihis.FhirEngine.OpenApi

    # Update Program.cs - Add Swagger services
    if ! grep -q "AddSwaggerGen" Program.cs; then
        sed -i '/var app = builder\.Build/i\
// Add OpenAPI/Swagger\
builder.Services.AddEndpointsApiExplorer();\
builder.Services.AddSwaggerGen();\
' Program.cs
        echo "  ✓ Added Swagger services to Program.cs"
    else
        echo "  ⚠️  Swagger services already configured"
    fi

    # Add Swagger middleware
    if ! grep -q "UseSwagger" Program.cs; then
        sed -i '/var app = builder\.Build/a\
\
// Enable Swagger UI\
app.UseSwagger();\
app.UseSwaggerUI();' Program.cs
        echo "  ✓ Added Swagger middleware to Program.cs"
    else
        echo "  ⚠️  Swagger middleware already configured"
    fi

    echo "  ✅ OpenAPI/Swagger enabled"
    echo "  📍 Swagger UI will be available at: http://localhost:5000/swagger"
    echo ""
fi

# Feature: OpenTelemetry
if [ "$ENABLE_OTEL" = true ]; then
    echo "📦 Adding OpenTelemetry..."

    # Add NuGet packages
    dotnet add "$CSPROJ_FILE" package OpenTelemetry.Extensions.Hosting
    dotnet add "$CSPROJ_FILE" package OpenTelemetry.Instrumentation.AspNetCore
    dotnet add "$CSPROJ_FILE" package OpenTelemetry.Exporter.Console

    # Update Program.cs - Add OpenTelemetry
    if ! grep -q "AddOpenTelemetry" Program.cs; then
        sed -i '/builder\.Services\.AddFhirEngine/i\
// Add OpenTelemetry\
builder.Services.AddOpenTelemetry()\
    .WithTracing(tracerProviderBuilder =>\
    {\
        tracerProviderBuilder\
            .AddAspNetCoreInstrumentation()\
            .AddConsoleExporter();\
    });\
' Program.cs
        echo "  ✓ Updated Program.cs"
    else
        echo "  ⚠️  OpenTelemetry already configured"
    fi

    echo "  ✅ OpenTelemetry enabled"
    echo ""
fi

# Feature: Audit Logging
if [ "$ENABLE_AUDIT" = true ]; then
    echo "📦 Adding Audit Logging..."

    # Add NuGet package
    dotnet add "$CSPROJ_FILE" package Ihis.FhirEngine.Audit

    # Update Program.cs - Add Audit services
    if ! grep -q "AddFhirAudit" Program.cs; then
        sed -i '/builder\.Services\.AddFhirEngine/a\
\
// Add Audit logging\
builder.Services.AddFhirAudit(options =>\
{\
    options.EnableAuditLog = true;\
});' Program.cs
        echo "  ✓ Updated Program.cs"
    else
        echo "  ⚠️  Audit logging already configured in Program.cs"
    fi

    # Update appsettings.json - Add Audit configuration
    if ! grep -q '"Audit"' appsettings.json; then
        # Add Audit configuration to FhirEngine section
        if grep -q '"FhirEngine"' appsettings.json; then
            sed -i '/"FhirEngine": {/a\
    "Audit": {\
      "Enabled": true,\
      "LogToConsole": true\
    },' appsettings.json
        else
            sed -i '/{/a\
  "FhirEngine": {\
    "Audit": {\
      "Enabled": true,\
      "LogToConsole": true\
    }\
  },' appsettings.json
        fi
        echo "  ✓ Updated appsettings.json"
    else
        echo "  ⚠️  Audit configuration already exists in appsettings.json"
    fi

    echo "  ✅ Audit logging enabled"
    echo ""
fi

# Feature: CORS
if [ "$ENABLE_CORS" = true ]; then
    echo "📦 Adding CORS..."

    # Update Program.cs - Add CORS services
    if ! grep -q "AddCors" Program.cs; then
        sed -i '/var app = builder\.Build/i\
// Add CORS\
builder.Services.AddCors(options =>\
{\
    options.AddDefaultPolicy(policy =>\
    {\
        policy.WithOrigins(builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>())\
              .AllowAnyMethod()\
              .AllowAnyHeader();\
    });\
});\
' Program.cs
        echo "  ✓ Added CORS services to Program.cs"
    else
        echo "  ⚠️  CORS services already configured"
    fi

    # Add CORS middleware
    if ! grep -q "app.UseCors" Program.cs; then
        sed -i '/var app = builder\.Build/a\
\
// Enable CORS\
app.UseCors();' Program.cs
        echo "  ✓ Added CORS middleware to Program.cs"
    else
        echo "  ⚠️  CORS middleware already configured"
    fi

    # Update appsettings.json - Add CORS configuration
    if ! grep -q '"Cors"' appsettings.json; then
        sed -i '/{/a\
  "Cors": {\
    "AllowedOrigins": ["http://localhost:3000", "https://localhost:3001"]\
  },' appsettings.json
        echo "  ✓ Updated appsettings.json"
    else
        echo "  ⚠️  CORS configuration already exists"
    fi

    echo "  ✅ CORS enabled"
    echo ""
fi

# Feature: Test Project
if [ "$ADD_TEST_PROJECT" = true ]; then
    echo "📦 Adding Test Project..."

    # Check if test project already exists
    if [ -d "${PROJECT_NAME}.Tests" ]; then
        echo "  ⚠️  Test project ${PROJECT_NAME}.Tests already exists"
    else
        # Create test project
        dotnet new fhirengine-test -n "${PROJECT_NAME}.Tests" -o "${PROJECT_NAME}.Tests"

        # Add to solution if solution file exists
        SLN_FILE=$(find . -maxdepth 1 -name "*.sln" | head -n 1)
        if [ -n "$SLN_FILE" ]; then
            dotnet sln "$SLN_FILE" add "${PROJECT_NAME}.Tests/${PROJECT_NAME}.Tests.csproj"
            echo "  ✓ Added test project to solution"
        fi

        echo "  ✅ Test project created: ${PROJECT_NAME}.Tests"
    fi
    echo ""
fi

# Build project to verify changes
echo "🔨 Building project to verify changes..."
dotnet build "$CSPROJ_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All features added successfully!"
    echo ""
    echo "Modified files:"
    [ "$ENABLE_REDIS" = true ] || [ "$ENABLE_OPENAPI" = true ] || [ "$ENABLE_OTEL" = true ] || [ "$ENABLE_AUDIT" = true ] && echo "  • $PROJECT_NAME.csproj (NuGet packages)"
    [ "$ENABLE_REDIS" = true ] || [ "$ENABLE_OPENAPI" = true ] || [ "$ENABLE_OTEL" = true ] || [ "$ENABLE_AUDIT" = true ] || [ "$ENABLE_CORS" = true ] && echo "  • Program.cs (service configuration)"
    [ "$ENABLE_REDIS" = true ] || [ "$ENABLE_AUDIT" = true ] || [ "$ENABLE_CORS" = true ] && echo "  • appsettings.json (feature settings)"
    echo ""
    echo "Next steps:"
    echo "1. Review changes: git diff"
    echo "2. Update configuration values in appsettings.json as needed"
    echo "3. Test the application: dotnet run"
    [ "$ENABLE_REDIS" = true ] && echo "4. Configure Redis connection string in appsettings.json"
    [ "$ENABLE_OPENAPI" = true ] && echo "4. Access Swagger UI at: http://localhost:5000/swagger"
    echo ""
else
    echo ""
    echo "❌ Build failed. Please review the errors above."
    echo ""
    exit 1
fi
```

## Usage Notes

This script:
1. Adds NuGet packages for selected features
2. Updates Program.cs with service configuration
3. Updates appsettings.json with feature settings
4. Creates test project if requested
5. Builds project to verify changes

**Important**:
- The script uses `sed` to modify Program.cs and appsettings.json
- It checks if features are already enabled to avoid duplicates
- Always review changes with `git diff` before committing
- Update configuration values in appsettings.json as needed
