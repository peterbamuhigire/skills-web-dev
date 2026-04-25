# 🏗️ Project Organization & Registry Patterns

## 🎯 AGENT REGISTRY PATTERN

**Purpose**: Centralized management and discovery of agents with automatic registration, dependency injection, and lifecycle management.

### Pattern 1: Agent Registry

**File**: `agents/registry/agent-registry.js`

```javascript
/**
 * Agent Registry
 *
 * Centralized registry for agent discovery, instantiation, and management.
 * Provides dependency injection, lifecycle management, and agent relationships.
 */

class AgentRegistry {
  constructor(config = {}) {
    this.config = {
      autoDiscovery: true,
      dependencyInjection: true,
      lifecycleManagement: true,
      maxInstances: 100,
      instanceTimeout: 3600000, // 1 hour
      ...config,
    };

    this.agents = new Map(); // agentName -> agentClass
    this.instances = new Map(); // agentName -> instance
    this.dependencies = new Map(); // agentName -> Set of dependencies
    this.metadata = new Map(); // agentName -> metadata
    this.lifecycle = new Map(); // agentName -> lifecycle state

    this.instancePool = new Map(); // agentName -> Array of instances (for pooling)
    this.instanceStats = new Map(); // agentName -> usage stats
  }

  /**
   * Register an agent class with the registry
   */
  register(agentClass, options = {}) {
    const agentName =
      options.name || agentClass.name.replace("Agent", "").toLowerCase();

    if (this.agents.has(agentName)) {
      throw new Error(`Agent '${agentName}' is already registered`);
    }

    // Extract metadata from class
    const metadata = this.extractMetadata(agentClass, options);

    // Register agent
    this.agents.set(agentName, agentClass);
    this.metadata.set(agentName, metadata);
    this.lifecycle.set(agentName, "registered");
    this.instanceStats.set(agentName, {
      totalInstances: 0,
      activeInstances: 0,
      totalExecutions: 0,
      averageExecutionTime: 0,
      lastUsed: null,
      errors: 0,
    });

    // Register dependencies
    if (metadata.dependencies) {
      this.dependencies.set(agentName, new Set(metadata.dependencies));
    }

    console.log(`✅ Registered agent: ${agentName} (${metadata.category})`);
    return agentName;
  }

  /**
   * Extract metadata from agent class
   */
  extractMetadata(agentClass, options) {
    const metadata = {
      name: options.name || agentClass.name.replace("Agent", "").toLowerCase(),
      category: options.category || "general",
      description:
        options.description || agentClass.description || "No description",
      version: options.version || "1.0.0",
      author: options.author || "Unknown",
      tags: options.tags || [],
      capabilities: options.capabilities || [],
      dependencies: options.dependencies || [],
      configSchema: options.configSchema || {},
      inputSchema: options.inputSchema || {},
      outputSchema: options.outputSchema || {},
      singleton: options.singleton || false,
      poolable: options.poolable || false,
      maxPoolSize: options.maxPoolSize || 5,
      timeout: options.timeout || 300000, // 5 minutes
      retryPolicy: options.retryPolicy || { maxRetries: 0, backoff: "linear" },
      healthCheck: typeof agentClass.prototype.healthCheck === "function",
    };

    return metadata;
  }

  /**
   * Get an agent instance
   */
  async get(agentName, config = {}) {
    if (!this.agents.has(agentName)) {
      throw new Error(`Agent '${agentName}' is not registered`);
    }

    const metadata = this.metadata.get(agentName);
    const stats = this.instanceStats.get(agentName);

    // Check if singleton
    if (metadata.singleton) {
      if (!this.instances.has(agentName)) {
        const instance = await this.createInstance(agentName, config);
        this.instances.set(agentName, instance);
      }
      stats.lastUsed = new Date();
      return this.instances.get(agentName);
    }

    // Check if poolable
    if (metadata.poolable) {
      return this.getFromPool(agentName, config);
    }

    // Create new instance
    const instance = await this.createInstance(agentName, config);
    stats.totalInstances++;
    stats.activeInstances++;
    stats.lastUsed = new Date();

    return instance;
  }

  /**
   * Create a new agent instance with dependency injection
   */
  async createInstance(agentName, config = {}) {
    const agentClass = this.agents.get(agentName);
    const metadata = this.metadata.get(agentName);

    // Resolve dependencies
    const dependencies = {};
    if (this.config.dependencyInjection && metadata.dependencies) {
      for (const depName of metadata.dependencies) {
        if (!this.agents.has(depName)) {
          throw new Error(
            `Dependency '${depName}' for agent '${agentName}' is not registered`,
          );
        }
        dependencies[depName] = await this.get(depName);
      }
    }

    // Merge configurations
    const finalConfig = {
      ...metadata.configSchema,
      ...config,
      registry: this,
      dependencies,
    };

    // Create instance
    const instance = new agentClass(finalConfig);

    // Initialize if method exists
    if (typeof instance.initialize === "function") {
      await instance.initialize();
    }

    // Set lifecycle
    this.lifecycle.set(agentName, "active");

    return instance;
  }

  /**
   * Get instance from pool or create new one
   */
  async getFromPool(agentName, config) {
    const metadata = this.metadata.get(agentName);
    const stats = this.instanceStats.get(agentName);

    let pool = this.instancePool.get(agentName);
    if (!pool) {
      pool = [];
      this.instancePool.set(agentName, pool);
    }

    // Find available instance
    let instance = pool.find((inst) => !inst._inUse);

    if (!instance) {
      // Create new instance if pool not full
      if (pool.length < metadata.maxPoolSize) {
        instance = await this.createInstance(agentName, config);
        instance._inUse = false;
        instance._poolId = `${agentName}_${pool.length}`;
        pool.push(instance);
      } else {
        // Wait for available instance
        instance = await this.waitForAvailableInstance(pool);
      }
    }

    // Mark as in use
    instance._inUse = true;
    instance._lastUsed = new Date();

    stats.activeInstances++;

    return instance;
  }

  /**
   * Wait for an available instance in the pool
   */
  async waitForAvailableInstance(pool) {
    return new Promise((resolve, reject) => {
      const checkInterval = setInterval(() => {
        const available = pool.find((inst) => !inst._inUse);
        if (available) {
          clearInterval(checkInterval);
          resolve(available);
        }
      }, 100); // Check every 100ms

      // Timeout after 30 seconds
      setTimeout(() => {
        clearInterval(checkInterval);
        reject(new Error("Timeout waiting for available instance"));
      }, 30000);
    });
  }

  /**
   * Return instance to pool
   */
  returnToPool(instance) {
    if (instance._poolId) {
      instance._inUse = false;
      const agentName = instance._poolId.split("_")[0];
      const stats = this.instanceStats.get(agentName);
      if (stats) {
        stats.activeInstances = Math.max(0, stats.activeInstances - 1);
      }
    }
  }

  /**
   * Execute an agent with automatic resource management
   */
  async execute(agentName, inputs, options = {}) {
    const instance = await this.get(agentName, options.config);
    const stats = this.instanceStats.get(agentName);

    const startTime = Date.now();

    try {
      // Execute agent
      const result = await instance.execute(inputs, options);

      // Record success
      const duration = Date.now() - startTime;
      stats.totalExecutions++;
      stats.averageExecutionTime =
        (stats.averageExecutionTime * (stats.totalExecutions - 1) + duration) /
        stats.totalExecutions;

      return result;
    } catch (error) {
      // Record error
      stats.errors++;
      throw error;
    } finally {
      // Return to pool if poolable
      const metadata = this.metadata.get(agentName);
      if (metadata.poolable) {
        this.returnToPool(instance);
      }

      // Clean up non-singleton instances after timeout
      if (!metadata.singleton) {
        setTimeout(() => {
          this.cleanupInstance(agentName, instance);
        }, this.config.instanceTimeout);
      }
    }
  }

  /**
   * Clean up an instance
   */
  cleanupInstance(agentName, instance) {
    const stats = this.instanceStats.get(agentName);
    if (stats) {
      stats.activeInstances = Math.max(0, stats.activeInstances - 1);
    }

    // Call cleanup if method exists
    if (typeof instance.cleanup === "function") {
      instance.cleanup();
    }
  }

  /**
   * Get agent metadata
   */
  getMetadata(agentName) {
    return this.metadata.get(agentName) || null;
  }

  /**
   * List all registered agents
   */
  listAgents(category = null) {
    const agents = Array.from(this.agents.keys()).map((name) => ({
      name,
      ...this.metadata.get(name),
      lifecycle: this.lifecycle.get(name),
      stats: this.instanceStats.get(name),
    }));

    if (category) {
      return agents.filter((agent) => agent.category === category);
    }

    return agents;
  }

  /**
   * Find agents by capability
   */
  findByCapability(capability) {
    return this.listAgents().filter((agent) =>
      agent.capabilities.includes(capability),
    );
  }

  /**
   * Find agents by tag
   */
  findByTag(tag) {
    return this.listAgents().filter((agent) => agent.tags.includes(tag));
  }

  /**
   * Get agent dependencies
   */
  getDependencies(agentName) {
    return Array.from(this.dependencies.get(agentName) || []);
  }

  /**
   * Get dependent agents (agents that depend on this one)
   */
  getDependents(agentName) {
    const dependents = [];

    for (const [name, deps] of this.dependencies) {
      if (deps.has(agentName)) {
        dependents.push(name);
      }
    }

    return dependents;
  }

  /**
   * Check if agent can be safely removed
   */
  canRemove(agentName) {
    const dependents = this.getDependents(agentName);
    const hasActiveInstances =
      this.instanceStats.get(agentName)?.activeInstances > 0;

    return {
      canRemove: dependents.length === 0 && !hasActiveInstances,
      dependents,
      hasActiveInstances,
    };
  }

  /**
   * Remove an agent from registry
   */
  remove(agentName) {
    const check = this.canRemove(agentName);

    if (!check.canRemove) {
      throw new Error(
        `Cannot remove agent '${agentName}': ${check.dependents.length} dependents, ${check.hasActiveInstances ? "has active instances" : ""}`,
      );
    }

    // Clean up instances
    if (this.instances.has(agentName)) {
      const instance = this.instances.get(agentName);
      this.cleanupInstance(agentName, instance);
      this.instances.delete(agentName);
    }

    // Clean up pool
    if (this.instancePool.has(agentName)) {
      const pool = this.instancePool.get(agentName);
      pool.forEach((instance) => this.cleanupInstance(agentName, instance));
      this.instancePool.delete(agentName);
    }

    // Remove from registry
    this.agents.delete(agentName);
    this.metadata.delete(agentName);
    this.dependencies.delete(agentName);
    this.lifecycle.delete(agentName);
    this.instanceStats.delete(agentName);

    console.log(`🗑️ Removed agent: ${agentName}`);
  }

  /**
   * Get registry statistics
   */
  getStats() {
    const agents = this.listAgents();
    const totalInstances = agents.reduce(
      (sum, agent) => sum + agent.stats.totalInstances,
      0,
    );
    const activeInstances = agents.reduce(
      (sum, agent) => sum + agent.stats.activeInstances,
      0,
    );
    const totalExecutions = agents.reduce(
      (sum, agent) => sum + agent.stats.totalExecutions,
      0,
    );
    const totalErrors = agents.reduce(
      (sum, agent) => sum + agent.stats.errors,
      0,
    );

    return {
      totalAgents: agents.length,
      agentsByCategory: agents.reduce((acc, agent) => {
        acc[agent.category] = (acc[agent.category] || 0) + 1;
        return acc;
      }, {}),
      totalInstances,
      activeInstances,
      totalExecutions,
      totalErrors,
      errorRate:
        totalExecutions > 0
          ? ((totalErrors / totalExecutions) * 100).toFixed(2) + "%"
          : "0%",
      averageExecutionTime:
        agents.reduce(
          (sum, agent) => sum + agent.stats.averageExecutionTime,
          0,
        ) / agents.length,
    };
  }

  /**
   * Health check for all agents
   */
  async healthCheck() {
    const results = {
      overall: "healthy",
      agents: {},
      timestamp: new Date(),
    };

    for (const [agentName, metadata] of this.metadata) {
      try {
        const instance = await this.get(agentName);
        let healthStatus = "unknown";

        if (metadata.healthCheck) {
          const health = await instance.healthCheck();
          healthStatus = health.status || "healthy";
        } else {
          // Basic health check - can instantiate
          healthStatus = "healthy";
        }

        results.agents[agentName] = {
          status: healthStatus,
          lastUsed: this.instanceStats.get(agentName).lastUsed,
          activeInstances: this.instanceStats.get(agentName).activeInstances,
        };

        if (healthStatus !== "healthy") {
          results.overall = "degraded";
        }
      } catch (error) {
        results.agents[agentName] = {
          status: "error",
          error: error.message,
        };
        results.overall = "unhealthy";
      }
    }

    return results;
  }

  /**
   * Auto-discover agents from directory
   */
  async autoDiscover(directory = "./agents") {
    if (!this.config.autoDiscovery) return;

    const fs = require("fs").promises;
    const path = require("path");

    try {
      const entries = await fs.readdir(directory, { withFileTypes: true });

      for (const entry of entries) {
        if (
          entry.isDirectory() &&
          !entry.name.startsWith(".") &&
          entry.name !== "registry"
        ) {
          const agentPath = path.join(directory, entry.name, "agent.js");

          try {
            const stats = await fs.stat(agentPath);
            if (stats.isFile()) {
              const AgentClass = require(path.resolve(agentPath));
              this.register(AgentClass);
            }
          } catch (error) {
            console.warn(
              `Failed to load agent from ${agentPath}: ${error.message}`,
            );
          }
        }
      }

      console.log(`🔍 Auto-discovered ${this.agents.size} agents`);
    } catch (error) {
      console.warn(`Auto-discovery failed: ${error.message}`);
    }
  }
}

// Global registry instance
const globalRegistry = new AgentRegistry();

module.exports = {
  AgentRegistry,
  globalRegistry,
};
```

### Pattern 2: Agent Factory

**File**: `agents/factory/agent-factory.js`

```javascript
/**
 * Agent Factory
 *
 * Factory pattern for creating agents with configuration management,
 * validation, and instantiation strategies.
 */

const { globalRegistry } = require("../registry/agent-registry");

class AgentFactory {
  constructor(registry = globalRegistry) {
    this.registry = registry;
    this.creationStrategies = new Map();
    this.configValidators = new Map();
    this.postProcessors = new Map();

    this.registerDefaultStrategies();
  }

  /**
   * Register a creation strategy for an agent type
   */
  registerStrategy(agentType, strategy) {
    this.creationStrategies.set(agentType, strategy);
  }

  /**
   * Register a configuration validator
   */
  registerValidator(agentType, validator) {
    this.configValidators.set(agentType, validator);
  }

  /**
   * Register a post-processor
   */
  registerPostProcessor(agentType, processor) {
    this.postProcessors.set(agentType, processor);
  }

  /**
   * Create an agent instance
   */
  async create(agentType, config = {}, options = {}) {
    // Get agent metadata
    const metadata = this.registry.getMetadata(agentType);
    if (!metadata) {
      throw new Error(`Unknown agent type: ${agentType}`);
    }

    // Validate configuration
    const validatedConfig = await this.validateConfig(
      agentType,
      config,
      metadata,
    );

    // Select creation strategy
    const strategy =
      this.creationStrategies.get(agentType) ||
      this.creationStrategies.get("default");

    // Create instance
    const instance = await strategy.create(
      agentType,
      validatedConfig,
      options,
      this.registry,
    );

    // Apply post-processors
    const postProcessor = this.postProcessors.get(agentType);
    if (postProcessor) {
      await postProcessor.process(instance, validatedConfig, options);
    }

    return instance;
  }

  /**
   * Validate agent configuration
   */
  async validateConfig(agentType, config, metadata) {
    // Use registered validator if available
    const validator = this.configValidators.get(agentType);
    if (validator) {
      return await validator.validate(config, metadata);
    }

    // Default validation
    return this.defaultValidation(config, metadata);
  }

  /**
   * Default configuration validation
   */
  defaultValidation(config, metadata) {
    const validated = { ...config };

    // Apply schema defaults
    Object.entries(metadata.configSchema).forEach(([key, schema]) => {
      if (!(key in validated) && "default" in schema) {
        validated[key] = schema.default;
      }
    });

    // Type validation
    Object.entries(metadata.configSchema).forEach(([key, schema]) => {
      if (key in validated) {
        const value = validated[key];
        if (!this.validateType(value, schema.type)) {
          throw new Error(
            `Invalid type for ${key}: expected ${schema.type}, got ${typeof value}`,
          );
        }
      }
    });

    return validated;
  }

  /**
   * Validate value type
   */
  validateType(value, expectedType) {
    switch (expectedType) {
      case "string":
        return typeof value === "string";
      case "number":
        return typeof value === "number" && !isNaN(value);
      case "boolean":
        return typeof value === "boolean";
      case "array":
        return Array.isArray(value);
      case "object":
        return (
          typeof value === "object" && value !== null && !Array.isArray(value)
        );
      default:
        return true; // Unknown type, allow
    }
  }

  /**
   * Register default creation strategies
   */
  registerDefaultStrategies() {
    // Default strategy - use registry
    this.registerStrategy("default", {
      create: async (agentType, config, options, registry) => {
        return await registry.get(agentType, config);
      },
    });

    // Singleton strategy
    this.registerStrategy("singleton", {
      create: async (agentType, config, options, registry) => {
        const metadata = registry.getMetadata(agentType);
        if (!metadata.singleton) {
          throw new Error(`Agent ${agentType} is not configured as singleton`);
        }
        return await registry.get(agentType, config);
      },
    });

    // Pooled strategy
    this.registerStrategy("pooled", {
      create: async (agentType, config, options, registry) => {
        const metadata = registry.getMetadata(agentType);
        if (!metadata.poolable) {
          throw new Error(`Agent ${agentType} is not configured as poolable`);
        }
        return await registry.get(agentType, config);
      },
    });

    // Prototype strategy - always create new instance
    this.registerStrategy("prototype", {
      create: async (agentType, config, options, registry) => {
        const agentClass = registry.agents.get(agentType);
        return new agentClass(config);
      },
    });
  }

  /**
   * Create multiple agents at once
   */
  async createBatch(agentConfigs) {
    const results = new Map();
    const errors = [];

    // Create agents in parallel
    const promises = agentConfigs.map(async (config) => {
      try {
        const instance = await this.create(
          config.type,
          config.config,
          config.options,
        );
        results.set(config.name || config.type, instance);
      } catch (error) {
        errors.push({
          agent: config.name || config.type,
          error: error.message,
        });
      }
    });

    await Promise.allSettled(promises);

    return {
      instances: results,
      errors,
      success: errors.length === 0,
    };
  }

  /**
   * Create agent from specification
   */
  async createFromSpec(spec) {
    // Specification format:
    // {
    //   type: 'data-analyzer',
    //   config: { ... },
    //   dependencies: ['database', 'logger'],
    //   strategy: 'pooled',
    //   postProcessors: ['metrics', 'logging']
    // }

    const {
      type,
      config = {},
      dependencies = [],
      strategy,
      postProcessors = [],
    } = spec;

    // Ensure dependencies are available
    for (const dep of dependencies) {
      if (!this.registry.agents.has(dep)) {
        throw new Error(`Dependency not available: ${dep}`);
      }
    }

    // Set strategy if specified
    if (strategy) {
      spec.strategy = strategy;
    }

    // Apply post-processors
    for (const processor of postProcessors) {
      this.applyPostProcessor(type, processor);
    }

    return await this.create(type, config, spec);
  }

  /**
   * Apply a named post-processor
   */
  applyPostProcessor(agentType, processorName) {
    const processors = {
      metrics: (instance) => {
        // Add metrics wrapper
        const originalExecute = instance.execute.bind(instance);
        instance.execute = async (inputs, options) => {
          const start = Date.now();
          try {
            const result = await originalExecute(inputs, options);
            console.log(
              `Agent ${agentType} executed in ${Date.now() - start}ms`,
            );
            return result;
          } catch (error) {
            console.error(`Agent ${agentType} failed: ${error.message}`);
            throw error;
          }
        };
      },

      logging: (instance) => {
        // Add logging wrapper
        const originalExecute = instance.execute.bind(instance);
        instance.execute = async (inputs, options) => {
          console.log(`Executing ${agentType} with inputs:`, inputs);
          const result = await originalExecute(inputs, options);
          console.log(`Agent ${agentType} result:`, result);
          return result;
        };
      },

      caching: (instance) => {
        // Add caching wrapper
        instance._cache = new Map();
        const originalExecute = instance.execute.bind(instance);
        instance.execute = async (inputs, options) => {
          const key = JSON.stringify(inputs);
          if (instance._cache.has(key)) {
            return instance._cache.get(key);
          }
          const result = await originalExecute(inputs, options);
          instance._cache.set(key, result);
          return result;
        };
      },
    };

    if (processors[processorName]) {
      this.registerPostProcessor(agentType, {
        process: processors[processorName],
      });
    }
  }

  /**
   * Get factory statistics
   */
  getStats() {
    return {
      registeredStrategies: Array.from(this.creationStrategies.keys()),
      registeredValidators: Array.from(this.configValidators.keys()),
      registeredPostProcessors: Array.from(this.postProcessors.keys()),
      registryStats: this.registry.getStats(),
    };
  }
}

// Usage examples
async function setupAgentFactory() {
  const factory = new AgentFactory();

  // Register custom validator
  factory.registerValidator("data-analyzer", {
    validate: async (config, metadata) => {
      if (config.dataSource && !config.connectionString) {
        throw new Error(
          "connectionString required when dataSource is specified",
        );
      }
      return factory.defaultValidation(config, metadata);
    },
  });

  // Register custom post-processor
  factory.registerPostProcessor("data-analyzer", {
    process: async (instance, config, options) => {
      // Add custom initialization
      instance.metricsEnabled = config.enableMetrics || false;
    },
  });

  return factory;
}

async function createAgentsWithFactory() {
  const factory = await setupAgentFactory();

  // Create single agent
  const analyzer = await factory.create("data-analyzer", {
    dataSource: "database",
    connectionString: "mysql://...",
    enableMetrics: true,
  });

  // Create from specification
  const specAgent = await factory.createFromSpec({
    type: "report-generator",
    config: { format: "pdf", template: "sales" },
    dependencies: ["data-analyzer"],
    postProcessors: ["metrics", "logging"],
  });

  // Create batch
  const batchResult = await factory.createBatch([
    {
      name: "sales-analyzer",
      type: "data-analyzer",
      config: { dataSource: "sales_db" },
    },
    {
      name: "inventory-analyzer",
      type: "data-analyzer",
      config: { dataSource: "inventory_db" },
    },
  ]);

  return {
    analyzer,
    specAgent,
    batchResult,
  };
}

module.exports = { AgentFactory };
```

## 🏗️ PROJECT ORGANIZATION PATTERNS

### Pattern 3: Agent Project Structure

**File**: `project-structure.md`

```markdown
# Agent Project Structure

## Standard Directory Layout
```

agents/
├── registry/ # Agent registry and factory
│ ├── agent-registry.js # Central agent registry
│ └── agent-factory.js # Agent factory with strategies
│
├── conductor/ # Parent/Sub-Agent orchestration
│ ├── base.js # Base conductor class
│ └── specialized/ # Domain-specific conductors
│ ├── data-processing-conductor/
│ ├── bi-conductor/
│ └── self-healing-conductor/
│
├── categories/ # Agent categories by function
│ ├── data/ # Data processing agents
│ │ ├── extractor/
│ │ ├── transformer/
│ │ └── loader/
│ ├── analysis/ # Analysis and AI agents
│ │ ├── analyzer/
│ │ ├── predictor/
│ │ └── classifier/
│ ├── integration/ # External system integration
│ │ ├── api-client/
│ │ ├── webhook-handler/
│ │ └── message-queue/
│ └── utility/ # Utility and helper agents
│ ├── logger/
│ ├── validator/
│ └── formatter/
│
├── shared/ # Shared utilities and base classes
│ ├── base-agent.js # Base agent class
│ ├── mixins/ # Mixins for common functionality
│ ├── utils/ # Utility functions
│ └── schemas/ # JSON schemas for validation
│
├── config/ # Configuration management
│ ├── default-config.js # Default configurations
│ ├── environment-config.js # Environment-specific configs
│ └── config-validator.js # Configuration validation
│
├── monitoring/ # Monitoring and observability
│ ├── metrics-collector.js # Metrics collection
│ ├── health-checker.js # Health monitoring
│ └── alert-manager.js # Alert management
│
└── tests/ # Test infrastructure
├── unit/ # Unit tests
├── integration/ # Integration tests
├── fixtures/ # Test data and fixtures
└── helpers/ # Test helpers and utilities

````

## Agent Categories and Responsibilities

### Data Agents
- **ExtractorAgent**: Extract data from various sources (DB, API, files)
- **TransformerAgent**: Transform and normalize data
- **LoaderAgent**: Load data into target systems
- **ValidatorAgent**: Validate data quality and integrity

### Analysis Agents
- **AnalyzerAgent**: Perform data analysis and generate insights
- **PredictorAgent**: Make predictions using ML models
- **ClassifierAgent**: Classify data into categories
- **TrendAnalyzerAgent**: Identify trends and patterns

### Integration Agents
- **ApiClientAgent**: Handle external API communications
- **WebhookHandlerAgent**: Process incoming webhooks
- **MessageQueueAgent**: Handle message queue operations
- **DatabaseAgent**: Database operations and queries

### Utility Agents
- **LoggerAgent**: Centralized logging functionality
- **ValidatorAgent**: Input/output validation
- **FormatterAgent**: Data formatting and serialization
- **CacheAgent**: Caching layer for performance

## Naming Conventions

### Directory Names
- Use kebab-case: `data-extractor`, `api-client`
- Group related agents: `analysis/`, `integration/`
- Use descriptive names: `trend-analyzer`, not `analyzer`

### File Names
- Main agent file: `agent.js`
- Test files: `agent.test.js`
- Configuration: `config.js`
- Documentation: `README.md`

### Class Names
- Agent classes: `DataExtractorAgent`, `ApiClientAgent`
- Base classes: `BaseAgent`, `ConductorAgent`
- Utility classes: `AgentRegistry`, `AgentFactory`

## Configuration Management

### Configuration Hierarchy
1. **Default Config**: Built-in defaults in agent
2. **Environment Config**: Environment-specific overrides
3. **Instance Config**: Per-instance configuration
4. **Runtime Config**: Dynamic configuration changes

### Configuration Schema
```javascript
const configSchema = {
  type: 'object',
  properties: {
    timeout: {
      type: 'number',
      default: 30000,
      minimum: 1000,
      maximum: 300000
    },
    retries: {
      type: 'number',
      default: 3,
      minimum: 0,
      maximum: 10
    },
    enableMetrics: {
      type: 'boolean',
      default: true
    }
  },
  required: ['timeout']
};
````

## Dependency Management

### Agent Dependencies

- **Explicit Dependencies**: Declared in agent metadata
- **Optional Dependencies**: Loaded conditionally
- **Peer Dependencies**: Expected to be provided by consumer
- **Circular Dependencies**: Avoided through careful design

### Dependency Injection

```javascript
class DataProcessorAgent extends BaseAgent {
  constructor(config = {}) {
    super(config);

    // Injected dependencies
    this.database = config.dependencies?.database;
    this.logger = config.dependencies?.logger;
    this.cache = config.dependencies?.cache;
  }
}
```

## Lifecycle Management

### Agent Lifecycle States

- **registered**: Agent class registered with registry
- **instantiated**: Instance created
- **active**: Currently executing
- **idle**: Waiting for work
- **error**: In error state
- **disposed**: Cleaned up and disposed

### Lifecycle Hooks

```javascript
class LifecycleAgent extends BaseAgent {
  async initialize() {
    // Called after instantiation
    await this.setupConnections();
  }

  async execute(inputs, options) {
    // Main execution logic
    return await this.process(inputs);
  }

  async cleanup() {
    // Called before disposal
    await this.closeConnections();
  }

  async healthCheck() {
    // Health check implementation
    return { status: "healthy", details: {} };
  }
}
```

## Error Handling and Resilience

### Error Classification

- **Recoverable Errors**: Can retry (network timeouts, temporary failures)
- **Permanent Errors**: Cannot retry (invalid input, authentication failures)
- **Transient Errors**: May succeed on retry (resource contention, rate limits)

### Circuit Breaker Pattern

```javascript
class CircuitBreakerAgent extends BaseAgent {
  constructor(config = {}) {
    super(config);
    this.failureCount = 0;
    this.state = "closed"; // closed, open, half-open
    this.nextAttempt = 0;
  }

  async execute(inputs, options) {
    if (this.state === "open") {
      if (Date.now() < this.nextAttempt) {
        throw new Error("Circuit breaker is open");
      }
      this.state = "half-open";
    }

    try {
      const result = await this.wrappedAgent.execute(inputs, options);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = "closed";
  }

  onFailure() {
    this.failureCount++;
    if (this.failureCount >= this.config.failureThreshold) {
      this.state = "open";
      this.nextAttempt = Date.now() + this.config.timeout;
    }
  }
}
```

## Testing Strategy

### Test Categories

- **Unit Tests**: Test individual agent methods
- **Integration Tests**: Test agent interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test under load
- **Chaos Tests**: Test failure scenarios

### Test Structure

```
tests/
├── unit/
│   ├── agents/
│   │   ├── data-extractor.test.js
│   │   └── analyzer.test.js
│   └── registry/
│       └── agent-registry.test.js
├── integration/
│   ├── workflows/
│   │   └── data-processing-workflow.test.js
│   └── registry/
│       └── dependency-injection.test.js
├── e2e/
│   ├── scenarios/
│   │   └── complete-data-pipeline.test.js
└── fixtures/
    ├── sample-data.json
    └── mock-responses.json
```

### Test Utilities

```javascript
// Test agent base class
class TestAgent extends BaseAgent {
  async execute(inputs, options) {
    // Mock implementation for testing
    return { success: true, result: "test" };
  }
}

// Agent test helper
class AgentTestHelper {
  static async createTestAgent(type, config = {}) {
    const registry = new AgentRegistry();
    const factory = new AgentFactory(registry);

    // Register test agent
    registry.register(TestAgent, { name: type });

    return await factory.create(type, config);
  }

  static async mockDependencies(agent, mocks) {
    // Replace dependencies with mocks
    Object.assign(agent.config.dependencies, mocks);
  }
}
```

## Documentation Standards

### Agent Documentation Template

```markdown
# [AgentName] Agent

## Overview

Brief description of what this agent does.

## Capabilities

- Capability 1
- Capability 2
- Capability 3

## Configuration

\`\`\`javascript
const config = {
property1: 'value1',
property2: 'value2'
};
\`\`\`

## Input Schema

\`\`\`json
{
"type": "object",
"properties": {
"input1": { "type": "string" },
"input2": { "type": "number" }
}
}
\`\`\`

## Output Schema

\`\`\`json
{
"type": "object",
"properties": {
"result": { "type": "string" },
"metadata": { "type": "object" }
}
}
\`\`\`

## Dependencies

- dependency1: Description
- dependency2: Description

## Usage Examples

\`\`\`javascript
const agent = await registry.get('agent-name');
const result = await agent.execute({
input1: 'value',
input2: 42
});
\`\`\`

## Error Handling

Description of error conditions and handling.

## Performance Characteristics

Expected performance metrics and limitations.
```

## Deployment and Scaling

### Deployment Strategies

- **Single Instance**: Simple deployment for low-traffic agents
- **Load Balanced**: Multiple instances behind load balancer
- **Geographic Distribution**: Instances in multiple regions
- **Serverless**: Deploy as serverless functions

### Scaling Patterns

- **Horizontal Scaling**: Add more instances
- **Vertical Scaling**: Increase instance resources
- **Auto-scaling**: Scale based on metrics
- **Circuit Breaker**: Prevent cascade failures

### Resource Management

```javascript
class ResourceManagedAgent extends BaseAgent {
  constructor(config = {}) {
    super(config);
    this.resourcePool = new ResourcePool({
      maxConnections: config.maxConnections || 10,
      acquireTimeout: config.acquireTimeout || 30000,
    });
  }

  async execute(inputs, options) {
    const resource = await this.resourcePool.acquire();

    try {
      return await this.processWithResource(inputs, resource);
    } finally {
      this.resourcePool.release(resource);
    }
  }
}
```

## Monitoring and Observability

### Metrics Collection

- **Execution Metrics**: Duration, success rate, error rate
- **Resource Metrics**: CPU, memory, network usage
- **Business Metrics**: Throughput, data processed
- **Health Metrics**: Response time, availability

### Logging Strategy

- **Structured Logging**: JSON format with consistent fields
- **Log Levels**: ERROR, WARN, INFO, DEBUG
- **Context Propagation**: Include request IDs and correlation IDs
- **Log Aggregation**: Centralized log collection and analysis

### Alerting Rules

- **Performance Alerts**: High latency, high error rates
- **Resource Alerts**: High CPU/memory usage
- **Business Alerts**: Low throughput, data quality issues
- **Health Alerts**: Instance failures, dependency issues

This comprehensive project organization provides a solid foundation for building scalable, maintainable agent systems with clear patterns for development, testing, deployment, and operations.

````

## 📊 REGISTRY MONITORING & ANALYTICS

### Pattern 4: Registry Analytics

**File**: `agents/registry/registry-analytics.js`

```javascript
/**
 * Registry Analytics
 *
 * Advanced analytics and insights for agent registry performance,
 * usage patterns, and optimization recommendations.
 */

const { globalRegistry } = require('./agent-registry');

class RegistryAnalytics {
  constructor(registry = globalRegistry) {
    this.registry = registry;
    this.analytics = {
      usage: new Map(),
      performance: new Map(),
      errors: new Map(),
      dependencies: new Map(),
      trends: []
    };

    this.collectionInterval = 60000; // 1 minute
    this.retentionPeriod = 86400000 * 7; // 7 days
  }

  /**
   * Start analytics collection
   */
  startCollection() {
    this.collectionTimer = setInterval(() => {
      this.collectMetrics();
    }, this.collectionInterval);

    console.log('📊 Registry analytics collection started');
  }

  /**
   * Stop analytics collection
   */
  stopCollection() {
    if (this.collectionTimer) {
      clearInterval(this.collectionTimer);
      this.collectionTimer = null;
    }

    console.log('📊 Registry analytics collection stopped');
  }

  /**
   * Collect current metrics
   */
  collectMetrics() {
    const timestamp = new Date();
    const stats = this.registry.getStats();

    // Collect usage metrics
    this.collectUsageMetrics(timestamp);

    // Collect performance metrics
    this.collectPerformanceMetrics(timestamp, stats);

    // Collect error metrics
    this.collectErrorMetrics(timestamp);

    // Collect dependency metrics
    this.collectDependencyMetrics(timestamp);

    // Clean old data
    this.cleanupOldData();
  }

  /**
   * Collect usage metrics
   */
  collectUsageMetrics(timestamp) {
    const agents = this.registry.listAgents();

    agents.forEach(agent => {
      const key = agent.name;
      if (!this.analytics.usage.has(key)) {
        this.analytics.usage.set(key, []);
      }

      this.analytics.usage.get(key).push({
        timestamp,
        executions: agent.stats.totalExecutions,
        activeInstances: agent.stats.activeInstances,
        totalInstances: agent.stats.totalInstances
      });
    });
  }

  /**
   * Collect performance metrics
   */
  collectPerformanceMetrics(timestamp, stats) {
    this.analytics.performance.set(timestamp.getTime(), {
      timestamp,
      totalAgents: stats.totalAgents,
      totalInstances: stats.totalInstances,
      activeInstances: stats.activeInstances,
      totalExecutions: stats.totalExecutions,
      errorRate: stats.errorRate,
      averageExecutionTime: stats.averageExecutionTime,
      agentsByCategory: stats.agentsByCategory
    });
  }

  /**
   * Collect error metrics
   */
  collectErrorMetrics(timestamp) {
    const agents = this.registry.listAgents();

    agents.forEach(agent => {
      const key = agent.name;
      if (!this.analytics.errors.has(key)) {
        this.analytics.errors.set(key, []);
      }

      this.analytics.errors.get(key).push({
        timestamp,
        errors: agent.stats.errors,
        errorRate: agent.stats.totalExecutions > 0 ?
          (agent.stats.errors / agent.stats.totalExecutions) : 0
      });
    });
  }

  /**
   * Collect dependency metrics
   */
  collectDependencyMetrics(timestamp) {
    const agents = this.registry.listAgents();

    agents.forEach(agent => {
      const key = agent.name;
      const dependencies = this.registry.getDependencies(key);
      const dependents = this.registry.getDependents(key);

      if (!this.analytics.dependencies.has(key)) {
        this.analytics.dependencies.set(key, []);
      }

      this.analytics.dependencies.get(key).push({
        timestamp,
        dependencies: dependencies.length,
        dependents: dependents.length,
        dependencyList: dependencies,
        dependentList: dependents
      });
    });
  }

  /**
   * Clean up old analytics data
   */
  cleanupOldData() {
    const cutoff = Date.now() - this.retentionPeriod;

    // Clean usage data
    for (const [key, data] of this.analytics.usage) {
      this.analytics.usage.set(key, data.filter(d => d.timestamp.getTime() > cutoff));
    }

    // Clean performance data
    for (const [timestamp, data] of this.analytics.performance) {
      if (timestamp < cutoff) {
        this.analytics.performance.delete(timestamp);
      }
    }

    // Clean error data
    for (const [key, data] of this.analytics.errors) {
      this.analytics.errors.set(key, data.filter(d => d.timestamp.getTime() > cutoff));
    }

    // Clean dependency data
    for (const [key, data] of this.analytics.dependencies) {
      this.analytics.dependencies.set(key, data.filter(d => d.timestamp.getTime() > cutoff));
    }
  }

  /**
   * Get usage analytics for an agent
   */
  getUsageAnalytics(agentName, timeRange = '1h') {
    const data = this.analytics.usage.get(agentName);
    if (!data) return null;

    const filtered = this.filterByTimeRange(data, timeRange);

    return {
      agent: agentName,
      timeRange,
      dataPoints: filtered.length,
      averageExecutions: this.calculateAverage(filtered, 'executions'),
      peakActiveInstances: Math.max(...filtered.map(d => d.activeInstances)),
      totalInstancesCreated: filtered[filtered.length - 1]?.totalInstances || 0,
      usageTrend: this.calculateTrend(filtered, 'executions')
    };
  }

  /**
   * Get performance analytics
   */
  getPerformanceAnalytics(timeRange = '1h') {
    const data = Array.from(this.analytics.performance.values());
    const filtered = this.filterByTimeRange(data, timeRange);

    if (filtered.length === 0) return null;

    return {
      timeRange,
      dataPoints: filtered.length,
      averageExecutionTime: this.calculateAverage(filtered, 'averageExecutionTime'),
      totalExecutions: filtered.reduce((sum, d) => sum + d.totalExecutions, 0),
      errorRate: this.calculateAverage(filtered, 'errorRate'),
      agentGrowth: this.calculateTrend(filtered, 'totalAgents'),
      instanceUtilization: this.calculateAverage(filtered, 'activeInstances') /
                          this.calculateAverage(filtered, 'totalInstances') * 100
    };
  }

  /**
   * Get error analytics
   */
  getErrorAnalytics(agentName = null, timeRange = '1h') {
    let data;

    if (agentName) {
      data = this.analytics.errors.get(agentName);
    } else {
      // Aggregate across all agents
      data = [];
      for (const agentData of this.analytics.errors.values()) {
        data.push(...agentData);
      }
      // Group by timestamp
      const grouped = new Map();
      data.forEach(d => {
        const key = d.timestamp.getTime();
        if (!grouped.has(key)) {
          grouped.set(key, { timestamp: d.timestamp, totalErrors: 0, agentsWithErrors: 0 });
        }
        grouped.get(key).totalErrors += d.errors;
        if (d.errors > 0) grouped.get(key).agentsWithErrors++;
      });
      data = Array.from(grouped.values());
    }

    if (!data) return null;

    const filtered = this.filterByTimeRange(data, timeRange);

    return {
      agent: agentName || 'all',
      timeRange,
      dataPoints: filtered.length,
      totalErrors: filtered.reduce((sum, d) => sum + (d.errors || d.totalErrors), 0),
      averageErrorRate: this.calculateAverage(filtered, 'errorRate'),
      errorTrend: this.calculateTrend(filtered, agentName ? 'errors' : 'totalErrors'),
      agentsAffected: agentName ? 1 : Math.max(...filtered.map(d => d.agentsWithErrors || 1))
    };
  }

  /**
   * Get dependency analytics
   */
  getDependencyAnalytics() {
    const agents = this.registry.listAgents();
    const dependencyGraph = {
      nodes: [],
      edges: []
    };

    // Build dependency graph
    agents.forEach(agent => {
      dependencyGraph.nodes.push({
        id: agent.name,
        label: agent.name,
        category: agent.category,
        executions: agent.stats.totalExecutions
      });

      const dependencies = this.registry.getDependencies(agent.name);
      dependencies.forEach(dep => {
        dependencyGraph.edges.push({
          from: agent.name,
          to: dep,
          type: 'depends_on'
        });
      });
    });

    // Calculate dependency metrics
    const metrics = {
      totalDependencies: dependencyGraph.edges.length,
      averageDependenciesPerAgent: dependencyGraph.edges.length / agents.length,
      mostDependedOn: this.findMostDependedOn(dependencyGraph),
      dependencyChains: this.findDependencyChains(dependencyGraph),
      circularDependencies: this.detectCircularDependencies(dependencyGraph)
    };

    return {
      graph: dependencyGraph,
      metrics
    };
  }

  /**
   * Find most depended upon agents
   */
  findMostDependedOn(graph) {
    const counts = new Map();

    graph.edges.forEach(edge => {
      counts.set(edge.to, (counts.get(edge.to) || 0) + 1);
    });

    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([agent, count]) => ({ agent, dependents: count }));
  }

  /**
   * Find dependency chains
   */
  findDependencyChains(graph) {
    const chains = [];

    // Simple chain detection (can be enhanced with more sophisticated algorithms)
    graph.nodes.forEach(node => {
      const chain = this.findChainFromNode(graph, node.id, new Set());
      if (chain.length > 2) { // Only report chains longer than 2
        chains.push(chain);
      }
    });

    return chains.slice(0, 10); // Limit to top 10
  }

  /**
   * Find chain from a starting node
   */
  findChainFromNode(graph, startNode, visited) {
    if (visited.has(startNode)) return [];

    visited.add(startNode);
    const chain = [startNode];

    const outgoing = graph.edges.filter(e => e.from === startNode);
    if (outgoing.length > 0) {
      // Follow first dependency (can be enhanced to follow all paths)
      const nextNode = outgoing[0].to;
      const restOfChain = this.findChainFromNode(graph, nextNode, new Set(visited));
      chain.push(...restOfChain);
    }

    return chain;
  }

  /**
   * Detect circular dependencies
   */
  detectCircularDependencies(graph) {
    const circularDeps = [];

    graph.nodes.forEach(node => {
      const visited = new Set();
      const recursionStack = new Set();

      if (this.hasCircularDependency(graph, node.id, visited, recursionStack)) {
        // Find the actual cycle (simplified)
        circularDeps.push({
          involved: Array.from(recursionStack),
          description: `Circular dependency involving: ${Array.from(recursionStack).join(' -> ')}`
        });
      }
    });

    return circularDeps;
  }

  /**
   * Check for circular dependency using DFS
   */
  hasCircularDependency(graph, node, visited, recursionStack) {
    visited.add(node);
    recursionStack.add(node);

    const outgoing = graph.edges.filter(e => e.from === node);
    for (const edge of outgoing) {
      if (!visited.has(edge.to)) {
        if (this.hasCircularDependency(graph, edge.to, visited, recursionStack)) {
          return true;
        }
      } else if (recursionStack.has(edge.to)) {
        return true;
      }
    }

    recursionStack.delete(node);
    return false;
  }

  /**
   * Generate optimization recommendations
   */
  generateRecommendations() {
    const recommendations = [];
    const performance = this.getPerformanceAnalytics('24h');
    const errors = this.getErrorAnalytics(null, '24h');

    // Performance recommendations
    if (performance && performance.averageExecutionTime > 60000) { // 1 minute
      recommendations.push({
        type: 'performance',
        priority: 'high',
        message: 'High average execution time detected. Consider optimizing slow agents.',
        metric: `Average: ${Math.round(performance.averageExecutionTime)}ms`
      });
    }

    // Error recommendations
    if (errors && errors.totalErrors > 10) {
      recommendations.push({
        type: 'reliability',
        priority: 'high',
        message: 'High error count detected. Review error patterns and implement retry logic.',
        metric: `Total errors: ${errors.totalErrors}`
      });
    }

    // Usage recommendations
    const agents = this.registry.listAgents();
    const lowUsageAgents = agents.filter(a => a.stats.totalExecutions < 5);

    if (lowUsageAgents.length > 0) {
      recommendations.push({
        type: 'optimization',
        priority: 'medium',
        message: 'Low usage agents detected. Consider removing unused agents.',
        agents: lowUsageAgents.map(a => a.name)
      });
    }

    // Dependency recommendations
    const depAnalytics = this.getDependencyAnalytics();

    if (depAnalytics.metrics.circularDependencies.length > 0) {
      recommendations.push({
        type: 'architecture',
        priority: 'high',
        message: 'Circular dependencies detected. Refactor to break dependency cycles.',
        details: depAnalytics.metrics.circularDependencies
      });
    }

    return recommendations;
  }

  /**
   * Utility methods
   */
  filterByTimeRange(data, timeRange) {
    const now = Date.now();
    const ranges = {
      '1h': 3600000,
      '6h': 21600000,
      '24h': 86400000,
      '7d': 604800000
    };

    const range = ranges[timeRange] || ranges['1h'];
    const cutoff = now - range;

    return data.filter(d => d.timestamp.getTime() > cutoff);
  }

  calculateAverage(data, field) {
    if (data.length === 0) return 0;
    const sum = data.reduce((acc, d) => acc + (d[field] || 0), 0);
    return sum / data.length;
  }

  calculateTrend(data, field) {
    if (data.length < 2) return 0;

    const first = data[0][field] || 0;
    const last = data[data.length - 1][field] || 0;
    const change = last - first;

    return {
      change,
      percentage: first > 0 ? (change / first) * 100 : 0,
      direction: change > 0 ? 'increasing' : change < 0 ? 'decreasing' : 'stable'
    };
  }

  /**
   * Export analytics data
   */
  exportData(format = 'json') {
    const data = {
      timestamp: new Date(),
      performance: Object.fromEntries(this.analytics.performance),
      usage: Object.fromEntries(this.analytics.usage),
      errors: Object.fromEntries(this.analytics.errors),
      dependencies: Object.fromEntries(this.analytics.dependencies),
      summary: this.getPerformanceAnalytics('24h')
    };

    if (format === 'json') {
      return JSON.stringify(data, null, 2);
    }

    // Could add CSV, XML formats here
    return data;
  }
}

// Usage example
async function setupRegistryAnalytics() {
  const analytics = new RegistryAnalytics();

  // Start collection
  analytics.startCollection();

  // Generate reports periodically
  setInterval(() => {
    const report = {
      performance: analytics.getPerformanceAnalytics(),
      recommendations: analytics.generateRecommendations(),
      topAgents: analytics.getUsageAnalytics(null, '24h')
    };

    console.log('📊 Analytics Report:', report);
  }, 300000); // Every 5 minutes

  return analytics;
}

module.exports = { RegistryAnalytics };
````

## 📋 SUMMARY

### Project Organization & Registry Patterns Summary

| Pattern                | Purpose                      | Key Features                                      | Use Case                      |
| ---------------------- | ---------------------------- | ------------------------------------------------- | ----------------------------- |
| **Agent Registry**     | Centralized agent management | Registration, instantiation, dependency injection | All agent systems             |
| **Agent Factory**      | Configurable agent creation  | Strategies, validation, post-processing           | Complex agent instantiation   |
| **Project Structure**  | Standardized organization    | Categories, naming, lifecycle                     | Large-scale agent development |
| **Registry Analytics** | Performance monitoring       | Usage tracking, optimization recommendations      | Production agent systems      |

### Best Practices

✅ **Registry First**: Always register agents with the registry for discoverability  
✅ **Dependency Injection**: Use constructor injection for testability and flexibility  
✅ **Factory Pattern**: Use factories for complex instantiation logic  
✅ **Singleton Wisely**: Only use singletons for truly shared resources  
✅ **Pool Resources**: Use object pooling for expensive resources  
✅ **Monitor Everything**: Comprehensive metrics and analytics for optimization  
✅ **Version Carefully**: Semantic versioning for agent compatibility  
✅ **Document Thoroughly**: Complete documentation for each agent

### When to Use Registry Pattern

- **Multiple Agents**: Systems with many agent types
- **Dynamic Loading**: Agents loaded at runtime
- **Dependency Management**: Complex inter-agent dependencies
- **Monitoring**: Need centralized metrics and health checks
- **Scaling**: Systems that need to scale agent instances
- **Testing**: Need mock agents and test isolation

This organization provides a robust foundation for building and managing complex agent ecosystems with proper governance, monitoring, and scalability.</content>
<parameter name="filePath">c:\wamp64\www\birdc_erp\skills\custom-sub-agents\references\07-project-organization.md
