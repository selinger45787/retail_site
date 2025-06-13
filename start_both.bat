@echo off
echo ========================================
echo     ЗАПУСК RETAIL SITE + CRM
echo ========================================
echo.
echo Остановка старых контейнеров...
docker-compose down
echo.
echo Запуск обоих сервисов...
docker-compose up -d
echo.
echo Проверка статуса...
docker ps
echo.
echo ========================================
echo Сервисы запущены:
echo - Основное приложение: http://localhost:5000
echo - CRM сервис: http://localhost:5001
echo ========================================
pause 