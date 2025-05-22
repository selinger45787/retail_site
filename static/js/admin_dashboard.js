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
                const userName = row.querySelector('td:first-child').textContent.toLowerCase();
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
    const detailsRow = document.getElementById(`user-details-${userId}`);
    const loadingIndicator = detailsRow.querySelector('.loading-indicator');
    const userDetails = detailsRow.querySelector('.user-details');
    const expandButton = document.querySelector(`.user-row[data-user-id="${userId}"] .btn-expand i`);
    const userRow = document.querySelector(`.user-row[data-user-id="${userId}"]`);
    
    if (detailsRow.classList.contains('expanded')) {
        detailsRow.classList.remove('expanded');
        detailsRow.style.display = 'none';
        expandButton.classList.remove('fa-chevron-up');
        expandButton.classList.add('fa-chevron-down');
        return;
    }
    
    loadingIndicator.style.display = 'flex';
    userDetails.style.display = 'none';
    detailsRow.classList.add('expanded');
    detailsRow.style.display = '';
    expandButton.classList.remove('fa-chevron-down');
    expandButton.classList.add('fa-chevron-up');
    
    console.log('Fetching data for user:', userId);
    fetch(`/api/admin/user_tests/${userId}`)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            loadingIndicator.style.display = 'none';
            userDetails.style.display = 'block';
            
            // Обновляем количество тестов и средний балл
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
            const testCountCell = userRow.querySelector('td:nth-child(2)');
            const avgScoreCell = userRow.querySelector('td:nth-child(3)');
            
            testCountCell.textContent = attemptsCount;
            avgScoreCell.textContent = avgScore + '%';
            
            let html = '';
            
            if (data.brands && data.brands.length > 0) {
                console.log('Processing brands:', data.brands);
                data.brands.forEach(brand => {
                    html += `
                        <div class="brand-section">
                            <h3 class="brand-header" onclick="toggleAccordion(this)">
                                <i class="fas fa-chevron-right"></i>
                                ${brand.name}
                            </h3>
                            <div class="brand-content" style="display: none;">
                    `;
                    
                    brand.materials.forEach(material => {
                        console.log('Processing material:', material);
                        html += `
                            <div class="material-section">
                                <h4 class="material-header" onclick="toggleAccordion(this)">
                                    <i class="fas fa-chevron-right"></i>
                                    ${material.title}
                                </h4>
                                <div class="material-content" style="display: none;">
                                    <table class="test-history">
                                        <thead>
                                            <tr>
                                                <th>Дата</th>
                                                <th>Балл</th>
                                                <th>Правильных</th>
                                                <th>Неправильных</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        `;
                        
                        material.attempts.forEach(attempt => {
                            // Определяем класс для оценки
                            let scoreClass = 'score-low';
                            if (attempt.score >= 80) {
                                scoreClass = 'score-high';
                            } else if (attempt.score >= 60) {
                                scoreClass = 'score-medium';
                            }
                            
                            html += `
                                <tr class="test-row" onclick="window.location.href='/view_material/${material.id}'" style="cursor: pointer;">
                                    <td>${attempt.date}</td>
                                    <td class="${scoreClass}">${attempt.score}%</td>
                                    <td>${attempt.correct_answers}</td>
                                    <td>${attempt.wrong_answers}</td>
                                </tr>
                            `;
                        });
                        
                        html += `
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += `
                            </div>
                        </div>
                    `;
                });
            } else {
                html = '<p class="no-data">Нет данных о результатах тестов</p>';
            }
            
            userDetails.innerHTML = html;
        })
        .catch(error => {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            userDetails.innerHTML = '<p class="error">Ошибка при загрузке данных</p>';
        });
}

function toggleAccordion(header) {
    const content = header.nextElementSibling;
    const chevron = header.querySelector('i');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        chevron.classList.remove('fa-chevron-right');
        chevron.classList.add('fa-chevron-down');
    } else {
        content.style.display = 'none';
        chevron.classList.remove('fa-chevron-down');
        chevron.classList.add('fa-chevron-right');
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
            const testCountCell = userRow.querySelector('td:nth-child(2)');
            const avgScoreCell = userRow.querySelector('td:nth-child(3)');
            
            testCountCell.textContent = attemptsCount;
            avgScoreCell.textContent = avgScore + '%';
        })
        .catch(error => {
            console.error('Error loading user stats:', error);
        });
}

// Функция сортировки таблицы
function sortTable(sortType) {
    const tbody = document.querySelector('.users-table tbody');
    const rows = Array.from(tbody.querySelectorAll('.user-row'));
    
    rows.sort((a, b) => {
        let valueA, valueB;
        
        switch(sortType) {
            case 'name':
                valueA = a.querySelector('td:first-child').textContent.toLowerCase();
                valueB = b.querySelector('td:first-child').textContent.toLowerCase();
                return valueA.localeCompare(valueB);
                
            case 'tests':
                valueA = parseInt(a.querySelector('td:nth-child(2)').textContent) || 0;
                valueB = parseInt(b.querySelector('td:nth-child(2)').textContent) || 0;
                return valueB - valueA; // Сортировка по убыванию
                
            case 'score':
                valueA = parseInt(a.querySelector('td:nth-child(3)').textContent) || 0;
                valueB = parseInt(b.querySelector('td:nth-child(3)').textContent) || 0;
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