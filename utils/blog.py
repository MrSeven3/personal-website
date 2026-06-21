import sqlite3
import os
from dotenv import load_dotenv
import sentry_sdk

load_dotenv()

def get_blog_previews() -> list[list]:
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM blogs")
        blog_entries = cursor.fetchall() #returns a list of tuples. each tuple is like this: (id, blog_title, url_slug, created_time, edited_time, markdown_text)

        blog_previews = [] #format is a list of lists, each list is [name, url slug, preview text]
        for blog in blog_entries:
            blog_text = blog[5].split("\n")[0] #get the first line of markdown
            if len(blog_text) > 200: #cap it to 200 characters
                blog_text = blog_text[:200]

            blog_info = [blog[1], blog[2], blog_text+"..."]
            blog_previews.append(blog_info)
        return blog_previews
    except Exception as e:
        print("blog list gathering failed")
        sentry_sdk.capture_exception(e)
    finally:
        cursor.close()
        conn.close()

def get_blog_info(slug:str) -> list|None:
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * from blogs WHERE slug = ?",(slug,))

        info = cursor.fetchone()
        return info
    finally:
        cursor.close()
        conn.close()

def create_blog(title:str,slug:str,markdown:str):
    conn = sqlite3.connect("data/data.db")
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO blogs (`id`, `title`, `slug`, `published`, `blog_markdown`) VALUES (NULL, ?, ?, CURRENT_TIMESTAMP, ?)",(title,slug,markdown,))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    blog_title = input("title: ")
    blog_slug = input("slug: ")

    file_location = input("markdown file: ")
    if not os.path.exists(file_location):
        print("file not found")
        exit()

    markdown_file = open(file_location)
    markdown = markdown_file.read()

    if get_blog_info(blog_slug):
        print("that slug is already in use, rename it or press enter to exit. you can also type the same thing to overwrite the existing info")
        blog_slug = input("new slug: ")
        if blog_slug == "":
            exit()

    create_blog(blog_title, blog_slug, markdown)