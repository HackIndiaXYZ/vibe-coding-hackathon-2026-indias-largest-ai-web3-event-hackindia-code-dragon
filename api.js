/**
 * Natsuki-Ren AI System - Complete Features API
 * Handles all 6 feature modules with Firebase integration
 */

class NatsukiRenAPI {
    constructor() {
        this.baseURL = '/api';
        this.authToken = null;
    }

    async getAuthToken() {
        try {
            if (window._fbAuth && window._fbAuth.currentUser) {
                return await window._fbAuth.currentUser.getIdToken();
            }
        } catch (e) {
            console.warn('Failed to get auth token:', e);
        }
        return null;
    }

    async request(endpoint, method = 'GET', data = null) {
        const token = await this.getAuthToken();
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const options = {
            method,
            headers
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'API request failed');
            }

            return result;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // ============ DASHBOARD ============
    async getDashboard() {
        return this.request('/dashboard');
    }

    // ============ STUDY HUB ============
    async createNote(title, content, subject) {
        return this.request('/notes', 'POST', { title, content, subject });
    }

    async getNotes() {
        return this.request('/notes');
    }

    async createQuiz(title, questions, subject) {
        return this.request('/quizzes', 'POST', { title, questions, subject });
    }

    async getQuizzes() {
        return this.request('/quizzes');
    }

    async completeQuiz(quizId, score) {
        return this.request(`/quizzes/${quizId}/complete`, 'POST', { score });
    }

    async createFlashcard(question, answer, category) {
        return this.request('/flashcards', 'POST', { question, answer, category });
    }

    async getFlashcards() {
        return this.request('/flashcards');
    }

    async createStudyPlan(title, schedule, duration) {
        return this.request('/study-plans', 'POST', { title, schedule, duration });
    }

    async getStudyPlans() {
        return this.request('/study-plans');
    }

    // ============ CODE HUB ============
    async saveCodeSnippet(language, code, description) {
        return this.request('/code-snippets', 'POST', { language, code, description });
    }

    async getCodeSnippets() {
        return this.request('/code-snippets');
    }

    // ============ AI TOOLS ============
    async analyzeImage(file) {
        const formData = new FormData();
        formData.append('file', file);
        return this._requestFormData('/analyze-image', 'POST', formData);
    }

    async performOCR(file) {
        const formData = new FormData();
        formData.append('file', file);
        return this._requestFormData('/ocr', 'POST', formData);
    }

    async reviewResume(resumeText) {
        return this.request('/resume-review', 'POST', { resume: resumeText });
    }

    async summarizePDF(content) {
        return this.request('/pdf-summary', 'POST', { content });
    }

    async _requestFormData(endpoint, method = 'POST', formData) {
        const token = await this.getAuthToken();
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method,
                headers,
                body: formData
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'API request failed');
            }

            return result;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // ============ COMMUNITY ============
    async shareChat(title, messages, description) {
        return this.request('/share-chat', 'POST', { title, messages, description });
    }

    async getSharedChats() {
        return this.request('/shared-chats');
    }

    async createPublicPrompt(title, content, category) {
        return this.request('/prompts', 'POST', { title, content, category });
    }

    async getPublicPrompts() {
        return this.request('/prompts');
    }

    async addMarketplaceItem(title, description, price, category) {
        return this.request('/marketplace', 'POST', { title, description, price, category });
    }

    async getMarketplace() {
        return this.request('/marketplace');
    }

    async getLeaderboard(limit = 50) {
        return this.request(`/leaderboard?limit=${limit}`);
    }

    // ============ GAMIFICATION ============
    async addXP(xpAmount) {
        return this.request('/user/xp', 'POST', { xp: xpAmount });
    }

    async addBadge(badgeName) {
        return this.request('/user/badge', 'POST', { badge: badgeName });
    }

    async createDailyChallenge(title, description, rewardXp = 50) {
        return this.request('/daily-challenges', 'POST', { title, description, reward_xp: rewardXp });
    }

    async getDailyChallenges() {
        return this.request('/daily-challenges');
    }

    async completeDailyChallenge(challengeId) {
        return this.request(`/daily-challenges/${challengeId}/complete`, 'POST');
    }
}

// Global API instance
window.NatsukiAPI = new NatsukiRenAPI();

/**
 * UI Handler for all features
 */
class NatsukiRenUI {
    constructor() {
        this.currentView = 'chat';
    }

    // Switch between views
    switchView(viewName) {
        this.currentView = viewName;
        this.hideAllViews();
        document.getElementById(`view-${viewName}`)?.style.display = 'block';
        this.updateNavigation(viewName);
    }

    hideAllViews() {
        document.querySelectorAll('[id^="view-"]').forEach(el => {
            el.style.display = 'none';
        });
    }

    updateNavigation(active) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-view="${active}"]`)?.classList.add('active');
    }

    // Toast notification
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    // Loading spinner
    showLoading(element) {
        element.innerHTML = '<div class="spinner"></div>';
    }

    // Dashboard display
    async displayDashboard() {
        try {
            const data = await window.NatsukiAPI.getDashboard();
            const dashboard = document.getElementById('dashboard-stats');
            if (dashboard) {
                dashboard.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-label">Total Chats</div>
                        <div class="stat-value">${data.total_chats || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Messages Sent</div>
                        <div class="stat-value">${data.messages_sent || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Daily Streak</div>
                        <div class="stat-value">${data.daily_streak || 0} [FIRE]</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">AI Usage</div>
                        <div class="stat-value">${data.ai_usage || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Level</div>
                        <div class="stat-value">${data.level || 1}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">XP</div>
                        <div class="stat-value">${data.xp || 0}</div>
                    </div>
                `;
            }
        } catch (error) {
            this.showToast(`Error loading dashboard: ${error.message}`, 'error');
        }
    }
}

// Global UI instance
window.NatsukiUI = new NatsukiRenUI();

console.log('[OK] Natsuki-Ren Features API loaded');
