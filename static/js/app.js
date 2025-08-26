// 営業管理システム - メインJavaScript

// グローバル変数
const AppConfig = {
    API_BASE_URL: '',
    CHART_COLORS: {
        primary: '#0d6efd',
        success: '#198754',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#0dcaf0',
        secondary: '#6c757d'
    }
};

// ユーティリティ関数
const Utils = {
    // 日付フォーマット
    formatDate: function(date) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        return date.toLocaleDateString('ja-JP');
    },
    
    // 数値フォーマット（通貨）
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('ja-JP', {
            style: 'currency',
            currency: 'JPY',
            maximumFractionDigits: 0
        }).format(amount);
    },
    
    // 数値フォーマット（通常）
    formatNumber: function(number) {
        return new Intl.NumberFormat('ja-JP').format(number);
    },
    
    // パーセンテージフォーマット
    formatPercent: function(value, decimals = 1) {
        return (value || 0).toFixed(decimals) + '%';
    },
    
    // デバウンス関数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // ローカルストレージ操作
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn('LocalStorage write failed:', e);
            }
        },
        
        get: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.warn('LocalStorage read failed:', e);
                return defaultValue;
            }
        },
        
        remove: function(key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.warn('LocalStorage remove failed:', e);
            }
        }
    }
};

// API通信ヘルパー
const API = {
    // GET リクエスト
    get: async function(endpoint) {
        try {
            const response = await fetch(AppConfig.API_BASE_URL + endpoint);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API GET error:', error);
            throw error;
        }
    },
    
    // POST リクエスト
    post: async function(endpoint, data) {
        try {
            const response = await fetch(AppConfig.API_BASE_URL + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API POST error:', error);
            throw error;
        }
    }
};

// 通知システム
const Notification = {
    show: function(message, type = 'info', duration = 5000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // 自動削除
        if (duration > 0) {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, duration);
        }
    },
    
    success: function(message) {
        this.show(message, 'success');
    },
    
    error: function(message) {
        this.show(message, 'danger', 0); // エラーは手動で閉じる
    },
    
    warning: function(message) {
        this.show(message, 'warning');
    },
    
    info: function(message) {
        this.show(message, 'info');
    }
};

// ローディング管理
const Loading = {
    show: function(target = 'body') {
        const targetEl = typeof target === 'string' ? document.querySelector(target) : target;
        const loadingEl = document.createElement('div');
        loadingEl.className = 'loading-overlay';
        loadingEl.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">読み込み中...</span>
                </div>
                <p class="mt-2">データを読み込み中...</p>
            </div>
        `;
        loadingEl.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999;
        `;
        
        if (targetEl) {
            targetEl.style.position = 'relative';
            targetEl.appendChild(loadingEl);
        }
    },
    
    hide: function(target = 'body') {
        const targetEl = typeof target === 'string' ? document.querySelector(target) : target;
        const loadingEl = targetEl ? targetEl.querySelector('.loading-overlay') : null;
        
        if (loadingEl) {
            loadingEl.remove();
        }
    }
};

// フォームバリデーション
const Validation = {
    rules: {
        required: (value) => value && value.toString().trim() !== '',
        email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        number: (value) => !isNaN(value) && isFinite(value),
        minLength: (value, min) => value && value.toString().length >= min,
        maxLength: (value, max) => value && value.toString().length <= max,
        min: (value, min) => parseFloat(value) >= min,
        max: (value, max) => parseFloat(value) <= max
    },
    
    validate: function(formElement) {
        const errors = [];
        const inputs = formElement.querySelectorAll('[data-validate]');
        
        inputs.forEach(input => {
            const rules = input.dataset.validate.split('|');
            const value = input.value;
            
            rules.forEach(rule => {
                const [ruleName, ruleValue] = rule.split(':');
                
                if (this.rules[ruleName]) {
                    const isValid = this.rules[ruleName](value, ruleValue);
                    
                    if (!isValid) {
                        errors.push({
                            input: input,
                            rule: ruleName,
                            message: this.getErrorMessage(ruleName, input.name || input.id, ruleValue)
                        });
                    }
                }
            });
        });
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },
    
    getErrorMessage: function(rule, fieldName, value) {
        const messages = {
            required: `${fieldName}は必須項目です`,
            email: `${fieldName}の形式が正しくありません`,
            number: `${fieldName}は数値で入力してください`,
            minLength: `${fieldName}は${value}文字以上で入力してください`,
            maxLength: `${fieldName}は${value}文字以下で入力してください`,
            min: `${fieldName}は${value}以上で入力してください`,
            max: `${fieldName}は${value}以下で入力してください`
        };
        
        return messages[rule] || `${fieldName}の値が正しくありません`;
    },
    
    showErrors: function(errors) {
        // 既存のエラーメッセージをクリア
        document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        
        // 新しいエラーメッセージを表示
        errors.forEach(error => {
            error.input.classList.add('is-invalid');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = error.message;
            
            error.input.parentNode.appendChild(errorDiv);
        });
    }
};

// チャートヘルパー
const ChartHelper = {
    defaultOptions: {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: 'bottom'
            }
        }
    },
    
    createPieChart: function(ctx, data, options = {}) {
        return new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                ...this.defaultOptions,
                ...options
            }
        });
    },
    
    createBarChart: function(ctx, data, options = {}) {
        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                ...this.defaultOptions,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                ...options
            }
        });
    },
    
    createLineChart: function(ctx, data, options = {}) {
        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                ...this.defaultOptions,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                ...options
            }
        });
    }
};

// イベントリスナーの初期設定
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltipの初期化
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Bootstrap popoverの初期化
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 自動保存機能
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    autoSaveForms.forEach(form => {
        const formId = form.id;
        const debouncedSave = Utils.debounce(() => {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            Utils.storage.set(`autosave_${formId}`, data);
            console.log('Form auto-saved:', formId);
        }, 2000);
        
        form.addEventListener('input', debouncedSave);
        form.addEventListener('change', debouncedSave);
        
        // ページロード時に保存されたデータを復元
        const savedData = Utils.storage.get(`autosave_${formId}`);
        if (savedData) {
            Object.entries(savedData).forEach(([key, value]) => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = value;
                }
            });
        }
    });
    
    // Ajax フォーム送信
    const ajaxForms = document.querySelectorAll('[data-ajax-form]');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const validation = Validation.validate(form);
            if (!validation.isValid) {
                Validation.showErrors(validation.errors);
                return;
            }
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            const endpoint = form.action || form.dataset.endpoint;
            
            try {
                Loading.show(form);
                const result = await API.post(endpoint, data);
                
                if (result.success) {
                    Notification.success(result.message || 'データを保存しました');
                    form.reset();
                } else {
                    Notification.error(result.error || 'エラーが発生しました');
                }
            } catch (error) {
                Notification.error('通信エラーが発生しました');
            } finally {
                Loading.hide(form);
            }
        });
    });
    
    console.log('営業管理システム JavaScript initialized');
});

// グローバルに公開
window.Utils = Utils;
window.API = API;
window.Notification = Notification;
window.Loading = Loading;
window.Validation = Validation;
window.ChartHelper = ChartHelper;
