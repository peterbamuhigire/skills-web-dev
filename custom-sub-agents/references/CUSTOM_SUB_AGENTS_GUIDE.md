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

```

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

````

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
````

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

## Summary

- Default folder: no enforced default
- Recommended: top-level agents/
- Use AGENTS.md for discovery and indexing
- Keep each agent self-contained
```
