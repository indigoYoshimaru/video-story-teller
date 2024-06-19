from toolz import pipe
from pydantic import BaseModel
from pymongo import MongoClient
from typing import Text
from loguru import logger


class CrawlerPipeline(BaseModel):
    db_client: MongoClient
    video_root_path: Text

    class Config:
        arbitrary_types_allowed = True

    def run_pipeline(self, posts):
        from toolz.curried import map, filter

        logger.info(f"Running crawler pipeline...")
        results = pipe(
            posts,
            filter(self.run_filter),
            map(self.process),
            map(self.create_video_folder),
            list,
            self.insert_to_db,
        )
        logger.info(f"Closing crawler pipeline...")
        return results

    def run_filter(self, post):
        from story_teller.database.crud.read import get_post

        try:
            logger.info(f"Checking duplicate {post.id}-{post.title}")
            similar_post = get_post(
                db_client=self.db_client,
                post_id=post.id,
            )
            if similar_post:
                raise FileExistsError
        except FileExistsError as e:
            logger.error(f"{type(e).__name__}: Similar post(s) exist(s). Skipping...")
            return False
        else:
            return True

    def process(self, post):
        from story_teller.database.enum import StatusEnum
        import os

        try:
            post_dict = dict(
                post_id=post.id,
                subreddit=post.subreddit.display_name,
                title=post.title,
                title_vn="",
                url=post.url,
                body=post.selftext,
                body_vn="",
                created=post.created,
                status=StatusEnum.raw.value,
                image_dir=os.path.join(self.video_root_path, post.id, "images"),
                audio_dir=os.path.join(self.video_root_path, post.id, "audios"),
            )

        except Exception as e:
            logger.error(
                f"{type(e).__name__}: {e} happened while processing post {post.id}-{post.title}"
            )
            pass
        else:
            logger.success(f"Processed post:\n {post_dict}")
            return post_dict

    def create_video_folder(self, post):
        import os

        try:
            image_dir = post["image_dir"]
            audio_dir = post["audio_dir"]
            if not os.path.exists(image_dir):
                logger.info(f"Creating video folder at {image_dir.split('/')[:-1]}")
                os.makedirs(image_dir)
                os.makedirs(audio_dir)
        except Exception as e:
            logger.error(
                f"{type(e).__name__}: {e}. Cannot create folders for {post['post_id']}-{post['title']}"
            )
            return post
        else:
            return post

    def insert_to_db(self, posts):
        from story_teller.database.crud.create import insert_post_many

        logger.info(f"{type(posts)}-{posts}")
        inserted_ids = insert_post_many(posts=posts, db_client=self.db_client)
        logger.info(f"Inserted ids: {inserted_ids}")
        return inserted_ids
