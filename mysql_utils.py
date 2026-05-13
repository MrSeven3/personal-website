import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

pool = mysql.connector.pooling.MySQLConnectionPool(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USERNAME"),
    password=os.environ.get('DB_PASSWORD'),
    port=os.environ.get("DB_PORT"),
    pool_size=5,
    pool_reset_session=True,
)

