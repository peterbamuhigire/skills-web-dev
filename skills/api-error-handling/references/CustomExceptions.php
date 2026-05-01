<?php

namespace App\Http\Exceptions;

use Exception;

/**
 * Validation Exception (422)
 *
 * Used for validation errors with field-specific messages
 */
class ValidationException extends Exception
{
    private array $errors;

    public function __construct(array $errors, string $message = 'Validation failed')
    {
        parent::__construct($message);
        $this->errors = $errors;
    }

    public function getErrors(): array
    {
        return $this->errors;
    }
}

/**
 * Authentication Exception (401)
 *
 * Used when authentication is required or fails
 */
class AuthenticationException extends Exception
{
    private string $errorCode;

    public function __construct(string $message = 'Authentication required', string $errorCode = 'UNAUTHORIZED')
    {
        parent::__construct($message);
        $this->errorCode = $errorCode;
    }

    public function getErrorCode(): string
    {
        return $this->errorCode;
    }
}

/**
 * Authorization Exception (403)
 *
 * Used when user lacks required permission
 */
class AuthorizationException extends Exception
{
    private string $permission;

    public function __construct(string $permission = '', string $message = '')
    {
        $this->permission = $permission;

        $finalMessage = $message ?: ($permission
            ? "Permission required: {$permission}"
            : "You do not have permission to perform this action");

        parent::__construct($finalMessage);
    }

    public function getPermission(): string
    {
        return $this->permission;
    }
}

/**
 * Not Found Exception (404)
 *
 * Used when a requested resource doesn't exist
 */
class NotFoundException extends Exception
{
    private string $resource;
    private $identifier;

    public function __construct(string $resource, $identifier = null, string $message = '')
    {
        $this->resource = $resource;
        $this->identifier = $identifier;

        $finalMessage = $message ?: ($identifier
            ? "{$resource} with identifier '{$identifier}' not found"
            : "{$resource} not found");

        parent::__construct($finalMessage);
    }

    public function getResource(): string
    {
        return $this->resource;
    }

    public function getIdentifier()
    {
        return $this->identifier;
    }
}

/**
 * Conflict Exception (409)
 *
 * Used for business rule violations and conflicts
 */
class ConflictException extends Exception
{
    private string $errorCode;

    public function __construct(string $message, string $errorCode = 'CONFLICT')
    {
        parent::__construct($message);
        $this->errorCode = $errorCode;
    }

    public function getErrorCode(): string
    {
        return $this->errorCode;
    }
}

/**
 * Rate Limit Exception (429)
 *
 * Used when rate limits are exceeded
 */
class RateLimitException extends Exception
{
    private int $retryAfter;

    public function __construct(int $retryAfter = 60, string $message = '')
    {
        $this->retryAfter = $retryAfter;

        $finalMessage = $message ?: "Too many requests. Please try again in {$retryAfter} seconds.";

        parent::__construct($finalMessage);
    }

    public function getRetryAfter(): int
    {
        return $this->retryAfter;
    }
}

/**
 * Bad Request Exception (400)
 *
 * Used for malformed requests, invalid JSON, etc.
 */
class BadRequestException extends Exception
{
    private string $errorCode;

    public function __construct(string $message = 'Bad request', string $errorCode = 'BAD_REQUEST')
    {
        parent::__construct($message);
        $this->errorCode = $errorCode;
    }

    public function getErrorCode(): string
    {
        return $this->errorCode;
    }
}
