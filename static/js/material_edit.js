// JavaScript for material_edit.html

// Remove this comment and keep only necessary scripts. 

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация CKEditor
    let editor;
    DecoupledEditor
        .create(document.querySelector('#editor-container'))
        .then(newEditor => {
            editor = newEditor;
            const toolbarContainer = document.querySelector('.toolbar-container');
            toolbarContainer.appendChild(editor.ui.view.toolbar.element);
            
            // Устанавливаем начальное содержимое
            editor.setData(document.querySelector('#description').value);
        })
        .catch(error => {
            console.error(error);
        });

    // Обработка формы
    const form = document.getElementById('editMaterialForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Обновляем содержимое textarea перед отправкой
        document.querySelector('#description').value = editor.getData();
        
        // Отправляем форму
        this.submit();
    });

    // Предпросмотр главного изображения
    const mainImageInput = document.getElementById('image');
    const imagePreview = document.getElementById('imagePreview');
    
    mainImageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `
                    <img src="${e.target.result}" class="img-thumbnail mt-2" style="max-height: 200px;">
                `;
            };
            reader.readAsDataURL(file);
        }
    });

    // Добавление полей для дополнительных изображений
    const addImageBtn = document.getElementById('addImageBtn');
    const additionalImagesContainer = document.getElementById('additionalImagesContainer');
    
    addImageBtn.addEventListener('click', function() {
        const newInput = document.createElement('div');
        newInput.className = 'additional-image-input mb-2';
        newInput.innerHTML = `
            <div class="input-group">
                <input type="file" class="form-control" name="additional_images" accept="image/*">
                <button type="button" class="btn btn-danger remove-input">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        additionalImagesContainer.appendChild(newInput);
    });

    // Удаление полей для дополнительных изображений
    additionalImagesContainer.addEventListener('click', function(e) {
        if (e.target.closest('.remove-input')) {
            e.target.closest('.additional-image-input').remove();
        }
    });

    // Удаление существующих дополнительных изображений
    const removeImageButtons = document.querySelectorAll('.remove-image');
    removeImageButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const imageId = this.getAttribute('data-image-id');
            const confirmed = confirm('Ви впевнені, що хочете видалити це зображення?');
            
            if (confirmed) {
                try {
                    const response = await fetch(`/material/image/${imageId}/delete`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                        }
                    });
                    
                    if (response.ok) {
                        this.closest('.additional-image-item').remove();
                    } else {
                        alert('Помилка при видаленні зображення');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Помилка при видаленні зображення');
                }
            }
        });
    });
}); 