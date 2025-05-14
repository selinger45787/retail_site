// Перенаправление на редактирование
function editMaterial(materialId) {
    window.location.href = `/material/${materialId}/edit`;
}

// Удаление материала с подтверждением
function deleteMaterial(materialId) {
    // Сохраняем ID материала для удаления
    window.materialToDelete = materialId;
    // Показываем модальное окно
    document.getElementById('deleteMaterialModal').style.display = 'flex';
}

// Функция для подтверждения удаления
function confirmDeleteMaterial() {
    const materialId = window.materialToDelete;
    if (!materialId) return;

    // Получаем CSRF токен
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            alert(data.error || 'Помилка при видаленні матеріалу');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Помилка при видаленні матеріалу');
    })
    .finally(() => {
        // Закрываем модальное окно
        document.getElementById('deleteMaterialModal').style.display = 'none';
        // Очищаем ID материала
        window.materialToDelete = null;
    });
}

// Открытие модального окна
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Блокируем прокрутку
    }
}

// Закрытие модального окна
function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = ''; // Восстанавливаем прокрутку
    }
}

// Закрытие модалки при клике вне неё
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
};

// Обработчик клика вне модального окна
window.addEventListener('click', function(event) {
    const modal = document.getElementById('deleteMaterialModal');
    if (event.target === modal) {
        modal.style.display = 'none';
        window.materialToDelete = null;
    }
});

// Подключаем обработчики после загрузки страницы
document.addEventListener('DOMContentLoaded', () => {
    // Кнопки редактирования
    document.querySelectorAll('.action-btn.edit').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.materialId;
            if (id) editMaterial(id);
        });
    });

    // Кнопки удаления
    document.querySelectorAll('.action-btn.delete').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.materialId;
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