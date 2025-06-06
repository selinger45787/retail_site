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

    groupImagesIntoGrid();
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

// Автоматическое группирование изображений в grid
function groupImagesIntoGrid() {
    const description = document.querySelector('.material-description');
    if (!description) return;
    
    // Ищем все группы последовательных изображений
    const allElements = Array.from(description.children);
    let imageGroups = [];
    let currentGroup = [];
    
    allElements.forEach((element, index) => {
        // Проверяем любые элементы (P, H1, H2, H3, DIV и т.д.) содержащие изображения
        if (element.tagName === 'P' || element.tagName.startsWith('H') || element.tagName === 'DIV') {
            const images = element.querySelectorAll('img');
            
            if (images.length > 1) {
                // Если в элементе несколько изображений, группируем их
                images.forEach(img => currentGroup.push(img));
                // Сохраняем группу сразу
                if (currentGroup.length > 1) {
                    imageGroups.push([...currentGroup]);
                }
                currentGroup = [];
            } else if (images.length === 1) {
                // Если одно изображение, добавляем к текущей группе
                currentGroup.push(images[0]);
            } else {
                // Элемент без изображений - завершаем группу если есть
                if (currentGroup.length > 1) {
                    imageGroups.push([...currentGroup]);
                }
                currentGroup = [];
            }
        } else if (element.tagName === 'IMG') {
            currentGroup.push(element);
        } else {
            // Любой другой элемент завершает группу
            if (currentGroup.length > 1) {
                imageGroups.push([...currentGroup]);
            }
            currentGroup = [];
        }
    });
    
    // Не забываем последнюю группу
    if (currentGroup.length > 1) {
        imageGroups.push(currentGroup);
    }
    
    // Создаем grid для каждой группы
    imageGroups.forEach(group => {
        if (group.length > 1) {
            createImageGrid(group);
        }
    });
}

// Получить текст между двумя элементами
function getTextBetweenElements(element1, element2) {
    let text = '';
    let current = element1.nextSibling;
    
    while (current && current !== element2) {
        if (current.nodeType === Node.TEXT_NODE) {
            text += current.textContent;
        } else if (current.nodeType === Node.ELEMENT_NODE) {
            text += current.textContent;
        }
        current = current.nextSibling;
    }
    
    return text.trim();
}

// Создать grid из группы изображений
function createImageGrid(imageGroup) {
    if (imageGroup.length < 2) return;
    
    // Создаем контейнер grid
    const gridContainer = document.createElement('div');
    gridContainer.className = 'image-grid';
    
    // Находим родительский элемент первого изображения
    const firstImage = imageGroup[0];
    const parentElement = firstImage.closest('p') || firstImage.closest('h1') || firstImage.closest('h2') || firstImage.closest('h3') || firstImage.closest('h4') || firstImage.closest('h5') || firstImage.closest('h6') || firstImage.closest('div') || firstImage.parentNode;
    
    // Вставляем grid после родительского элемента
    if (parentElement.nextSibling) {
        parentElement.parentNode.insertBefore(gridContainer, parentElement.nextSibling);
    } else {
        parentElement.parentNode.appendChild(gridContainer);
    }
    
    // Перемещаем все изображения в grid и удаляем пустые параграфы
    const elementsToRemove = new Set();
    
    imageGroup.forEach(img => {
        // Клонируем изображение для сохранения атрибутов
        const clonedImg = img.cloneNode(true);
        gridContainer.appendChild(clonedImg);
        
        // Отмечаем родительские элементы для удаления
        const imgParent = img.closest('p') || img.closest('h1') || img.closest('h2') || img.closest('h3') || img.closest('h4') || img.closest('h5') || img.closest('h6') || img.closest('div') || img.parentNode;
        elementsToRemove.add(imgParent);
        
        // Удаляем оригинальное изображение
        img.remove();
    });
    
    // Обрабатываем родительские элементы
    elementsToRemove.forEach(element => {
        // Если элемент - заголовок, сохраняем текст без изображений
        if (element.tagName && element.tagName.startsWith('H')) {
            // Клонируем заголовок
            const newHeader = element.cloneNode(false);
            // Добавляем только текстовые узлы (без изображений)
            Array.from(element.childNodes).forEach(node => {
                if (node.nodeType === Node.TEXT_NODE || (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'IMG')) {
                    newHeader.appendChild(node.cloneNode(true));
                }
            });
            // Заменяем оригинальный заголовок если в нем остался текст
            if (newHeader.textContent.trim().length > 0) {
                element.parentNode.insertBefore(newHeader, element);
            }
            element.remove();
        } else if (element.textContent.trim().length === 0) {
            // Удаляем пустые элементы
            element.remove();
        }
    });
}