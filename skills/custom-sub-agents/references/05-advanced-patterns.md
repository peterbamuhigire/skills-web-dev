# 🚀 Advanced Patterns & Orchestration

## 🎭 ADVANCED AGENT PATTERNS

**Purpose**: Complex agent architectures that go beyond basic CRUD operations.

### Pattern 1: Chain of Responsibility

**When to Use**: Sequential processing with multiple validation/filtering steps.

**File**: `agents/data-processor/agent.js`

```javascript
/**
 * Data Processor Agent - Chain of Responsibility Pattern
 *
 * Processes data through a series of handlers, each responsible for
 * a specific transformation or validation step.
 */

class DataProcessorAgent {
  constructor(handlers = []) {
    this.handlers = handlers;
    this.buildChain();
  }

  buildChain() {
    // Link handlers in sequence
    for (let i = 0; i < this.handlers.length - 1; i++) {
      this.handlers[i].setNext(this.handlers[i + 1]);
    }
  }

  async process(data, context = {}) {
    if (this.handlers.length === 0) {
      throw new Error('No handlers configured');
    }

    // Start the chain with the first handler
    return await this.handlers[0].handle(data, context);
  }

  addHandler(handler) {
    this.handlers.push(handler);
    this.buildChain();
  }

  removeHandler(handlerType) {
    this.handlers = this.handlers.filter(h => !(h instanceof handlerType));
    this.buildChain();
  }
}

// Handler base class
class Handler {
  constructor() {
    this.nextHandler = null;
  }

  setNext(handler) {
    this.nextHandler = handler;
    return handler; // Enable method chaining
  }

  async handle(data, context) {
    // Pre-processing
    const result = await this.process(data, context);

    // Pass to next handler if available
    if (this.nextHandler && result.shouldContinue !== false) {
      return await this.nextHandler.handle(result.data, result.context || context);
    }

    return result;
  }

  async process(data, context) {
    // Override in subclasses
    return { data, context, shouldContinue: true };
  }
}

// Concrete handlers
class ValidationHandler extends Handler {
  async process(data, context) {
    console.log('🔍 Validating data...');

    const errors = [];
    if (!data.records || !Array.isArray(data.records)) {
      errors.push('Data must contain a records array');
    }

    if (data.records.length === 0) {
      errors.push('Records array cannot be empty');
    }

    if (errors.length > 0) {
      return {
        data,
        context: { ...context, errors },
        shouldContinue: false,
        status: 'validation_failed'
      };
    }

    return {
      data: { ...data, validationPassed: true },
      context,
      shouldContinue: true
    };
  }
}

class DeduplicationHandler extends Handler {
  async process(data, context) {
    console.log('🗑️ Removing duplicates...');

    const seen = new Set();
    const uniqueRecords = data.records.filter(record => {
      const key = this.generateKey(record);
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });

    return {
      data: {
        ...data,
        records: uniqueRecords,
        duplicatesRemoved: data.records.length - uniqueRecords.length
      },
      context: {
        ...context,
        originalCount: data.records.length,
        uniqueCount: uniqueRecords.length
      },
      shouldContinue: true
    };
  }

  generateKey(record) {
    // Generate unique key based on business logic
    return `${record.customer_id}-${record.date}-${record.amount}`;
  }
}

class EnrichmentHandler extends Handler {
  constructor(customerService, productService) {
    super();
    this.customerService = customerService;
    this.productService = productService;
  }

  async process(data, context) {
    console.log('✨ Enriching data...');

    const enrichedRecords = await Promise.all(
      data.records.map(async (record) => {
        // Enrich with customer data
        const customer = await this.customerService.getById(record.customer_id);
        const product = await this.productService.getById(record.product_id);

        return {
          ...record,
          customer_name: customer?.name || 'Unknown',
          product_name: product?.name || 'Unknown',
          product_category: product?.category || 'Unknown'
        };
      })
    );

    return {
      data: { ...data, records: enrichedRecords },
      context: { ...context, enriched: true },
      shouldContinue: true
    };
  }
}

class AggregationHandler extends Handler {
  async process(data, context) {
    console.log('📊 Aggregating data...');

    const aggregated = data.records.reduce((acc, record) => {
      const key = record.customer_id;
      if (!acc[key]) {
        acc[key] = {
          customer_id: key,
          customer_name: record.customer_name,
          total_amount: 0,
          transaction_count: 0,
          products: new Set()
        };
      }

      acc[key].total_amount += record.amount;
      acc[key].transaction_count += 1;
      acc[key].products.add(record.product_name);

      return acc;
    }, {});

    const summary = Object.values(aggregated).map(customer => ({
      ...customer,
      products: Array.from(customer.products)
    }));

    return {
      data: { ...data, summary },
      context: { ...context, aggregated: true },
      shouldContinue: true
    };
  }
}

class ExportHandler extends Handler {
  constructor(exporter) {
    super();
    this.exporter = exporter;
  }

  async process(data, context) {
    console.log('📤 Exporting results...');

    const exportResult = await this.exporter.export(data, {
      format: context.format || 'json',
      filename: context.filename || `processed-data-${Date.now()}`
    });

    return {
      data: { ...data, exportResult },
      context: { ...context, exported: true },
      shouldContinue: false // End of chain
    };
  }
}

// Usage example
function createDataProcessor() {
  const handlers = [
    new ValidationHandler(),
    new DeduplicationHandler(),
    new EnrichmentHandler(customerService, productService),
    new AggregationHandler(),
    new ExportHandler(jsonExporter)
  ];

  return new DataProcessorAgent(handlers);
}

module.exports = {
  DataProcessorAgent,
  ValidationHandler,
  DeduplicationHandler,
  EnrichmentHandler,
  AggregationHandler,
  ExportHandler
};
```

### Pattern 2: Strategy Pattern

**When to Use**: Multiple algorithms for the same operation, selected at runtime.

**File**: `agents/analyzer/agent.js`

```javascript
/**
 * Analyzer Agent - Strategy Pattern
 *
 * Uses different analysis strategies based on data characteristics
 * and user requirements.
 */

class AnalyzerAgent {
  constructor(strategies = {}) {
    this.strategies = strategies;
    this.defaultStrategy = 'basic';
  }

  registerStrategy(name, strategy) {
    this.strategies[name] = strategy;
  }

  async analyze(data, options = {}) {
    const strategyName = this.selectStrategy(data, options);
    const strategy = this.strategies[strategyName];

    if (!strategy) {
      throw new Error(`Unknown analysis strategy: ${strategyName}`);
    }

    console.log(`📈 Using ${strategyName} analysis strategy`);

    return await strategy.analyze(data, options);
  }

  selectStrategy(data, options) {
    // Strategy selection logic
    if (options.strategy) {
      return options.strategy;
    }

    if (data.length > 10000) {
      return 'big_data';
    }

    if (this.hasTimeSeriesData(data)) {
      return 'time_series';
    }

    if (this.hasGeographicData(data)) {
      return 'geographic';
    }

    return this.defaultStrategy;
  }

  hasTimeSeriesData(data) {
    return data.some(item => item.timestamp || item.date);
  }

  hasGeographicData(data) {
    return data.some(item => item.latitude || item.longitude || item.location);
  }
}

// Strategy base class
class AnalysisStrategy {
  constructor(name) {
    this.name = name;
  }

  async analyze(data, options) {
    throw new Error('analyze() must be implemented by subclass');
  }

  validateData(data) {
    // Common validation logic
    if (!Array.isArray(data)) {
      throw new Error('Data must be an array');
    }

    if (data.length === 0) {
      throw new Error('Data cannot be empty');
    }
  }
}

// Concrete strategies
class BasicAnalysisStrategy extends AnalysisStrategy {
  constructor() {
    super('basic');
  }

  async analyze(data, options) {
    this.validateData(data);

    const summary = {
      totalRecords: data.length,
      averageValue: this.calculateAverage(data),
      minValue: this.findMin(data),
      maxValue: this.findMax(data),
      uniqueValues: this.countUnique(data)
    };

    return {
      strategy: this.name,
      summary,
      data
    };
  }

  calculateAverage(data) {
    const sum = data.reduce((acc, item) => acc + (item.value || 0), 0);
    return sum / data.length;
  }

  findMin(data) {
    return Math.min(...data.map(item => item.value || 0));
  }

  findMax(data) {
    return Math.max(...data.map(item => item.value || 0));
  }

  countUnique(data) {
    const values = data.map(item => item.value).filter(v => v != null);
    return new Set(values).size;
  }
}

class TimeSeriesAnalysisStrategy extends AnalysisStrategy {
  constructor() {
    super('time_series');
  }

  async analyze(data, options) {
    this.validateData(data);

    // Sort by time
    const sortedData = this.sortByTime(data);

    const analysis = {
      trend: this.calculateTrend(sortedData),
      seasonality: this.detectSeasonality(sortedData),
      outliers: this.findOutliers(sortedData),
      forecast: options.forecast ? this.generateForecast(sortedData, options.forecast) : null
    };

    return {
      strategy: this.name,
      analysis,
      data: sortedData
    };
  }

  sortByTime(data) {
    return [...data].sort((a, b) => {
      const timeA = new Date(a.timestamp || a.date);
      const timeB = new Date(b.timestamp || b.date);
      return timeA - timeB;
    });
  }

  calculateTrend(data) {
    // Simple linear regression
    const n = data.length;
    const sumX = data.reduce((sum, _, i) => sum + i, 0);
    const sumY = data.reduce((sum, item) => sum + (item.value || 0), 0);
    const sumXY = data.reduce((sum, item, i) => sum + i * (item.value || 0), 0);
    const sumXX = data.reduce((sum, _, i) => sum + i * i, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    return { slope, intercept, direction: slope > 0 ? 'increasing' : 'decreasing' };
  }

  detectSeasonality(data) {
    // Basic seasonality detection (simplified)
    const values = data.map(item => item.value || 0);
    const periods = [7, 30, 365]; // Daily, monthly, yearly

    const seasonality = periods.map(period => {
      if (values.length < period * 2) return null;

      const correlations = [];
      for (let lag = 1; lag <= period; lag++) {
        const correlation = this.calculateCorrelation(values, lag);
        correlations.push(correlation);
      }

      const avgCorrelation = correlations.reduce((sum, c) => sum + c, 0) / correlations.length;

      return {
        period,
        periodName: period === 7 ? 'weekly' : period === 30 ? 'monthly' : 'yearly',
        strength: avgCorrelation
      };
    }).filter(s => s !== null);

    return seasonality.sort((a, b) => b.strength - a.strength);
  }

  calculateCorrelation(values, lag) {
    let sum = 0;
    let count = 0;

    for (let i = lag; i < values.length; i++) {
      sum += values[i] * values[i - lag];
      count++;
    }

    return count > 0 ? sum / count : 0;
  }

  findOutliers(data) {
    const values = data.map(item => item.value || 0);
    const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
    const stdDev = Math.sqrt(
      values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length
    );

    const threshold = 2 * stdDev; // 2 standard deviations

    return data.filter((item, index) => {
      const deviation = Math.abs(values[index] - mean);
      return deviation > threshold;
    });
  }

  generateForecast(data, periods) {
    // Simple exponential smoothing forecast
    const values = data.map(item => item.value || 0);
    const alpha = 0.3; // Smoothing factor

    let smoothed = values[0];
    const smoothedValues = [smoothed];

    for (let i = 1; i < values.length; i++) {
      smoothed = alpha * values[i] + (1 - alpha) * smoothed;
      smoothedValues.push(smoothed);
    }

    // Generate forecast
    const forecast = [];
    let lastValue = smoothedValues[smoothedValues.length - 1];

    for (let i = 1; i <= periods; i++) {
      lastValue = alpha * lastValue + (1 - alpha) * lastValue; // Simplified
      forecast.push({
        period: i,
        predictedValue: lastValue,
        confidence: Math.max(0.5, 1 - (i * 0.1)) // Decreasing confidence
      });
    }

    return forecast;
  }
}

class BigDataAnalysisStrategy extends AnalysisStrategy {
  constructor() {
    super('big_data');
  }

  async analyze(data, options) {
    this.validateData(data);

    // Use streaming/chunked processing for large datasets
    const chunkSize = options.chunkSize || 1000;
    const chunks = this.chunkArray(data, chunkSize);

    const results = await Promise.all(
      chunks.map(async (chunk, index) => {
        console.log(`Processing chunk ${index + 1}/${chunks.length}`);
        return await this.processChunk(chunk);
      })
    );

    // Combine results
    const combined = this.combineResults(results);

    return {
      strategy: this.name,
      analysis: combined,
      chunksProcessed: chunks.length,
      data
    };
  }

  chunkArray(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  async processChunk(chunk) {
    // Process chunk in parallel
    const promises = chunk.map(async (item) => {
      // Simulate async processing
      await new Promise(resolve => setTimeout(resolve, Math.random() * 10));
      return {
        value: item.value || 0,
        processed: true,
        timestamp: Date.now()
      };
    });

    return await Promise.all(promises);
  }

  combineResults(results) {
    const allValues = results.flat().map(r => r.value);
    const totalProcessed = results.flat().length;

    return {
      totalRecords: totalProcessed,
      averageValue: allValues.reduce((sum, v) => sum + v, 0) / allValues.length,
      minValue: Math.min(...allValues),
      maxValue: Math.max(...allValues),
      processingStats: {
        chunksProcessed: results.length,
        avgProcessingTime: results.flat().reduce((sum, r) => sum + r.timestamp, 0) / totalProcessed
      }
    };
  }
}

// Usage example
function createAnalyzer() {
  const strategies = {
    basic: new BasicAnalysisStrategy(),
    time_series: new TimeSeriesAnalysisStrategy(),
    big_data: new BigDataAnalysisStrategy()
  };

  return new AnalyzerAgent(strategies);
}

module.exports = {
  AnalyzerAgent,
  AnalysisStrategy,
  BasicAnalysisStrategy,
  TimeSeriesAnalysisStrategy,
  BigDataAnalysisStrategy
};
```

### Pattern 3: Observer Pattern

**When to Use**: Notify multiple components when agent state changes.

**File**: `agents/monitor/agent.js`

```javascript
/**
 * Monitor Agent - Observer Pattern
 *
 * Monitors system health and notifies observers of changes.
 * Observers can react to different types of events.
 */

class MonitorAgent {
  constructor(checkInterval = 30000) {
    this.observers = new Map();
    this.checkInterval = checkInterval;
    this.isRunning = false;
    this.lastCheck = null;
    this.status = 'stopped';
  }

  subscribe(eventType, observer) {
    if (!this.observers.has(eventType)) {
      this.observers.set(eventType, new Set());
    }
    this.observers.get(eventType).add(observer);
  }

  unsubscribe(eventType, observer) {
    if (this.observers.has(eventType)) {
      this.observers.get(eventType).delete(observer);
    }
  }

  async notify(eventType, data) {
    if (!this.observers.has(eventType)) {
      return;
    }

    const observers = this.observers.get(eventType);
    const promises = Array.from(observers).map(async (observer) => {
      try {
        await observer.update(eventType, data);
      } catch (error) {
        console.error(`Observer error for ${eventType}:`, error);
      }
    });

    await Promise.allSettled(promises);
  }

  async start() {
    if (this.isRunning) {
      return;
    }

    this.isRunning = true;
    this.status = 'running';
    await this.notify('monitor_started', { timestamp: new Date() });

    this.intervalId = setInterval(async () => {
      await this.performCheck();
    }, this.checkInterval);

    // Perform initial check
    await this.performCheck();
  }

  async stop() {
    if (!this.isRunning) {
      return;
    }

    this.isRunning = false;
    this.status = 'stopped';

    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    await this.notify('monitor_stopped', { timestamp: new Date() });
  }

  async performCheck() {
    const checkStart = new Date();
    this.lastCheck = checkStart;

    try {
      const results = await this.runHealthChecks();

      const checkResult = {
        timestamp: checkStart,
        duration: Date.now() - checkStart.getTime(),
        results,
        overallStatus: this.determineOverallStatus(results)
      };

      await this.notify('health_check_completed', checkResult);

      // Notify about status changes
      if (checkResult.overallStatus !== this.status) {
        const oldStatus = this.status;
        this.status = checkResult.overallStatus;
        await this.notify('status_changed', {
          oldStatus,
          newStatus: this.status,
          timestamp: new Date(),
          checkResult
        });
      }

    } catch (error) {
      console.error('Health check failed:', error);
      await this.notify('health_check_failed', {
        error: error.message,
        timestamp: checkStart
      });
    }
  }

  async runHealthChecks() {
    const checks = [
      { name: 'database', check: this.checkDatabase },
      { name: 'memory', check: this.checkMemory },
      { name: 'cpu', check: this.checkCPU },
      { name: 'disk', check: this.checkDisk },
      { name: 'network', check: this.checkNetwork }
    ];

    const results = await Promise.allSettled(
      checks.map(async ({ name, check }) => {
        const startTime = Date.now();
        try {
          const result = await check.call(this);
          return {
            name,
            status: 'healthy',
            duration: Date.now() - startTime,
            details: result
          };
        } catch (error) {
          return {
            name,
            status: 'unhealthy',
            duration: Date.now() - startTime,
            error: error.message
          };
        }
      })
    );

    return results.map(result => result.value || result.reason);
  }

  determineOverallStatus(results) {
    const hasCriticalFailure = results.some(r => r.status === 'unhealthy' && this.isCritical(r.name));
    const hasWarnings = results.some(r => r.status === 'warning');

    if (hasCriticalFailure) {
      return 'critical';
    } else if (hasWarnings) {
      return 'warning';
    } else {
      return 'healthy';
    }
  }

  isCritical(checkName) {
    const criticalChecks = ['database', 'memory'];
    return criticalChecks.includes(checkName);
  }

  async checkDatabase() {
    // Simulate database health check
    const connectionTime = Math.random() * 100 + 50; // 50-150ms
    await new Promise(resolve => setTimeout(resolve, connectionTime));

    if (Math.random() < 0.9) { // 90% success rate
      return {
        connectionTime: `${connectionTime.toFixed(1)}ms`,
        activeConnections: Math.floor(Math.random() * 50) + 10,
        queryLatency: `${(Math.random() * 20 + 5).toFixed(1)}ms`
      };
    } else {
      throw new Error('Database connection timeout');
    }
  }

  async checkMemory() {
    const memUsage = process.memoryUsage();
    const totalMB = (memUsage.heapTotal / 1024 / 1024).toFixed(1);
    const usedMB = (memUsage.heapUsed / 1024 / 1024).toFixed(1);
    const usagePercent = ((memUsage.heapUsed / memUsage.heapTotal) * 100).toFixed(1);

    if (usagePercent > 90) {
      throw new Error(`High memory usage: ${usagePercent}%`);
    }

    return {
      total: `${totalMB}MB`,
      used: `${usedMB}MB`,
      usage: `${usagePercent}%`
    };
  }

  async checkCPU() {
    // Simplified CPU check
    const loadAverage = Math.random() * 2; // 0-2 (normalized)

    if (loadAverage > 1.5) {
      throw new Error(`High CPU load: ${loadAverage.toFixed(2)}`);
    }

    return {
      loadAverage: loadAverage.toFixed(2),
      cores: require('os').cpus().length
    };
  }

  async checkDisk() {
    // Simulate disk space check
    const freeGB = Math.random() * 100 + 10; // 10-110GB

    if (freeGB < 5) {
      throw new Error(`Low disk space: ${freeGB.toFixed(1)}GB free`);
    }

    return {
      free: `${freeGB.toFixed(1)}GB`,
      status: freeGB > 20 ? 'good' : 'warning'
    };
  }

  async checkNetwork() {
    // Simulate network connectivity check
    const latency = Math.random() * 100 + 10; // 10-110ms

    if (latency > 200) {
      throw new Error(`High network latency: ${latency.toFixed(1)}ms`);
    }

    return {
      latency: `${latency.toFixed(1)}ms`,
      status: latency < 50 ? 'excellent' : latency < 100 ? 'good' : 'fair'
    };
  }

  getStatus() {
    return {
      isRunning: this.isRunning,
      status: this.status,
      lastCheck: this.lastCheck,
      checkInterval: this.checkInterval,
      observerCount: Array.from(this.observers.values()).reduce((sum, set) => sum + set.size, 0)
    };
  }
}

// Observer base class
class Observer {
  constructor(name) {
    this.name = name;
  }

  async update(eventType, data) {
    console.log(`${this.name} received ${eventType}:`, data);
    // Override in subclasses
  }
}

// Concrete observers
class AlertObserver extends Observer {
  constructor(alertService) {
    super('AlertObserver');
    this.alertService = alertService;
  }

  async update(eventType, data) {
    super.update(eventType, data);

    if (eventType === 'status_changed' && data.newStatus === 'critical') {
      await this.alertService.sendAlert({
        level: 'critical',
        message: 'System health status changed to CRITICAL',
        details: data
      });
    } else if (eventType === 'health_check_failed') {
      await this.alertService.sendAlert({
        level: 'error',
        message: 'Health check failed',
        details: data
      });
    }
  }
}

class LoggingObserver extends Observer {
  constructor(logger) {
    super('LoggingObserver');
    this.logger = logger;
  }

  async update(eventType, data) {
    super.update(eventType, data);

    await this.logger.log({
      level: eventType.includes('failed') || eventType.includes('critical') ? 'error' : 'info',
      event: eventType,
      data,
      timestamp: new Date()
    });
  }
}

class MetricsObserver extends Observer {
  constructor(metricsService) {
    super('MetricsObserver');
    this.metricsService = metricsService;
  }

  async update(eventType, data) {
    super.update(eventType, data);

    if (eventType === 'health_check_completed') {
      await this.metricsService.recordMetrics({
        health_check_duration: data.duration,
        overall_status: data.overallStatus,
        checks_count: data.results.length,
        healthy_checks: data.results.filter(r => r.status === 'healthy').length,
        timestamp: data.timestamp
      });
    }
  }
}

class DashboardObserver extends Observer {
  constructor(dashboardService) {
    super('DashboardObserver');
    this.dashboardService = dashboardService;
  }

  async update(eventType, data) {
    super.update(eventType, data);

    if (eventType === 'health_check_completed') {
      await this.dashboardService.updateStatus({
        status: data.overallStatus,
        lastCheck: data.timestamp,
        checks: data.results,
        uptime: this.calculateUptime()
      });
    }
  }

  calculateUptime() {
    // Simplified uptime calculation
    return Math.random() * 100; // Percentage
  }
}

// Usage example
function createMonitor() {
  const monitor = new MonitorAgent(30000); // 30 second intervals

  // Add observers
  monitor.subscribe('health_check_completed', new LoggingObserver(logger));
  monitor.subscribe('status_changed', new AlertObserver(alertService));
  monitor.subscribe('health_check_completed', new MetricsObserver(metricsService));
  monitor.subscribe('health_check_completed', new DashboardObserver(dashboardService));

  return monitor;
}

module.exports = {
  MonitorAgent,
  Observer,
  AlertObserver,
  LoggingObserver,
  MetricsObserver,
  DashboardObserver
};
```

## 🎼 PARENT/SUB-AGENT ORCHESTRATION

**Purpose**: Coordinate multiple specialized agents to solve complex problems.

### Pattern 1: Sequential Execution

**When to Use**: Tasks that must be completed in order, where each step depends on the previous.

**File**: `agents/workflow-orchestrator/agent.js`

```javascript
/**
 * Workflow Orchestrator Agent - Sequential Pattern
 *
 * Executes a series of sub-agents in sequence, passing results
 * from one to the next.
 */

class WorkflowOrchestratorAgent {
  constructor(agents = []) {
    this.agents = agents;
    this.results = new Map();
    this.errors = [];
  }

  async execute(workflow, initialData = {}) {
    console.log('🚀 Starting workflow execution');

    let currentData = { ...initialData };
    const executionResults = [];

    for (let i = 0; i < this.agents.length; i++) {
      const agent = this.agents[i];
      const stepName = workflow.steps[i]?.name || `step_${i + 1}`;

      try {
        console.log(`📋 Executing ${stepName} (${agent.constructor.name})`);

        const stepConfig = workflow.steps[i] || {};
        const stepResult = await this.executeStep(agent, currentData, stepConfig);

        executionResults.push({
          step: stepName,
          agent: agent.constructor.name,
          status: 'completed',
          result: stepResult,
          duration: stepResult.duration
        });

        // Update data for next step
        currentData = {
          ...currentData,
          [stepName]: stepResult.data,
          ...stepResult.outputs // Allow agents to add custom outputs
        };

        this.results.set(stepName, stepResult);

      } catch (error) {
        console.error(`❌ Step ${stepName} failed:`, error);

        const errorResult = {
          step: stepName,
          agent: agent.constructor.name,
          status: 'failed',
          error: error.message,
          duration: Date.now() - (executionResults[executionResults.length - 1]?.startTime || Date.now())
        };

        executionResults.push(errorResult);
        this.errors.push(errorResult);

        // Check if workflow should continue on error
        if (!workflow.continueOnError) {
          throw new Error(`Workflow failed at step ${stepName}: ${error.message}`);
        }
      }
    }

    const finalResult = {
      success: this.errors.length === 0,
      totalSteps: this.agents.length,
      completedSteps: executionResults.filter(r => r.status === 'completed').length,
      failedSteps: this.errors.length,
      executionResults,
      errors: this.errors,
      finalData: currentData,
      duration: this.calculateTotalDuration(executionResults)
    };

    console.log(`✅ Workflow completed: ${finalResult.completedSteps}/${finalResult.totalSteps} steps successful`);

    return finalResult;
  }

  async executeStep(agent, inputData, stepConfig) {
    const startTime = Date.now();

    // Prepare inputs for this agent
    const agentInputs = this.prepareInputs(inputData, stepConfig.inputs || {});

    // Execute agent
    const result = await agent.execute(agentInputs, stepConfig.options || {});

    const duration = Date.now() - startTime;

    return {
      data: result,
      outputs: stepConfig.outputs || {},
      duration,
      startTime,
      endTime: Date.now()
    };
  }

  prepareInputs(data, inputMapping) {
    // Map workflow data to agent inputs
    const inputs = {};

    Object.entries(inputMapping).forEach(([agentParam, workflowKey]) => {
      if (typeof workflowKey === 'string') {
        inputs[agentParam] = this.getNestedValue(data, workflowKey);
      } else if (typeof workflowKey === 'object') {
        // Complex mapping
        inputs[agentParam] = this.transformValue(data, workflowKey);
      } else {
        inputs[agentParam] = workflowKey;
      }
    });

    return inputs;
  }

  getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  transformValue(data, transformation) {
    // Support for simple transformations
    if (transformation.type === 'array_filter') {
      const array = this.getNestedValue(data, transformation.source);
      return array.filter(item => {
        if (transformation.condition) {
          return this.evaluateCondition(item, transformation.condition);
        }
        return true;
      });
    }

    if (transformation.type === 'object_map') {
      const obj = this.getNestedValue(data, transformation.source);
      const mapped = {};
      Object.entries(transformation.mapping).forEach(([newKey, sourceKey]) => {
        mapped[newKey] = this.getNestedValue(obj, sourceKey);
      });
      return mapped;
    }

    return transformation.default || null;
  }

  evaluateCondition(item, condition) {
    const { field, operator, value } = condition;
    const fieldValue = item[field];

    switch (operator) {
      case 'equals': return fieldValue === value;
      case 'not_equals': return fieldValue !== value;
      case 'greater_than': return fieldValue > value;
      case 'less_than': return fieldValue < value;
      case 'contains': return fieldValue?.includes(value);
      case 'in': return Array.isArray(value) && value.includes(fieldValue);
      default: return false;
    }
  }

  calculateTotalDuration(results) {
    if (results.length === 0) return 0;

    const startTime = results[0].startTime;
    const endTime = results[results.length - 1].endTime;

    return endTime - startTime;
  }

  addAgent(agent, stepConfig = {}) {
    this.agents.push(agent);
    // Could store stepConfig for later use
  }

  getResults() {
    return {
      results: Object.fromEntries(this.results),
      errors: this.errors
    };
  }
}

// Example workflow definition
const salesAnalysisWorkflow = {
  name: 'Sales Analysis Pipeline',
  continueOnError: false,
  steps: [
    {
      name: 'data_extraction',
      inputs: {
        startDate: 'config.startDate',
        endDate: 'config.endDate',
        source: 'config.dataSource'
      }
    },
    {
      name: 'data_validation',
      inputs: {
        data: 'data_extraction',
        rules: 'config.validationRules'
      }
    },
    {
      name: 'data_enrichment',
      inputs: {
        records: 'data_validation.validRecords',
        enrichmentConfig: 'config.enrichment'
      }
    },
    {
      name: 'analysis',
      inputs: {
        data: 'data_enrichment',
        analysisType: 'config.analysisType'
      }
    },
    {
      name: 'reporting',
      inputs: {
        analysis: 'analysis',
        format: 'config.reportFormat',
        template: 'config.reportTemplate'
      }
    }
  ]
};

// Usage example
async function runSalesAnalysisWorkflow() {
  const orchestrator = new WorkflowOrchestratorAgent([
    dataExtractionAgent,
    dataValidationAgent,
    dataEnrichmentAgent,
    analysisAgent,
    reportingAgent
  ]);

  const initialData = {
    config: {
      startDate: '2024-01-01',
      endDate: '2024-01-31',
      dataSource: 'sales_db',
      validationRules: ['required_fields', 'data_types'],
      enrichment: { addCustomerData: true, addProductData: true },
      analysisType: 'comprehensive',
      reportFormat: 'pdf',
      reportTemplate: 'sales-summary'
    }
  };

  try {
    const result = await orchestrator.execute(salesAnalysisWorkflow, initialData);

    if (result.success) {
      console.log('✅ Workflow completed successfully');
      console.log(`📊 Generated report: ${result.finalData.reporting.filename}`);
    } else {
      console.log('❌ Workflow completed with errors');
      console.log(`Failed steps: ${result.failedSteps}`);
    }

    return result;
  } catch (error) {
    console.error('💥 Workflow execution failed:', error);
    throw error;
  }
}

module.exports = { WorkflowOrchestratorAgent, salesAnalysisWorkflow };
```

### Pattern 2: Parallel Execution

**When to Use**: Independent tasks that can run simultaneously to improve performance.

**File**: `agents/parallel-orchestrator/agent.js`

```javascript
/**
 * Parallel Orchestrator Agent - Parallel Pattern
 *
 * Executes multiple sub-agents in parallel and combines their results.
 */

class ParallelOrchestratorAgent {
  constructor(maxConcurrency = 5) {
    this.maxConcurrency = maxConcurrency;
    this.activeTasks = new Map();
    this.completedTasks = new Map();
    this.failedTasks = new Map();
  }

  async execute(tasks, options = {}) {
    console.log(`🚀 Starting parallel execution of ${tasks.length} tasks`);

    const {
      timeout = 300000, // 5 minutes
      failFast = false,
      resultCombiner = this.defaultResultCombiner
    } = options;

    const startTime = Date.now();
    const results = new Map();

    try {
      // Execute all tasks in parallel with concurrency control
      const taskPromises = tasks.map((task, index) =>
        this.executeTask(task, index, timeout, failFast)
      );

      // Wait for all tasks to complete
      const taskResults = await Promise.allSettled(taskPromises);

      // Process results
      taskResults.forEach((result, index) => {
        const taskId = `task_${index + 1}`;
        if (result.status === 'fulfilled') {
          results.set(taskId, {
            status: 'completed',
            result: result.value,
            duration: result.value.duration
          });
          this.completedTasks.set(taskId, result.value);
        } else {
          results.set(taskId, {
            status: 'failed',
            error: result.reason.message,
            duration: Date.now() - startTime
          });
          this.failedTasks.set(taskId, result.reason);
        }
      });

      const totalDuration = Date.now() - startTime;
      const combinedResult = await resultCombiner(results, tasks);

      console.log(`✅ Parallel execution completed in ${totalDuration}ms`);
      console.log(`📊 ${this.completedTasks.size} successful, ${this.failedTasks.size} failed`);

      return {
        success: this.failedTasks.size === 0,
        totalTasks: tasks.length,
        completedTasks: this.completedTasks.size,
        failedTasks: this.failedTasks.size,
        results: Object.fromEntries(results),
        combinedResult,
        duration: totalDuration
      };

    } catch (error) {
      console.error('💥 Parallel execution failed:', error);
      throw error;
    }
  }

  async executeTask(task, index, timeout, failFast) {
    const taskId = `task_${index + 1}`;
    const startTime = Date.now();

    console.log(`📋 Starting ${taskId}: ${task.name || task.agent?.constructor?.name}`);

    this.activeTasks.set(taskId, { startTime, task });

    try {
      // Create timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error(`Task ${taskId} timed out after ${timeout}ms`)), timeout);
      });

      // Execute task
      const taskPromise = this.runTask(task);

      // Race between task completion and timeout
      const result = await Promise.race([taskPromise, timeoutPromise]);

      const duration = Date.now() - startTime;

      console.log(`✅ ${taskId} completed in ${duration}ms`);

      return {
        ...result,
        duration,
        taskId,
        startTime,
        endTime: Date.now()
      };

    } catch (error) {
      const duration = Date.now() - startTime;

      console.error(`❌ ${taskId} failed after ${duration}ms:`, error.message);

      if (failFast) {
        throw error;
      }

      throw new Error(`Task ${taskId} failed: ${error.message}`);
    } finally {
      this.activeTasks.delete(taskId);
    }
  }

  async runTask(task) {
    const { agent, inputs = {}, options = {} } = task;

    if (!agent) {
      throw new Error('Task must specify an agent');
    }

    // Execute the agent
    return await agent.execute(inputs, options);
  }

  async defaultResultCombiner(results, tasks) {
    // Default combiner: merge all successful results
    const successfulResults = Array.from(results.entries())
      .filter(([_, result]) => result.status === 'completed')
      .map(([taskId, result]) => ({
        taskId,
        data: result.result.data
      }));

    // Combine data based on task types
    const combined = {};

    successfulResults.forEach(({ taskId, data }) => {
      if (typeof data === 'object' && data !== null) {
        Object.assign(combined, data);
      } else {
        combined[taskId] = data;
      }
    });

    return combined;
  }

  getStatus() {
    return {
      activeTasks: this.activeTasks.size,
      completedTasks: this.completedTasks.size,
      failedTasks: this.failedTasks.size,
      totalTasks: this.activeTasks.size + this.completedTasks.size + this.failedTasks.size
    };
  }

  cancelTask(taskId) {
    // Implementation would depend on how agents handle cancellation
    // This is a simplified version
    if (this.activeTasks.has(taskId)) {
      const task = this.activeTasks.get(taskId);
      // In a real implementation, you'd need to implement cancellation tokens
      console.log(`🛑 Cancelling ${taskId}`);
      this.activeTasks.delete(taskId);
      return true;
    }
    return false;
  }

  async waitForCompletion(timeout = 60000) {
    const startTime = Date.now();

    while (this.activeTasks.size > 0) {
      if (Date.now() - startTime > timeout) {
        throw new Error(`Timeout waiting for task completion after ${timeout}ms`);
      }

      await new Promise(resolve => setTimeout(resolve, 100));
    }

    return this.getStatus();
  }
}

// Specialized combiners for different use cases
class DataAggregationCombiner {
  async combine(results, tasks) {
    const datasets = [];
    const metadata = {};

    results.forEach((result, taskId) => {
      if (result.status === 'completed' && result.result.data) {
        if (Array.isArray(result.result.data)) {
          datasets.push(...result.result.data);
        } else if (typeof result.result.data === 'object') {
          datasets.push(result.result.data);
        }

        // Collect metadata
        if (result.result.metadata) {
          metadata[taskId] = result.result.metadata;
        }
      }
    });

    return {
      combinedData: datasets,
      metadata,
      totalRecords: datasets.length,
      sourceTasks: Array.from(results.keys()).filter(key => results.get(key).status === 'completed')
    };
  }
}

class ReportGenerationCombiner {
  async combine(results, tasks) {
    const reports = [];
    const summary = {
      totalReports: 0,
      successfulReports: 0,
      failedReports: 0,
      totalDataPoints: 0
    };

    results.forEach((result, taskId) => {
      if (result.status === 'completed') {
        reports.push({
          taskId,
          report: result.result,
          generatedAt: new Date()
        });
        summary.successfulReports++;
        summary.totalDataPoints += result.result.dataPoints || 0;
      } else {
        summary.failedReports++;
      }
      summary.totalReports++;
    });

    return {
      reports,
      summary,
      masterReport: this.generateMasterReport(reports)
    };
  }

  generateMasterReport(reports) {
    // Generate a consolidated report from all individual reports
    return {
      title: 'Consolidated Analysis Report',
      generatedAt: new Date(),
      reportCount: reports.length,
      totalDataPoints: reports.reduce((sum, r) => sum + (r.report.dataPoints || 0), 0),
      sections: reports.map(r => ({
        title: r.taskId,
        summary: r.report.summary || 'No summary available'
      }))
    };
  }
}

// Usage examples
async function runParallelDataProcessing() {
  const orchestrator = new ParallelOrchestratorAgent(3); // Max 3 concurrent tasks

  const tasks = [
    {
      name: 'sales_data_extraction',
      agent: salesDataAgent,
      inputs: { source: 'database', table: 'sales_transactions' }
    },
    {
      name: 'customer_data_extraction',
      agent: customerDataAgent,
      inputs: { source: 'database', table: 'customers' }
    },
    {
      name: 'product_data_extraction',
      agent: productDataAgent,
      inputs: { source: 'database', table: 'products' }
    },
    {
      name: 'external_api_data',
      agent: externalAPIAgent,
      inputs: { endpoint: 'https://api.example.com/data', apiKey: process.env.API_KEY }
    }
  ];

  const result = await orchestrator.execute(tasks, {
    timeout: 120000, // 2 minutes
    failFast: false,
    resultCombiner: new DataAggregationCombiner().combine.bind(new DataAggregationCombiner())
  });

  return result;
}

async function runParallelReportGeneration() {
  const orchestrator = new ParallelOrchestratorAgent(5);

  const tasks = [
    { name: 'sales_report', agent: salesReportAgent, inputs: { period: 'monthly' } },
    { name: 'customer_report', agent: customerReportAgent, inputs: { segment: 'premium' } },
    { name: 'product_report', agent: productReportAgent, inputs: { category: 'electronics' } },
    { name: 'regional_report', agent: regionalReportAgent, inputs: { region: 'north_america' } },
    { name: 'trend_report', agent: trendReportAgent, inputs: { timeframe: 'quarterly' } }
  ];

  const result = await orchestrator.execute(tasks, {
    resultCombiner: new ReportGenerationCombiner().combine.bind(new ReportGenerationCombiner())
  });

  return result;
}

module.exports = {
  ParallelOrchestratorAgent,
  DataAggregationCombiner,
  ReportGenerationCombiner
};
```

### Pattern 3: Conditional Execution

**When to Use**: Execute different agents based on conditions or previous results.

**File**: `agents/conditional-orchestrator/agent.js`

```javascript
/**
 * Conditional Orchestrator Agent - Conditional Pattern
 *
 * Executes sub-agents based on conditions, allowing for
 * dynamic workflow branching.
 */

class ConditionalOrchestratorAgent {
  constructor() {
    this.conditions = new Map();
    this.actions = new Map();
    this.results = new Map();
    this.executionPath = [];
  }

  // Define conditions
  when(conditionName, conditionFn) {
    this.conditions.set(conditionName, conditionFn);
    return this;
  }

  // Define actions for conditions
  then(conditionName, agent, inputs = {}, options = {}) {
    if (!this.actions.has(conditionName)) {
      this.actions.set(conditionName, []);
    }

    this.actions.get(conditionName).push({
      agent,
      inputs,
      options,
      type: 'then'
    });

    return this;
  }

  otherwise(agent, inputs = {}, options = {}) {
    // Find the last condition and add otherwise action
    const lastCondition = Array.from(this.conditions.keys()).pop();
    if (lastCondition) {
      if (!this.actions.has(lastCondition)) {
        this.actions.set(lastCondition, []);
      }

      this.actions.get(lastCondition).push({
        agent,
        inputs,
        options,
        type: 'otherwise'
      });
    }

    return this;
  }

  async execute(initialData = {}, context = {}) {
    console.log('🚀 Starting conditional workflow execution');

    const startTime = Date.now();
    let currentData = { ...initialData };
    let currentContext = { ...context };

    this.executionPath = [];
    this.results.clear();

    try {
      for (const [conditionName, conditionFn] of this.conditions) {
        console.log(`🔍 Evaluating condition: ${conditionName}`);

        const conditionResult = await this.evaluateCondition(conditionFn, currentData, currentContext);

        this.executionPath.push({
          condition: conditionName,
          result: conditionResult,
          timestamp: new Date()
        });

        if (conditionResult) {
          // Execute "then" actions
          const thenActions = this.actions.get(conditionName)?.filter(a => a.type === 'then') || [];
          currentData = await this.executeActions(thenActions, currentData, currentContext, conditionName, 'then');
        } else {
          // Execute "otherwise" actions
          const otherwiseActions = this.actions.get(conditionName)?.filter(a => a.type === 'otherwise') || [];
          currentData = await this.executeActions(otherwiseActions, currentData, currentContext, conditionName, 'otherwise');
        }
      }

      const totalDuration = Date.now() - startTime;

      const finalResult = {
        success: true,
        executionPath: this.executionPath,
        results: Object.fromEntries(this.results),
        finalData: currentData,
        duration: totalDuration,
        conditionsEvaluated: this.conditions.size,
        actionsExecuted: this.executionPath.length
      };

      console.log(`✅ Conditional workflow completed in ${totalDuration}ms`);
      console.log(`📊 Executed ${finalResult.actionsExecuted} action branches`);

      return finalResult;

    } catch (error) {
      console.error('💥 Conditional workflow failed:', error);
      throw error;
    }
  }

  async evaluateCondition(conditionFn, data, context) {
    try {
      // Support both function and string conditions
      if (typeof conditionFn === 'function') {
        return await conditionFn(data, context);
      } else if (typeof conditionFn === 'string') {
        return this.evaluateStringCondition(conditionFn, data, context);
      }

      return false;
    } catch (error) {
      console.error('Condition evaluation failed:', error);
      return false;
    }
  }

  evaluateStringCondition(condition, data, context) {
    // Simple expression evaluator for common conditions
    const expressions = {
      'data.length > 1000': () => data.length > 1000,
      'data.status === "error"': () => data.status === 'error',
      'context.user.role === "admin"': () => context.user?.role === 'admin',
      'data.total > 10000': () => data.total > 10000,
      'data.records && data.records.length > 0': () => data.records && data.records.length > 0
    };

    return expressions[condition]?.() || false;
  }

  async executeActions(actions, data, context, conditionName, actionType) {
    let currentData = { ...data };

    for (const action of actions) {
      const actionId = `${conditionName}_${actionType}_${action.agent.constructor.name}`;

      try {
        console.log(`📋 Executing ${actionId}`);

        const inputs = this.resolveInputs(action.inputs, currentData, context);
        const result = await action.agent.execute(inputs, action.options);

        this.results.set(actionId, {
          status: 'completed',
          result,
          executedAt: new Date()
        });

        // Update data with action results
        currentData = {
          ...currentData,
          [actionId]: result,
          ...result // Allow agents to add custom outputs to data
        };

      } catch (error) {
        console.error(`❌ Action ${actionId} failed:`, error);

        this.results.set(actionId, {
          status: 'failed',
          error: error.message,
          executedAt: new Date()
        });

        // Continue with other actions unless specified otherwise
        if (action.options?.failFast) {
          throw error;
        }
      }
    }

    return currentData;
  }

  resolveInputs(inputTemplate, data, context) {
    const resolved = {};

    Object.entries(inputTemplate).forEach(([key, value]) => {
      if (typeof value === 'string' && value.startsWith('$')) {
        // Reference to data or context
        const path = value.substring(1); // Remove $
        resolved[key] = this.getNestedValue({ data, context }, path);
      } else if (typeof value === 'function') {
        // Dynamic value
        resolved[key] = value(data, context);
      } else {
        // Static value
        resolved[key] = value;
      }
    });

    return resolved;
  }

  getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  // Builder methods for fluent API
  ifCondition(conditionName, conditionFn) {
    return this.when(conditionName, conditionFn);
  }

  thenExecute(agent, inputs = {}, options = {}) {
    const lastCondition = Array.from(this.conditions.keys()).pop();
    if (lastCondition) {
      this.then(lastCondition, agent, inputs, options);
    }
    return this;
  }

  elseExecute(agent, inputs = {}, options = {}) {
    this.otherwise(agent, inputs, options);
    return this;
  }

  getExecutionPath() {
    return this.executionPath;
  }

  getResults() {
    return Object.fromEntries(this.results);
  }
}

// Predefined condition functions
const Conditions = {
  hasData: (data) => data && (Array.isArray(data) ? data.length > 0 : Object.keys(data).length > 0),
  hasErrors: (data) => data.errors && data.errors.length > 0,
  isLargeDataset: (data) => Array.isArray(data) && data.length > 10000,
  isAdminUser: (data, context) => context.user?.role === 'admin',
  hasValidRecords: (data) => data.validRecords && data.validRecords.length > 0,
  exceedsThreshold: (threshold) => (data) => data.total > threshold,
  hasRequiredFields: (fields) => (data) => fields.every(field => data[field] != null)
};

// Usage examples
async function createDataProcessingWorkflow() {
  const orchestrator = new ConditionalOrchestratorAgent();

  // Define workflow logic
  orchestrator
    .when('has_data', Conditions.hasData)
    .then(dataValidationAgent, { data: '$data' })
    .otherwise(noDataAgent, { message: 'No data available' })

    .when('validation_passed', (data) => !data.errors || data.errors.length === 0)
    .then(dataProcessingAgent, { data: '$data.validRecords' })
    .otherwise(errorHandlingAgent, { errors: '$data.errors' })

    .when('is_large_dataset', Conditions.isLargeDataset)
    .then(parallelProcessingAgent, { data: '$data', chunks: 10 })
    .otherwise(sequentialProcessingAgent, { data: '$data' })

    .when('processing_successful', (data) => data.status === 'completed')
    .then(reportingAgent, { results: '$data.results' })
    .otherwise(retryAgent, { failedData: '$data' });

  return orchestrator;
}

async function createUserRoleWorkflow() {
  const orchestrator = new ConditionalOrchestratorAgent();

  orchestrator
    .when('is_admin', Conditions.isAdminUser)
    .then(adminDashboardAgent, { user: '$context.user' })
    .otherwise(standardDashboardAgent, { user: '$context.user' })

    .when('has_permissions', (data, context) => context.user.permissions?.includes('export'))
    .then(exportAgent, { data: '$data' })
    .otherwise(viewOnlyAgent, { data: '$data' });

  return orchestrator;
}

async function createBusinessLogicWorkflow() {
  const orchestrator = new ConditionalOrchestratorAgent();

  orchestrator
    .when('sales_above_threshold', Conditions.exceedsThreshold(100000))
    .then(highValueSalesAgent, { sales: '$data' })
    .otherwise(standardSalesAgent, { sales: '$data' })

    .when('customer_is_vip', (data) => data.customer?.tier === 'vip')
    .then(vipProcessingAgent, { customer: '$data.customer' })
    .otherwise(standardProcessingAgent, { customer: '$data.customer' });

  return orchestrator;
}

// Execution example
async function runConditionalWorkflow() {
  const workflow = await createDataProcessingWorkflow();

  const testData = {
    records: [
      { id: 1, name: 'Item 1', value: 100 },
      { id: 2, name: 'Item 2', value: 200 }
    ],
    source: 'database'
  };

  const context = {
    user: { id: 123, role: 'analyst' },
    requestId: 'req_456'
  };

  try {
    const result = await workflow.execute(testData, context);

    console.log('Workflow execution path:');
    result.executionPath.forEach(step => {
      console.log(`  ${step.condition}: ${step.result}`);
    });

    return result;
  } catch (error) {
    console.error('Workflow execution failed:', error);
    throw error;
  }
}

module.exports = {
  ConditionalOrchestratorAgent,
  Conditions
};
```

## 📁 PROJECT ORGANIZATION PATTERNS

### Pattern 1: Agent Registry

**When to Use**: Manage multiple agents with discovery and instantiation.

**File**: `agents/registry.js`

```javascript
/**
 * Agent Registry
 *
 * Centralized registry for agent discovery, instantiation, and management.
 */

class AgentRegistry {
  constructor() {
    this.agents = new Map();
    this.categories = new Map();
    this.dependencies = new Map();
  }

  register(agentClass, metadata = {}) {
    const agentName = metadata.name || agentClass.name;

    this.agents.set(agentName, {
      class: agentClass,
      metadata: {
        name: agentName,
        description: metadata.description || '',
        category: metadata.category || 'general',
        version: metadata.version || '1.0.0',
        author: metadata.author || '',
        tags: metadata.tags || [],
        inputs: metadata.inputs || {},
        outputs: metadata.outputs || {},
        dependencies: metadata.dependencies || [],
        ...metadata
      }
    });

    // Register in category
    if (!this.categories.has(metadata.category)) {
      this.categories.set(metadata.category, new Set());
    }
    this.categories.get(metadata.category).add(agentName);

    // Register dependencies
    if (metadata.dependencies) {
      this.dependencies.set(agentName, metadata.dependencies);
    }

    console.log(`✅ Registered agent: ${agentName} (${metadata.category})`);
  }

  unregister(agentName) {
    if (this.agents.has(agentName)) {
      const metadata = this.agents.get(agentName).metadata;

      // Remove from category
      if (this.categories.has(metadata.category)) {
        this.categories.get(metadata.category).delete(agentName);
      }

      // Remove dependencies
      this.dependencies.delete(agentName);

      // Remove agent
      this.agents.delete(agentName);

      console.log(`🗑️ Unregistered agent: ${agentName}`);
      return true;
    }
    return false;
  }

  async create(agentName, config = {}) {
    const agentInfo = this.agents.get(agentName);
    if (!agentInfo) {
      throw new Error(`Agent not found: ${agentName}`);
    }

    // Check dependencies
    await this.checkDependencies(agentName);

    // Create instance
    try {
      const instance = new agentInfo.class(config);
      console.log(`🏗️ Created agent instance: ${agentName}`);
      return instance;
    } catch (error) {
      console.error(`Failed to create agent ${agentName}:`, error);
      throw error;
    }
  }

  async checkDependencies(agentName) {
    const deps = this.dependencies.get(agentName);
    if (!deps || deps.length === 0) {
      return;
    }

    const missingDeps = [];
    for (const dep of deps) {
      if (!this.agents.has(dep)) {
        missingDeps.push(dep);
      }
    }

    if (missingDeps.length > 0) {
      throw new Error(`Missing dependencies for ${agentName}: ${missingDeps.join(', ')}`);
    }
  }

  get(agentName) {
    return this.agents.get(agentName);
  }

  list(category = null) {
    if (category) {
      const categoryAgents = this.categories.get(category);
      if (!categoryAgents) {
        return [];
      }

      return Array.from(categoryAgents).map(name => ({
        name,
        ...this.agents.get(name).metadata
      }));
    }

    return Array.from(this.agents.entries()).map(([name, info]) => ({
      name,
      ...info.metadata
    }));
  }

  search(query) {
    const results = [];
    const queryLower = query.toLowerCase();

    for (const [name, info] of this.agents) {
      const metadata = info.metadata;
      if (
        name.toLowerCase().includes(queryLower) ||
        metadata.description.toLowerCase().includes(queryLower) ||
        metadata.tags.some(tag => tag.toLowerCase().includes(queryLower)) ||
        metadata.category.toLowerCase().includes(queryLower)
      ) {
        results.push({ name, ...metadata });
      }
    }

    return results;
  }

  getCategories() {
    const categories = {};
    for (const [category, agents] of this.categories) {
      categories[category] = {
        count: agents.size,
        agents: Array.from(agents)
      };
    }
    return categories;
  }

  getStats() {
    return {
      totalAgents: this.agents.size,
      categories: this.categories.size,
      categoryBreakdown: Object.fromEntries(
        Array.from(this.categories.entries()).map(([cat, agents]) => [cat, agents.size])
      )
    };
  }

  async validateAgent(agentName) {
    const agentInfo = this.agents.get(agentName);
    if (!agentInfo) {
      return { valid: false, error: 'Agent not found' };
    }

    const issues = [];

    // Check required metadata
    const requiredFields = ['name', 'description', 'category'];
    for (const field of requiredFields) {
      if (!agentInfo.metadata[field]) {
        issues.push(`Missing required field: ${field}`);
      }
    }

    // Check dependencies
    try {
      await this.checkDependencies(agentName);
    } catch (error) {
      issues.push(`Dependency issue: ${error.message}`);
    }

    // Try to instantiate
    try {
      const testInstance = new agentInfo.class({});
      if (typeof testInstance.execute !== 'function') {
        issues.push('Agent class must have an execute method');
      }
    } catch (error) {
      issues.push(`Instantiation failed: ${error.message}`);
    }

    return {
      valid: issues.length === 0,
      issues
    };
  }
}

// Global registry instance
const globalRegistry = new AgentRegistry();

// Helper functions
function registerAgent(agentClass, metadata) {
  globalRegistry.register(agentClass, metadata);
}

function createAgent(agentName, config) {
  return globalRegistry.create(agentName, config);
}

function listAgents(category) {
  return globalRegistry.list(category);
}

function searchAgents(query) {
  return globalRegistry.search(query);
}

// Auto-discover agents from directories
async function discoverAgents(basePath = './agents') {
  const fs = require('fs').promises;
  const path = require('path');

  try {
    const categories = await fs.readdir(basePath);

    for (const category of categories) {
      const categoryPath = path.join(basePath, category);

      try {
        const stat = await fs.stat(categoryPath);
        if (!stat.isDirectory()) continue;

        const agentFiles = await fs.readdir(categoryPath);
        const indexFile = agentFiles.find(file => file === 'index.js' || file === 'agent.js');

        if (indexFile) {
          try {
            const agentModule = require(path.join(categoryPath, indexFile));

            // Look for agent classes (classes that have execute method)
            Object.entries(agentModule).forEach(([exportName, exportValue]) => {
              if (typeof exportValue === 'function' && exportValue.prototype?.execute) {
                const metadata = {
                  name: exportName,
                  category,
                  autoDiscovered: true,
                  path: path.join(categoryPath, indexFile)
                };

                globalRegistry.register(exportValue, metadata);
              }
            });
          } catch (error) {
            console.warn(`Failed to load agent from ${categoryPath}:`, error.message);
          }
        }
      } catch (error) {
        console.warn(`Failed to read category ${category}:`, error.message);
      }
    }

    console.log(`🔍 Auto-discovered ${globalRegistry.getStats().totalAgents} agents`);
  } catch (error) {
    console.warn('Agent discovery failed:', error.message);
  }
}

module.exports = {
  AgentRegistry,
  globalRegistry,
  registerAgent,
  createAgent,
  listAgents,
  searchAgents,
  discoverAgents
};
```

### Pattern 2: Agent Factory

**When to Use**: Create agents with complex configuration and dependency injection.

**File**: `agents/factory.js`

```javascript
/**
 * Agent Factory
 *
 * Creates and configures agents with proper dependency injection
 * and configuration management.
 */

class AgentFactory {
  constructor() {
    this.builders = new Map();
    this.configurations = new Map();
    this.dependencies = new Map();
  }

  registerBuilder(agentType, builder) {
    this.builders.set(agentType, builder);
  }

  registerConfiguration(agentType, config) {
    this.configurations.set(agentType, config);
  }

  registerDependency(name, dependency) {
    this.dependencies.set(name, dependency);
  }

  async create(agentType, customConfig = {}) {
    const builder = this.builders.get(agentType);
    if (!builder) {
      throw new Error(`No builder registered for agent type: ${agentType}`);
    }

    const baseConfig = this.configurations.get(agentType) || {};
    const config = { ...baseConfig, ...customConfig };

    // Resolve dependencies
    const resolvedDeps = await this.resolveDependencies(config.dependencies || []);

    // Create agent using builder
    const agent = await builder(config, resolvedDeps);

    console.log(`🏭 Created ${agentType} agent with config:`, Object.keys(config));
    return agent;
  }

  async resolveDependencies(depNames) {
    const resolved = {};

    for (const depName of depNames) {
      if (this.dependencies.has(depName)) {
        resolved[depName] = this.dependencies.get(depName);
      } else {
        // Try to create dependency if it's another agent type
        try {
          resolved[depName] = await this.create(depName);
        } catch (error) {
          throw new Error(`Cannot resolve dependency ${depName}: ${error.message}`);
        }
      }
    }

    return resolved;
  }

  createBulk(agentConfigs) {
    const promises = agentConfigs.map(config =>
      this.create(config.type, config.config)
    );

    return Promise.all(promises);
  }

  getAvailableTypes() {
    return Array.from(this.builders.keys());
  }

  validateConfiguration(agentType, config) {
    const baseConfig = this.configurations.get(agentType);
    if (!baseConfig) {
      return { valid: false, error: `No configuration found for ${agentType}` };
    }

    const issues = [];

    // Check required fields
    if (baseConfig.required) {
      for (const field of baseConfig.required) {
        if (!(field in config)) {
          issues.push(`Missing required field: ${field}`);
        }
      }
    }

    // Validate field types
    if (baseConfig.types) {
      for (const [field, expectedType] of Object.entries(baseConfig.types)) {
        if (field in config) {
          const actualType = typeof config[field];
          if (actualType !== expectedType) {
            issues.push(`Field ${field} should be ${expectedType}, got ${actualType}`);
          }
        }
      }
    }

    return {
      valid: issues.length === 0,
      issues
    };
  }
}

// Builder functions for different agent types
const builders = {
  async salesAnalyzer(config, deps) {
    const { SalesAnalyzerAgent } = require('./sales-analyzer/agent');

    return new SalesAnalyzerAgent({
      database: deps.database,
      reporting: deps.reporting,
      cache: deps.cache,
      ...config
    });
  },

  async dataProcessor(config, deps) {
    const { DataProcessorAgent } = require('./data-processor/agent');

    return new DataProcessorAgent({
      validation: deps.validation,
      enrichment: deps.enrichment,
      storage: deps.storage,
      ...config
    });
  },

  async monitor(config, deps) {
    const { MonitorAgent } = require('./monitor/agent');

    return new MonitorAgent({
      logger: deps.logger,
      alerting: deps.alerting,
      metrics: deps.metrics,
      ...config
    });
  },

  async workflowOrchestrator(config, deps) {
    const { WorkflowOrchestratorAgent } = require('./workflow-orchestrator/agent');

    // Create sub-agents
    const subAgents = [];
    if (config.subAgents) {
      for (const subAgentConfig of config.subAgents) {
        const subAgent = await factory.create(subAgentConfig.type, subAgentConfig.config);
        subAgents.push(subAgent);
      }
    }

    return new WorkflowOrchestratorAgent(subAgents, {
      workflow: config.workflow,
      ...deps
    });
  }
};

// Configuration templates
const configurations = {
  salesAnalyzer: {
    required: ['database'],
    types: {
      maxRecords: 'number',
      enableCache: 'boolean'
    },
    defaults: {
      maxRecords: 10000,
      enableCache: true,
      dependencies: ['database', 'reporting', 'cache']
    }
  },

  dataProcessor: {
    required: ['input'],
    types: {
      batchSize: 'number',
      validateData: 'boolean'
    },
    defaults: {
      batchSize: 100,
      validateData: true,
      dependencies: ['validation', 'enrichment', 'storage']
    }
  },

  monitor: {
    types: {
      checkInterval: 'number',
      enableAlerts: 'boolean'
    },
    defaults: {
      checkInterval: 30000,
      enableAlerts: true,
      dependencies: ['logger', 'alerting', 'metrics']
    }
  },

  workflowOrchestrator: {
    required: ['subAgents', 'workflow'],
    defaults: {
      continueOnError: false,
      dependencies: []
    }
  }
};

// Create and configure factory
const factory = new AgentFactory();

// Register builders
Object.entries(builders).forEach(([type, builder]) => {
  factory.registerBuilder(type, builder);
});

// Register configurations
Object.entries(configurations).forEach(([type, config]) => {
  factory.registerConfiguration(type, config);
});

// Register common dependencies
factory.registerDependency('database', createDatabaseConnection());
factory.registerDependency('reporting', createReportingService());
factory.registerDependency('cache', createCacheService());
factory.registerDependency('validation', createValidationService());
factory.registerDependency('enrichment', createEnrichmentService());
factory.registerDependency('storage', createStorageService());
factory.registerDependency('logger', createLogger());
factory.registerDependency('alerting', createAlertingService());
factory.registerDependency('metrics', createMetricsService());

// Helper functions (simplified - would be actual implementations)
function createDatabaseConnection() { return { query: async () => [] }; }
function createReportingService() { return { generate: async () => ({}) }; }
function createCacheService() { return { get: () => null, set: () => {} }; }
function createValidationService() { return { validate: () => ({ valid: true }) }; }
function createEnrichmentService() { return { enrich: async (data) => data }; }
function createStorageService() { return { save: async () => {} }; }
function createLogger() { return { log: () => {} }; }
function createAlertingService() { return { alert: () => {} }; }
function createMetricsService() { return { record: () => {} }; }

module.exports = {
  AgentFactory,
  factory
};
```

## 📋 SUMMARY

### Advanced Patterns Summary

| Pattern | Purpose | When to Use | Example |
|---------|---------|-------------|---------|
| **Chain of Responsibility** | Sequential processing with multiple steps | Data pipelines, validation chains | DataProcessorAgent |
| **Strategy** | Multiple algorithms for same operation | Different analysis methods, export formats | AnalyzerAgent |
| **Observer** | Event-driven notifications | Monitoring, logging, alerts | MonitorAgent |
| **Sequential Orchestration** | Ordered task execution | Workflows, pipelines | WorkflowOrchestratorAgent |
| **Parallel Orchestration** | Concurrent task execution | Independent operations, performance | ParallelOrchestratorAgent |
| **Conditional Orchestration** | Dynamic branching | Business rules, error handling | ConditionalOrchestratorAgent |
| **Registry** | Agent discovery and management | Large agent ecosystems | AgentRegistry |
| **Factory** | Complex agent creation | Dependency injection, configuration | AgentFactory |

### Best Practices

✅ **Single Responsibility**: Each agent has one clear purpose  
✅ **Dependency Injection**: Pass dependencies explicitly  
✅ **Configuration Management**: Externalize config from code  
✅ **Error Handling**: Graceful failure with meaningful messages  
✅ **Logging**: Comprehensive logging for debugging  
✅ **Testing**: Unit and integration tests for all agents  
✅ **Documentation**: Clear interfaces and usage examples  

### When to Use Advanced Patterns

- **Chain**: Multi-step data processing
- **Strategy**: Multiple approaches to same problem
- **Observer**: Event-driven systems
- **Sequential**: Dependent tasks
- **Parallel**: Independent tasks
- **Conditional**: Business logic branching
- **Registry**: Many agents to manage
- **Factory**: Complex agent setup

This structure enables building sophisticated agent systems that are maintainable, testable, and scalable.</content>
<parameter name="filePath">c:\wamp64\www\birdc_erp\skills\custom-sub-agents\references\05-advanced-patterns.md