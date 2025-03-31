from transformers import VitsModel, AutoTokenizer, set_seed
import torch
from ruaccent import RUAccent


def generate_speech(image_description: str, device='cpu', speaker=0, seed=555):   # speaker: 0-woman, 1-man

    set_seed(seed)  # make deterministic

    model_name = "utrobinmv/tts_ru_free_hf_vits_low_multispeaker"

    model = VitsModel.from_pretrained(model_name).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model.eval()

    # load accentizer
    accentizer = RUAccent()
    accentizer.load(omograph_model_size='turbo', use_dictionary=True, device=device)

    text = accentizer.process_all(image_description.replace("\n", " "))

    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        output = model(**inputs.to(device), speaker_id=speaker).waveform
        output = output.detach().cpu().numpy().squeeze() # .squeeze() удаляет лишние измерения
    
    return output, model.config.sampling_rate