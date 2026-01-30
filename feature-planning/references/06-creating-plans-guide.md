## 🎯 Creating a Plan: Step-by-Step

### Step 1: Understand the Request

```javascript
// User request
const request = {
  goal: "Create Q4 strategic plan for franchise expansion",
  priority: "urgent",
  constraints: {
    budget: "high",
    timeline: "2 weeks",
    regions: ["East Africa"],
  },
};
```

### Step 2: Decompose into Atomic Steps

```
Ask yourself: "What are the smallest, executable actions?"

NOT: "Create strategic plan" (too vague)
BUT:
  - Analyze market
  - Identify audience
  - Define positioning
  - Create messaging
  - Validate strategy
```

### Step 3: Identify Dependencies

```
What needs what?

Analyze Market         [NEEDS: nothing, can start first]
  └─→ outputs: market insights

Identify Audience      [NEEDS: market insights]
  └─→ outputs: audience profile

Define Positioning     [NEEDS: market insights]
  └─→ outputs: positioning statement

Create Messaging       [NEEDS: positioning, audience profile]
  └─→ outputs: messaging strategy

Validate Strategy      [NEEDS: messaging, positioning, audience]
  └─→ outputs: validation report
```

### Step 4: Create the Plan Object

```javascript
const plan = {
  steps: [
    // Step 1: No dependencies
    {
      id: "analyze-market",
      name: "Analyze Market",
      action: "planning-agent.analyzeMarket",
      depends_on: [],
    },

    // Step 2: Depends on Step 1
    {
      id: "identify-audience",
      name: "Identify Audience",
      action: "planning-agent.identifyAudience",
      depends_on: ["analyze-market"],
    },

    // Step 3: Also depends on Step 1 (can run parallel with Step 2)
    {
      id: "define-positioning",
      name: "Define Positioning",
      action: "planning-agent.definePositioning",
      depends_on: ["analyze-market"],
    },

    // Step 4: Depends on 2 and 3
    {
      id: "create-messaging",
      name: "Create Messaging",
      action: "planning-agent.createMessaging",
      depends_on: ["identify-audience", "define-positioning"],
    },

    // Step 5: Depends on everything
    {
      id: "validate-strategy",
      name: "Validate Strategy",
      action: "planning-agent.validateStrategy",
      depends_on: ["create-messaging"],
    },
  ],
};
```
