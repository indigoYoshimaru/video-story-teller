from typer import Typer
from story_teller.editor.text_editor import TextEditor, ui
app = Typer(name="editor", no_args_is_help=True)


@app.command(name="translate")
def translate_all_raw(
    limit: int = 3,
):
    from story_teller.database import connect
    from story_teller.editor import translator

    e2v_translator = translator.Translator()
    db_client = connect.connect_db()
    translator_pipeline = translator.TranslatorPipeline(
        db_client=db_client, translator=e2v_translator
    )
    translated_ids = translator_pipeline.run_pipeline(limit=limit)
    return translated_ids


@app.command(name="edit")
def open_editor(dark_mode: bool = False): 
    from story_teller.database import connect

    db_client = connect.connect_db()
    editor = TextEditor(db_client=db_client)
    editor.run()    
