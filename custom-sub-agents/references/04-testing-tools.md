# 🧪 Testing & Utility Frameworks

## 🧪 TESTS/ FOLDER

**Purpose**: Contains all test files and testing infrastructure for the agent.

### What Goes Here

- Unit tests for individual functions/methods
- Integration tests for end-to-end functionality
- Test fixtures and mock data
- Test utilities and helpers
- Test configuration files

### Example 1: agent.test.js (Jest)

**File**: `agents/sales-analyzer/tests/agent.test.js`

```javascript
/**
 * Sales Analyzer Agent - Unit Tests
 *
 * Tests the core functionality of the SalesAnalyzerAgent class.
 */

const { SalesAnalyzerAgent } = require("../agent");
const { DatabaseTool } = require("../tools/database");
const { ReportingTool } = require("../tools/reporting");

// Mock dependencies
jest.mock("../tools/database");
jest.mock("../tools/reporting");

describe("SalesAnalyzerAgent", () => {
  let agent;
  let mockDatabase;
  let mockReporting;

  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();

    // Create mock instances
    mockDatabase = new DatabaseTool();
    mockReporting = new ReportingTool();

    // Mock return values
    mockDatabase.getSalesData.mockResolvedValue([
      { date: "2024-01-01", amount: 1000, customer_id: 1 },
      { date: "2024-01-02", amount: 1500, customer_id: 2 },
    ]);

    // Create agent with mocked dependencies
    agent = new SalesAnalyzerAgent({
      database: mockDatabase,
      reporting: mockReporting,
      analysis: { maxRecords: 1000 },
    });
  });

  describe("analyze()", () => {
    test("analyzes sales data correctly", async () => {
      const result = await agent.analyze({
        startDate: "2024-01-01",
        endDate: "2024-01-31",
        groupBy: "month",
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.insights).toBeDefined();
      expect(mockDatabase.getSalesData).toHaveBeenCalledWith(
        "2024-01-01",
        "2024-01-31",
      );
    });

    test("handles database errors gracefully", async () => {
      mockDatabase.getSalesData.mockRejectedValue(
        new Error("Database connection failed"),
      );

      const result = await agent.analyze({
        startDate: "2024-01-01",
        endDate: "2024-01-31",
      });

      expect(result.success).toBe(false);
      expect(result.error).toBe("Database connection failed");
    });

    test("groups data by different periods", async () => {
      const result = await agent.analyze({
        startDate: "2024-01-01",
        endDate: "2024-01-07",
        groupBy: "day",
      });

      expect(result.success).toBe(true);
      // Verify data is grouped by day
      expect(Object.keys(result.data)).toHaveLength(7); // 7 days
    });

    test("respects maxRecords limit", async () => {
      // Mock large dataset
      const largeDataset = Array(2000)
        .fill()
        .map((_, i) => ({
          date: "2024-01-01",
          amount: 100 + i,
          customer_id: i,
        }));
      mockDatabase.getSalesData.mockResolvedValue(largeDataset);

      const result = await agent.analyze({
        startDate: "2024-01-01",
        endDate: "2024-01-31",
      });

      expect(result.success).toBe(true);
      // Should respect maxRecords from config
    });
  });

  describe("forecast()", () => {
    beforeEach(() => {
      mockDatabase.getHistoricalSales.mockResolvedValue([
        { month: "2023-01", total: 10000 },
        { month: "2023-02", total: 12000 },
        { month: "2023-03", total: 11000 },
        { month: "2023-04", total: 13000 },
        { month: "2023-05", total: 12500 },
        { month: "2023-06", total: 14000 },
      ]);
    });

    test("generates forecast using linear method", async () => {
      const result = await agent.forecast({
        months: 3,
        method: "linear",
      });

      expect(result.success).toBe(true);
      expect(result.forecast).toHaveLength(3);
      expect(result.method).toBe("linear");
      expect(result.confidence).toBeGreaterThan(0);
    });

    test("generates forecast using exponential method", async () => {
      const result = await agent.forecast({
        months: 2,
        method: "exponential",
      });

      expect(result.success).toBe(true);
      expect(result.forecast).toHaveLength(2);
      expect(result.method).toBe("exponential");
    });

    test("handles insufficient historical data", async () => {
      mockDatabase.getHistoricalSales.mockResolvedValue([
        { month: "2023-01", total: 10000 },
      ]);

      const result = await agent.forecast({
        months: 3,
        method: "linear",
      });

      expect(result.success).toBe(true);
      // Should still generate forecast with limited data
    });
  });

  describe("generateReport()", () => {
    beforeEach(() => {
      mockReporting.generateSalesReport.mockResolvedValue({
        format: "pdf",
        size: 245760,
        filename: "sales-report-2024-01.pdf",
      });
    });

    test("generates PDF report with charts", async () => {
      const result = await agent.generateReport({
        format: "pdf",
        includeCharts: true,
      });

      expect(result.success).toBe(true);
      expect(result.report.format).toBe("pdf");
      expect(mockReporting.generateSalesReport).toHaveBeenCalledWith(
        expect.any(Array),
        expect.objectContaining({
          format: "pdf",
          includeCharts: true,
          title: expect.stringContaining("Sales Report"),
        }),
      );
    });

    test("generates Excel report without charts", async () => {
      const result = await agent.generateReport({
        format: "excel",
        includeCharts: false,
      });

      expect(result.success).toBe(true);
      expect(result.report.format).toBe("excel");
      expect(mockReporting.generateSalesReport).toHaveBeenCalledWith(
        expect.any(Array),
        expect.objectContaining({
          format: "excel",
          includeCharts: false,
        }),
      );
    });

    test("handles reporting errors", async () => {
      mockReporting.generateSalesReport.mockRejectedValue(
        new Error("Chart generation failed"),
      );

      const result = await agent.generateReport({
        format: "pdf",
        includeCharts: true,
      });

      expect(result.success).toBe(false);
      expect(result.error).toBe("Chart generation failed");
    });
  });

  describe("exportData()", () => {
    test("exports data as CSV", async () => {
      const result = await agent.exportData({
        format: "csv",
        startDate: "2024-01-01",
        endDate: "2024-01-31",
      });

      expect(result.success).toBe(true);
      expect(result.format).toBe("csv");
      expect(typeof result.data).toBe("string");
      expect(result.data).toContain("date,amount,customer_id"); // CSV headers
    });

    test("exports data as JSON", async () => {
      const result = await agent.exportData({
        format: "json",
        startDate: "2024-01-01",
        endDate: "2024-01-31",
      });

      expect(result.success).toBe(true);
      expect(result.format).toBe("json");
      expect(Array.isArray(result.data)).toBe(true);
      expect(result.data).toHaveLength(2);
    });

    test("handles unsupported formats", async () => {
      const result = await agent.exportData({
        format: "unsupported",
        startDate: "2024-01-01",
        endDate: "2024-01-31",
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain("Unsupported export format");
    });
  });
});
```

### Example 2: integration.test.js

**File**: `agents/sales-analyzer/tests/integration.test.js`

```javascript
/**
 * Sales Analyzer Agent - Integration Tests
 *
 * Tests the agent with real dependencies and external services.
 * These tests are slower and may require external resources.
 */

const { createAgent } = require("../index");
const {
  setupTestDatabase,
  teardownTestDatabase,
} = require("./helpers/database");
const { mockExternalAPI } = require("./helpers/api-mock");

describe("SalesAnalyzerAgent Integration", () => {
  let agent;
  let dbConnection;

  beforeAll(async () => {
    // Set up test database
    dbConnection = await setupTestDatabase();

    // Create agent with real config
    agent = createAgent({
      database: {
        host: process.env.TEST_DB_HOST || "localhost",
        database: "test_sales_db",
        user: "test_user",
        password: "test_password",
      },
      analysis: {
        maxRecords: 1000,
        cacheEnabled: false, // Disable caching for tests
      },
    });
  });

  afterAll(async () => {
    // Clean up test database
    await teardownTestDatabase(dbConnection);
  });

  beforeEach(async () => {
    // Clear test data before each test
    await dbConnection.query("DELETE FROM sales_transactions");
    await dbConnection.query("DELETE FROM customers");

    // Insert test data
    await dbConnection.query(`
      INSERT INTO customers (id, name) VALUES
      (1, 'Customer A'),
      (2, 'Customer B'),
      (3, 'Customer C')
    `);

    await dbConnection.query(`
      INSERT INTO sales_transactions (date, amount, customer_id) VALUES
      ('2024-01-01', 1000.00, 1),
      ('2024-01-02', 1500.00, 2),
      ('2024-01-03', 800.00, 1),
      ('2024-01-04', 1200.00, 3),
      ('2024-01-05', 900.00, 2)
    `);
  });

  describe("End-to-End Analysis", () => {
    test("analyzes real sales data from database", async () => {
      const result = await agent.analyze({
        startDate: "2024-01-01",
        endDate: "2024-01-05",
        groupBy: "day",
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();

      // Verify data integrity
      const totalSales = Object.values(result.data).reduce(
        (sum, day) => sum + day.total,
        0,
      );
      expect(totalSales).toBe(5400); // 1000 + 1500 + 800 + 1200 + 900

      // Verify insights are generated
      expect(result.insights).toBeDefined();
      expect(Array.isArray(result.insights)).toBe(true);
    });

    test("handles large datasets efficiently", async () => {
      // Insert large amount of test data
      const largeData = Array(1000)
        .fill()
        .map((_, i) => ({
          date: "2024-01-01",
          amount: Math.random() * 1000,
          customer_id: (i % 3) + 1,
        }));

      const values = largeData
        .map((d) => `('${d.date}', ${d.amount}, ${d.customer_id})`)
        .join(", ");
      await dbConnection.query(`
        INSERT INTO sales_transactions (date, amount, customer_id) VALUES ${values}
      `);

      const startTime = Date.now();

      const result = await agent.analyze({
        startDate: "2024-01-01",
        endDate: "2024-01-05",
        groupBy: "month",
      });

      const duration = Date.now() - startTime;

      expect(result.success).toBe(true);
      expect(duration).toBeLessThan(5000); // Should complete within 5 seconds
    });

    test("integrates with external reporting service", async () => {
      // Mock external API
      const apiMock = mockExternalAPI({
        endpoint: "https://api.reporting-service.com/generate",
        response: { reportId: "report-123", status: "completed" },
      });

      const result = await agent.generateReport({
        format: "pdf",
        includeCharts: true,
      });

      expect(result.success).toBe(true);
      expect(result.report.reportId).toBe("report-123");

      // Verify API was called correctly
      expect(apiMock.requests).toHaveLength(1);
      expect(apiMock.requests[0].body).toMatchObject({
        format: "pdf",
        includeCharts: true,
      });

      apiMock.restore();
    });
  });

  describe("Database Integration", () => {
    test("handles database connection failures", async () => {
      // Temporarily break database connection
      await dbConnection.end();

      const result = await agent.analyze({
        startDate: "2024-01-01",
        endDate: "2024-01-05",
      });

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/database|connection/i);

      // Restore connection for other tests
      dbConnection = await setupTestDatabase();
    });

    test("respects database query limits", async () => {
      // Insert more data than maxRecords
      const excessData = Array(1500)
        .fill()
        .map((_, i) => ({
          date: "2024-01-01",
          amount: 100,
          customer_id: 1,
        }));

      const values = excessData
        .map((d) => `('${d.date}', ${d.amount}, ${d.customer_id})`)
        .join(", ");
      await dbConnection.query(`
        INSERT INTO sales_transactions (date, amount, customer_id) VALUES ${values}
      `);

      const result = await agent.analyze({
        startDate: "2024-01-01",
        endDate: "2024-01-05",
      });

      expect(result.success).toBe(true);
      // Should not exceed maxRecords limit
      const totalRecords = Object.values(result.data).reduce(
        (sum, day) => sum + day.count,
        0,
      );
      expect(totalRecords).toBeLessThanOrEqual(1000);
    });
  });

  describe("Performance Benchmarks", () => {
    test("meets performance requirements", async () => {
      const testCases = [
        { records: 100, expectedTime: 100 },
        { records: 500, expectedTime: 200 },
        { records: 1000, expectedTime: 500 },
      ];

      for (const testCase of testCases) {
        // Clear and insert test data
        await dbConnection.query("DELETE FROM sales_transactions");
        const data = Array(testCase.records)
          .fill()
          .map((_, i) => ({
            date: "2024-01-01",
            amount: Math.random() * 1000,
            customer_id: (i % 3) + 1,
          }));

        const values = data
          .map((d) => `('${d.date}', ${d.amount}, ${d.customer_id})`)
          .join(", ");
        await dbConnection.query(`
          INSERT INTO sales_transactions (date, amount, customer_id) VALUES ${values}
        `);

        const startTime = Date.now();

        const result = await agent.analyze({
          startDate: "2024-01-01",
          endDate: "2024-01-05",
        });

        const duration = Date.now() - startTime;

        expect(result.success).toBe(true);
        expect(duration).toBeLessThan(testCase.expectedTime);
      }
    });
  });
});
```

## 🛠️ TOOLS/ FOLDER

**Purpose**: Contains reusable utility functions, helpers, and service integrations.

### What Goes Here

- Database connection and query helpers
- External API integrations
- Data transformation utilities
- Validation functions
- Logging and monitoring helpers
- File system operations
- Caching mechanisms

### Example 1: tools/database.js

**File**: `agents/sales-analyzer/tools/database.js`

```javascript
/**
 * Database Tool
 *
 * Handles all database operations for the Sales Analyzer Agent.
 * Provides a clean interface for querying sales data.
 */

const mysql = require("mysql2/promise");

class DatabaseTool {
  constructor(config) {
    this.config = config;
    this.pool = null;
  }

  async connect() {
    if (!this.pool) {
      this.pool = mysql.createPool({
        host: this.config.host,
        port: this.config.port || 3306,
        database: this.config.database,
        user: this.config.user,
        password: this.config.password,
        waitForConnections: true,
        connectionLimit: this.config.poolSize || 10,
        queueLimit: 0,
        acquireTimeout: this.config.acquireTimeoutMillis || 60000,
        timeout: this.config.timeout || 60000,
        enableKeepAlive: true,
        keepAliveInitialDelay: 0,
      });
    }
    return this.pool;
  }

  async disconnect() {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
    }
  }

  async query(sql, params = []) {
    const pool = await this.connect();
    try {
      const [rows] = await pool.execute(sql, params);
      return rows;
    } catch (error) {
      console.error("Database query error:", error);
      throw error;
    }
  }

  async getSalesData(startDate, endDate, options = {}) {
    const limit = options.limit || this.config.maxRecords || 100000;
    const offset = options.offset || 0;

    const sql = `
      SELECT
        st.id,
        st.date,
        st.amount,
        st.customer_id,
        c.name as customer_name,
        st.product_id,
        p.name as product_name,
        st.quantity,
        st.unit_price
      FROM sales_transactions st
      LEFT JOIN customers c ON st.customer_id = c.id
      LEFT JOIN products p ON st.product_id = p.id
      WHERE st.date BETWEEN ? AND ?
      ORDER BY st.date ASC, st.id ASC
      LIMIT ? OFFSET ?
    `;

    const results = await this.query(sql, [startDate, endDate, limit, offset]);

    // Convert date strings to Date objects for easier processing
    return results.map((row) => ({
      ...row,
      date: new Date(row.date),
    }));
  }

  async getSalesByPeriod(startDate, endDate, groupBy = "month") {
    let dateFormat;
    switch (groupBy) {
      case "day":
        dateFormat = "%Y-%m-%d";
        break;
      case "week":
        dateFormat = "%Y-%u";
        break;
      case "month":
        dateFormat = "%Y-%m";
        break;
      case "quarter":
        dateFormat = 'CONCAT(%Y, "-", QUARTER(date))';
        break;
      case "year":
        dateFormat = "%Y";
        break;
      default:
        dateFormat = "%Y-%m";
    }

    const sql = `
      SELECT
        DATE_FORMAT(date, '${dateFormat}') as period,
        COUNT(*) as transaction_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        MIN(amount) as min_amount,
        MAX(amount) as max_amount,
        SUM(quantity) as total_quantity
      FROM sales_transactions
      WHERE date BETWEEN ? AND ?
      GROUP BY period
      ORDER BY period ASC
    `;

    return await this.query(sql, [startDate, endDate]);
  }

  async getHistoricalSales(months = 12) {
    const sql = `
      SELECT
        DATE_FORMAT(date, '%Y-%m') as month,
        SUM(amount) as total,
        COUNT(*) as transactions
      FROM sales_transactions
      WHERE date >= DATE_SUB(CURDATE(), INTERVAL ? MONTH)
      GROUP BY month
      ORDER BY month ASC
    `;

    return await this.query(sql, [months]);
  }

  async getTopCustomers(limit = 10, startDate = null, endDate = null) {
    let dateFilter = "";
    let params = [limit];

    if (startDate && endDate) {
      dateFilter = "AND st.date BETWEEN ? AND ?";
      params = [startDate, endDate, limit];
    }

    const sql = `
      SELECT
        c.id,
        c.name,
        COUNT(st.id) as transaction_count,
        SUM(st.amount) as total_amount,
        AVG(st.amount) as avg_transaction,
        MAX(st.date) as last_transaction
      FROM customers c
      JOIN sales_transactions st ON c.id = st.customer_id
      WHERE 1=1 ${dateFilter}
      GROUP BY c.id, c.name
      ORDER BY total_amount DESC
      LIMIT ?
    `;

    return await this.query(sql, params);
  }

  async getProductPerformance(startDate, endDate) {
    const sql = `
      SELECT
        p.id,
        p.name,
        p.category,
        SUM(st.amount) as total_sales,
        SUM(st.quantity) as total_quantity,
        COUNT(st.id) as transaction_count,
        AVG(st.unit_price) as avg_price
      FROM products p
      JOIN sales_transactions st ON p.id = st.product_id
      WHERE st.date BETWEEN ? AND ?
      GROUP BY p.id, p.name, p.category
      ORDER BY total_sales DESC
    `;

    return await this.query(sql, [startDate, endDate]);
  }

  async insertSalesTransaction(transaction) {
    const sql = `
      INSERT INTO sales_transactions
      (date, amount, customer_id, product_id, quantity, unit_price)
      VALUES (?, ?, ?, ?, ?, ?)
    `;

    const params = [
      transaction.date,
      transaction.amount,
      transaction.customer_id,
      transaction.product_id,
      transaction.quantity,
      transaction.unit_price,
    ];

    const result = await this.query(sql, params);
    return result.insertId;
  }

  async updateSalesTransaction(id, updates) {
    const setParts = [];
    const params = [];

    Object.entries(updates).forEach(([key, value]) => {
      setParts.push(`${key} = ?`);
      params.push(value);
    });

    params.push(id);

    const sql = `
      UPDATE sales_transactions
      SET ${setParts.join(", ")}
      WHERE id = ?
    `;

    return await this.query(sql, params);
  }

  async deleteSalesTransaction(id) {
    const sql = "DELETE FROM sales_transactions WHERE id = ?";
    return await this.query(sql, [id]);
  }

  async getTransactionCount(startDate = null, endDate = null) {
    let sql = "SELECT COUNT(*) as count FROM sales_transactions";
    let params = [];

    if (startDate && endDate) {
      sql += " WHERE date BETWEEN ? AND ?";
      params = [startDate, endDate];
    }

    const result = await this.query(sql, params);
    return result[0].count;
  }

  async healthCheck() {
    try {
      await this.query("SELECT 1");
      return { status: "healthy", timestamp: new Date() };
    } catch (error) {
      return {
        status: "unhealthy",
        error: error.message,
        timestamp: new Date(),
      };
    }
  }
}

module.exports = { DatabaseTool };
```

### Example 2: tools/reporting.js

**File**: `agents/sales-analyzer/tools/reporting.js`

```javascript
/**
 * Reporting Tool
 *
 * Handles report generation and formatting for various output formats.
 * Integrates with external reporting services and template engines.
 */

const fs = require('fs').promises;
const path = require('path');
const puppeteer = require('puppeteer');
const ExcelJS = require('exceljs');
const PDFDocument = require('pdfkit');
const Handlebars = require('handlebars');

class ReportingTool {
  constructor(config) {
    this.config = config;
    this.templates = new Map();
    this.cache = new Map();
  }

  async generateSalesReport(salesData, options = {}) {
    const {
      format = 'pdf',
      includeCharts = true,
      title = 'Sales Report',
      template = 'default'
    } = options;

    try {
      const reportData = this.prepareReportData(salesData);

      switch (format.toLowerCase()) {
        case 'pdf':
          return await this.generatePDFReport(reportData, { includeCharts, title, template });

        case 'excel':
          return await this.generateExcelReport(reportData, { includeCharts, title });

        case 'html':
          return await this.generateHTMLReport(reportData, { includeCharts, title, template });

        case 'json':
          return await this.generateJSONReport(reportData, options);

        default:
          throw new Error(`Unsupported report format: ${format}`);
      }
    } catch (error) {
      console.error('Report generation failed:', error);
      throw error;
    }
  }

  prepareReportData(salesData) {
    // Calculate summary statistics
    const totalSales = salesData.reduce((sum, sale) => sum + sale.amount, 0);
    const totalTransactions = salesData.length;
    const averageTransaction = totalSales / totalTransactions;

    // Group by date
    const salesByDate = salesData.reduce((acc, sale) => {
      const date = sale.date.toISOString().split('T')[0];
      if (!acc[date]) {
        acc[date] = { date, total: 0, count: 0, transactions: [] };
      }
      acc[date].total += sale.amount;
      acc[date].count += 1;
      acc[date].transactions.push(sale);
      return acc;
    }, {});

    // Group by customer
    const salesByCustomer = salesData.reduce((acc, sale) => {
      const customerId = sale.customer_id;
      if (!acc[customerId]) {
        acc[customerId] = {
          customer_id: customerId,
          customer_name: sale.customer_name,
          total: 0,
          count: 0,
          transactions: []
        };
      }
      acc[customerId].total += sale.amount;
      acc[customerId].count += 1;
      acc[customerId].transactions.push(sale);
      return acc;
    }, {});

    return {
      summary: {
        totalSales,
        totalTransactions,
        averageTransaction,
        dateRange: {
          start: salesData[0]?.date.toISOString().split('T')[0],
          end: salesData[salesData.length - 1]?.date.toISOString().split('T')[0]
        }
      },
      salesByDate: Object.values(salesByDate),
      salesByCustomer: Object.values(salesByCustomer),
      rawData: salesData
    };
  }

  async generatePDFReport(reportData, options) {
    const { includeCharts, title, template } = options;

    // Get HTML template
    const htmlTemplate = await this.loadTemplate(template || 'sales-report');
    const html = this.renderTemplate(htmlTemplate, {
      ...reportData,
      title,
      includeCharts,
      generatedAt: new Date().toISOString()
    });

    // Generate PDF using Puppeteer
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
      const page = await browser.newPage();
      await page.setContent(html, { waitUntil: 'networkidle0' });

      const pdf = await page.pdf({
        format: 'A4',
        printBackground: true,
        margin: {
          top: '1cm',
          right: '1cm',
          bottom: '1cm',
          left: '1cm'
        }
      });

      return {
        format: 'pdf',
        data: pdf,
        size: pdf.length,
        filename: `${title.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}.pdf`
      };
    } finally {
      await browser.close();
    }
  }

  async generateExcelReport(reportData, options) {
    const { includeCharts, title } = options;

    const workbook = new ExcelJS.Workbook();
    workbook.creator = 'Sales Analyzer Agent';
    workbook.created = new Date();

    // Summary sheet
    const summarySheet = workbook.addWorksheet('Summary');
    summarySheet.addRow(['Sales Report Summary']);
    summarySheet.addRow(['Generated', new Date()]);
    summarySheet.addRow(['Total Sales', reportData.summary.totalSales]);
    summarySheet.addRow(['Total Transactions', reportData.summary.totalTransactions]);
    summarySheet.addRow(['Average Transaction', reportData.summary.averageTransaction]);

    // Sales by Date sheet
    const dateSheet = workbook.addWorksheet('Sales by Date');
    dateSheet.addRow(['Date', 'Total Sales', 'Transaction Count']);
    reportData.salesByDate.forEach(day => {
      dateSheet.addRow([day.date, day.total, day.count]);
    });

    // Sales by Customer sheet
    const customerSheet = workbook.addWorksheet('Sales by Customer');
    customerSheet.addRow(['Customer ID', 'Customer Name', 'Total Sales', 'Transaction Count']);
    reportData.salesByCustomer.forEach(customer => {
      customerSheet.addRow([customer.customer_id, customer.customer_name, customer.total, customer.count]);
    });

    // Raw Data sheet
    const dataSheet = workbook.addWorksheet('Raw Data');
    dataSheet.addRow(['Date', 'Amount', 'Customer ID', 'Customer Name', 'Product ID', 'Product Name', 'Quantity', 'Unit Price']);
    reportData.rawData.forEach(transaction => {
      dataSheet.addRow([
        transaction.date.toISOString().split('T')[0],
        transaction.amount,
        transaction.customer_id,
        transaction.customer_name,
        transaction.product_id,
        transaction.product_name,
        transaction.quantity,
        transaction.unit_price
      ]);
    });

    const buffer = await workbook.xlsx.writeBuffer();

    return {
      format: 'excel',
      data: buffer,
      size: buffer.length,
      filename: `${title.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}.xlsx`
    };
  }

  async generateHTMLReport(reportData, options) {
    const { includeCharts, title, template } = options;

    const htmlTemplate = await this.loadTemplate(template || 'sales-report-html');
    const html = this.renderTemplate(htmlTemplate, {
      ...reportData,
      title,
      includeCharts,
      generatedAt: new Date().toISOString()
    });

    return {
      format: 'html',
      data: html,
      size: Buffer.byteLength(html, 'utf8'),
      filename: `${title.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}.html`
    };
  }

  async generateJSONReport(reportData, options) {
    const jsonData = {
      ...reportData,
      metadata: {
        generatedAt: new Date().toISOString(),
        version: '1.0.0',
        format: 'json'
      }
    };

    const jsonString = JSON.stringify(jsonData, null, 2);

    return {
      format: 'json',
      data: jsonString,
      size: Buffer.byteLength(jsonString, 'utf8'),
      filename: `sales-report-${Date.now()}.json`
    };
  }

  async loadTemplate(templateName) {
    if (this.templates.has(templateName)) {
      return this.templates.get(templateName);
    }

    const templatePath = path.join(__dirname, '..', 'templates', `${templateName}.hbs`);

    try {
      const templateContent = await fs.readFile(templatePath, 'utf8');
      const compiled = Handlebars.compile(templateContent);
      this.templates.set(templateName, compiled);
      return compiled;
    } catch (error) {
      // Fallback to default template
      const defaultTemplate = await this.getDefaultTemplate(templateName);
      const compiled = Handlebars.compile(defaultTemplate);
      this.templates.set(templateName, compiled);
      return compiled;
    }
  }

  renderTemplate(template, data) {
    return template(data);
  }

  async getDefaultTemplate(type) {
    // Default HTML template for sales reports
    if (type === 'sales-report') {
      return `
        <!DOCTYPE html>
        <html>
        <head>
          <title>{{title}}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
            .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>{{title}}</h1>
            <p>Generated on {{generatedAt}}</p>
          </div>

          <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Sales:</strong> ${{summary.totalSales}}</p>
            <p><strong>Total Transactions:</strong> {{summary.totalTransactions}}</p>
            <p><strong>Average Transaction:</strong> ${{averageTransaction}}</p>
            <p><strong>Date Range:</strong> {{summary.dateRange.start}} to {{summary.dateRange.end}}</p>
          </div>

          <h2>Sales by Date</h2>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Total Sales</th>
                <th>Transaction Count</th>
              </tr>
            </thead>
            <tbody>
              {{#each salesByDate}}
              <tr>
                <td>{{date}}</td>
                <td>${{total}}</td>
                <td>{{count}}</td>
              </tr>
              {{/each}}
            </tbody>
          </table>

          <div class="footer">
            <p>Report generated by Sales Analyzer Agent v1.0.0</p>
          </div>
        </body>
        </html>
      `;
    }

    return '<div>Default template</div>';
  }
}

module.exports = { ReportingTool };
```

### Example 3: tools/validation.js

**File**: `agents/sales-analyzer/tools/validation.js`

```javascript
/**
 * Validation Tool
 *
 * Provides data validation, sanitization, and business rule checking
 * for the Sales Analyzer Agent.
 */

const Joi = require("joi");

class ValidationTool {
  constructor(config) {
    this.config = config;
    this.schemas = this.initializeSchemas();
  }

  initializeSchemas() {
    return {
      salesTransaction: Joi.object({
        date: Joi.date().required(),
        amount: Joi.number().positive().precision(2).required(),
        customer_id: Joi.number().integer().positive().required(),
        product_id: Joi.number().integer().positive().optional(),
        quantity: Joi.number().positive().precision(2).required(),
        unit_price: Joi.number().positive().precision(2).required(),
      }),

      analysisRequest: Joi.object({
        startDate: Joi.date().required(),
        endDate: Joi.date()
          .when("startDate", {
            is: Joi.exist(),
            then: Joi.date().min(Joi.ref("startDate")),
          })
          .required(),
        groupBy: Joi.string()
          .valid("day", "week", "month", "quarter", "year")
          .default("month"),
        limit: Joi.number().integer().min(1).max(100000).default(10000),
      }),

      forecastRequest: Joi.object({
        months: Joi.number().integer().min(1).max(24).default(3),
        method: Joi.string()
          .valid("linear", "exponential", "moving_average")
          .default("linear"),
        confidence: Joi.boolean().default(true),
      }),

      reportRequest: Joi.object({
        format: Joi.string()
          .valid("pdf", "excel", "html", "json")
          .default("pdf"),
        includeCharts: Joi.boolean().default(true),
        title: Joi.string().max(100).default("Sales Report"),
        dateRange: Joi.object({
          start: Joi.date().required(),
          end: Joi.date().required(),
        }).optional(),
      }),
    };
  }

  validate(data, schemaName) {
    const schema = this.schemas[schemaName];
    if (!schema) {
      throw new Error(`Unknown validation schema: ${schemaName}`);
    }

    const { error, value } = schema.validate(data, {
      abortEarly: false,
      stripUnknown: true,
    });

    if (error) {
      return {
        valid: false,
        errors: error.details.map((detail) => ({
          field: detail.path.join("."),
          message: detail.message,
          value: detail.context.value,
        })),
        sanitizedData: null,
      };
    }

    return {
      valid: true,
      errors: [],
      sanitizedData: value,
    };
  }

  validateSalesTransaction(transaction) {
    return this.validate(transaction, "salesTransaction");
  }

  validateAnalysisRequest(request) {
    return this.validate(request, "analysisRequest");
  }

  validateForecastRequest(request) {
    return this.validate(request, "forecastRequest");
  }

  validateReportRequest(request) {
    return this.validate(request, "reportRequest");
  }

  validateSalesData(data) {
    if (!Array.isArray(data)) {
      return {
        valid: false,
        errors: [
          {
            field: "data",
            message: "Data must be an array",
            value: typeof data,
          },
        ],
        sanitizedData: null,
      };
    }

    if (data.length === 0) {
      return {
        valid: false,
        errors: [
          { field: "data", message: "Data array cannot be empty", value: 0 },
        ],
        sanitizedData: null,
      };
    }

    const errors = [];
    const sanitizedData = [];

    data.forEach((item, index) => {
      const validation = this.validateSalesTransaction(item);
      if (!validation.valid) {
        errors.push({
          index,
          errors: validation.errors,
        });
      } else {
        sanitizedData.push(validation.sanitizedData);
      }
    });

    return {
      valid: errors.length === 0,
      errors,
      sanitizedData: errors.length === 0 ? sanitizedData : null,
    };
  }

  validateDateRange(startDate, endDate) {
    const errors = [];

    if (!startDate || !endDate) {
      errors.push({
        field: "dateRange",
        message: "Both start and end dates are required",
      });
    } else {
      const start = new Date(startDate);
      const end = new Date(endDate);

      if (isNaN(start.getTime()) || isNaN(end.getTime())) {
        errors.push({ field: "dateRange", message: "Invalid date format" });
      } else if (start > end) {
        errors.push({
          field: "dateRange",
          message: "Start date cannot be after end date",
        });
      } else if (end - start > 365 * 24 * 60 * 60 * 1000) {
        // 1 year
        errors.push({
          field: "dateRange",
          message: "Date range cannot exceed 1 year",
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  validateBusinessRules(data, rules = {}) {
    const errors = [];

    // Check for negative amounts
    if (rules.noNegativeAmounts !== false) {
      data.forEach((item, index) => {
        if (item.amount < 0) {
          errors.push({
            index,
            field: "amount",
            message: "Transaction amount cannot be negative",
            value: item.amount,
          });
        }
      });
    }

    // Check for future dates
    if (rules.noFutureDates !== false) {
      const now = new Date();
      data.forEach((item, index) => {
        if (item.date > now) {
          errors.push({
            index,
            field: "date",
            message: "Transaction date cannot be in the future",
            value: item.date,
          });
        }
      });
    }

    // Check for duplicate transactions (same customer, date, amount)
    if (rules.noDuplicates !== false) {
      const seen = new Set();
      data.forEach((item, index) => {
        const key = `${item.customer_id}-${item.date.toISOString()}-${item.amount}`;
        if (seen.has(key)) {
          errors.push({
            index,
            field: "transaction",
            message: "Duplicate transaction detected",
            value: key,
          });
        }
        seen.add(key);
      });
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  sanitizeData(data, options = {}) {
    return data.map((item) => {
      const sanitized = { ...item };

      // Trim string fields
      Object.keys(sanitized).forEach((key) => {
        if (typeof sanitized[key] === "string") {
          sanitized[key] = sanitized[key].trim();
        }
      });

      // Round numeric fields
      if (options.roundAmounts && typeof sanitized.amount === "number") {
        sanitized.amount = Math.round(sanitized.amount * 100) / 100;
      }

      // Normalize dates
      if (sanitized.date && !(sanitized.date instanceof Date)) {
        sanitized.date = new Date(sanitized.date);
      }

      return sanitized;
    });
  }

  generateValidationReport(data, validations) {
    return {
      summary: {
        totalRecords: data.length,
        validRecords: validations.filter((v) => v.valid).length,
        invalidRecords: validations.filter((v) => !v.valid).length,
        totalErrors: validations.reduce((sum, v) => sum + v.errors.length, 0),
      },
      validations,
      recommendations: this.generateRecommendations(validations),
    };
  }

  generateRecommendations(validations) {
    const recommendations = [];
    const errorCounts = {};

    // Count error types
    validations.forEach((validation) => {
      validation.errors.forEach((error) => {
        const key = `${error.field}:${error.message}`;
        errorCounts[key] = (errorCounts[key] || 0) + 1;
      });
    });

    // Generate recommendations based on error patterns
    Object.entries(errorCounts).forEach(([errorKey, count]) => {
      if (count > validations.length * 0.1) {
        // More than 10% of records
        const [field, message] = errorKey.split(":");
        recommendations.push({
          type: "data_quality",
          field,
          issue: message,
          affectedRecords: count,
          recommendation: this.getRecommendationForError(field, message),
        });
      }
    });

    return recommendations;
  }

  getRecommendationForError(field, message) {
    const recommendations = {
      amount: {
        "must be a positive number":
          "Review data entry process for negative amounts",
        "is required": "Ensure amount field is always populated",
      },
      date: {
        "must be a valid date":
          "Standardize date format across all data sources",
        "cannot be in the future": "Implement date validation at data entry",
      },
      customer_id: {
        "is required": "Verify customer identification process",
      },
    };

    return recommendations[field]?.[message] || "Review data validation rules";
  }
}

module.exports = { ValidationTool };
```

## 🔄 How They Work Together

The `tests/` and `tools/` folders work together to ensure agent reliability:

```
agent.js (main logic)
    ↓
uses tools/database.js (data access)
    ↓
uses tools/reporting.js (output generation)
    ↓
uses tools/validation.js (data quality)
    ↓
tested by tests/agent.test.js (unit tests)
    ↓
tested by tests/integration.test.js (end-to-end)
```

## ✅ When to Use tests/ and tools/

### ✅ Use tests/ When

- **Unit Testing**: Test individual functions/methods
- **Integration Testing**: Test with real dependencies
- **Regression Testing**: Ensure changes don't break existing functionality
- **Performance Testing**: Validate speed and resource usage
- **Edge Case Testing**: Test unusual inputs and error conditions

### ✅ Use tools/ When

- **Reusable Logic**: Code used by multiple parts of the agent
- **External Integrations**: Database, APIs, file systems
- **Complex Operations**: Data processing, validation, formatting
- **Shared Utilities**: Common functions across the agent
- **Abstraction Layer**: Hide complexity from main agent logic

### ❌ DON'T Use tools/ For

- **One-off Logic**: Code only used once
- **Agent-Specific Logic**: Belongs in agent.js
- **Configuration**: Belongs in config.json
- **Documentation**: Belongs in README.md

## 🏃 Running Tests

### package.json Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:integration": "jest --testPathPattern=integration",
    "test:unit": "jest --testPathPattern=unit"
  }
}
```

### Jest Configuration

```javascript
// jest.config.js
module.exports = {
  testEnvironment: "node",
  testMatch: ["<rootDir>/tests/**/*.test.js", "<rootDir>/tests/**/*.spec.js"],
  collectCoverageFrom: ["agent.js", "tools/**/*.js", "index.js"],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ["<rootDir>/tests/setup.js"],
};
```

### Test Setup File

```javascript
// tests/setup.js
const dotenv = require("dotenv");

// Load test environment variables
dotenv.config({ path: ".env.test" });

// Global test setup
beforeAll(async () => {
  // Setup test database, mocks, etc.
});

afterAll(async () => {
  // Cleanup
});

// Custom matchers
expect.extend({
  toBeValidDate(received) {
    const pass = received instanceof Date && !isNaN(received);
    return {
      message: () => `expected ${received} to be a valid Date`,
      pass,
    };
  },
});
```

## 📁 Summary

### tests/ Folder

- **Purpose**: Ensure agent reliability and catch regressions
- **Contents**: Unit tests, integration tests, fixtures, helpers
- **Tools**: Jest, Mocha, test frameworks
- **Coverage**: Aim for 80%+ code coverage

### tools/ Folder

- **Purpose**: Encapsulate reusable logic and external integrations
- **Contents**: Database helpers, API clients, validation, utilities
- **Design**: Single responsibility, dependency injection
- **Testing**: Test tools independently of agent logic

### Best Practice

```
Keep agent.js focused on orchestration
Move reusable logic to tools/
Test everything thoroughly in tests/
```

This structure ensures maintainable, testable, and reliable agents.</content>
<parameter name="filePath">c:\wamp64\www\birdc_erp\skills\custom-sub-agents\references\04-testing-tools.md
