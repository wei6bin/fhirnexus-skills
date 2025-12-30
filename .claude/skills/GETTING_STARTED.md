# Getting Started with FHIR Engine Claude Skills

## Quick Start for Developers

These skills help you build FHIR APIs using the FHIR Engine framework (Ihis.FhirEngine NuGet packages).

## Installation

### Option 1: Get Skills from FHIR Engine Package

If the skills are distributed with FHIR Engine, you may find them in:
- NuGet package content files
- FHIR Engine GitHub repository
- FHIR Engine documentation site

### Option 2: Manual Copy

Copy the `.claude/skills/` directory to your FHIR API project:

```bash
# In your FHIR API project root
mkdir -p .claude/skills/

# Copy the three skill directories
cp -r /path/to/fhir-engine-skills/fhir-config-troubleshooting .claude/skills/
cp -r /path/to/fhir-engine-skills/handler-patterns .claude/skills/
cp -r /path/to/fhir-engine-skills/fhir-errors-debugger .claude/skills/
```

### Option 3: Git Submodule (for teams)

If your team shares skills via git:

```bash
# Add as submodule
git submodule add <skills-repo-url> .claude/skills

# Team members can then pull with:
git submodule update --init
```

Once installed, skills automatically activate when you open your project in Claude Code. No additional configuration needed!

## Try It Now

Open Claude Code and ask these questions to test the skills:

### Test Configuration Help
```
"I'm getting an error that my handler isn't registered. Here's my fhirengine.json: ..."
```

### Test Handler Implementation
```
"How do I create a Read handler for the Patient resource?"
```

### Test Error Debugging
```
"I'm getting this error: 'No handler found for interaction type Read'. What does this mean?"
```

## Common Developer Scenarios

### Scenario 1: Setting Up a New FHIR API

**Ask Claude:**
```
"I want to create a new FHIR API that supports Patient resources with PostgreSQL.
What do I need in my configuration?"
```

**Claude will provide:**
- Complete fhirengine.json configuration
- Connection string setup in appsettings.json
- Required NuGet packages
- Handler registration steps

---

### Scenario 2: Implementing Custom Business Logic

**Ask Claude:**
```
"I need to validate that a Patient has a valid national ID before creating the record.
How do I implement this?"
```

**Claude will provide:**
- PreCRUD validation handler example
- Handler signature and attributes
- Configuration for registering the handler
- Error handling best practices

---

### Scenario 3: Debugging a Confusing Error

**Ask Claude:**
```
"My API returns 500 Internal Server Error when I try to GET /Patient/123.
The logs show 'InvalidHandlerSignatureException'. What's wrong?"
```

**Claude will:**
- Explain what InvalidHandlerSignatureException means
- Ask to see your handler code
- Identify the signature issue
- Provide the corrected handler code

---

### Scenario 4: Migrating from SQL Server to DynamoDB

**Ask Claude:**
```
"I want to migrate my data store from SQL Server to DynamoDB + S3.
What changes do I need to make?"
```

**Claude will provide:**
- New data store configuration
- Required packages
- Migration considerations
- Testing approach

---

## How Skills Help with Common Pain Points

### Pain Point: "I don't understand the error message"

**Before Skills:**
```
Error: "Unable to resolve service for type 'IFhirDataStore'"
Developer: *Confused, spends 2 hours searching*
```

**With Skills:**
```
Developer: "I'm getting 'Unable to resolve service for type IFhirDataStore'"
Claude: "This means your data store isn't configured in fhirengine.json.
        Here's what you need to add to Handlers.Repository: ..."
```

---

### Pain Point: "Configuration is too complex"

**Before Skills:**
```
Developer: *Opens fhirengine.json*
Developer: "What does UseSqlDocument mean? What's AcceptedTypes?"
Developer: *Reads through multiple docs, still confused*
```

**With Skills:**
```
Developer: "How do I configure a SQL Server data store?"
Claude: "Here's the exact configuration you need with explanations:
        - UseSqlDocument: true  // Uses JSON document storage
        - ConnectionString: 'Local'  // References appsettings.json
        - AcceptedTypes: ['Patient']  // Resources handled by this store"
```

---

### Pain Point: "I don't know the correct handler pattern"

**Before Skills:**
```
Developer: *Writes handler with wrong signature*
Developer: *Gets InvalidHandlerSignatureException*
Developer: *Trial and error for 1 hour*
```

**With Skills:**
```
Developer: "How do I create a Search handler for Appointment?"
Claude: "Here's the complete handler with the correct signature:
        [Complete working code example with explanations]"
```

---

## Team Best Practices

### 1. Ask Before Coding
Before implementing a feature, ask Claude for the pattern:
```
"How should I implement [feature] in FHIR Engine?"
```

### 2. Share Error Messages Fully
When debugging, paste the complete error:
```
"I'm getting this error: [full stack trace]
My configuration is: [relevant section]"
```

### 3. Ask for Explanations
Don't just copy-paste code, understand it:
```
"Why does this handler use IAsyncEnumerable instead of Task<List>?"
```

### 4. Request Best Practices
Ask for the recommended approach:
```
"What's the best way to handle pagination in search results?"
```

---

## Advanced Usage

### Creating Project-Specific Skills

If your project has custom patterns, add new skills:

1. Create a new directory: `.claude/skills/your-skill-name/`
2. Add a `SKILL.md` file with YAML frontmatter
3. Commit and share with the team

Example: Create a skill for your team's specific deployment process.

### Extending Existing Skills

You can enhance the existing skills:

1. Edit the SKILL.md file in the skill directory
2. Add project-specific examples or edge cases
3. Reference your team's internal documentation

---

## Troubleshooting Skills

### Skills Not Working?

**Check if skills are loaded:**
```
Ask Claude: "What skills are available?"
```

**Expected response:**
```
- fhir-config-troubleshooting
- handler-patterns
- fhir-errors-debugger
```

**If skills aren't listed:**
1. Ensure you're in the FhirEngine project directory
2. Check that `.claude/skills/` directory exists
3. Restart Claude Code

### Skill Not Triggering?

**Make your question more specific:**

Instead of:
```
"My code isn't working"
```

Use:
```
"I'm getting a handler not found error when calling GET /Patient/123"
```

---

## Examples from Real Scenarios

### Example 1: New Developer Onboarding

**Day 1 - Understanding the Framework:**
```
New Dev: "What's the difference between HandlerCategory.CRUD and HandlerCategory.PreCRUD?"
Claude: [Explains the pipeline phases with examples]
```

**Day 2 - First Implementation:**
```
New Dev: "I need to create endpoints for the Observation resource. How do I start?"
Claude: [Provides complete handler implementation + configuration]
```

**Day 3 - Debugging:**
```
New Dev: "My POST /Observation returns 500. Error: NullReferenceException at line 45"
Claude: [Identifies null check missing, provides fix]
```

**Result:** New developer productive in 3 days instead of 2 weeks

---

### Example 2: Production Issue Resolution

**Production Error:**
```
"GET /Patient?family=Smith returns 500 Internal Server Error"
Logs show: "SearchParamException: Invalid search parameter 'family'"
```

**Developer asks Claude:**
```
"I'm getting SearchParamException for parameter 'family' on Patient search.
This worked yesterday. What changed?"
```

**Claude responds:**
```
"This error means the search parameter isn't registered in your SearchParameters
configuration. Check:
1. Does your fhirengine.json include SearchParameters system plugin?
2. Is 'family' defined in your SearchParameter definitions?
3. Did a recent config change remove it?

Here's how to register it: [configuration example]"
```

**Result:** Issue resolved in 15 minutes instead of hours

---

## Feedback and Improvement

If you encounter scenarios not covered by these skills:

1. Document the issue
2. Ask Claude for help (it may find a solution using docs)
3. Consider creating a new skill for that scenario
4. Share with the team

## Next Steps

1. Open your project in Claude Code
2. Try asking one of the test questions above
3. When you encounter a real issue, ask Claude before searching docs
4. Share your experience with the team

The more you use skills, the more productive you'll become with FHIR Engine!
