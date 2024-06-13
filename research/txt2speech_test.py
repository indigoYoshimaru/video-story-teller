from transformers import VitsModel, AutoTokenizer, set_seed
import torch
import numpy as np
import torch


def txt2speech(text):
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
    model = VitsModel.from_pretrained(
        "facebook/mms-tts-vie",
    ).to("cuda")

    set_seed(555)
    model.speaking_rate = 1.5

    inputs = tokenizer(text, return_tensors="pt", padding=True).to("cuda")
    with torch.no_grad():
        output = model(**inputs).waveform

    print(output)
    output = output.clone().detach().cpu()

    # output = torch.tensor(output, device="cpu")

    return output, model


# print(type(output), output.get_device())
# scipy.io.wavfile.write("techno.wav", rate=model.config.sampling_rate, data=output)
