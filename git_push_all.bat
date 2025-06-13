@echo off
echo ========================================
echo      GIT PUSH - ОБА СЕРВИСА
echo ========================================
echo.

echo Проверка что .env файлы НЕ попадут в Git...
git check-ignore crm_service/.env
if errorlevel 1 (
    echo ОШИБКА: .env файл не исключен из Git!
    echo Проверьте .gitignore
    pause
    exit /b 1
)

echo.
echo Статус Git:
git status
echo.

echo Добавление безопасных файлов...
git add .gitignore
git add requirements.txt
git add app.py
git add config.py
git add docker-compose.yml
git add Dockerfile
git add .dockerignore
git add SECURITY.md
git add ИНСТРУКЦИЯ.md
git add Procfile

echo Добавление CRM файлов (без .env!)...
git add crm_service/config_secure.py
git add crm_service/secure_crm.py
git add crm_service/README.md
git add crm_service/Dockerfile
git add crm_service/.env.example

echo.
echo Готово к коммиту!
echo Выполните:
echo git commit -m "Complete secure retail site with CRM microservice"
echo git push origin fix-image-collision
echo.
pause 