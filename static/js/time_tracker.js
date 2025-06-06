// Отслеживание времени просмотра материала
class TimeTracker {
    constructor(materialId) {
        this.materialId = materialId;
        this.startTime = Date.now();
        this.lastUpdateTime = this.startTime;
        this.totalTime = 0;
        this.isActive = true;
        this.updateInterval = 10000; // Обновляем каждые 10 секунд
        this.minTimeToSave = 5; // Минимум 5 секунд для сохранения
        
        this.init();
    }
    
    init() {
        // Отслеживаем активность пользователя
        this.addEventListeners();
        
        // Запускаем таймер обновления
        this.timer = setInterval(() => {
            this.updateTime();
        }, this.updateInterval);
        
        // Сохраняем время при закрытии страницы
        window.addEventListener('beforeunload', () => {
            this.saveTime();
        });
        
        // Сохраняем время при потере фокуса
        window.addEventListener('blur', () => {
            this.saveTime();
        });
    }
    
    addEventListeners() {
        // Отслеживаем активность пользователя
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        
        events.forEach(event => {
            document.addEventListener(event, () => {
                this.isActive = true;
            }, true);
        });
        
        // Определяем неактивность
        setInterval(() => {
            this.isActive = false;
        }, 30000); // 30 секунд неактивности
    }
    
    updateTime() {
        if (!this.isActive) return;
        
        const now = Date.now();
        const timeSpent = Math.floor((now - this.lastUpdateTime) / 1000);
        
        if (timeSpent >= this.minTimeToSave) {
            this.totalTime += timeSpent;
            this.saveTime();
        }
        
        this.lastUpdateTime = now;
    }
    
    saveTime() {
        if (this.totalTime < this.minTimeToSave) return;
        
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (!csrfToken) return;
        
        fetch(`/material/${this.materialId}/update_time`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                time_spent: this.totalTime
            })
        }).then(response => {
            if (response.ok) {
                console.log(`Время просмотра обновлено: ${this.totalTime} секунд`);
            }
        }).catch(error => {
            console.error('Помилка при збереженні часу перегляду:', error);
        });
    }
    
    destroy() {
        if (this.timer) {
            clearInterval(this.timer);
        }
        this.saveTime();
    }
}

// Инициализация отслеживания времени для материала
function initTimeTracker(materialId) {
    if (materialId) {
        window.timeTracker = new TimeTracker(materialId);
    }
} 