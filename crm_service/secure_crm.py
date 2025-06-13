import os
import time
import psycopg2
from flask import Flask, jsonify, request, render_template
from config_secure import config

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Получаем конфигурацию
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Проверка IP адресов
    def check_ip_allowed():
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        allowed_ips = app.config['ALLOWED_IPS']
        
        # Debug logging
        print(f"DEBUG: Client IP: {client_ip}")
        print(f"DEBUG: Allowed IPs: {allowed_ips}")
        
        for allowed_ip in allowed_ips:
            if '/' in allowed_ip:  # CIDR notation
                from ipaddress import ip_network, ip_address
                try:
                    if ip_address(client_ip) in ip_network(allowed_ip.strip()):
                        print(f"DEBUG: IP {client_ip} matched network {allowed_ip}")
                        return True
                except Exception as e:
                    print(f"DEBUG: Error checking {client_ip} against {allowed_ip}: {e}")
                    continue
            else:  # Direct IP match
                if client_ip == allowed_ip.strip():
                    print(f"DEBUG: IP {client_ip} matched directly {allowed_ip}")
                    return True
        
        print(f"DEBUG: IP {client_ip} not allowed")
        return False
    
    @app.before_request
    def limit_remote_addr():
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        allowed_ips = app.config.get('ALLOWED_IPS', [])
        print(f"=== DEBUG INFO ===")
        print(f"Client IP: {client_ip}")
        print(f"Allowed IPs: {allowed_ips}")
        print(f"Config keys: {list(app.config.keys())}")
        print(f"==================")
        
        if not check_ip_allowed():
            return jsonify({'error': 'Access denied', 'debug': {'client_ip': client_ip, 'allowed_ips': allowed_ips}}), 403
    
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'Secure CRM',
            'timestamp': time.time(),
            'config_loaded': True
        })
    
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'api': 'ready',
            'database': 'configured via environment variables',
            'security': 'enhanced',
            'max_records': app.config['MAX_RECORDS_PER_REQUEST']
        })
    
    @app.route('/api/test-db')
    def test_db():
        """Тест подключения к базе (без показа паролей)"""
        try:
            import psycopg2
            
            # Формируем строку подключения
            conn_string = f"postgresql://{app.config['CRM_DB_USER']}:{app.config['CRM_DB_PASSWORD']}@{app.config['CRM_DB_HOST']}:{app.config['CRM_DB_PORT']}/{app.config['CRM_DB_NAME']}"
            
            # Пытаемся подключиться
            try:
                conn = psycopg2.connect(conn_string)
                cursor = conn.cursor()
                cursor.execute('SELECT version()')
                version = cursor.fetchone()
                cursor.close()
                conn.close()
                
                db_config = {
                    'host': app.config['CRM_DB_HOST'],
                    'port': app.config['CRM_DB_PORT'],
                    'user': app.config['CRM_DB_USER'],
                    'database': app.config['CRM_DB_NAME']
                }
                
                return jsonify({
                    'database_config': db_config,
                    'status': 'connected',
                    'database_accessible': True,
                    'postgresql_version': version[0] if version else 'unknown',
                    'note': 'Successfully connected to database'
                })
                
            except psycopg2.Error as db_err:
                return jsonify({
                    'database_config': {
                        'host': app.config['CRM_DB_HOST'],
                        'port': app.config['CRM_DB_PORT'],
                        'user': app.config['CRM_DB_USER'],
                        'database': app.config['CRM_DB_NAME']
                    },
                    'status': 'connection_failed',
                    'database_accessible': False,
                    'error': str(db_err),
                    'note': 'Configuration loaded but database connection failed'
                })
                
        except ImportError:
            return jsonify({
                'error': 'psycopg2 not installed',
                'note': 'Cannot test database connection without PostgreSQL adapter'
            }), 500
        except Exception as e:
            return jsonify({'error': f'Database configuration error: {str(e)}'}), 500
    
    @app.route('/api/inventory-report')
    def inventory_report():
        """Звіт по залишках і рухах товарів"""
        try:
            # SQL запрос - PIVOT по дням, операции в столбцах
            sql_query = """
            WITH daily_operations AS (
              SELECT
                DATE_TRUNC('day', acc."_period") AS "date_period",
                oper."_description" AS "operation_type",
                SUM(
                  CASE
                    WHEN acc."_recordkind" = 0 THEN acc."_fld19509"
                    ELSE -acc."_fld19509"
                  END
                ) AS "net_movement"
              FROM
                "public"."_accumrg19502" acc
                LEFT JOIN "public"."_reference276" AS oper ON acc."_fld19511rref" = oper."_idrref"
              WHERE
                acc."_period" >= CURRENT_DATE - INTERVAL '10 days'
                AND acc."_period" < CURRENT_DATE
                AND oper."_description" IS NOT NULL
              GROUP BY
                DATE_TRUNC('day', acc."_period"),
                oper."_description"
            )
            SELECT
              TO_CHAR(date_period, 'YYYY-MM-DD') AS "Дата",
              COALESCE(SUM(CASE WHEN operation_type = 'Продаж покупцю' THEN net_movement ELSE 0 END), 0) AS "Продаж_покупцю",
              COALESCE(SUM(CASE WHEN operation_type = 'Звіт про роздрібні продажі' THEN net_movement ELSE 0 END), 0) AS "Звіт_про_роздрібні_продажі",
              COALESCE(SUM(CASE WHEN operation_type = 'Поступление товаров и услуг' THEN net_movement ELSE 0 END), 0) AS "Поступление_товаров",
              COALESCE(SUM(CASE WHEN operation_type = 'Перемещение товаров' THEN net_movement ELSE 0 END), 0) AS "Перемещение_товаров",
              COALESCE(SUM(CASE WHEN operation_type = 'Реализация товаров и услуг' THEN net_movement ELSE 0 END), 0) AS "Реализация_товаров",
              COALESCE(SUM(CASE WHEN operation_type = 'Списание товаров' THEN net_movement ELSE 0 END), 0) AS "Списание_товаров",
              COALESCE(SUM(CASE WHEN operation_type = 'Инвентаризация товаров' THEN net_movement ELSE 0 END), 0) AS "Инвентаризация",
              COALESCE(SUM(net_movement), 0) AS "Общее_движение",
              0 AS "Остаток_на_начало",
              COALESCE(SUM(SUM(net_movement)) OVER (ORDER BY date_period), 0) AS "Остаток_на_конец"
            FROM daily_operations
            GROUP BY date_period
            ORDER BY date_period ASC
            LIMIT 50;
            """
            
            # Подключение к базе данных
            conn_string = f"postgresql://{app.config['CRM_DB_USER']}:{app.config['CRM_DB_PASSWORD']}@{app.config['CRM_DB_HOST']}:{app.config['CRM_DB_PORT']}/{app.config['CRM_DB_NAME']}"
            
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            
            # Выполнение запроса
            cursor.execute(sql_query)
            
            # Получение результатов
            columns = [desc[0] for desc in cursor.description]
            records = []
            
            for row in cursor.fetchall():
                record = {}
                for i, value in enumerate(row):
                    record[columns[i]] = value
                records.append(record)
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'status': 'success',
                'records': records,
                'total_records': len(records),
                'query_executed': 'inventory_report',
                'timestamp': time.time()
            })
            
        except psycopg2.Error as db_err:
            return jsonify({
                'error': f'Database error: {str(db_err)}',
                'type': 'database_error'
            }), 500
            
        except Exception as e:
            return jsonify({
                'error': f'Unexpected error: {str(e)}',
                'type': 'general_error'
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Secure CRM microservice on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=app.config['DEBUG']) 