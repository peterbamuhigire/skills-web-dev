## 💻 Code: Understanding Plan Structure

### Simple Plan Object

```javascript
// A PLAN is a data structure that defines work
const plan = {
  id: "strategic-plan-q4",
  name: "Create Q4 Strategic Plan",
  description: "Develop Q4 strategy for franchises",

  // All the steps we need to execute
  steps: [
    {
      id: "step-1",
      name: "Analyze Market Conditions",
      description: "Understand current market trends",
      action: "planning-agent.analyzeMarket", // Who executes this?
      input: {
        sector: "retail",
        region: "east-africa",
      },
      output_format: "market_analysis", // What should we get back?
      depends_on: [], // No dependencies
      timeout: "5 minutes",
      retry_count: 2,
    },

    {
      id: "step-2",
      name: "Identify Target Audience",
      description: "Define who we're targeting",
      action: "planning-agent.identifyAudience",
      input: {
        market_analysis: "step-1", // Reference output from step-1
      },
      output_format: "audience_profile",
      depends_on: ["step-1"], // Needs STEP 1 done first!
      timeout: "3 minutes",
      retry_count: 2,
    },

    {
      id: "step-3a",
      name: "Define Positioning",
      action: "planning-agent.definePositioning",
      input: {
        market_analysis: "step-1",
        audience: "step-2",
      },
      output_format: "positioning",
      depends_on: ["step-1", "step-2"],
      timeout: "5 minutes",
    },

    {
      id: "step-3b",
      name: "Analyze Competitors",
      action: "planning-agent.analyzeCompetitors", // Can run parallel with step-3a!
      input: {
        market_analysis: "step-1",
      },
      output_format: "competitor_analysis",
      depends_on: ["step-1"], // Also depends on step-1, but not step-2
      timeout: "10 minutes",
    },

    {
      id: "step-4",
      name: "Create Messaging",
      description: "Develop marketing messaging",
      action: "planning-agent.createMessaging",
      input: {
        positioning: "step-3a",
        competitors: "step-3b",
        audience: "step-2",
      },
      output_format: "messaging_strategy",
      depends_on: ["step-3a", "step-3b"], // Needs BOTH step-3a AND step-3b
      timeout: "5 minutes",
    },

    {
      id: "step-5",
      name: "Validate Strategy",
      action: "planning-agent.validateStrategy",
      input: {
        positioning: "step-3a",
        messaging: "step-4",
        audience: "step-2",
      },
      output_format: "validation_report",
      depends_on: ["step-4"], // Needs final step done
      timeout: "5 minutes",
    },
  ],

  // Validation rules for outputs
  validations: {
    "step-1": {
      rule: "output must have key findings",
      check: (output) => output.findings && output.findings.length > 0,
    },
    "step-2": {
      rule: "audience profile must have segments",
      check: (output) => output.segments && output.segments.length > 0,
    },
  },

  // If something fails, what do we do?
  error_handling: {
    strategy: "try_fallback", // Other options: retry, escalate, skip
    fallback_plan: "simple-planning-flow",
  },
};
```
