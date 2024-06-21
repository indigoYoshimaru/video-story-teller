from pydantic import BaseModel
from loguru import logger
from typing import Any, Text, List, Dict
from nicegui import ui


class TextEditorConfig(BaseModel):
    html_headers: List
    # styles
    label_style: Text
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
            ui.chip("ID", color=self.config.chip_colors[1]).style(self.config.label_style)
            self.label_dict["post_id"] = ui.label().style(self.config.label_style)

            ui.chip("Subreddit", color=self.config.chip_colors[2])
            self.label_dict["subreddit"] = ui.label().style(self.config.label_style)

            ui.chip("Date", color=self.config.chip_colors[3])
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
            # ui.button("Load", on_click=lambda: self.load_data(entry_post_id.value)).style(
            #     self.config.button_style
            # ).props(self.config.button_props)
            ui.button(
                icon="publish",
                text="Submit",
                color=self.config.default_color,
            ).style(self.config.button_style).props(self.config.button_props).classes(
                "shadow-lg"
            )
            ui.button(
                icon="search",
                text="View Posts",
                color=self.config.default_color,
                on_click=lambda: self.open_post_selection_window(),
            ).style(self.config.button_style).props(self.config.button_props).classes(
                "shadow-lg"
            )

    def load_data(self, post_id: Text):
        from story_teller.database.crud import read
        logger.info(f'Loading post {post_id}')
        try:
            post = read.get_post(self.db_client, post_id)
            logger.info(f'{post=}')
            assert post
            for k, v in self.label_dict.items():
                v.text = post[k]
        except Exception as e:
            msg = "Post not found"
            logger.error(f"{type(e).__name__}: {e}. {msg}")
            ui.notify(msg, type="negative")

    def create_table_cols(self, feature_name):
        feat_dict = dict(
            name=feature_name,
            label=feature_name,
            field=feature_name,
        )
        if feature_name == "date":
            feat_dict["sortable"] = True
        return feat_dict

    def open_post_selection_window(self):
        from story_teller.database.crud import read

        try:
            posts = list(read.get_translated_posts(self.db_client))
            delete_keys = ["_id", "title_vn", "body", "body_vn", "image_dir", "audio_dir"]
            for post in posts: 
                for key in delete_keys: 
                    del post[key] 
                
            logger.info(f"{posts=}")
            columns = [self.create_table_cols(k) for k in posts[0].keys()]
            logger.info(f"{columns=}")
        except Exception as e:
            msg = "Cannot load translated posts"
            logger.error(f"{type(e).__name__}: {e}. {msg}")

        with ui.dialog().props("full-width") as dialog:
            dialog.open()
            with ui.card().classes("flex-card-grow h-full"):
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
                        self.load_data(table.selected[0]["post_id"]),
                        dialog.close(),
                    ),
                )

    def run(self):
        ui.run(reload=False)
