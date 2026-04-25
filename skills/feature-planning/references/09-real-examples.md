## 🎯 Real Example: Creating a Plan for Maduuka

### Scenario: "Create franchise expansion strategy"

```javascript
const plan = {
  name: "Franchise Expansion Strategy Q4",

  steps: [
    // TIER 1: Data gathering (no dependencies)
    {
      id: "analyze-current-franchises",
      name: "Analyze Current Franchises",
      action: "data-agent.analyzeFranchises",
      depends_on: [],
      timeout: "10 min",
    },
    {
      id: "analyze-market-demographics",
      name: "Analyze Market Demographics",
      action: "data-agent.analyzeMarket",
      depends_on: [],
      timeout: "10 min",
    },
    {
      id: "analyze-competition",
      name: "Analyze Competition",
      action: "data-agent.analyzeCompetition",
      depends_on: [],
      timeout: "10 min",
    },

    // TIER 2: Analysis (depends on TIER 1)
    {
      id: "identify-opportunities",
      name: "Identify Expansion Opportunities",
      action: "planning-agent.identifyOpportunities",
      depends_on: [
        "analyze-current-franchises",
        "analyze-market-demographics",
        "analyze-competition",
      ],
      timeout: "15 min",
    },
    {
      id: "assess-financial-feasibility",
      name: "Assess Financial Feasibility",
      action: "planning-agent.assessFinance",
      depends_on: ["analyze-current-franchises", "identify-opportunities"],
      timeout: "15 min",
    },

    // TIER 3: Strategy (depends on TIER 2)
    {
      id: "create-expansion-strategy",
      name: "Create Expansion Strategy",
      action: "planning-agent.createStrategy",
      depends_on: ["identify-opportunities", "assess-financial-feasibility"],
      timeout: "20 min",
    },

    // TIER 4: Validation (depends on TIER 3)
    {
      id: "validate-strategy",
      name: "Validate Strategy",
      action: "planning-agent.validateStrategy",
      depends_on: ["create-expansion-strategy"],
      timeout: "10 min",
    },

    // TIER 5: Documentation (depends on everything)
    {
      id: "document-plan",
      name: "Document Strategy in Google Docs",
      action: "reporting-agent.documentPlan",
      depends_on: ["validate-strategy"],
      timeout: "10 min",
    },
  ],

  // Execution timing:
  // TIER 1 (all parallel): 10 min
  // TIER 2 (all parallel): 15 min
  // TIER 3: 20 min
  // TIER 4: 10 min
  // TIER 5: 10 min
  // TOTAL: 65 minutes (not 85+, because of parallelization!)
};
```
