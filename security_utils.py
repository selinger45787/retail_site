import os
from werkzeug.utils import secure_filename
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# Разрешенные MIME типы для изображений
ALLOWED_IMAGE_MIME_TYPES = {
    'image/jpeg',
    'image/jpg', 
    'image/png',
    'image/gif',
    'image/webp'
}

# Разрешенные расширения файлов
ALLOWED_IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp'
}

# Максимальный размер файла (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

def validate_image_file(file):
    """
    Проверяет, является ли загружаемый файл допустимым изображением
    
    Args:
        file: FileStorage объект из Flask
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    try:
        # Проверяем, что файл не пустой
        if not file or not file.filename:
            return False, "Файл не выбран"
        
        # Проверяем MIME тип
        if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
            return False, f"Недопустимый тип файла: {file.content_type}. Разрешены только изображения."
        
        # Проверяем расширение файла
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            return False, f"Недопустимое расширение файла: {file_ext}. Разрешены: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        
        # Проверяем размер файла
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return False, f"Файл слишком большой: {file_size / (1024*1024):.1f}MB. Максимальный размер: {MAX_FILE_SIZE / (1024*1024)}MB"
        
        # Дополнительная проверка на основе содержимого файла
        file.seek(0)
        try:
            # Читаем первые 512 байт для определения типа
            header = file.read(512)
            file.seek(0)
            
            # Проверяем магические байты для основных форматов изображений
            if not is_valid_image_header(header):
                return False, "Файл не является допустимым изображением"
                
        except Exception as e:
            logger.warning(f"Не удалось проверить заголовок файла: {e}")
            # Продолжаем, если не удалось прочитать заголовок
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Ошибка при валидации файла: {e}")
        return False, "Ошибка при проверке файла"

def is_valid_image_header(header):
    """
    Проверяет магические байты файла для определения типа изображения
    
    Args:
        header: первые байты файла
        
    Returns:
        bool: True если файл является изображением
    """
    if not header:
        return False
    
    # JPEG
    if header.startswith(b'\xff\xd8\xff'):
        return True
    
    # PNG
    if header.startswith(b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'):
        return True
    
    # GIF
    if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
        return True
    
    # WebP
    if b'WEBP' in header[:20]:
        return True
    
    return False

def generate_secure_filename(filename):
    """
    Генерирует безопасное имя файла с временной меткой
    
    Args:
        filename: оригинальное имя файла
        
    Returns:
        str: безопасное имя файла
    """
    from datetime import datetime
    
    # Получаем безопасное имя файла
    secure_name = secure_filename(filename)
    
    if not secure_name:
        # Если имя файла полностью "плохое", создаем стандартное
        ext = os.path.splitext(filename)[1].lower()
        if ext in ALLOWED_IMAGE_EXTENSIONS:
            secure_name = f"image{ext}"
        else:
            secure_name = "image.jpg"
    
    # Добавляем временную метку для уникальности
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
    name, ext = os.path.splitext(secure_name)
    
    return f"{timestamp}{name}{ext}"

def sanitize_path(path):
    """
    Очищает путь от потенциально опасных символов
    
    Args:
        path: путь для очистки
        
    Returns:
        str: очищенный путь
    """
    # Удаляем потенциально опасные символы
    dangerous_chars = ['..', '~', '$', '&', '|', ';', '`', '!', '"', "'", '<', '>']
    
    for char in dangerous_chars:
        path = path.replace(char, '_')
    
    # Нормализуем путь
    path = os.path.normpath(path)
    
    # Убираем ведущие слеши для предотвращения absolute paths
    path = path.lstrip('/')
    
    return path 