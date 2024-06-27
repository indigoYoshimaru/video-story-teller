from pydantic import BaseModel
from transformers import VitsModel, AutoTokenizer, set_seed
from vinorm import TTSnorm
from typing import Text, List
from underthesea import sent_tokenize
import torch
from loguru import logger
from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np


class AudioGenerator(BaseModel):
    tokenizer: AutoTokenizer
    model: VitsModel

    def __init__(self, device, model_name):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = VitsModel.from_pretrained(model_name).to(device)
        super().__init__(model=model, tokenizer=tokenizer)

    def process_for_tts(self, paragraph: Text):
        import re

        pattern = r"([" + re.escape(",.?!()") + "])"
        result = TTSnorm(paragraph, lower=False, unknown=False)
        result = re.sub(pattern, r"\1 ' ", result)
        result = sent_tokenize(result)
        return result

    def pre_process(self, text: Text) -> List:
        paragraphs = text.split("\n\n")
        paragraphs = [self.process_for_tts(par) for par in paragraphs]
        return paragraphs

    def generate(self, paragraph):
        try:
            inputs = self.tokenizer(
                paragraph,
                return_tensors="pt",
                padding=True,
            ).to("cuda")

            with torch.no_grad():
                output = self.model(**inputs).waveform

            output = output.cpu().numpy().squeeze()

        except Exception as e:
            logger.error(
                f"{type(e).__name__}: {e} happened during generating audio for paragraph: \n{paragraph}"
            )
            raise e
        else:
            return output

    def post_process(self, waves):
        silence_thresh = -35  # in dBFS, adjust according to your audio
        min_silence_len = 500  # in milliseconds

        # each paragraph has multiple output wave <-> each wave is a sentence
        try:
            filtered_audio = AudioSegment.empty()
            for waveform in waves:
                waveform_integers = np.int16(waveform * 32767)  # Convert to 16-bit PCM

                # Convert the integer waveform to byte data
                byte_data = waveform_integers.tobytes()
                audio = AudioSegment(
                    data=byte_data,
                    sample_width=waveform_integers.dtype.itemsize,
                    frame_rate=self.model.config.sampling_rate,
                    channels=1,
                )

                # Split audio on silence
                chunks = split_on_silence(
                    audio,
                    min_silence_len=min_silence_len,
                    silence_thresh=silence_thresh,
                    keep_silence=100,
                )  # Add a bit of silence back

                # Concatenate chunks to form the final audio

                for chunk in chunks:
                    filtered_audio += chunk

        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}")
            raise e
        else:
            return filtered_audio
