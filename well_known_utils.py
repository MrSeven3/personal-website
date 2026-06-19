import mysql.connector
import os
from dotenv import load_dotenv
import sentry_sdk

load_dotenv()

pool = mysql.connector.pooling.MySQLConnectionPool(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USERNAME"),
    password=os.environ.get('DB_PASSWORD'),
    port=os.environ.get("DB_PORT"),
    database="personal-website",
    pool_size=2,
    pool_reset_session=True,
)

def add_well_known_entry(slug:str,content:str,domain:str):
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM well_known WHERE slug = %s AND domain = %s",(slug,domain,))

        if cursor.fetchone():
            return False

        cursor.execute("INSERT INTO well_known (`id`,`slug`,`content`,`domain`) VALUES (NULL, %s, %s, %s)",(slug,content,domain,))
        conn.commit()
    except Exception as e:
        print("adding well known entry failed")
        sentry_sdk.capture_exception(e)
    finally:
        cursor.close()
        conn.close()