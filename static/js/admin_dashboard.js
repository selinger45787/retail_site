document.addEventListener('DOMContentLoaded', function() {
    const addUserForm = document.getElementById('addUserForm');
    const userSearch = document.getElementById('userSearch');
    const sortBy = document.getElementById('sortBy');
    
    // Добавляем обработчик для фильтрации
    if (userSearch) {
        userSearch.addEventListener('input', function() {
            const searchText = this.value.toLowerCase();
            const userRows = document.querySelectorAll('.user-row');
            
            userRows.forEach(row => {
                const userName = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                const detailsRow = document.getElementById(`user-details-${row.dataset.userId}`);
                
                if (userName.includes(searchText)) {
                    row.style.display = '';
                    if (detailsRow) {
                        // Only show details row if it was previously expanded
                        detailsRow.style.display = detailsRow.classList.contains('expanded') ? '' : 'none';
                    }
                } else {
                    row.style.display = 'none';
                    if (detailsRow) {
                        detailsRow.style.display = 'none';
                    }
                }
            });
        });
    }
    
    if (addUserForm) {
        addUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('/admin/add_user', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.error) {
                    showError(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Сталася помилка при створенні користувача');
            });
        });
    }

    // Добавляем обработчик для сортировки
    if (sortBy) {
        sortBy.addEventListener('change', function() {
            sortTable(this.value);
        });
    }

    // Проверяем, есть ли данные графика в глобальной области
    if (typeof window.chartData !== 'undefined') {
        initializeDashboard(window.chartData);
    }
});

// Admin Dashboard JavaScript

// Глобальные переменные
let expandedUsers = new Set();

function expandUserRow(userId) {
    const button = document.querySelector(`.user-row[data-user-id="${userId}"] .btn-expand`);
    const detailsRow = document.getElementById(`user-details-${userId}`);
    
    if (expandedUsers.has(userId)) {
        // Скрываем детали
        detailsRow.style.display = 'none';
        detailsRow.classList.remove('expanded');
        button.innerHTML = '<i class="fas fa-chevron-right"></i>';
        expandedUsers.delete(userId);
    } else {
        // Показываем детали
        detailsRow.style.display = 'table-row';
        detailsRow.classList.add('expanded');
        button.innerHTML = '<i class="fas fa-chevron-down"></i>';
        expandedUsers.add(userId);
        
        // Загружаем данные, если еще не загружены
        if (detailsRow.querySelector('.loading')) {
            fetch(`/api/admin/user_tests/${userId}`)
                .then(response => response.json())
                .then(data => {
                    let html = '<div class="user-details-content">';
                    
                    if (!data.brands || data.brands.length === 0) {
                        html += '<div class="no-data">У користувача немає результатів тестів</div>';
                    } else {
                        data.brands.forEach(brand => {
                            html += `
                                <div class="brand-section">
                                    <div class="brand-header" onclick="toggleBrandContent(this)">
                                        <div class="brand-title">
                                            <h4>${brand.name}</h4>
                                            <div class="brand-stats">
                                                <span class="brand-stat">Тести: <strong>${brand.stats.tests_count}</strong></span>
                                                <span class="brand-stat ${getScoreColorClass(brand.stats.avg_score)}">Бал: <strong>${brand.stats.avg_score}%</strong></span>
                                                <span class="brand-stat">Загальний час: <strong>${brand.stats.total_time_formatted}</strong></span>
                                                <span class="brand-stat">Середній час: <strong>${brand.stats.avg_time_formatted}</strong></span>
                                            </div>
                                        </div>
                                        <span class="toggle-icon"><i class="fas fa-chevron-right"></i></span>
                                    </div>
                                    <div class="brand-content" style="display: none;">
                            `;
                            
                            brand.materials.forEach(material => {
                                html += `
                                    <div class="material-section">
                                        <div class="material-header" onclick="toggleMaterialContent(this)">
                                            <h5>${material.title}</h5>
                                            <span class="toggle-icon"><i class="fas fa-chevron-right"></i></span>
                                        </div>
                                        <div class="material-content" style="display: none;">
                                `;
                                
                                if (!material.attempts || material.attempts.length === 0) {
                                    html += '<div class="no-attempts">Немає спроб проходження тесту</div>';
                                } else {
                                    html += `
                                        <table class="attempts-table">
                                            <thead>
                                                <tr>
                                                                                                    <th>Дата</th>
                                                <th class="text-center">Результат</th>
                                                <th class="text-center">Час</th>
                                                <th class="text-center">Статус</th>
                                                <th class="text-center">Дії</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                    `;
                                    
                                    material.attempts.forEach(attempt => {
                                        const statusClass = getScoreBadgeClass(attempt.score);
                                        const statusText = attempt.score >= 80 ? 'Відмінно' : attempt.score >= 60 ? 'Добре' : 'Незадовільно';
                                        
                                        // Правильное форматирование даты
                                        let formattedDate = 'N/A';
                                        if (attempt.date) {
                                            // Если дата уже отформатирована на сервере, используем её как есть
                                            formattedDate = attempt.date;
                                        }
                                        
                                        html += `
                                            <tr class="attempt-row">
                                                <td>${formattedDate}</td>
                                                <td class="text-center">
                                                    <span class="score-badge ${statusClass}">${attempt.score}%</span>
                                                </td>
                                                <td class="text-center">${attempt.time_taken || 'N/A'}</td>
                                                <td class="text-center">
                                                    <span class="status-badge ${statusClass}">${statusText}</span>
                                                </td>
                                                <td class="text-center">
                                                    <button class="btn btn-info btn-sm" onclick="toggleAttemptDetails(this)">
                                                        Показати відповіді
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr class="attempt-details-row" style="display: none;">
                                                <td colspan="5">
                                                    <div class="attempt-details">
                                                        <table class="questions-table">
                                                            <thead>
                                                                <tr>
                                                                                                                                    <th>Питання</th>
                                                                <th class="text-center">Відповідь користувача</th>
                                                                <th class="text-center">Правильна відповідь</th>
                                                                <th class="text-center">Результат</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                        `;
                                        
                                        attempt.question_details.forEach(detail => {
                                            const resultClass = detail.is_correct ? 'correct' : 'incorrect';
                                            const resultText = detail.is_correct ? 'Вірно' : 'Невірно';
                                            
                                            html += `
                                                <tr class="${resultClass}">
                                                    <td>${detail.question_text}</td>
                                                    <td class="text-center">${detail.user_answer}</td>
                                                    <td class="text-center">${detail.correct_answer}</td>
                                                    <td class="text-center">${resultText}</td>
                                                </tr>
                                            `;
                                        });
                                        
                                        html += `
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </td>
                                            </tr>
                                        `;
                                    });
                                    
                                    html += `
                                            </tbody>
                                        </table>
                                    `;
                                }
                                
                                html += `
                                        </div>
                                    </div>
                                `;
                            });
                            
                            html += `
                                    </div>
                                </div>
                            `;
                        });
                        
                        html += `
                                </div>
                            </div>
                        `;
                    }
                    
                    html += '</div>';
                    detailsRow.querySelector('td').innerHTML = html;
                })
                .catch(error => {
                    console.error('Error:', error);
                    detailsRow.querySelector('td').innerHTML = '<div class="error-message">Помилка при завантаженні даних</div>';
                });
        }
    }
}

function toggleBrandContent(header) {
    const content = header.nextElementSibling;
    const icon = header.querySelector('.toggle-icon');
    
    if (content.style.display === 'none' || !content.style.display) {
        content.style.display = 'block';
        icon.innerHTML = '<i class="fas fa-chevron-down"></i>';
    } else {
        content.style.display = 'none';
        icon.innerHTML = '<i class="fas fa-chevron-right"></i>';
    }
}

function toggleMaterialContent(header) {
    const content = header.nextElementSibling;
    const icon = header.querySelector('.toggle-icon');
    
    if (content.style.display === 'none' || !content.style.display) {
        content.style.display = 'block';
        icon.innerHTML = '<i class="fas fa-chevron-down"></i>';
    } else {
        content.style.display = 'none';
        icon.innerHTML = '<i class="fas fa-chevron-right"></i>';
    }
}

function toggleAttemptDetails(button) {
    const row = button.closest('tr');
    const detailsRow = row.nextElementSibling;
    const isVisible = detailsRow.style.display !== 'none';
    
    if (!isVisible) {
        detailsRow.style.display = 'table-row';
        button.innerHTML = 'Сховати відповіді';
    } else {
        detailsRow.style.display = 'none';
        button.innerHTML = 'Показати відповіді';
    }
}

function sortTable(sortType) {
    const tbody = document.querySelector('.users-table tbody');
    const rows = Array.from(tbody.querySelectorAll('.user-row'));
    
    rows.sort((a, b) => {
        let valueA, valueB;
        
        switch(sortType) {
            case 'name':
                valueA = a.dataset.username.toLowerCase();
                valueB = b.dataset.username.toLowerCase();
                return valueA.localeCompare(valueB);
                
            case 'tests':
                valueA = parseInt(a.dataset.testsCount) || 0;
                valueB = parseInt(b.dataset.testsCount) || 0;
                return valueB - valueA; // Сортировка по убыванию
                
            case 'score':
                valueA = parseFloat(a.dataset.avgScore) || 0;
                valueB = parseFloat(b.dataset.avgScore) || 0;
                return valueB - valueA; // Сортировка по убыванию
                
            case 'total_time':
                valueA = parseInt(a.dataset.totalTimeSeconds) || 0;
                valueB = parseInt(b.dataset.totalTimeSeconds) || 0;
                return valueB - valueA; // Сортировка по убыванию
                
            case 'avg_time':
                valueA = parseFloat(a.dataset.avgTimeSeconds) || 0;
                valueB = parseFloat(b.dataset.avgTimeSeconds) || 0;
                return valueB - valueA; // Сортировка по убыванию
                
            default:
                return 0;
        }
    });
    
    // Перемещаем строки с деталями вместе с основными строками
    rows.forEach((row, index) => {
        const userId = row.dataset.userId;
        const detailsRow = document.getElementById(`user-details-${userId}`);
        
        // Удаляем старые строки
        tbody.removeChild(row);
        if (detailsRow) {
            tbody.removeChild(detailsRow);
        }
        
        // Вставляем строки в новом порядке
        tbody.insertBefore(row, tbody.children[index * 2]);
        if (detailsRow) {
            tbody.insertBefore(detailsRow, tbody.children[index * 2 + 1]);
        }
    });
}

// Функция инициализации дашборда с данными графика
function initializeDashboard(chartData) {
    if (!chartData) {
        console.error('Chart data not provided');
        return;
    }
    
    const ctx = document.getElementById('testsChart');
    if (!ctx) {
        console.error('Chart canvas not found');
        return;
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: chartData.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

// Функция для определения CSS класса цвета по баллу
function getScoreColorClass(score) {
    if (score >= 80) return 'score-excellent';
    if (score >= 60) return 'score-good';
    return 'score-poor';
}

// Функция для определения CSS класса для бейджей
function getScoreBadgeClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    return 'poor';
} 