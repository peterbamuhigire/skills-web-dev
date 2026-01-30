# 🤖 Custom Sub-Agents: Complete Development Guide

**Version**: 2.0 - Modular Edition
**Date**: January 2026
**Purpose**: Comprehensive guide for developing custom sub-agents with VS Code integration

---

## 📋 TABLE OF CONTENTS

### Core Architecture

1. **[Agent Folder Structure](01-agent-folder-structure.md)** - File organization and naming conventions
2. **[Agent Configuration & Documentation](02-agent-config-documentation.md)** - Config management and README standards
3. **[Entry Points & Patterns](03-entry-points-patterns.md)** - Clean interfaces and export strategies
4. **[Testing Tools & Frameworks](04-testing-tools.md)** - Unit tests, integration tests, and utilities

### Advanced Patterns

5. **[Advanced Orchestration Patterns](05-advanced-patterns.md)** - Chain of Responsibility, Strategy, Observer patterns
6. **[Parent & Sub-Agent Architecture](06-parent-sub-agent.md)** - Conductor agents and workflow orchestration
7. **[Project Organization & Registry](07-project-organization.md)** - Agent Registry, Factory patterns, and analytics

### Integration & Deployment

8. **[Integration & Deployment Patterns](08-integration-deployment.md)** - API gateways, containers, monitoring, and production deployment

### Decision Frameworks

- **[Skills vs Sub-Agents: Decision Matrix](#skills-vs-sub-agents-decision-framework)** - When to use static skills vs dynamic sub-agents

---

## 🎯 QUICK START

### For New Agent Developers

1. **Read Section 1** - Understand folder structure and file organization
2. **Read Section 2** - Learn configuration and documentation standards
3. **Read Section 3** - Master entry points and clean interfaces
4. **Read Section 4** - Set up testing frameworks and utilities

### For Advanced Users

5. **Read Section 5** - Implement complex orchestration patterns
6. **Read Section 6** - Build parent/sub-agent architectures
7. **Read Section 7** - Use registry and factory patterns for scalability
8. **Read Section 8** - Deploy to production with monitoring

### For Architects

- **Review the Decision Framework** below to choose between skills and sub-agents
- **Study Section 7** for enterprise-scale agent management
- **Implement Section 8** patterns for production deployment

---

## 🧠 SKILLS VS SUB-AGENTS: DECISION FRAMEWORK

**Critical Decision**: Choose the right architecture based on your use case to optimize token efficiency and development velocity.

---

## 📚 Quick Comparison

| Aspect              | SKILL                       | SUB-AGENT                |
| ------------------- | --------------------------- | ------------------------ |
| **What it is**      | Documented pattern/template | Autonomous agent         |
| **Cost**            | Read once, reuse forever    | Runs every time (tokens) |
| **Intelligence**    | Static instructions         | Dynamic decision-making  |
| **Reusability**     | Copy-paste into agents      | Called by conductor      |
| **When Used**       | "Here's HOW to do X"        | "Should we do X?"        |
| **Communication**   | None (just instructions)    | Parent ↔ Sub-agent       |
| **Decision Making** | Human decides               | Agent decides            |
| **Updates**         | Change skill once           | Each agent must update   |

---

## 🤔 The Real Question

```
SKILL: "Here's how to document a plan"
├─ Template structure
├─ Required sections
├─ Formatting guidelines
└─ Error handling steps

SUB-AGENT: "Should we document this plan? How? In what format?"
├─ Decides IF planning needed
├─ Decides HOW to execute
├─ Adapts based on context
└─ Handles special cases
```

---

## 💡 Example Scenario

### Your Current Situation

```
agents/planning-agent/agent.js
├─ Has code to create plan
├─ Has code to write to docs/plans/
└─ Uses skills/plan-documentation/ as reference
```

### DON'T Create a Sub-Agent If:

```javascript
// BAD: Redundant sub-agent
class DocumentationSubAgent {
  async documentPlan(plan) {
    // This just copies what PlanningAgent already does!
    // It's the SAME logic, running TWICE
    // Wastes tokens, adds complexity

    const template = this.loadTemplate(); // From skill
    const formatted = this.format(plan); // From skill
    const saved = this.save(formatted); // From skill
    return saved;
  }
}
```

### DO Create a Sub-Agent If:

```javascript
// GOOD: Sub-agent makes intelligent decisions
class DocumentationSubAgent {
  async evaluate(plan) {
    // This is DIFFERENT logic!

    // Decides IF documentation is needed
    if (plan.priority === "urgent" && plan.complexity === "high") {
      return {
        document: true,
        format: "detailed",
        urgency: "high",
      };
    }

    if (plan.status === "draft") {
      return {
        document: true,
        format: "template_only",
        urgency: "low",
      };
    }

    return {
      document: false,
      reason: "Not worth documenting",
    };
  }
}
```

---

## 🏗️ Three Valid Architectures

### Architecture 1: SKILL-BASED (Recommended for Simple Cases)

```
CONDUCTOR AGENT
    ↓
PLANNING AGENT
    ├─ Uses skill: docs/skills/plan-documentation/
    │  (Reads template, formats, saves)
    └─ No separate sub-agent needed

Token Cost: LOW
Complexity: LOW
Reusability: HIGH
```

**When**: Creating, documenting, saving plans is straightforward

```javascript
// In PlanningAgent
async createAndDocumentPlan(request) {
  // Create plan
  const plan = this.generateStrategy(request);

  // Use skill directly (no sub-agent)
  const skillContent = this.loadSkill('plan-documentation');
  const formatted = this.applyTemplate(plan, skillContent);

  // Save
  await this.savePlan(formatted);

  return plan;
}
```

---

### Architecture 2: SUB-AGENT FOR DECISION-MAKING (Recommended for Complex Cases)

```
CONDUCTOR AGENT
    ↓
    ├─ PLANNING AGENT (creates plan)
    │
    └─ DOCUMENTATION SUB-AGENT (decides HOW to document)
        └─ Uses skill: docs/skills/plan-documentation/
           (But makes intelligent decisions)

Token Cost: MEDIUM (one extra agent call)
Complexity: MEDIUM
Reusability: HIGH
```

**When**: Documentation needs intelligence (different formats, conditional saving, validation)

```javascript
// In DocumentationSubAgent
async smartDocument(plan) {
  // DECISION: How to document this plan?
  const decision = await this.analyzeNeed(plan);

  if (decision.format === 'detailed') {
    // Use full skill template
    const skillContent = this.loadSkill('plan-documentation/detailed');
    return this.applyTemplate(plan, skillContent);
  }

  if (decision.format === 'minimal') {
    // Use simplified skill template
    const skillContent = this.loadSkill('plan-documentation/minimal');
    return this.applyTemplate(plan, skillContent);
  }

  return null; // Don't document
}
```

---

### Architecture 3: SUB-AGENT FOR SPECIALIZATION (Only if Multiple Docs Needed)

```
CONDUCTOR AGENT
    ├─ PLANNING AGENT
    │
    ├─ DOCUMENTATION SUB-AGENT
    │  ├─ Uses skill: docs/skills/plan-documentation/
    │  ├─ Uses skill: docs/skills/approval-documentation/
    │  └─ Uses skill: docs/skills/archive-documentation/
    │
    └─ Could call multiple doc-related skills

Token Cost: MEDIUM-HIGH (extra agent, but centralizes doc logic)
Complexity: HIGH
Reusability: HIGH (all doc skills in one place)
```

**When**: You have MANY documentation needs that should be centralized

```javascript
class DocumentationSubAgent {
  // All doc skills centralized here

  async document(plan, context) {
    if (context === "planning") {
      return await this.documentPlan(plan);
    }

    if (context === "approval") {
      return await this.documentApproval(plan);
    }

    if (context === "archive") {
      return await this.documentArchive(plan);
    }
  }

  async documentPlan(plan) {
    const skill = this.loadSkill("plan-documentation");
    return this.apply(plan, skill);
  }

  async documentApproval(plan) {
    const skill = this.loadSkill("approval-documentation");
    return this.apply(plan, skill);
  }

  async documentArchive(plan) {
    const skill = this.loadSkill("archive-documentation");
    return this.apply(plan, skill);
  }
}
```

---

## 🤔 Decision Tree

```
Do you need to DOCUMENT a plan?
    ↓
Does it require DECISION-MAKING?
├─ NO  → Use SKILL directly
│        (In PlanningAgent or ConductorAgent)
│        Cost: 0 extra tokens
│
└─ YES → Does it need MULTIPLE SKILLS?
         ├─ NO  → Create SUB-AGENT
         │        Cost: 1 extra agent call (200-500 tokens)
         │        Benefit: Intelligent decisions
         │
         └─ YES → Create SUB-AGENT with multiple skills
                  Cost: 1 extra agent call
                  Benefit: Centralized doc logic
```

---

## 📊 Real Example: Your Apps

### MADUUKA: Planning Agent Creating Sales Strategy

**Option 1: SKILL-ONLY (Recommended)**

```javascript
// In PlanningAgent
async createSalesStrategy(request) {
  // Generate strategy
  const strategy = this.generateStrategy(request);

  // Use skill directly
  const planSkill = this.loadSkill('plan-documentation');
  const documented = this.format(strategy, planSkill);

  // Save
  await this.saveToFranchise(documented);

  return strategy;
}

// Cost: 0 extra tokens
// Complexity: Simple
```

**Option 2: SUB-AGENT (If logic is complex)**

```javascript
// In ConductorAgent
async orchestrate(request) {
  // Planning creates strategy
  const plan = await this.planning.createStrategy(request);

  // DocumentationSubAgent decides how to document
  const documented = await this.documentation.smartDocument({
    plan,
    franchise_id: request.franchise_id,
    priority: request.priority
  });

  return {plan, documented};
}

// DocumentationSubAgent
async smartDocument(input) {
  // Intelligent decision
  if (input.franchise_id === 'flagship') {
    // Detailed documentation
    const skill = this.loadSkill('plan-documentation/detailed');
  } else {
    // Quick documentation
    const skill = this.loadSkill('plan-documentation/quick');
  }

  return this.format(input.plan, skill);
}

// Cost: ~400 tokens for extra agent call
// Benefit: Intelligent decision-making
```

---

## ✅ Decision Matrix

### WHEN TO USE SKILL

✅ Simple, deterministic process
✅ Same every time
✅ No context-based decisions
✅ One standard template
✅ Reuse across many agents

**Example**: Basic plan documentation with standard template

---

### WHEN TO USE SUB-AGENT

✅ Complex decision-making needed
✅ Conditional logic ("if urgent, do X")
✅ Multiple formats/templates
✅ Needs to validate before saving
✅ Centralizes complex logic

**Example**:

```javascript
// Complex decision
if (plan.isUrgent() && plan.needsApproval()) {
  // Detailed docs + approval tracking
} else if (plan.isDraft()) {
  // Template-only docs
} else {
  // No docs
}
```

---

## 💰 Token Cost Analysis

### Scenario: PlanningAgent creates 10 plans

**Option 1: Skill-Only**

```
10 plans × PlanningAgent logic = 10 × 1500 tokens = 15,000 tokens
Skill loading (cached) = ~100 tokens
Total: ~15,100 tokens
```

**Option 2: Sub-Agent**

```
10 plans × PlanningAgent = 10 × 1500 = 15,000 tokens
10 plans × DocumentationAgent = 10 × 400 = 4,000 tokens
Skill loading (cached) = ~100 tokens
Total: ~19,100 tokens  ← 4,000 tokens MORE!
```

**Cost of complexity: ~4,000 extra tokens**

**Worth it if**:

- Logic is sufficiently complex (>200 lines of conditional code)
- Saves time in development/maintenance
- Provides measurable benefit (better docs, smarter decisions)

**NOT worth it if**:

- Just copying skill template
- No decision-making
- Same output every time

---

## 🎓 Your Specific Case

You have: `docs/skills/plan-documentation/`

**Questions to ask:**

1. **Does every plan get documented the same way?**
   - YES → Use SKILL directly
   - NO → Create SUB-AGENT

2. **Is documentation always needed?**
   - YES → Use SKILL directly
   - NO → Create SUB-AGENT (to decide)

3. **Does documentation require context awareness?**
   - NO → Use SKILL directly
   - YES → Create SUB-AGENT

4. **Will you use this skill with multiple agents?**
   - YES → Use SKILL directly (reuse across agents)
   - NO → Could use SUB-AGENT (centralize)

---

## 🏆 RECOMMENDATION FOR YOU

Based on typical scenarios:

### For MADUUKA:

```
Planning Agent
└─ Uses skill: docs/skills/plan-documentation/
   (directly, no sub-agent)

Reasoning:
- Plan documentation is deterministic
- Same template every time
- Could use with other agents too
```

### For MEDIC8:

```
Planning Agent
└─ IF complex decision logic needed:
   └─ Create DocumentationSubAgent
      └─ Uses multiple skills
         (care-plan docs, approval docs, etc.)

Reasoning:
- Medical plans have complex rules
- Different docs for different situations
- Centralize healthcare-specific logic
```

### For BRIGHTSOMA:

```
Curriculum Planning Agent
└─ Uses skill: docs/skills/lesson-plan-documentation/
   (directly)

Reasoning:
- Lesson plans follow standard template
- Documentation is deterministic
- Can reuse with other agents
```

---

## 📝 Summary Table

| Scenario                      | Use       | Reason                      |
| ----------------------------- | --------- | --------------------------- |
| Standard plan → standard docs | SKILL     | Simple, reusable, no tokens |
| Smart docs (urgency-aware)    | SUB-AGENT | Needs decision-making       |
| 5 different doc types         | SUB-AGENT | Centralize complexity       |
| Always same template          | SKILL     | No intelligence needed      |
| Conditional documentation     | SUB-AGENT | Decides IF and HOW          |

---

## 💡 The Right Way Forward

### For Your System

```
agents/
├── conductor-agent/
│   └─ Orchestrates work
│
├── planning-agent/
│   └─ Uses skill: docs/skills/plan-documentation/
│      (No separate sub-agent unless logic gets complex)
│
└── (Only create DocumentationSubAgent if:
    - Logic becomes >200 lines
    - Multiple doc types needed
    - Conditional decisions required)
```

### Cost-Benefit Calculation

```
Add DocumentationSubAgent if:

Benefits:
+ Better organized code
+ Reusable across multiple parents
+ Intelligent decisions

Costs:
- Extra agent call (~400 tokens per request)
- More complexity
- Harder to test

Break-even: When decision logic would be 500+ lines in PlanningAgent
```

---

## ✨ FINAL ANSWER TO YOUR QUESTION

**"Won't we waste tokens?"**

Yes, IF the sub-agent is just copying the skill template.

**NO, if the sub-agent:**

- Makes intelligent decisions
- Validates context
- Chooses between multiple skills
- Handles conditional logic
- Serves multiple parent agents

**Your skill is valuable** because:

- It's reusable documentation
- Other agents can use it
- It's the "how-to" manual

**A sub-agent makes sense only if:**

- You need "when to", "which version", "is this valid?"
- Decision logic is complex
- Multiple documentation strategies exist

**In your case**: Start with SKILL-ONLY. Add sub-agent later if complexity demands it.

---

## 💡 Rule of Thumb

If you can explain the documentation process in one paragraph, use a SKILL. If you need 10 paragraphs of conditional logic, use a SUB-AGENT.

---

## 🏗️ ARCHITECTURAL OVERVIEW

### Agent Ecosystem Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Static      │ │ Dynamic     │ │ Conductor   │           │
│  │ Skills      │ │ Sub-Agents  │ │ Agents      │           │
│  │ (VS Code)   │ │ (Runtime)   │ │ (Workflow)  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Agent       │ │ Factory     │ │ Registry    │           │
│  │ Registry    │ │ Pattern     │ │ (Management)│           │
│  │ (Discovery) │ │ (Creation)  │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ API Gateway │ │ CLI Tool    │ │ Monitoring  │           │
│  │ (HTTP)      │ │ (Command)   │ │ (Observability)│        │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Docker      │ │ Kubernetes  │ │ CI/CD       │           │
│  │ (Container) │ │ (Orchestration)│ (Automation)│         │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Patterns

1. **Registry Pattern** - Centralized agent discovery and management
2. **Factory Pattern** - Dynamic agent creation with configuration
3. **Conductor Pattern** - Orchestration of complex workflows
4. **Observer Pattern** - Event-driven agent communication
5. **Strategy Pattern** - Pluggable algorithms and behaviors

### Technology Stack

- **Runtime**: Node.js 18+ with ES6 modules
- **Testing**: Jest with coverage reporting
- **Deployment**: Docker + Kubernetes
- **Monitoring**: Prometheus + Grafana
- **API**: RESTful with OpenAPI specification
- **CLI**: Commander.js for command-line interface

---

## 📚 DEVELOPMENT WORKFLOW

### 1. Planning Phase

```bash
# Use the planning skill to create comprehensive implementation plans
# See: skills/writing-plans/SKILL.md
```

### 2. Agent Creation

```bash
# Create new agent with proper structure
mkdir agents/my-new-agent
cd agents/my-new-agent

# Initialize with template
cp -r ../templates/basic-agent/* .

# Customize configuration
edit config.json
edit README.md
```

### 3. Implementation

```javascript
// Implement core logic in agent.js
class MyAgent {
  constructor(config) {
    this.config = config;
  }

  async execute(inputs) {
    // Your business logic here
    return await this.process(inputs);
  }
}

module.exports = { MyAgent };
```

### 4. Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Generate coverage report
npm run test:coverage
```

### 5. Registration

```javascript
// Register with global registry
const { globalRegistry } = require("../registry/agent-registry");
const { MyAgent } = require("./agent");

globalRegistry.register(MyAgent, {
  name: "my-agent",
  category: "utility",
  description: "My custom agent",
});
```

### 6. Deployment

```bash
# Build container
docker build -t my-agent .

# Deploy to Kubernetes
kubectl apply -f deployment/k8s/

# Check health
curl http://localhost:3000/api/v1/health
```

---

## 🔧 DEVELOPMENT TOOLS

### VS Code Integration

**Required Extensions:**

- ESLint (for JavaScript linting)
- Prettier (for code formatting)
- Jest (for testing)
- Docker (for container development)

**Recommended Settings:**

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.validate": ["javascript"],
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### CLI Tools

```bash
# Agent management
agent-cli list                    # List all agents
agent-cli info my-agent          # Get agent details
agent-cli execute my-agent       # Execute agent
agent-cli health                 # Check system health

# Development
agent-cli test my-agent          # Run agent tests
agent-cli validate my-agent      # Validate configuration
```

### API Endpoints

```bash
# Agent operations
GET  /api/v1/agents              # List agents
GET  /api/v1/agents/:name        # Get agent details
POST /api/v1/agents/:name/execute # Execute agent

# System management
GET  /api/v1/health              # Health check
GET  /api/v1/metrics             # System metrics
GET  /api/v1/analytics           # Usage analytics
```

---

## 📊 MONITORING & ANALYTICS

### Key Metrics

- **Performance**: Execution time, throughput, error rates
- **Usage**: Agent popularity, usage patterns, adoption rates
- **Health**: System status, agent availability, resource usage
- **Quality**: Test coverage, code quality, reliability scores

### Dashboard

Access the monitoring dashboard at: `http://localhost:3000/dashboard`

Features:

- Real-time agent metrics
- Performance graphs
- Error tracking
- Usage analytics
- System health overview

---

## 🚀 PRODUCTION DEPLOYMENT

### Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd agent-system

# Install dependencies
npm install

# Configure environment
cp .env.example .env
edit .env  # Add production values

# Run database migrations
npm run migrate

# Start services
docker-compose up -d
```

### Scaling Considerations

- **Horizontal Scaling**: Add more agent instances
- **Load Balancing**: Distribute requests across instances
- **Caching**: Implement Redis for performance
- **Database**: Use connection pooling
- **Monitoring**: Set up alerts and dashboards

### Security

- **Authentication**: JWT tokens for API access
- **Authorization**: Role-based access control
- **Encryption**: TLS for all communications
- **Secrets**: Use environment variables and secret management
- **Auditing**: Log all agent executions and system events

---

## 🆘 TROUBLESHOOTING

### Common Issues

**Agent not found:**

- Check if agent is registered with the registry
- Verify agent name and category
- Check agent configuration

**Execution timeout:**

- Increase timeout in agent configuration
- Optimize agent performance
- Check for infinite loops or blocking operations

**Memory issues:**

- Monitor agent memory usage
- Implement garbage collection
- Use streaming for large data processing

**Network errors:**

- Check API gateway configuration
- Verify network connectivity
- Check firewall settings

### Debug Mode

```bash
# Enable debug logging
export DEBUG=agent:*
npm run dev

# Check agent logs
docker logs agent-registry

# Test agent directly
node -e "require('./agents/my-agent').MyAgent().execute({test: true})"
```

---

## 📖 FURTHER READING

- [Agent Folder Structure](01-agent-folder-structure.md) - Detailed file organization
- [Configuration Management](02-agent-config-documentation.md) - Config patterns and validation
- [Entry Points](03-entry-points-patterns.md) - Clean interface design
- [Testing Frameworks](04-testing-tools.md) - Comprehensive testing strategies
- [Advanced Patterns](05-advanced-patterns.md) - Complex orchestration techniques
- [Parent/Sub-Agent Architecture](06-parent-sub-agent.md) - Workflow orchestration
- [Project Organization](07-project-organization.md) - Registry and factory patterns
- [Integration & Deployment](08-integration-deployment.md) - Production deployment guides

---

## 🤝 CONTRIBUTING

1. Follow the established patterns in each section
2. Add comprehensive tests for new agents
3. Update documentation for any changes
4. Use the CLI tools for development and testing
5. Follow the commit message conventions

### Code Standards

- Use ESLint and Prettier for code formatting
- Write comprehensive unit and integration tests
- Follow the established folder structure
- Document all public APIs and configurations
- Use TypeScript for type safety (optional but recommended)

---

## 📄 LICENSE

This guide is part of the Custom Sub-Agents framework. See individual agent licenses for distribution terms.

---

**Last Updated**: January 2026
**Version**: 2.0 - Modular Architecture
**Authors**: BIRDC Development Team
