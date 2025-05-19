// JavaScript for test_create.html

let questionCount = 0;

function showFlashMessage(message, type = 'danger') {
    const flashContainer = document.getElementById('flash-messages');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    flashContainer.appendChild(alertDiv);
    
    // Автоматически скрываем сообщение через 5 секунд
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function checkDuplicateAnswers(questionDiv) {
    const answers = [
        questionDiv.querySelector('[name="correct_answers[]"]').value.trim(),
        questionDiv.querySelector('[name="wrong_answers_1[]"]').value.trim(),
        questionDiv.querySelector('[name="wrong_answers_2[]"]').value.trim(),
        questionDiv.querySelector('[name="wrong_answers_3[]"]').value.trim()
    ];
    
    const uniqueAnswers = new Set(answers);
    return uniqueAnswers.size === answers.length;
}

function validateForm() {
    const questions = document.querySelectorAll('.card');
    
    // Проверка минимального количества вопросов
    if (questions.length < 5) {
        showFlashMessage('Тест повинен містити мінімум 5 питань');
        return false;
    }
    
    // Проверка уникальности ответов для каждого вопроса
    for (const question of questions) {
        if (!checkDuplicateAnswers(question)) {
            showFlashMessage('Всі відповіді на одне питання повинні бути унікальними');
            return false;
        }
    }
    
    return true;
}

function addQuestion() {
    const container = document.getElementById('questionsContainer');
    const questionCount = container.querySelectorAll('.card').length;
    
    const questionDiv = document.createElement('div');
    questionDiv.className = 'card mb-4';
    questionDiv.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="card-title mb-0">Питання ${questionCount + 1}</h5>
                <button type="button" class="btn btn-danger btn-sm" onclick="removeQuestion(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="mb-3">
                <label for="question_${questionCount}" class="form-label">Питання</label>
                <input type="text" class="form-control" id="question_${questionCount}" 
                       name="questions[]" required>
            </div>
            <div class="mb-3">
                <label for="correct_${questionCount}" class="form-label">Правильна відповідь</label>
                <input type="text" class="form-control" id="correct_${questionCount}" 
                       name="correct_answers[]" required>
            </div>
            <div class="mb-3">
                <label for="wrong1_${questionCount}" class="form-label">Неправильна відповідь 1</label>
                <input type="text" class="form-control" id="wrong1_${questionCount}" 
                       name="wrong_answers_1[]" required>
            </div>
            <div class="mb-3">
                <label for="wrong2_${questionCount}" class="form-label">Неправильна відповідь 2</label>
                <input type="text" class="form-control" id="wrong2_${questionCount}" 
                       name="wrong_answers_2[]" required>
            </div>
            <div class="mb-3">
                <label for="wrong3_${questionCount}" class="form-label">Неправильна відповідь 3</label>
                <input type="text" class="form-control" id="wrong3_${questionCount}" 
                       name="wrong_answers_3[]" required>
            </div>
        </div>
    `;
    
    container.appendChild(questionDiv);
}

function removeQuestion(button) {
    const questionDiv = button.closest('.card');
    questionDiv.remove();
    updateQuestionNumbers();
}

function updateQuestionNumbers() {
    const questions = document.querySelectorAll('.card');
    questions.forEach((question, index) => {
        question.querySelector('.card-title').textContent = `Питання ${index + 1}`;
    });
}

// Добавляем первый вопрос при загрузке страницы, если нет сохраненных данных
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем первый вопрос при загрузке страницы, если нет сохраненных данных
    if (document.querySelectorAll('.card').length === 0) {
        addQuestion();
    }

    // Добавляем контейнер для flash-сообщений, если его нет
    if (!document.getElementById('flash-messages')) {
        const flashContainer = document.createElement('div');
        flashContainer.id = 'flash-messages';
        flashContainer.className = 'container mt-3';
        document.querySelector('form').insertAdjacentElement('beforebegin', flashContainer);
    }
    
    // Добавляем обработчик отправки формы
    const form = document.getElementById('testForm');
    const submitButton = form.querySelector('button[type="submit"]');
    let isSubmitting = false;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (isSubmitting) {
            return;
        }
        
        if (validateForm()) {
            // Если форма валидна, отправляем её
            isSubmitting = true;
            this.submit();
        }
    });
}); 