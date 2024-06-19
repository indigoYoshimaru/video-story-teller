from pydantic import BaseModel
from typing import Text, Dict, Any, List
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

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, config: TranslatorConfig):
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
            super().__init__(tokenizer=tokenizer, model=model)
            self.generator_params["decoder_start_token_id"] = tokenizer.lang_code_to_id[
                config.dst_lang
            ]

    def translate(self, input_text: Text):
        try:
            assert input_text, "Empty input text"

            split_texts = input_text.split("\n\n")

            input_ids = self.tokenizer(split_texts, **self.tokenizer_params)
            output_ids = self.model.generate(**input_ids, **self.generator_params)
            output_texts = self.tokenizer.batch_decode(output_ids, **self.decode_params)

            assert output_texts, "Empty output text"
        except Exception as e:
            logger.error(f"{type(e).__name__}: {e} happened during translation")
            raise e
        else:
            return output_texts.join("\n\n")


