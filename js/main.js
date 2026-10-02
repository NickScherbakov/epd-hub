/**
 * EPD-Hub Frontend Main JavaScript
 * Handles API communication, UI interactions, and status checking
 */

// ==================== Configuration ====================
const API_BASE_URL = 'http://localhost:8000';
const STATUS_CHECK_INTERVAL = 30000; // 30 seconds

// ==================== DOM Elements ====================
const apiStatusWidget = document.getElementById('api-status');
const statusDot = document.querySelector('.status-dot');
const statusText = document.querySelector('.status-text');
const statusMessage = document.getElementById('status-message');
const statusInfo = document.querySelector('.status-info');

// ==================== API Communication ====================

/**
 * Check if the API is running and update the UI accordingly
 */
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const data = await response.json();
            updateStatusUI(true, data);
            return true;
        } else {
            updateStatusUI(false, null);
            return false;
        }
    } catch (error) {
        console.warn('API Status Check Failed:', error.message);
        updateStatusUI(false, null);
        return false;
    }
}

/**
 * Update the API status widget UI
 */
function updateStatusUI(isOnline, data) {
    if (isOnline) {
        statusDot.style.backgroundColor = '#2e7d32';
        statusDot.style.animation = 'pulse 2s infinite';
        statusText.textContent = 'API Online';
        statusMessage.innerHTML = `
            <strong>✅ API Status: Online</strong><br>
            Service: ${data.service}<br>
            Version: ${data.version}<br>
            Last checked: ${new Date().toLocaleTimeString()}
        `;
        apiStatusWidget.style.backgroundColor = '#e8f5e9';
    } else {
        statusDot.style.backgroundColor = '#ff6b35';
        statusDot.style.animation = 'pulse 1s infinite';
        statusText.textContent = 'API Offline';
        statusMessage.innerHTML = `
            <strong>⚠️ API Status: Offline</strong><br>
            The server is not responding.<br>
            Last checked: ${new Date().toLocaleTimeString()}<br>
            <small>Make sure the server is running on ${API_BASE_URL}</small>
        `;
        apiStatusWidget.style.backgroundColor = '#ffebee';
    }
}

// ==================== Event Listeners ====================

/**
 * Toggle status info visibility
 */
apiStatusWidget.addEventListener('click', function (e) {
    e.stopPropagation();
    const isVisible = statusInfo.style.display === 'block';
    statusInfo.style.display = isVisible ? 'none' : 'block';
});

/**
 * Close status info when clicking outside
 */
document.addEventListener('click', function () {
    statusInfo.style.display = 'none';
});

/**
 * Smooth scroll for navigation links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const target = document.getElementById(targetId);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

/**
 * Button click handlers
 */
document.querySelectorAll('.btn-primary, .btn-secondary').forEach(btn => {
    btn.addEventListener('click', function () {
        const btnText = this.textContent.trim();
        
        if (btnText.includes('Начать')) {
            console.log('Starting development...');
            alert('📖 Перейдите на https://github.com/NickScherbakov/epd-hub для начала разработки');
        } else if (btnText.includes('документацию')) {
            console.log('Opening documentation...');
            alert('📚 Документация доступна на https://github.com/NickScherbakov/epd-hub');
        } else if (btnText.includes('Вход')) {
            console.log('Redirecting to login...');
            alert('🔐 Функция входа будет добавлена в следующей версии');
        }
    });
});

// ==================== Intersection Observer for Animations ====================

/**
 * Animate elements when they come into view
 */
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

/**
 * Observe all feature cards, audience cards, and tech items
 */
document.querySelectorAll('.feature-card, .audience-card, .tech-item, .step').forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(element);
});

// ==================== Keyboard Navigation ====================

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function (e) {
    // Alt + D: Open documentation
    if (e.altKey && e.key === 'd') {
        window.open('https://github.com/NickScherbakov/epd-hub', '_blank');
    }

    // Alt + A: Open API docs
    if (e.altKey && e.key === 'a') {
        window.open(`${API_BASE_URL}/docs`, '_blank');
    }

    // Alt + G: Open GitHub
    if (e.altKey && e.key === 'g') {
        window.open('https://github.com/NickScherbakov/epd-hub', '_blank');
    }
});

// ==================== Performance Monitoring ====================

/**
 * Monitor API response time
 */
async function monitorAPIPerformance() {
    const startTime = performance.now();
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const endTime = performance.now();
        const responseTime = (endTime - startTime).toFixed(2);
        
        console.log(`API Response Time: ${responseTime}ms`);
        
        if (responseTime > 1000) {
            console.warn('API Response Time is slow:', responseTime + 'ms');
        }
    } catch (error) {
        console.error('Performance Monitoring Error:', error);
    }
}

// ==================== Initialization ====================

/**
 * Initialize the application
 */
function initialize() {
    console.log('🚀 EPD-Hub Frontend Initializing...');

    // Check API status immediately
    checkAPIStatus();

    // Set up periodic API status checks
    setInterval(checkAPIStatus, STATUS_CHECK_INTERVAL);

    // Monitor performance
    setInterval(monitorAPIPerformance, 60000); // Every minute

    // Log page load time
    window.addEventListener('load', () => {
        const pageLoadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`Page Load Time: ${pageLoadTime}ms`);
    });

    console.log('✅ EPD-Hub Frontend Initialized');
    console.log('Available Keyboard Shortcuts:');
    console.log('  Alt + D: Open Documentation');
    console.log('  Alt + A: Open API Docs');
    console.log('  Alt + G: Open GitHub Repository');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// ==================== Service Worker Registration ====================

/**
 * Register service worker for offline support (if available)
 */
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js').catch(err => {
            console.log('ServiceWorker registration failed: ', err);
        });
    });
}

// ==================== Error Handling ====================

/**
 * Global error handler
 */
window.addEventListener('error', (event) => {
    console.error('Global Error:', event.error);
});

/**
 * Unhandled promise rejection
 */
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
});

// ==================== Utility Functions ====================

/**
 * Format date for display
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
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
 * Log analytics event (placeholder for future implementation)
 */
function logAnalyticsEvent(eventName, eventData) {
    console.log(`📊 Event: ${eventName}`, eventData);
    // TODO: Integrate with analytics service
}

// ==================== Export Functions ====================

// Make functions available globally for debugging
window.EPDHub = {
    checkAPIStatus,
    updateStatusUI,
    formatDate,
    debounce,
    logAnalyticsEvent,
    API_BASE_URL
};

console.log('💡 Tip: Access EPD-Hub functions via window.EPDHub');
