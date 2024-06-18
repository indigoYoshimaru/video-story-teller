from typer import Typer

app = Typer(name="reddit-crawler", no_args_is_help=True)


@app.command(name="hotposts")
def crawl_hotposts(
    env_file_path: str = "story_teller/crawler/.env",
    video_root_path: str = "/mnt/sda1/Linh_store/nosleep-videos",
    subreddit_name: str = "nosleep",
    limit: int = 5,
):
    import praw
    from story_teller.utils import read_env
    from story_teller.database import connect
    from story_teller.crawler.pipeline import CrawlerPipeline

    client_info = read_env(env_file=env_file_path)
    reddit = praw.Reddit(**client_info)
    subreddit = reddit.subreddit(subreddit_name)

    db_client = connect.connect_db()
    crawler_pipeline = CrawlerPipeline(
        db_client=db_client, video_root_path=video_root_path
    )
    posts = subreddit.hot(limit=limit)
    inserted_posts = crawler_pipeline.run_pipeline(posts)
