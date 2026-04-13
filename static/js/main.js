/**
 * SFU Food Pantry Management System
 * Main JavaScript Module
 */

// ============================================
// Utility Functions
// ============================================

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type: success, error, warning, info
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getIconForType(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

/**
 * Format date to readable format
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date
 */
function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return date.toLocaleDateString('en-US', options);
}

/**
 * Format currency
 * @param {number} value - Value to format
 * @returns {string} Formatted currency
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

/**
 * Debounce function for search inputs
 * @param {function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Confirm dialog
 * @param {string} message - Confirmation message
 * @param {function} onConfirm - Callback on confirm
 * @param {function} onCancel - Callback on cancel
 */
function confirmDialog(message, onConfirm, onCancel) {
    if (confirm(message)) {
        onConfirm();
    } else if (onCancel) {
        onCancel();
    }
}

/**
 * Check if element is in viewport
 * @param {Element} element - Element to check
 * @returns {boolean} Whether element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// ============================================
// Form Utilities
// ============================================

/**
 * Validate email
 * @param {string} email - Email to validate
 * @returns {boolean} Whether email is valid
 */
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Get form data as object
 * @param {HTMLFormElement} form - Form element
 * @returns {Object} Form data
 */
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (data[key]) {
            if (!Array.isArray(data[key])) {
                data[key] = [data[key]];
            }
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }
    
    return data;
}

/**
 * Validate required fields
 * @param {Object} data - Data to validate
 * @param {Array} requiredFields - Required field names
 * @returns {Object} Validation result
 */
function validateRequired(data, requiredFields) {
    const errors = {};
    
    requiredFields.forEach(field => {
        if (!data[field] || data[field].toString().trim() === '') {
            errors[field] = `${field} is required`;
        }
    });
    
    return {
        isValid: Object.keys(errors).length === 0,
        errors: errors
    };
}

/**
 * Display form errors
 * @param {Object} errors - Error object
 */
function displayFormErrors(errors) {
    Object.keys(errors).forEach(field => {
        const input = document.querySelector(`[name="${field}"]`);
        if (input) {
            input.classList.add('error');
            const errorMsg = document.createElement('div');
            errorMsg.className = 'form-error';
            errorMsg.textContent = errors[field];
            input.parentElement.appendChild(errorMsg);
        }
    });
}

/**
 * Clear form errors
 * @param {HTMLFormElement} form - Form element
 */
function clearFormErrors(form) {
    form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    form.querySelectorAll('.form-error').forEach(el => el.remove());
}

// ============================================
// Table Utilities
// ============================================

/**
 * Sort table by column
 * @param {string} columnIndex - Column index
 * @param {HTMLTableElement} table - Table element
 */
function sortTable(columnIndex, table) {
    let rows = Array.from(table.querySelectorAll('tbody tr'));
    let isAsc = !table.dataset.sortAsc;
    
    rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent.trim();
        const bVal = b.cells[columnIndex].textContent.trim();
        
        // Try numeric sort
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAsc ? aNum - bNum : bNum - aNum;
        }
        
        // String sort
        return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
    
    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));
    
    table.dataset.sortAsc = isAsc;
}

/**
 * Filter table by text
 * @param {string} searchText - Text to search
 * @param {HTMLTableElement} table - Table element
 */
function filterTable(searchText, table) {
    const rows = table.querySelectorAll('tbody tr');
    const search = searchText.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(search) ? '' : 'none';
    });
}

/**
 * Export table to CSV
 * @param {HTMLTableElement} table - Table element
 * @param {string} filename - Output filename
 */
function exportTableToCSV(table, filename = 'export.csv') {
    let csv = [];
    
    // Get headers
    const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
    csv.push(headers.join(','));
    
    // Get rows
    table.querySelectorAll('tbody tr').forEach(row => {
        const cells = Array.from(row.querySelectorAll('td')).map(td => {
            let text = td.textContent.trim();
            // Escape quotes in CSV
            text = text.replace(/"/g, '""');
            // Wrap in quotes if contains comma
            if (text.includes(',')) {
                text = `"${text}"`;
            }
            return text;
        });
        csv.push(cells.join(','));
    });
    
    downloadFile(csv.join('\n'), filename, 'text/csv');
}

/**
 * Download file
 * @param {string} content - File content
 * @param {string} filename - Output filename
 * @param {string} type - MIME type
 */
function downloadFile(content, filename, type = 'text/plain') {
    const element = document.createElement('a');
    element.setAttribute('href', `data:${type};charset=utf-8,${encodeURIComponent(content)}`);
    element.setAttribute('download', filename);
    element.style.display = 'none';
    
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// ============================================
// DOM Ready & Initialization
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('SFU Food Pantry Management System - Ready');
    
    // Close alert messages
    document.querySelectorAll('.alert .close').forEach(btn => {
        btn.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});

// ============================================
// AJAX Utilities
// ============================================

/**
 * Generic AJAX request
 * @param {string} url - Request URL
 * @param {Object} options - Request options
 * @returns {Promise} Response promise
 */
function ajax(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };
    
    return fetch(url, defaultOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX error:', error);
            showToast('An error occurred. Please try again.', 'error');
            throw error;
        });
}

/**
 * GET request
 * @param {string} url - Request URL
 * @returns {Promise} Response promise
 */
function get(url) {
    return ajax(url, { method: 'GET' });
}

/**
 * POST request
 * @param {string} url - Request URL
 * @param {Object} data - Request data
 * @returns {Promise} Response promise
 */
function post(url, data) {
    return ajax(url, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * PUT request
 * @param {string} url - Request URL
 * @param {Object} data - Request data
 * @returns {Promise} Response promise
 */
function put(url, data) {
    return ajax(url, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

/**
 * DELETE request
 * @param {string} url - Request URL
 * @returns {Promise} Response promise
 */
function deleteRequest(url) {
    return ajax(url, { method: 'DELETE' });
}

// ============================================
// Export for use in modules
// ============================================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showToast,
        formatDate,
        formatCurrency,
        debounce,
        confirmDialog,
        validateEmail,
        getFormData,
        validateRequired,
        sortTable,
        filterTable,
        exportTableToCSV,
        ajax,
        get,
        post,
        put,
        deleteRequest
    };
}
