@echo off
echo ========================================
echo   ИСПРАВЛЕНИЕ ХОСТА CRM БАЗЫ ДАННЫХ
echo ========================================
echo.

echo Заменяем host.docker.internal на правильный IP сервера...

cd crm_service

if exist .env (
    echo Исправляем существующий .env файл...
    
    REM Создаем временную копию
    copy .env .env.backup
    
    REM Заменяем host.docker.internal на правильный IP
    powershell -Command "(Get-Content .env) -replace 'CRM_DB_HOST=host.docker.internal', 'CRM_DB_HOST=192.168.20.189' | Set-Content .env"
    
    echo ✅ Хост изменен с host.docker.internal на 192.168.20.189
    echo ✅ Создана резервная копия: .env.backup
) else (
    echo ❌ Файл .env не найден!
    echo Сначала запустите: setup_crm_database.bat
    pause
    exit /b 1
)

cd ..

echo.
echo Перезапускаем CRM сервис с новыми настройками...
docker-compose restart crm-service

echo.
echo ========================================
echo   ИСПРАВЛЕНИЕ ЗАВЕРШЕНО
echo ========================================
echo.
echo 📊 Новые настройки:
echo    - CRM_DB_HOST: 192.168.20.189 (удаленный сервер)
echo    - CRM_DB_NAME: Basssmallbussines
echo.
echo 🔄 Проверьте подключение:
echo    python test_crm_database.py
echo.
pause 