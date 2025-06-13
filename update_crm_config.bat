@echo off
echo ========================================
echo   ОБНОВЛЕНИЕ КОНФИГУРАЦИИ CRM
echo ========================================
echo.

echo Обновляем .env файл с правильными данными CRM сервера...

cd crm_service

if exist .env (
    echo Создаем резервную копию существующего .env...
    copy .env .env.backup
    
    echo Обновляем конфигурацию базы данных...
    
    REM Обновляем все параметры базы данных
    powershell -Command "(Get-Content .env) -replace 'CRM_DB_HOST=.*', 'CRM_DB_HOST=94.130.69.41' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'CRM_DB_PORT=.*', 'CRM_DB_PORT=64821' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'CRM_DB_USER=.*', 'CRM_DB_USER=analyst' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'CRM_DB_PASSWORD=.*', 'CRM_DB_PASSWORD=Am76Rv55pG' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'CRM_DB_NAME=.*', 'CRM_DB_NAME=BASSmallBusinessN' | Set-Content .env"
    
    echo ✅ Конфигурация обновлена
    echo ✅ Резервная копия: .env.backup
) else (
    echo Создаем новый .env файл...
    
    echo # ================================= > .env
    echo # CRM SERVICE CONFIGURATION >> .env
    echo # ================================= >> .env
    echo # ВАЖНО: Этот файл НЕ должен попадать в Git! >> .env
    echo. >> .env
    echo # Flask настройки >> .env
    echo SECRET_KEY=crm-secret-key-for-local-development-only >> .env
    echo FLASK_ENV=development >> .env
    echo FLASK_DEBUG=true >> .env
    echo. >> .env
    echo # База данных CRM >> .env
    echo CRM_DB_HOST=94.130.69.41 >> .env
    echo CRM_DB_PORT=64821 >> .env
    echo CRM_DB_USER=analyst >> .env
    echo CRM_DB_PASSWORD=Am76Rv55pG >> .env
    echo CRM_DB_NAME=BASSmallBusinessN >> .env
    echo. >> .env
    echo # Безопасность >> .env
    echo ALLOWED_IPS=127.0.0.1,localhost,192.168.20.0/24,172.18.0.0/16,10.0.0.0/8 >> .env
    echo. >> .env
    echo # Дополнительные настройки >> .env
    echo MAX_RECORDS_PER_REQUEST=100 >> .env
    
    echo ✅ Новый .env файл создан
)

cd ..

echo.
echo Перезапускаем CRM сервис...
docker-compose restart crm-service

echo.
echo ========================================
echo   КОНФИГУРАЦИЯ ОБНОВЛЕНА
echo ========================================
echo.
echo 📊 Параметры подключения к CRM:
echo    - Сервер: 94.130.69.41:64821
echo    - База данных: BASSmallBusinessN
echo    - Пользователь: analyst
echo    - Пароль: [СКРЫТ]
echo.
echo 🔄 Проверьте подключение:
echo    python test_crm_database.py
echo.
pause 