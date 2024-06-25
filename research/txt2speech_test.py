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
    # from TTS.api import TTS

    # tts = TTS(model_path="~/.dotfiles/.cache/huggingface/hub/models--facebook--mms-tts-vie",)
    # tts.tts_to_file(text, speaker_wav="research/sound_3.wav", language="vi", file_path="research/sound_2_vc.wav")

    import torch
    from TTS.api import TTS

    # Get device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # List available 🐸TTS models
    # print(TTS().list_models())

    # Init TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    # Run TTS
    # ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
    # Text to speech list of amplitude values as output
    # wav = tts.tts(text="Hello world!", speaker_wav="my/cloning/audio.wav", language="en")
    # Text to speech to a file
    tts.tts_to_file(text="The Big Five personality traits, also known as the five-factor model (FFM) and the OCEAN model, is a taxonomy, or grouping, for personality traits.", language="en", file_path="output.wav")

def toucan_test(text: str): 
    from toucan.InferenceInterfaces.ControllableInterface import ControllableInterface
    import IPython
    from IPython.display import Audio
    import scipy
    
    controlable_interface = ControllableInterface(
        language='vie', 
        gpu_id="cuda", 
        available_artificial_voices=1000
    )
    
    sr, wav, fig = controlable_interface.read(
        prompt = text, 
        language='vie', 
        accent='vie', 
        voice_seed=300, 
        duration_scaling_factor=1, 
        pause_duration_scaling_factor=1, 
        pitch_variance_scale=1, 
        energy_variance_scale=1, 
        emb_slider_5=10, 
        emb_slider_1=0, 
        emb_slider_2=0,
        emb_slider_3=0, 
        emb_slider_4=0,
        emb_slider_6=0, 

    )
    IPython.display.display(Audio(wav, rate=24000))
    scipy.io.wavfile.write(f"research/story/toucan-{0}.wav", rate=24000, data=wav)
    return sr, wav, fig

toucan_test("""Khi tôi 11 tuổi, tôi đứng chót lớp cho đến khi giáo viên, cô Henry, bắt tôi ngồi cạnh một đứa mới. Thomas và gia đình chuyển đến thị trấn vào giữa học kỳ, vì vậy nó đùng phát xuất hiện trong lớp tôi thôi. Trong tuần thứ hai của mình, cô Henry đã cố gắng kéo nó ra khỏi vùng an toàn của mình bằng cách hỏi về chương trình truyền hình yêu thích của nó. "Chương trình truyền hình là gì ạ?"" nó trả lời.""")