import psycopg2
from tabulate import tabulate
from datetime import datetime

try:
    # Подключаемся к базе данных
    connection = psycopg2.connect(
        host='94.130.69.41',
        port='64821',
        database='BASSmallBusinessN',
        user='analyst',
        password='Am76Rv55pG'
    )
    
    # Создаем курсор
    cursor = connection.cursor()
    
    # Выполняем запрос
    print("Выполняем запрос к базе данных...")
    cursor.execute("""
    SELECT
        "_period",
        "Номенклатура",
        "Операція",
        "Прихід",
        "Витрата",
        "Чистий_рух_за_день",
        SUM("Чистий_рух_за_день") OVER (
            PARTITION BY "Номенклатура"
            ORDER BY "_period"
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS "Залишок_накопичений_на_дату"
    FROM (
        SELECT
            DATE_TRUNC('day', acc."_period") AS "_period",
            art."_description" AS "Номенклатура",
            oper."_description" AS "Операція",
            SUM(CASE WHEN acc."_recordkind" = 0 THEN acc."_fld19509" ELSE 0 END) AS "Прихід",
            SUM(CASE WHEN acc."_recordkind" = 1 THEN acc."_fld19509" ELSE 0 END) AS "Витрата",
            SUM(CASE WHEN acc."_recordkind" = 0 THEN acc."_fld19509" ELSE 0 END) -
            SUM(CASE WHEN acc."_recordkind" = 1 THEN acc."_fld19509" ELSE 0 END) AS "Чистий_рух_за_день"
        FROM
            "public"."_accumrg19502" acc
            LEFT JOIN "public"."_reference160x1" AS art ON acc."_fld19505rref" = art."_idrref"
            LEFT JOIN "public"."_reference276" AS oper ON acc."_fld19511rref" = oper."_idrref"
        WHERE
            acc."_period" < CURRENT_DATE
        GROUP BY
            DATE_TRUNC('day', acc."_period"),
            art."_description",
            oper."_description"
    ) AS source
    ORDER BY
        "_period" DESC,
        "Номенклатура",
        "Операція"
    """)
    
    # Получаем результаты
    results = cursor.fetchall()
    
    # Получаем названия колонок
    column_names = [desc[0] for desc in cursor.description]
    
    # Форматируем даты и числа для вывода
    formatted_results = []
    for row in results:
        formatted_row = list(row)
        # Форматируем дату
        if isinstance(formatted_row[0], datetime):
            formatted_row[0] = formatted_row[0].strftime('%Y-%m-%d')
        # Форматируем числовые значения
        for i in range(3, 7):
            if formatted_row[i] is not None:
                formatted_row[i] = f"{formatted_row[i]:,.2f}"
        formatted_results.append(formatted_row)
    
    # Выводим результаты в виде таблицы
    print("\nРезультаты запроса:")
    print(tabulate(formatted_results, headers=column_names, tablefmt='grid'))
    print(f"\nВсего записей: {len(results)}")
    
except Exception as e:
    print(f"Ошибка при выполнении запроса: {e}")
    
finally:
    if 'connection' in locals():
        cursor.close()
        connection.close()
        print("\nСоединение закрыто") 