from nicegui import ui, context
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
        entry_post_id.text = post.get("post_id", "")
        text_title_en.value = post.get("title", "")
        text_title_vn.value = post.get("title_vn", "")
        text_vietnamese.value = post.get("body_vn", "")
        text_english.value = post.get("body", "")
    else:
        ui.notify("Post not found", type="negative")


# Function to submit data to MongoDB
def submit_data():
    post_id = entry_post_id.value
    title = text_title_en.value
    title_vn = text_title_vn.value
    vietnamese_text = urllib.parse.quote(text_vietnamese.value.strip())
    english_text = text_english.value.strip()

    post_data = {
        "post_id": post_id,
        "title": title,
        "title_vn": title_vn,
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
        {
            "name": "post_id",
            "label": "Post ID",
            "field": "post_id",
            "required": True,
            "align": "left",
        },
        {"name": "title", "label": "Title", "field": "title", "sortable": True},
    ]
    with ui.dialog() as dialog:
        # dialog.classes("w-500")
        dialog.open()
        with ui.card().classes("flex-card-grow h-full"):
            ui.label("Select Post").style("font-size: 20px; font-weight: bold; font-family: Iosevka Nerd Font")

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

            ui.button(
                "Edit",
                icon="edit",
                on_click=lambda: (
                    load_data(table.selected[0]["post_id"]),
                    dialog.close(),
                ),
            )


# ui.dark_mode(True)
ui.add_head_html("<style>.flex-grow .q-field__control {height: 100%;} </style>")
ui.add_head_html("<style>textarea.q-field__native {min-height: 10px;} </style>")
ui.add_head_html("<style>.flex-card-grow .q-dialog__inner {max-width: 1200px;} </style>")
# ui.add_head_html("<style>card.q-dialog__inner--minimized  {max-width: 1200px;} </style>")
# ui.add_body_html("<script src=\"https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js\"></script>")
# src = "https://assets5.lottiefiles.com/packages/lf20_MKCnqtNQvg.json"
# ui.html(f"<lottie-player src=\"{src}\" loop autoplay").classes('w-24')
ui.query(".nicegui-content").classes("h-screen no-wrap")
# Creating the main layout
with ui.row().classes("w-full"):
    ui.label("Post ID").style("font-size: 20px; font-weight: bold; font-family: Iosevka Nerd Font")
    entry_post_id = ui.label().style("width: 50%; font-size: 20px; font-family: Iosevka Nerd Font ")

# with ui.grid(columns=2).style("max-width: 1200px; margin:auto;").classes("w-full gap-5 flex-grow"):
with ui.row().classes("w-full gap-0"):
    with ui.column().classes("w-1/2"):
        ui.label("Title-VN").style("font-size: 20px; font-weight: bold; font-family: Iosevka Nerd Font")
        text_title_vn = ui.input().style("width: 90%; font-size: 14px; font-family: Iosevka Nerd Font")
    with ui.column().classes("w-1/2"):
        ui.label("Title-EN").style("font-size: 20px; font-weight: bold; font-family: Iosevka Nerd Font")
        text_title_en = ui.input().style("width: 90%; font-size: 14px; font-family: Iosevka Nerd Font")
with ui.row().classes("h-full w-full no-wrap"):
    with ui.column().classes("w-1/2 h-full"):
        ui.label("Body-VN").style("font-size: 20px; font-weight: bold; font-family: Iosevka Nerd Font")
        text_vietnamese = (
            ui.textarea()
            .style(
                "width: 100%; height: 100%; font-size: 16px; font-family: Iosevka Nerd Font"
            )
            .classes("border flex-grow w-full")
        )
    with ui.column().classes("w-1/2 h-full"):
        ui.label("Body-EN").style("font-size: 20px; font-weight: bold; font-family: Iosevka Nerd Font")
        text_english = (
            ui.textarea()
            .style("width: 100%; height: 100%; font-size: 16px; font-family: Iosevka Nerd Font")
            .classes("border flex-grow w-full")
        )

with ui.row():
    # ui.button("Load", on_click=lambda: load_data(entry_post_id.value)).style(
    #     "font-size: 16px;"
    # )
    ui.button(icon="publish", text="Submit", on_click=submit_data).style(
        "font-size: 16px;"
    )
    ui.button(icon="search", text="View Posts", on_click=open_post_selection_window).style(
        "font-size: 16px;"
    )

ui.run()
