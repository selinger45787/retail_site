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
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
        if (modalId === 'deleteMaterialModal') {
            materialToDelete = null;
        }
    }, 300);
}

// Удаление материала
function deleteMaterial() {
    if (!materialToDelete) return;

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
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            closeModal('deleteMaterialModal');
            alert(data.error || 'Помилка при видаленні матеріалу');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        closeModal('deleteMaterialModal');
        alert('Помилка при видаленні матеріалу');
    });
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
});