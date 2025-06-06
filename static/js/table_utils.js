// Утилиты для работы с таблицами: поиск и сортировка

class TableUtils {
    constructor(tableId, searchInputId) {
        this.table = document.getElementById(tableId);
        this.searchInput = document.getElementById(searchInputId);
        this.tbody = this.table.querySelector('tbody');
        this.rows = Array.from(this.tbody.querySelectorAll('tr'));
        this.headers = this.table.querySelectorAll('thead th');
        this.sortDirection = {}; // Для отслеживания направления сортировки
        
        this.initSearch();
        this.initSort();
    }
    
    // Инициализация поиска
    initSearch() {
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.search(e.target.value.toLowerCase());
            });
        }
    }
    
    // Функция поиска
    search(query) {
        this.rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        // Обновляем счетчик результатов
        this.updateResultsCounter();
    }
    
    // Обновление счетчика результатов
    updateResultsCounter() {
        const visibleRows = this.rows.filter(row => row.style.display !== 'none');
        const counter = document.getElementById('resultsCounter');
        if (counter) {
            counter.textContent = `Показано: ${visibleRows.length} из ${this.rows.length}`;
        }
    }
    
    // Инициализация сортировки
    initSort() {
        this.headers.forEach((header, index) => {
            // Пропускаем колонку "Дії" (обычно последняя)
            if (header.textContent.trim() === 'Дії') return;
            
            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';
            header.classList.add('sortable');
            
            // Добавляем иконку сортировки
            const icon = document.createElement('i');
            icon.className = 'fas fa-sort ms-2 text-muted';
            header.appendChild(icon);
            
            header.addEventListener('click', () => {
                this.sort(index, header);
            });
        });
    }
    
    // Функция сортировки
    sort(columnIndex, header) {
        const currentDirection = this.sortDirection[columnIndex] || 'asc';
        const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
        this.sortDirection[columnIndex] = newDirection;
        
        // Сброс иконок всех заголовков
        this.headers.forEach(h => {
            const icon = h.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-sort ms-2 text-muted';
            }
        });
        
        // Установка иконки для текущего заголовка
        const currentIcon = header.querySelector('i');
        if (currentIcon) {
            currentIcon.className = newDirection === 'asc' 
                ? 'fas fa-sort-up ms-2 text-primary' 
                : 'fas fa-sort-down ms-2 text-primary';
        }
        
        // Сортировка строк
        const sortedRows = this.rows.slice().sort((a, b) => {
            const aValue = this.getCellValue(a, columnIndex);
            const bValue = this.getCellValue(b, columnIndex);
            
            // Определяем тип данных для правильной сортировки
            const aNum = this.parseNumber(aValue);
            const bNum = this.parseNumber(bValue);
            
            let result;
            if (!isNaN(aNum) && !isNaN(bNum)) {
                // Числовая сортировка
                result = aNum - bNum;
            } else if (this.isDate(aValue) && this.isDate(bValue)) {
                // Сортировка по дате
                result = new Date(this.parseDate(aValue)) - new Date(this.parseDate(bValue));
            } else {
                // Текстовая сортировка
                result = aValue.localeCompare(bValue, 'uk', {numeric: true});
            }
            
            return newDirection === 'asc' ? result : -result;
        });
        
        // Перестраиваем таблицу
        sortedRows.forEach(row => this.tbody.appendChild(row));
    }
    
    // Получение значения ячейки
    getCellValue(row, columnIndex) {
        const cell = row.cells[columnIndex];
        if (!cell) return '';
        
        // Извлекаем текст из badges и других элементов
        const badges = cell.querySelectorAll('.badge');
        if (badges.length > 0) {
            return badges[0].textContent.trim();
        }
        
        return cell.textContent.trim();
    }
    
    // Парсинг чисел (включая форматированные числа)
    parseNumber(value) {
        const cleaned = value.replace(/[^\d.,]/g, '').replace(',', '.');
        return parseFloat(cleaned);
    }
    
    // Проверка, является ли строка датой
    isDate(value) {
        return /^\d{2}\.\d{2}\.\d{4}/.test(value);
    }
    
    // Парсинг даты в формате dd.mm.yyyy
    parseDate(value) {
        const match = value.match(/(\d{2})\.(\d{2})\.(\d{4})/);
        if (match) {
            return `${match[3]}-${match[2]}-${match[1]}`;
        }
        return value;
    }
    
    // Добавление строки поиска
    static addSearchBar(containerId, placeholder = 'Пошук...') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const searchBar = document.createElement('div');
        searchBar.className = 'row mb-3';
        searchBar.innerHTML = `
            <div class="col-md-6">
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="fas fa-search"></i>
                    </span>
                    <input type="text" class="form-control" id="tableSearch" placeholder="${placeholder}">
                </div>
            </div>
            <div class="col-md-6 text-end">
                <small class="text-muted" id="resultsCounter"></small>
            </div>
        `;
        
        // Вставляем перед таблицей
        const table = container.querySelector('.table-responsive') || container.querySelector('table');
        if (table) {
            table.parentNode.insertBefore(searchBar, table);
        }
    }
}

// CSS стили для сортируемых заголовков
const style = document.createElement('style');
style.textContent = `
    .sortable:hover {
        background-color: #f8f9fa;
    }
    
    .sortable i {
        transition: all 0.2s;
    }
    
    .table-responsive {
        border-radius: 0.375rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }
    
    .input-group-text {
        background-color: #e9ecef;
        border-color: #ced4da;
    }
    
    #tableSearch {
        border-color: #ced4da;
    }
    
    #tableSearch:focus {
        border-color: #86b7fe;
        box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    }
`;
document.head.appendChild(style); 