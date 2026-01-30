# 🏗️ Parent & Sub-Agent Architecture

## 🎯 PARENT/SUB-AGENT CONDUCTOR PATTERN

**Purpose**: Orchestrate complex workflows using parent agents that coordinate specialized sub-agents.

### Pattern 1: Conductor Agent Base Class

**File**: `agents/conductor/base.js`

```javascript
/**
 * Conductor Agent Base Class
 *
 * Base class for agents that orchestrate multiple sub-agents.
 * Provides common functionality for execution control, error handling,
 * and result aggregation.
 */

class ConductorAgent {
  constructor(config = {}) {
    this.config = {
      maxConcurrency: 5,
      timeout: 300000, // 5 minutes
      continueOnError: false,
      enableLogging: true,
      enableMetrics: true,
      ...config,
    };

    this.subAgents = new Map();
    this.executionHistory = [];
    this.metrics = {
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      averageExecutionTime: 0,
    };
  }

  // Abstract method - must be implemented by subclasses
  async defineWorkflow(input, context) {
    throw new Error("defineWorkflow() must be implemented by subclass");
  }

  // Abstract method - must be implemented by subclasses
  async processResults(results, context) {
    throw new Error("processResults() must be implemented by subclass");
  }

  async execute(input, context = {}) {
    const executionId = this.generateExecutionId();
    const startTime = Date.now();

    this.log("info", `🚀 Starting conductor execution ${executionId}`);

    try {
      // Define the workflow
      const workflow = await this.defineWorkflow(input, context);

      // Execute the workflow
      const results = await this.executeWorkflow(workflow, context);

      // Process results
      const finalResult = await this.processResults(results, context);

      // Record successful execution
      const duration = Date.now() - startTime;
      this.recordExecution(true, duration);

      this.log(
        "info",
        `✅ Conductor execution ${executionId} completed in ${duration}ms`,
      );

      return {
        success: true,
        executionId,
        result: finalResult,
        duration,
        workflow: workflow.name,
        subAgentResults: results,
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      this.recordExecution(false, duration);

      this.log(
        "error",
        `💥 Conductor execution ${executionId} failed: ${error.message}`,
      );

      return {
        success: false,
        executionId,
        error: error.message,
        duration,
        workflow: null,
      };
    }
  }

  async executeWorkflow(workflow, context) {
    const results = new Map();

    switch (workflow.executionMode) {
      case "sequential":
        return await this.executeSequential(workflow, context);

      case "parallel":
        return await this.executeParallel(workflow, context);

      case "conditional":
        return await this.executeConditional(workflow, context);

      case "pipeline":
        return await this.executePipeline(workflow, context);

      default:
        throw new Error(`Unknown execution mode: ${workflow.executionMode}`);
    }
  }

  async executeSequential(workflow, context) {
    const results = new Map();
    let currentData = { ...context };

    for (const step of workflow.steps) {
      const stepResult = await this.executeStep(step, currentData, context);
      results.set(step.name, stepResult);

      if (stepResult.success) {
        // Pass successful results to next step
        currentData = { ...currentData, [step.name]: stepResult.data };
      } else if (!this.config.continueOnError) {
        throw new Error(`Step ${step.name} failed: ${stepResult.error}`);
      }
    }

    return results;
  }

  async executeParallel(workflow, context) {
    const promises = workflow.steps.map((step) =>
      this.executeStep(step, context, context),
    );

    const settledResults = await Promise.allSettled(promises);

    const results = new Map();
    settledResults.forEach((settled, index) => {
      const step = workflow.steps[index];
      if (settled.status === "fulfilled") {
        results.set(step.name, settled.value);
      } else {
        results.set(step.name, {
          success: false,
          error: settled.reason.message,
          duration: 0,
        });
      }
    });

    return results;
  }

  async executeConditional(workflow, context) {
    const results = new Map();

    for (const branch of workflow.branches) {
      const conditionMet = await this.evaluateCondition(
        branch.condition,
        context,
      );

      if (conditionMet) {
        this.log("info", `Branch condition met: ${branch.name}`);
        const branchResults = await this.executeWorkflow(
          branch.workflow,
          context,
        );

        // Merge branch results
        for (const [stepName, result] of branchResults) {
          results.set(`${branch.name}.${stepName}`, result);
        }

        // Stop at first matching branch unless specified otherwise
        if (!workflow.continueAfterMatch) {
          break;
        }
      }
    }

    return results;
  }

  async executePipeline(workflow, context) {
    let pipelineData = { ...context };

    for (const stage of workflow.pipeline) {
      // Execute all steps in this stage in parallel
      const stagePromises = stage.steps.map((step) =>
        this.executeStepWithData(step, pipelineData, context),
      );

      const stageResults = await Promise.all(stagePromises);

      // Aggregate stage results into pipeline data
      pipelineData = stageResults.reduce(
        (acc, result, index) => {
          if (result.success) {
            acc[stage.steps[index].name] = result.data;
            acc = { ...acc, ...result.data }; // Allow agents to add to global context
          }
          return acc;
        },
        { ...pipelineData },
      );

      // Check if pipeline should continue
      const allSuccessful = stageResults.every((r) => r.success);
      if (!allSuccessful && !stage.continueOnError) {
        throw new Error(`Pipeline stage failed: ${stage.name}`);
      }
    }

    return new Map([
      ["pipeline_result", { success: true, data: pipelineData }],
    ]);
  }

  async executeStep(step, inputData, context) {
    const startTime = Date.now();

    try {
      const agent = this.getSubAgent(step.agent);
      const inputs = this.prepareInputs(step.inputs, inputData, context);

      this.log(
        "debug",
        `Executing step: ${step.name} with agent: ${step.agent}`,
      );

      const result = await agent.execute(inputs, step.options || {});

      const duration = Date.now() - startTime;

      return {
        success: true,
        data: result,
        duration,
        agent: step.agent,
        inputs,
      };
    } catch (error) {
      const duration = Date.now() - startTime;

      this.log("error", `Step ${step.name} failed: ${error.message}`);

      return {
        success: false,
        error: error.message,
        duration,
        agent: step.agent,
      };
    }
  }

  async executeStepWithData(step, pipelineData, context) {
    // Similar to executeStep but designed for pipeline data flow
    return await this.executeStep(step, pipelineData, context);
  }

  prepareInputs(inputTemplate, data, context) {
    const inputs = {};

    Object.entries(inputTemplate).forEach(([key, value]) => {
      if (typeof value === "string" && value.startsWith("$")) {
        // Reference to data or context
        const path = value.substring(1);
        inputs[key] = this.getNestedValue({ data, context }, path);
      } else if (typeof value === "function") {
        // Dynamic value
        inputs[key] = value(data, context);
      } else {
        // Static value
        inputs[key] = value;
      }
    });

    return inputs;
  }

  getNestedValue(obj, path) {
    return path.split(".").reduce((current, key) => current?.[key], obj);
  }

  async evaluateCondition(condition, context) {
    if (typeof condition === "function") {
      return await condition(context);
    } else if (typeof condition === "string") {
      return this.evaluateStringCondition(condition, context);
    }
    return false;
  }

  evaluateStringCondition(condition, context) {
    // Simple condition evaluator
    const conditions = {
      "context.user.isAdmin": () => context.user?.isAdmin === true,
      "context.data.length > 0": () => context.data?.length > 0,
      "context.hasErrors": () => context.errors?.length > 0,
      "context.isLargeDataset": () =>
        Array.isArray(context.data) && context.data.length > 10000,
    };

    return conditions[condition]?.() || false;
  }

  registerSubAgent(name, agent) {
    this.subAgents.set(name, agent);
    this.log("info", `Registered sub-agent: ${name}`);
  }

  getSubAgent(name) {
    const agent = this.subAgents.get(name);
    if (!agent) {
      throw new Error(`Sub-agent not found: ${name}`);
    }
    return agent;
  }

  generateExecutionId() {
    return `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  recordExecution(success, duration) {
    this.metrics.totalExecutions++;
    if (success) {
      this.metrics.successfulExecutions++;
    } else {
      this.metrics.failedExecutions++;
    }

    // Update rolling average
    const totalTime =
      this.metrics.averageExecutionTime * (this.metrics.totalExecutions - 1);
    this.metrics.averageExecutionTime =
      (totalTime + duration) / this.metrics.totalExecutions;
  }

  log(level, message) {
    if (!this.config.enableLogging) return;

    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${level.toUpperCase()}: ${message}`;

    console.log(logEntry);

    // Store in execution history
    this.executionHistory.push({
      timestamp,
      level,
      message,
    });
  }

  getMetrics() {
    return { ...this.metrics };
  }

  getExecutionHistory() {
    return [...this.executionHistory];
  }

  clearExecutionHistory() {
    this.executionHistory = [];
  }
}

module.exports = { ConductorAgent };
```

### Pattern 2: Data Processing Conductor

**File**: `agents/data-processing-conductor/agent.js`

```javascript
/**
 * Data Processing Conductor
 *
 * Orchestrates a complete data processing pipeline using specialized sub-agents.
 * Handles data extraction, validation, transformation, enrichment, and storage.
 */

const { ConductorAgent } = require("../conductor/base");

class DataProcessingConductor extends ConductorAgent {
  constructor(config = {}) {
    super({
      maxConcurrency: 3,
      timeout: 600000, // 10 minutes
      continueOnError: false,
      ...config,
    });

    // Register sub-agents
    this.registerSubAgents();
  }

  registerSubAgents() {
    // Import and register sub-agents
    const { DataExtractorAgent } = require("../data-extractor/agent");
    const { DataValidatorAgent } = require("../data-validator/agent");
    const { DataTransformerAgent } = require("../data-transformer/agent");
    const { DataEnricherAgent } = require("../data-enricher/agent");
    const { DataStorageAgent } = require("../data-storage/agent");
    const { QualityReporterAgent } = require("../quality-reporter/agent");

    this.registerSubAgent("extractor", new DataExtractorAgent());
    this.registerSubAgent("validator", new DataValidatorAgent());
    this.registerSubAgent("transformer", new DataTransformerAgent());
    this.registerSubAgent("enricher", new DataEnricherAgent());
    this.registerSubAgent("storage", new DataStorageAgent());
    this.registerSubAgent("reporter", new QualityReporterAgent());
  }

  async defineWorkflow(input, context) {
    const {
      source,
      destination,
      transformations = [],
      enrichments = [],
    } = input;

    return {
      name: "Data Processing Pipeline",
      executionMode: "pipeline",
      pipeline: [
        {
          name: "extraction",
          continueOnError: false,
          steps: [
            {
              name: "extract",
              agent: "extractor",
              inputs: {
                source: "$data.source",
                filters: "$data.filters",
                limit: "$data.limit",
              },
            },
          ],
        },
        {
          name: "validation",
          continueOnError: false,
          steps: [
            {
              name: "validate",
              agent: "validator",
              inputs: {
                data: "$extraction.extract",
                rules: "$data.validationRules",
              },
            },
          ],
        },
        {
          name: "processing",
          continueOnError: true, // Continue even if some transformations fail
          steps: [
            {
              name: "transform",
              agent: "transformer",
              inputs: {
                data: "$validation.validate.validRecords",
                transformations: "$data.transformations",
              },
            },
            {
              name: "enrich",
              agent: "enricher",
              inputs: {
                data: "$processing.transform",
                enrichments: "$data.enrichments",
              },
            },
          ],
        },
        {
          name: "storage",
          continueOnError: false,
          steps: [
            {
              name: "store",
              agent: "storage",
              inputs: {
                data: "$processing.enrich",
                destination: "$data.destination",
                options: "$data.storageOptions",
              },
            },
          ],
        },
        {
          name: "reporting",
          continueOnError: true, // Don't fail the whole pipeline for reporting issues
          steps: [
            {
              name: "report",
              agent: "reporter",
              inputs: {
                results: "$pipeline_result",
                metrics: {
                  extraction: "$extraction.extract",
                  validation: "$validation.validate",
                  processing: "$processing",
                  storage: "$storage.store",
                },
              },
            },
          ],
        },
      ],
    };
  }

  async processResults(results, context) {
    // Extract key results from the pipeline
    const pipelineResult = results.get("pipeline_result");

    if (!pipelineResult?.success) {
      throw new Error("Pipeline execution failed");
    }

    const finalData = pipelineResult.data;

    // Compile comprehensive result
    return {
      success: true,
      processedRecords: finalData.processing?.enrich?.length || 0,
      storedRecords: finalData.storage?.store?.recordsStored || 0,
      qualityMetrics: finalData.reporting?.report?.qualityMetrics || {},
      executionDetails: {
        extraction: this.summarizeStep(finalData.extraction?.extract),
        validation: this.summarizeStep(finalData.validation?.validate),
        transformation: this.summarizeStep(finalData.processing?.transform),
        enrichment: this.summarizeStep(finalData.processing?.enrich),
        storage: this.summarizeStep(finalData.storage?.store),
        reporting: this.summarizeStep(finalData.reporting?.report),
      },
      data: finalData,
    };
  }

  summarizeStep(stepResult) {
    if (!stepResult) return null;

    return {
      success: stepResult.success !== false,
      duration: stepResult.duration || 0,
      recordsProcessed: stepResult.recordsProcessed || 0,
      error: stepResult.error || null,
    };
  }
}

// Usage example
async function processCustomerData() {
  const conductor = new DataProcessingConductor();

  const input = {
    source: {
      type: "database",
      table: "raw_customers",
      connection: "staging_db",
    },
    destination: {
      type: "database",
      table: "processed_customers",
      connection: "production_db",
    },
    filters: {
      created_after: "2024-01-01",
      status: "active",
    },
    limit: 10000,
    validationRules: [
      { field: "email", type: "email", required: true },
      { field: "phone", type: "phone", required: false },
      { field: "age", type: "number", min: 18, max: 120 },
    ],
    transformations: [
      { type: "normalize", fields: ["name", "address"] },
      { type: "format", field: "phone", format: "international" },
      { type: "calculate", field: "age_group", expression: "FLOOR(age/10)*10" },
    ],
    enrichments: [
      { type: "geocode", field: "address", output: "coordinates" },
      {
        type: "lookup",
        field: "company_id",
        source: "companies",
        output: "company_info",
      },
    ],
    storageOptions: {
      createTable: true,
      indexes: ["email", "company_id"],
      partitions: { type: "monthly", field: "created_at" },
    },
  };

  const context = {
    user: { id: 123, name: "Data Engineer" },
    requestId: "req_456",
    environment: "production",
  };

  try {
    const result = await conductor.execute(input, context);

    console.log("Data processing completed:");
    console.log(`- Processed: ${result.result.processedRecords} records`);
    console.log(`- Stored: ${result.result.storedRecords} records`);
    console.log(
      `- Quality Score: ${result.result.qualityMetrics.overallScore}%`,
    );

    return result;
  } catch (error) {
    console.error("Data processing failed:", error);
    throw error;
  }
}

module.exports = { DataProcessingConductor };
```

### Pattern 3: Business Intelligence Conductor

**File**: `agents/bi-conductor/agent.js`

```javascript
/**
 * Business Intelligence Conductor
 *
 * Orchestrates complex BI workflows including data analysis, reporting,
 * alerting, and automated insights generation.
 */

const { ConductorAgent } = require("../conductor/base");

class BIConductor extends ConductorAgent {
  constructor(config = {}) {
    super({
      maxConcurrency: 4,
      timeout: 900000, // 15 minutes
      continueOnError: true, // BI can be partially successful
      ...config,
    });

    this.registerSubAgents();
  }

  registerSubAgents() {
    const { DataAnalyzerAgent } = require("../data-analyzer/agent");
    const { TrendAnalyzerAgent } = require("../trend-analyzer/agent");
    const { AnomalyDetectorAgent } = require("../anomaly-detector/agent");
    const { ReportGeneratorAgent } = require("../report-generator/agent");
    const { AlertManagerAgent } = require("../alert-manager/agent");
    const { InsightGeneratorAgent } = require("../insight-generator/agent");
    const { DashboardUpdaterAgent } = require("../dashboard-updater/agent");

    this.registerSubAgent("analyzer", new DataAnalyzerAgent());
    this.registerSubAgent("trend_analyzer", new TrendAnalyzerAgent());
    this.registerSubAgent("anomaly_detector", new AnomalyDetectorAgent());
    this.registerSubAgent("report_generator", new ReportGeneratorAgent());
    this.registerSubAgent("alert_manager", new AlertManagerAgent());
    this.registerSubAgent("insight_generator", new InsightGeneratorAgent());
    this.registerSubAgent("dashboard_updater", new DashboardUpdaterAgent());
  }

  async defineWorkflow(input, context) {
    const { analysisType, timeRange, dimensions, metrics, alerts = [] } = input;

    // Define workflow based on analysis type
    switch (analysisType) {
      case "comprehensive":
        return this.createComprehensiveWorkflow(input, context);
      case "real_time":
        return this.createRealtimeWorkflow(input, context);
      case "predictive":
        return this.createPredictiveWorkflow(input, context);
      default:
        return this.createBasicWorkflow(input, context);
    }
  }

  createComprehensiveWorkflow(input, context) {
    return {
      name: "Comprehensive BI Analysis",
      executionMode: "conditional",
      branches: [
        {
          name: "large_dataset",
          condition: (ctx) => ctx.data?.length > 50000,
          workflow: {
            name: "Large Dataset Analysis",
            executionMode: "parallel",
            steps: [
              {
                name: "parallel_analysis",
                agent: "analyzer",
                inputs: { data: "$data", type: "parallel", chunks: 10 },
              },
              {
                name: "trend_analysis",
                agent: "trend_analyzer",
                inputs: { data: "$data", timeField: "timestamp" },
              },
            ],
          },
        },
        {
          name: "standard_dataset",
          condition: (ctx) => ctx.data?.length <= 50000,
          workflow: {
            name: "Standard Analysis",
            executionMode: "sequential",
            steps: [
              {
                name: "data_analysis",
                agent: "analyzer",
                inputs: {
                  data: "$data",
                  dimensions: "$dimensions",
                  metrics: "$metrics",
                },
              },
              {
                name: "trend_analysis",
                agent: "trend_analyzer",
                inputs: { data: "$data", timeRange: "$timeRange" },
              },
              {
                name: "anomaly_detection",
                agent: "anomaly_detector",
                inputs: { data: "$data", sensitivity: "medium" },
              },
            ],
          },
        },
      ],
      continueAfterMatch: false,
    };
  }

  createRealtimeWorkflow(input, context) {
    return {
      name: "Real-time BI Analysis",
      executionMode: "parallel",
      steps: [
        {
          name: "quick_analysis",
          agent: "analyzer",
          inputs: { data: "$data", type: "quick" },
        },
        {
          name: "anomaly_check",
          agent: "anomaly_detector",
          inputs: { data: "$data", sensitivity: "high" },
        },
        {
          name: "alert_check",
          agent: "alert_manager",
          inputs: { data: "$data", rules: "$alerts" },
        },
      ],
    };
  }

  createPredictiveWorkflow(input, context) {
    return {
      name: "Predictive BI Analysis",
      executionMode: "sequential",
      steps: [
        {
          name: "historical_analysis",
          agent: "analyzer",
          inputs: { data: "$data", type: "historical" },
        },
        {
          name: "trend_forecasting",
          agent: "trend_analyzer",
          inputs: { data: "$data", forecast: true, periods: 12 },
        },
        {
          name: "insight_generation",
          agent: "insight_generator",
          inputs: {
            analysis: "$historical_analysis",
            trends: "$trend_forecasting",
            type: "predictive",
          },
        },
      ],
    };
  }

  createBasicWorkflow(input, context) {
    return {
      name: "Basic BI Analysis",
      executionMode: "sequential",
      steps: [
        {
          name: "analysis",
          agent: "analyzer",
          inputs: {
            data: "$data",
            dimensions: "$dimensions",
            metrics: "$metrics",
          },
        },
        {
          name: "reporting",
          agent: "report_generator",
          inputs: {
            analysis: "$analysis",
            format: "dashboard",
            title: "BI Analysis Report",
          },
        },
      ],
    };
  }

  async processResults(results, context) {
    // Aggregate results from different analysis paths
    const aggregatedResults = {
      analysis: null,
      trends: null,
      anomalies: [],
      alerts: [],
      insights: [],
      reports: [],
      dashboards: [],
    };

    // Extract results from different execution paths
    for (const [stepName, result] of results) {
      if (result.success && result.data) {
        if (stepName.includes("analysis") || stepName.includes("analyzer")) {
          aggregatedResults.analysis = result.data;
        } else if (stepName.includes("trend")) {
          aggregatedResults.trends = result.data;
        } else if (stepName.includes("anomaly")) {
          aggregatedResults.anomalies.push(...(result.data.anomalies || []));
        } else if (stepName.includes("alert")) {
          aggregatedResults.alerts.push(...(result.data.alerts || []));
        } else if (stepName.includes("insight")) {
          aggregatedResults.insights.push(...(result.data.insights || []));
        } else if (stepName.includes("report")) {
          aggregatedResults.reports.push(result.data);
        } else if (stepName.includes("dashboard")) {
          aggregatedResults.dashboards.push(result.data);
        }
      }
    }

    // Generate summary
    const summary = {
      totalMetrics: aggregatedResults.analysis?.metrics?.length || 0,
      trendsIdentified: aggregatedResults.trends?.trends?.length || 0,
      anomaliesDetected: aggregatedResults.anomalies.length,
      alertsTriggered: aggregatedResults.alerts.length,
      insightsGenerated: aggregatedResults.insights.length,
      reportsCreated: aggregatedResults.reports.length,
      dashboardsUpdated: aggregatedResults.dashboards.length,
    };

    return {
      success: true,
      summary,
      results: aggregatedResults,
      executionTime: Date.now() - context.startTime,
      recommendations: this.generateRecommendations(aggregatedResults),
    };
  }

  generateRecommendations(results) {
    const recommendations = [];

    if (results.anomalies.length > 0) {
      recommendations.push({
        type: "alert",
        priority: "high",
        message: `${results.anomalies.length} anomalies detected requiring attention`,
      });
    }

    if (results.alerts.length > 0) {
      recommendations.push({
        type: "action",
        priority: "high",
        message: `${results.alerts.length} business alerts triggered`,
      });
    }

    if (results.insights.length > 5) {
      recommendations.push({
        type: "review",
        priority: "medium",
        message: "Multiple insights generated - review for strategic decisions",
      });
    }

    if (results.trends && results.trends.growth > 20) {
      recommendations.push({
        type: "opportunity",
        priority: "medium",
        message: "Strong growth trend detected - consider expansion strategies",
      });
    }

    return recommendations;
  }
}

// Specialized BI conductors for different domains
class SalesBIConductor extends BIConductor {
  async defineWorkflow(input, context) {
    // Sales-specific workflow
    return {
      name: "Sales BI Analysis",
      executionMode: "sequential",
      steps: [
        {
          name: "sales_analysis",
          agent: "analyzer",
          inputs: {
            data: "$data",
            dimensions: ["region", "product", "salesperson"],
            metrics: ["revenue", "units", "conversion_rate"],
          },
        },
        {
          name: "sales_trends",
          agent: "trend_analyzer",
          inputs: { data: "$data", timeField: "sale_date" },
        },
        {
          name: "sales_forecasting",
          agent: "trend_analyzer",
          inputs: { data: "$data", forecast: true, periods: 6 },
        },
        {
          name: "sales_insights",
          agent: "insight_generator",
          inputs: {
            analysis: "$sales_analysis",
            trends: "$sales_trends",
            forecasts: "$sales_forecasting",
            domain: "sales",
          },
        },
        {
          name: "sales_report",
          agent: "report_generator",
          inputs: {
            analysis: "$sales_analysis",
            insights: "$sales_insights",
            format: "executive_summary",
          },
        },
      ],
    };
  }
}

class MarketingBIConductor extends BIConductor {
  async defineWorkflow(input, context) {
    return {
      name: "Marketing BI Analysis",
      executionMode: "parallel",
      steps: [
        {
          name: "campaign_analysis",
          agent: "analyzer",
          inputs: {
            data: "$data",
            dimensions: ["campaign", "channel", "audience"],
            metrics: ["impressions", "clicks", "conversions", "roi"],
          },
        },
        {
          name: "customer_segmentation",
          agent: "analyzer",
          inputs: {
            data: "$data",
            type: "clustering",
            features: ["engagement", "spending", "demographics"],
          },
        },
        {
          name: "attribution_modeling",
          agent: "analyzer",
          inputs: {
            data: "$data",
            type: "attribution",
            model: "multi_touch",
          },
        },
      ],
    };
  }
}

// Usage examples
async function runSalesBIAnalysis() {
  const conductor = new SalesBIConductor();

  const input = {
    analysisType: "comprehensive",
    timeRange: { start: "2024-01-01", end: "2024-12-31" },
    dimensions: ["region", "product_category"],
    metrics: ["revenue", "profit_margin", "customer_acquisition_cost"],
    alerts: [
      {
        metric: "revenue",
        condition: "decrease",
        threshold: 10,
        period: "month",
      },
      { metric: "profit_margin", condition: "below", threshold: 15 },
    ],
  };

  const salesData = [
    // Large dataset of sales transactions
  ];

  const context = {
    user: { id: 123, role: "sales_manager" },
    data: salesData,
    startTime: Date.now(),
  };

  const result = await conductor.execute(input, context);
  return result;
}

module.exports = {
  BIConductor,
  SalesBIConductor,
  MarketingBIConductor,
};
```

## 🏗️ ADVANCED CONDUCTOR PATTERNS

### Pattern 4: Self-Healing Conductor

**File**: `agents/self-healing-conductor/agent.js`

```javascript
/**
 * Self-Healing Conductor
 *
 * Automatically handles failures and retries operations with
 * fallback strategies and recovery mechanisms.
 */

const { ConductorAgent } = require("../conductor/base");

class SelfHealingConductor extends ConductorAgent {
  constructor(config = {}) {
    super({
      maxRetries: 3,
      retryDelay: 1000,
      enableFallbacks: true,
      healingStrategies: ["retry", "alternative_agent", "simplified_mode"],
      ...config,
    });

    this.failurePatterns = new Map();
    this.healingHistory = [];
  }

  async executeStep(step, inputData, context) {
    let lastError = null;
    let attempt = 0;

    while (attempt <= this.config.maxRetries) {
      try {
        const result = await this.attemptStepExecution(
          step,
          inputData,
          context,
          attempt,
        );
        return result;
      } catch (error) {
        lastError = error;
        attempt++;

        this.log(
          "warn",
          `Step ${step.name} failed (attempt ${attempt}): ${error.message}`,
        );

        // Record failure pattern
        this.recordFailure(step.agent, error);

        if (attempt <= this.config.maxRetries) {
          await this.attemptHealing(step, error, attempt);
          await this.delay(this.config.retryDelay * attempt); // Exponential backoff
        }
      }
    }

    // All retries exhausted
    throw new Error(
      `Step ${step.name} failed after ${this.config.maxRetries + 1} attempts: ${lastError.message}`,
    );
  }

  async attemptStepExecution(step, inputData, context, attempt) {
    const startTime = Date.now();

    try {
      const agent = this.getSubAgent(step.agent);
      const inputs = this.prepareInputs(step.inputs, inputData, context);

      // Modify inputs based on attempt (e.g., reduce complexity on retries)
      const modifiedInputs = this.modifyInputsForRetry(inputs, attempt);

      this.log(
        "debug",
        `Executing step: ${step.name} (attempt ${attempt + 1})`,
      );

      const result = await agent.execute(modifiedInputs, step.options || {});

      const duration = Date.now() - startTime;

      return {
        success: true,
        data: result,
        duration,
        agent: step.agent,
        inputs: modifiedInputs,
        attempts: attempt + 1,
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      throw new Error(`${error.message} (duration: ${duration}ms)`);
    }
  }

  modifyInputsForRetry(inputs, attempt) {
    if (attempt === 0) return inputs;

    const modified = { ...inputs };

    // Progressive degradation strategies
    switch (attempt) {
      case 1:
        // First retry: Reduce data size
        if (modified.limit) {
          modified.limit = Math.floor(modified.limit * 0.5);
        }
        break;

      case 2:
        // Second retry: Simplify processing
        modified.simplified = true;
        if (modified.options) {
          modified.options.simplified = true;
        }
        break;

      case 3:
        // Third retry: Minimal processing
        modified.minimal = true;
        modified.skipValidation = true;
        break;
    }

    return modified;
  }

  async attemptHealing(step, error, attempt) {
    const healingStrategy = this.selectHealingStrategy(step, error, attempt);

    this.healingHistory.push({
      step: step.name,
      agent: step.agent,
      error: error.message,
      attempt,
      strategy: healingStrategy,
      timestamp: new Date(),
    });

    switch (healingStrategy) {
      case "retry":
        this.log("info", `Healing strategy: retry for ${step.name}`);
        break;

      case "alternative_agent":
        await this.tryAlternativeAgent(step, error);
        break;

      case "simplified_mode":
        this.log("info", `Healing strategy: simplified mode for ${step.name}`);
        break;

      case "skip_step":
        this.log("warn", `Healing strategy: skipping step ${step.name}`);
        // Return a default result to continue workflow
        return {
          success: true,
          data: { skipped: true, reason: "healing_strategy_skip" },
          duration: 0,
          agent: step.agent,
          healed: true,
        };

      default:
        this.log("warn", `No healing strategy available for ${step.name}`);
    }
  }

  selectHealingStrategy(step, error, attempt) {
    // Analyze error type
    const errorType = this.categorizeError(error);

    // Check failure patterns
    const agentFailures = this.failurePatterns.get(step.agent) || [];
    const recentFailures = agentFailures.filter(
      (f) => Date.now() - f.timestamp < 300000, // Last 5 minutes
    );

    // Strategy selection logic
    if (errorType === "timeout" && attempt < 2) {
      return "retry";
    }

    if (errorType === "resource_exhausted" && recentFailures.length > 2) {
      return "simplified_mode";
    }

    if (
      errorType === "dependency_unavailable" &&
      this.hasAlternativeAgent(step.agent)
    ) {
      return "alternative_agent";
    }

    if (attempt >= 2 && errorType === "validation_error") {
      return "skip_step";
    }

    return "retry";
  }

  categorizeError(error) {
    const message = error.message.toLowerCase();

    if (message.includes("timeout") || message.includes("timed out")) {
      return "timeout";
    }

    if (message.includes("memory") || message.includes("out of memory")) {
      return "resource_exhausted";
    }

    if (message.includes("connection") || message.includes("network")) {
      return "dependency_unavailable";
    }

    if (message.includes("validation") || message.includes("invalid")) {
      return "validation_error";
    }

    return "unknown";
  }

  hasAlternativeAgent(agentName) {
    const alternatives = {
      primary_database: ["backup_database", "cache_database"],
      external_api: ["cached_api", "mock_api"],
      complex_analyzer: ["simple_analyzer"],
    };

    return alternatives[agentName]?.length > 0;
  }

  async tryAlternativeAgent(step, error) {
    const alternatives = {
      primary_database: "backup_database",
      external_api: "cached_api",
      complex_analyzer: "simple_analyzer",
    };

    const alternative = alternatives[step.agent];
    if (alternative && this.subAgents.has(alternative)) {
      this.log(
        "info",
        `Switching ${step.agent} to alternative: ${alternative}`,
      );
      step.agent = alternative;
      return true;
    }

    return false;
  }

  recordFailure(agentName, error) {
    if (!this.failurePatterns.has(agentName)) {
      this.failurePatterns.set(agentName, []);
    }

    this.failurePatterns.get(agentName).push({
      error: error.message,
      timestamp: Date.now(),
      type: this.categorizeError(error),
    });

    // Keep only recent failures (last hour)
    const recentFailures = this.failurePatterns
      .get(agentName)
      .filter((f) => Date.now() - f.timestamp < 3600000);
    this.failurePatterns.set(agentName, recentFailures);
  }

  delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  getHealingStats() {
    const stats = {
      totalHealings: this.healingHistory.length,
      strategiesUsed: {},
      successRate: 0,
    };

    this.healingHistory.forEach((healing) => {
      stats.strategiesUsed[healing.strategy] =
        (stats.strategiesUsed[healing.strategy] || 0) + 1;
    });

    return stats;
  }

  async performHealthCheck() {
    const issues = [];

    // Check sub-agent health
    for (const [name, agent] of this.subAgents) {
      try {
        if (typeof agent.healthCheck === "function") {
          const health = await agent.healthCheck();
          if (health.status !== "healthy") {
            issues.push({
              agent: name,
              status: health.status,
              message: health.message,
            });
          }
        }
      } catch (error) {
        issues.push({
          agent: name,
          status: "error",
          message: error.message,
        });
      }
    }

    return {
      status: issues.length === 0 ? "healthy" : "degraded",
      issues,
      timestamp: new Date(),
    };
  }
}

module.exports = { SelfHealingConductor };
```

## 📊 CONDUCTOR MONITORING & METRICS

### Pattern 5: Conductor Monitor

**File**: `agents/conductor-monitor/agent.js`

```javascript
/**
 * Conductor Monitor Agent
 *
 * Monitors conductor performance, tracks metrics, and provides
 * insights for optimization.
 */

const { ConductorAgent } = require("../conductor/base");

class ConductorMonitor extends ConductorAgent {
  constructor(config = {}) {
    super({
      monitoringInterval: 30000, // 30 seconds
      metricsRetention: 86400000, // 24 hours
      alertThresholds: {
        errorRate: 0.05, // 5%
        avgExecutionTime: 300000, // 5 minutes
        failureStreak: 3,
      },
      ...config,
    });

    this.metrics = {
      conductors: new Map(),
      executions: [],
      alerts: [],
      performance: {
        totalExecutions: 0,
        successfulExecutions: 0,
        failedExecutions: 0,
        averageExecutionTime: 0,
        errorRate: 0,
      },
    };

    this.monitoredConductors = new Set();
  }

  registerConductor(conductor, name) {
    this.monitoredConductors.add(name);
    this.metrics.conductors.set(name, {
      name,
      instance: conductor,
      stats: {
        executions: 0,
        successes: 0,
        failures: 0,
        lastExecution: null,
        averageTime: 0,
        errorRate: 0,
      },
    });

    // Monkey patch the conductor's execute method to track metrics
    const originalExecute = conductor.execute.bind(conductor);
    conductor.execute = async (input, context) => {
      const startTime = Date.now();
      const executionId = `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      try {
        const result = await originalExecute(input, context);
        this.recordExecution(
          name,
          executionId,
          true,
          Date.now() - startTime,
          result,
        );
        return result;
      } catch (error) {
        this.recordExecution(
          name,
          executionId,
          false,
          Date.now() - startTime,
          error,
        );
        throw error;
      }
    };

    this.log("info", `Registered conductor for monitoring: ${name}`);
  }

  recordExecution(conductorName, executionId, success, duration, result) {
    const conductorStats = this.metrics.conductors.get(conductorName);
    if (!conductorStats) return;

    // Update conductor stats
    conductorStats.stats.executions++;
    conductorStats.stats.lastExecution = new Date();

    if (success) {
      conductorStats.stats.successes++;
    } else {
      conductorStats.stats.failures++;
    }

    // Update rolling average
    const totalTime =
      conductorStats.stats.averageTime * (conductorStats.stats.executions - 1);
    conductorStats.stats.averageTime =
      (totalTime + duration) / conductorStats.stats.executions;

    // Calculate error rate
    conductorStats.stats.errorRate =
      conductorStats.stats.failures / conductorStats.stats.executions;

    // Record execution
    const execution = {
      id: executionId,
      conductor: conductorName,
      success,
      duration,
      timestamp: new Date(),
      result: success ? "completed" : result.message,
    };

    this.metrics.executions.push(execution);

    // Keep only recent executions
    const cutoff = Date.now() - this.config.metricsRetention;
    this.metrics.executions = this.metrics.executions.filter(
      (e) => e.timestamp.getTime() > cutoff,
    );

    // Check for alerts
    this.checkAlerts(conductorName, conductorStats.stats);

    this.log(
      "debug",
      `Recorded execution: ${conductorName} (${success ? "success" : "failure"}) ${duration}ms`,
    );
  }

  checkAlerts(conductorName, stats) {
    const alerts = [];

    // Error rate alert
    if (stats.errorRate > this.config.alertThresholds.errorRate) {
      alerts.push({
        type: "error_rate",
        conductor: conductorName,
        message: `Error rate ${stats.errorRate.toFixed(2)} exceeds threshold ${this.config.alertThresholds.errorRate}`,
        severity: "high",
        timestamp: new Date(),
      });
    }

    // Execution time alert
    if (stats.averageTime > this.config.alertThresholds.avgExecutionTime) {
      alerts.push({
        type: "performance",
        conductor: conductorName,
        message: `Average execution time ${stats.averageTime}ms exceeds threshold ${this.config.alertThresholds.avgExecutionTime}ms`,
        severity: "medium",
        timestamp: new Date(),
      });
    }

    // Failure streak alert
    const recentExecutions = this.metrics.executions
      .filter((e) => e.conductor === conductorName)
      .slice(-this.config.alertThresholds.failureStreak);

    const recentFailures = recentExecutions.filter((e) => !e.success).length;

    if (recentFailures >= this.config.alertThresholds.failureStreak) {
      alerts.push({
        type: "failure_streak",
        conductor: conductorName,
        message: `${recentFailures} consecutive failures detected`,
        severity: "critical",
        timestamp: new Date(),
      });
    }

    // Add alerts to metrics
    this.metrics.alerts.push(...alerts);

    // Keep only recent alerts
    const cutoff = Date.now() - this.config.metricsRetention;
    this.metrics.alerts = this.metrics.alerts.filter(
      (a) => a.timestamp.getTime() > cutoff,
    );

    // Log alerts
    alerts.forEach((alert) => {
      this.log(
        "warn",
        `ALERT [${alert.severity.toUpperCase()}]: ${alert.message}`,
      );
    });
  }

  getMetrics(conductorName = null) {
    if (conductorName) {
      return this.metrics.conductors.get(conductorName)?.stats || null;
    }

    // Aggregate metrics across all conductors
    const allStats = Array.from(this.metrics.conductors.values()).map(
      (c) => c.stats,
    );

    return {
      totalConductors: this.monitoredConductors.size,
      totalExecutions: allStats.reduce((sum, s) => sum + s.executions, 0),
      totalSuccesses: allStats.reduce((sum, s) => sum + s.successes, 0),
      totalFailures: allStats.reduce((sum, s) => sum + s.failures, 0),
      averageExecutionTime:
        allStats.reduce((sum, s) => sum + s.averageTime, 0) / allStats.length,
      overallErrorRate:
        allStats.reduce((sum, s) => sum + s.errorRate, 0) / allStats.length,
      activeAlerts: this.metrics.alerts.filter(
        (a) => a.timestamp.getTime() > Date.now() - 3600000,
      ).length, // Last hour
      conductorStats: Object.fromEntries(
        Array.from(this.metrics.conductors.entries()).map(([name, data]) => [
          name,
          data.stats,
        ]),
      ),
    };
  }

  getExecutionHistory(conductorName = null, limit = 100) {
    let executions = this.metrics.executions;

    if (conductorName) {
      executions = executions.filter((e) => e.conductor === conductorName);
    }

    return executions.sort((a, b) => b.timestamp - a.timestamp).slice(0, limit);
  }

  getAlerts(severity = null, since = null) {
    let alerts = this.metrics.alerts;

    if (severity) {
      alerts = alerts.filter((a) => a.severity === severity);
    }

    if (since) {
      const sinceTime = new Date(since).getTime();
      alerts = alerts.filter((a) => a.timestamp.getTime() >= sinceTime);
    }

    return alerts.sort((a, b) => b.timestamp - a.timestamp);
  }

  generateReport() {
    const metrics = this.getMetrics();
    const recentAlerts = this.getAlerts(null, new Date(Date.now() - 3600000)); // Last hour
    const recentExecutions = this.getExecutionHistory(null, 50);

    return {
      generatedAt: new Date(),
      summary: {
        totalConductors: metrics.totalConductors,
        totalExecutions: metrics.totalExecutions,
        successRate:
          ((metrics.totalSuccesses / metrics.totalExecutions) * 100).toFixed(
            2,
          ) + "%",
        errorRate:
          ((metrics.totalFailures / metrics.totalExecutions) * 100).toFixed(2) +
          "%",
        averageExecutionTime: Math.round(metrics.averageExecutionTime) + "ms",
        activeAlerts: recentAlerts.length,
      },
      alerts: recentAlerts,
      recentExecutions: recentExecutions,
      conductorPerformance: metrics.conductorStats,
      recommendations: this.generateRecommendations(metrics, recentAlerts),
    };
  }

  generateRecommendations(metrics, alerts) {
    const recommendations = [];

    if (metrics.overallErrorRate > 0.1) {
      recommendations.push({
        type: "reliability",
        priority: "high",
        message:
          "High error rate detected. Consider implementing retry logic or circuit breakers.",
        affectedConductors: Object.entries(metrics.conductorStats)
          .filter(([_, stats]) => stats.errorRate > 0.1)
          .map(([name, _]) => name),
      });
    }

    if (metrics.averageExecutionTime > 300000) {
      recommendations.push({
        type: "performance",
        priority: "medium",
        message:
          "Long execution times detected. Consider optimizing sub-agents or implementing parallel processing.",
        affectedConductors: Object.entries(metrics.conductorStats)
          .filter(([_, stats]) => stats.averageTime > 300000)
          .map(([name, _]) => name),
      });
    }

    if (alerts.length > 5) {
      recommendations.push({
        type: "monitoring",
        priority: "medium",
        message:
          "Multiple alerts detected. Review alert thresholds and conductor health.",
        alertCount: alerts.length,
      });
    }

    return recommendations;
  }

  async startMonitoring() {
    this.monitoringInterval = setInterval(async () => {
      await this.performMonitoringCheck();
    }, this.config.monitoringInterval);

    this.log("info", "Conductor monitoring started");
  }

  async stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }

    this.log("info", "Conductor monitoring stopped");
  }

  async performMonitoringCheck() {
    // Perform health checks on monitored conductors
    for (const conductorName of this.monitoredConductors) {
      const conductorData = this.metrics.conductors.get(conductorName);
      if (!conductorData) continue;

      try {
        // Check if conductor has health check method
        if (typeof conductorData.instance.performHealthCheck === "function") {
          const health = await conductorData.instance.performHealthCheck();

          if (health.status !== "healthy") {
            this.log(
              "warn",
              `Conductor ${conductorName} health check failed: ${health.status}`,
            );
          }
        }
      } catch (error) {
        this.log(
          "error",
          `Health check failed for conductor ${conductorName}: ${error.message}`,
        );
      }
    }
  }
}

// Usage example
async function setupConductorMonitoring() {
  const monitor = new ConductorMonitor();

  // Register conductors to monitor
  monitor.registerConductor(dataProcessingConductor, "data-processing");
  monitor.registerConductor(biConductor, "business-intelligence");
  monitor.registerConductor(selfHealingConductor, "self-healing");

  // Start monitoring
  await monitor.startMonitoring();

  // Generate periodic reports
  setInterval(() => {
    const report = monitor.generateReport();
    console.log("Conductor Performance Report:", report.summary);

    if (report.recommendations.length > 0) {
      console.log("Recommendations:");
      report.recommendations.forEach((rec) => {
        console.log(`- ${rec.priority.toUpperCase()}: ${rec.message}`);
      });
    }
  }, 300000); // Every 5 minutes

  return monitor;
}

module.exports = { ConductorMonitor };
```

## 📋 SUMMARY

### Parent & Sub-Agent Architecture Summary

| Pattern               | Purpose                      | Key Features                                 | Use Case                    |
| --------------------- | ---------------------------- | -------------------------------------------- | --------------------------- |
| **Conductor Base**    | Foundation for orchestration | Workflow definition, error handling, metrics | All complex agent systems   |
| **Data Processing**   | ETL pipelines                | Pipeline stages, data flow, quality checks   | Data integration workflows  |
| **BI Conductor**      | Analytics workflows          | Conditional execution, parallel analysis     | Business intelligence       |
| **Self-Healing**      | Fault tolerance              | Retry logic, fallback strategies             | Critical production systems |
| **Conductor Monitor** | Performance tracking         | Metrics collection, alerting, reporting      | System observability        |

### Best Practices

✅ **Single Responsibility**: Each sub-agent has one clear purpose  
✅ **Loose Coupling**: Sub-agents communicate through well-defined interfaces  
✅ **Error Isolation**: Failures in one sub-agent don't crash the entire conductor  
✅ **Configurable Workflows**: Workflows defined externally, not hardcoded  
✅ **Monitoring**: Comprehensive metrics and alerting for all conductors  
✅ **Testing**: Unit tests for sub-agents, integration tests for conductors

### When to Use Parent/Sub-Agent Pattern

- **Complex Workflows**: Multi-step processes with dependencies
- **Scalable Systems**: Need to add/remove agents without changing core logic
- **Fault Tolerance**: Systems that must continue operating despite failures
- **Performance**: Parallel execution of independent tasks
- **Maintainability**: Clear separation of concerns and responsibilities

This architecture enables building robust, scalable agent systems that can handle complex real-world scenarios while maintaining reliability and performance.</content>
<parameter name="filePath">c:\wamp64\www\birdc_erp\skills\custom-sub-agents\references\06-parent-sub-agent.md
