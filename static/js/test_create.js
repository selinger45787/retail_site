// JavaScript for test_create.html

let questionCount = 0;

function addQuestion() {
    const container = document.getElementById('questionsContainer');
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
                <input type="text" class="form-control" id="question_${questionCount}" name="questions[]" required>
            </div>
            <div class="mb-3">
                <label for="correct_${questionCount}" class="form-label">Правильна відповідь</label>
                <input type="text" class="form-control" id="correct_${questionCount}" name="correct_answers[]" required>
            </div>
            <div class="mb-3">
                <label for="wrong1_${questionCount}" class="form-label">Неправильна відповідь 1</label>
                <input type="text" class="form-control" id="wrong1_${questionCount}" name="wrong_answers_1[]" required>
            </div>
            <div class="mb-3">
                <label for="wrong2_${questionCount}" class="form-label">Неправильна відповідь 2</label>
                <input type="text" class="form-control" id="wrong2_${questionCount}" name="wrong_answers_2[]" required>
            </div>
            <div class="mb-3">
                <label for="wrong3_${questionCount}" class="form-label">Неправильна відповідь 3</label>
                <input type="text" class="form-control" id="wrong3_${questionCount}" name="wrong_answers_3[]" required>
            </div>
        </div>
    `;
    container.appendChild(questionDiv);
    questionCount++;
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

// Добавляем первый вопрос при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    addQuestion();
}); 