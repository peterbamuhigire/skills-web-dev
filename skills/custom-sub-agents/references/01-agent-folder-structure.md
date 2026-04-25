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

const { DatabaseTool } = require("./tools/database");
const { ReportingTool } = require("./tools/reporting");

class SalesAnalyzerAgent {
  constructor(config) {
    this.config = config;
    this.database = new DatabaseTool(config.database);
    this.reporting = new ReportingTool(config.reporting);
  }

  /**
   * Analyze sales data for a given period
   * @param {Object} options - Analysis options
   * @param {string} options.startDate - Start date (YYYY-MM-DD)
   * @param {string} options.endDate - End date (YYYY-MM-DD)
   * @param {string} options.groupBy - Group by ('day', 'week', 'month')
   * @returns {Promise<Object>} Analysis results
   */
  async analyze({ startDate, endDate, groupBy = "month" }) {
    try {
      // Get raw sales data
      const salesData = await this.database.getSalesData(startDate, endDate);

      // Process the data
      const processed = this.processSalesData(salesData, groupBy);

      // Generate insights
      const insights = this.generateInsights(processed);

      return {
        success: true,
        data: processed,
        insights,
        metadata: {
          period: { startDate, endDate },
          groupBy,
          recordCount: salesData.length,
          generatedAt: new Date().toISOString(),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        metadata: {
          period: { startDate, endDate },
          generatedAt: new Date().toISOString(),
        },
      };
    }
  }

  /**
   * Forecast future sales based on historical data
   * @param {Object} options - Forecast options
   * @param {number} options.months - Number of months to forecast
   * @param {string} options.method - Forecast method ('linear', 'exponential')
   * @returns {Promise<Object>} Forecast results
   */
  async forecast({ months = 3, method = "linear" }) {
    try {
      // Get historical data for forecasting
      const historicalData = await this.database.getHistoricalSales(12); // Last 12 months

      // Apply forecasting algorithm
      const forecast = this.calculateForecast(historicalData, months, method);

      return {
        success: true,
        forecast,
        method,
        confidence: this.calculateConfidence(forecast),
        metadata: {
          months,
          method,
          generatedAt: new Date().toISOString(),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        metadata: {
          months,
          method,
          generatedAt: new Date().toISOString(),
        },
      };
    }
  }

  /**
   * Generate a comprehensive sales report
   * @param {Object} options - Report options
   * @param {string} options.format - Report format ('pdf', 'excel', 'json')
   * @param {boolean} options.includeCharts - Include charts in report
   * @returns {Promise<Object>} Report generation results
   */
  async generateReport({ format = "pdf", includeCharts = true }) {
    try {
      // Get current month sales data
      const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM
      const salesData = await this.database.getSalesData(
        `${currentMonth}-01`,
        `${currentMonth}-31`,
      );

      // Generate report using reporting tool
      const report = await this.reporting.generateSalesReport(salesData, {
        format,
        includeCharts,
        title: `Sales Report - ${currentMonth}`,
      });

      return {
        success: true,
        report,
        format,
        metadata: {
          title: `Sales Report - ${currentMonth}`,
          format,
          generatedAt: new Date().toISOString(),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        metadata: {
          format,
          generatedAt: new Date().toISOString(),
        },
      };
    }
  }

  /**
   * Export sales data in various formats
   * @param {Object} options - Export options
   * @param {string} options.format - Export format ('csv', 'json', 'xml')
   * @param {string} options.startDate - Start date
   * @param {string} options.endDate - End date
   * @returns {Promise<Object>} Export results
   */
  async exportData({ format = "csv", startDate, endDate }) {
    try {
      // Get data to export
      const data = await this.database.getSalesData(startDate, endDate);

      // Format data according to requested format
      const formattedData = this.formatDataForExport(data, format);

      return {
        success: true,
        data: formattedData,
        format,
        metadata: {
          recordCount: data.length,
          format,
          exportedAt: new Date().toISOString(),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        metadata: {
          format,
          exportedAt: new Date().toISOString(),
        },
      };
    }
  }

  // Private helper methods
  processSalesData(salesData, groupBy) {
    // Group data by specified period
    const grouped = {};
    salesData.forEach((sale) => {
      const key = this.getGroupKey(sale.date, groupBy);
      if (!grouped[key]) {
        grouped[key] = { total: 0, count: 0, items: [] };
      }
      grouped[key].total += sale.amount;
      grouped[key].count += 1;
      grouped[key].items.push(sale);
    });
    return grouped;
  }

  generateInsights(processedData) {
    const periods = Object.keys(processedData);
    const insights = [];

    // Calculate trends
    if (periods.length >= 2) {
      const current = processedData[periods[periods.length - 1]];
      const previous = processedData[periods[periods.length - 2]];

      const growth = ((current.total - previous.total) / previous.total) * 100;
      insights.push({
        type: "growth",
        message: `Sales ${growth >= 0 ? "increased" : "decreased"} by ${Math.abs(growth).toFixed(1)}% compared to last period`,
        value: growth,
      });
    }

    // Identify top performing periods
    const sortedPeriods = periods.sort(
      (a, b) => processedData[b].total - processedData[a].total,
    );
    if (sortedPeriods.length > 0) {
      const topPeriod = sortedPeriods[0];
      insights.push({
        type: "top_performer",
        message: `Best performing period: ${topPeriod} with $${processedData[topPeriod].total.toFixed(2)}`,
        period: topPeriod,
        value: processedData[topPeriod].total,
      });
    }

    return insights;
  }

  calculateForecast(historicalData, months, method) {
    // Simple forecasting implementation
    const forecast = [];
    const lastValue = historicalData[historicalData.length - 1].total;

    for (let i = 1; i <= months; i++) {
      let predictedValue;
      if (method === "linear") {
        // Simple linear extrapolation
        const trend = this.calculateTrend(historicalData);
        predictedValue = lastValue + trend * i;
      } else if (method === "exponential") {
        // Simple exponential smoothing
        const alpha = 0.3;
        predictedValue = lastValue * Math.pow(1 + alpha, i);
      }

      forecast.push({
        month: i,
        predicted: Math.max(0, predictedValue), // Ensure non-negative
        method,
      });
    }

    return forecast;
  }

  calculateTrend(data) {
    if (data.length < 2) return 0;

    const values = data.map((d) => d.total);
    const n = values.length;
    const sumX = (n * (n - 1)) / 2;
    const sumY = values.reduce((sum, val) => sum + val, 0);
    const sumXY = values.reduce((sum, val, idx) => sum + val * idx, 0);
    const sumXX = (n * (n - 1) * (2 * n - 1)) / 6;

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    return slope;
  }

  calculateConfidence(forecast) {
    // Simple confidence calculation based on historical volatility
    return 0.75; // Placeholder - would calculate based on actual data
  }

  getGroupKey(date, groupBy) {
    const d = new Date(date);
    switch (groupBy) {
      case "day":
        return d.toISOString().slice(0, 10);
      case "week":
        const weekStart = new Date(d);
        weekStart.setDate(d.getDate() - d.getDay());
        return weekStart.toISOString().slice(0, 10);
      case "month":
        return d.toISOString().slice(0, 7);
      default:
        return d.toISOString().slice(0, 7);
    }
  }

  formatDataForExport(data, format) {
    switch (format) {
      case "csv":
        return this.convertToCSV(data);
      case "json":
        return JSON.stringify(data, null, 2);
      case "xml":
        return this.convertToXML(data);
      default:
        return data;
    }
  }

  convertToCSV(data) {
    if (data.length === 0) return "";

    const headers = Object.keys(data[0]);
    const csvRows = [];

    // Add headers
    csvRows.push(headers.join(","));

    // Add data rows
    data.forEach((row) => {
      const values = headers.map((header) => {
        const value = row[header];
        // Escape commas and quotes in CSV
        if (
          typeof value === "string" &&
          (value.includes(",") || value.includes('"'))
        ) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      });
      csvRows.push(values.join(","));
    });

    return csvRows.join("\n");
  }

  convertToXML(data) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<sales>\n';

    data.forEach((sale, index) => {
      xml += `  <sale id="${index + 1}">\n`;
      Object.entries(sale).forEach(([key, value]) => {
        xml += `    <${key}>${value}</${key}>\n`;
      });
      xml += "  </sale>\n";
    });

    xml += "</sales>";
    return xml;
  }
}

module.exports = { SalesAnalyzerAgent };
```

### Python Example

**File**: `agents/data-processor/agent.py`

```python
"""
Data Processor Agent

Processes and transforms data from various sources.
Core implementation of the data processing agent.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from .tools.database import DatabaseTool
from .tools.validation import ValidationTool

class DataProcessorAgent:
    """
    Agent for processing and transforming data from various sources.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.database = DatabaseTool(config.get('database', {}))
        self.validator = ValidationTool(config.get('validation', {}))
        self.logger = logging.getLogger(__name__)

    def process_data(self, source: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data from a specified source.

        Args:
            source: Data source identifier ('database', 'api', 'file')
            options: Processing options

        Returns:
            Dict containing processed data and metadata
        """
        try:
            self.logger.info(f"Processing data from source: {source}")

            # Retrieve raw data
            raw_data = self._retrieve_data(source, options)

            # Validate data
            validation_result = self.validator.validate(raw_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Data validation failed: {validation_result['errors']}",
                    'metadata': {
                        'source': source,
                        'processed_at': datetime.now().isoformat()
                    }
                }

            # Transform data
            processed_data = self._transform_data(raw_data, options)

            # Clean data
            cleaned_data = self._clean_data(processed_data, options)

            return {
                'success': True,
                'data': cleaned_data,
                'metadata': {
                    'source': source,
                    'record_count': len(cleaned_data) if hasattr(cleaned_data, '__len__') else 1,
                    'processed_at': datetime.now().isoformat(),
                    'validation': validation_result
                }
            }

        except Exception as e:
            self.logger.error(f"Data processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'metadata': {
                    'source': source,
                    'processed_at': datetime.now().isoformat()
                }
            }

    def aggregate_data(self, data: Any, group_by: List[str], aggregations: Dict[str, str]) -> Dict[str, Any]:
        """
        Aggregate data by specified groups with given aggregation functions.

        Args:
            data: Data to aggregate (DataFrame, list, etc.)
            group_by: Columns/fields to group by
            aggregations: Dict of field -> aggregation function

        Returns:
            Dict containing aggregated data and metadata
        """
        try:
            if isinstance(data, pd.DataFrame):
                # Pandas aggregation
                result = data.groupby(group_by).agg(aggregations).reset_index()
                return {
                    'success': True,
                    'data': result,
                    'metadata': {
                        'aggregation_type': 'pandas',
                        'group_count': len(result),
                        'aggregated_at': datetime.now().isoformat()
                    }
                }
            else:
                # Custom aggregation for other data types
                return self._custom_aggregate(data, group_by, aggregations)

        except Exception as e:
            return {
                'success': False,
                'error': f"Aggregation failed: {str(e)}",
                'metadata': {
                    'aggregated_at': datetime.now().isoformat()
                }
            }

    def export_data(self, data: Any, format: str, destination: str) -> Dict[str, Any]:
        """
        Export processed data to specified format and destination.

        Args:
            data: Data to export
            format: Export format ('csv', 'json', 'parquet', 'excel')
            destination: Export destination ('file', 'database', 'api')

        Returns:
            Dict containing export results and metadata
        """
        try:
            export_functions = {
                'csv': self._export_csv,
                'json': self._export_json,
                'parquet': self._export_parquet,
                'excel': self._export_excel
            }

            if format not in export_functions:
                return {
                    'success': False,
                    'error': f"Unsupported export format: {format}",
                    'metadata': {
                        'format': format,
                        'destination': destination,
                        'exported_at': datetime.now().isoformat()
                    }
                }

            result = export_functions[format](data, destination)

            return {
                'success': True,
                'result': result,
                'metadata': {
                    'format': format,
                    'destination': destination,
                    'exported_at': datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Export failed: {str(e)}",
                'metadata': {
                    'format': format,
                    'destination': destination,
                    'exported_at': datetime.now().isoformat()
                }
            }

    # Private helper methods
    def _retrieve_data(self, source: str, options: Dict[str, Any]) -> Any:
        """Retrieve data from specified source."""
        if source == 'database':
            return self.database.query(options.get('query', ''))
        elif source == 'api':
            return self._fetch_from_api(options.get('endpoint', ''), options)
        elif source == 'file':
            return self._read_from_file(options.get('file_path', ''), options)
        else:
            raise ValueError(f"Unsupported data source: {source}")

    def _transform_data(self, data: Any, options: Dict[str, Any]) -> Any:
        """Transform data according to specified rules."""
        transformations = options.get('transformations', [])

        for transformation in transformations:
            transform_type = transformation.get('type')
            if transform_type == 'rename_columns':
                data = self._rename_columns(data, transformation.get('mapping', {}))
            elif transform_type == 'filter':
                data = self._filter_data(data, transformation.get('condition', ''))
            elif transform_type == 'add_column':
                data = self._add_column(data, transformation.get('name', ''), transformation.get('expression', ''))

        return data

    def _clean_data(self, data: Any, options: Dict[str, Any]) -> Any:
        """Clean data by handling missing values, duplicates, etc."""
        cleaning_options = options.get('cleaning', {})

        if cleaning_options.get('remove_duplicates', False):
            data = self._remove_duplicates(data)

        if cleaning_options.get('handle_missing'):
            data = self._handle_missing_values(data, cleaning_options['handle_missing'])

        if cleaning_options.get('normalize'):
            data = self._normalize_data(data, cleaning_options['normalize'])

        return data

    def _custom_aggregate(self, data: List[Dict], group_by: List[str], aggregations: Dict[str, str]) -> Dict[str, Any]:
        """Custom aggregation for non-DataFrame data."""
        grouped_data = {}

        # Group data
        for item in data:
            key_parts = [str(item.get(field, '')) for field in group_by]
            key = '|'.join(key_parts)

            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append(item)

        # Apply aggregations
        result = []
        for key, items in grouped_data.items():
            aggregated_item = {}

            # Add group by fields
            key_parts = key.split('|')
            for i, field in enumerate(group_by):
                aggregated_item[field] = key_parts[i]

            # Apply aggregations
            for field, agg_func in aggregations.items():
                values = [item.get(field) for item in items if item.get(field) is not None]

                if agg_func == 'sum':
                    aggregated_item[field] = sum(values)
                elif agg_func == 'avg':
                    aggregated_item[field] = sum(values) / len(values) if values else 0
                elif agg_func == 'count':
                    aggregated_item[field] = len(values)
                elif agg_func == 'min':
                    aggregated_item[field] = min(values) if values else None
                elif agg_func == 'max':
                    aggregated_item[field] = max(values) if values else None

            result.append(aggregated_item)

        return {
            'success': True,
            'data': result,
            'metadata': {
                'aggregation_type': 'custom',
                'group_count': len(result),
                'aggregated_at': datetime.now().isoformat()
            }
        }

    # Export helper methods
    def _export_csv(self, data: Any, destination: str) -> str:
        """Export data as CSV."""
        if isinstance(data, pd.DataFrame):
            return data.to_csv(index=False)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        else:
            raise ValueError("Data format not supported for CSV export")

    def _export_json(self, data: Any, destination: str) -> str:
        """Export data as JSON."""
        import json
        return json.dumps(data, indent=2, default=str)

    def _export_parquet(self, data: Any, destination: str) -> bytes:
        """Export data as Parquet."""
        if isinstance(data, pd.DataFrame):
            import io
            buffer = io.BytesIO()
            data.to_parquet(buffer, index=False)
            return buffer.getvalue()
        else:
            raise ValueError("Data format not supported for Parquet export")

    def _export_excel(self, data: Any, destination: str) -> bytes:
        """Export data as Excel."""
        if isinstance(data, pd.DataFrame):
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                data.to_excel(writer, index=False, sheet_name='Data')
            return buffer.getvalue()
        else:
            raise ValueError("Data format not supported for Excel export")

    # Data transformation helpers
    def _rename_columns(self, data: Any, mapping: Dict[str, str]) -> Any:
        """Rename columns in data."""
        if isinstance(data, pd.DataFrame):
            return data.rename(columns=mapping)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            return [{mapping.get(k, k): v for k, v in item.items()} for item in data]
        return data

    def _filter_data(self, data: Any, condition: str) -> Any:
        """Filter data based on condition."""
        if isinstance(data, pd.DataFrame):
            return data.query(condition)
        # For other data types, implement custom filtering
        return data

    def _add_column(self, data: Any, name: str, expression: str) -> Any:
        """Add a new column based on expression."""
        if isinstance(data, pd.DataFrame):
            return data.assign(**{name: data.eval(expression)})
        # For other data types, implement custom column addition
        return data

    # Data cleaning helpers
    def _remove_duplicates(self, data: Any) -> Any:
        """Remove duplicate records."""
        if isinstance(data, pd.DataFrame):
            return data.drop_duplicates()
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            seen = set()
            unique_data = []
            for item in data:
                item_tuple = tuple(sorted(item.items()))
                if item_tuple not in seen:
                    seen.add(item_tuple)
                    unique_data.append(item)
            return unique_data
        return data

    def _handle_missing_values(self, data: Any, method: str) -> Any:
        """Handle missing values in data."""
        if isinstance(data, pd.DataFrame):
            if method == 'drop':
                return data.dropna()
            elif method == 'fill':
                return data.fillna('')
        return data

    def _normalize_data(self, data: Any, config: Dict) -> Any:
        """Normalize data values."""
        # Implement data normalization logic
        return data

    # Data retrieval helpers
    def _fetch_from_api(self, endpoint: str, options: Dict[str, Any]) -> Any:
        """Fetch data from API endpoint."""
        import requests
        response = requests.get(endpoint, params=options.get('params', {}))
        response.raise_for_status()
        return response.json()

    def _read_from_file(self, file_path: str, options: Dict[str, Any]) -> Any:
        """Read data from file."""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path).to_dict('records')
        elif file_path.endswith('.json'):
            import json
            with open(file_path, 'r') as f:
                return json.load(f)
        elif file_path.endswith('.parquet'):
            return pd.read_parquet(file_path).to_dict('records')
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
</content>
<parameter name="filePath">c:\wamp64\www\birdc_erp\skills\custom-sub-agents\references\01-agent-folder-structure.md
```
