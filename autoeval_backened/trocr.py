# trocr.py
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch

processor = TrOCRProcessor.from_pretrained(
    "microsoft/trocr-base-handwritten"
)

model = VisionEncoderDecoderModel.from_pretrained(
    "microsoft/trocr-base-handwritten"
)
model.eval()

def extract_text_with_trocr(pil_image: Image.Image) -> str:
    """
    ONLY for handwritten / cursive images
    """
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")

    with torch.no_grad():
        pixel_values = processor(
            images=pil_image,
            return_tensors="pt"
        ).pixel_values

        generated_ids = model.generate(
            pixel_values,
            max_length=256,
            num_beams=4
        )

        text = processor.batch_decode(
            generated_ids,
            skip_special_tokens=True
        )[0]

    return text.strip()
