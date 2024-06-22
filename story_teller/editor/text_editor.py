from pydantic import BaseModel
from loguru import logger
from typing import Any, Text, List, Dict
from nicegui import ui


class TextEditorConfig(BaseModel):
    html_headers: List
    # styles
    label_style: Text
    label_style_no_color: Text
    input_style: Text
    textarea_style: Text
    button_style: Text
    # layouts
    textarea_layout: Text
    row_half_layout: Text
    # props
    button_props: Text
    default_color: Text
    positive_color: Text
    chip_colors: List

    def __init__(self, config_path: Text = "story_teller/editor/editor.yaml"):
        from story_teller.utils import FileReader

        config = FileReader().read(config_path)
        super().__init__(**config)


class TextEditor(BaseModel):
    db_client: Any
    config: TextEditorConfig
    label_dict: Dict = dict()
    input_dict: Dict = dict()
    textarea_dict: Dict = dict()

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        db_client,
        config: TextEditorConfig = None,
        dark_mode: bool = False,
    ):
        if not config:
            config = TextEditorConfig()
        super().__init__(db_client=db_client, config=config)
        global ui
        # Create GUI
        ui.dark_mode(dark_mode)
        for header in config.html_headers:
            ui.add_head_html(header)
        ui.query(".nicegui-content").classes("h-screen no-wrap")
        ui.colors(primary="#651fff")
        ## Post's information layout: id, subreddit, date, link
        with ui.row().classes("w-full gap-5"):
            ui.chip("ID", color=self.config.chip_colors[1]).style(
                self.config.label_style_no_color
            )
            self.label_dict["post_id"] = ui.label().style(self.config.label_style)

            ui.chip("Subreddit", color=self.config.chip_colors[2]).style(
                self.config.label_style_no_color
            )
            self.label_dict["subreddit"] = ui.label().style(self.config.label_style)

            ui.chip("Date", color=self.config.chip_colors[3]).style(
                self.config.label_style_no_color
            )
            self.label_dict["created"] = ui.label().style(self.config.label_style)

            # ui.chip("Link", color=self.config.chip_colors[3])
            # self.label_dict["url"] = ui.label().style(self.config.label_style)

        with ui.row().classes("w-full gap-0"):
            with ui.column().classes("w-1/2"):
                ui.label("Title-VN").style(self.config.label_style)
                self.input_dict["title_vn"] = ui.input().style(self.config.input_style)

            with ui.column().classes("w-1/2"):
                ui.label("Title-EN").style(self.config.label_style)
                self.input_dict["title"] = ui.input().style(self.config.input_style)

        with ui.row().classes("h-full w-full no-wrap"):
            with ui.column().classes("w-1/2 h-full"):
                ui.label("Body-VN").style(self.config.label_style)
                self.textarea_dict["body_vn"] = (
                    ui.textarea()
                    .style(self.config.textarea_style)
                    .classes(self.config.textarea_layout)
                )
            with ui.column().classes("w-1/2 h-full"):
                ui.label("Body-EN").style(self.config.label_style)
                self.textarea_dict["body"] = (
                    ui.textarea()
                    .style(self.config.textarea_style)
                    .classes(self.config.textarea_layout)
                )

        with ui.row():
            ui.button(
                icon="upload_file",
                text="Load post",
                color=self.config.default_color,
                on_click=lambda: self.open_load_post_window(),
            ).style(self.config.button_style).props(self.config.button_props).classes(
                "shadow-lg"
            )
            ui.button(
                icon="view_list",
                text="View Posts",
                color=self.config.default_color,
                on_click=lambda: self.open_post_selection_window(),
            ).style(self.config.button_style).props(self.config.button_props).classes(
                "shadow-lg"
            )
            ui.button(
                icon="publish",
                text="Submit",
                color=self.config.default_color,
                on_click=lambda: self.submit(),
            ).style(self.config.button_style).props(self.config.button_props).classes(
                "shadow-lg"
            )
            ui.button(
                icon="find_replace",
                text="Replace Text",
                color=self.config.default_color,
                on_click=lambda: self.open_replace_window(),
            ).style(self.config.button_style).props(self.config.button_props).classes(
                "shadow-lg"
            )

    def load_post(self, post_id: Text):
        from story_teller.database.crud import read

        logger.info(f"Loading post {post_id}")
        try:
            post = read.get_post(self.db_client, post_id)
            logger.info(f"{post=}")
            assert post
            for k, v in self.label_dict.items():
                if k == "created":
                    from datetime import datetime

                    v.text = datetime.fromtimestamp(post[k]).strftime(
                        "%a/%d/%m/%y, %H:%M"
                    )
                    continue
                v.text = post[k]

            for k, v in self.input_dict.items():
                v.value = post[k]
            for k, v in self.textarea_dict.items():
                v.value = post[k]
        except Exception as e:
            msg = "Post not found"
            logger.error(f"{type(e).__name__}: {e}. {msg}")
            ui.notify(msg, type="negative")

    def open_load_post_window(self):
        with ui.dialog() as dialog:
            dialog.open()
            with ui.card():
                post_id_input = (
                    ui.input(label="Post ID")
                    .style(self.config.input_style)
                    .props(f"label-color: {self.config.default_color}")
                )

                ui.button(
                    "Edit",
                    icon="edit",
                    on_click=lambda: (
                        self.load_post(post_id_input.value),
                        dialog.close(),
                    ),
                )

    def replace_vn_text(self, search_text: Text, replace_text: Text):
        to_be_replaced = dict(body_vn=self.textarea_dict, title_vn=self.input_dict)
        num_appear = 0
        for k, edit_dict in to_be_replaced.items():
            old_text = edit_dict[k].value
            num_appear += old_text.count(search_text)
            new_text = old_text.replace(search_text, replace_text)

            edit_dict[k].value = new_text

        ui.notify(
            f"Replaced {num_appear} occurences of `{search_text}` with `{replace_text}`",
            type="positive",
        )

    def open_replace_window(self):
        with ui.dialog() as dialog:
            dialog.open()
            with ui.card():
                search_text = (
                    ui.input(label="Origin")
                    .style(self.config.input_style)
                    .props(f"label-color: {self.config.default_color}")
                )

                replace_text = (
                    ui.input(label="Target")
                    .style(self.config.input_style)
                    .props(f"label-color: {self.config.default_color}")
                )

                ui.button(
                    "Replace",
                    icon="find_replace",
                    on_click=lambda: (
                        self.replace_vn_text(
                            search_text.value,
                            replace_text.value,
                        ),
                        dialog.close(),
                    ),
                )

    def create_table_cols(self, feature_name):
        feat_dict = dict(
            name=feature_name,
            label=feature_name,
            field=feature_name,
            align="left",
        )
        if feature_name == "created":
            feat_dict["sortable"] = True

        return feat_dict

    def open_post_selection_window(self):
        from story_teller.database.crud import read
        from datetime import datetime

        try:
            posts = list(read.get_translated_posts(self.db_client))
            delete_keys = [
                "_id",
                "body",
                "body_vn",
                "image_dir",
                "audio_dir",
                "url",
            ]
            for post in posts:
                for key in delete_keys:
                    del post[key]
                post["created"] = datetime.fromtimestamp(post["created"]).strftime(
                    "%d/%m/%y, %H:%M"
                )
            logger.info(f"{posts=}")
            columns = [self.create_table_cols(k) for k in posts[0].keys()]
            logger.info(f"{columns=}")
        except Exception as e:
            msg = "Cannot load translated posts"
            logger.error(f"{type(e).__name__}: {e}. {msg}")

        with ui.dialog().props("full-width") as dialog:
            dialog.open()
            with ui.card().classes("h-full"):
                ui.label("Select Post").style(self.config.label_style)

                table = ui.table(
                    title="Posts",
                    columns=columns,
                    rows=posts,
                    row_key="post_id",
                    pagination=10,
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
                        self.load_post(table.selected[0]["post_id"]),
                        dialog.close(),
                    ),
                )

    def submit(self):
        from story_teller.database.enum import StatusEnum
        from story_teller.database.crud import update

        post_new = dict()
        try:

            for k, v in self.input_dict.items():
                post_new[k] = v.value

            for k, v in self.textarea_dict.items():
                post_new[k] = v.value

            post_new["status"] = StatusEnum.edited.value
            post_new["post_id"] = self.label_dict["post_id"].text
            logger.info(f"Saving post {post_new}")
            update.update_post(db_client=self.db_client, post=post_new)
        except Exception as e:
            msg = "Cannot save post to DB"
            logger.error(f"{type(e).__name__}: {e}. {msg}")
        else:
            msg = f"Saved post {post_new['post_id']} - {post_new['title_vn']} to DB"
            logger.success(msg)
            ui.notify(msg, type="positive")

    def run(self):
        ui.run(reload=False, show=False)
