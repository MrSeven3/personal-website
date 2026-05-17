import mysql.connector
import os
import requests
import dateparser
import datetime
from dotenv import load_dotenv

load_dotenv()

pool = mysql.connector.pooling.MySQLConnectionPool(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USERNAME"),
    password=os.environ.get('DB_PASSWORD'),
    port=os.environ.get("DB_PORT"),
    pool_size=10,
    pool_reset_session=True,
)

def get_data_from_key(key:str) -> list|None:
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("USE `personal-website`")

        cursor.execute("SELECT * from cached_data WHERE name = %s",(key,))
        data = cursor.fetchone() # data is ordered in [id, key, last_updated, data, update_frequency]
        if not data is None:
            return list(data)
        else:
            return None

    except Exception as e:
        print("data retrieval failed: "+str(e))
    finally:
        conn.close()

def store_data_to_key(key:str, data:str):
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("USE `personal-website`")

        if get_data_from_key(key):
            cursor.execute("UPDATE `cached_data` SET `last_updated` = NOW(), `data` = %s WHERE name = %s", (data,key,))
        else:
            cursor.execute("INSERT INTO `cached_data` (`id`, `name`, `last_updated`, `data`, `frequency_min`) VALUES (NULL, %s, NOW(), %s, 5)", (key, data,))

        conn.commit()
    except Exception as e:
        print("data storage failed: "+str(e))
    finally:
        conn.close()

def get_docker_services():
    existing_data = get_data_from_key("docker_services")
    if existing_data:
        last_updated = existing_data[2]
        time_since_updated = datetime.datetime.now() - last_updated

        if time_since_updated.total_seconds() <= int(existing_data[4])*60:
            print("data is still new, returning stored data")
            return int(existing_data[3])

    print("stale data, refreshing")
    komodo_auth_headers = {"X-Api-Key": os.environ.get("KOMODO_API_KEY"), "X-Api-Secret": os.environ.get("KOMODO_API_SECRET"), "Content-Type": "application/json"}

    deploy_summary = requests.post("https://komodo.thirtyseventh.xyz/read/GetDeploymentsSummary", headers=komodo_auth_headers, json={})
    stack_summary = requests.post("https://komodo.thirtyseventh.xyz/read/GetStacksSummary", headers=komodo_auth_headers, json={})

    total_docker_services = int(deploy_summary.json()['total']) + int(stack_summary.json()['total'])

    store_data_to_key("docker_services",str(total_docker_services))

    return total_docker_services


get_docker_services()