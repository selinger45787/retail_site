document.addEventListener('DOMContentLoaded', function() {
    const departmentSelect = document.getElementById('department');
    const positionSelect = document.getElementById('position');
    const positionDiv = positionSelect.closest('.col-md-4');
    const photoField = document.getElementById('photoField');
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');

    // Определяем структуру зависимостей отделов и должностей
    const departmentPositions = {
        'founders': [
            { value: 'founder', label: 'Засновник' }
        ],
        'general_director': [
            { value: 'general_director', label: 'Директор' }
        ],
        'accounting': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'accountant', label: 'Бухгалтер' }
        ],
        'marketing': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'photographer', label: 'Фотограф' },
            { value: 'marketer', label: 'Маркетолог' }
        ],
        'online_sales': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'customer_manager', label: 'Менеджер по роботі з клієнтами' }
        ],
        'offline_sales': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'seller', label: 'Продавець' },
            { value: 'cashier', label: 'Касир' },
            { value: 'merchandiser', label: 'Мерчендайзер' }
        ],
        'foreign_trade': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'foreign_trade_manager', label: 'Менеджер ЗЕД' }
        ],
        'warehouse': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'warehouse_worker', label: 'Комірник' }
        ],
        'analytics': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'analyst', label: 'Аналітик' }
        ],
        'abrams_production': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'warehouse_worker', label: 'Комірник' }
        ],
        'other': [
            { value: 'office_manager', label: 'Офіс менеджер' },
            { value: 'cleaner', label: 'Прибиральниця' },
            { value: 'other_position', label: 'Інше' }
        ]
    };

    // Позиции, которые требуют фотографии
    const photoRequiredPositions = ['founder', 'general_director', 'department_head'];

    function updatePositionOptions() {
        const selectedDepartment = departmentSelect.value;
        const positions = departmentPositions[selectedDepartment] || [];

        // Очищаем текущие опции
        positionSelect.innerHTML = '';
        
        // Показываем поле должности для всех отделов
        positionDiv.style.display = 'block';
        
        // Добавляем новые опции
        positions.forEach(position => {
            const option = document.createElement('option');
            option.value = position.value;
            option.textContent = position.label;
            positionSelect.appendChild(option);
        });

        // Проверяем, нужно ли показать поле фото
        updatePhotoFieldVisibility();
    }

    function updatePhotoFieldVisibility() {
        const selectedPosition = positionSelect.value;
        if (photoField && photoRequiredPositions.includes(selectedPosition)) {
            photoField.style.display = 'block';
        } else if (photoField) {
            photoField.style.display = 'none';
            // Очищаем превью при скрытии поля
            if (photoPreview) {
                photoPreview.innerHTML = '';
            }
        }
    }

    // Функция предпросмотра фотографии
    function handlePhotoPreview(event) {
        const file = event.target.files[0];
        if (file && photoPreview) {
            const reader = new FileReader();
            reader.onload = function(e) {
                photoPreview.innerHTML = `
                    <div class="photo-preview-container">
                        <img src="${e.target.result}" alt="Попередній перегляд" 
                             style="max-width: 150px; max-height: 150px; border-radius: 8px; border: 2px solid #ddd;">
                        <div class="mt-2 text-muted small">${file.name}</div>
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        }
    }

    // Инициализация при загрузке страницы
    updatePositionOptions();

    // Обработчики событий
    departmentSelect.addEventListener('change', updatePositionOptions);
    positionSelect.addEventListener('change', updatePhotoFieldVisibility);
    if (photoInput) {
        photoInput.addEventListener('change', handlePhotoPreview);
    }
}); 