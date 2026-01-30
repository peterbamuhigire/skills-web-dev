# 📄 Entry Points & Export Patterns

## 📝 **4. index.js - Entry Point**

**Purpose**: Provides clean, consistent interface for importing and using the agent.

### 🎯 Why You Need index.js

**Without index.js (Bad)**

```javascript
// User has to know internal structure
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer/agent");
const DatabaseTool = require("./agents/sales-analyzer/tools/database");
const ReportingTool = require("./agents/sales-analyzer/tools/reporting");

// Lots of imports, user needs to know file structure
const agent = new SalesAnalyzerAgent({
  database: new DatabaseTool(config.database),
  reporting: new ReportingTool(config.reporting),
});
```

**With index.js (Good)**

```javascript
// Clean, simple import
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");

// Just use it - no internal knowledge needed
const agent = new SalesAnalyzerAgent(config);
```

### Without index.js (Bad)

**Problems:**

- Users must know internal file structure
- Multiple imports required
- Dependencies must be manually instantiated
- Breaking changes if you reorganize files
- No version management
- Hard to test as a unit

### With index.js (Good)

**Benefits:**

- Single import point
- Encapsulated complexity
- Easy to refactor internals
- Version management
- Testable as a unit
- Consistent API

## 📝 Basic index.js Example

**File**: `agents/sales-analyzer/index.js`

```javascript
/**
 * Sales Analyzer Agent - Entry Point
 *
 * This file provides the main interface for using the Sales Analyzer Agent.
 * It handles dependency injection, configuration validation, and exports
 * the main agent class and any utilities.
 */

const { SalesAnalyzerAgent } = require("./agent");
const { DatabaseTool } = require("./tools/database");
const { ReportingTool } = require("./tools/reporting");
const { ValidationTool } = require("./tools/validation");
const configSchema = require("./config.schema.json");
const packageInfo = require("./package.json");

// Validate configuration against schema
function validateConfig(config) {
  // Basic validation - you could use a library like Joi or Ajv
  const required = ["database", "analysis"];
  const missing = required.filter((key) => !config[key]);

  if (missing.length > 0) {
    throw new Error(`Missing required configuration: ${missing.join(", ")}`);
  }

  return true;
}

// Create configured agent instance
function createAgent(config = {}) {
  // Load default config
  const defaultConfig = require("./config.json");

  // Merge with user config
  const finalConfig = {
    ...defaultConfig,
    ...config,
    // Override with environment variables if present
    database: {
      ...defaultConfig.database,
      ...config.database,
      password:
        process.env.DB_PASSWORD ||
        config.database?.password ||
        defaultConfig.database.password,
      apiKey:
        process.env.ANALYTICS_API_KEY ||
        config.database?.apiKey ||
        defaultConfig.database.apiKey,
    },
  };

  // Validate configuration
  validateConfig(finalConfig);

  // Create dependencies
  const database = new DatabaseTool(finalConfig.database);
  const reporting = new ReportingTool(finalConfig.reporting);
  const validation = new ValidationTool(finalConfig.validation);

  // Create and return agent
  return new SalesAnalyzerAgent({
    ...finalConfig,
    database,
    reporting,
    validation,
  });
}

// Factory function for easy instantiation
function SalesAnalyzerAgentFactory(config = {}) {
  return createAgent(config);
}

// Export the main class and factory
module.exports = {
  SalesAnalyzerAgent,
  createAgent,
  SalesAnalyzerAgentFactory,
  version: packageInfo.version,
  name: packageInfo.name,
};

// Named exports for ES6-style imports
module.exports.SalesAnalyzerAgent = SalesAnalyzerAgent;
module.exports.createAgent = createAgent;
module.exports.SalesAnalyzerAgentFactory = SalesAnalyzerAgentFactory;
```

## 🚀 Different Patterns

### Pattern 1: Simple Export (Best for Simple Agents)

**Best for:** Agents with minimal dependencies and configuration.

```javascript
// agents/simple-agent/index.js
const { SimpleAgent } = require("./agent");

module.exports = {
  SimpleAgent,
  createAgent: (config) => new SimpleAgent(config),
  version: require("./package.json").version,
};
```

**Usage:**

```javascript
const { SimpleAgent } = require("./agents/simple-agent");
const agent = new SimpleAgent(config);
```

### Pattern 2: Named Exports (Best for Multiple Exports)

**Best for:** Agents that export multiple classes or utilities.

```javascript
// agents/multi-export-agent/index.js
const { MainAgent } = require("./agent");
const { HelperClass } = require("./helper");
const { UtilityFunction } = require("./utils");

module.exports = {
  MainAgent,
  HelperClass,
  UtilityFunction,
  createAgent: (config) => new MainAgent(config),
  version: require("./package.json").version,
};
```

**Usage:**

```javascript
const { MainAgent, HelperClass } = require("./agents/multi-export-agent");
const agent = new MainAgent(config);
const helper = new HelperClass();
```

### Pattern 3: Factory Pattern (Most Flexible)

**Best for:** Complex agents with dependency injection and configuration validation.

```javascript
// agents/complex-agent/index.js
const { ComplexAgent } = require("./agent");
const { DatabaseService } = require("./services/database");
const { CacheService } = require("./services/cache");
const { ConfigValidator } = require("./utils/config-validator");

class AgentFactory {
  static create(config = {}) {
    // Load and merge configuration
    const defaultConfig = require("./config.json");
    const finalConfig = { ...defaultConfig, ...config };

    // Validate configuration
    ConfigValidator.validate(finalConfig);

    // Create dependencies
    const database = new DatabaseService(finalConfig.database);
    const cache = new CacheService(finalConfig.cache);

    // Create and configure agent
    const agent = new ComplexAgent(finalConfig);
    agent.setDatabase(database);
    agent.setCache(cache);

    // Initialize agent
    agent.initialize();

    return agent;
  }

  static createWithDefaults() {
    return this.create({});
  }
}

module.exports = {
  ComplexAgent,
  AgentFactory,
  createAgent: AgentFactory.create.bind(AgentFactory),
  createAgentWithDefaults: AgentFactory.createWithDefaults.bind(AgentFactory),
  version: require("./package.json").version,
};
```

**Usage:**

```javascript
const { createAgent } = require("./agents/complex-agent");
const agent = createAgent(config);
```

## 📋 Real-World Examples

### Example 1: Node.js App Using Agent

```javascript
// app.js
const express = require("express");
const { createAgent } = require("./agents/sales-analyzer");

const app = express();
const salesAgent = createAgent({
  database: { host: "localhost" },
});

app.get("/api/sales/analysis", async (req, res) => {
  try {
    const result = await salesAgent.analyze({
      startDate: req.query.start,
      endDate: req.query.end,
    });
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log("Server running on port 3000");
});
```

### Example 2: Test File Using Agent

```javascript
// tests/agent.test.js
const { createAgent } = require("../agents/sales-analyzer");

describe("SalesAnalyzerAgent", () => {
  let agent;

  beforeEach(() => {
    agent = createAgent({
      database: {
        /* test config */
      },
      analysis: { maxRecords: 100 },
    });
  });

  test("analyzes sales data correctly", async () => {
    const result = await agent.analyze({
      startDate: "2024-01-01",
      endDate: "2024-01-31",
    });

    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
  });
});
```

### Example 3: Multiple Agents in One Project

```javascript
// multi-agent-app.js
const { createAgent: createSalesAgent } = require("./agents/sales-analyzer");
const { createAgent: createReportAgent } = require("./agents/report-generator");
const { createAgent: createDataAgent } = require("./agents/data-processor");

// Create all agents with consistent interface
const agents = {
  sales: createSalesAgent({ database: dbConfig }),
  reports: createReportAgent({ templates: templateConfig }),
  data: createDataAgent({ processors: processorConfig }),
};

// Use agents
async function processBusinessData(input) {
  // Process raw data
  const processed = await agents.data.process(input);

  // Analyze sales
  const analysis = await agents.sales.analyze(processed);

  // Generate report
  const report = await agents.reports.generate({
    data: analysis,
    format: "pdf",
  });

  return report;
}
```

## 🐍 Python Agent Equivalent

**File**: `agents/data-processor/__init__.py`

```python
"""
Data Processor Agent - Python Entry Point

This module provides the main interface for the Data Processor Agent.
"""

from .agent import DataProcessorAgent
from .tools.database import DatabaseTool
from .tools.validation import ValidationTool
from .config import load_config, validate_config
import os

__version__ = "1.0.0"
__all__ = ['DataProcessorAgent', 'create_agent']

def create_agent(config=None):
    """
    Factory function to create a configured DataProcessorAgent.

    Args:
        config (dict, optional): Configuration dictionary. If None, loads from config.json

    Returns:
        DataProcessorAgent: Configured agent instance
    """
    if config is None:
        config = load_config()

    # Override with environment variables
    config['database']['password'] = os.getenv('DB_PASSWORD', config['database'].get('password'))
    config['api']['key'] = os.getenv('API_KEY', config['api'].get('key'))

    # Validate configuration
    validate_config(config)

    # Create dependencies
    database = DatabaseTool(config['database'])
    validation = ValidationTool(config['validation'])

    # Create and return agent
    agent = DataProcessorAgent(config)
    agent.database = database
    agent.validation = validation

    return agent

# For easy importing
__all__ = ['DataProcessorAgent', 'create_agent']
```

**Usage:**

```python
from agents.data_processor import create_agent

agent = create_agent()
result = agent.process_data(source='database', options={})
```

## ✅ Best Practices for index.js

### ✅ DO

- **Single Responsibility**: Only handle imports and instantiation
- **Configuration Validation**: Validate config before creating agent
- **Environment Variables**: Support .env overrides
- **Error Handling**: Provide clear error messages
- **Version Export**: Export version for compatibility checks
- **Named Exports**: Support both `require()` and `import`
- **Documentation**: Comment complex logic

### ❌ DON'T

- **Business Logic**: Don't put agent logic in index.js
- **Hardcoded Values**: Don't hardcode configuration
- **Side Effects**: Don't execute code on import
- **Complex Dependencies**: Keep dependency creation simple
- **File System Access**: Don't read files unless necessary
- **Network Calls**: Don't make network requests on import

## 📁 Complete Agent Folder With index.js

```
agents/sales-analyzer/
├── agent.js              # Core agent logic
├── config.json           # Configuration
├── index.js              # ← Entry point (this file)
├── package.json          # Dependencies
├── .env.example          # Environment template
├── README.md             # Documentation
├── tests/
│   ├── agent.test.js
│   └── integration.test.js
└── tools/
    ├── database.js
    ├── reporting.js
    └── validation.js
```

## 🔄 Import Flow

### How Users Import Your Agent

```
User Code
    ↓
require('./agents/sales-analyzer')  ← index.js
    ↓
Loads agent.js, config.json, tools/
    ↓
Validates config, creates dependencies
    ↓
Returns configured agent instance
    ↓
User gets ready-to-use agent
```

## ✅ Summary

### What index.js Does

- **Encapsulates Complexity**: Users don't need to know internal structure
- **Handles Configuration**: Merges defaults, validates, applies environment variables
- **Dependency Injection**: Creates and wires up all dependencies
- **Provides Interface**: Single point for importing the agent
- **Version Management**: Exports version for compatibility
- **Error Handling**: Validates configuration and provides clear errors

### Result

**Before (Complex):**

```javascript
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer/agent");
const DatabaseTool = require("./agents/sales-analyzer/tools/database");
const agent = new SalesAnalyzerAgent({
  database: new DatabaseTool(config.database),
});
```

**After (Simple):**

```javascript
const { createAgent } = require("./agents/sales-analyzer");
const agent = createAgent(config);
```

## 🏆 Recommended index.js Template

```javascript
/**
 * [Agent Name] - Entry Point
 *
 * Provides clean interface for importing and using the agent.
 * Handles configuration, dependency injection, and validation.
 */

const { AgentClass } = require("./agent");
const { Dependency1 } = require("./tools/dependency1");
const { Dependency2 } = require("./tools/dependency2");
const packageInfo = require("./package.json");

function validateConfig(config) {
  // Validate required configuration
  const required = ["setting1", "setting2"];
  const missing = required.filter((key) => !config[key]);
  if (missing.length > 0) {
    throw new Error(`Missing required config: ${missing.join(", ")}`);
  }
}

function createAgent(config = {}) {
  // Load defaults
  const defaultConfig = require("./config.json");

  // Merge configurations
  const finalConfig = {
    ...defaultConfig,
    ...config,
    // Environment variable overrides
    secrets: {
      apiKey: process.env.API_KEY || config.secrets?.apiKey,
      dbPassword: process.env.DB_PASSWORD || config.secrets?.dbPassword,
    },
  };

  // Validate
  validateConfig(finalConfig);

  // Create dependencies
  const dep1 = new Dependency1(finalConfig.dep1);
  const dep2 = new Dependency2(finalConfig.dep2);

  // Create and return agent
  return new AgentClass({
    ...finalConfig,
    dep1,
    dep2,
  });
}

module.exports = {
  AgentClass,
  createAgent,
  version: packageInfo.version,
  name: packageInfo.name,
};
```

This template provides a solid foundation for any agent's entry point, ensuring consistency and maintainability across your agent ecosystem.</content>
<parameter name="filePath">c:\wamp64\www\birdc_erp\skills\custom-sub-agents\references\03-entry-points-patterns.md
