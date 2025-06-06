// Перенаправление на редактирование
function editMaterial(materialId) {
    window.location.href = `/material/${materialId}/edit`;
}

let materialToDelete = null;

// Показать модальное окно удаления
function showDeleteModal(materialId) {
    materialToDelete = materialId;
    const modal = document.getElementById('deleteMaterialModal');
    modal.style.display = 'flex';
    setTimeout(() => modal.classList.add('show'), 10);
}

// Закрыть модальное окно
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Удаление материала
function deleteMaterial() {
    if (!materialToDelete) return;

    const confirmBtn = document.getElementById('confirmDeleteBtn');
    const originalText = confirmBtn.textContent;
    
    // Показываем состояние загрузки
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Видаляємо...';

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch(`/material/${materialToDelete}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            csrf_token: csrfToken
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.needs_confirmation) {
            // Показываем модальное окно с зависимостями
            showDependenciesWarning(data);
            resetDeleteButton(confirmBtn, originalText);
        } else if (data.success) {
            window.location.href = data.redirect;
        } else {
            alert(data.error || 'Помилка при видаленні матеріалу');
            resetDeleteButton(confirmBtn, originalText);
        }
        
        closeModal('deleteMaterialModal');
    })
    .catch(error => {
        console.error('Error:', error);
        closeModal('deleteMaterialModal');
        alert('Помилка при видаленні матеріалу');
        resetDeleteButton(confirmBtn, originalText);
    });
}

// Показать модальное окно с предупреждением о зависимостях
function showDependenciesWarning(data) {
    const dependenciesList = document.getElementById('dependenciesList');
    dependenciesList.innerHTML = '';

    // Добавляем информацию о тестах
    if (data.has_test) {
        const testItem = document.createElement('div');
        testItem.className = 'dependency-item';
        testItem.innerHTML = `
            <i class="fas fa-clipboard-list"></i>
            <span>Створений тест для цього матеріалу</span>
        `;
        dependenciesList.appendChild(testItem);
    }

    // Добавляем информацию о назначениях
    if (data.has_active_assignments) {
        const assignmentItem = document.createElement('div');
        assignmentItem.className = 'dependency-item';
        assignmentItem.innerHTML = `
            <i class="fas fa-users"></i>
            <span>Активні призначення користувачам</span>
            <span class="dependency-count">${data.active_assignments_count}</span>
        `;
        dependenciesList.appendChild(assignmentItem);
    }

    // Добавляем информацию о результатах тестов
    if (data.has_test_results) {
        const resultsItem = document.createElement('div');
        resultsItem.className = 'dependency-item';
        resultsItem.innerHTML = `
            <i class="fas fa-chart-bar"></i>
            <span>Результати проходження тестів</span>
            <span class="dependency-count">${data.test_results_count}</span>
        `;
        dependenciesList.appendChild(resultsItem);
    }

    // Показываем модальное окно
    const modal = document.getElementById('dependenciesWarningModal');
    modal.style.display = 'flex';
    setTimeout(() => modal.classList.add('show'), 10);

    // Устанавливаем обработчик для кнопки подтверждения
    const confirmDependentDeleteBtn = document.getElementById('confirmDependentDeleteBtn');
    confirmDependentDeleteBtn.onclick = () => confirmDependentDelete();
}

// Подтверждение удаления с зависимостями
function confirmDependentDelete() {
    const confirmBtn = document.getElementById('confirmDependentDeleteBtn');
    const originalText = confirmBtn.innerHTML;
    
    // Показываем состояние загрузки
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Видаляємо...';

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch(`/material/${materialToDelete}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            csrf_token: csrfToken,
            confirmed: true
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Delete response data:', data);
        if (data.success) {
            // Показываем успешное сообщение перед перенаправлением
            showSuccessMessage('Матеріал успішно видалено!');
            setTimeout(() => {
                window.location.href = data.redirect;
            }, 1500);
        } else {
            alert(data.error || 'Помилка при видаленні матеріалу');
            resetConfirmDependentDeleteButton(confirmBtn, originalText);
        }
        
        closeModal('dependenciesWarningModal');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Помилка при видаленні матеріалу');
        resetConfirmDependentDeleteButton(confirmBtn, originalText);
        closeModal('dependenciesWarningModal');
    });
}

function resetConfirmDependentDeleteButton(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
}

// Показать сообщение об успехе
function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success';
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    `;
    successDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        ${message}
    `;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 2000);
}

function resetDeleteButton(button, originalText) {
    button.disabled = false;
    button.textContent = originalText;
}

// Подключаем обработчики после загрузки страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing button handlers...');
    
    // Кнопки редактирования
    document.querySelectorAll('.action-btn.edit').forEach(btn => {
        console.log('Found edit button:', btn);
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-material-id');
            console.log('Edit button clicked, material ID:', id);
            if (id) editMaterial(id);
        });
    });

    // Кнопки удаления
    document.querySelectorAll('.action-btn.delete').forEach(btn => {
        console.log('Found delete button:', btn);
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-material-id');
            console.log('Delete button clicked, material ID:', id);
            if (id) showDeleteModal(id);
        });
    });

    // Кнопка подтверждения удаления в модальном окне
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', deleteMaterial);
    }

    // Закрытие модального окна при клике вне его содержимого
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });

    // Инициализация кнопок закрытия для флеш-сообщений
    document.querySelectorAll('.alert .btn-close').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.alert').remove();
        });
    });

    // Intersection Observer для анимации появления карточек
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
            }
        });
    }, observerOptions);

    // Наблюдаем за всеми карточками материалов
    const materialCards = document.querySelectorAll('.material-card');
    materialCards.forEach(card => {
        card.style.animationPlayState = 'paused';
        observer.observe(card);
    });
    
    // Обработка ошибок загрузки изображений
    const materialImages = document.querySelectorAll('.material-img');
    materialImages.forEach(img => {
        img.addEventListener('error', function() {
            this.src = '/static/img/matertial_logo.png';
        });
    });
});

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Enhanced Brand Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Элементы управления
    const searchInput = document.getElementById('materialSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    const sortSelect = document.getElementById('sortBy');
    const resetBtn = document.getElementById('resetFilters');

    const materialsContainer = document.getElementById('materialsContainer');
    const materialsCount = document.getElementById('materialsCount');
    const noResults = document.getElementById('noResults');
    
    // Получаем все карточки материалов
    let allMaterials = Array.from(document.querySelectorAll('.material-card'));
    let filteredMaterials = [...allMaterials];
    
    // Инициализация
    init();
    
    function init() {
        // Обработчики событий
        if (searchInput) {
            searchInput.addEventListener('input', debounce(handleSearch, 300));
        }
        
        if (categoryFilter) {
            categoryFilter.addEventListener('change', handleFilter);
        }
        
        if (sortSelect) {
            sortSelect.addEventListener('change', handleSort);
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', resetFilters);
        }
        

        
        // Обработчики для кнопок действий
        setupActionButtons();
        
        // Анимация появления карточек
        animateCards();
    }
    
    // Поиск материалов
    function handleSearch() {
        const query = searchInput.value.toLowerCase().trim();
        
        filteredMaterials = allMaterials.filter(card => {
            const title = card.dataset.title || '';
            return title.includes(query);
        });
        
        applyFiltersAndSort();
    }
    
    // Фильтрация по категории
    function handleFilter() {
        const selectedCategory = categoryFilter.value;
        
        if (!selectedCategory) {
            filteredMaterials = [...allMaterials];
        } else {
            filteredMaterials = allMaterials.filter(card => {
                return card.dataset.category === selectedCategory;
            });
        }
        
        // Применяем поиск к отфильтрованным результатам
        if (searchInput && searchInput.value.trim()) {
            const query = searchInput.value.toLowerCase().trim();
            filteredMaterials = filteredMaterials.filter(card => {
                const title = card.dataset.title || '';
                return title.includes(query);
            });
        }
        
        applyFiltersAndSort();
    }
    
    // Сортировка материалов
    function handleSort() {
        const sortBy = sortSelect.value;
        
        filteredMaterials.sort((a, b) => {
            switch (sortBy) {
                case 'date_desc':
                    return new Date(b.dataset.date) - new Date(a.dataset.date);
                case 'date_asc':
                    return new Date(a.dataset.date) - new Date(b.dataset.date);
                case 'title_asc':
                    return a.dataset.title.localeCompare(b.dataset.title);
                case 'title_desc':
                    return b.dataset.title.localeCompare(a.dataset.title);
                default:
                    return 0;
            }
        });
        
        updateDisplay();
    }
    
    // Применение фильтров и сортировки
    function applyFiltersAndSort() {
        handleSort();
    }
    
    // Обновление отображения
    function updateDisplay() {
        // Скрываем все карточки
        allMaterials.forEach(card => {
            card.style.display = 'none';
        });
        
        // Показываем отфильтрованные карточки
        if (filteredMaterials.length > 0) {
            filteredMaterials.forEach((card, index) => {
                card.style.display = 'block';
                card.style.animationDelay = `${index * 0.1}s`;
            });
            
            // Перестраиваем порядок в DOM
            filteredMaterials.forEach(card => {
                materialsContainer.appendChild(card);
            });
            
            noResults.style.display = 'none';
        } else {
            noResults.style.display = 'block';
        }
        
        // Обновляем счетчик
        if (materialsCount) {
            materialsCount.textContent = filteredMaterials.length;
        }
        
        // Перезапускаем анимации
        animateCards();
    }
    
    // Сброс фильтров
    function resetFilters() {
        if (searchInput) searchInput.value = '';
        if (categoryFilter) categoryFilter.value = '';
        if (sortSelect) sortSelect.value = 'date_desc';
        
        filteredMaterials = [...allMaterials];
        updateDisplay();
    }
    

    
    // Настройка кнопок действий
    function setupActionButtons() {
        // Кнопки редактирования
        document.querySelectorAll('.action-btn.edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const materialId = btn.dataset.materialId;
                window.location.href = `/material/${materialId}/edit`;
            });
        });
        
        // Кнопки удаления
        document.querySelectorAll('.action-btn.delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const materialId = btn.dataset.materialId;
                showDeleteModal(materialId);
            });
        });
    }
    
    // Анимация карточек
    function animateCards() {
        const visibleCards = filteredMaterials.filter(card => 
            card.style.display !== 'none'
        );
        
        visibleCards.forEach((card, index) => {
            card.style.animation = 'none';
            card.offsetHeight; // Trigger reflow
            card.style.animation = `fadeInUp 0.6s ease forwards`;
            card.style.animationDelay = `${index * 0.1}s`;
        });
    }
    
    // Уведомления
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        // Добавляем в начало контейнера
        const container = document.querySelector('.materials-section');
        container.insertBefore(notification, container.firstChild);
        
        // Автоматически скрыть через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Глобальная функция сброса фильтров
    window.resetFilters = resetFilters;
    
    // Debounce функция
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
});

// CSS анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: scale(1);
        }
        to {
            opacity: 0;
            transform: scale(0.8);
        }
    }
    
    .notification {
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);