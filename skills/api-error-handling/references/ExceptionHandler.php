<?php

namespace App\Http;

use PDOException;
use Throwable;
use App\Http\Exceptions\{
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    RateLimitException
};

/**
 * Exception Handler
 *
 * Converts all exceptions to standardized API responses.
 * Extracts specific error messages from PDOException.
 */
class ExceptionHandler
{
    /**
     * Handle exception and send appropriate response
     *
     * @param Throwable $e
     */
    public static function handle(Throwable $e): void
    {
        // Log error with context
        self::logError($e);

        // Convert exception to API response
        if ($e instanceof ValidationException) {
            ApiResponse::validationError($e->getErrors(), $e->getMessage());
        } elseif ($e instanceof AuthenticationException) {
            ApiResponse::unauthorized($e->getMessage());
        } elseif ($e instanceof AuthorizationException) {
            ApiResponse::forbidden($e->getPermission());
        } elseif ($e instanceof NotFoundException) {
            ApiResponse::notFound($e->getResource(), $e->getIdentifier());
        } elseif ($e instanceof ConflictException) {
            ApiResponse::conflict($e->getMessage(), $e->getErrorCode());
        } elseif ($e instanceof RateLimitException) {
            ApiResponse::rateLimited($e->getRetryAfter());
        } elseif ($e instanceof PDOException) {
            self::handlePDOException($e);
        } else {
            self::handleGenericException($e);
        }
    }

    /**
     * Handle PDOException with specific message extraction
     *
     * @param PDOException $e
     */
    private static function handlePDOException(PDOException $e): void
    {
        $sqlState = $e->errorInfo[0] ?? '';
        $errorCode = $e->errorInfo[1] ?? 0;
        $message = $e->getMessage();

        // SQLSTATE 45000: User-defined exception (triggers/procedures)
        if ($sqlState === '45000') {
            $extracted = self::extractTriggerMessage($message);
            ApiResponse::conflict($extracted['message'], $extracted['code']);
            return;
        }

        // SQLSTATE 23000: Integrity constraint violation
        if ($sqlState === '23000') {
            // Duplicate entry
            if (stripos($message, 'Duplicate entry') !== false) {
                $extracted = self::extractDuplicateMessage($message);
                ApiResponse::conflict($extracted, 'DUPLICATE_ENTRY');
                return;
            }

            // Foreign key constraint
            if (stripos($message, 'foreign key constraint') !== false ||
                stripos($message, 'Cannot add or update a child row') !== false) {
                ApiResponse::conflict(
                    'Referenced record does not exist',
                    'FOREIGN_KEY_VIOLATION'
                );
                return;
            }

            // Foreign key delete constraint
            if (stripos($message, 'Cannot delete or update a parent row') !== false) {
                $extracted = self::extractForeignKeyDeleteMessage($message);
                ApiResponse::conflict($extracted, 'FOREIGN_KEY_DELETE');
                return;
            }

            // Generic integrity violation
            ApiResponse::conflict(
                'Data integrity violation',
                'INTEGRITY_VIOLATION'
            );
            return;
        }

        // SQLSTATE 40001: Deadlock
        if ($sqlState === '40001' || stripos($message, 'Deadlock') !== false) {
            ApiResponse::serviceUnavailable('Database conflict. Please try again.');
            return;
        }

        // SQLSTATE 42000: Syntax error or access violation
        if ($sqlState === '42000') {
            self::logError($e, 'SQL syntax error');
            ApiResponse::serverError('Database query error');
            return;
        }

        // SQLSTATE 08xxx: Connection errors
        if (substr($sqlState, 0, 2) === '08') {
            ApiResponse::serviceUnavailable('Database connection error');
            return;
        }

        // Generic database error
        self::logError($e, 'Unhandled PDOException');
        ApiResponse::serverError('Database error occurred');
    }

    /**
     * Extract message from SQLSTATE 45000 (trigger)
     *
     * Example: "SQLSTATE[45000]: <<1>>: 1644 Overpayment not allowed"
     * Extracted: "Overpayment not allowed"
     *
     * @param string $message
     * @return array
     */
    private static function extractTriggerMessage(string $message): array
    {
        // Pattern: SQLSTATE[45000]: <<1>>: 1644 [Message]
        if (preg_match('/1644\s+(.+?)(?:\s*$|\\\\n)/', $message, $matches)) {
            $extracted = trim($matches[1]);
            $code = strtoupper(str_replace(' ', '_', $extracted));

            return [
                'message' => $extracted,
                'code' => $code
            ];
        }

        // Fallback
        return [
            'message' => 'Business rule violation',
            'code' => 'BUSINESS_RULE_VIOLATION'
        ];
    }

    /**
     * Extract duplicate entry message
     *
     * Example: "Duplicate entry 'john@example.com' for key 'uk_email_franchise'"
     * Extracted: "A record with this Email already exists: 'john@example.com'"
     *
     * @param string $message
     * @return string
     */
    private static function extractDuplicateMessage(string $message): string
    {
        if (preg_match("/Duplicate entry '([^']+)' for key '([^']+)'/", $message, $matches)) {
            $value = $matches[1];
            $key = $matches[2];

            // Extract field name from key (uk_email_franchise -> Email)
            $field = self::extractFieldFromKey($key);

            return "A record with this {$field} already exists: '{$value}'";
        }

        return 'A record with these values already exists';
    }

    /**
     * Extract foreign key delete message
     *
     * Example: "Cannot delete or update a parent row: a foreign key constraint fails
     *           (`db`.`orders`, CONSTRAINT `fk_customer` FOREIGN KEY (`customer_id`)...)"
     * Extracted: "Referenced Customer does not exist or cannot be deleted"
     *
     * @param string $message
     * @return string
     */
    private static function extractForeignKeyDeleteMessage(string $message): string
    {
        if (preg_match('/CONSTRAINT `fk_(\w+)`/', $message, $matches)) {
            $entity = ucfirst($matches[1]);
            return "Cannot delete {$entity} because other records depend on it";
        }

        return 'Cannot delete record because other records depend on it';
    }

    /**
     * Extract field name from constraint key
     *
     * Examples:
     *   uk_email_franchise -> Email
     *   uk_phone -> Phone
     *   idx_username -> Username
     *
     * @param string $key
     * @return string
     */
    private static function extractFieldFromKey(string $key): string
    {
        // Remove prefixes (uk_, idx_, fk_)
        $field = preg_replace('/^(uk|idx|fk)_/', '', $key);

        // Remove franchise/tenant suffixes
        $field = preg_replace('/_(franchise|tenant)$/', '', $field);

        // Convert underscores to spaces and capitalize
        $field = str_replace('_', ' ', $field);
        $field = ucwords($field);

        return $field;
    }

    /**
     * Handle generic exception
     *
     * @param Throwable $e
     */
    private static function handleGenericException(Throwable $e): void
    {
        $isDevelopment = defined('APP_DEBUG') && APP_DEBUG === true;

        if ($isDevelopment) {
            ApiResponse::serverError(
                $e->getMessage() . ' in ' . $e->getFile() . ':' . $e->getLine()
            );
        } else {
            ApiResponse::serverError('An unexpected error occurred');
        }
    }

    /**
     * Log error with context
     *
     * @param Throwable $e
     * @param string $type
     */
    private static function logError(Throwable $e, string $type = 'Exception'): void
    {
        $requestId = $_SERVER['HTTP_X_REQUEST_ID'] ?? $_SERVER['REQUEST_ID'] ?? 'req_' . bin2hex(random_bytes(8));

        $context = [
            'user_id' => $_SESSION['user_id'] ?? null,
            'franchise_id' => $_SESSION['franchise_id'] ?? null,
            'url' => $_SERVER['REQUEST_URI'] ?? '',
            'method' => $_SERVER['REQUEST_METHOD'] ?? '',
            'ip' => $_SERVER['REMOTE_ADDR'] ?? ''
        ];

        $logMessage = sprintf(
            "[%s] %s: %s in %s:%d\nContext: %s",
            $requestId,
            get_class($e),
            $e->getMessage(),
            $e->getFile(),
            $e->getLine(),
            json_encode($context)
        );

        error_log($logMessage);

        // In development, also log stack trace
        if (defined('APP_DEBUG') && APP_DEBUG === true) {
            error_log("Stack trace:\n" . $e->getTraceAsString());
        }
    }
}
