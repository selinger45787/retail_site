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
    .then(response => response.json())
    .then(data => {
        if (data.needs_confirmation && !data.confirmed) {
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
    .then(response => response.json())
    .then(data => {
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
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Помилка при видаленні матеріалу');
        resetConfirmDependentDeleteButton(confirmBtn, originalText);
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

// Глобальная функция для кнопки сброса в шаблоне
function resetFilters() {
    const searchInput = document.getElementById('materialSearch');
    const brandFilter = document.getElementById('brandFilter');
    const sortSelect = document.getElementById('sortBy');
    
    if (searchInput) searchInput.value = '';
    if (brandFilter) brandFilter.value = '';
    if (sortSelect) sortSelect.value = 'date_desc';
    
    // Триггерим событие для обновления фильтров
    if (searchInput) searchInput.dispatchEvent(new Event('input'));
}

// Enhanced Category Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Category page JavaScript loaded');
    
    // Элементы управления
    const searchInput = document.getElementById('materialSearch');
    const brandFilter = document.getElementById('brandFilter');
    const sortSelect = document.getElementById('sortBy');
    const resetBtn = document.getElementById('resetFilters');
    const viewBtns = document.querySelectorAll('.view-btn');
    const materialsContainer = document.getElementById('materialsContainer');
    const materialsCount = document.getElementById('materialsCount');
    const noResults = document.getElementById('noResults');
    
    // Получаем все карточки материалов
    let allMaterials = Array.from(document.querySelectorAll('.material-card'));
    let filteredMaterials = [...allMaterials];
    
    console.log('Found materials:', allMaterials.length);
    
    // Инициализация
    init();
    
    function init() {
        // Обработчики событий
        if (searchInput) {
            searchInput.addEventListener('input', debounce(applyAllFilters, 300));
            console.log('Search input listener added');
        }
        
        if (brandFilter) {
            brandFilter.addEventListener('change', applyAllFilters);
            console.log('Brand filter listener added');
        }
        
        if (sortSelect) {
            sortSelect.addEventListener('change', applyAllFilters);
            console.log('Sort select listener added');
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', resetFilters);
            console.log('Reset button listener added');
        }
        
        // Переключение видов
        viewBtns.forEach(btn => {
            btn.addEventListener('click', (e) => switchView(e.target.closest('.view-btn').dataset.view));
        });
        
        // Обработчики для кнопок действий
        setupActionButtons();
        
        // Анимация появления карточек
        animateCards();
        
        // Инициальное обновление счетчика
        updateCount();
    }
    
    // Применить все фильтры и сортировку
    function applyAllFilters() {
        console.log('Applying all filters...');
        
        const searchQuery = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const selectedBrand = brandFilter ? brandFilter.value : '';
        const sortType = sortSelect ? sortSelect.value : 'date_desc';
        
        console.log('Search query:', searchQuery);
        console.log('Selected brand:', selectedBrand);
        console.log('Sort type:', sortType);
        
        // Начинаем с всех материалов
        filteredMaterials = [...allMaterials];
        
        // Применяем поиск
        if (searchQuery) {
            filteredMaterials = filteredMaterials.filter(card => {
                const title = card.dataset.title || '';
                return title.includes(searchQuery);
            });
        }
        
        // Применяем фильтр по бренду
        if (selectedBrand) {
            filteredMaterials = filteredMaterials.filter(card => {
                return card.dataset.brand === selectedBrand;
            });
        }
        
        console.log('Filtered materials count:', filteredMaterials.length);
        
        // Применяем сортировку
        filteredMaterials.sort((a, b) => {
            switch (sortType) {
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
    
    function updateDisplay() {
        // Очищаем контейнер
        materialsContainer.innerHTML = '';
        
        if (filteredMaterials.length === 0) {
            noResults.style.display = 'block';
            updateCount(0);
        } else {
            noResults.style.display = 'none';
            updateCount(filteredMaterials.length);
            
            // Добавляем отфильтрованные карточки
            filteredMaterials.forEach(card => {
                materialsContainer.appendChild(card);
            });
        }
        
        // Переустанавливаем обработчики кнопок для новых элементов
        setupActionButtons();
        
        // Обновляем анимации
        animateCards();
    }
    
    function updateCount(count = null) {
        const displayCount = count !== null ? count : filteredMaterials.length;
        if (materialsCount) {
            materialsCount.textContent = displayCount;
        }
    }
    
    function switchView(view) {
        viewBtns.forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-view="${view}"]`).classList.add('active');
        
        materialsContainer.className = view === 'list' ? 'materials-list' : 'materials-grid';
    }
    
    function setupActionButtons() {
        // Кнопки редактирования
        document.querySelectorAll('.action-btn.edit').forEach(btn => {
            // Удаляем старые обработчики
            btn.replaceWith(btn.cloneNode(true));
        });
        
        document.querySelectorAll('.action-btn.edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const id = btn.getAttribute('data-material-id');
                if (id) editMaterial(id);
            });
        });

        // Кнопки удаления
        document.querySelectorAll('.action-btn.delete').forEach(btn => {
            // Удаляем старые обработчики
            btn.replaceWith(btn.cloneNode(true));
        });
        
        document.querySelectorAll('.action-btn.delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const id = btn.getAttribute('data-material-id');
                if (id) showDeleteModal(id);
            });
        });
    }
    
    function animateCards() {
        const cards = materialsContainer.querySelectorAll('.material-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('animate-in');
        });
    }
    
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
    
    // Инициализация кнопок закрытия для флеш-сообщений
    document.querySelectorAll('.alert .btn-close').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.alert').remove();
        });
    });

    // Обработка ошибок загрузки изображений
    const materialImages = document.querySelectorAll('.material-img');
    materialImages.forEach(img => {
        img.addEventListener('error', function() {
            this.src = '/static/img/matertial_logo.png';
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
    allMaterials.forEach(card => {
        card.style.animationPlayState = 'paused';
        observer.observe(card);
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