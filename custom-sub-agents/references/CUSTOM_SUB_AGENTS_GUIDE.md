# 📁 Agent Folder Structure - Complete Guide

**Goal**: Keep each agent self-contained with code, config, and README clearly separated.

---

## 🏗️ Complete Folder Structure Per Agent

```
agents/sales-analyzer/
├── agent.js                 ← The actual agent code (logic/implementation)
├── config.json             ← Configuration settings (non-sensitive)
├── README.md               ← Documentation (how to use this agent)
├── package.json            ← Dependencies (for Node.js agents)
├── .env.example            ← Environment variables template (sensitive values)
├── index.js                ← Export/entry point
├── tests/                  ← Test files
│   ├── agent.test.js
│   └── integration.test.js
└── tools/                  ← Helper functions/utilities
    ├── database.js
    ├── reporting.js
    └── validation.js
```

---

## 📝 **1. agent.js - The Agent Code**

**Purpose**: Contains the actual agent logic and implementation.

### What Goes Here

- Main agent class/function
- Core business logic
- Method definitions
- Integration with tools and services

### Node.js Example

**File**: `agents/sales-analyzer/agent.js`

```javascript
/**
 * Sales Analyzer Agent
 *
 * Analyzes sales data, generates insights, and forecasts trends.
 * This is the core implementation of the agent.
 */

const axios = require("axios");
const DatabaseHelper = require("./tools/database");
const ReportGenerator = require("./tools/reporting");
const Validator = require("./tools/validation");

class SalesAnalyzerAgent {
  constructor(config) {
    // Load configuration
    this.config = config;
    this.name = "Sales Analyzer Agent";
    this.version = "1.0.0";

    // Initialize tools
    this.db = new DatabaseHelper(config.database);
    this.reporter = new ReportGenerator();
    this.validator = new Validator();

    // Define capabilities
    this.tools = ["analyze", "forecast", "generateReport", "exportData"];
  }

  /**
   * Analyze sales data based on query
   * @param {Object} options - Query options
   * @param {string} options.period - Time period (daily, weekly, monthly)
   * @param {string} options.region - Optional region filter
   * @returns {Promise<Object>} Analysis results
   */
  async analyze(options) {
    try {
      console.log(`[${this.name}] Analyzing sales data...`, options);

      // Validate input
      this.validator.validateAnalysisOptions(options);

      // Query database
      const data = await this.db.querySales({
        period: options.period,
        region: options.region,
      });

      // Calculate metrics
      const metrics = this.calculateMetrics(data);

      // Generate insights
      const insights = this.generateInsights(metrics);

      return {
        success: true,
        timestamp: new Date(),
        metrics,
        insights,
        dataPoints: data.length,
      };
    } catch (error) {
      console.error(`[${this.name}] Analysis failed:`, error);
      throw error;
    }
  }

  /**
   * Forecast future sales
   * @param {Object} options - Forecast options
   * @returns {Promise<Object>} Forecast results
   */
  async forecast(options) {
    try {
      console.log(`[${this.name}] Generating forecast...`);

      const historicalData = await this.db.getHistoricalData(12); // 12 months

      // Simple forecast (you'd use ML in production)
      const forecast = this.calculateForecast(historicalData, options.months);

      return {
        success: true,
        forecast,
        confidence: 0.85,
        methodology: "Moving Average",
      };
    } catch (error) {
      console.error(`[${this.name}] Forecast failed:`, error);
      throw error;
    }
  }

  /**
   * Generate detailed report
   * @param {Object} options - Report options
   * @returns {Promise<Object>} Report path
   */
  async generateReport(options) {
    try {
      console.log(`[${this.name}] Generating report...`);

      // Analyze data
      const analysis = await this.analyze({
        period: options.period || "monthly",
      });

      // Generate report
      const reportPath = await this.reporter.generate({
        title: options.title || "Sales Analysis Report",
        data: analysis,
        format: options.format || "pdf",
      });

      return {
        success: true,
        reportPath,
        format: options.format || "pdf",
        size: "calculated in reporter",
      };
    } catch (error) {
      console.error(`[${this.name}] Report generation failed:`, error);
      throw error;
    }
  }

  /**
   * Export data in specified format
   * @param {Object} options - Export options
   * @returns {Promise<Object>} Export results
   */
  async exportData(options) {
    try {
      const data = await this.db.querySales(options);

      const exportPath = await this.reporter.export(data, {
        format: options.format || "csv",
        filename: options.filename || "sales-data",
      });

      return {
        success: true,
        exportPath,
        format: options.format,
        rows: data.length,
      };
    } catch (error) {
      console.error(`[${this.name}] Export failed:`, error);
      throw error;
    }
  }

  /**
   * Main run method - orchestrates agent execution
   * @param {Object} input - Input parameters
   * @returns {Promise<Object>} Results
   */
  async run(input) {
    console.log(`[${this.name}] Starting with input:`, input);

    // Route to appropriate method based on input
    if (input.action === "analyze") {
      return await this.analyze(input);
    } else if (input.action === "forecast") {
      return await this.forecast(input);
    } else if (input.action === "report") {
      return await this.generateReport(input);
    } else if (input.action === "export") {
      return await this.exportData(input);
    } else {
      throw new Error(`Unknown action: ${input.action}`);
    }
  }

  // ====== HELPER METHODS ======

  calculateMetrics(data) {
    // Calculate total, average, growth rate, etc.
    return {
      total: data.reduce((sum, d) => sum + d.amount, 0),
      average: data.reduce((sum, d) => sum + d.amount, 0) / data.length,
      count: data.length,
      min: Math.min(...data.map((d) => d.amount)),
      max: Math.max(...data.map((d) => d.amount)),
    };
  }

  generateInsights(metrics) {
    // Generate business insights from metrics
    const insights = [];

    if (metrics.growth > 0.1) {
      insights.push("Strong positive growth detected");
    }

    return insights;
  }

  calculateForecast(historicalData, months) {
    // Simple moving average forecast
    const avg = historicalData.reduce((a, b) => a + b) / historicalData.length;
    return Array(months).fill(avg);
  }
}

module.exports = SalesAnalyzerAgent;
```

### Python Example

**File**: `agents/data-processor/agent.py`

```python
"""
Data Processor Agent

Processes, validates, and cleans data files.
This is the core implementation of the agent.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

class DataProcessorAgent:
    def __init__(self, config):
        """Initialize the agent with configuration"""
        self.config = config
        self.name = "Data Processor Agent"
        self.version = "1.0.0"

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Define capabilities
        self.tools = [
            'process',
            'validate',
            'clean',
            'detect_anomalies',
            'export'
        ]

    def process(self, input_file, output_format='json'):
        """
        Process a data file

        Args:
            input_file (str): Path to input file
            output_format (str): Output format (json, csv, excel)

        Returns:
            dict: Processing results
        """
        try:
            self.logger.info(f"[{self.name}] Processing {input_file}...")

            # Load data
            data = self._load_data(input_file)
            self.logger.info(f"Loaded {len(data)} rows")

            # Validate
            validation_results = self.validate(data)
            if not validation_results['valid']:
                self.logger.warning(f"Validation failed: {validation_results['errors']}")

            # Clean
            cleaned_data = self.clean(data)

            # Export
            output_path = self._export_data(cleaned_data, output_format)

            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_path,
                'rows_processed': len(cleaned_data),
                'format': output_format
            }

        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            raise

    def validate(self, data):
        """
        Validate data integrity

        Args:
            data (DataFrame): Data to validate

        Returns:
            dict: Validation results
        """
        errors = []
        warnings = []

        # Check for nulls
        null_counts = data.isnull().sum()
        if null_counts.sum() > 0:
            warnings.append(f"Found {null_counts.sum()} null values")

        # Check data types
        for column in data.columns:
            if data[column].dtype == 'object':
                # Try to detect if should be numeric
                pass

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'rows': len(data),
            'columns': len(data.columns)
        }

    def clean(self, data):
        """
        Clean and normalize data

        Args:
            data (DataFrame): Raw data

        Returns:
            DataFrame: Cleaned data
        """
        cleaned = data.copy()

        # Remove duplicates
        cleaned = cleaned.drop_duplicates()

        # Handle missing values
        for column in cleaned.columns:
            if cleaned[column].dtype == 'numeric':
                cleaned[column] = cleaned[column].fillna(cleaned[column].mean())
            else:
                cleaned[column] = cleaned[column].fillna('Unknown')

        # Trim whitespace
        for column in cleaned.columns:
            if cleaned[column].dtype == 'object':
                cleaned[column] = cleaned[column].str.strip()

        return cleaned

    def detect_anomalies(self, data):
        """Detect anomalies in data"""
        anomalies = []

        for column in data.select_dtypes(include=[np.number]).columns:
            mean = data[column].mean()
            std = data[column].std()

            # Flag values > 3 standard deviations
            outliers = data[np.abs(data[column] - mean) > 3 * std]
            if len(outliers) > 0:
                anomalies.append({
                    'column': column,
                    'count': len(outliers),
                    'rows': outliers.index.tolist()
                })

        return anomalies

    def export(self, data, output_format='csv', filename='output'):
        """Export data in specified format"""
        if output_format == 'csv':
            path = f"{filename}.csv"
            data.to_csv(path, index=False)
        elif output_format == 'excel':
            path = f"{filename}.xlsx"
            data.to_excel(path, index=False)
        elif output_format == 'json':
            path = f"{filename}.json"
            data.to_json(path, orient='records')

        return path

    def run(self, input_data):
        """Main run method"""
        return self.process(input_data['file'], input_data.get('format', 'json'))

    # ====== HELPER METHODS ======

    def _load_data(self, filepath):
        """Load data from file"""
        if filepath.endswith('.csv'):
            return pd.read_csv(filepath)
        elif filepath.endswith('.xlsx'):
            return pd.read_excel(filepath)
        elif filepath.endswith('.json'):
            return pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")

    def _export_data(self, data, format):
        """Export data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"output_{timestamp}"
        return self.export(data, format, filename)

if __name__ == '__main__':
    agent = DataProcessorAgent({})
    result = agent.run({'file': 'data.csv'})
    print(result)
```

---

## ⚙️ **2. config.json - Configuration Settings**

**Purpose**: Non-sensitive configuration values that control agent behavior.

**File**: `agents/sales-analyzer/config.json`

```json
{
  "agent": {
    "name": "Sales Analyzer Agent",
    "version": "1.0.0",
    "description": "Analyzes sales data and generates insights",
    "enabled": true
  },

  "database": {
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "name": "sales_db",
    "timeout": 30000,
    "pool": {
      "min": 2,
      "max": 10
    }
  },

  "analysis": {
    "defaultPeriod": "monthly",
    "forecastMonths": 12,
    "confidenceLevel": 0.85,
    "minDataPoints": 10
  },

  "reporting": {
    "outputDir": "./reports",
    "defaultFormat": "pdf",
    "supportedFormats": ["pdf", "excel", "csv"]
  },

  "logging": {
    "level": "info",
    "file": "./logs/sales-analyzer.log",
    "maxSize": "10m",
    "maxFiles": 7
  },

  "performance": {
    "cacheTTL": 3600,
    "maxConnections": 10,
    "requestTimeout": 30000
  }
}
```

**For Python Agent**

**File**: `agents/data-processor/config.json`

```json
{
  "agent": {
    "name": "Data Processor Agent",
    "version": "1.0.0",
    "description": "Processes and validates data files"
  },

  "processing": {
    "chunkSize": 10000,
    "maxFileSize": "1GB",
    "supportedFormats": ["csv", "json", "xlsx"]
  },

  "validation": {
    "checkDuplicates": true,
    "checkMissing": true,
    "checkOutliers": true,
    "outlierStandardDeviations": 3
  },

  "cleaning": {
    "removeWhitespace": true,
    "removeEmptyRows": true,
    "normalizeDates": true
  },

  "output": {
    "defaultFormat": "csv",
    "outputDir": "./processed",
    "includeMetadata": true
  },

  "logging": {
    "level": "info",
    "file": "./logs/data-processor.log"
  }
}
```

---

## 📖 **3. README.md - Documentation**

**Purpose**: How to use this specific agent (usage guide, examples, troubleshooting).

**File**: `agents/sales-analyzer/README.md`

````markdown
# Sales Analyzer Agent

## Overview

This agent analyzes sales data and generates insights for business decision-making.

**Location**: `agents/sales-analyzer/`
**Language**: Node.js
**Status**: Production Ready
**Version**: 1.0.0

---

## What It Does

✅ Analyzes sales transactions and patterns
✅ Generates trend reports and insights
✅ Forecasts future sales
✅ Exports data in multiple formats
✅ Identifies outliers and anomalies

---

## Quick Start

### Installation

```bash
cd agents/sales-analyzer
npm install
```
````

### Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
DB_URL=mysql://user:password@localhost/sales_db
API_KEY=your_api_key_here
LOG_LEVEL=info
```

### Basic Usage

```javascript
const SalesAnalyzerAgent = require("./");

const agent = new SalesAnalyzerAgent({
  database: process.env.DB_URL,
  apiKey: process.env.API_KEY,
});

// Analyze sales
const analysis = await agent.analyze({
  period: "monthly",
  region: "North America",
});

console.log(analysis);
```

---

## Methods

### analyze(options)

Analyze sales data based on period and optional filters.

**Parameters:**

- `period` (string): 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
- `region` (string, optional): Filter by region
- `startDate` (string, optional): ISO date format
- `endDate` (string, optional): ISO date format

**Returns:** Analysis object with metrics and insights

**Example:**

```javascript
const result = await agent.analyze({
  period: "monthly",
  region: "West Coast",
  startDate: "2024-01-01",
  endDate: "2024-03-31",
});

console.log(result.metrics); // { total, average, min, max, count }
console.log(result.insights); // ['Strong growth', ...]
```

---

### forecast(options)

Generate sales forecast.

**Parameters:**

- `months` (number): Number of months to forecast (1-24)
- `confidence` (number, optional): Confidence level (0-1), default 0.85

**Returns:** Forecast with projected values

**Example:**

```javascript
const forecast = await agent.forecast({
  months: 6,
  confidence: 0.9,
});

console.log(forecast.values); // Forecasted monthly sales
console.log(forecast.confidence);
```

---

### generateReport(options)

Generate detailed report.

**Parameters:**

- `title` (string): Report title
- `period` (string): Analysis period
- `format` (string): 'pdf', 'excel', 'csv'

**Returns:** Report file path

**Example:**

```javascript
const report = await agent.generateReport({
  title: "Q4 2024 Sales Analysis",
  period: "monthly",
  format: "pdf",
});

console.log(report.reportPath); // ./reports/sales-report-20240115.pdf
```

---

### exportData(options)

Export sales data.

**Parameters:**

- `format` (string): 'csv', 'json', 'excel'
- `filename` (string, optional): Output filename

**Returns:** Export file path

**Example:**

```javascript
const exported = await agent.exportData({
  format: "csv",
  filename: "sales-2024",
});
```

---

## Configuration

### Environment Variables (.env)

```
# Database Connection
DB_URL=mysql://user:password@localhost/sales

# API Keys
API_KEY=your_key_here

# Logging
LOG_LEVEL=info

# Paths
OUTPUT_DIR=./reports
LOG_DIR=./logs
```

### config.json

Main configuration file controls:

- Database settings
- Default analysis parameters
- Report output formats
- Logging configuration

See `config.json` for all options.

---

## Examples

### Example 1: Monthly Sales Analysis

```javascript
const agent = new SalesAnalyzerAgent(config);

const result = await agent.analyze({
  period: "monthly",
});

console.log(`Total Sales: $${result.metrics.total}`);
console.log(`Average: $${result.metrics.average}`);
console.log(`Growth: ${result.insights[0]}`);
```

### Example 2: Generate Quarterly Report

```javascript
const report = await agent.generateReport({
  title: "Q4 2024 Sales Summary",
  period: "monthly",
  format: "pdf",
});

console.log(`Report saved to: ${report.reportPath}`);
```

### Example 3: Forecast and Export

```javascript
// Get forecast
const forecast = await agent.forecast({ months: 12 });

// Export analysis
const exported = await agent.exportData({
  format: "excel",
  filename: "sales-forecast-2025",
});

console.log(`Forecast exported to: ${exported.exportPath}`);
```

---

## Testing

Run tests:

```bash
npm test
```

Run with coverage:

```bash
npm run test:coverage
```

---

## Troubleshooting

### "Database connection failed"

**Error**: `Error: connect ECONNREFUSED 127.0.0.1:3306`

**Solution**:

1. Verify MySQL is running
2. Check `DB_URL` in `.env`
3. Verify username/password are correct
4. Check database name exists

### "No data found for period"

**Error**: `Error: No sales data available for this period`

**Solution**:

1. Check date range has data
2. Verify region filter is valid
3. Try expanding date range
4. Check database is populated

### "Report generation timeout"

**Error**: `Error: Report generation timed out`

**Solution**:

1. Reduce time period
2. Increase `timeout` in config.json
3. Check system resources (RAM, CPU)
4. Split large reports into smaller ones

---

## Performance Tips

1. **Use caching** - Results cached for 1 hour by default
2. **Limit time periods** - Smaller periods = faster queries
3. **Index database columns** - Add indexes on `date`, `region`, `customer_id`
4. **Archive old data** - Move 2+ year old data to archive table

---

## API Endpoints (if running as service)

If deployed as a REST service:

```
POST /agents/sales-analyzer/analyze
  Body: { period, region, startDate, endDate }

POST /agents/sales-analyzer/forecast
  Body: { months, confidence }

POST /agents/sales-analyzer/report
  Body: { title, period, format }

POST /agents/sales-analyzer/export
  Body: { format, filename }
```

---

## Related Agents

- `report-generator` - For advanced report formatting
- `data-processor` - For data validation before analysis
- `notification-service` - For sending reports via email

---

## Contributing

To improve this agent:

1. Create a branch: `git checkout -b feature/improvement`
2. Make changes
3. Write tests: `npm test`
4. Submit pull request

---

## Support

- **Issues**: Create issue in repository
- **Questions**: See AGENTS.md in root
- **Contact**: [team-email@company.com]

---

**Last Updated**: January 2025
**Maintained By**: Analytics Team

````

---

## 📄 **4. index.js - Entry Point**

**Purpose**: Entry point that exports your agent so it can be used by other files/apps.

Think of it as the "front door" to your agent.

---

## 🎯 Why You Need index.js

### Without index.js (Bad)
```javascript
// In your app, you'd have to do this:
const SalesAnalyzerAgent = require('./agents/sales-analyzer/agent.js');
const config = require('./agents/sales-analyzer/config.json');

const agent = new SalesAnalyzerAgent(config);
````

**Problems**:

- ❌ Need to know exact file path
- ❌ Need to import config separately
- ❌ Imports are scattered throughout your app
- ❌ Hard to refactor later
- ❌ Not clean

### With index.js (Good)

```javascript
// In your app, you can simply do this:
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");

const agent = new SalesAnalyzerAgent(config);
```

**Benefits**:

- ✅ Clean, simple import
- ✅ Path is shorter
- ✅ Can reorganize files internally without changing imports
- ✅ Exports exactly what users need
- ✅ Professional structure

---

## 📝 Basic index.js Example

**File**: `agents/sales-analyzer/index.js`

```javascript
/**
 * Sales Analyzer Agent - Entry Point
 *
 * This file exports the agent class and helper functions.
 * Users should import from this file, not from agent.js directly.
 */

// Import the agent class
const SalesAnalyzerAgent = require("./agent");

// Import configuration
const config = require("./config.json");

// ====== EXPORT THE AGENT ======

// Option 1: Export just the class
module.exports = SalesAnalyzerAgent;

// Option 2: Export the class and config
module.exports = {
  SalesAnalyzerAgent,
  config,
};

// Option 3: Export a factory function (most flexible)
module.exports = {
  SalesAnalyzerAgent,
  config,
  // Factory function to create agent with default config
  createAgent: (overrideConfig = {}) => {
    const finalConfig = { ...config, ...overrideConfig };
    return new SalesAnalyzerAgent(finalConfig);
  },
};
```

---

## 🚀 Different Patterns

### Pattern 1: Simple Export (Best for Simple Agents)

**File**: `agents/sales-analyzer/index.js`

```javascript
const SalesAnalyzerAgent = require("./agent");

module.exports = SalesAnalyzerAgent;
```

**Usage**:

```javascript
const SalesAnalyzerAgent = require("./agents/sales-analyzer");

const agent = new SalesAnalyzerAgent(config);
await agent.run(input);
```

---

### Pattern 2: Named Exports (Best for Multiple Exports)

**File**: `agents/sales-analyzer/index.js`

```javascript
const SalesAnalyzerAgent = require("./agent");
const config = require("./config.json");
const DatabaseHelper = require("./tools/database");
const ReportGenerator = require("./tools/reporting");

module.exports = {
  SalesAnalyzerAgent,
  config,
  DatabaseHelper,
  ReportGenerator,
  version: "1.0.0",
  description: "Sales analysis agent",
};
```

**Usage**:

```javascript
const {
  SalesAnalyzerAgent,
  config,
  DatabaseHelper,
} = require("./agents/sales-analyzer");

const agent = new SalesAnalyzerAgent(config);
```

---

### Pattern 3: Factory Pattern (Most Flexible)

**File**: `agents/sales-analyzer/index.js`

```javascript
const SalesAnalyzerAgent = require("./agent");
const config = require("./config.json");

/**
 * Create a pre-configured agent instance
 * @param {Object} overrides - Override default config values
 * @returns {SalesAnalyzerAgent} Configured agent instance
 */
function createAgent(overrides = {}) {
  const finalConfig = {
    ...config,
    ...overrides,
  };
  return new SalesAnalyzerAgent(finalConfig);
}

module.exports = {
  SalesAnalyzerAgent,
  config,
  createAgent,
};
```

**Usage**:

```javascript
const { createAgent } = require("./agents/sales-analyzer");

// Create with default config
const agent1 = createAgent();

// Create with custom config
const agent2 = createAgent({
  database: "different-db-url",
  logLevel: "debug",
});

await agent1.run(input);
```

---

## 💡 Real-World Examples

### Example 1: Node.js App Using Agent

**Your App File**: `src/main.js`

```javascript
// Thanks to index.js, this import is clean and simple
const { SalesAnalyzerAgent, createAgent } = require("../agents/sales-analyzer");

async function analyzeMonthlyData() {
  // Create agent with default config
  const agent = createAgent();

  // Run analysis
  const result = await agent.run({
    action: "analyze",
    period: "monthly",
  });

  return result;
}

async function analyzeWithCustomDB() {
  // Create agent with custom database
  const agent = createAgent({
    database: "mysql://prod-server/sales",
  });

  const result = await agent.run({
    action: "analyze",
    period: "quarterly",
  });

  return result;
}

module.exports = { analyzeMonthlyData, analyzeWithCustomDB };
```

---

### Example 2: Test File Using Agent

**Test File**: `agents/sales-analyzer/tests/agent.test.js`

```javascript
// index.js makes importing in tests clean
const { SalesAnalyzerAgent, createAgent } = require("../");

describe("Sales Analyzer Agent", () => {
  let agent;

  beforeEach(() => {
    // Create agent with test config
    agent = createAgent({
      database: "sqlite://test.db",
      logLevel: "error",
    });
  });

  test("should analyze sales data", async () => {
    const result = await agent.analyze({
      period: "monthly",
    });

    expect(result.success).toBe(true);
    expect(result.metrics).toBeDefined();
  });

  test("should forecast sales", async () => {
    const forecast = await agent.forecast({
      months: 6,
    });

    expect(forecast.success).toBe(true);
    expect(forecast.values).toHaveLength(6);
  });
});
```

---

### Example 3: Multiple Agents in One Project

**Root index.js**: `agents/index.js`

```javascript
/**
 * All Agents - Master Export
 *
 * This file exports all agents in the project.
 * Users can import any agent from this single point.
 */

const SalesAnalyzer = require("./sales-analyzer");
const ReportGenerator = require("./report-generator");
const DataProcessor = require("./data-processor");

module.exports = {
  SalesAnalyzer,
  ReportGenerator,
  DataProcessor,

  // Helper to create any agent
  createAgent: (agentName, config = {}) => {
    const agents = {
      "sales-analyzer": SalesAnalyzer,
      "report-generator": ReportGenerator,
      "data-processor": DataProcessor,
    };

    if (!agents[agentName]) {
      throw new Error(`Unknown agent: ${agentName}`);
    }

    return agents[agentName].createAgent(config);
  },
};
```

**Usage**:

```javascript
const { SalesAnalyzer, createAgent } = require("./agents");

// Option 1: Import specific agent
const { createAgent: createSalesAgent } = require("./agents/sales-analyzer");
const agent = createSalesAgent();

// Option 2: Use master createAgent function
const agent = createAgent("sales-analyzer", {
  database: "custom-db",
});
```

---

## 📦 Python Agent Equivalent

For Python agents, the equivalent would be an `__init__.py` file:

**File**: `agents/data-processor/__init__.py`

```python
"""
Data Processor Agent - Entry Point

This module exports the agent class and helper functions.
"""

from .agent import DataProcessorAgent
import json
import os

# Load config
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# ====== EXPORTS ======

def create_agent(overrides=None):
    """
    Create a pre-configured agent instance

    Args:
        overrides (dict): Override config values

    Returns:
        DataProcessorAgent: Configured agent instance
    """
    final_config = config.copy()
    if overrides:
        final_config.update(overrides)
    return DataProcessorAgent(final_config)

# Export publicly available items
__all__ = [
    'DataProcessorAgent',
    'config',
    'create_agent'
]
```

**Usage**:

```python
from agents.data_processor import DataProcessorAgent, create_agent

# Method 1
agent = DataProcessorAgent(config)
result = agent.run(input_data)

# Method 2
agent = create_agent({'log_level': 'debug'})
result = agent.run(input_data)
```

---

## 🎨 Best Practices for index.js

### ✅ DO

1. **Export the main class**

   ```javascript
   module.exports = SalesAnalyzerAgent;
   ```

2. **Export a factory function**

   ```javascript
   module.exports = {
     SalesAnalyzerAgent,
     createAgent: (config) => new SalesAnalyzerAgent(config),
   };
   ```

3. **Export config**

   ```javascript
   module.exports = {
     SalesAnalyzerAgent,
     config,
   };
   ```

4. **Document exports**

   ```javascript
   /**
    * Sales Analyzer Agent
    *
    * @exports SalesAnalyzerAgent
    * @exports config
    * @exports createAgent
    */
   ```

5. **Keep it simple**

   ```javascript
   // Short and clear
   const Agent = require("./agent");
   const config = require("./config.json");

   module.exports = { Agent, config };
   ```

---

### ❌ DON'T

1. **Don't export everything**

   ```javascript
   // BAD: Exports internal helpers
   module.exports = {
     SalesAnalyzerAgent,
     DatabaseHelper, // Internal
     ReportGenerator, // Internal
     Validator, // Internal
     PrivateUtil, // Internal
   };
   ```

2. **Don't create instances**

   ```javascript
   // BAD: Can't configure
   const agent = new SalesAnalyzerAgent(config);
   module.exports = agent; // This is wrong!
   ```

3. **Don't duplicate config loading**

   ```javascript
   // BAD: Loading config twice
   const SalesAnalyzerAgent = require("./agent");
   const config1 = require("./config.json");
   const config2 = require("./config.json"); // Don't do this
   ```

4. **Don't make it too complex**
   ```javascript
   // BAD: Too many helper functions
   module.exports = {
     Agent,
     createFromFile: () => {},
     createFromDB: () => {},
     createFromAPI: () => {},
     createFromEnv: () => {},
     // etc...
   };
   ```

---

## 📋 Complete Agent Folder With index.js

```
agents/sales-analyzer/
├── index.js              ← ENTRY POINT (what users import)
├── agent.js              ← Implementation (internal)
├── config.json           ← Configuration (loaded by index.js)
├── README.md             ← Documentation
├── package.json
├── .env.example
├── tests/
│   └── agent.test.js    ← Imports from index.js
└── tools/                ← Internal helpers
    ├── database.js
    └── reporting.js
```

---

## 🔄 Import Flow

### How Users Import Your Agent

```
User Code (main.js)
    ↓
const { SalesAnalyzerAgent } = require('./agents/sales-analyzer');
    ↓
Looks for index.js in agents/sales-analyzer/
    ↓
index.js loads agent.js and config.json
    ↓
index.js exports SalesAnalyzerAgent
    ↓
User gets clean, configured agent
```

---

## 🎯 Summary

### What index.js Does

| Job                     | Example                                           |
| ----------------------- | ------------------------------------------------- |
| Import agent class      | `const Agent = require('./agent')`                |
| Import config           | `const config = require('./config.json')`         |
| Create factory function | `createAgent = () => new Agent(config)`           |
| Export everything       | `module.exports = { Agent, config, createAgent }` |

### Result

Users can do:

```javascript
// Clean, simple import
const { SalesAnalyzerAgent, createAgent } = require("./agents/sales-analyzer");

// Easy to use
const agent = createAgent({ database: "custom" });
```

Instead of:

```javascript
// Messy imports from multiple files
const SalesAnalyzerAgent = require("./agents/sales-analyzer/agent.js");
const config = require("./agents/sales-analyzer/config.json");
const DatabaseHelper = require("./agents/sales-analyzer/tools/database.js");

const agent = new SalesAnalyzerAgent(config);
```

---

## ✅ Recommended index.js Template

Copy this for every new agent:

```javascript
/**
 * [Agent Name] - Entry Point
 *
 * This file exports the agent class and utilities.
 * Users should import from this file, not from agent.js directly.
 *
 * @example
 * const { AgentClass, createAgent } = require('./agents/[agent-name]');
 * const agent = createAgent();
 */

// Import agent class
const AgentClass = require("./agent");

// Import configuration
const config = require("./config.json");

/**
 * Factory function to create a configured agent instance
 * @param {Object} overrides - Override default config values
 * @returns {AgentClass} Configured agent instance
 */
function createAgent(overrides = {}) {
  const finalConfig = {
    ...config,
    ...overrides,
  };
  return new AgentClass(finalConfig);
}

// ====== EXPORTS ======

module.exports = {
  AgentClass,
  config,
  createAgent,
  // Optional: Add version/metadata
  version: config.agent?.version || "1.0.0",
  name: config.agent?.name || "[Agent Name]",
};

// Alternative: Just export the class
// module.exports = AgentClass;
```

---

**index.js is the "public interface" of your agent folder. Keep it clean!** 🚀

---

## 🎯 **Summary: What Goes Where**

### **agent.js** (The Code)

- Main agent class
- All methods (analyze, forecast, report, etc.)
- Business logic
- Helper functions
- Error handling

### **config.json** (Settings)

- Database configuration
- Default parameters
- Output directories
- Logging levels
- Performance tuning
- Feature flags

### **README.md** (Documentation)

- Overview of what agent does
- Installation instructions
- Configuration setup
- Method documentation with examples
- Troubleshooting guide
- Performance tips
- Related agents

---

## 📂 **Complete Example Structure**

```

agents/sales-analyzer/
├── agent.js ← IMPLEMENTATION (logic)
├── config.json ← CONFIGURATION (settings)
├── README.md ← DOCUMENTATION (how-to)
├── package.json ← Dependencies
├── .env.example ← Environment template
├── index.js ← Exports
├── tests/
│ └── agent.test.js
└── tools/
├── database.js ← Helpers
├── reporting.js
└── validation.js

```

---

## ✅ **Checklist per Agent Folder**

- [ ] `agent.js` - Main implementation with all methods
- [ ] `config.json` - All configuration options
- [ ] `README.md` - Complete usage guide
- [ ] `package.json` - All dependencies listed
- [ ] `.env.example` - Environment variables template
- [ ] `index.js` - Proper exports
- [ ] `tests/` folder with tests
- [ ] `tools/` folder with helpers (if needed)
- [ ] Clear comments in code
- [ ] Examples in README

---

# 📁 tests/ and tools/ Folders - Complete Guide

**Purpose**:

- `tests/` - Verify your agent works correctly
- `tools/` - Helper utilities that the agent uses

---

## 🧪 TESTS/ FOLDER

### What Goes Here

Test files that verify your agent works correctly.

```
agents/sales-analyzer/
├── tests/
│   ├── agent.test.js          ← Main agent tests
│   ├── integration.test.js     ← Tests with real database
│   ├── unit.test.js            ← Tests for specific methods
│   └── fixtures/               ← Test data
│       ├── sample-data.json
│       └── mock-responses.json
```

---

### Example 1: agent.test.js (Jest)

**File**: `agents/sales-analyzer/tests/agent.test.js`

```javascript
/**
 * Sales Analyzer Agent Tests
 *
 * Tests the main functionality of the agent
 */

// Import from index.js (thanks to index.js, this is clean!)
const { SalesAnalyzerAgent, createAgent, config } = require("../");

describe("Sales Analyzer Agent", () => {
  let agent;

  // Setup before each test
  beforeEach(() => {
    // Create agent with test config
    agent = createAgent({
      database: "sqlite://test.db",
      logLevel: "error",
      cacheEnabled: false, // Disable cache for tests
    });
  });

  // Cleanup after each test
  afterEach(async () => {
    // Close connections, clean up
    await agent.close?.();
  });

  // ====== CONSTRUCTOR TESTS ======

  describe("constructor", () => {
    test("should create agent with config", () => {
      expect(agent).toBeDefined();
      expect(agent.name).toBe("Sales Analyzer Agent");
      expect(agent.tools).toContain("analyze");
    });

    test("should merge config overrides", () => {
      const customAgent = createAgent({
        logLevel: "debug",
      });
      expect(customAgent.config.logLevel).toBe("debug");
    });

    test("should have all required tools", () => {
      const requiredTools = [
        "analyze",
        "forecast",
        "generateReport",
        "exportData",
      ];
      requiredTools.forEach((tool) => {
        expect(agent.tools).toContain(tool);
      });
    });
  });

  // ====== ANALYZE METHOD TESTS ======

  describe("analyze()", () => {
    test("should analyze sales data for monthly period", async () => {
      const result = await agent.analyze({
        period: "monthly",
      });

      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.metrics).toBeDefined();
      expect(result.metrics.total).toBeGreaterThanOrEqual(0);
    });

    test("should include metrics object", async () => {
      const result = await agent.analyze({
        period: "monthly",
      });

      const metrics = result.metrics;
      expect(metrics).toHaveProperty("total");
      expect(metrics).toHaveProperty("average");
      expect(metrics).toHaveProperty("count");
      expect(metrics).toHaveProperty("min");
      expect(metrics).toHaveProperty("max");
    });

    test("should filter by region when provided", async () => {
      const result = await agent.analyze({
        period: "monthly",
        region: "North America",
      });

      expect(result.success).toBe(true);
      // In a real test, you'd verify region filtering worked
    });

    test("should throw error for invalid period", async () => {
      await expect(agent.analyze({ period: "invalid" })).rejects.toThrow(
        "Invalid period",
      );
    });

    test("should support date range filtering", async () => {
      const result = await agent.analyze({
        period: "monthly",
        startDate: "2024-01-01",
        endDate: "2024-03-31",
      });

      expect(result.success).toBe(true);
    });

    test("should handle empty results gracefully", async () => {
      // Empty database should not crash
      const result = await agent.analyze({
        period: "monthly",
        startDate: "2000-01-01",
        endDate: "2000-01-02",
      });

      expect(result.success).toBe(true);
      expect(result.metrics.count).toBe(0);
    });
  });

  // ====== FORECAST METHOD TESTS ======

  describe("forecast()", () => {
    test("should generate forecast for specified months", async () => {
      const result = await agent.forecast({
        months: 6,
      });

      expect(result.success).toBe(true);
      expect(result.forecast).toBeDefined();
      expect(result.forecast).toHaveLength(6);
    });

    test("should include confidence level", async () => {
      const result = await agent.forecast({
        months: 12,
        confidence: 0.95,
      });

      expect(result.confidence).toBe(0.95);
    });

    test("should validate month range", async () => {
      // Too many months
      await expect(agent.forecast({ months: 100 })).rejects.toThrow();

      // Zero months
      await expect(agent.forecast({ months: 0 })).rejects.toThrow();
    });

    test("should return numeric forecast values", async () => {
      const result = await agent.forecast({ months: 3 });

      result.forecast.forEach((value) => {
        expect(typeof value).toBe("number");
        expect(value).toBeGreaterThanOrEqual(0);
      });
    });
  });

  // ====== GENERATE REPORT METHOD TESTS ======

  describe("generateReport()", () => {
    test("should generate PDF report", async () => {
      const result = await agent.generateReport({
        title: "Test Report",
        period: "monthly",
        format: "pdf",
      });

      expect(result.success).toBe(true);
      expect(result.reportPath).toBeDefined();
      expect(result.reportPath).toMatch(/\.pdf$/);
    });

    test("should support Excel format", async () => {
      const result = await agent.generateReport({
        title: "Test Report",
        format: "excel",
      });

      expect(result.reportPath).toMatch(/\.xlsx$/);
    });

    test("should support CSV format", async () => {
      const result = await agent.generateReport({
        title: "Test Report",
        format: "csv",
      });

      expect(result.reportPath).toMatch(/\.csv$/);
    });

    test("should reject unsupported format", async () => {
      await expect(
        agent.generateReport({
          title: "Test",
          format: "unknown",
        }),
      ).rejects.toThrow("Unsupported format");
    });

    test("should use default period if not specified", async () => {
      const result = await agent.generateReport({
        title: "Test",
        format: "pdf",
      });

      expect(result.success).toBe(true);
    });
  });

  // ====== EXPORT DATA METHOD TESTS ======

  describe("exportData()", () => {
    test("should export as CSV", async () => {
      const result = await agent.exportData({
        format: "csv",
      });

      expect(result.success).toBe(true);
      expect(result.exportPath).toMatch(/\.csv$/);
    });

    test("should export as JSON", async () => {
      const result = await agent.exportData({
        format: "json",
      });

      expect(result.exportPath).toMatch(/\.json$/);
    });

    test("should use provided filename", async () => {
      const result = await agent.exportData({
        format: "csv",
        filename: "custom-export",
      });

      expect(result.exportPath).toContain("custom-export");
    });

    test("should include row count in result", async () => {
      const result = await agent.exportData({
        format: "json",
      });

      expect(result.rows).toBeGreaterThanOrEqual(0);
    });
  });

  // ====== RUN METHOD TESTS ======

  describe("run()", () => {
    test("should route to analyze action", async () => {
      const result = await agent.run({
        action: "analyze",
        period: "monthly",
      });

      expect(result.success).toBe(true);
      expect(result.metrics).toBeDefined();
    });

    test("should route to forecast action", async () => {
      const result = await agent.run({
        action: "forecast",
        months: 6,
      });

      expect(result.success).toBe(true);
      expect(result.forecast).toBeDefined();
    });

    test("should route to report action", async () => {
      const result = await agent.run({
        action: "report",
        title: "Test",
        format: "pdf",
      });

      expect(result.success).toBe(true);
    });

    test("should throw error for unknown action", async () => {
      await expect(agent.run({ action: "unknown" })).rejects.toThrow(
        "Unknown action",
      );
    });
  });

  // ====== ERROR HANDLING TESTS ======

  describe("error handling", () => {
    test("should handle database connection errors", async () => {
      const badAgent = createAgent({
        database: "mysql://invalid-host/nonexistent",
      });

      await expect(badAgent.analyze({ period: "monthly" })).rejects.toThrow();
    });

    test("should handle missing required parameters", async () => {
      await expect(
        agent.analyze({
          /* missing period */
        }),
      ).rejects.toThrow();
    });

    test("should log errors appropriately", async () => {
      const consoleSpy = jest.spyOn(console, "error");

      try {
        await agent.analyze({ period: "invalid" });
      } catch (e) {
        // Expected
      }

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  // ====== PERFORMANCE TESTS ======

  describe("performance", () => {
    test("should analyze data quickly", async () => {
      const start = Date.now();
      await agent.analyze({ period: "monthly" });
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(1000); // Less than 1 second
    });

    test("should handle multiple concurrent requests", async () => {
      const promises = [
        agent.analyze({ period: "monthly" }),
        agent.analyze({ period: "weekly" }),
        agent.forecast({ months: 6 }),
      ];

      const results = await Promise.all(promises);
      expect(results).toHaveLength(3);
      results.forEach((result) => {
        expect(result.success).toBe(true);
      });
    });
  });
});
```

---

### Example 2: integration.test.js

**File**: `agents/sales-analyzer/tests/integration.test.js`

```javascript
/**
 * Integration Tests
 *
 * Tests the agent with real database connections
 * (runs against test database, not production)
 */

const { createAgent } = require("../");
const mysql = require("mysql2/promise");

describe("Sales Analyzer - Integration Tests", () => {
  let agent;
  let connection;

  beforeAll(async () => {
    // Setup test database
    connection = await mysql.createConnection({
      host: process.env.TEST_DB_HOST || "localhost",
      user: process.env.TEST_DB_USER || "test_user",
      password: process.env.TEST_DB_PASSWORD || "test_pass",
      database: "sales_test",
    });

    // Create test data
    await setupTestData(connection);
  });

  beforeEach(() => {
    agent = createAgent({
      database:
        process.env.TEST_DB_URL ||
        "mysql://test_user:test_pass@localhost/sales_test",
    });
  });

  afterAll(async () => {
    // Cleanup test database
    await cleanupTestData(connection);
    await connection.end();
  });

  test("should query real database and return results", async () => {
    const result = await agent.analyze({
      period: "monthly",
    });

    expect(result.success).toBe(true);
    expect(result.metrics.count).toBeGreaterThan(0);
  });

  test("should handle complex queries with multiple filters", async () => {
    const result = await agent.analyze({
      period: "monthly",
      region: "East Coast",
      startDate: "2024-01-01",
      endDate: "2024-03-31",
    });

    expect(result.success).toBe(true);
  });

  test("should calculate accurate metrics from real data", async () => {
    const result = await agent.analyze({
      period: "monthly",
    });

    // Verify calculations are correct
    const expectedTotal = 0; // Calculate from test data
    expect(result.metrics.total).toBe(expectedTotal);
  });

  test("should handle large datasets", async () => {
    // Load 10,000 test records
    await connection.query(
      "INSERT INTO sales SELECT ... FROM large_dataset LIMIT 10000",
    );

    const result = await agent.analyze({
      period: "monthly",
    });

    expect(result.success).toBe(true);
    expect(result.metrics.count).toBe(10000);
  });
});

// Test helper functions
async function setupTestData(connection) {
  await connection.query(`
    CREATE TABLE IF NOT EXISTS sales (
      id INT PRIMARY KEY,
      amount DECIMAL(10,2),
      date DATE,
      region VARCHAR(100)
    )
  `);

  // Insert test data
  await connection.query(`
    INSERT INTO sales VALUES
    (1, 100.00, '2024-01-01', 'East Coast'),
    (2, 200.00, '2024-01-02', 'West Coast'),
    (3, 300.00, '2024-02-01', 'East Coast')
  `);
}

async function cleanupTestData(connection) {
  await connection.query("DROP TABLE IF EXISTS sales");
}
```

---

## 🛠️ TOOLS/ FOLDER

### What Goes Here

Helper utility modules that the agent uses internally.

```
agents/sales-analyzer/
└── tools/
    ├── database.js          ← Database helper class
    ├── reporting.js         ← Report generation utilities
    ├── validation.js        ← Input validation
    ├── cache.js             ← Caching utilities (optional)
    └── logger.js            ← Logging utilities (optional)
```

---

### Example 1: tools/database.js

**File**: `agents/sales-analyzer/tools/database.js`

```javascript
/**
 * Database Helper
 *
 * Handles all database operations for the agent
 */

const mysql = require("mysql2/promise");

class DatabaseHelper {
  constructor(config) {
    this.config = config;
    this.pool = null;
    this.initialized = false;
  }

  /**
   * Initialize database connection
   */
  async initialize() {
    if (this.initialized) return;

    try {
      console.log("[DatabaseHelper] Initializing connection...");

      this.pool = await mysql.createPool({
        host: this.config.host || "localhost",
        user: this.config.user || "root",
        password: this.config.password || "",
        database: this.config.database || "sales",
        waitForConnections: true,
        connectionLimit: this.config.connectionLimit || 10,
        queueLimit: 0,
      });

      this.initialized = true;
      console.log("[DatabaseHelper] Connection initialized");
    } catch (error) {
      console.error("[DatabaseHelper] Initialization failed:", error);
      throw error;
    }
  }

  /**
   * Query sales data
   */
  async querySales(options = {}) {
    await this.initialize();

    const { period, region, startDate, endDate } = options;

    // Build dynamic query
    let query = "SELECT * FROM sales WHERE 1=1";
    const params = [];

    // Add period-based date filter
    if (period) {
      const dateRange = this.getDateRange(period);
      query += " AND date >= ? AND date <= ?";
      params.push(dateRange.start, dateRange.end);
    }

    // Add custom date range
    if (startDate) {
      query += " AND date >= ?";
      params.push(startDate);
    }
    if (endDate) {
      query += " AND date <= ?";
      params.push(endDate);
    }

    // Add region filter
    if (region) {
      query += " AND region = ?";
      params.push(region);
    }

    // Execute query
    try {
      const connection = await this.pool.getConnection();
      const [rows] = await connection.execute(query, params);
      connection.release();

      console.log(`[DatabaseHelper] Retrieved ${rows.length} rows`);
      return rows;
    } catch (error) {
      console.error("[DatabaseHelper] Query failed:", error);
      throw error;
    }
  }

  /**
   * Get historical data for forecasting
   */
  async getHistoricalData(months = 12) {
    await this.initialize();

    const query = `
      SELECT SUM(amount) as total, DATE_TRUNC(date, MONTH) as month
      FROM sales
      WHERE date >= DATE_SUB(NOW(), INTERVAL ? MONTH)
      GROUP BY DATE_TRUNC(date, MONTH)
      ORDER BY month DESC
    `;

    try {
      const connection = await this.pool.getConnection();
      const [rows] = await connection.execute(query, [months]);
      connection.release();

      return rows.map((row) => row.total);
    } catch (error) {
      console.error("[DatabaseHelper] Historical query failed:", error);
      throw error;
    }
  }

  /**
   * Helper: Get date range for period
   */
  getDateRange(period) {
    const today = new Date();
    let start,
      end = today;

    switch (period) {
      case "daily":
        start = new Date(today);
        start.setDate(start.getDate() - 1);
        break;
      case "weekly":
        start = new Date(today);
        start.setDate(start.getDate() - 7);
        break;
      case "monthly":
        start = new Date(today);
        start.setMonth(start.getMonth() - 1);
        break;
      case "quarterly":
        start = new Date(today);
        start.setMonth(start.getMonth() - 3);
        break;
      case "yearly":
        start = new Date(today);
        start.setFullYear(start.getFullYear() - 1);
        break;
      default:
        throw new Error(`Invalid period: ${period}`);
    }

    return { start, end };
  }

  /**
   * Close database connection
   */
  async close() {
    if (this.pool) {
      await this.pool.end();
      this.initialized = false;
      console.log("[DatabaseHelper] Connection closed");
    }
  }
}

module.exports = DatabaseHelper;
```

---

### Example 2: tools/reporting.js

**File**: `agents/sales-analyzer/tools/reporting.js`

```javascript
/**
 * Report Generator Utility
 *
 * Generates reports in various formats
 */

const PDFDocument = require("pdfkit");
const ExcelJS = require("exceljs");
const fs = require("fs");
const path = require("path");

class ReportGenerator {
  constructor(config = {}) {
    this.outputDir = config.outputDir || "./reports";
    this.ensureOutputDir();
  }

  ensureOutputDir() {
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  /**
   * Generate report in specified format
   */
  async generate(options) {
    const { title, data, format } = options;

    console.log(`[ReportGenerator] Generating ${format} report...`);

    try {
      switch (format) {
        case "pdf":
          return await this.generatePDF(title, data);
        case "excel":
          return await this.generateExcel(title, data);
        case "csv":
          return await this.generateCSV(title, data);
        default:
          throw new Error(`Unsupported format: ${format}`);
      }
    } catch (error) {
      console.error("[ReportGenerator] Generation failed:", error);
      throw error;
    }
  }

  /**
   * Generate PDF report
   */
  async generatePDF(title, data) {
    const filename = `${title.replace(/\s+/g, "-")}-${Date.now()}.pdf`;
    const filepath = path.join(this.outputDir, filename);

    return new Promise((resolve, reject) => {
      try {
        const doc = new PDFDocument();
        const stream = fs.createWriteStream(filepath);

        doc.pipe(stream);

        // Title
        doc.fontSize(20).text(title, { align: "center" });
        doc.moveDown();

        // Metrics
        doc.fontSize(12).text("Metrics:", { underline: true });
        Object.entries(data.metrics).forEach(([key, value]) => {
          doc.text(`  ${key}: ${value}`);
        });

        // Insights
        doc.moveDown();
        doc.fontSize(12).text("Insights:", { underline: true });
        data.insights.forEach((insight) => {
          doc.text(`  • ${insight}`);
        });

        doc.end();

        stream.on("finish", () => {
          console.log(`[ReportGenerator] PDF saved to ${filepath}`);
          resolve(filepath);
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Generate Excel report
   */
  async generateExcel(title, data) {
    const filename = `${title.replace(/\s+/g, "-")}-${Date.now()}.xlsx`;
    const filepath = path.join(this.outputDir, filename);

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet("Report");

    // Header
    worksheet.columns = [
      { header: "Metric", key: "metric", width: 20 },
      { header: "Value", key: "value", width: 20 },
    ];

    // Add metrics
    Object.entries(data.metrics).forEach(([key, value]) => {
      worksheet.addRow({ metric: key, value });
    });

    // Save
    await workbook.xlsx.writeFile(filepath);
    console.log(`[ReportGenerator] Excel saved to ${filepath}`);

    return filepath;
  }

  /**
   * Generate CSV report
   */
  async generateCSV(title, data) {
    const filename = `${title.replace(/\s+/g, "-")}-${Date.now()}.csv`;
    const filepath = path.join(this.outputDir, filename);

    const csv = [
      ["Metric", "Value"],
      ...Object.entries(data.metrics).map(([k, v]) => [k, v]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    fs.writeFileSync(filepath, csv);
    console.log(`[ReportGenerator] CSV saved to ${filepath}`);

    return filepath;
  }

  /**
   * Export data
   */
  async export(data, options = {}) {
    const { format, filename } = options;
    // Similar logic to generate()
    return await this.generate({
      title: filename || "export",
      data,
      format,
    });
  }
}

module.exports = ReportGenerator;
```

---

### Example 3: tools/validation.js

**File**: `agents/sales-analyzer/tools/validation.js`

```javascript
/**
 * Input Validation Utility
 *
 * Validates inputs to agent methods
 */

class Validator {
  /**
   * Validate analysis options
   */
  validateAnalysisOptions(options = {}) {
    if (!options.period) {
      throw new Error("period is required");
    }

    const validPeriods = ["daily", "weekly", "monthly", "quarterly", "yearly"];
    if (!validPeriods.includes(options.period)) {
      throw new Error(
        `Invalid period: ${options.period}. Must be one of: ${validPeriods.join(", ")}`,
      );
    }

    if (options.startDate && !this.isValidDate(options.startDate)) {
      throw new Error(`Invalid startDate format: ${options.startDate}`);
    }

    if (options.endDate && !this.isValidDate(options.endDate)) {
      throw new Error(`Invalid endDate format: ${options.endDate}`);
    }

    if (options.region && typeof options.region !== "string") {
      throw new Error("region must be a string");
    }
  }

  /**
   * Validate forecast options
   */
  validateForecastOptions(options = {}) {
    if (!options.months) {
      throw new Error("months is required");
    }

    if (
      typeof options.months !== "number" ||
      options.months < 1 ||
      options.months > 24
    ) {
      throw new Error("months must be a number between 1 and 24");
    }

    if (options.confidence) {
      if (
        typeof options.confidence !== "number" ||
        options.confidence < 0 ||
        options.confidence > 1
      ) {
        throw new Error("confidence must be a number between 0 and 1");
      }
    }
  }

  /**
   * Validate report options
   */
  validateReportOptions(options = {}) {
    if (!options.title || typeof options.title !== "string") {
      throw new Error("title is required and must be a string");
    }

    const validFormats = ["pdf", "excel", "csv"];
    if (options.format && !validFormats.includes(options.format)) {
      throw new Error(`format must be one of: ${validFormats.join(", ")}`);
    }
  }

  /**
   * Helper: Check if date is valid ISO format
   */
  isValidDate(dateString) {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateString)) return false;

    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
  }
}

module.exports = Validator;
```

---

## 📊 How They Work Together

```
agent.js (Main logic)
    ↓
    ├→ imports from tools/database.js
    │  └→ Queries database
    │
    ├→ imports from tools/reporting.js
    │  └→ Generates reports
    │
    └→ imports from tools/validation.js
       └→ Validates inputs

tests/agent.test.js (Testing)
    ↓
    ├→ imports from index.js
    │  └→ Creates agent instances
    │
    └→ Calls agent methods
       └→ Verifies results
```

---

## 🎯 Complete Folder Structure

```
agents/sales-analyzer/
├── agent.js                  ← Main agent class
├── config.json              ← Configuration
├── README.md                ← Documentation
├── index.js                 ← Entry point
├── package.json             ← Dependencies
├── .env.example             ← Secrets template
│
├── tests/                   ← TEST FILES
│   ├── agent.test.js       ← Unit/integration tests
│   ├── integration.test.js ← Real database tests
│   ├── unit.test.js        ← Specific method tests
│   └── fixtures/           ← Test data
│       └── sample-data.json
│
└── tools/                   ← HELPER UTILITIES
    ├── database.js         ← Database operations
    ├── reporting.js        ← Report generation
    ├── validation.js       ← Input validation
    ├── cache.js            ← Caching logic (optional)
    └── logger.js           ← Logging utilities (optional)
```

---

## ✅ When to Use tests/ and tools/

### ✅ Use tests/ When

- Writing unit tests for methods
- Testing edge cases
- Integration testing with real database
- Performance testing
- Error handling tests

### ✅ Use tools/ When

- Database operations need a helper class
- Report generation is complex
- Input validation is needed
- Caching logic is needed
- Logging is centralized
- Any utility the agent uses repeatedly

### ❌ DON'T Use tools/ For

- Code that belongs in agent.js main class
- One-time use functions
- Simple inline code

---

## 🚀 Running Tests

```bash
# Install test framework
npm install --save-dev jest

# Run all tests
npm test

# Run specific test file
npm test tests/agent.test.js

# Run with coverage report
npm test -- --coverage

# Run in watch mode (reruns on file change)
npm test -- --watch
```

---

## 📋 package.json Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:integration": "jest tests/integration.test.js",
    "test:unit": "jest tests/agent.test.js"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

---

## 💡 Summary

| Folder     | Purpose            | Contains   | Example Files                            |
| ---------- | ------------------ | ---------- | ---------------------------------------- |
| **tests/** | Verify agent works | Test files | agent.test.js, integration.test.js       |
| **tools/** | Help agent work    | Utilities  | database.js, reporting.js, validation.js |

**Result**:

- ✅ Code is well-tested
- ✅ Code is modular and maintainable
- ✅ Logic is separated by concern
- ✅ Easy to debug and extend

---

**Tests verify correctness. Tools prevent errors. Together they make your agent solid!** 🚀

---

**Each agent is completely self-contained and can be understood by reading those three files!** 🚀

### Option 3: Monorepo Style

```

your-app-repo/
├── packages/
│ ├── agents/
│ │ ├── sales-analyzer/
│ │ ├── report-generator/
│ │ └── package.json
│ ├── web/
│ ├── api/
│ └── shared/
└── package.json (root)

```

---

## Best Practice Recommendation

Use Option 1 (top-level agents/) because:

- Clear separation of concerns
- Easy to find and manage agents
- Each agent is self-contained
- Easy to version control
- Follows common patterns

---

## Structure for a Single Agent

```

agents/sales-analyzer/
├── agent.js (Main agent file)
├── package.json (Dependencies)
├── config.json (Configuration)
├── .env.example (Environment variables template)
├── README.md (Documentation)
├── index.js (Entry point/exports)
├── tests/
│ ├── agent.test.js
│ └── integration.test.js
└── tools/
├── database.js
├── reporting.js
└── caching.js

```

---

## Example: Custom JavaScript Agent

### agents/sales-analyzer/agent.js

```javascript
class SalesAnalyzerAgent {
  constructor(config) {
    this.config = config;
    this.name = "Sales Analyzer Agent";
    this.tools = ["queryDatabase", "generateReport", "sendNotification"];
  }

  async analyze(query) {
    console.log(`[${this.name}] Analyzing: ${query}`);
    // Agent logic here
  }

  async run(input) {
    return await this.analyze(input);
  }
}

module.exports = SalesAnalyzerAgent;
```

### agents/sales-analyzer/package.json

```json
{
  "name": "sales-analyzer-agent",
  "version": "1.0.0",
  "description": "Custom agent for analyzing sales data",
  "main": "index.js",
  "scripts": {
    "test": "jest",
    "start": "node index.js"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "dotenv": "^16.0.0"
  }
}
```

### agents/sales-analyzer/index.js

```javascript
const SalesAnalyzerAgent = require("./agent");

module.exports = {
  SalesAnalyzerAgent,
  createAgent: (config) => new SalesAnalyzerAgent(config),
};
```

---

## Example: Custom Python Agent

### agents/data-processor/agent.py

```python
class DataProcessorAgent:
    def __init__(self, config):
        self.config = config
        self.name = "Data Processor Agent"
        self.tools = [
            "process_csv",
            "validate_data",
            "export_results"
        ]

    def process(self, data):
        print(f"[{self.name}] Processing data...")
        # Agent logic here
        return processed_data

    def run(self, input_data):
        return self.process(input_data)

if __name__ == "__main__":
    agent = DataProcessorAgent({})
    result = agent.run("input.csv")
```

### agents/data-processor/requirements.txt

```
pandas==2.0.0
numpy==1.24.0
python-dotenv==1.0.0
requests==2.31.0
```

---

## Usage in Your App

### Node.js

```javascript
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");

const agent = new SalesAnalyzerAgent({
  database: process.env.DB_URL,
  apiKey: process.env.API_KEY,
});

agent.run("Analyze Q4 sales").then((result) => {
  console.log(result);
});
```

### Python

```python
from agents.data_processor.agent import DataProcessorAgent

agent = DataProcessorAgent(config={
    "database": os.getenv("DB_URL"),
    "api_key": os.getenv("API_KEY")
})

result = agent.run("input.csv")
```

---

## .gitignore for Agents

```
# Agent-specific ignores
agents/**/node_modules/
agents/**/.env
agents/**/.env.local
agents/**/dist/
agents/**/__pycache__/
agents/**/*.pyc
agents/**/.venv/
agents/**/venv/
agents/**/*.log
```

---

## Git Structure

```
# Initialize agents with version control
git add agents/
git commit -m "feat: Add custom sales-analyzer agent

- Standalone sub-agent for sales analysis
- Self-contained with own dependencies
- Includes tests and documentation"

git push
```

---

## Complete Directory Setup

```bash
# Create agents directory structure
mkdir -p agents/agent-name/{tests,tools}
cd agents/agent-name
touch agent.js package.json config.json .env.example README.md index.js

# For Python
touch agent.py requirements.txt

# For TypeScript
touch agent.ts tsconfig.json
```

---

## Checklist for Custom Agent

- [ ] Agent code in agents/[name]/agent.js|.py|.ts
- [ ] Dependencies in package.json or requirements.txt
- [ ] Configuration in config.json
- [ ] Environment template in .env.example
- [ ] Documentation in README.md
- [ ] Entry point in index.js (for Node.js)
- [ ] Tests in tests/ subdirectory
- [ ] Added to .gitignore (ignore node_modules, venv, .env)
- [ ] Committed to git with clear message
- [ ] Documented in main repo README

---

# AGENTS.md Documentation Strategy

Use a two-level AGENTS.md structure:

```
your-app-repo/
├── AGENTS.md                  ← Project-level directory of all agents
├── agents/
│   ├── AGENTS.md             ← Index of agents in this folder
│   ├── sales-analyzer/
│   │   ├── AGENT.md          ← Individual agent spec (optional)
│   │   ├── agent.js
│   │   ├── package.json
│   │   └── README.md
│   ├── report-generator/
│   └── data-processor/
├── src/
├── skills/
└── package.json
```

## Root AGENTS.md (Project Overview)

````markdown
# Project Agents Directory

This document lists all custom sub-agents available in this project.

## Overview

This project contains **[N]** custom sub-agents for handling specialized tasks.

## Agents Summary

| Agent            | Location                 | Purpose                        | Status            |
| ---------------- | ------------------------ | ------------------------------ | ----------------- |
| Sales Analyzer   | agents/sales-analyzer/   | Analyzes sales data and trends | ✅ Active         |
| Report Generator | agents/report-generator/ | Generates PDF/Excel reports    | ✅ Active         |
| Data Processor   | agents/data-processor/   | Processes and validates data   | 🔧 In Development |

## Quick Access

### Sales Analyzer

- Location: agents/sales-analyzer/
- Purpose: Analyzes sales data, trends, forecasting
- Language: JavaScript (Node.js)
- Dependencies: See agents/sales-analyzer/package.json
- Usage: See agents/sales-analyzer/AGENT.md

### Report Generator

- Location: agents/report-generator/
- Purpose: Generates reports in PDF, Excel, CSV formats
- Language: JavaScript (Node.js)

### Data Processor

- Location: agents/data-processor/
- Purpose: Validates, cleans, and processes data files
- Language: Python
- Status: In development

## Running Agents

### From Node.js Code

```javascript
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");
const agent = new SalesAnalyzerAgent(config);
await agent.run(input);
```
````

### From Python Code

```python
from agents.data_processor import DataProcessorAgent
agent = DataProcessorAgent(config)
result = agent.run(input_data)
```

### Standalone

```bash
cd agents/sales-analyzer
npm start

# Or for Python
python agent.py
```

## Adding New Agents

1. Create directory: agents/[agent-name]/
2. Create AGENT.md in the agent directory
3. Update this AGENTS.md file with new agent summary
4. Commit to git

See agents/AGENTS.md for detailed agent specifications.

````

## agents/AGENTS.md (Detailed Index)

```markdown
# Agents - Detailed Specifications

## 1. Sales Analyzer Agent

Location: agents/sales-analyzer/

### Purpose
Analyzes sales transactions, generates insights, forecasts trends.

### Technical Details
- Language: JavaScript (Node.js)
- Entry Point: agents/sales-analyzer/agent.js
- Config File: agents/sales-analyzer/config.json
- Main Class: SalesAnalyzerAgent

### Installation
```bash
cd agents/sales-analyzer
npm install
````

### Usage

```javascript
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");

const agent = new SalesAnalyzerAgent({
  database: process.env.DB_URL,
  apiKey: process.env.API_KEY,
});

const result = await agent.run({
  query: "Analyze Q4 2024 sales",
  format: "json",
});

console.log(result);
```

### Tools/Methods Available

- analyze(query)
- forecast(period)
- generateReport(options)
- exportData(format)

````

## Individual AGENT.md (Optional)

```markdown
# Sales Analyzer Agent

## Quick Reference

Agent ID: sales-analyzer
Type: Data Analysis
Language: Node.js
Status: Production
Version: 1.2.0

## Overview

Sales Analyzer Agent processes sales transactions and generates insights for business decision-making.

## How to Use

```javascript
const agent = new SalesAnalyzerAgent(config);
const result = await agent.analyze("Q4 sales trends");
````

```

---

## Parent & Sub-Agent Architecture

### Overview

The Parent & Sub-Agent Architecture provides a sophisticated orchestration framework for complex multi-agent systems. This pattern enables a "Conductor Agent" to coordinate multiple specialized "Sub-Agents" in sequential, parallel, or conditional execution flows.

**Key Benefits:**
- **Modular Complexity**: Break down complex tasks into specialized sub-agents
- **Execution Control**: Sequential, parallel, and conditional execution modes
- **Error Handling**: Centralized error management and recovery
- **Scalability**: Easy addition of new sub-agents without modifying existing code
- **Reusability**: Sub-agents can be reused across different parent agents

### Core Components

#### 1. Conductor Agent (Parent)

The Conductor Agent orchestrates the execution of sub-agents according to predefined workflows.

```javascript
// agents/conductor-agent/index.js
const { BaseAgent } = require('../base-agent');
const { PlanningAgent } = require('../planning-agent');
const { DataProcessingAgent } = require('../data-processing-agent');
const { ReportingAgent } = require('../reporting-agent');

class ConductorAgent extends BaseAgent {
  constructor(config) {
    super(config);
    this.subAgents = {
      planning: new PlanningAgent(config),
      data: new DataProcessingAgent(config),
      reporting: new ReportingAgent(config)
    };
  }

  async execute(task) {
    const workflow = this.determineWorkflow(task.type);
    return await this.runWorkflow(workflow, task);
  }

  determineWorkflow(taskType) {
    const workflows = {
      'analysis': ['planning', 'data', 'reporting'],
      'report': ['planning', 'reporting'],
      'data-sync': ['data']
    };
    return workflows[taskType] || ['planning', 'data', 'reporting'];
  }

  async runWorkflow(workflow, task) {
    const results = {};
    const context = { task, results };

    for (const agentName of workflow) {
      try {
        this.logger.info(`Executing sub-agent: ${agentName}`);
        const subAgent = this.subAgents[agentName];
        results[agentName] = await subAgent.execute(context);
        context.results = results;
      } catch (error) {
        this.logger.error(`Sub-agent ${agentName} failed:`, error);
        await this.handleSubAgentFailure(agentName, error, context);
      }
    }

    return this.aggregateResults(results);
  }

  async handleSubAgentFailure(agentName, error, context) {
    // Implement retry logic, fallback agents, or error recovery
    if (this.config.retryOnFailure) {
      this.logger.info(`Retrying sub-agent: ${agentName}`);
      // Retry logic here
    }
    throw error; // Re-throw if recovery fails
  }

  aggregateResults(results) {
    return {
      success: true,
      timestamp: new Date().toISOString(),
      results: results,
      summary: this.generateSummary(results)
    };
  }

  generateSummary(results) {
    // Generate consolidated summary from all sub-agent results
    return {
      totalSteps: Object.keys(results).length,
      completedSteps: Object.keys(results).filter(k => results[k].success).length,
      executionTime: this.calculateTotalExecutionTime(results)
    };
  }
}

module.exports = { ConductorAgent };
```

#### 2. Planning Agent (Sub-Agent)

Specialized in task planning, requirements analysis, and execution strategy.

```javascript
// agents/planning-agent/index.js
const { BaseAgent } = require('../base-agent');

class PlanningAgent extends BaseAgent {
  async execute(context) {
    const { task } = context;

    // Analyze task requirements
    const requirements = await this.analyzeRequirements(task);

    // Generate execution plan
    const plan = await this.generatePlan(requirements);

    // Validate plan feasibility
    const validation = await this.validatePlan(plan);

    return {
      success: validation.isValid,
      requirements,
      plan,
      validation,
      estimatedDuration: this.estimateDuration(plan)
    };
  }

  async analyzeRequirements(task) {
    return {
      dataSources: this.identifyDataSources(task),
      processingSteps: this.determineProcessingSteps(task),
      outputFormats: this.specifyOutputFormats(task),
      constraints: this.identifyConstraints(task)
    };
  }

  async generatePlan(requirements) {
    return {
      phases: [
        { name: 'data-collection', duration: 5, dependencies: [] },
        { name: 'data-processing', duration: 15, dependencies: ['data-collection'] },
        { name: 'analysis', duration: 10, dependencies: ['data-processing'] },
        { name: 'reporting', duration: 5, dependencies: ['analysis'] }
      ],
      resources: this.allocateResources(requirements),
      timeline: this.createTimeline(requirements)
    };
  }

  async validatePlan(plan) {
    const issues = [];

    // Check resource availability
    if (!await this.checkResourceAvailability(plan.resources)) {
      issues.push('Insufficient resources allocated');
    }

    // Check timeline feasibility
    if (!this.validateTimeline(plan.timeline)) {
      issues.push('Timeline conflicts detected');
    }

    return {
      isValid: issues.length === 0,
      issues
    };
  }
}

module.exports = { PlanningAgent };
```

#### 3. Data Processing Agent (Sub-Agent)

Handles data collection, transformation, and processing operations.

```javascript
// agents/data-processing-agent/index.js
const { BaseAgent } = require('../base-agent');

class DataProcessingAgent extends BaseAgent {
  async execute(context) {
    const { task, results } = context;
    const plan = results.planning?.plan;

    // Execute data processing pipeline
    const rawData = await this.collectData(task, plan);
    const processedData = await this.processData(rawData, plan);
    const validatedData = await this.validateData(processedData);

    return {
      success: validatedData.isValid,
      rawData: this.summarizeData(rawData),
      processedData: this.summarizeData(processedData),
      validation: validatedData,
      metrics: this.calculateMetrics(processedData)
    };
  }

  async collectData(task, plan) {
    const collectors = {
      'database': () => this.collectFromDatabase(task.query),
      'api': () => this.collectFromAPI(task.endpoint),
      'files': () => this.collectFromFiles(task.filePaths)
    };

    const collector = collectors[task.dataSource];
    if (!collector) {
      throw new Error(`Unsupported data source: ${task.dataSource}`);
    }

    return await collector();
  }

  async processData(rawData, plan) {
    const processors = plan.processingSteps || ['clean', 'transform', 'aggregate'];

    let processed = rawData;
    for (const step of processors) {
      processed = await this.applyProcessingStep(processed, step);
    }

    return processed;
  }

  async validateData(data) {
    const validations = [
      this.validateDataTypes(data),
      this.validateDataCompleteness(data),
      this.validateBusinessRules(data)
    ];

    const results = await Promise.all(validations);
    const issues = results.flatMap(r => r.issues || []);

    return {
      isValid: issues.length === 0,
      issues,
      qualityScore: this.calculateQualityScore(data, issues)
    };
  }

  calculateMetrics(data) {
    return {
      recordCount: data.length,
      fieldCount: Object.keys(data[0] || {}).length,
      processingTime: Date.now() - this.startTime,
      memoryUsage: process.memoryUsage().heapUsed
    };
  }
}

module.exports = { DataProcessingAgent };
```

#### 4. Reporting Agent (Sub-Agent)

Generates reports, visualizations, and formatted outputs.

```javascript
// agents/reporting-agent/index.js
const { BaseAgent } = require('../base-agent');

class ReportingAgent extends BaseAgent {
  async execute(context) {
    const { task, results } = context;
    const processedData = results.data?.processedData;

    // Generate requested report formats
    const reports = await this.generateReports(processedData, task.reportFormats);

    // Apply formatting and styling
    const formattedReports = await this.formatReports(reports, task.formatting);

    // Generate visualizations if requested
    const visualizations = task.includeCharts ?
      await this.generateVisualizations(processedData) : [];

    return {
      success: true,
      reports: formattedReports,
      visualizations,
      metadata: this.generateReportMetadata(task, results)
    };
  }

  async generateReports(data, formats) {
    const generators = {
      'pdf': () => this.generatePDFReport(data),
      'excel': () => this.generateExcelReport(data),
      'json': () => this.generateJSONReport(data),
      'html': () => this.generateHTMLReport(data)
    };

    const reports = {};
    for (const format of formats) {
      const generator = generators[format];
      if (generator) {
        reports[format] = await generator();
      }
    }

    return reports;
  }

  async formatReports(reports, formatting) {
    const formatted = {};

    for (const [format, report] of Object.entries(reports)) {
      formatted[format] = await this.applyFormatting(report, formatting);
    }

    return formatted;
  }

  async generateVisualizations(data) {
    const charts = [];

    // Generate charts based on data analysis
    if (this.hasTimeSeriesData(data)) {
      charts.push(await this.generateTimeSeriesChart(data));
    }

    if (this.hasCategoricalData(data)) {
      charts.push(await this.generateBarChart(data));
    }

    if (this.hasGeographicData(data)) {
      charts.push(await this.generateMapVisualization(data));
    }

    return charts;
  }

  generateReportMetadata(task, results) {
    return {
      reportId: this.generateReportId(),
      generatedAt: new Date().toISOString(),
      task: task.name,
      executionTime: this.calculateExecutionTime(results),
      dataQuality: results.data?.validation?.qualityScore,
      version: this.config.version
    };
  }
}

module.exports = { ReportingAgent };
```

### Execution Patterns

#### Sequential Execution

Sub-agents execute one after another, with each receiving context from previous agents.

```javascript
// Sequential workflow in ConductorAgent
async runSequentialWorkflow(workflow, task) {
  const results = {};
  let context = { task };

  for (const agentName of workflow) {
    const subAgent = this.subAgents[agentName];
    const result = await subAgent.execute(context);

    results[agentName] = result;
    context = { ...context, results, [agentName]: result };
  }

  return results;
}
```

#### Parallel Execution

Multiple sub-agents execute simultaneously for performance optimization.

```javascript
// Parallel workflow in ConductorAgent
async runParallelWorkflow(workflow, task) {
  const context = { task };
  const promises = workflow.map(agentName => {
    const subAgent = this.subAgents[agentName];
    return subAgent.execute(context).then(result => ({ agentName, result }));
  });

  const results = await Promise.all(promises);
  return results.reduce((acc, { agentName, result }) => {
    acc[agentName] = result;
    return acc;
  }, {});
}
```

#### Conditional Execution

Sub-agents execute based on conditions or previous results.

```javascript
// Conditional workflow in ConductorAgent
async runConditionalWorkflow(workflow, task) {
  const results = {};
  const context = { task };

  for (const step of workflow) {
    const { agent: agentName, condition } = step;

    // Evaluate condition
    if (condition && !await this.evaluateCondition(condition, context)) {
      this.logger.info(`Skipping ${agentName} due to condition: ${condition}`);
      continue;
    }

    // Execute agent
    const subAgent = this.subAgents[agentName];
    const result = await subAgent.execute(context);

    results[agentName] = result;
    context.results = results;
  }

  return results;
}

async evaluateCondition(condition, context) {
  // Simple condition evaluation
  const { field, operator, value } = condition;

  switch (operator) {
    case 'equals':
      return context.results?.[field] === value;
    case 'exists':
      return context.results?.[field] !== undefined;
    case 'greaterThan':
      return context.results?.[field] > value;
    default:
      return true;
  }
}
```

### Configuration and Setup

#### Workflow Configuration

```javascript
// config/workflows.js
module.exports = {
  analysis: {
    type: 'sequential',
    agents: ['planning', 'data', 'reporting'],
    timeout: 300000, // 5 minutes
    retryPolicy: {
      maxRetries: 3,
      backoffMs: 1000
    }
  },

  quickReport: {
    type: 'parallel',
    agents: ['data', 'reporting'],
    timeout: 120000, // 2 minutes
    skipPlanning: true
  },

  conditionalAnalysis: {
    type: 'conditional',
    steps: [
      { agent: 'planning', condition: null },
      { agent: 'data', condition: { field: 'planning', operator: 'exists' } },
      { agent: 'reporting', condition: { field: 'data', operator: 'equals', value: 'success' } }
    ]
  }
};
```

#### Agent Configuration

```javascript
// config/agents.js
module.exports = {
  conductor: {
    class: 'ConductorAgent',
    config: {
      retryOnFailure: true,
      maxConcurrency: 3,
      timeoutMs: 300000
    }
  },

  planning: {
    class: 'PlanningAgent',
    config: {
      maxPlanningDepth: 5,
      resourceOptimization: true
    }
  },

  data: {
    class: 'DataProcessingAgent',
    config: {
      batchSize: 1000,
      validationLevel: 'strict',
      cachingEnabled: true
    }
  },

  reporting: {
    class: 'ReportingAgent',
    config: {
      defaultFormats: ['pdf', 'json'],
      chartLibrary: 'chartjs',
      templateEngine: 'handlebars'
    }
  }
};
```

### Error Handling and Recovery

#### Centralized Error Management

```javascript
// agents/conductor-agent/error-handler.js
class ErrorHandler {
  constructor(config) {
    this.config = config;
    this.recoveryStrategies = {
      retry: this.retryStrategy.bind(this),
      fallback: this.fallbackStrategy.bind(this),
      skip: this.skipStrategy.bind(this)
    };
  }

  async handleError(agentName, error, context) {
    const strategy = this.determineStrategy(error, context);

    this.logger.error(`Error in ${agentName}:`, error);

    try {
      return await this.recoveryStrategies[strategy](agentName, error, context);
    } catch (recoveryError) {
      this.logger.error(`Recovery failed for ${agentName}:`, recoveryError);
      throw recoveryError;
    }
  }

  determineStrategy(error, context) {
    if (error.code === 'TIMEOUT') return 'retry';
    if (error.code === 'VALIDATION_FAILED') return 'fallback';
    if (error.code === 'RESOURCE_UNAVAILABLE') return 'skip';
    return 'retry'; // default
  }

  async retryStrategy(agentName, error, context) {
    const maxRetries = this.config.retryPolicy?.maxRetries || 3;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        this.logger.info(`Retry attempt ${attempt} for ${agentName}`);
        const subAgent = context.conductor.subAgents[agentName];
        return await subAgent.execute(context);
      } catch (retryError) {
        if (attempt === maxRetries) throw retryError;
        await this.delay(this.config.retryPolicy?.backoffMs || 1000 * attempt);
      }
    }
  }

  async fallbackStrategy(agentName, error, context) {
    const fallbackAgent = this.findFallbackAgent(agentName);
    if (fallbackAgent) {
      this.logger.info(`Using fallback agent: ${fallbackAgent}`);
      const subAgent = context.conductor.subAgents[fallbackAgent];
      return await subAgent.execute(context);
    }
    throw error;
  }

  async skipStrategy(agentName, error, context) {
    this.logger.warn(`Skipping ${agentName} due to error: ${error.message}`);
    return { success: false, skipped: true, error: error.message };
  }

  findFallbackAgent(agentName) {
    const fallbacks = {
      'data': 'reporting', // Use reporting as fallback for data processing
      'reporting': 'data'  // Use data processing as fallback for reporting
    };
    return fallbacks[agentName];
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### Monitoring and Observability

#### Execution Tracking

```javascript
// agents/conductor-agent/monitor.js
class ExecutionMonitor {
  constructor() {
    this.metrics = {
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      averageExecutionTime: 0,
      agentMetrics: {}
    };
  }

  startExecution(workflowId, task) {
    const execution = {
      id: this.generateExecutionId(),
      workflowId,
      task,
      startTime: Date.now(),
      status: 'running',
      agentResults: {}
    };

    this.activeExecutions.set(execution.id, execution);
    return execution.id;
  }

  recordAgentResult(executionId, agentName, result) {
    const execution = this.activeExecutions.get(executionId);
    if (execution) {
      execution.agentResults[agentName] = {
        result,
        timestamp: Date.now(),
        duration: Date.now() - execution.startTime
      };
    }
  }

  completeExecution(executionId, finalResult) {
    const execution = this.activeExecutions.get(executionId);
    if (execution) {
      execution.endTime = Date.now();
      execution.duration = execution.endTime - execution.startTime;
      execution.status = finalResult.success ? 'completed' : 'failed';
      execution.finalResult = finalResult;

      this.updateMetrics(execution);
      this.persistExecution(execution);
      this.activeExecutions.delete(executionId);
    }
  }

  updateMetrics(execution) {
    this.metrics.totalExecutions++;
    if (execution.status === 'completed') {
      this.metrics.successfulExecutions++;
    } else {
      this.metrics.failedExecutions++;
    }

    // Update average execution time
    const totalTime = this.metrics.averageExecutionTime * (this.metrics.totalExecutions - 1);
    this.metrics.averageExecutionTime = (totalTime + execution.duration) / this.metrics.totalExecutions;

    // Update agent-specific metrics
    Object.keys(execution.agentResults).forEach(agentName => {
      if (!this.metrics.agentMetrics[agentName]) {
        this.metrics.agentMetrics[agentName] = { executions: 0, failures: 0, avgTime: 0 };
      }

      const agentMetric = this.metrics.agentMetrics[agentName];
      agentMetric.executions++;
      if (!execution.agentResults[agentName].result.success) {
        agentMetric.failures++;
      }

      const agentTime = execution.agentResults[agentName].duration;
      agentMetric.avgTime = (agentMetric.avgTime * (agentMetric.executions - 1) + agentTime) / agentMetric.executions;
    });
  }

  getMetrics() {
    return { ...this.metrics };
  }

  getExecutionHistory(limit = 100) {
    return Array.from(this.executionHistory.values()).slice(-limit);
  }
}
```

### Usage Examples

#### Basic Sequential Workflow

```javascript
// Example: Complete data analysis workflow
const conductor = new ConductorAgent(config);

const result = await conductor.execute({
  type: 'analysis',
  name: 'Q4 Sales Analysis',
  dataSource: 'database',
  query: 'SELECT * FROM sales WHERE quarter = 4',
  reportFormats: ['pdf', 'excel']
});

console.log('Analysis completed:', result.summary);
```

#### Parallel Processing

```javascript
// Example: Multiple independent reports
const conductor = new ConductorAgent(config);

const result = await conductor.execute({
  type: 'parallel-reports',
  reports: [
    { name: 'Sales Report', data: salesData },
    { name: 'Inventory Report', data: inventoryData },
    { name: 'Financial Report', data: financialData }
  ]
});
```

#### Conditional Execution

```javascript
// Example: Conditional data processing
const conductor = new ConductorAgent(config);

const result = await conductor.execute({
  type: 'conditional-analysis',
  conditions: {
    'high-priority': salesData.urgent,
    'data-quality-check': true
  },
  fallback: {
    'data-processing-failed': 'basic-report'
  }
});
```

### Best Practices

#### Agent Design Principles

1. **Single Responsibility**: Each sub-agent should have one clear purpose
2. **Loose Coupling**: Sub-agents should communicate through well-defined interfaces
3. **Error Isolation**: Failures in one sub-agent shouldn't cascade to others
4. **Configurable Behavior**: Allow customization through configuration
5. **Observable Operations**: Provide hooks for monitoring and debugging

#### Workflow Design

1. **Clear Dependencies**: Define explicit dependencies between sub-agents
2. **Resource Management**: Consider resource constraints in parallel execution
3. **Timeout Handling**: Set appropriate timeouts for long-running operations
4. **Graceful Degradation**: Design workflows that can continue with partial failures

#### Error Handling

1. **Retry Logic**: Implement exponential backoff for transient failures
2. **Fallback Strategies**: Provide alternative execution paths
3. **Circuit Breakers**: Prevent cascading failures
4. **Logging**: Comprehensive logging for debugging and monitoring

#### Performance Optimization

1. **Caching**: Cache expensive operations and intermediate results
2. **Parallelization**: Identify opportunities for parallel execution
3. **Resource Pooling**: Reuse connections and resources
4. **Lazy Loading**: Load components only when needed

### Testing Strategies

#### Unit Testing Sub-Agents

```javascript
// tests/agents/planning-agent.test.js
const { PlanningAgent } = require('../../agents/planning-agent');

describe('PlanningAgent', () => {
  let agent;

  beforeEach(() => {
    agent = new PlanningAgent({ /* config */ });
  });

  test('analyzes requirements correctly', async () => {
    const task = { type: 'analysis', complexity: 'high' };
    const requirements = await agent.analyzeRequirements(task);

    expect(requirements).toHaveProperty('dataSources');
    expect(requirements).toHaveProperty('processingSteps');
  });

  test('generates valid execution plan', async () => {
    const requirements = { /* mock requirements */ };
    const plan = await agent.generatePlan(requirements);

    expect(plan.phases).toBeDefined();
    expect(plan.phases.length).toBeGreaterThan(0);
  });
});
```

#### Integration Testing Workflows

```javascript
// tests/workflows/analysis-workflow.test.js
const { ConductorAgent } = require('../../agents/conductor-agent');

describe('Analysis Workflow', () => {
  let conductor;

  beforeEach(() => {
    conductor = new ConductorAgent({ /* config */ });
  });

  test('executes complete analysis workflow', async () => {
    const task = {
      type: 'analysis',
      name: 'Test Analysis',
      dataSource: 'mock'
    };

    const result = await conductor.execute(task);

    expect(result.success).toBe(true);
    expect(result.results).toHaveProperty('planning');
    expect(result.results).toHaveProperty('data');
    expect(result.results).toHaveProperty('reporting');
  });

  test('handles sub-agent failures gracefully', async () => {
    // Mock a sub-agent to fail
    const failingTask = { /* task that causes failure */ };

    const result = await conductor.execute(failingTask);

    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });
});
```

#### Performance Testing

```javascript
// tests/performance/workflow-performance.test.js
describe('Workflow Performance', () => {
  test('completes analysis within time limit', async () => {
    const startTime = Date.now();

    const result = await conductor.execute(largeAnalysisTask);

    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(300000); // 5 minutes
  });

  test('handles concurrent workflows efficiently', async () => {
    const promises = Array(5).fill().map(() =>
      conductor.execute(analysisTask)
    );

    const startTime = Date.now();
    const results = await Promise.all(promises);
    const duration = Date.now() - startTime;

    expect(results.every(r => r.success)).toBe(true);
    expect(duration).toBeLessThan(600000); // 10 minutes for 5 concurrent
  });
});
```

### Deployment and Scaling

#### Container Configuration

```dockerfile
# Dockerfile for Conductor Agent
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY agents/ ./agents/
COPY config/ ./config/

EXPOSE 3000

CMD ["node", "agents/conductor-agent/index.js"]
```

#### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: conductor-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: conductor-agent
  template:
    metadata:
      labels:
        app: conductor-agent
    spec:
      containers:
      - name: conductor
        image: conductor-agent:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### Horizontal Scaling Considerations

1. **Stateless Design**: Ensure agents are stateless for easy scaling
2. **Shared Storage**: Use shared storage for intermediate results
3. **Load Balancing**: Distribute workflows across multiple instances
4. **Monitoring**: Implement comprehensive monitoring and alerting
5. **Auto-scaling**: Configure auto-scaling based on queue depth

### Security Considerations

#### Access Control

```javascript
// agents/conductor-agent/security.js
class SecurityManager {
  constructor(config) {
    this.config = config;
    this.permissions = config.permissions || {};
  }

  async authorizeExecution(user, workflow) {
    // Check user permissions for workflow execution
    const userPermissions = await this.getUserPermissions(user);

    for (const agentName of workflow.agents) {
      if (!userPermissions.includes(`agent:${agentName}:execute`)) {
        throw new Error(`User ${user.id} not authorized to execute ${agentName}`);
      }
    }

    return true;
  }

  async validateDataAccess(user, task) {
    // Validate data access permissions
    const dataPermissions = await this.getDataPermissions(user);

    if (task.dataSource === 'database') {
      if (!dataPermissions.includes(`database:${task.database}:read`)) {
        throw new Error(`User ${user.id} not authorized to access ${task.database}`);
      }
    }

    return true;
  }

  async auditExecution(executionId, user, result) {
    // Log execution for audit purposes
    await this.auditLogger.log({
      executionId,
      userId: user.id,
      timestamp: new Date(),
      result: result.success,
      agents: Object.keys(result.results || {})
    });
  }
}
```

#### Data Protection

1. **Encryption**: Encrypt sensitive data in transit and at rest
2. **Input Validation**: Validate all inputs to prevent injection attacks
3. **Output Sanitization**: Sanitize outputs to prevent data leakage
4. **Access Logging**: Log all data access for audit purposes

### Future Enhancements

#### Advanced Features

1. **Dynamic Workflows**: AI-driven workflow optimization
2. **Machine Learning Integration**: Predictive analytics for workflow optimization
3. **Event-Driven Execution**: React to external events and triggers
4. **Multi-Cloud Deployment**: Deploy across multiple cloud providers
5. **Advanced Monitoring**: Real-time performance dashboards and alerting

#### Research Areas

1. **Self-Optimizing Workflows**: Workflows that learn and optimize themselves
2. **Agent Marketplace**: Marketplace for sharing and discovering agents
3. **Federated Execution**: Execute workflows across distributed agent networks
4. **Quantum Computing Integration**: Leverage quantum computing for complex optimizations

---

## Summary

- Default folder: no enforced default
- Recommended: top-level agents/
- Use AGENTS.md for discovery and indexing
- Keep each agent self-contained
```
