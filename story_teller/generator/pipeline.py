from pydantic import BaseModel
from typing import Text, Dict, Any
from pymongo import MongoClient
from loguru import logger


class GeneratorPipeline(BaseModel):
    db_client: MongoClient
    generator: Any
    media_type: Text = "audio"
    save_dir: Text = ""

    class Config:
        arbitrary_types_allowed = True

    def run_generate_pipeline(self, post_id: Text):
        from toolz import pipe
        from toolz.curried import map
        from story_teller.database.crud.read import get_edited_posts, get_post

        try:
            logger.info(f"Running translator pipeline...")
            if post_id:
                post = get_post(self.db_client, post_id)
            else:
                post = list(get_edited_posts(self.db_client, sorted=True))[0]

            body = post["body"]
            if self.media_type == "audio":
                body = post["body_vn"]

            self.save_dir = post[f"{self.media_type}_dir"]
            logger.info(f"{post=}")
            pipe(
                body,
                self.generator.pre_process,
                map(self.generator.generate),
                map(self.generator.post_process),
                map(self.save),
                list,
            )
            logger.info(f"Closing translator pipeline...")
        except Exception as e:
            raise e
        else:
            logger.success(
                f"{self.media_type} generated and saved successfully to {self.save_dir}"
            )

    def run_edit_pipeline(self, post_id: Text, media_index: int):
        from toolz import pipe
        from toolz.curried import map
        from story_teller.database.crud.read import get_edited_posts, get_post

        try:
            logger.info(f"Running translator pipeline...")
            if post_id:
                post = get_post(self.db_client, post_id)
            else:
                post = list(get_edited_posts(self.db_client, sorted=True))[0]

            body = post["body"]
            if self.media_type == "audio":
                body = post["body_vn"]
            body = [self.generator.pre_process(body)[media_index]]
            self.save_dir = post[f"{self.media_type}_dir"]
            logger.info(f"{body=}")
            pipe(
                body,
                map(self.generator.generate),
                map(self.generator.post_process),
                map(self.save),
                list,
            )
            logger.info(f"Closing translator pipeline...")
        except Exception as e:
            raise e
        else:
            logger.success(
                f"{self.media_type} generated and saved successfully to {self.save_dir}"
            )

    def save(self, output_dict):
        import os

        try:
            idx = output_dict["idx"]
            output = output_dict["output"]
            if self.media_type == "audio":
                path = os.path.join(self.save_dir, f"{idx}.wav")
                output.export(path, format="wav")
            else:
                pass

        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}")
            raise e
        else:
            logger.success(f"Saved {self.media_type} to {path}")
