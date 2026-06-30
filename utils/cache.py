import ast
import sqlite3
import os
import dateparser
import requests
import datetime
import sentry_sdk


def get_cache_data(key:str) -> list | None:
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * from cached_data WHERE name = ?",(key,))
        data = cursor.fetchone() # data is ordered in [id, key, last_updated, data, update_frequency]
        if not data is None:
            return list(data)
        else:
            return None

    except Exception as e:
        print("data retrieval failed: "+str(e))
        sentry_sdk.capture_exception(e)
    finally:
        cursor.close()
        conn.close()

def store_cache_data(key:str, data:str):
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()

        if get_cache_data(key):
            cursor.execute("UPDATE `cached_data` SET `last_updated` = CURRENT_TIMESTAMP, `data` = ? WHERE name = ?", (data,key,))
        else:
            cursor.execute("INSERT INTO `cached_data` (`id`, `name`, `last_updated`, `data`, `frequency_min`) VALUES (NULL, ?, CURRENT_TIMESTAMP, ?, 5)", (key, data,))

        print("updated the database")
        conn.commit()
    except Exception as e:
        print("data storage failed: "+str(e))
        sentry_sdk.capture_exception(e)
    finally:
        cursor.close()
        conn.close()


def get_docker_data() -> list[int]:
    existing_data = get_cache_data("docker_services")
    if existing_data:
        last_updated = existing_data[2]
        time_since_updated = datetime.datetime.now() - dateparser.parse(last_updated)

        if time_since_updated.total_seconds() <= int(existing_data[4])*60: #check if i can use the existing data, and return it if i can
            return ast.literal_eval(existing_data[3])
        print("data is " + str(time_since_updated.total_seconds()) + " seconds old. refreshing stale data")

    komodo_auth_headers = {"X-Api-Key": os.environ.get("KOMODO_API_KEY"), "X-Api-Secret": os.environ.get("KOMODO_API_SECRET"), "Content-Type": "application/json"}
    try: #pulls service and container summaries from komodo, returning existing data if it fails, or -1 if there is no existing data
        deploy_summary = requests.post("https://komodo.thirtyseventh.xyz/read/GetDeploymentsSummary", headers=komodo_auth_headers, json={}, timeout=(1, 2))
        if deploy_summary.status_code != 200:
            print("komodo data get failed with code " +str(deploy_summary.status_code)+"\n"+str(deploy_summary.text))
            return ast.literal_eval(existing_data[3]) if existing_data else [-1,-1] #if its available, return old data on new data fail
        stack_summary = requests.post("https://komodo.thirtyseventh.xyz/read/GetStacksSummary", headers=komodo_auth_headers, json={}, timeout=(1, 2))
        if stack_summary.status_code != 200:
            print("komodo data get failed with code " +str(stack_summary.status_code)+"\n"+str(deploy_summary.text))
            return ast.literal_eval(existing_data[3]) if existing_data else [-1,-1]#if its available, return old data on new data fail
        container_summary = requests.post("https://komodo.thirtyseventh.xyz/read/GetDockerContainersSummary", headers=komodo_auth_headers, json={}, timeout=(1, 2))
        if container_summary.status_code != 200:
            print("komodo data get failed with code " +str(container_summary.status_code)+"\n"+str(container_summary.text))
            return ast.literal_eval(existing_data[3]) if existing_data else [-1,-1]#if its available, return old data on new data fail
    except requests.exceptions.Timeout:
        sentry_sdk.capture_message(
            "komodo docker data gathering timed out",
            level="warning",
        )
        return ast.literal_eval(existing_data[3]) if existing_data else [-1,-1]#if its available, return old data on new data fail

    total_docker_services = int(deploy_summary.json()['running']) + int(stack_summary.json()['running'])
    docker_containers = int(container_summary.json()['running'])

    docker_data = [total_docker_services, docker_containers]

    store_cache_data("docker_services", str(docker_data))
    return docker_data

def get_website_uptime() -> float:
    existing_data = get_cache_data("website_uptime")
    if existing_data:
        last_updated = existing_data[2]
        time_since_updated = datetime.datetime.now() - dateparser.parse(last_updated)

        if time_since_updated.total_seconds() <= int(existing_data[4])*60: #check if i can use the existing data, and return it if i can
            return float(existing_data[3])
        print("data is " + str(time_since_updated.total_seconds()) + " seconds old. refreshing stale data")

    grafana_auth_headers = {"Authorization": "Bearer "+os.environ.get("GRAFANA_API_KEY")}

    try: #pull the uptime data from prometheus using grafana. prometheus gets it from uptime kuma, tho the calculations are different, so this is slightly wrong. TODO: either fix prometheus or find a way to poll uptime kuma directly
        uptime_data = requests.get("https://grafana.thirtyseventh.xyz/api/datasources/uid/efive1u0b5wqob/resources/api/v1/query?query=avg_over_time(monitor_status%7Bmonitor_name%3D%22Personal%20Website%22%7D%5B30d%5D)", headers=grafana_auth_headers, timeout=(1, 2))
        if uptime_data.status_code != 200:
            print("uptime data get failed with code " +str(uptime_data.status_code)+"\n"+str(uptime_data.text))
            float(existing_data[3]) if existing_data else -1 #if its available, return old data on new data fail
    except requests.exceptions.Timeout:
        sentry_sdk.capture_message(
            "uptime data gathering timed out",
            level="warning",
        )
        return float(existing_data[3]) if existing_data else -1#if its available, return old data on new data fail

    uptime = float(uptime_data.json()['data']['result'][0]['value'][1]) * 100
    uptime = round(uptime, 2)

    store_cache_data("website_uptime", str(uptime))
    return uptime