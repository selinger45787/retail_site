// Index page JavaScript

// Переменные для модального окна выбора действия
let currentMaterialId = null;

function showLoginModal() {
  const modal = document.getElementById('loginModal');
  modal.classList.add('show');
  modal.style.display = 'flex';
  setTimeout(() => modal.classList.add('visible'), 10);
}

function closeLoginModal() {
  const modal = document.getElementById('loginModal');
  modal.classList.remove('visible');
  setTimeout(() => modal.style.display = 'none', 300);
}

function submitLoginForm() {
  const formData = new FormData(document.getElementById('login-form'));
  const errorElement = document.getElementById('login-error');
  errorElement.innerText = '';
  
  fetch("/login_modal", {
    method: "POST",
    body: formData,
    headers: {
      'Accept': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    if (data.success) {
      closeLoginModal();
      window.location.reload();
    } else {
      errorElement.innerText = data.message || 'Помилка входу';
    }
  })
  .catch(error => {
    console.error('Помилка при відправці форми:', error);
    errorElement.innerText = 'Помилка з\'єднання з сервером. Спробуйте пізніше.';
  });
}

// Функции для модального окна выбора действия для теста
function showTestActionModal(materialId, materialTitle) {
  currentMaterialId = materialId;
  const modal = document.getElementById('testActionModal');
  const titleElement = modal.querySelector('.modal-material-title');
  
  // Устанавливаем название материала
  titleElement.textContent = `Матеріал: ${materialTitle}`;
  
  // Показываем модальное окно с плавной анимацией
  modal.style.display = 'flex';
  setTimeout(() => modal.classList.add('show'), 10);
}

function closeTestActionModal() {
  const modal = document.getElementById('testActionModal');
  modal.classList.remove('show');
  setTimeout(() => {
    modal.style.display = 'none';
    currentMaterialId = null;
  }, 400);
}

function viewMaterial() {
  if (currentMaterialId) {
    window.location.href = `/material/${currentMaterialId}`;
  }
}

function startTest() {
  if (currentMaterialId) {
    window.location.href = `/material/${currentMaterialId}/test`;
  }
}

// Закрытие модального окна при клике на backdrop
document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('testActionModal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeTestActionModal();
      }
    });
  }
}); 