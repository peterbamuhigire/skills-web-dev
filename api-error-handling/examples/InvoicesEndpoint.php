<?php

/**
 * Invoices API Endpoint
 *
 * Complete example showing proper error handling patterns.
 * Demonstrates validation, business rules, and database errors.
 */

require_once __DIR__ . '/../references/bootstrap.php';

use App\Http\ApiResponse;
use App\Http\Exceptions\{NotFoundException, ValidationException, ConflictException};

// Require authentication for all invoice operations
require_auth();

// Route request to appropriate handler
handle_request(function () {
    $method = $_SERVER['REQUEST_METHOD'];

    match ($method) {
        'GET' => handleGet(),
        'POST' => handlePost(),
        'PUT' => handlePut(),
        'DELETE' => handleDelete(),
        default => ApiResponse::methodNotAllowed(['GET', 'POST', 'PUT', 'DELETE'])
    };
});

/**
 * GET - List or retrieve invoices
 */
function handleGet(): void
{
    $db = get_db();
    $auth = require_auth();

    // Get single invoice by ID
    if (isset($_GET['id'])) {
        $stmt = $db->prepare("
            SELECT * FROM invoices
            WHERE id = ? AND franchise_id = ?
        ");
        $stmt->execute([$_GET['id'], $auth['franchise_id']]);
        $invoice = $stmt->fetch();

        if (!$invoice) {
            throw new NotFoundException('Invoice', $_GET['id']);
        }

        ApiResponse::success($invoice);
        return;
    }

    // List invoices with filters
    $status = $_GET['status'] ?? null;
    $customerId = $_GET['customer_id'] ?? null;

    $sql = "SELECT * FROM invoices WHERE franchise_id = ?";
    $params = [$auth['franchise_id']];

    if ($status) {
        $sql .= " AND status = ?";
        $params[] = $status;
    }

    if ($customerId) {
        $sql .= " AND customer_id = ?";
        $params[] = $customerId;
    }

    $sql .= " ORDER BY created_at DESC LIMIT 100";

    $stmt = $db->prepare($sql);
    $stmt->execute($params);
    $invoices = $stmt->fetchAll();

    ApiResponse::success($invoices);
}

/**
 * POST - Create new invoice
 */
function handlePost(): void
{
    require_permission('CREATE_INVOICES');

    $data = read_json_body();
    validate_required($data, ['customer_id', 'items']);

    // Validation
    $errors = validateInvoiceData($data);
    if ($errors) {
        throw new ValidationException($errors, 'Invoice validation failed');
    }

    $db = get_db();
    $auth = require_auth();

    // Verify customer exists
    $stmt = $db->prepare("
        SELECT id FROM customers
        WHERE id = ? AND franchise_id = ?
    ");
    $stmt->execute([$data['customer_id'], $auth['franchise_id']]);
    if (!$stmt->fetch()) {
        throw new NotFoundException('Customer', $data['customer_id']);
    }

    // Start transaction
    $db->beginTransaction();

    try {
        // Insert invoice
        $stmt = $db->prepare("
            INSERT INTO invoices (
                franchise_id, customer_id, invoice_number,
                total_amount, status, notes, created_at
            ) VALUES (?, ?, ?, ?, 'pending', ?, NOW())
        ");

        $invoiceNumber = generateInvoiceNumber($db, $auth['franchise_id']);
        $totalAmount = calculateTotal($data['items']);

        $stmt->execute([
            $auth['franchise_id'],
            $data['customer_id'],
            $invoiceNumber,
            $totalAmount,
            $data['notes'] ?? ''
        ]);

        $invoiceId = $db->lastInsertId();

        // Insert invoice items
        $stmt = $db->prepare("
            INSERT INTO invoice_items (
                invoice_id, product_id, quantity, unit_price, total
            ) VALUES (?, ?, ?, ?, ?)
        ");

        foreach ($data['items'] as $item) {
            $stmt->execute([
                $invoiceId,
                $item['product_id'],
                $item['quantity'],
                $item['unit_price'],
                $item['quantity'] * $item['unit_price']
            ]);
        }

        $db->commit();

        ApiResponse::created([
            'id' => $invoiceId,
            'invoice_number' => $invoiceNumber
        ], 'Invoice created successfully');

    } catch (PDOException $e) {
        $db->rollBack();
        throw $e; // ExceptionHandler will extract specific message
    }
}

/**
 * PUT - Update invoice
 */
function handlePut(): void
{
    require_permission('UPDATE_INVOICES');
    require_method('PUT');

    $data = read_json_body();
    validate_required($data, ['id']);

    $db = get_db();
    $auth = require_auth();

    // Lock invoice for update
    $stmt = $db->prepare("
        SELECT * FROM invoices
        WHERE id = ? AND franchise_id = ?
        FOR UPDATE
    ");
    $stmt->execute([$data['id'], $auth['franchise_id']]);
    $invoice = $stmt->fetch();

    if (!$invoice) {
        throw new NotFoundException('Invoice', $data['id']);
    }

    // Business rule: Can't edit paid or voided invoices
    if (in_array($invoice['status'], ['paid', 'voided'])) {
        throw new ConflictException(
            "Cannot edit {$invoice['status']} invoice",
            'INVOICE_' . strtoupper($invoice['status'])
        );
    }

    // Update invoice
    $stmt = $db->prepare("
        UPDATE invoices
        SET notes = ?, updated_at = NOW()
        WHERE id = ? AND franchise_id = ?
    ");
    $stmt->execute([
        $data['notes'] ?? $invoice['notes'],
        $data['id'],
        $auth['franchise_id']
    ]);

    ApiResponse::success(['id' => $data['id']], 'Invoice updated successfully');
}

/**
 * DELETE - Void invoice
 */
function handleDelete(): void
{
    require_permission('VOID_INVOICES');

    $id = $_GET['id'] ?? null;
    if (!$id) {
        throw new ValidationException(['id' => 'Invoice ID required'], 'Validation failed');
    }

    $data = read_json_body();
    $reason = $data['reason'] ?? '';

    if (empty($reason)) {
        throw new ValidationException(['reason' => 'Void reason required'], 'Validation failed');
    }

    $db = get_db();
    $auth = require_auth();

    // Lock invoice
    $stmt = $db->prepare("
        SELECT * FROM invoices
        WHERE id = ? AND franchise_id = ?
        FOR UPDATE
    ");
    $stmt->execute([$id, $auth['franchise_id']]);
    $invoice = $stmt->fetch();

    if (!$invoice) {
        throw new NotFoundException('Invoice', $id);
    }

    // Business rules
    if ($invoice['status'] === 'voided') {
        throw new ConflictException('Invoice already voided', 'ALREADY_VOIDED');
    }

    if ($invoice['status'] === 'paid') {
        throw new ConflictException(
            'Cannot void paid invoice. Please issue a credit note instead.',
            'INVOICE_PAID'
        );
    }

    // Void invoice
    $stmt = $db->prepare("
        UPDATE invoices
        SET status = 'voided', void_reason = ?, voided_at = NOW(), voided_by = ?
        WHERE id = ? AND franchise_id = ?
    ");
    $stmt->execute([$reason, $auth['user_id'], $id, $auth['franchise_id']]);

    ApiResponse::success(['id' => $id], 'Invoice voided successfully');
}

/**
 * Validate invoice data
 *
 * @param array $data
 * @return array Validation errors
 */
function validateInvoiceData(array $data): array
{
    $errors = [];

    // Customer ID
    if (empty($data['customer_id'])) {
        $errors['customer_id'] = 'Customer ID is required';
    } elseif (!is_numeric($data['customer_id'])) {
        $errors['customer_id'] = 'Customer ID must be numeric';
    }

    // Items
    if (empty($data['items']) || !is_array($data['items'])) {
        $errors['items'] = 'At least one item is required';
    } else {
        foreach ($data['items'] as $index => $item) {
            if (empty($item['product_id'])) {
                $errors["items.{$index}.product_id"] = 'Product ID required';
            }
            if (empty($item['quantity']) || $item['quantity'] <= 0) {
                $errors["items.{$index}.quantity"] = 'Quantity must be greater than 0';
            }
            if (!isset($item['unit_price']) || $item['unit_price'] < 0) {
                $errors["items.{$index}.unit_price"] = 'Invalid unit price';
            }
        }
    }

    return $errors;
}

/**
 * Calculate total from items
 *
 * @param array $items
 * @return float
 */
function calculateTotal(array $items): float
{
    $total = 0;
    foreach ($items as $item) {
        $total += ($item['quantity'] ?? 0) * ($item['unit_price'] ?? 0);
    }
    return round($total, 2);
}

/**
 * Generate unique invoice number
 *
 * @param PDO $db
 * @param int $franchiseId
 * @return string
 */
function generateInvoiceNumber(PDO $db, int $franchiseId): string
{
    $prefix = 'INV';
    $year = date('Y');

    $stmt = $db->prepare("
        SELECT MAX(CAST(SUBSTRING(invoice_number, 9) AS UNSIGNED)) as last_num
        FROM invoices
        WHERE franchise_id = ?
        AND invoice_number LIKE ?
    ");
    $stmt->execute([$franchiseId, "{$prefix}{$year}%"]);
    $result = $stmt->fetch();

    $nextNum = ($result['last_num'] ?? 0) + 1;

    return sprintf('%s%s%04d', $prefix, $year, $nextNum);
}
