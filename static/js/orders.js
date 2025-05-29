document.addEventListener('DOMContentLoaded', function() {
    // Инициализация фильтров
    initializeFilters();
});

// Функции для работы с фильтрами
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
    const statusValue = document.getElementById('statusFilter').value;
    const departmentValue = document.getElementById('departmentFilter').value;
    
    const orders = document.querySelectorAll('.order-card');
    
    orders.forEach(order => {
        const title = order.querySelector('.order-title').textContent.toLowerCase();
        const description = order.querySelector('.order-description').textContent.toLowerCase();
        const status = order.dataset.status;
        const department = order.dataset.department;
        
        const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
        const matchesStatus = !statusValue || status === statusValue;
        const matchesDepartment = !departmentValue || department === departmentValue;
        
        if (matchesSearch && matchesStatus && matchesDepartment) {
            order.style.display = 'flex';
        } else {
            order.style.display = 'none';
        }
    });
}

function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('departmentFilter').value = '';
    
    const orders = document.querySelectorAll('.order-card');
    orders.forEach(order => {
        order.style.display = 'flex';
    });
}

function deleteOrder(orderId) {
    const modal = document.getElementById('deleteOrderModal');
    const form = document.getElementById('deleteOrderForm');
    
    if (modal && form) {
        form.action = `/orders/${orderId}/delete`;
        modal.style.display = 'block';
    }
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