// Скрипти для сторінки керування користувачами

document.addEventListener('DOMContentLoaded', function() {
    // Ініціалізація модального вікна
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteUserModal'), {
        backdrop: true,
        keyboard: true
    });
    
    // Функція для фільтрації таблиці
    function filterTable() {
        const searchText = document.getElementById('searchInput').value.toLowerCase();
        const roleFilter = document.getElementById('roleFilter').value.toLowerCase();
        const departmentFilter = document.getElementById('departmentFilter').value;
        const rows = document.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const username = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
            const role = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const departmentCell = row.querySelector('td:nth-child(4)');
            const department = departmentCell.getAttribute('data-department') || departmentCell.textContent.toLowerCase();
            
            const matchesSearch = username.includes(searchText);
            const matchesRole = !roleFilter || role.includes(roleFilter);
            const matchesDepartment = !departmentFilter || department.includes(departmentFilter);
            
            row.style.display = matchesSearch && matchesRole && matchesDepartment ? '' : 'none';
        });
        
        // Оновлюємо лічильник користувачів
        const visibleRows = document.querySelectorAll('tbody tr:not([style*="display: none"])').length;
        document.getElementById('userCount').textContent = `Всього: ${visibleRows}`;
    }
    
    // Обробники подій для фільтрів
    document.getElementById('searchInput').addEventListener('input', filterTable);
    document.getElementById('roleFilter').addEventListener('change', filterTable);
    document.getElementById('departmentFilter').addEventListener('change', filterTable);
    
    // Скидання фільтрів
    document.getElementById('resetFilters').addEventListener('click', function() {
        document.getElementById('searchInput').value = '';
        document.getElementById('roleFilter').value = '';
        document.getElementById('departmentFilter').value = '';
        filterTable();
    });
    
    // Обробник видалення користувача
    document.querySelectorAll('.delete-user-btn').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            const username = this.getAttribute('data-username');
            
            // Перевіряємо залежності користувача
            fetch(`/admin/users/${userId}/dependencies`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(data.error || 'Помилка при перевірці залежностей');
                }
                
                // Очищуємо попередні попередження
                const warningsDiv = document.getElementById('deleteWarnings');
                warningsDiv.innerHTML = '';
                
                // Додаємо попередження, якщо є залежності
                if (data.test_results_count > 0) {
                    warningsDiv.innerHTML += `<div class="alert alert-warning">У користувача є ${data.test_results_count} результатів тестів, які також будуть видалені.</div>`;
                }
                
                if (data.test_assignments_count > 0) {
                    warningsDiv.innerHTML += `<div class="alert alert-danger">У користувача є ${data.test_assignments_count} призначених тестів, які також будуть видалені.</div>`;
                }
                
                document.getElementById('deleteUserName').textContent = username;
                document.getElementById('confirmDeleteBtn').setAttribute('data-user-id', userId);
                deleteModal.show();
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || 'Помилка при перевірці залежностей користувача');
            });
        });
    });
    
    // Підтвердження видалення
    document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
        const userId = this.getAttribute('data-user-id');
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        fetch(`/admin/users/${userId}/delete`, {
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
            if (data.success) {
                // Показуємо повідомлення про успіх
                const flashContainer = document.createElement('div');
                flashContainer.className = 'alert alert-success alert-dismissible fade show';
                flashContainer.innerHTML = `
                    ${data.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                document.querySelector('.container').insertBefore(flashContainer, document.querySelector('.container').firstChild);
                
                // Перезавантажуємо сторінку через невелику затримку
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            } else {
                alert(data.error || 'Помилка при видаленні користувача');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Помилка при видаленні користувача');
        })
        .finally(() => {
            deleteModal.hide();
        });
    });
}); 