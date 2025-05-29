// Index page JavaScript

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
    console.error('Ошибка при отправке формы:', error);
    errorElement.innerText = 'Помилка з\'єднання з сервером. Спробуйте пізніше.';
  });
} 