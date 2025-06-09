# Database Configuration Example
# Copy this file to database.py and fill in your actual database credentials

# Database connection parameters
DB_USER = 'your_db_username'
DB_PASSWORD = 'your_db_password'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'your_database_name'

# Construct database URI
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Warning: Never commit the real database.py file to version control!
# Add database.py to your .gitignore file 