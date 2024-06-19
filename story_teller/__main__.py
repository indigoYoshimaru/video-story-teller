from story_teller.crawler import reddit
from story_teller.editor import __main__ as editor
from typer import Typer

from loguru import logger

app = Typer(no_args_is_help=True)
app.add_typer(reddit.app)
app.add_typer(editor.app)

if __name__ == '__main__': 
    app()

