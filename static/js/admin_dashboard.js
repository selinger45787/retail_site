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

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    
    const form = document.getElementById('addUserForm');
    form.insertBefore(errorDiv, form.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function expandUserRow(userId) {
    const row = document.querySelector(`tr[data-user-id="${userId}"]`);
    const detailsRow = document.getElementById(`user-details-${userId}`);
    const button = row.querySelector('.btn-expand');
    
    if (detailsRow.style.display === 'none' || !detailsRow.style.display) {
        detailsRow.style.display = 'table-row';
        button.innerHTML = '<i class="fas fa-chevron-down"></i>';
        
        // Загружаем данные только если они еще не загружены
        if (detailsRow.querySelector('.loading')) {
            fetch(`/api/admin/user_tests/${userId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        detailsRow.querySelector('td').innerHTML = `<div class="error-message">${data.error}</div>`;
                        return;
                    }
                    
                    let html = '<div class="user-details">';
                    
                    // Общая статистика
                    let totalAttempts = 0;
                    let totalScore = 0;
                    
                    data.brands.forEach(brand => {
                        brand.materials.forEach(material => {
                            totalAttempts += material.attempts.length;
                            material.attempts.forEach(attempt => {
                                totalScore += attempt.score;
                            });
                        });
                    });
                    
                    const avgScore = totalAttempts > 0 ? (totalScore / totalAttempts).toFixed(1) : 0;
                    
                    html += `
                        <div class="user-stats">
                            <h4>Общая статистика</h4>
                            <p>Всего попыток: ${totalAttempts}</p>
                            <p>Средний балл: ${avgScore}%</p>
                        </div>
                    `;
                    
                    // Детальная информация по брендам и материалам
                    data.brands.forEach(brand => {
                        // Считаем статистику по бренду
                        let brandAttempts = 0;
                        let brandTotalScore = 0;
                        
                        brand.materials.forEach(material => {
                            brandAttempts += material.attempts.length;
                            material.attempts.forEach(attempt => {
                                brandTotalScore += attempt.score;
                            });
                        });
                        
                        const brandAvgScore = brandAttempts > 0 ? (brandTotalScore / brandAttempts).toFixed(1) : 0;
                        
                        html += `
                            <div class="brand-section">
                                <div class="brand-header" onclick="toggleBrandContent(this)">
                                    <h3>${brand.name}</h3>
                                    <div class="brand-stats">
                                        <span>Попыток: ${brandAttempts}</span>
                                        <span>Средний балл: ${brandAvgScore}%</span>
                                    </div>
                                    <span class="toggle-icon"><i class="fas fa-chevron-right"></i></span>
                                </div>
                                <div class="brand-content" style="display: none;">
                        `;
                        
                        brand.materials.forEach(material => {
                            html += `
                                <div class="material-section">
                                    <div class="material-header" onclick="toggleMaterialContent(this)">
                                        <h4>${material.title}</h4>
                                        <span class="toggle-icon"><i class="fas fa-chevron-right"></i></span>
                                    </div>
                                    <div class="material-content" style="display: none;">
                            `;
                            
                            if (material.attempts.length === 0) {
                                html += '<p>Нет попыток прохождения теста</p>';
                            } else {
                                html += `
                                    <table class="attempts-table">
                                        <thead>
                                            <tr>
                                                <th>Дата</th>
                                                <th class="text-center">Балл</th>
                                                <th class="text-center">Правильных</th>
                                                <th class="text-center">Неправильных</th>
                                                <th class="text-center">Действия</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                `;
                                
                                material.attempts.forEach(attempt => {
                                    html += `
                                        <tr>
                                            <td>${attempt.date}</td>
                                            <td class="text-center">${attempt.score}%</td>
                                            <td class="text-center">${attempt.correct_answers}</td>
                                            <td class="text-center">${attempt.wrong_answers}</td>
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
                    
                    html += '</div>';
                    detailsRow.querySelector('td').innerHTML = html;
                })
                .catch(error => {
                    console.error('Error:', error);
                    detailsRow.querySelector('td').innerHTML = '<div class="error-message">Ошибка при загрузке данных</div>';
                });
        }
    } else {
        detailsRow.style.display = 'none';
        button.innerHTML = '<i class="fas fa-chevron-right"></i>';
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