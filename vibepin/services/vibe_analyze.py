"""
CLIP-based vibe analysis — v2.

Pipeline:
  1. Pre-encode per-category archetype text ensembles (cached at startup).
  2. Download user pin images concurrently.
  3. Encode each image → 512-dim vector.
  4. Classify each image: fashion | interior | aesthetic → keep; else skip.
  5. Average image embeddings per category (taste vector per category).
  6. Score each archetype: dot-product of that category's taste vector
     against that category's archetype text vector.
  7. Weighted-average scores across categories (weighted by image count).
  8. Z-score → softmax(T=1.5) → all 53 scores sum to 1.0 (100%).
"""

import asyncio

import httpx
import numpy as np

from vibepin.services import clip_model
from vibepin.services.archetype_data import ARCHETYPE_TEXTS

# ── Category classification ───────────────────────────────────────────────────

# Images we KEEP and which archetype-description bucket they map to
_KEEP_CATEGORIES: dict[str, str] = {
    "fashion":  "a fashion photo of a person wearing an outfit, clothing, or accessories",
    "interior": "a photo of a room, interior design, home decor, or living space",
    "aesthetic": "an aesthetic photo, mood board, beauty, makeup, flat lay, flowers, or texture",
}

# Images we SKIP — if any of these wins the argmax, drop the image
_SKIP_PROMPTS: list[str] = [
    "a photo of food, meal, cooking, or restaurant dish",
    "a travel or outdoor landscape or scenic nature photo",
    "a screenshot, text quote, meme, or social media post",
    "a photo of an animal, pet, or wildlife",
    "a diagram, infographic, or product catalog page",
]

# Cached text vectors
_cat_keep_vecs:  dict[str, np.ndarray] | None = None  # {category: vec}
_cat_skip_vecs:  list[np.ndarray] | None = None        # [vec, ...]
_archetype_vecs: dict[str, dict[str, np.ndarray]] | None = None
# shape: {archetype: {category: vec}}


async def _get_category_vecs() -> tuple[dict[str, np.ndarray], list[np.ndarray]]:
    global _cat_keep_vecs, _cat_skip_vecs
    if _cat_keep_vecs is not None:
        return _cat_keep_vecs, _cat_skip_vecs

    keep_texts = list(_KEEP_CATEGORIES.values())
    skip_texts  = _SKIP_PROMPTS

    all_texts = keep_texts + skip_texts
    all_vecs  = await asyncio.gather(*[clip_model.encode_text(t) for t in all_texts])

    keep_names = list(_KEEP_CATEGORIES.keys())
    _cat_keep_vecs = {
        keep_names[i]: all_vecs[i]
        for i in range(len(keep_names))
        if all_vecs[i] is not None
    }
    _cat_skip_vecs = [v for v in all_vecs[len(keep_names):] if v is not None]
    return _cat_keep_vecs, _cat_skip_vecs


async def _get_archetype_vecs() -> dict[str, dict[str, np.ndarray]]:
    """
    For each archetype and each category, average the CLIP embeddings
    of all text descriptions in that list (text ensemble).
    Missing categories fall back to the fashion vectors.
    """
    global _archetype_vecs
    if _archetype_vecs is not None:
        return _archetype_vecs

    categories = list(_KEEP_CATEGORIES.keys())  # ["fashion", "interior", "aesthetic"]

    # Flatten all texts we need to encode
    tasks: list[str] = []
    index: list[tuple[str, str, int]] = []  # (archetype, category, start_idx)

    for arch, cat_dict in ARCHETYPE_TEXTS.items():
        for cat in categories:
            phrases = cat_dict.get(cat) or cat_dict.get("fashion", [])
            start = len(tasks)
            tasks.extend(phrases)
            index.append((arch, cat, start, len(phrases)))

    # Encode everything in one parallel batch
    all_vecs = await asyncio.gather(*[clip_model.encode_text(t) for t in tasks])

    result: dict[str, dict[str, np.ndarray]] = {}
    for arch, cat, start, count in index:
        vecs = [all_vecs[start + i] for i in range(count) if all_vecs[start + i] is not None]
        if not vecs:
            continue
        avg = np.mean(vecs, axis=0)
        norm = np.linalg.norm(avg)
        if norm > 0:
            avg = avg / norm
        result.setdefault(arch, {})[cat] = avg

    # Ensure every archetype has all categories (fall back to fashion)
    for arch in result:
        fashion_vec = result[arch].get("fashion")
        if fashion_vec is None:
            continue
        for cat in categories:
            if cat not in result[arch]:
                result[arch][cat] = fashion_vec

    _archetype_vecs = result
    return _archetype_vecs


def _classify_image(
    img_vec: np.ndarray,
    keep_vecs: dict[str, np.ndarray],
    skip_vecs: list[np.ndarray],
) -> str | None:
    """Return keep category name, or None if the image should be skipped."""
    best_keep_cat  = max(keep_vecs, key=lambda c: float(np.dot(img_vec, keep_vecs[c])))
    best_keep_score = float(np.dot(img_vec, keep_vecs[best_keep_cat]))
    best_skip_score = max((float(np.dot(img_vec, sv)) for sv in skip_vecs), default=-1.0)

    # Skip if a skip prompt scores higher (with a small margin so borderline cases stay)
    if best_skip_score > best_keep_score - 0.01:
        return None
    return best_keep_cat


async def analyze_pins(pins: list[dict]) -> dict[str, float]:
    """
    Full pipeline: download → encode → classify → average embeddings per
    category → score archetypes → softmax normalize.
    Returns {archetype: probability} summing to 1.0.
    """
    keep_vecs, skip_vecs = await _get_category_vecs()
    archetype_vecs = await _get_archetype_vecs()

    if not archetype_vecs or not keep_vecs:
        return {}

    # ── Download images ───────────────────────────────────────────────────────
    image_urls = [p["image_url"] for p in pins if p.get("image_url")][:150]
    sem = asyncio.Semaphore(10)

    async def download(url: str) -> bytes | None:
        async with sem:
            try:
                async with httpx.AsyncClient(timeout=10.0) as c:
                    r = await c.get(url, follow_redirects=True)
                    return r.content if r.status_code == 200 else None
            except Exception:
                return None

    raw_images = await asyncio.gather(*[download(u) for u in image_urls])
    image_bytes_list = [b for b in raw_images if b]

    if not image_bytes_list:
        return {}

    # ── Encode all images ─────────────────────────────────────────────────────
    img_vecs = await asyncio.gather(*[
        clip_model.encode_image(b) for b in image_bytes_list
    ])

    # ── Classify + bucket ─────────────────────────────────────────────────────
    category_buckets: dict[str, list[np.ndarray]] = {c: [] for c in keep_vecs}
    for vec in img_vecs:
        if vec is None:
            continue
        cat = _classify_image(vec, keep_vecs, skip_vecs)
        if cat:
            category_buckets[cat].append(vec)

    # If everything was skipped, fall back to treating all images as fashion
    total_kept = sum(len(v) for v in category_buckets.values())
    if total_kept == 0:
        for vec in img_vecs:
            if vec is not None:
                category_buckets["fashion"].append(vec)

    # ── Average embedding per category ───────────────────────────────────────
    cat_taste_vecs: dict[str, np.ndarray] = {}
    cat_weights: dict[str, int] = {}
    for cat, vecs in category_buckets.items():
        if not vecs:
            continue
        avg = np.mean(vecs, axis=0)
        norm = np.linalg.norm(avg)
        if norm > 0:
            cat_taste_vecs[cat] = avg / norm
            cat_weights[cat] = len(vecs)

    if not cat_taste_vecs:
        return {}

    total_weight = sum(cat_weights.values())

    # ── Build ordered archetype list + matrix of archetype vectors per cat ────
    arch_names = list(archetype_vecs.keys())
    n_arch = len(arch_names)

    # arch_mat[cat] = (n_arch, 512) matrix of archetype vectors for that cat
    arch_mat: dict[str, np.ndarray] = {}
    for cat in cat_taste_vecs:
        rows = []
        for arch in arch_names:
            vec = archetype_vecs[arch].get(cat)
            if vec is None:
                vec = archetype_vecs[arch].get("fashion")
            rows.append(vec if vec is not None else np.zeros(512))
        arch_mat[cat] = np.stack(rows)  # (n_arch, 512)

    # ── Per-image sharp voting ────────────────────────────────────────────────
    # Each image votes for archetypes by soft-argmax (high T) rather than
    # contributing a tiny raw cosine similarity. Distinct style images commit
    # strongly to 1-3 archetypes; noise images spread flat and cancel out.
    T_VOTE = 20.0
    vote_totals = np.zeros(n_arch)

    for cat, img_vecs in category_buckets.items():
        if not img_vecs or cat not in arch_mat:
            continue
        w = cat_weights[cat] / total_weight
        mat = arch_mat[cat]  # (n_arch, 512)
        for img_vec in img_vecs:
            sims = mat @ img_vec  # (n_arch,) cosine sims
            # Standardize per image so scale doesn't matter, only relative rank
            mu_i, sd_i = sims.mean(), sims.std() or 1e-6
            z_i = (sims - mu_i) / sd_i
            votes = np.exp(z_i * T_VOTE)
            votes /= votes.sum()
            vote_totals += w * votes

    # ── Final softmax over accumulated votes → sum to 1.0 ────────────────────
    mu_v, sd_v = vote_totals.mean(), vote_totals.std() or 1e-6
    z_v   = (vote_totals - mu_v) / sd_v
    exp_v = np.exp(z_v * 2.0)   # moderate sharpening for final distribution
    probs = exp_v / exp_v.sum()

    return {name: round(float(p), 4) for name, p in zip(arch_names, probs)}
