"""
CLIP-based content moderation for try-on uploads.
Checks person photos for nudity and garment photos for underwear/lingerie.
"""

import numpy as np

from vibepin.services import clip_model

# ── Person photo safety ───────────────────────────────────────────────────────

_PERSON_SAFE_PROMPTS = [
    "a fully clothed person standing in normal clothing",
    "a person wearing a complete outfit with shirt and pants or dress",
]
_PERSON_UNSAFE_PROMPTS = [
    "a nude or topless or naked person showing skin",
    "a person wearing only underwear or a bikini",
    "a partially undressed person",
]

# ── Garment safety ────────────────────────────────────────────────────────────

_GARMENT_SAFE_PROMPTS = [
    "a dress, shirt, jacket, coat, pants, skirt, or sweater laid flat",
    "outerwear or full clothing item on a white background",
]
_GARMENT_UNSAFE_PROMPTS = [
    "underwear, bra, panties, or lingerie",
    "a bikini, swimsuit, or swimwear",
    "intimate apparel or barely-there clothing",
]

import asyncio as _asyncio

# Cache encoded prompt vectors
_person_safe_vecs: list[np.ndarray] | None = None
_person_unsafe_vecs: list[np.ndarray] | None = None
_garment_safe_vecs: list[np.ndarray] | None = None
_garment_unsafe_vecs: list[np.ndarray] | None = None
_init_lock = _asyncio.Lock()


async def _ensure_vecs() -> None:
    global _person_safe_vecs, _person_unsafe_vecs, _garment_safe_vecs, _garment_unsafe_vecs
    # Fast path — already initialised
    if _person_safe_vecs is not None:
        return
    # Serialise concurrent initialisations so only one coroutine runs the
    # expensive CLIP text-encoding and sets the globals.
    async with _init_lock:
        if _person_safe_vecs is not None:
            return  # Another coroutine beat us to it
        all_prompts = (
            _PERSON_SAFE_PROMPTS
            + _PERSON_UNSAFE_PROMPTS
            + _GARMENT_SAFE_PROMPTS
            + _GARMENT_UNSAFE_PROMPTS
        )
        vecs = await _asyncio.gather(*[clip_model.encode_text(p) for p in all_prompts])
        n_ps = len(_PERSON_SAFE_PROMPTS)
        n_pu = len(_PERSON_UNSAFE_PROMPTS)
        n_gs = len(_GARMENT_SAFE_PROMPTS)
        # Set all four atomically (assign in one go before any await)
        _person_safe_vecs   = [v for v in vecs[:n_ps] if v is not None]
        _person_unsafe_vecs = [v for v in vecs[n_ps:n_ps+n_pu] if v is not None]
        _garment_safe_vecs  = [v for v in vecs[n_ps+n_pu:n_ps+n_pu+n_gs] if v is not None]
        _garment_unsafe_vecs = [v for v in vecs[n_ps+n_pu+n_gs:] if v is not None]


def _avg_sim(img_vec: np.ndarray, prompt_vecs: list[np.ndarray]) -> float:
    if not prompt_vecs:
        return 0.0
    return float(np.mean([np.dot(img_vec, pv) for pv in prompt_vecs]))


async def check_person_photo(image_bytes: bytes) -> tuple[bool, str]:
    """
    Returns (is_safe, reason).
    is_safe=False means the image should be rejected.
    """
    await _ensure_vecs()
    img_vec = await clip_model.encode_image(image_bytes)
    if img_vec is None:
        # CLIP unavailable — fail open (don't block valid images)
        return True, "ok"

    safe_score   = _avg_sim(img_vec, _person_safe_vecs)
    unsafe_score = _avg_sim(img_vec, _person_unsafe_vecs)

    if unsafe_score > safe_score + 0.05:
        return False, "Please upload a photo where you are fully clothed."
    return True, "ok"


async def check_garment_photo(image_bytes: bytes) -> tuple[bool, str]:
    """
    Returns (is_safe, reason).
    Rejects underwear, lingerie, bikinis, swimwear.
    """
    await _ensure_vecs()
    img_vec = await clip_model.encode_image(image_bytes)
    if img_vec is None:
        # CLIP unavailable — fail open
        return True, "ok"

    safe_score   = _avg_sim(img_vec, _garment_safe_vecs)
    unsafe_score = _avg_sim(img_vec, _garment_unsafe_vecs)

    if unsafe_score > safe_score + 0.05:
        return False, "Only full clothing items are supported (no underwear, lingerie, or swimwear)."
    return True, "ok"
