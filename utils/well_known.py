import sqlite3
import sentry_sdk


def add_well_known_entry(slug:str,content:str,domain:str):
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM well_known WHERE slug = ? AND domain = ?",(slug,domain,))

        if cursor.fetchone():
            return False

        cursor.execute("INSERT INTO well_known (`id`,`slug`,`content`,`domain`) VALUES (NULL, ?, ?, ?)",(slug,content,domain,))
        conn.commit()
    except Exception as e:
        print("adding well known entry failed")
        sentry_sdk.capture_exception(e)
    finally:
        cursor.close()
        conn.close()

def get_well_known_entry(slug:str,domain:str) -> str|None:
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM well_known WHERE slug = ? AND domain = ?",(slug,domain,))

        data = cursor.fetchone()

        if data: return data[2]
        else: return None

    except Exception as e:
        print("retrieving well known entry failed")
        sentry_sdk.capture_exception(e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_well_known_entries() -> list[str]|None:
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM well_known")

        data = cursor.fetchall()

        if data: return data
        else: return None

    except Exception as e:
        print("retrieving all well known entries failed")
        sentry_sdk.capture_exception(e)
        return None
    finally:
        cursor.close()
        conn.close()

def delete_well_known_entry(slug:str,domain:str):
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM well_known WHERE slug = ? AND domain = ?",(slug,domain,))

        if not cursor.fetchone():
            return False

        cursor.execute("DELETE FROM well_known WHERE slug = ? AND domain = ?",(slug,domain,))
        conn.commit()

    except Exception as e:
        print("deleting well known entry failed")
        sentry_sdk.capture_exception(e)
        return None
    finally:
        cursor.close()
        conn.close()
