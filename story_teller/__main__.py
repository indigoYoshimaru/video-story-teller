from story_teller.crawler import reddit
from typer import Typer

from loguru import logger

app = Typer(no_args_is_help=True)
app.add_typer(reddit.app)

if __name__ == '__main__': 
    app()

