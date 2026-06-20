import sqlite3
import os

def init_db():
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists("data/data.db"):
        conn = sqlite3.connect("data/data.db")
        cursor = conn.cursor()

        cursor.execute('CREATE TABLE "well_known" ("id" integer,"slug" text,"content" longtext,"domain" text, PRIMARY KEY ("id"))')
        cursor.execute('CREATE TABLE "cached_data" ("id" integer,"name" text,"last_updated" datetime,"data" text,"frequency_min" int, PRIMARY KEY ("id"))')
        cursor.execute('CREATE TABLE "blogs" ("id" integer,"title" text,"slug" text,"published" datetime,"edited" datetime,"blog_markdown" text, PRIMARY KEY ("id"))')