document.addEventListener('DOMContentLoaded', function() {
    const departmentSelect = document.getElementById('department');
    const positionSelect = document.getElementById('position');
    const positionDiv = positionSelect.closest('.col-md-4');

    // Определяем структуру зависимостей отделов и должностей
    const departmentPositions = {
        'founders': [
            { value: 'founder', label: 'Засновник' }
        ],
        'general_director': [
            { value: 'general_director', label: 'Генеральний директор' }
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
            { value: 'analyst', label: 'Аналітик' }
        ],
        'other': [
            { value: 'office_manager', label: 'Офіс менеджер' },
            { value: 'cleaner', label: 'Прибиральниця' }
        ],
        'abrams_production': [
            { value: 'department_head', label: 'Керівник відділу' },
            { value: 'warehouse_worker', label: 'Комірник' },
            { value: 'other_position', label: 'Інше' }
        ]
    };

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
    }

    // Инициализация при загрузке страницы
    updatePositionOptions();

    // Обработчик изменения отдела
    departmentSelect.addEventListener('change', updatePositionOptions);
}); 