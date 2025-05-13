// Перенаправление на редактирование
function editMaterial(materialId) {
    window.location.href = `/material/${materialId}/edit`;
}

// Удаление материала с подтверждением
function deleteMaterial(materialId) {
    if (confirm('Ви впевнені, що хочете видалити цей матеріал?')) {
        fetch(`/material/${materialId}/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Помилка при видаленні матеріалу');
            }
        })
        .catch(err => {
            console.error(err);
            alert('Помилка при видаленні');
        });
    }
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

            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message || 'Помилка при додаванні матеріалу');
                }
            })
            .catch(err => {
                console.error(err);
                alert('Помилка при додаванні матеріалу');
            });
        });
    }
});