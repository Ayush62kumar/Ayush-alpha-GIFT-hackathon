// ALPHA Finance API Client
// Handles all communication with the FastAPI backend

class AlphaAPI {
    constructor(baseURL = 'http://127.0.0.1:8001') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('alpha_token') || null;
        this.user = JSON.parse(localStorage.getItem('alpha_user') || 'null');
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add authorization header if token exists
        if (this.token) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Authentication methods
    async login(username) {
        try {
            const data = await this.request(`/auth/login?username=${encodeURIComponent(username)}`, {
                method: 'POST'
            });

            this.token = data.token;
            this.user = { id: data.user_id, username };
            
            localStorage.setItem('alpha_token', this.token);
            localStorage.setItem('alpha_user', JSON.stringify(this.user));

            return data;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    async register(username, email) {
        try {
            const data = await this.request(`/auth/register?username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}`, {
                method: 'POST'
            });

            this.token = data.token;
            this.user = { id: data.user_id, username, email };
            
            localStorage.setItem('alpha_token', this.token);
            localStorage.setItem('alpha_user', JSON.stringify(this.user));

            return data;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('alpha_token');
        localStorage.removeItem('alpha_user');
    }

    // Learning Modules methods
    async getAllModules() {
        return this.request('/modules');
    }

    async getModulesByLevel(level) {
        return this.request(`/modules/${level}`);
    }

    async getModuleDetails(moduleId) {
        return this.request(`/modules/${moduleId}/details`);
    }

    // Progress Tracking methods
    async getUserProgress(userId = this.user?.id) {
        if (!userId) throw new Error('User ID required');
        return this.request(`/progress/${userId}`);
    }

    async updateModuleProgress(moduleId, progress, timeSpent = 0, checkpoint = null) {
        if (!this.user) throw new Error('User not authenticated');
        
        return this.request(`/progress/${this.user.id}/${moduleId}`, {
            method: 'POST',
            body: JSON.stringify({
                progress,
                time_spent: timeSpent,
                checkpoint
            })
        });
    }

    // Trading Simulator methods
    async initializeSimulator(level = 'beginner') {
        if (!this.user) throw new Error('User not authenticated');
        
        return this.request(`/simulator/${this.user.id}/initialize`, {
            method: 'POST',
            body: JSON.stringify({ level })
        });
    }

    async getSimulatorState() {
        if (!this.user) throw new Error('User not authenticated');
        
        return this.request(`/simulator/${this.user.id}/state`);
    }

    async executeTrade(symbol, action, quantity, orderType = 'market', limitPrice = null) {
        if (!this.user) throw new Error('User not authenticated');
        
        return this.request(`/simulator/${this.user.id}/trade`, {
            method: 'POST',
            body: JSON.stringify({
                symbol,
                action,
                quantity,
                order_type: orderType,
                limit_price: limitPrice
            })
        });
    }

    async getTradeHistory(limit = 50) {
        if (!this.user) throw new Error('User not authenticated');
        
        return this.request(`/simulator/${this.user.id}/trades?limit=${limit}`);
    }

    async updateStockPrices() {
        if (!this.user) throw new Error('User not authenticated');
        
        return this.request(`/simulator/${this.user.id}/update-prices`, {
            method: 'POST'
        });
    }

    // User Management methods
    async getUserProfile(userId = this.user?.id) {
        if (!userId) throw new Error('User ID required');
        return this.request(`/user/${userId}`);
    }

    async updateUserLevel(level) {
        if (!this.user) throw new Error('User not authenticated');
        
        return this.request(`/user/${this.user.id}/level`, {
            method: 'PUT',
            body: JSON.stringify({ level })
        });
    }

    // Analytics methods
    async getPlatformAnalytics() {
        return this.request('/analytics/overview');
    }

    // Utility methods
    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    getCurrentUser() {
        return this.user;
    }

    async healthCheck() {
        return this.request('/');
    }
}

// Create global API instance
const alphaAPI = new AlphaAPI();

// Export for use in other scripts
window.alphaAPI = alphaAPI;

// Auto-initialize user session on page load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Check if backend is available
        await alphaAPI.healthCheck();
        console.log('✅ ALPHA Backend connected successfully');
        
        // Initialize user session if token exists
        if (alphaAPI.isAuthenticated()) {
            console.log('👤 User session restored:', alphaAPI.getCurrentUser());
        }
    } catch (error) {
        console.warn('⚠️ ALPHA Backend not available:', error.message);
        console.log('🔄 Falling back to localStorage mode');
    }
});

// Helper functions for common operations
window.AlphaUtils = {
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Format percentage
    formatPercentage(value) {
        return `${value.toFixed(1)}%`;
    },

    // Format time
    formatTime(minutes) {
        if (minutes < 60) {
            return `${minutes}m`;
        } else {
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return `${hours}h ${mins}m`;
        }
    },

    // Show notification
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alpha-notification alpha-notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? 'var(--green)' : type === 'error' ? 'var(--red)' : 'var(--amber)'};
            color: var(--bg);
            border-radius: 8px;
            font-family: var(--mono);
            font-size: 12px;
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    // Handle API errors
    handleAPIError(error, context = '') {
        console.error(`API Error ${context}:`, error);
        
        let message = 'An error occurred';
        if (error.message.includes('User not authenticated')) {
            message = 'Please login to continue';
        } else if (error.message.includes('Simulator not initialized')) {
            message = 'Please initialize the trading simulator first';
        } else if (error.message.includes('Insufficient')) {
            message = 'Insufficient funds or shares';
        } else {
            message = error.message;
        }
        
        this.showNotification(message, 'error');
    },

    // Sync progress with backend
    async syncProgressWithBackend() {
        if (!alphaAPI.isAuthenticated()) {
            console.log('User not authenticated, skipping backend sync');
            return;
        }

        try {
            // Get progress from localStorage
            const localProgress = localStorage.getItem('learningModule_progress');
            if (!localProgress) return;

            const progressData = JSON.parse(localProgress);
            
            // Sync each module progress with backend
            for (const [moduleId, progress] of Object.entries(progressData)) {
                try {
                    await alphaAPI.updateModuleProgress(
                        moduleId,
                        progress.progress,
                        progress.timeSpent || 0
                    );
                    console.log(`✅ Synced progress for ${moduleId}`);
                } catch (error) {
                    console.warn(`⚠️ Failed to sync ${moduleId}:`, error.message);
                }
            }
            
            this.showNotification('Progress synced with backend', 'success');
        } catch (error) {
            this.handleAPIError(error, 'during progress sync');
        }
    },

    // Sync simulator state with backend
    async syncSimulatorWithBackend() {
        if (!alphaAPI.isAuthenticated()) {
            console.log('User not authenticated, skipping simulator sync');
            return;
        }

        try {
            // Get simulator state from localStorage
            const localState = localStorage.getItem('tradingSimulator_state');
            if (!localState) return;

            const stateData = JSON.parse(localState);
            
            // Initialize simulator on backend if not exists
            try {
                await alphaAPI.getSimulatorState();
                console.log('✅ Simulator already exists on backend');
            } catch (error) {
                if (error.message.includes('Simulator not initialized')) {
                    await alphaAPI.initializeSimulator(stateData.level);
                    console.log('✅ Simulator initialized on backend');
                }
            }
            
            this.showNotification('Trading simulator synced', 'success');
        } catch (error) {
            this.handleAPIError(error, 'during simulator sync');
        }
    }
};

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
