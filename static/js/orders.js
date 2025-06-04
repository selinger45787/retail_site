// JavaScript для страницы заказов
console.log('Orders page loaded - full version');

let currentOrderId = null;
let deleteModal = null;

// Делаем карточки кликабельными
document.addEventListener('DOMContentLoaded', function() {
    const orderCards = document.querySelectorAll('.order-card');
    orderCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function(e) {
            // Не переходим если кликнули по кнопке
            if (e.target.closest('.order-actions')) {
                return;
            }
            
            // Находим ссылку для просмотра и переходим по ней
            const viewLink = card.querySelector('.order-actions a[href*="/orders/"]');
            if (viewLink) {
                window.location.href = viewLink.href;
            }
        });
    });
    
    // Инициализируем модальное окно
    const deleteModalElement = document.getElementById('deleteOrderModal');
    if (deleteModalElement && typeof bootstrap !== 'undefined') {
        deleteModal = new bootstrap.Modal(deleteModalElement);
        
        // Добавляем обработчик для кнопки подтверждения
        const confirmButton = document.getElementById('confirmDeleteOrder');
        if (confirmButton) {
            confirmButton.addEventListener('click', function() {
                confirmDeleteOrder();
            });
        }
    }
    
    // Инициализируем фильтры
    initializeFilters();
});

function initializeFilters() {
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const departmentFilter = document.getElementById('departmentFilter');
    const resetButton = document.getElementById('resetFilters');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterOrders);
    }
    if (statusFilter) {
        statusFilter.addEventListener('change', filterOrders);
    }
    if (departmentFilter) {
        departmentFilter.addEventListener('change', filterOrders);
    }
    if (resetButton) {
        resetButton.addEventListener('click', resetFilters);
    }
}

function filterOrders() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const departmentFilter = document.getElementById('departmentFilter').value;
    
    const orderCards = document.querySelectorAll('.order-card');
    
    orderCards.forEach(card => {
        const title = card.querySelector('.order-title').textContent.toLowerCase();
        const description = card.querySelector('.order-description').textContent.toLowerCase();
        const cardStatus = card.getAttribute('data-status');
        const cardDepartments = card.getAttribute('data-departments');
        
        // Поиск по тексту
        const matchesSearch = !searchTerm || 
            title.includes(searchTerm) || 
            description.includes(searchTerm);
        
        // Фильтр по статусу
        const matchesStatus = !statusFilter || cardStatus === statusFilter;
        
        // Фильтр по отделу - проверяем, есть ли выбранный отдел в списке отделов карточки
        let matchesDepartment = !departmentFilter;
        if (departmentFilter && cardDepartments) {
            // Проверяем, содержит ли список отделов выбранный отдел или 'all'
            const departmentsList = cardDepartments.split(',');
            matchesDepartment = departmentsList.includes('all') || departmentsList.includes(departmentFilter);
        }
        
        if (matchesSearch && matchesStatus && matchesDepartment) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('departmentFilter').value = '';
    
    // Показываем все карточки
    const orderCards = document.querySelectorAll('.order-card');
    orderCards.forEach(card => {
        card.style.display = 'block';
    });
}

function deleteOrder(orderId) {
    currentOrderId = orderId;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Первый запрос для получения данных о распоряжении
    fetch(`/orders/${orderId}/delete`, {
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
    .then(response => response.json())
    .then(data => {
        if (data.needs_confirmation) {
            // Показываем детали распоряжения
            const orderDetailsDiv = document.getElementById('orderDetails');
            if (orderDetailsDiv) {
                orderDetailsDiv.innerHTML = `
                    <div class="alert alert-info">
                        <strong>Назва:</strong> ${data.order_title}<br>
                        <strong>Номер:</strong> ${data.order_number}
                    </div>
                `;
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
        alert('Помилка при видаленні розпорядження');
    });
}

function confirmDeleteOrder() {
    if (!currentOrderId) return;

    const confirmBtn = document.getElementById('confirmDeleteOrder');
    const originalText = confirmBtn.textContent;
    
    // Показываем состояние загрузки
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Видаляємо...';

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Второй запрос для фактического удаления
    fetch(`/orders/${currentOrderId}/delete`, {
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
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Показываем флеш сообщение и перенаправляем
            sessionStorage.setItem('flash_message', data.message);
            sessionStorage.setItem('flash_type', 'success');
            window.location.href = data.redirect;
        } else {
            alert(data.error || 'Помилка при видаленні розпорядження');
            resetDeleteButton(confirmBtn, originalText);
        }
        
        if (deleteModal) {
            deleteModal.hide();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Помилка при видаленні розпорядження');
        resetDeleteButton(confirmBtn, originalText);
        if (deleteModal) {
            deleteModal.hide();
        }
    });
}

function resetDeleteButton(button, originalText) {
    button.disabled = false;
    button.textContent = originalText;
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Закрытие модальных окон
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
} 