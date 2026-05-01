# ⚙️ Agent Configuration & Documentation

## 📝 **2. config.json - Configuration Settings**

**Purpose**: Stores non-sensitive configuration settings that control agent behavior.

### What Goes Here

- Database connection settings (without passwords)
- API endpoints and timeouts
- Default parameters and thresholds
- Feature flags and options
- Logging and output preferences

### Example Structure

**File**: `agents/sales-analyzer/config.json`

```json
{
  "name": "Sales Analyzer Agent",
  "version": "1.2.0",
  "description": "Analyzes sales data and generates business insights",

  "database": {
    "host": "localhost",
    "port": 3306,
    "database": "sales_db",
    "charset": "utf8mb4",
    "poolSize": 10,
    "acquireTimeoutMillis": 60000,
    "timeout": 60000
  },

  "analysis": {
    "defaultPeriod": "last_30_days",
    "maxRecords": 100000,
    "cacheEnabled": true,
    "cacheTTL": 3600,
    "parallelProcessing": true,
    "batchSize": 1000
  },

  "forecasting": {
    "defaultMethod": "linear",
    "maxForecastMonths": 12,
    "confidenceThreshold": 0.75,
    "seasonalAdjustment": true
  },

  "reporting": {
    "defaultFormat": "pdf",
    "includeCharts": true,
    "chartLibrary": "chartjs",
    "maxReportSize": "10MB",
    "compressionEnabled": true
  },

  "export": {
    "supportedFormats": ["csv", "json", "xml", "excel"],
    "defaultFormat": "csv",
    "maxFileSize": "50MB",
    "includeMetadata": true
  },

  "logging": {
    "level": "info",
    "format": "json",
    "maxFileSize": "10MB",
    "maxFiles": 5,
    "logToConsole": true,
    "logToFile": true
  },

  "performance": {
    "memoryLimit": "512MB",
    "cpuLimit": "80%",
    "timeout": 300000,
    "retryAttempts": 3,
    "retryDelay": 1000
  },

  "features": {
    "realTimeAnalysis": false,
    "predictiveInsights": true,
    "anomalyDetection": true,
    "trendAnalysis": true,
    "benchmarking": false
  }
}
```

### Configuration Best Practices

#### Environment-Specific Configs

```json
{
  "development": {
    "database": {
      "host": "localhost",
      "debug": true
    },
    "logging": {
      "level": "debug"
    }
  },
  "production": {
    "database": {
      "host": "prod-db.cluster.com",
      "debug": false
    },
    "logging": {
      "level": "warn"
    }
  }
}
```

#### Validation Rules

```json
{
  "validation": {
    "database": {
      "host": { "type": "string", "required": true },
      "port": { "type": "number", "min": 1, "max": 65535 },
      "poolSize": { "type": "number", "min": 1, "max": 100 }
    },
    "analysis": {
      "maxRecords": { "type": "number", "min": 1, "max": 1000000 }
    }
  }
}
```

---

## 📖 **3. README.md - Documentation**

**Purpose**: Complete documentation for how to use, configure, and understand the agent.

### Standard README Structure

**File**: `agents/sales-analyzer/README.md`

````markdown
# Sales Analyzer Agent

## Overview

Sales Analyzer Agent processes sales transactions and generates insights for business decision-making.

## What It Does

- Analyzes sales data across different time periods
- Generates performance insights and trends
- Creates sales forecasts using various methods
- Produces comprehensive reports in multiple formats
- Exports data in various formats for external analysis

## Quick Start

### Installation

```bash
# Clone the agent
git clone <repository-url>
cd agents/sales-analyzer

# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env
# Edit .env with your database credentials
```
````

### Configuration

Edit `config.json` to match your environment:

```json
{
  "database": {
    "host": "your-db-host",
    "database": "your-database-name"
  }
}
```

Create a `.env` file with sensitive information:

```env
DB_PASSWORD=your-secure-password
API_KEY=your-api-key
```

### Basic Usage

```javascript
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");

const agent = new SalesAnalyzerAgent();

// Analyze last month's sales
const result = await agent.analyze({
  startDate: "2024-01-01",
  endDate: "2024-01-31",
  groupBy: "week",
});

console.log(result.insights);
```

## Methods

### analyze(options)

Analyzes sales data for a given period.

**Parameters:**

- `startDate` (string): Start date in YYYY-MM-DD format
- `endDate` (string): End date in YYYY-MM-DD format
- `groupBy` (string): Grouping period ('day', 'week', 'month')

**Returns:** Analysis results with data and insights

**Example:**

```javascript
const result = await agent.analyze({
  startDate: "2024-01-01",
  endDate: "2024-01-31",
  groupBy: "month",
});
```

### forecast(options)

Forecasts future sales based on historical data.

**Parameters:**

- `months` (number): Number of months to forecast (default: 3)
- `method` (string): Forecast method ('linear', 'exponential')

**Returns:** Forecast data with confidence intervals

**Example:**

```javascript
const forecast = await agent.forecast({
  months: 6,
  method: "linear",
});
```

### generateReport(options)

Generates a comprehensive sales report.

**Parameters:**

- `format` (string): Report format ('pdf', 'excel', 'json')
- `includeCharts` (boolean): Include charts in report

**Returns:** Generated report file/buffer

**Example:**

```javascript
const report = await agent.generateReport({
  format: "pdf",
  includeCharts: true,
});
```

### exportData(options)

Exports sales data in various formats.

**Parameters:**

- `format` (string): Export format ('csv', 'json', 'xml')
- `startDate` (string): Start date for data export
- `endDate` (string): End date for data export

**Returns:** Exported data in requested format

**Example:**

```javascript
const data = await agent.exportData({
  format: "csv",
  startDate: "2024-01-01",
  endDate: "2024-01-31",
});
```

## Configuration

### Environment Variables (.env)

Create a `.env` file in the agent directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sales_db
DB_USER=app_user
DB_PASSWORD=secure_password

# API Keys
ANALYTICS_API_KEY=your_analytics_key
REPORTING_API_KEY=your_reporting_key

# Feature Flags
ENABLE_REAL_TIME_ANALYSIS=false
ENABLE_PREDICTIVE_INSIGHTS=true
```

### config.json

Main configuration file with non-sensitive settings:

```json
{
  "database": {
    "poolSize": 10,
    "acquireTimeoutMillis": 60000
  },
  "analysis": {
    "maxRecords": 100000,
    "cacheEnabled": true
  }
}
```

## Examples

### Example 1: Monthly Sales Analysis

```javascript
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");

async function analyzeMonthlySales() {
  const agent = new SalesAnalyzerAgent();

  const result = await agent.analyze({
    startDate: "2024-01-01",
    endDate: "2024-01-31",
    groupBy: "week",
  });

  console.log("Analysis Results:");
  console.log("Total Sales:", result.data.total);
  console.log("Insights:", result.insights);

  return result;
}
```

### Example 2: Generate Quarterly Report

```javascript
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");

async function generateQuarterlyReport() {
  const agent = new SalesAnalyzerAgent();

  const report = await agent.generateReport({
    format: "pdf",
    includeCharts: true,
    title: "Q1 2024 Sales Report",
  });

  // Save report to file
  await fs.writeFile("q1-report.pdf", report.buffer);

  console.log("Report generated successfully");
}
```

### Example 3: Forecast and Export

```javascript
const { SalesAnalyzerAgent } = require("./agents/sales-analyzer");

async function forecastAndExport() {
  const agent = new SalesAnalyzerAgent();

  // Generate forecast
  const forecast = await agent.forecast({
    months: 6,
    method: "linear",
  });

  // Export forecast data
  const exported = await agent.exportData({
    format: "json",
    data: forecast.data,
  });

  console.log("Forecast exported:", exported);
}
```

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- tests/agent.test.js

# Run with coverage
npm run test:coverage
```

### Test Structure

```
tests/
├── agent.test.js          # Main agent functionality tests
├── integration.test.js    # Integration tests
├── fixtures/              # Test data fixtures
│   ├── sample-sales.json
│   └── mock-responses.json
└── helpers/               # Test helper functions
    └── test-utils.js
```

## Troubleshooting

### "Database connection failed"

**Problem:** Agent cannot connect to the database.

**Solutions:**

1. Check database credentials in `.env` file
2. Verify database server is running
3. Check network connectivity
4. Ensure correct database name and host

**Example error:**

```
Error: connect ECONNREFUSED 127.0.0.1:3306
```

**Fix:**

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database
```

### "No data found for period"

**Problem:** Analysis returns empty results.

**Solutions:**

1. Verify date range is correct
2. Check if data exists in database
3. Ensure proper date format (YYYY-MM-DD)
4. Check database table names and column names

**Debug:**

```javascript
// Add logging to see what dates are being used
console.log("Searching for data between:", startDate, "and", endDate);
```

### "Report generation timeout"

**Problem:** Report generation takes too long and times out.

**Solutions:**

1. Reduce data range
2. Disable charts for large datasets
3. Increase timeout in config
4. Process data in smaller batches

**Config fix:**

```json
{
  "performance": {
    "timeout": 600000
  },
  "reporting": {
    "includeCharts": false
  }
}
```

## Performance Tips

### Optimizing Analysis Performance

1. **Enable Caching**: Cache frequently accessed data
2. **Use Indexes**: Ensure database has proper indexes
3. **Batch Processing**: Process large datasets in batches
4. **Parallel Processing**: Enable parallel processing for multiple operations

### Memory Optimization

1. **Stream Processing**: Process large files as streams
2. **Garbage Collection**: Force GC after large operations
3. **Memory Limits**: Set appropriate memory limits

### Database Optimization

1. **Connection Pooling**: Use connection pools for better performance
2. **Query Optimization**: Use efficient queries with proper WHERE clauses
3. **Result Limiting**: Limit results for large datasets

## API Endpoints (if running as service)

If the agent runs as a web service, it exposes these endpoints:

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.2.0",
  "uptime": "2d 4h 30m"
}
```

### POST /analyze

Analyze sales data.

**Request:**

```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-01-31",
  "groupBy": "month"
}
```

**Response:**

```json
{
  "success": true,
  "data": {...},
  "insights": [...]
}
```

### POST /forecast

Generate sales forecast.

**Request:**

```json
{
  "months": 6,
  "method": "linear"
}
```

**Response:**

```json
{
  "success": true,
  "forecast": [...],
  "confidence": 0.85
}
```

## Related Agents

- **Data Processor Agent**: Pre-processes raw sales data
- **Reporting Agent**: Creates advanced visualizations
- **Alert Agent**: Monitors sales KPIs and sends alerts

## Contributing

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-org/sales-analyzer.git
cd sales-analyzer

# Install dependencies
npm install

# Set up development database
npm run setup:dev

# Run tests
npm test
```

### Code Style

- Use ESLint configuration
- Follow JavaScript Standard Style
- Add JSDoc comments for all public methods
- Write tests for new features

### Pull Request Process

1. Create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

## Support

### Getting Help

- **Documentation**: Check this README first
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

### Common Issues

**Q: Agent runs slow on large datasets**
A: Enable parallel processing and increase batch size in config.json

**Q: Memory errors during analysis**
A: Reduce maxRecords in config or enable streaming processing

**Q: Database connection drops**
A: Increase connection pool size and timeouts

### Version History

- **v1.2.0** (2024-01-15): Added forecasting capabilities
- **v1.1.0** (2024-01-01): Improved performance and caching
- **v1.0.0** (2023-12-01): Initial release
  </content>
  <parameter name="filePath">c:\wamp64\www\birdc_erp\skills\custom-sub-agents\references\02-agent-config-documentation.md
