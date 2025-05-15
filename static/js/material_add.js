// JavaScript for material_add.html

// Add your custom scripts here

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, инициализация формы...');
    
    const form = document.getElementById('addMaterialForm');
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('imagePreview');
    const addImageBtn = document.getElementById('addImageBtn');
    const additionalImagesContainer = document.getElementById('additionalImagesContainer');
    let editor = null;

    console.log('Элементы формы:', {
        form: form,
        imageInput: imageInput,
        imagePreview: imagePreview,
        addImageBtn: addImageBtn,
        additionalImagesContainer: additionalImagesContainer
    });

    // Инициализация CKEditor
    DecoupledEditor
        .create(document.querySelector('#description'), {
            language: 'uk',
            toolbar: {
                items: [
                    'heading',
                    '|',
                    'fontSize',
                    'fontFamily',
                    '|',
                    'fontColor',
                    'fontBackgroundColor',
                    '|',
                    'bold',
                    'italic',
                    'underline',
                    'strikethrough',
                    '|',
                    'alignment',
                    '|',
                    'numberedList',
                    'bulletedList',
                    '|',
                    'outdent',
                    'indent',
                    '|',
                    'link',
                    'blockQuote',
                    'insertTable',
                    '|',
                    'undo',
                    'redo'
                ],
                shouldNotGroupWhenFull: true
            },
            placeholder: 'Введіть опис матеріалу...',
            table: {
                contentToolbar: [
                    'tableColumn',
                    'tableRow',
                    'mergeTableCells'
                ]
            }
        })
        .then(newEditor => {
            console.log('CKEditor успешно инициализирован');
            editor = newEditor;
            
            const toolbarContainer = document.querySelector('.toolbar-container');
            toolbarContainer.appendChild(editor.ui.view.toolbar.element);
            
            // Добавляем слушатель изменений
            editor.model.document.on('change:data', () => {
                const data = editor.getData();
                console.log('Текущее содержимое редактора:', data);
                // Обновляем значение textarea
                document.getElementById('description').value = data;
            });
        })
        .catch(error => {
            console.error('Ошибка при инициализации CKEditor:', error);
        });

    // Обработка отправки формы
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log('Форма отправляется...');
        
        // Проверяем, инициализирован ли редактор
        if (!editor) {
            console.error('Редактор еще не инициализирован');
            alert('Будь ласка, зачекайте поки редактор завантажиться');
            return;
        }
        
        // Получаем данные из CKEditor
        const description = editor.getData();
        console.log('Данные из CKEditor перед отправкой:', description);
        
        // Проверяем все обязательные поля
        const title = document.getElementById('title').value;
        const categoryId = document.getElementById('category_id').value;
        const brandId = document.getElementById('brand_id') ? document.getElementById('brand_id').value : null;
        
        console.log('Form data before submit:', {
            title,
            description,
            categoryId,
            brandId
        });
        
        // Если все поля заполнены, отправляем форму
        if (title && description && categoryId && (brandId || !document.getElementById('brand_id'))) {
            // Устанавливаем значение из редактора в textarea
            document.getElementById('description').value = description;
            console.log('Submitting form with description:', document.getElementById('description').value);
            form.submit();
        } else {
            alert('Будь ласка, заповніть всі обов\'язкові поля');
        }
    });

    // Предпросмотр изображения
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            }
            reader.readAsDataURL(file);
        } else {
            imagePreview.innerHTML = '';
        }
    });

    // Добавление нового поля для изображения
    if (addImageBtn) {
        console.log('Кнопка добавления изображения найдена');
        
        // Проверяем, что обработчик события добавляется
        addImageBtn.onclick = function(e) {
            console.log('Кнопка нажата (onclick)');
            e.preventDefault();
            e.stopPropagation();
        };

        addImageBtn.addEventListener('click', function(e) {
            console.log('Кнопка нажата (addEventListener)');
            e.preventDefault();
            e.stopPropagation();
            
            const newInput = document.createElement('div');
            newInput.className = 'additional-image-input mb-2';
            newInput.innerHTML = `
                <div class="input-group">
                    <input type="file" class="form-control" name="additional_images" accept="image/*">
                    <button type="button" class="btn btn-danger remove-image">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            console.log('Создан новый элемент:', newInput);
            additionalImagesContainer.appendChild(newInput);
            console.log('Элемент добавлен в контейнер');

            // Добавляем обработчик для кнопки удаления
            const removeBtn = newInput.querySelector('.remove-image');
            if (removeBtn) {
                removeBtn.addEventListener('click', function() {
                    console.log('Кнопка удаления нажата');
                    newInput.remove();
                });
            }
        });
    } else {
        console.error('Кнопка добавления изображения не найдена');
    }
}); 