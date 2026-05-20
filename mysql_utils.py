import ast
import mysql.connector
import os
import requests
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

print("db connection initialised")

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


def get_docker_data() -> list:
    existing_data = get_data_from_key("docker_services")
    if existing_data:
        last_updated = existing_data[2]
        time_since_updated = datetime.datetime.now() - last_updated

        if time_since_updated.total_seconds() <= int(existing_data[4])*60:
            return ast.literal_eval(existing_data[3])

    komodo_auth_headers = {"X-Api-Key": os.environ.get("KOMODO_API_KEY"), "X-Api-Secret": os.environ.get("KOMODO_API_SECRET"), "Content-Type": "application/json"}

    deploy_summary = requests.post("https://komodo.thirtyseventh.xyz/read/GetDeploymentsSummary", headers=komodo_auth_headers, json={})
    if deploy_summary.status_code != 200:
        print("uptime data get failed with code " +str(deploy_summary.status_code)+"\n"+str(deploy_summary.text))
        return [-1,-1]
    stack_summary = requests.post("https://komodo.thirtyseventh.xyz/read/GetStacksSummary", headers=komodo_auth_headers, json={})
    if stack_summary.status_code != 200:
        print("uptime data get failed with code " +str(stack_summary.status_code)+"\n"+str(deploy_summary.text))
        return [-1,-1]
    container_summary = requests.post("https://komodo.thirtyseventh.xyz/read/GetDockerContainersSummary", headers=komodo_auth_headers, json={})
    if container_summary.status_code != 200:
        print("uptime data get failed with code " +str(container_summary.status_code)+"\n"+str(container_summary.text))
        return [-1,-1]

    total_docker_services = int(deploy_summary.json()['running']) + int(stack_summary.json()['running'])
    docker_containers = int(container_summary.json()['running'])

    docker_data = [total_docker_services, docker_containers]

    store_data_to_key("docker_services",str(docker_data))
    return docker_data

def get_website_uptime() -> float:
    existing_data = get_data_from_key("website_uptime")
    if existing_data:
        last_updated = existing_data[2]
        time_since_updated = datetime.datetime.now() - last_updated

        if time_since_updated.total_seconds() <= int(existing_data[4])*60:
            return float(existing_data[3])

    grafana_auth_headers = {"Authorization": "Bearer "+os.environ.get("GRAFANA_API_KEY")}

    uptime_data = requests.get("https://grafana.thirtyseventh.xyz/api/datasources/uid/efive1u0b5wqob/resources/api/v1/query?query=avg_over_time(monitor_status%7Bmonitor_name%3D%22Personal%20Website%22%7D%5B30d%5D)", headers=grafana_auth_headers)

    if uptime_data.status_code != 200:
        print("uptime data get failed with code " +str(uptime_data.status_code)+"\n"+str(uptime_data.text))
        return -1

    uptime = float(uptime_data.json()['data']['result'][0]['value'][1]) * 100
    uptime = round(uptime, 2)

    store_data_to_key("website_uptime",str(uptime))
    return uptime