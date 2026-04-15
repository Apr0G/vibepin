"""
CLIP model singleton — loads once, runs inference in a thread pool.
Uses openai/clip-vit-base-patch32 (~600 MB, downloaded on first call).
"""

import asyncio
import io
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import numpy as np
from PIL import Image

_executor = ThreadPoolExecutor(max_workers=2)


@lru_cache(maxsize=1)
def _load():
    from transformers import CLIPModel, CLIPProcessor

    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.eval()
    return model, processor


def _norm(vec) -> np.ndarray:
    n = np.linalg.norm(vec)
    return vec / n if n else vec


def _encode_image_sync(image_bytes: bytes) -> np.ndarray:
    import torch

    model, processor = _load()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        vision_out = model.vision_model(pixel_values=inputs["pixel_values"])
        features = model.visual_projection(vision_out.pooler_output)  # (1, 512)
    return _norm(features.squeeze().numpy())  # (512,)


def _encode_text_sync(text: str) -> np.ndarray:
    import torch

    model, processor = _load()
    inputs = processor(text=[text], return_tensors="pt", padding=True, truncation=True, max_length=77)
    with torch.no_grad():
        text_out = model.text_model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
        )
        features = model.text_projection(text_out.pooler_output)  # (1, 512)
    return _norm(features.squeeze().numpy())  # (512,)


async def encode_image(image_bytes: bytes) -> np.ndarray | None:
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(_executor, _encode_image_sync, image_bytes)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("CLIP encode_image failed: %s", e)
        return None


async def encode_text(text: str) -> np.ndarray | None:
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(_executor, _encode_text_sync, text)
    except Exception:
        return None
