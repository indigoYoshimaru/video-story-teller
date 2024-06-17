from transformers import VitsModel, AutoTokenizer, set_seed
import torch
import numpy as np


def txt2speech(text):
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
    model = VitsModel.from_pretrained(
        "facebook/mms-tts-vie",
    ).to("cuda")

    set_seed(100)
    model.speaking_rate = 1

    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
    ).to("cuda")
    with torch.no_grad():
        output = model(**inputs).waveform

    print(output)
    # output = output.clone().detach().cpu()
    output = output.cpu().numpy().squeeze()
    return output, model

def tts_test(text): 
    from TTS.api import TTS

    tts = TTS(model_path="~/.dotfiles/.cache/huggingface/hub/models--facebook--mms-tts-vie",)
    tts.tts_to_file(text, speaker_wav="research/sound_3.wav", language="vi", file_path="research/sound_2_vc.wav")

