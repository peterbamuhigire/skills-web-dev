# 🚀 Integration & Deployment Patterns

## 🎯 AGENT INTEGRATION FRAMEWORKS

**Purpose**: Seamless integration of agents with external systems, APIs, and deployment environments.

### Pattern 1: Agent API Gateway

**File**: `agents/integration/api-gateway.js`

```javascript
/**
 * Agent API Gateway
 *
 * RESTful API gateway for agent execution, providing HTTP endpoints
 * for agent discovery, execution, monitoring, and management.
 */

const express = require("express");
const { globalRegistry } = require("../registry/agent-registry");
const { RegistryAnalytics } = require("../registry/registry-analytics");

class AgentApiGateway {
  constructor(config = {}) {
    this.config = {
      port: 3000,
      host: "localhost",
      enableCors: true,
      enableAuth: false,
      enableMetrics: true,
      requestTimeout: 300000, // 5 minutes
      rateLimit: {
        windowMs: 60000, // 1 minute
        maxRequests: 100,
      },
      ...config,
    };

    this.app = express();
    this.registry = globalRegistry;
    this.analytics = new RegistryAnalytics(this.registry);

    this.setupMiddleware();
    this.setupRoutes();
    this.setupErrorHandling();
  }

  /**
   * Setup Express middleware
   */
  setupMiddleware() {
    // Body parsing
    this.app.use(express.json({ limit: "10mb" }));
    this.app.use(express.urlencoded({ extended: true }));

    // CORS
    if (this.config.enableCors) {
      this.app.use((req, res, next) => {
        res.header("Access-Control-Allow-Origin", "*");
        res.header(
          "Access-Control-Allow-Methods",
          "GET, POST, PUT, DELETE, OPTIONS",
        );
        res.header(
          "Access-Control-Allow-Headers",
          "Origin, X-Requested-With, Content-Type, Accept, Authorization",
        );
        if (req.method === "OPTIONS") {
          res.sendStatus(200);
        } else {
          next();
        }
      });
    }

    // Request logging
    this.app.use((req, res, next) => {
      const start = Date.now();
      console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);

      res.on("finish", () => {
        const duration = Date.now() - start;
        console.log(
          `${new Date().toISOString()} ${req.method} ${req.path} ${res.statusCode} ${duration}ms`,
        );
      });

      next();
    });

    // Rate limiting (simple implementation)
    if (this.config.rateLimit) {
      const requests = new Map();

      this.app.use((req, res, next) => {
        const key = req.ip;
        const now = Date.now();
        const windowStart = now - this.config.rateLimit.windowMs;

        if (!requests.has(key)) {
          requests.set(key, []);
        }

        const userRequests = requests.get(key);
        const recentRequests = userRequests.filter(
          (time) => time > windowStart,
        );

        if (recentRequests.length >= this.config.rateLimit.maxRequests) {
          return res.status(429).json({
            error: "Too many requests",
            retryAfter: Math.ceil(
              (recentRequests[0] + this.config.rateLimit.windowMs - now) / 1000,
            ),
          });
        }

        recentRequests.push(now);
        requests.set(key, recentRequests);
        next();
      });
    }

    // Request timeout
    this.app.use((req, res, next) => {
      res.setTimeout(this.config.requestTimeout, () => {
        res.status(408).json({ error: "Request timeout" });
      });
      next();
    });
  }

  /**
   * Setup API routes
   */
  setupRoutes() {
    const router = express.Router();

    // Health check
    router.get("/health", this.handleHealthCheck.bind(this));

    // Agent discovery
    router.get("/agents", this.handleListAgents.bind(this));
    router.get("/agents/:name", this.handleGetAgent.bind(this));

    // Agent execution
    router.post("/agents/:name/execute", this.handleExecuteAgent.bind(this));

    // Batch execution
    router.post("/batch/execute", this.handleBatchExecute.bind(this));

    // Registry management
    router.post("/agents", this.handleRegisterAgent.bind(this));
    router.delete("/agents/:name", this.handleUnregisterAgent.bind(this));

    // Analytics and monitoring
    router.get("/analytics", this.handleGetAnalytics.bind(this));
    router.get("/metrics", this.handleGetMetrics.bind(this));

    // Workflow execution
    router.post(
      "/workflows/:name/execute",
      this.handleExecuteWorkflow.bind(this),
    );

    this.app.use("/api/v1", router);
  }

  /**
   * Setup error handling
   */
  setupErrorHandling() {
    // 404 handler
    this.app.use((req, res) => {
      res.status(404).json({
        error: "Not found",
        path: req.path,
        method: req.method,
      });
    });

    // General error handler
    this.app.use((error, req, res, next) => {
      console.error("API Error:", error);

      const statusCode = error.statusCode || 500;
      const message = error.message || "Internal server error";

      res.status(statusCode).json({
        error: message,
        timestamp: new Date().toISOString(),
        path: req.path,
      });
    });
  }

  /**
   * Health check endpoint
   */
  async handleHealthCheck(req, res) {
    try {
      const health = await this.registry.healthCheck();
      const status = health.overall === "healthy" ? 200 : 503;

      res.status(status).json({
        status: health.overall,
        timestamp: new Date().toISOString(),
        version: "1.0.0",
        registry: health,
      });
    } catch (error) {
      res.status(503).json({
        status: "error",
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * List all agents
   */
  handleListAgents(req, res) {
    try {
      const { category, capability, tag } = req.query;
      let agents = this.registry.listAgents(category);

      if (capability) {
        agents = agents.filter((agent) =>
          agent.capabilities.includes(capability),
        );
      }

      if (tag) {
        agents = agents.filter((agent) => agent.tags.includes(tag));
      }

      res.json({
        agents: agents.map((agent) => ({
          name: agent.name,
          category: agent.category,
          description: agent.description,
          version: agent.version,
          capabilities: agent.capabilities,
          tags: agent.tags,
          stats: agent.stats,
        })),
        total: agents.length,
      });
    } catch (error) {
      throw new Error(`Failed to list agents: ${error.message}`);
    }
  }

  /**
   * Get agent details
   */
  handleGetAgent(req, res) {
    try {
      const { name } = req.params;
      const metadata = this.registry.getMetadata(name);

      if (!metadata) {
        return res.status(404).json({ error: "Agent not found" });
      }

      const stats = this.registry.instanceStats.get(name);
      const dependencies = this.registry.getDependencies(name);
      const dependents = this.registry.getDependents(name);

      res.json({
        ...metadata,
        stats,
        dependencies,
        dependents,
      });
    } catch (error) {
      throw new Error(`Failed to get agent: ${error.message}`);
    }
  }

  /**
   * Execute agent
   */
  async handleExecuteAgent(req, res) {
    try {
      const { name } = req.params;
      const { inputs, options = {} } = req.body;

      if (!inputs) {
        return res.status(400).json({ error: "Inputs required" });
      }

      // Validate agent exists
      if (!this.registry.agents.has(name)) {
        return res.status(404).json({ error: "Agent not found" });
      }

      // Execute agent
      const result = await this.registry.execute(name, inputs, options);

      res.json({
        executionId: result.executionId,
        success: result.success,
        result: result.result,
        duration: result.duration,
      });
    } catch (error) {
      throw new Error(`Agent execution failed: ${error.message}`);
    }
  }

  /**
   * Batch execute agents
   */
  async handleBatchExecute(req, res) {
    try {
      const { executions } = req.body;

      if (!Array.isArray(executions)) {
        return res.status(400).json({ error: "Executions array required" });
      }

      const results = await Promise.allSettled(
        executions.map(async (execution, index) => {
          try {
            const result = await this.registry.execute(
              execution.agent,
              execution.inputs,
              execution.options,
            );
            return {
              index,
              success: true,
              result: result.result,
              duration: result.duration,
            };
          } catch (error) {
            return {
              index,
              success: false,
              error: error.message,
            };
          }
        }),
      );

      const response = {
        total: executions.length,
        successful: results.filter(
          (r) => r.status === "fulfilled" && r.value.success,
        ).length,
        failed: results.filter(
          (r) => r.status === "rejected" || !r.value.success,
        ).length,
        results: results.map((result, index) => ({
          execution: executions[index],
          ...result.value,
        })),
      };

      res.json(response);
    } catch (error) {
      throw new Error(`Batch execution failed: ${error.message}`);
    }
  }

  /**
   * Register new agent
   */
  handleRegisterAgent(req, res) {
    try {
      const { class: AgentClass, options = {} } = req.body;

      if (!AgentClass) {
        return res.status(400).json({ error: "Agent class required" });
      }

      const agentName = this.registry.register(AgentClass, options);

      res.status(201).json({
        message: "Agent registered successfully",
        name: agentName,
      });
    } catch (error) {
      throw new Error(`Agent registration failed: ${error.message}`);
    }
  }

  /**
   * Unregister agent
   */
  handleUnregisterAgent(req, res) {
    try {
      const { name } = req.params;

      const canRemove = this.registry.canRemove(name);
      if (!canRemove.canRemove) {
        return res.status(400).json({
          error: "Cannot remove agent",
          reasons: {
            dependents: canRemove.dependents,
            hasActiveInstances: canRemove.hasActiveInstances,
          },
        });
      }

      this.registry.remove(name);

      res.json({ message: "Agent removed successfully" });
    } catch (error) {
      throw new Error(`Agent removal failed: ${error.message}`);
    }
  }

  /**
   * Get analytics
   */
  handleGetAnalytics(req, res) {
    try {
      const { timeRange = "1h" } = req.query;

      const analytics = {
        performance: this.analytics.getPerformanceAnalytics(timeRange),
        recommendations: this.analytics.generateRecommendations(),
      };

      res.json(analytics);
    } catch (error) {
      throw new Error(`Failed to get analytics: ${error.message}`);
    }
  }

  /**
   * Get metrics
   */
  handleGetMetrics(req, res) {
    try {
      const { agent } = req.query;

      let metrics;
      if (agent) {
        metrics = this.analytics.getUsageAnalytics(agent);
      } else {
        metrics = this.analytics.getPerformanceAnalytics();
      }

      res.json(metrics);
    } catch (error) {
      throw new Error(`Failed to get metrics: ${error.message}`);
    }
  }

  /**
   * Execute workflow
   */
  async handleExecuteWorkflow(req, res) {
    try {
      const { name } = req.params;
      const { inputs, options = {} } = req.body;

      // This would integrate with conductor agents
      // For now, return not implemented
      res.status(501).json({
        error: "Workflow execution not yet implemented",
        workflow: name,
      });
    } catch (error) {
      throw new Error(`Workflow execution failed: ${error.message}`);
    }
  }

  /**
   * Start the API gateway
   */
  async start() {
    return new Promise((resolve, reject) => {
      try {
        this.server = this.app.listen(
          this.config.port,
          this.config.host,
          () => {
            console.log(
              `🚀 Agent API Gateway listening on ${this.config.host}:${this.config.port}`,
            );
            console.log(
              `📊 Analytics collection: ${this.config.enableMetrics ? "enabled" : "disabled"}`,
            );

            if (this.config.enableMetrics) {
              this.analytics.startCollection();
            }

            resolve(this.server);
          },
        );

        this.server.on("error", reject);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Stop the API gateway
   */
  async stop() {
    return new Promise((resolve) => {
      if (this.analytics) {
        this.analytics.stopCollection();
      }

      if (this.server) {
        this.server.close(() => {
          console.log("🛑 Agent API Gateway stopped");
          resolve();
        });
      } else {
        resolve();
      }
    });
  }
}

// Usage example
async function startAgentApiGateway() {
  const gateway = new AgentApiGateway({
    port: 3000,
    enableMetrics: true,
    rateLimit: {
      windowMs: 60000,
      maxRequests: 100,
    },
  });

  await gateway.start();

  // Graceful shutdown
  process.on("SIGINT", async () => {
    console.log("Shutting down gracefully...");
    await gateway.stop();
    process.exit(0);
  });

  return gateway;
}

module.exports = { AgentApiGateway };
```

### Pattern 2: Agent CLI Tool

**File**: `agents/integration/cli-tool.js`

```javascript
/**
 * Agent CLI Tool
 *
 * Command-line interface for agent management, execution, and debugging.
 * Provides commands for registry operations, agent execution, and system monitoring.
 */

const { Command } = require("commander");
const { globalRegistry } = require("../registry/agent-registry");
const { RegistryAnalytics } = require("../registry/registry-analytics");
const fs = require("fs").promises;
const path = require("path");

class AgentCliTool {
  constructor() {
    this.registry = globalRegistry;
    this.analytics = new RegistryAnalytics(this.registry);
    this.program = new Command();

    this.setupCommands();
  }

  /**
   * Setup CLI commands
   */
  setupCommands() {
    this.program
      .name("agent-cli")
      .description("Agent CLI Tool for management and execution")
      .version("1.0.0");

    // Registry commands
    this.program
      .command("list")
      .description("List all registered agents")
      .option("-c, --category <category>", "Filter by category")
      .option("-t, --tag <tag>", "Filter by tag")
      .option("--json", "Output as JSON")
      .action(this.handleList.bind(this));

    this.program
      .command("info <name>")
      .description("Get detailed information about an agent")
      .option("--json", "Output as JSON")
      .action(this.handleInfo.bind(this));

    this.program
      .command("register <file>")
      .description("Register an agent from a file")
      .option("-n, --name <name>", "Agent name")
      .option("-c, --category <category>", "Agent category")
      .action(this.handleRegister.bind(this));

    this.program
      .command("unregister <name>")
      .description("Unregister an agent")
      .action(this.handleUnregister.bind(this));

    // Execution commands
    this.program
      .command("execute <name>")
      .description("Execute an agent")
      .option("-i, --input <file>", "Input file (JSON)")
      .option("-o, --output <file>", "Output file")
      .option("--json", "Output as JSON")
      .action(this.handleExecute.bind(this));

    this.program
      .command("batch <file>")
      .description("Execute multiple agents from a batch file")
      .option("-o, --output <file>", "Output file")
      .option("--json", "Output as JSON")
      .action(this.handleBatch.bind(this));

    // Monitoring commands
    this.program
      .command("health")
      .description("Check system health")
      .option("--json", "Output as JSON")
      .action(this.handleHealth.bind(this));

    this.program
      .command("metrics")
      .description("Show system metrics")
      .option("-a, --agent <name>", "Show metrics for specific agent")
      .option("-t, --time-range <range>", "Time range (1h, 6h, 24h, 7d)", "1h")
      .option("--json", "Output as JSON")
      .action(this.handleMetrics.bind(this));

    this.program
      .command("analytics")
      .description("Show analytics and recommendations")
      .option("-t, --time-range <range>", "Time range (1h, 6h, 24h, 7d)", "24h")
      .option("--json", "Output as JSON")
      .action(this.handleAnalytics.bind(this));

    // Development commands
    this.program
      .command("test <name>")
      .description("Run tests for an agent")
      .option("--watch", "Watch mode")
      .action(this.handleTest.bind(this));

    this.program
      .command("validate <name>")
      .description("Validate agent configuration")
      .action(this.handleValidate.bind(this));

    // Utility commands
    this.program
      .command("export")
      .description("Export registry data")
      .option("-f, --format <format>", "Export format (json, csv)", "json")
      .option("-o, --output <file>", "Output file")
      .action(this.handleExport.bind(this));

    this.program
      .command("import <file>")
      .description("Import registry data")
      .action(this.handleImport.bind(this));
  }

  /**
   * Handle list command
   */
  async handleList(options) {
    try {
      let agents = this.registry.listAgents(options.category);

      if (options.tag) {
        agents = agents.filter((agent) => agent.tags.includes(options.tag));
      }

      if (options.json) {
        console.log(JSON.stringify(agents, null, 2));
      } else {
        console.log(`📋 Registered Agents (${agents.length})\n`);

        const categories = {};
        agents.forEach((agent) => {
          if (!categories[agent.category]) {
            categories[agent.category] = [];
          }
          categories[agent.category].push(agent);
        });

        Object.entries(categories).forEach(([category, categoryAgents]) => {
          console.log(`\n${category.toUpperCase()}:`);
          categoryAgents.forEach((agent) => {
            const status = agent.lifecycle === "active" ? "🟢" : "🟡";
            console.log(`  ${status} ${agent.name} - ${agent.description}`);
            console.log(
              `     Executions: ${agent.stats.totalExecutions}, Errors: ${agent.stats.errors}`,
            );
          });
        });
      }
    } catch (error) {
      console.error("Error listing agents:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle info command
   */
  async handleInfo(name, options) {
    try {
      const metadata = this.registry.getMetadata(name);
      if (!metadata) {
        console.error(`Agent '${name}' not found`);
        process.exit(1);
      }

      const stats = this.registry.instanceStats.get(name);
      const dependencies = this.registry.getDependencies(name);
      const dependents = this.registry.getDependents(name);

      const info = {
        ...metadata,
        stats,
        dependencies,
        dependents,
      };

      if (options.json) {
        console.log(JSON.stringify(info, null, 2));
      } else {
        console.log(`📋 Agent Information: ${name}\n`);
        console.log(`Category: ${metadata.category}`);
        console.log(`Description: ${metadata.description}`);
        console.log(`Version: ${metadata.version}`);
        console.log(`Author: ${metadata.author}`);
        console.log(`Capabilities: ${metadata.capabilities.join(", ")}`);
        console.log(`Tags: ${metadata.tags.join(", ")}`);
        console.log(`Singleton: ${metadata.singleton}`);
        console.log(`Poolable: ${metadata.poolable}`);

        console.log(`\n📊 Statistics:`);
        console.log(`Total Executions: ${stats.totalExecutions}`);
        console.log(`Active Instances: ${stats.activeInstances}`);
        console.log(`Total Instances: ${stats.totalInstances}`);
        console.log(`Errors: ${stats.errors}`);
        console.log(
          `Average Execution Time: ${Math.round(stats.averageExecutionTime)}ms`,
        );
        console.log(`Last Used: ${stats.lastUsed || "Never"}`);

        if (dependencies.length > 0) {
          console.log(`\n🔗 Dependencies: ${dependencies.join(", ")}`);
        }

        if (dependents.length > 0) {
          console.log(`\n👥 Dependents: ${dependents.join(", ")}`);
        }
      }
    } catch (error) {
      console.error("Error getting agent info:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle register command
   */
  async handleRegister(file, options) {
    try {
      const filePath = path.resolve(file);
      const AgentClass = require(filePath);

      const agentOptions = {
        name: options.name,
        category: options.category,
      };

      const agentName = this.registry.register(AgentClass, agentOptions);
      console.log(`✅ Agent '${agentName}' registered successfully`);
    } catch (error) {
      console.error("Error registering agent:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle unregister command
   */
  async handleUnregister(name) {
    try {
      const canRemove = this.registry.canRemove(name);
      if (!canRemove.canRemove) {
        console.error(`Cannot remove agent '${name}':`);
        if (canRemove.dependents.length > 0) {
          console.error(
            `- Has ${canRemove.dependents.length} dependents: ${canRemove.dependents.join(", ")}`,
          );
        }
        if (canRemove.hasActiveInstances) {
          console.error("- Has active instances");
        }
        process.exit(1);
      }

      this.registry.remove(name);
      console.log(`✅ Agent '${name}' removed successfully`);
    } catch (error) {
      console.error("Error removing agent:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle execute command
   */
  async handleExecute(name, options) {
    try {
      let inputs = {};

      if (options.input) {
        const inputData = await fs.readFile(options.input, "utf8");
        inputs = JSON.parse(inputData);
      }

      console.log(`🚀 Executing agent '${name}'...`);
      const startTime = Date.now();

      const result = await this.registry.execute(name, inputs);

      const duration = Date.now() - startTime;

      if (options.json) {
        const output = {
          success: result.success,
          result: result.result,
          duration,
        };
        console.log(JSON.stringify(output, null, 2));
      } else {
        console.log(`✅ Execution completed in ${duration}ms`);
        console.log("Result:", result.result);
      }

      if (options.output) {
        const outputData = JSON.stringify(result, null, 2);
        await fs.writeFile(options.output, outputData);
        console.log(`💾 Result saved to ${options.output}`);
      }
    } catch (error) {
      console.error("Error executing agent:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle batch command
   */
  async handleBatch(file, options) {
    try {
      const batchData = await fs.readFile(file, "utf8");
      const batchConfig = JSON.parse(batchData);

      console.log(
        `🚀 Executing batch with ${batchConfig.executions.length} operations...`,
      );

      const results = [];
      for (const execution of batchConfig.executions) {
        try {
          console.log(`  Executing ${execution.agent}...`);
          const result = await this.registry.execute(
            execution.agent,
            execution.inputs || {},
            execution.options || {},
          );
          results.push({
            agent: execution.agent,
            success: true,
            result: result.result,
            duration: result.duration,
          });
        } catch (error) {
          results.push({
            agent: execution.agent,
            success: false,
            error: error.message,
          });
        }
      }

      const successful = results.filter((r) => r.success).length;
      const failed = results.filter((r) => !r.success).length;

      if (options.json) {
        const output = {
          total: results.length,
          successful,
          failed,
          results,
        };
        console.log(JSON.stringify(output, null, 2));
      } else {
        console.log(`\n📊 Batch Results:`);
        console.log(`Total: ${results.length}`);
        console.log(`Successful: ${successful}`);
        console.log(`Failed: ${failed}`);

        results.forEach((result, index) => {
          const status = result.success ? "✅" : "❌";
          console.log(`${index + 1}. ${status} ${result.agent}`);
        });
      }

      if (options.output) {
        const outputData = JSON.stringify(results, null, 2);
        await fs.writeFile(options.output, outputData);
        console.log(`💾 Results saved to ${options.output}`);
      }
    } catch (error) {
      console.error("Error executing batch:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle health command
   */
  async handleHealth(options) {
    try {
      const health = await this.registry.healthCheck();

      if (options.json) {
        console.log(JSON.stringify(health, null, 2));
      } else {
        const status =
          health.overall === "healthy"
            ? "🟢"
            : health.overall === "degraded"
              ? "🟡"
              : "🔴";
        console.log(`${status} System Health: ${health.overall.toUpperCase()}`);

        Object.entries(health.agents).forEach(([name, agentHealth]) => {
          const agentStatus = agentHealth.status === "healthy" ? "🟢" : "🔴";
          console.log(`  ${agentStatus} ${name}: ${agentHealth.status}`);
        });
      }
    } catch (error) {
      console.error("Error checking health:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle metrics command
   */
  async handleMetrics(options) {
    try {
      let metrics;

      if (options.agent) {
        metrics = this.analytics.getUsageAnalytics(
          options.agent,
          options.timeRange,
        );
        if (!metrics) {
          console.error(`No metrics found for agent '${options.agent}'`);
          process.exit(1);
        }
      } else {
        metrics = this.analytics.getPerformanceAnalytics(options.timeRange);
      }

      if (options.json) {
        console.log(JSON.stringify(metrics, null, 2));
      } else {
        if (options.agent) {
          console.log(`📊 Metrics for Agent: ${options.agent}`);
          console.log(`Time Range: ${options.timeRange}`);
          console.log(`Data Points: ${metrics.dataPoints}`);
          console.log(`Average Executions: ${metrics.averageExecutions}`);
          console.log(`Peak Active Instances: ${metrics.peakActiveInstances}`);
          console.log(
            `Total Instances Created: ${metrics.totalInstancesCreated}`,
          );
          console.log(
            `Usage Trend: ${metrics.usageTrend.direction} (${metrics.usageTrend.percentage.toFixed(2)}%)`,
          );
        } else {
          console.log(`📊 System Performance Metrics`);
          console.log(`Time Range: ${options.timeRange}`);
          console.log(`Data Points: ${metrics.dataPoints}`);
          console.log(
            `Average Execution Time: ${Math.round(metrics.averageExecutionTime)}ms`,
          );
          console.log(`Total Executions: ${metrics.totalExecutions}`);
          console.log(`Error Rate: ${metrics.errorRate}`);
          console.log(
            `Agent Growth: ${metrics.agentGrowth.direction} (${metrics.agentGrowth.percentage.toFixed(2)}%)`,
          );
          console.log(
            `Instance Utilization: ${metrics.instanceUtilization.toFixed(2)}%`,
          );
        }
      }
    } catch (error) {
      console.error("Error getting metrics:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle analytics command
   */
  async handleAnalytics(options) {
    try {
      const analytics = {
        performance: this.analytics.getPerformanceAnalytics(options.timeRange),
        recommendations: this.analytics.generateRecommendations(),
      };

      if (options.json) {
        console.log(JSON.stringify(analytics, null, 2));
      } else {
        console.log(`📊 System Analytics (${options.timeRange})\n`);

        const perf = analytics.performance;
        if (perf) {
          console.log("Performance:");
          console.log(
            `  - Average Execution Time: ${Math.round(perf.averageExecutionTime)}ms`,
          );
          console.log(`  - Total Executions: ${perf.totalExecutions}`);
          console.log(`  - Error Rate: ${perf.errorRate}`);
          console.log(
            `  - Instance Utilization: ${perf.instanceUtilization.toFixed(2)}%`,
          );
        }

        if (analytics.recommendations.length > 0) {
          console.log("\n💡 Recommendations:");
          analytics.recommendations.forEach((rec, index) => {
            const priority =
              rec.priority === "high"
                ? "🔴"
                : rec.priority === "medium"
                  ? "🟡"
                  : "🟢";
            console.log(`  ${index + 1}. ${priority} ${rec.message}`);
          });
        } else {
          console.log("\n✅ No recommendations at this time");
        }
      }
    } catch (error) {
      console.error("Error getting analytics:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle test command
   */
  async handleTest(name, options) {
    try {
      const testCommand = options.watch ? "npm test -- --watch" : "npm test";
      console.log(`🧪 Running tests for agent '${name}'...`);

      // This would integrate with a test runner
      // For now, just show a placeholder
      console.log("Test execution not yet implemented");
      console.log(`Would run: ${testCommand} --grep "${name}"`);
    } catch (error) {
      console.error("Error running tests:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle validate command
   */
  async handleValidate(name) {
    try {
      const metadata = this.registry.getMetadata(name);
      if (!metadata) {
        console.error(`Agent '${name}' not found`);
        process.exit(1);
      }

      console.log(`🔍 Validating agent '${name}'...`);

      // Basic validation
      const issues = [];

      if (!metadata.name) issues.push("Missing name");
      if (!metadata.category) issues.push("Missing category");
      if (!metadata.capabilities || metadata.capabilities.length === 0) {
        issues.push("No capabilities defined");
      }

      // Check dependencies
      const dependencies = this.registry.getDependencies(name);
      for (const dep of dependencies) {
        if (!this.registry.agents.has(dep)) {
          issues.push(`Missing dependency: ${dep}`);
        }
      }

      if (issues.length === 0) {
        console.log("✅ Agent validation passed");
      } else {
        console.log("❌ Agent validation failed:");
        issues.forEach((issue) => console.log(`  - ${issue}`));
        process.exit(1);
      }
    } catch (error) {
      console.error("Error validating agent:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle export command
   */
  async handleExport(options) {
    try {
      const data = {
        timestamp: new Date(),
        agents: this.registry.listAgents(),
        stats: this.registry.getStats(),
        analytics: this.analytics.exportData("json"),
      };

      let output;
      if (options.format === "csv") {
        output = this.convertToCSV(data.agents);
      } else {
        output = JSON.stringify(data, null, 2);
      }

      if (options.output) {
        await fs.writeFile(options.output, output);
        console.log(`💾 Registry data exported to ${options.output}`);
      } else {
        console.log(output);
      }
    } catch (error) {
      console.error("Error exporting data:", error.message);
      process.exit(1);
    }
  }

  /**
   * Handle import command
   */
  async handleImport(file) {
    try {
      const data = await fs.readFile(file, "utf8");
      const importData = JSON.parse(data);

      console.log(`📥 Importing ${importData.agents?.length || 0} agents...`);

      // This would implement import logic
      console.log("Import functionality not yet implemented");
    } catch (error) {
      console.error("Error importing data:", error.message);
      process.exit(1);
    }
  }

  /**
   * Convert data to CSV
   */
  convertToCSV(agents) {
    const headers = [
      "name",
      "category",
      "description",
      "version",
      "capabilities",
      "tags",
      "executions",
      "errors",
    ];
    const rows = agents.map((agent) => [
      agent.name,
      agent.category,
      `"${agent.description}"`,
      agent.version,
      `"${agent.capabilities.join(", ")}"`,
      `"${agent.tags.join(", ")}"`,
      agent.stats.totalExecutions,
      agent.stats.errors,
    ]);

    return [headers, ...rows].map((row) => row.join(",")).join("\n");
  }

  /**
   * Run the CLI tool
   */
  async run(argv = process.argv) {
    try {
      await this.program.parseAsync(argv);
    } catch (error) {
      console.error("CLI Error:", error.message);
      process.exit(1);
    }
  }
}

// Usage example
async function runCliTool() {
  const cli = new AgentCliTool();
  await cli.run();
}

// Export for testing
module.exports = { AgentCliTool };

// Run CLI if called directly
if (require.main === module) {
  runCliTool();
}
```

## 🚀 DEPLOYMENT PATTERNS

### Pattern 3: Container Deployment

**File**: `deployment/docker/Dockerfile`

```dockerfile
# Multi-stage Docker build for agent system

# Stage 1: Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY agents/package*.json ./agents/

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build agents (if needed)
RUN npm run build

# Stage 2: Production stage
FROM node:18-alpine AS production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S agentuser -u 1001

WORKDIR /app

# Copy built application
COPY --from=builder --chown=agentuser:nodejs /app .

# Switch to non-root user
USER agentuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('./agents/integration/api-gateway').AgentApiGateway().healthCheck()"

# Expose port
EXPOSE 3000

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "agents/integration/api-gateway.js"]
```

**File**: `deployment/docker/docker-compose.yml`

```yaml
version: "3.8"

services:
  agent-registry:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - AGENT_PORT=3000
      - AGENT_METRICS_ENABLED=true
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres
    volumes:
      - ../../agents:/app/agents:ro
      - agent-data:/app/data
    networks:
      - agent-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - agent-network
    restart: unless-stopped
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=agent_registry
      - POSTGRES_USER=agent_user
      - POSTGRES_PASSWORD=agent_password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - agent-network
    restart: unless-stopped

  agent-monitor:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile.monitor
    environment:
      - AGENT_REGISTRY_URL=http://agent-registry:3000
      - MONITOR_INTERVAL=30000
    depends_on:
      - agent-registry
    networks:
      - agent-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - agent-registry
    networks:
      - agent-network
    restart: unless-stopped

volumes:
  agent-data:
  redis-data:
  postgres-data:

networks:
  agent-network:
    driver: bridge
```

### Pattern 4: Kubernetes Deployment

**File**: `deployment/k8s/agent-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-registry
  labels:
    app: agent-registry
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-registry
  template:
    metadata:
      labels:
        app: agent-registry
    spec:
      containers:
        - name: agent-registry
          image: agent-registry:latest
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: "production"
            - name: AGENT_PORT
              value: "3000"
            - name: REDIS_URL
              value: "redis://redis-service:6379"
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/v1/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
          volumeMounts:
            - name: agent-data
              mountPath: /app/data
      volumes:
        - name: agent-data
          persistentVolumeClaim:
            claimName: agent-data-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: agent-registry-service
spec:
  selector:
    app: agent-registry
  ports:
    - port: 3000
      targetPort: 3000
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-registry-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: agents.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: agent-registry-service
                port:
                  number: 3000

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: agent-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
data:
  config.json: |
    {
      "enableMetrics": true,
      "maxConcurrency": 10,
      "rateLimit": {
        "windowMs": 60000,
        "maxRequests": 1000
      }
    }

---
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
type: Opaque
data:
  # Base64 encoded secrets
  database-password: <base64-encoded-password>
  api-key: <base64-encoded-api-key>
```

### Pattern 5: CI/CD Pipeline

**File**: `deployment/ci-cd/github-actions.yml`

```yaml
name: Agent System CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run linting
        run: npm run lint

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration

      - name: Generate test coverage
        run: npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: agent-registry
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add deployment commands here

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production environment"
          # Add deployment commands here
```

## 📊 MONITORING & OBSERVABILITY

### Pattern 6: Monitoring Dashboard

**File**: `monitoring/dashboard/grafana-dashboard.json`

```json
{
  "dashboard": {
    "title": "Agent System Monitoring",
    "tags": ["agents", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "title": "System Health",
        "type": "stat",
        "targets": [
          {
            "expr": "agent_health_status",
            "legendFormat": "{{status}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {
                "options": {
                  "healthy": {
                    "text": "Healthy",
                    "color": "green"
                  },
                  "degraded": {
                    "text": "Degraded",
                    "color": "yellow"
                  },
                  "unhealthy": {
                    "text": "Unhealthy",
                    "color": "red"
                  }
                },
                "type": "value"
              }
            ]
          }
        }
      },
      {
        "title": "Agent Execution Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(agent_executions_total[5m])",
            "legendFormat": "Executions per second"
          }
        ]
      },
      {
        "title": "Agent Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(agent_errors_total[5m]) / rate(agent_executions_total[5m]) * 100",
            "legendFormat": "Error rate (%)"
          }
        ]
      },
      {
        "title": "Agent Execution Duration",
        "type": "heatmap",
        "targets": [
          {
            "expr": "agent_execution_duration_seconds",
            "legendFormat": "{{agent}}"
          }
        ]
      },
      {
        "title": "Active Agent Instances",
        "type": "barchart",
        "targets": [
          {
            "expr": "agent_instances_active",
            "legendFormat": "{{agent}}"
          }
        ]
      },
      {
        "title": "Agent Resource Usage",
        "type": "table",
        "targets": [
          {
            "expr": "agent_memory_usage_bytes",
            "legendFormat": "Memory - {{agent}}"
          },
          {
            "expr": "agent_cpu_usage_percent",
            "legendFormat": "CPU - {{agent}}"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## 📋 SUMMARY

### Integration & Deployment Patterns Summary

| Pattern                  | Purpose                          | Key Features                              | Use Case                   |
| ------------------------ | -------------------------------- | ----------------------------------------- | -------------------------- |
| **API Gateway**          | HTTP interface for agents        | REST endpoints, rate limiting, monitoring | Web service integration    |
| **CLI Tool**             | Command-line agent management    | Registry ops, execution, monitoring       | Development and operations |
| **Container Deployment** | Docker containerization          | Multi-stage builds, orchestration         | Cloud deployment           |
| **Kubernetes**           | Container orchestration          | Auto-scaling, health checks, persistence  | Production deployment      |
| **CI/CD Pipeline**       | Automated testing and deployment | Multi-stage pipeline, security scanning   | DevOps automation          |
| **Monitoring Dashboard** | System observability             | Metrics visualization, alerting           | System monitoring          |

### Best Practices

✅ **API First**: Design APIs before implementations for better integration  
✅ **Containerization**: Use containers for consistent deployment across environments  
✅ **Infrastructure as Code**: Define infrastructure in code for reproducibility  
✅ **Observability**: Comprehensive monitoring, logging, and alerting  
✅ **Security**: Implement authentication, authorization, and secure communications  
✅ **Scalability**: Design for horizontal scaling and load balancing  
✅ **Disaster Recovery**: Implement backup, failover, and recovery procedures  
✅ **Documentation**: Keep deployment and operations documentation current

### Deployment Checklist

- [ ] Environment configuration (dev/staging/prod)
- [ ] Secret management (API keys, database credentials)
- [ ] Network security (firewalls, VPCs, security groups)
- [ ] Monitoring and alerting setup
- [ ] Backup and recovery procedures
- [ ] Performance benchmarking
- [ ] Security scanning and compliance checks
- [ ] Rollback procedures
- [ ] Documentation updates

This comprehensive integration and deployment framework provides everything needed to deploy agent systems to production with proper monitoring, security, and scalability.</content>
<parameter name="filePath">c:\wamp64\www\birdc_erp\skills\custom-sub-agents\references\08-integration-deployment.md
