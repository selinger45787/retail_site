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
                showError('Произошла ошибка при создании пользователя');
            });
        });
    }

    // Добавляем обработчик для сортировки
    if (sortBy) {
        sortBy.addEventListener('change', function() {
            sortTable(this.value);
        });
    }

    // Загружаем статистику для всех пользователей
    const userRows = document.querySelectorAll('.user-row');
    userRows.forEach(row => {
        const userId = row.dataset.userId;
        loadUserStats(userId);
    });
});

// Admin Dashboard JavaScript

// Глобальные переменные
let expandedUsers = new Set();

// Функции для работы с уведомлениями
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    // Автоматически скрыть через 5 секунд
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    // Автоматически скрыть через 5 секунд
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

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
                        html += '<div class="no-data">У пользователя нет результатов тестов</div>';
                    } else {
                        data.brands.forEach(brand => {
                            html += `
                                <div class="brand-section">
                                    <div class="brand-header" onclick="toggleBrandContent(this)">
                                        <h4>${brand.name}</h4>
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
                                    html += '<div class="no-attempts">Нет попыток прохождения теста</div>';
                                } else {
                                    html += `
                                        <table class="attempts-table">
                                            <thead>
                                                <tr>
                                                    <th>Дата</th>
                                                    <th class="text-center">Результат</th>
                                                    <th class="text-center">Время</th>
                                                    <th class="text-center">Статус</th>
                                                    <th class="text-center">Действия</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                    `;
                                    
                                    material.attempts.forEach(attempt => {
                                        const statusClass = attempt.score >= 80 ? 'success' : attempt.score >= 60 ? 'warning' : 'danger';
                                        const statusText = attempt.score >= 80 ? 'Отлично' : attempt.score >= 60 ? 'Хорошо' : 'Неудовлетворительно';
                                        
                                        html += `
                                            <tr class="attempt-row">
                                                <td>${new Date(attempt.completed_at).toLocaleDateString('uk-UA')}</td>
                                                <td class="text-center">
                                                    <span class="score-badge ${statusClass}">${attempt.score}%</span>
                                                </td>
                                                <td class="text-center">${attempt.time_taken || 'N/A'}</td>
                                                <td class="text-center">
                                                    <span class="status-badge ${statusClass}">${statusText}</span>
                                                </td>
                                                <td class="text-center">
                                                    <button class="btn btn-info btn-sm" onclick="toggleAttemptDetails(this)">
                                                        Показать ответы
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr class="attempt-details-row" style="display: none;">
                                                <td colspan="5">
                                                    <div class="attempt-details">
                                                        <table class="questions-table">
                                                            <thead>
                                                                <tr>
                                                                    <th>Вопрос</th>
                                                                    <th class="text-center">Ответ пользователя</th>
                                                                    <th class="text-center">Правильный ответ</th>
                                                                    <th class="text-center">Результат</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                        `;
                                        
                                        attempt.question_details.forEach(detail => {
                                            const resultClass = detail.is_correct ? 'correct' : 'incorrect';
                                            const resultText = detail.is_correct ? 'Верно' : 'Неверно';
                                            
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
                    detailsRow.querySelector('td').innerHTML = '<div class="error-message">Ошибка при загрузке данных</div>';
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
        button.innerHTML = 'Скрыть ответы';
    } else {
        detailsRow.style.display = 'none';
        button.innerHTML = 'Показать ответы';
    }
}

function loadUserStats(userId) {
    fetch(`/api/admin/user_tests/${userId}`)
        .then(response => response.json())
        .then(data => {
            const userRow = document.querySelector(`.user-row[data-user-id="${userId}"]`);
            if (!userRow) return;

            let totalTests = 0;
            let totalScore = 0;
            let attemptsCount = 0;
            
            if (data.brands && data.brands.length > 0) {
                data.brands.forEach(brand => {
                    brand.materials.forEach(material => {
                        if (material.attempts) {
                            attemptsCount += material.attempts.length;
                            material.attempts.forEach(attempt => {
                                totalScore += attempt.score;
                                totalTests++;
                            });
                        }
                    });
                });
            }
            
            const avgScore = totalTests > 0 ? Math.round(totalScore / totalTests) : 0;
            
            // Обновляем ячейки в таблице
            const testCountCell = userRow.querySelector('td:nth-child(3)');
            const avgScoreCell = userRow.querySelector('td:nth-child(4)');
            
            testCountCell.textContent = attemptsCount;
            avgScoreCell.textContent = avgScore + '%';
        })
        .catch(error => {
            console.error('Error loading user stats:', error);
        });
}

function sortTable(sortType) {
    const tbody = document.querySelector('.users-table tbody');
    const rows = Array.from(tbody.querySelectorAll('.user-row'));
    
    rows.sort((a, b) => {
        let valueA, valueB;
        
        switch(sortType) {
            case 'name':
                valueA = a.querySelector('td:nth-child(2)').textContent.toLowerCase();
                valueB = b.querySelector('td:nth-child(2)').textContent.toLowerCase();
                return valueA.localeCompare(valueB);
                
            case 'tests':
                valueA = parseInt(a.querySelector('td:nth-child(3)').textContent) || 0;
                valueB = parseInt(b.querySelector('td:nth-child(3)').textContent) || 0;
                return valueB - valueA; // Сортировка по убыванию
                
            case 'score':
                valueA = parseInt(a.querySelector('td:nth-child(4)').textContent) || 0;
                valueB = parseInt(b.querySelector('td:nth-child(4)').textContent) || 0;
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

// Инициализация графика и анимаций
function initializeDashboard(chartData) {
    // Анимация появления элементов при прокрутке
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Наблюдаем за элементами с классом fade-in
    document.querySelectorAll('.fade-in').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });

    // Инициализация графика
    const ctx = document.getElementById('testsChart');
    if (ctx && chartData) {
        new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: chartData.map(item => {
                    const date = new Date(item.date);
                    return date.toLocaleDateString('uk-UA', {day: '2-digit', month: '2-digit'});
                }),
                datasets: [{
                    label: 'Середній бал',
                    data: chartData.map(item => item.value),
                    backgroundColor: 'rgba(108, 117, 125, 0.2)',
                    borderColor: 'rgba(108, 117, 125, 1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgba(108, 117, 125, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: {
                                size: 14
                            },
                            color: '#495057'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(73, 80, 87, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#6c757d',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return `Середній бал: ${context.raw.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Середній бал (%)',
                            font: {
                                size: 14
                            },
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(108, 117, 125, 0.1)'
                        },
                        ticks: {
                            color: '#6c757d'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Дата',
                            font: {
                                size: 14
                            },
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(108, 117, 125, 0.1)'
                        },
                        ticks: {
                            color: '#6c757d'
                        }
                    }
                }
            }
        });
    }
} 