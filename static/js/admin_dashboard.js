document.addEventListener('DOMContentLoaded', function() {
    const addUserForm = document.getElementById('addUserForm');
    
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
    
    if (detailsRow.classList.contains('expanded')) {
        detailsRow.classList.remove('expanded');
        expandButton.classList.remove('fa-chevron-up');
        expandButton.classList.add('fa-chevron-down');
        return;
    }
    
    loadingIndicator.style.display = 'flex';
    userDetails.style.display = 'none';
    detailsRow.classList.add('expanded');
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
                                <div class="attempt-section">
                                    <div class="attempt-header" onclick="toggleAccordion(this)">
                                        <i class="fas fa-chevron-right"></i>
                                        <span>Тест от ${attempt.date}</span>
                                        <span class="attempt-score ${scoreClass}">${attempt.score}%</span>
                                    </div>
                                    <div class="attempt-content" style="display: none;">
                                        <div class="attempt-summary">
                                            <div class="attempt-stats">
                                                <span class="attempt-correct">Правильных: ${attempt.correct_answers}</span>
                                                <span class="attempt-wrong">Неправильных: ${attempt.wrong_answers}</span>
                                            </div>
                                        </div>
                                        ${attempt.question_details && attempt.question_details.length > 0 ? `
                                            <div class="questions-section">
                                                <h5>Детали ответов:</h5>
                                                <table class="questions-table">
                                                    <thead>
                                                        <tr>
                                                            <th>Вопрос</th>
                                                            <th>Ответ пользователя</th>
                                                            <th>Правильный ответ</th>
                                                            <th>Результат</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        ${attempt.question_details.map(question => `
                                                            <tr class="${question.is_correct ? 'correct-answer' : 'wrong-answer'}">
                                                                <td>${question.question_text}</td>
                                                                <td>${question.user_answer}</td>
                                                                <td>${question.correct_answer}</td>
                                                                <td>
                                                                    ${question.is_correct 
                                                                        ? '<i class="fas fa-check text-success"></i>' 
                                                                        : '<i class="fas fa-times text-danger"></i>'}
                                                                </td>
                                                            </tr>
                                                        `).join('')}
                                                    </tbody>
                                                </table>
                                            </div>
                                        ` : '<p class="no-details">Детальная информация по вопросам недоступна</p>'}
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