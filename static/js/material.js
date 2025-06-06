let currentMaterialId = null;
let deleteModal = null;

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    // CSS анимации fade-in работают автоматически при загрузке страницы

    // Инициализация галереи
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    const mainImage = document.getElementById('mainImage');

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Убираем активный класс у всех миниатюр
            thumbnails.forEach(t => t.classList.remove('active'));
            
            // Добавляем активный класс к текущей миниатюре
            this.classList.add('active');
            
            // Меняем главное изображение с плавной анимацией
            const newSrc = this.getAttribute('data-src');
            if (mainImage && newSrc && mainImage.src !== newSrc) {
                // Плавно уменьшаем прозрачность
                mainImage.style.opacity = '0';
                
                // Через 300ms меняем источник и возвращаем прозрачность
                setTimeout(() => {
                    mainImage.src = newSrc;
                    mainImage.style.opacity = '1';
                }, 300);
            }
        });
    });

    // Инициализируем модальное окно при загрузке страницы
    const modalElement = document.getElementById('deleteConfirmModal');
    
    if (modalElement) {
        // Удаляем старый backdrop, если он есть
        const oldBackdrop = document.querySelector('.modal-backdrop');
        if (oldBackdrop) {
            oldBackdrop.remove();
        }
        
        deleteModal = new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true
        });

        // Добавляем обработчики для кнопок
        const cancelButton = modalElement.querySelector('[data-bs-dismiss="modal"]');
        const confirmButton = document.getElementById('confirmDelete');

        if (cancelButton) {
            cancelButton.addEventListener('click', function() {
                deleteModal.hide();
            });
        }

        if (confirmButton) {
            confirmButton.addEventListener('click', function() {
                if (!currentMaterialId) return;
                
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                
                // Второй запрос для фактического удаления
                fetch(`/material/${currentMaterialId}/delete`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
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
                        window.location.href = data.redirect;
                    } else {
                        alert(data.error || 'Помилка при видаленні матеріалу');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Помилка при видаленні матеріалу');
                });
                
                deleteModal.hide();
            });
        }
    }
});

function deleteMaterial(materialId) {
    currentMaterialId = materialId;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Первый запрос для проверки зависимостей
    fetch(`/material/${materialId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
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
            // Показываем предупреждения
            const warningsDiv = document.getElementById('deleteWarnings');
            if (warningsDiv) {
                warningsDiv.innerHTML = '';
                
                if (data.has_test) {
                    warningsDiv.innerHTML += '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i>Цей матеріал має створений тест, який також буде видалено.</div>';
                }
                
                if (data.has_active_assignments) {
                    warningsDiv.innerHTML += `<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>У цього матеріалу є ${data.active_assignments_count} активних призначень тестів, які також будуть видалені.</div>`;
                }
                
                if (data.has_test_results) {
                    warningsDiv.innerHTML += `<div class="alert alert-warning"><i class="fas fa-chart-bar me-2"></i>У цього матеріалу є ${data.test_results_count} результатів проходження тестів, які також будуть видалені.</div>`;
                }
            }
            
            // Показываем модальное окно
            if (deleteModal) {
                deleteModal.show();
            }
        } else if (data.error) {
            alert(data.error);
        } else if (data.success) {
            window.location.href = data.redirect;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Помилка при видаленні матеріалу');
    });
}