from nicegui import ui
from pymongo import MongoClient
import urllib.parse

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.story_teller
collection = db["posts"]


# Function to load data from MongoDB
def load_data(post_id):
    post = collection.find_one({"post_id": post_id})
    if post:
        text_vietnamese.value = urllib.parse.unquote(post.get("body_vn", ""))
        text_english.value = post.get("body", "")
        entry_post_id.value = post.get("post_id", "")
        entry_post_title.value = post.get("title", "")
    else:
        ui.notify("Post not found", type="negative")


# Function to submit data to MongoDB
def submit_data():
    post_id = entry_post_id.value
    title = entry_post_title.value
    vietnamese_text = urllib.parse.quote(text_vietnamese.value.strip())
    english_text = text_english.value.strip()

    post_data = {
        "post_id": post_id,
        "title": title,
        "body_vn": vietnamese_text,
        "body": english_text,
    }

    collection.update_one({"post_id": post_id}, {"$set": post_data}, upsert=True)
    ui.notify("Data written to MongoDB", type="positive")


# Function to open the post selection window
def open_post_selection_window():
    posts = collection.find({"status": 1})

    post_list = [dict(post_id=post["post_id"], title=post["title"]) for post in posts]
    columns = [
        {'name': 'post_id', 'label': 'Post ID', 'field': 'post_id', 'required': True, 'align': 'left'},
        {'name': 'title', 'label': 'Title', 'field': 'title', 'sortable': True},
    ]
    with ui.dialog() as dialog:
        dialog.open()
        with ui.card():
            ui.label("Select Post")
            # post_select = ui.select(options=post_list, with_input=True)
            # ui.button(
            #     "Load",
            #     on_click=lambda: (
            #         load_data(post_select.value.split(":")[0].strip()),
            #         dialog.close,
            #     ),
            # )

            table = ui.table(
                title="Posts",
                columns=columns,
                rows=post_list,
                row_key="title",
                pagination=5,
                selection="single",
            )
            table.add_slot(
                "body-cell-title",
                r'<td><a :href="props.row.url">{{ props.row.title }}</a></td>',
            )
            table.on("rowClick", lambda e: print(e.args))
            

# Creating the main layout
with ui.column().style("max-width: 1200px; margin: auto;"):
    ui.label("Post ID").style("font-size: 16px;")
    entry_post_id = ui.input().style("width: 100%; font-size: 16px;")

    ui.label("Post Title").style("font-size: 16px;")
    entry_post_title = ui.input().style("width: 100%; font-size: 16px;")

    ui.label("body_vn").style("font-size: 16px;")
    text_vietnamese = ui.textarea().style(
        "width: 100%; height: 300px; font-size: 16px; font-family: Iosevka Nerd Font"
    )

    ui.label("body").style("font-size: 16px;")
    text_english = ui.textarea().style("width: 100%; height: 300px; font-size: 16px;")

    with ui.row():
        ui.button("Load", on_click=lambda: load_data(entry_post_id.value)).style(
            "font-size: 16px;"
        )
        ui.button("Submit", on_click=submit_data).style("font-size: 16px;")
        ui.button("Open Menu", on_click=open_post_selection_window).style(
            "font-size: 16px;"
        )

ui.run()
