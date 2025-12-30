# FHIR Project Setup Skill - Architecture and Best Practices

This document explains how the fhir-project-setup skill follows Claude Code best practices.

## File Structure

```
fhir-project-setup/
├── SKILL.md                        # Main skill file (477 lines - under 500 limit)
├── ARCHITECTURE.md                 # This file - architectural overview
├── mode-b-add-features.md         # Detailed Mode B instructions (progressive disclosure)
├── templates/
│   ├── setup-project.sh.md        # Bash script template for creating new projects
│   └── add-features.sh.md         # Bash script template for adding features
└── examples/
    ├── sample-configurations.md    # Example project configurations
    └── add-features-examples.md    # Real-world feature addition scenarios
```

## Design Principles

### 1. Progressive Disclosure (500-Line Rule)

**Goal**: Keep SKILL.md under 500 lines for optimal Claude Code performance

**Implementation**:
- SKILL.md: 477 lines ✅
- Core instructions and navigation in main file
- Detailed Mode B steps moved to `mode-b-add-features.md`
- Examples moved to separate files in `examples/`
- Templates stored in `templates/` directory

### 2. Multi-Mode Architecture

**Two Modes**:
1. **Mode A: Create New Project** - Scaffold from scratch using dotnet templates
2. **Mode B: Add Features** - Modify existing projects to enable features

**Mode Detection (Step 0)**:
```
Check for FHIR Engine project indicators:
├─ *.csproj files with Ihis.FhirEngine references
├─ fhirengine.json configuration file
└─ Program.cs with FHIR Engine setup

If found → Mode B (Add Features)
If not found → Mode A (Create New Project)
```

### 3. Ask-Show-Confirm-Execute Pattern

**Workflow for Mode A (Create New)**:
1. **Ask**: Use AskUserQuestion to collect preferences (5 questions)
2. **Show**: Display configuration summary
3. **Confirm**: Ask user to approve before proceeding
4. **Execute**: Generate and run bash script
5. **Guide**: Provide next steps and troubleshooting

**Workflow for Mode B (Add Features)**:
1. **Detect**: Scan project for current features
2. **Ask**: Show available features (multi-select)
3. **Show**: Display planned changes
4. **Confirm**: Ask user to approve
5. **Execute**: Run feature addition script
6. **Verify**: Build project to ensure changes work
7. **Guide**: Provide feature-specific configuration steps

### 4. Template-Based Script Generation

**Why Templates?**:
- Keeps complex bash logic out of SKILL.md
- Easier to maintain and version control
- Saves context by referencing external files
- Allows for detailed script logic without cluttering instructions

**Template Flow**:
```
SKILL.md (instructions)
    ↓
Read template from templates/*.sh.md
    ↓
Replace placeholders: {SOLUTION_NAME}, {DB_STORE}, {FHIR_VERSION}, etc.
    ↓
Write to /tmp/fhir-{operation}-{timestamp}.sh
    ↓
Make executable and execute
    ↓
Monitor output and verify
```

### 5. YAML Frontmatter Design

```yaml
name: fhir-project-setup                        # Kebab-case identifier
displayName: FHIR Project Setup                 # Human-readable name
description: Create new FHIR Engine Web API projects or add features...
version: 1.0.0                                  # Semantic versioning
triggers:                                       # Natural language triggers
  - "create a new fhir project"                # Mode A triggers
  - "setup fhir web api"
  - "enable redis in fhir project"             # Mode B triggers
  - "add swagger to fhir api"
examples:                                       # Concrete usage examples
  - query: "User prompt example"
    description: "What skill does"
```

**Key Design Decisions**:
- **description**: Includes concrete keywords (Redis, OpenAPI, Audit) for better discoverability
- **triggers**: Covers both modes (create new + add features)
- **examples**: Shows both creation and modification scenarios

### 6. Feature Detection Strategy

For Mode B, detect currently enabled features by checking:

| Feature | Detection Method |
|---------|------------------|
| Redis | `Ihis.FhirEngine.Caching.Redis` package OR Redis config in appsettings.json |
| OpenAPI | `Swashbuckle.AspNetCore` package OR Swagger in Program.cs |
| OpenTelemetry | `OpenTelemetry.*` package references |
| Audit | `Ihis.FhirEngine.Audit` package reference |
| CORS | CORS configuration in Program.cs |
| Test Project | Test project in solution file |

**Implementation**: Use Glob/Grep to search files, parse results, display status to user

### 7. Error Handling and Verification

**Pre-Execution Checks**:
- Prerequisites section lists required tools
- Bash script includes Step 0: Check Prerequisites
- Validates .NET SDK, NuGet source, templates, Git

**Post-Execution Verification**:
- Run `dotnet build` after all changes
- Check for build errors
- Provide troubleshooting guidance if failures occur

**Idempotent Operations**:
- Scripts check if features already enabled
- Avoid duplicate package additions
- Warn user if configuration already exists

### 8. User Interaction via AskUserQuestion

**Structure**:
```markdown
**Question N: Human-Readable Header**
- Header: "Short Label"          # Max 12 chars, shown as chip/tag
- Question: "Full question?"      # Clear, specific question
- Options:                        # 2-4 options
  - label: "Option (Recommended)" # Concise, actionable
    description: "Explanation..."  # Context and tradeoffs
- Multi-select: true/false        # Single or multiple choices
```

**Best Practices Implemented**:
- Clear, specific questions
- Detailed descriptions explaining tradeoffs
- "(Recommended)" tags for best practices
- Multi-select for features (Question 5, Mode B)
- Progressive questions (build on previous answers)

### 9. Supporting Files Organization

**templates/**:
- `setup-project.sh.md`: New project creation script (210 lines)
- `add-features.sh.md`: Feature addition script (280 lines)
- Both include usage notes and variable documentation

**examples/**:
- `sample-configurations.md`: 5 common project configurations
- `add-features-examples.md`: 6 real-world feature addition scenarios
- Includes troubleshooting and best practices

**Naming Convention**:
- Descriptive names (`mode-b-add-features.md` not `mode-b.md`)
- Kebab-case for files
- Grouped by purpose (templates vs examples vs reference)

### 10. Configuration Reference

Located at end of SKILL.md:
- Database Store Options (table)
- FHIR Versions (R4 vs R5)
- Framework Versions (net8.0 vs net9.0)
- Aspire Versions

**Purpose**: Quick lookup without cluttering main instructions

## Tool Usage Strategy

### File Operations
- **Glob**: Find .csproj, .sln files
- **Grep**: Search for package references, configuration patterns
- **Read**: View file contents for analysis

### Code Modification
- **Bash**: Primary tool for modifications (dotnet commands, sed for file edits)
- **Write**: Generate bash scripts from templates
- **Edit**: Not used directly - bash scripts handle modifications

### Why Bash Over Direct Edit?
- Bash scripts can handle complex logic (conditionals, loops)
- Can use sed for context-aware modifications
- Built-in error handling and verification
- Easier to test independently
- Familiar to .NET developers

### Command Execution
- `dotnet add package`: Add NuGet packages
- `dotnet build`: Verify changes
- `dotnet sln add`: Add projects to solution
- `git init/add/commit`: Version control initialization
- `sed`: In-place file modifications

## Testing Strategy

Located in `/tests/`:
- `test_installation.py`: Verify skill installation
- `test_skill_content.py`: Validate SKILL.md structure
- `test_integration.py`: End-to-end project creation tests

**Coverage**:
- 21 automated tests
- Installation verification
- Content structure validation
- Template syntax checking
- Script generation and execution

## Maintenance Guidelines

### Updating Templates
1. Modify template in `templates/*.sh.md`
2. Test with sample project
3. Update documentation if new variables added
4. Run integration tests

### Adding New Features
1. Add detection logic to mode-b-add-features.md
2. Update add-features.sh.md template
3. Add example to add-features-examples.md
4. Update triggers in YAML frontmatter
5. Test feature addition on sample project

### Keeping SKILL.md Under 500 Lines
1. Move detailed implementation to supporting files
2. Keep only essential instructions in SKILL.md
3. Use references to external files
4. Check line count: `wc -l SKILL.md` (target: <500)

## Performance Optimizations

1. **Progressive Disclosure**: Main file under 500 lines
2. **Template References**: Complex scripts in external files
3. **Example Separation**: Use cases in dedicated files
4. **Lazy Loading**: Claude reads supporting files only when needed

## Compliance with Claude Code Best Practices

✅ **SKILL.md under 500 lines** (477 lines)
✅ **Progressive disclosure** (detailed content in supporting files)
✅ **Clear YAML frontmatter** (triggers, description, examples)
✅ **Multi-file structure** (templates, examples, reference)
✅ **Template-based script generation** (saves context)
✅ **Ask-Show-Confirm-Execute pattern** (user-friendly workflow)
✅ **Error handling and verification** (prerequisites, build checks)
✅ **Comprehensive examples** (real-world scenarios)
✅ **Automated testing** (21 tests)
✅ **Clear documentation** (this file + TESTING.md)

## Future Enhancements

Potential improvements:
1. Add interactive feature detection (scan and suggest missing features)
2. Support for more databases (MySQL, MongoDB)
3. Cloud deployment templates (Azure, AWS)
4. Docker/containerization support
5. CI/CD pipeline generation
6. Migration helpers (upgrade FHIR versions, switch databases)

## References

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills.md)
- [TESTING.md](../../../TESTING.md) - Test suite documentation
- [templates/setup-project.sh.md](templates/setup-project.sh.md) - New project template
- [templates/add-features.sh.md](templates/add-features.sh.md) - Feature addition template
- [examples/add-features-examples.md](examples/add-features-examples.md) - Usage examples
- [CLAUDE.md](../../../CLAUDE.md) - Repository guidance
