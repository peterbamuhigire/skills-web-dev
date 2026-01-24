/**
 * API Client with Automatic Error Handling
 *
 * Centralized API client that automatically:
 * - Displays errors via SweetAlert2
 * - Handles validation errors with field highlighting
 * - Manages loading states
 * - Handles network errors gracefully
 */

class ApiClient {
    constructor(baseUrl = './api') {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    /**
     * GET request
     *
     * @param {string} endpoint
     * @param {object} params Query parameters
     * @returns {Promise<object|null>} Response data or null on error
     */
    async get(endpoint, params = {}) {
        const url = new URL(`${this.baseUrl}/${endpoint}`, window.location.origin);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

        return this.request(url.toString(), { method: 'GET' });
    }

    /**
     * POST request
     *
     * @param {string} endpoint
     * @param {object} data Request body
     * @returns {Promise<object|null>}
     */
    async post(endpoint, data = {}) {
        return this.request(`${this.baseUrl}/${endpoint}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     *
     * @param {string} endpoint
     * @param {object} data Request body
     * @returns {Promise<object|null>}
     */
    async put(endpoint, data = {}) {
        return this.request(`${this.baseUrl}/${endpoint}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     *
     * @param {string} endpoint
     * @param {object} data Optional request body
     * @returns {Promise<object|null>}
     */
    async delete(endpoint, data = {}) {
        const options = { method: 'DELETE' };
        if (Object.keys(data).length > 0) {
            options.body = JSON.stringify(data);
        }
        return this.request(`${this.baseUrl}/${endpoint}`, options);
    }

    /**
     * Core request handler
     *
     * @param {string} url
     * @param {object} options Fetch options
     * @returns {Promise<object|null>}
     */
    async request(url, options = {}) {
        try {
            // Add default headers
            options.headers = { ...this.defaultHeaders, ...options.headers };

            // Add CSRF token if available
            const csrfToken = this.getCsrfToken();
            if (csrfToken) {
                options.headers['X-CSRF-Token'] = csrfToken;
            }

            // Add auth token if available
            const authToken = this.getAuthToken();
            if (authToken) {
                options.headers['Authorization'] = `Bearer ${authToken}`;
            }

            const response = await fetch(url, options);
            const data = await response.json();

            if (data.success) {
                return data;
            } else {
                this.handleError(data);
                return null;
            }

        } catch (error) {
            if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                this.handleNetworkError();
            } else if (error instanceof SyntaxError) {
                this.handleJsonError();
            } else {
                this.handleUnknownError(error);
            }
            return null;
        }
    }

    /**
     * Handle API error response
     *
     * @param {object} data Error response
     */
    handleError(data) {
        const error = data.error || {};

        // Validation errors - show with field highlighting
        if (error.type === 'validation_error' && error.details) {
            this.handleValidationError(data.message, error.details);
            return;
        }

        // Other errors - show generic SweetAlert
        Swal.fire({
            icon: 'error',
            title: 'Error',
            html: this.formatErrorMessage(data.message, error),
            footer: error.code ? `<small>Error Code: ${error.code}</small>` : ''
        });
    }

    /**
     * Handle validation errors with field highlighting
     *
     * @param {string} message
     * @param {object} errors Field errors
     */
    handleValidationError(message, errors) {
        // Clear previous validation states
        document.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        document.querySelectorAll('.invalid-feedback').forEach(el => {
            el.remove();
        });

        // Add validation states
        Object.keys(errors).forEach(field => {
            const input = document.getElementById(field) ||
                         document.querySelector(`[name="${field}"]`);

            if (input) {
                input.classList.add('is-invalid');

                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = errors[field];
                input.parentNode.appendChild(feedback);
            }
        });

        // Show SweetAlert with formatted errors
        const errorList = Object.entries(errors)
            .map(([field, msg]) => `<li><strong>${this.formatFieldName(field)}:</strong> ${msg}</li>`)
            .join('');

        Swal.fire({
            icon: 'error',
            title: message || 'Validation Failed',
            html: `<ul style="text-align: left;">${errorList}</ul>`
        });
    }

    /**
     * Handle network errors
     */
    handleNetworkError() {
        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: 'Unable to connect to server. Please check your internet connection.',
            footer: '<small>If the problem persists, contact support.</small>'
        });
    }

    /**
     * Handle JSON parse errors
     */
    handleJsonError() {
        Swal.fire({
            icon: 'error',
            title: 'Server Error',
            text: 'Received invalid response from server.',
            footer: '<small>Please try again or contact support.</small>'
        });
    }

    /**
     * Handle unknown errors
     *
     * @param {Error} error
     */
    handleUnknownError(error) {
        console.error('API Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Unexpected Error',
            text: error.message || 'An unexpected error occurred.',
            footer: '<small>Please try again.</small>'
        });
    }

    /**
     * Format error message for display
     *
     * @param {string} message
     * @param {object} error
     * @returns {string}
     */
    formatErrorMessage(message, error) {
        let html = `<p>${message}</p>`;

        if (error.details && typeof error.details === 'object') {
            const details = Object.values(error.details).join('<br>');
            html += `<div style="margin-top: 10px; font-size: 0.9em;">${details}</div>`;
        }

        return html;
    }

    /**
     * Format field name for display
     *
     * @param {string} field
     * @returns {string}
     */
    formatFieldName(field) {
        return field
            .replace(/([A-Z])/g, ' $1')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase())
            .trim();
    }

    /**
     * Get CSRF token from meta tag or cookie
     *
     * @returns {string|null}
     */
    getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.content : null;
    }

    /**
     * Get auth token from localStorage
     *
     * @returns {string|null}
     */
    getAuthToken() {
        return localStorage.getItem('auth_token');
    }
}

// Helper functions for common SweetAlert patterns

/**
 * Show success message
 *
 * @param {string} message
 * @param {number} timer Auto-close timer in ms
 */
function showSuccess(message, timer = 2000) {
    Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: message,
        timer: timer,
        showConfirmButton: false
    });
}

/**
 * Show error message
 *
 * @param {string} message
 */
function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: message
    });
}

/**
 * Show warning message
 *
 * @param {string} message
 */
function showWarning(message) {
    Swal.fire({
        icon: 'warning',
        title: 'Warning',
        text: message
    });
}

/**
 * Show info message
 *
 * @param {string} message
 */
function showInfo(message) {
    Swal.fire({
        icon: 'info',
        title: 'Info',
        text: message
    });
}

/**
 * Show confirmation dialog
 *
 * @param {string} title
 * @param {string} text
 * @param {string} confirmText
 * @returns {Promise<boolean>}
 */
async function showConfirm(title, text, confirmText = 'Confirm') {
    const result = await Swal.fire({
        icon: 'warning',
        title: title,
        text: text,
        showCancelButton: true,
        confirmButtonText: confirmText,
        confirmButtonColor: '#d63939',
        cancelButtonText: 'Cancel'
    });

    return result.isConfirmed;
}

/**
 * Show loading indicator
 *
 * @param {string} message
 */
function showLoading(message = 'Processing...') {
    Swal.fire({
        title: message,
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    Swal.close();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ApiClient,
        showSuccess,
        showError,
        showWarning,
        showInfo,
        showConfirm,
        showLoading,
        hideLoading
    };
}
