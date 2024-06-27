from story_teller.crawler import reddit
from story_teller.editor import __main__ as editor
from story_teller.generator import __main__ as generator
from typer import Typer

from loguru import logger

app = Typer(no_args_is_help=True)
app.add_typer(reddit.app)
app.add_typer(editor.app)
app.add_typer(generator.audio_app)
app.add_typer(generator.image_app)

if __name__ in {"__main__", "__mp_main__"}:
    app()

