from typer import Typer

audio_app = Typer(name="audio", no_args_is_help=True)


@audio_app.command(name="generate-post")
def generate_audio(
    post_id: str = "",
    device: str = "cuda",
    model_name: str = "facebook/mms-tts-vie",
    seed: int = 500,
    speed: float = 1.2,
):
    from story_teller.generator.audio_generator import AudioGenerator
    from story_teller.database.connect import connect_db
    from story_teller.generator.pipeline import GeneratorPipeline

    db_client = connect_db()
    audio_generator = AudioGenerator(
        device=device,
        model_name=model_name,
        seed=seed,
    )
    audio_generator.set_speed(speed)
    pipeline = GeneratorPipeline(db_client=db_client, generator=audio_generator)
    pipeline.run_generate_pipeline(post_id)


@audio_app.command(name="edit")
def edit_single_audio(
    post_id: str,
    audio_index: int,
    speed: float,
    device: str = "cuda",
    model_name: str = "facebook/mms-tts-vie",
    seed: int = 500,
):
    from story_teller.generator.audio_generator import AudioGenerator
    from story_teller.database.connect import connect_db
    from story_teller.generator.pipeline import GeneratorPipeline

    db_client = connect_db()
    audio_generator = AudioGenerator(
        device=device,
        model_name=model_name,
        seed=seed,
    )
    print(f"{speed=}")
    audio_generator.set_speed(speed)
    pipeline = GeneratorPipeline(db_client=db_client, generator=audio_generator)
    pipeline.run_edit_pipeline(post_id, media_index=audio_index)


image_app = Typer(name="image", no_args_is_help=True)


@image_app.command(name="generate-post")
def generate_image(
    post_id: str,
    device: str = "cuda",
    model_name: str = "facebook/mms-tts-vie",
    seed: int = 500,
): ...


@image_app.command(name="edit")
def edit_single_image(
    post_id: str,
    image_index: int,
): ...
