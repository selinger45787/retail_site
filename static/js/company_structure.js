document.addEventListener('DOMContentLoaded', function() {
    // Инициализация состояния отделов (все развернуты по умолчанию)
    const departments = document.querySelectorAll('.department-section');
    departments.forEach(dept => {
        const content = dept.querySelector('.department-content');
        const header = dept.querySelector('.department-header');
        
        // По умолчанию все отделы развернуты
        content.classList.remove('collapsed');
        header.classList.remove('collapsed');
    });

    // Добавляем интерактивность для узлов организационной структуры
    const orgNodes = document.querySelectorAll('.org-node');
    
    orgNodes.forEach(node => {
        node.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        node.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Анимация появления элементов при прокрутке
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Наблюдаем за элементами с классом fade-in
    document.querySelectorAll('.fade-in').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
});

function toggleDepartment(deptCode) {
    const content = document.getElementById(`content-${deptCode}`);
    const header = document.querySelector(`#dept-${deptCode} .department-header`);
    const icon = header.querySelector('.toggle-icon i');
    
    if (content.classList.contains('collapsed')) {
        // Разворачиваем
        content.classList.remove('collapsed');
        header.classList.remove('collapsed');
        icon.className = 'fas fa-chevron-down';
        
        // Убираем inline стили, чтобы работали CSS правила
        content.style.maxHeight = '';
    } else {
        // Сворачиваем
        content.classList.add('collapsed');
        header.classList.add('collapsed');
        icon.className = 'fas fa-chevron-right';
        
        // Убираем inline стили, чтобы работали CSS правила
        content.style.maxHeight = '';
    }
}

function expandAllDepartments() {
    const departments = document.querySelectorAll('.department-section');
    departments.forEach(dept => {
        const deptCode = dept.id.replace('dept-', '');
        const content = document.getElementById(`content-${deptCode}`);
        const header = dept.querySelector('.department-header');
        const icon = header.querySelector('.toggle-icon i');
        
        if (content.classList.contains('collapsed')) {
            content.classList.remove('collapsed');
            header.classList.remove('collapsed');
            icon.className = 'fas fa-chevron-down';
            content.style.maxHeight = '';
        }
    });
    
    // Показываем уведомление
    showNotification('Всі відділи розгорнуто', 'success');
}

function collapseAllDepartments() {
    const departments = document.querySelectorAll('.department-section');
    departments.forEach(dept => {
        const deptCode = dept.id.replace('dept-', '');
        const content = document.getElementById(`content-${deptCode}`);
        const header = dept.querySelector('.department-header');
        const icon = header.querySelector('.toggle-icon i');
        
        if (!content.classList.contains('collapsed')) {
            content.classList.add('collapsed');
            header.classList.add('collapsed');
            icon.className = 'fas fa-chevron-right';
            content.style.maxHeight = '';
        }
    });
    
    // Показываем уведомление
    showNotification('Всі відділи згорнуто', 'info');
}

function showNotification(message, type = 'info') {
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Автоматически удаляем через 3 секунды
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
} 