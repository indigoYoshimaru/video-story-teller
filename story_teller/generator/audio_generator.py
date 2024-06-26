from pydantic import BaseModel
from story_teller.database.connect import MongoClient 
from transformers import VitsModel, AutoTokenizer, set_seed
from vinorm import TTSnorm
from typing import Text, List
from underthesea import sent_tokenize
import torch

class AudioGenerator(BaseModel): 
    db_client: MongoClient
    tokenizer: AutoTokenizer
    model: VitsModel

    def __init__(self, device, model_name): 
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = VitsModel.from_pretrained(model_name).to(device)
        super().__init__(model = model, tokenizer = tokenizer)

    def process_for_tts(self, paragraph: Text): 
        import re

        pattern = r"([" + re.escape(",.?!()") + "])"
        result = TTSnorm(paragraph, lower= False, unknown = False)
        result = re.sub(pattern, r"\1 ' ", result)
        result = sent_tokenize(result)
        return result

    def preprocess(self, text: Text) -> List: 
        paragraphs = text.split('\n\n')
        paragraphs = [self.process_for_tts(par) for par in paragraphs]
        return paragraphs
    
    def generate(self, paragraph): 
        