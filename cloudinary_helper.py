import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app
import os

def configure_cloudinary():
    """Настраивает Cloudinary с переменными окружения"""
    if current_app.config.get('CLOUDINARY_CLOUD_NAME'):
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET'],
            secure=True
        )
        return True
    return False

def upload_image(file, folder="materials"):
    """
    Загружает изображение в Cloudinary
    
    Args:
        file: файл изображения
        folder: папка в Cloudinary
    
    Returns:
        dict: результат загрузки с URL и public_id
    """
    try:
        # Настраиваем Cloudinary
        if not configure_cloudinary():
            raise Exception("Cloudinary не настроен")
        
        # Загружаем файл
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
            format="webp",  # Автоматическое сжатие в WebP
            quality="auto",  # Автоматическая оптимизация качества
            fetch_format="auto"  # Автоматический формат
        )
        
        return {
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'success': True
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }

def delete_image(public_id):
    """
    Удаляет изображение из Cloudinary
    
    Args:
        public_id: ID изображения в Cloudinary
    
    Returns:
        bool: успешность удаления
    """
    try:
        if not configure_cloudinary():
            return False
            
        cloudinary.uploader.destroy(public_id)
        return True
        
    except Exception:
        return False

def get_optimized_url(public_id, width=None, height=None, quality="auto"):
    """
    Генерирует оптимизированный URL изображения
    
    Args:
        public_id: ID изображения в Cloudinary
        width: ширина
        height: высота
        quality: качество
    
    Returns:
        str: оптимизированный URL
    """
    try:
        if not configure_cloudinary():
            return None
            
        transformation = {
            'quality': quality,
            'fetch_format': 'auto'
        }
        
        if width:
            transformation['width'] = width
        if height:
            transformation['height'] = height
            
        if width or height:
            transformation['crop'] = 'fill'
            
        url = cloudinary.CloudinaryImage(public_id).build_url(**transformation)
        return url
        
    except Exception:
        return None 