// Перенаправление на редактирование
function editMaterial(materialId) {
    window.location.href = `/material/${materialId}/edit`;
}

// Удаление материала с подтверждением
function deleteMaterial(materialId) {
    // Сохраняем ID материала для удаления
    window.materialToDelete = materialId;
    // Показываем модальное окно используя функцию из modals.js
    openModal('deleteMaterialModal');
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
            if (id) deleteMaterial(id);
        });
    });

    // Обработка формы добавления материала
    const form = document.getElementById('addMaterialForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            formData.append('csrf_token', csrfToken);

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect || window.location.href;
                } else {
                    alert(data.message || 'Помилка при додаванні матеріалу');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Помилка при додаванні матеріалу');
            });
        });
    }
});