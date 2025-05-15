// JavaScript для работы с модальными окнами

/**
 * Открывает модальное окно с анимацией
 * @param {string} id - ID модального окна
 */
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        // Сначала отобразить модальное окно без анимации
        modal.style.display = 'flex';
        
        // Добавить небольшую задержку перед анимацией для плавности
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        
        // Отключить прокрутку основного содержимого
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Закрывает модальное окно с анимацией
 * @param {string} id - ID модального окна
 */
function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        // Сначала удаляем класс для анимации выхода
        modal.classList.remove('show');
        
        // Добавить задержку перед скрытием, чтобы анимация успела завершиться
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
        
        // Восстановить прокрутку основного содержимого
        document.body.style.overflow = '';
    }
}

// Добавляем обработчики событий после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    // Закрытие модального окна при клике вне содержимого
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(event) {
            // Закрываем только если клик был не на содержимом модального окна, а на фоне
            if (event.target === this) {
                closeModal(this.id);
            }
        });
    });

    // Добавляем слушателей для кнопок закрытия
    document.querySelectorAll('.modal .close').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.closest('.modal').id;
            closeModal(modalId);
        });
    });

    // Добавляем функции для модального окна логина
    window.showLoginModal = function() {
        openModal('loginModal');
    };
    
    window.closeLoginModal = function() {
        closeModal('loginModal');
    };

    // Глобальная функция для подтверждения удаления материала
    window.confirmDeleteMaterial = function() {
        const materialId = window.materialToDelete;
        if (!materialId) return;
        
        // Показать индикатор загрузки на кнопке
        const deleteButton = document.querySelector('#deleteMaterialModal .btn-danger');
        const originalText = deleteButton.innerHTML;
        deleteButton.innerHTML = '<span class="spinner"></span> Видалення...';
        deleteButton.disabled = true;

        // Получаем CSRF токен
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        // Отправляем запрос на удаление
        fetch(`/material/${materialId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Помилка мережі');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                throw new Error(data.error || 'Помилка при видаленні');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message || 'Помилка при видаленні матеріалу');
            
            // Восстановить кнопку
            deleteButton.innerHTML = originalText;
            deleteButton.disabled = false;
            
            // Закрыть модальное окно
            closeModal('deleteMaterialModal');
        });
    };
}); 