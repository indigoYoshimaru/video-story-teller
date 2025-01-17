from pydantic import BaseModel
from typing import Text, Dict, Any
from pymongo import MongoClient
from loguru import logger


class TranslatorConfig(BaseModel):
    model_name: Text = "vinai/vinai-translate-en2vi-v2"
    device: Text = "cuda"
    src_lang: Text = "en_XX"
    dst_lang: Text = "vi_VN"


class Translator(BaseModel):
    tokenizer_params: Dict = dict(
        padding=True,
        return_tensors="pt",
    )
    generator_params: Dict = dict(
        num_return_sequences=1,
        num_beams=5,
        early_stopping=True,
        decoder_start_token_id=None,
    )
    decode_params: Dict = dict(skip_special_tokens=True)
    tokenizer: Any = None
    model: Any = None
    device: Any = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, config: TranslatorConfig = None):
        if not config:
            config = TranslatorConfig()

        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        try:
            logger.info(f"Initializing translator model...")
            device = torch.device(config.device)
            tokenizer = AutoTokenizer.from_pretrained(
                config.model_name,
                src_lang=config.src_lang,
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(config.model_name).to(device)

        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}. Cannot initialize translator model")
            raise e
        else:
            logger.success(f"Translator model initialized")
            super().__init__(tokenizer=tokenizer, model=model, device=device)
            self.generator_params["decoder_start_token_id"] = tokenizer.lang_code_to_id[
                config.dst_lang
            ]

    def split_batch(self, input_text: Text, batch_size: int = 5):

        try:
            from itertools import islice

            split_texts = iter(input_text.split("\n\n"))
            return iter(lambda: list(islice(split_texts, batch_size)), [])
        except Exception as e:
            logger.error(f"{type(e).__name__}: {e} cannot split batch")
            raise e

    def translate(self, input_text: Text):
        try:
            assert input_text, "Empty input text"
            output_texts = []
            # add batch processing!
            batch_texts = self.split_batch(input_text)

            for split_texts in batch_texts:
                input_ids = self.tokenizer(split_texts, **self.tokenizer_params).to(
                    self.device
                )
                output_ids = self.model.generate(**input_ids, **self.generator_params)
                output_texts += self.tokenizer.batch_decode(
                    output_ids, **self.decode_params
                )

            assert output_texts, "Empty output text"
        except Exception as e:
            logger.error(f"{type(e).__name__}: {e} happened during translation")
            raise e
        else:
            return "\n\n".join(output_texts)


class TranslatorPipeline(BaseModel):
    db_client: MongoClient
    translator: Translator

    class Config:
        arbitrary_types_allowed = True

    def run_pipeline(self, limit: int = 5):
        from toolz import pipe
        from toolz.curried import map
        from story_teller.database.crud.read import get_raw_posts

        try:
            logger.info(f"Running translator pipeline...")

            posts = list(get_raw_posts(self.db_client))[:limit]
            logger.info(f"{posts=}")
            translated_ids = pipe(
                posts,
                map(self.run_translate),
                map(self.update_to_db),
                list,
            )
            logger.info(f"Closing translator pipeline...")
        except Exception as e:
            raise e
        else:
            return translated_ids

    def run_translate(self, post):
        from story_teller.database.enum import StatusEnum

        try:
            logger.info(f"Translating post {post['post_id']}-{post['title']}")
            post["title_vn"] = self.translator.translate(post["title"])
            post["body_vn"] = self.translator.translate(post["body"])

        except Exception as e:
            logger.error(
                f"{type(e).__name__}: {e} happened during running translation in translator pipeline"
            )
            return post
        else:
            post["status"] = StatusEnum.translated.value
            logger.success(f"Translated {post['title_vn']=}")
            return post

    def update_to_db(self, post):
        from story_teller.database.crud.update import update_post

        try:
            logger.info(f"Updating to DB {post['post_id']}-{post['title']}")

            update_id = update_post(
                self.db_client,
                post=post,
            )
        except Exception as e:
            logger.error(
                f"{type(e).__name__}: {e} happened while updating post {post['post_id']}"
            )
            raise e
        else:
            logger.success(f"Updated post {post['post_id']}-{post['title']}")
            return update_id
