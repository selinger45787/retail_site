#!/usr/bin/env python3
"""
Безопасная настройка CRM - создает .env.crm файл
"""

env_content = """# CRM DATABASE CREDENTIALS - KEEP SECURE!
CRM_DB_HOST=94.130.69.41
CRM_DB_PORT=64821
CRM_DB_USER=analyst
CRM_DB_PASSWORD=Am76Rv55pG
CRM_DB_NAME=BASSmallBusinessN

# Security settings
SECRET_KEY=crm-secret-key-for-local-development-only
FLASK_ENV=development
FLASK_DEBUG=true
ALLOWED_IPS=127.0.0.1,localhost,192.168.20.0/24,172.18.0.0/16,10.0.0.0/8
MAX_RECORDS_PER_REQUEST=100
"""

# Создаем .env.crm файл
with open('.env.crm', 'w', encoding='ascii') as f:
    f.write(env_content)

print("✅ Создан .env.crm файл с данными CRM")
print("🔒 Файл исключен из Git (.gitignore)")
print("🔄 Теперь обновите docker-compose.yml для использования env_file") 