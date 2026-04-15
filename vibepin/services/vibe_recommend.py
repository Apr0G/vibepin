"""
Turn a vibe profile into shoppable product recommendations via SerpAPI Google Shopping.
Blends top 5 matching styles for diverse results.
"""

import asyncio

import httpx

from vibepin.core.config import settings

_SERPAPI_URL = "https://serpapi.com/search.json"

_QUERIES: dict[str, list[str]] = {
    "quiet luxury":        ["quiet luxury minimal dress women", "cashmere neutral coat women", "structured beige blazer women"],
    "clean girl":          ["clean girl aesthetic outfit women", "sleek minimalist neutral set women", "gold hoop white tank look"],
    "dark academia":       ["dark academia blazer women vintage", "plaid midi skirt women scholarly", "brown leather loafer women"],
    "light academia":      ["light academia linen blouse women", "cream cardigan pleated skirt women", "soft vintage academia outfit"],
    "cottagecore":         ["cottagecore floral prairie dress women", "linen gingham top women", "embroidered peasant blouse women"],
    "fairycore":           ["fairycore ethereal dress women", "sheer butterfly mesh top women", "iridescent pastel skirt women"],
    "Y2K":                 ["Y2K metallic mini skirt women", "2000s crop top rhinestone women", "low rise velvet flare Y2K women"],
    "e-girl":              ["e-girl outfit women alternative", "stripe long sleeve layered skirt women", "platform boots chains women"],
    "grunge":              ["grunge outfit women ripped jeans", "vintage band tee flannel shirt women", "combat boots leather jacket women"],
    "punk":                ["punk outfit women leather jacket studs", "fishnet tartan plaid skirt women", "platform chain boots punk women"],
    "goth":                ["goth outfit women black velvet", "gothic corset lace dress women", "platform boots choker goth women"],
    "streetwear":          ["streetwear oversized hoodie women", "cargo pants sneakers women urban", "graphic tee joggers women street"],
    "techwear":            ["techwear outfit women black nylon", "tactical cargo utility jacket women", "techwear boots women functional"],
    "gorpcore":            ["gorpcore fleece vest women outdoor", "hiking utility outfit women", "puffer technical jacket women trail"],
    "athleisure":          ["matching set leggings sports bra women luxury", "athleisure outfit women gym", "pilates set ribbed women"],
    "bohemian":            ["boho maxi floral dress women", "crochet festival top women", "bohemian wrap skirt women earthy"],
    "maximalist":          ["maximalist bold print dress women", "statement blazer clashing pattern women", "eclectic jewel tone outfit women"],
    "minimalist":          ["minimalist monochrome outfit women", "clean white wide leg trousers women", "simple black structured coat women"],
    "coquette":            ["coquette bow ribbon dress women", "satin pearl feminine outfit women", "lace corset top blush women"],
    "balletcore":          ["balletcore wrap cardigan leg warmers women", "ballet pink leotard outfit women", "ribbon detail dress balletcore"],
    "barbiecore":          ["hot pink dress barbiecore women", "fuchsia monochrome outfit women", "barbie pink blazer skirt set women"],
    "coastal grandmother": ["coastal grandmother linen trousers women", "stripe navy relaxed dress women", "straw hat linen set coastal women"],
    "preppy":              ["preppy polo shirt women classic", "argyle sweater plaid skirt women", "loafer headband collegiate women"],
    "French girl":         ["French girl Breton stripe top women", "Parisian trench coat women chic", "ballet flat beret French style women"],
    "tomboy":              ["tomboy baggy jeans oversized shirt women", "gender neutral skater outfit women", "dad fit sneakers women cool"],
    "western":             ["western cowboy boots women", "denim fringe jacket women western", "turquoise belt western chic women"],
    "mob wife":            ["mob wife fur coat women aesthetic", "leopard print dramatic coat women", "gold jewelry animal print outfit women"],
    "office siren":        ["office siren tailored blazer women", "pencil skirt stiletto power outfit women", "femme fatale workwear women"],
    "indie":               ["indie aesthetic vintage floral dress women", "70s flared jeans retro women", "thrift alternative art hoe outfit"],
    "soft girl":           ["soft girl pastel aesthetic outfit women", "kawaii bow floral dress women", "baby pink ruffle blush women"],
    "surfer":              ["surfer girl beach outfit women", "boardshort bikini coastal women", "sun-bleached denim cutoff beach look"],
    "regencycore":         ["regencycore puff sleeve dress women", "empire waist corset Bridgerton inspired", "lace gloves ribbon period women"],
    "mermaidcore":         ["mermaid sequin scale dress women", "iridescent holographic skirt women", "ocean shell jewelry mermaid aesthetic"],
    "angelcore":           ["white angel aesthetic dress women sheer", "celestial lace cream outfit women", "feather trim white top women angelic"],
    "dollcore":            ["dollcore lace ruffle dress women", "Victorian doll aesthetic outfit women", "bow ribbon porcelain doll dress"],
    "vintage glamour":     ["1950s pin-up dress women", "rockabilly polka dot wiggle dress women", "vintage 50s pencil skirt women"],
    "old Hollywood":       ["old Hollywood glamour dress women", "1950s satin gown women opera gloves", "vintage starlet pearl outfit women"],
    "kawaii":              ["kawaii pastel outfit women Japanese", "Harajuku fashion cute women colorful", "kawaii strawberry dress women sweet"],
    "art hoe":             ["art hoe aesthetic outfit women", "turtleneck beret corduroy women", "vintage oversized blazer sunflower women"],
    "VSCO girl":           ["VSCO girl aesthetic outfit women summer", "oversized tee scrunchie women beach", "Birkenstock shell necklace women casual"],
    "coconut girl":        ["coconut girl tropical floral dress women", "hibiscus print sarong women beach", "island aesthetic straw bag floral women"],
    "witchcore":           ["witchcore outfit women dark mystical", "moon star velvet dress women gothic", "crystal tarot aesthetic outfit women"],
    "après ski":           ["après ski outfit women cozy", "fur trim puffer jacket women lodge", "Nordic knit sweater women ski chalet"],
    "princesscore":        ["princess ballgown dress women fairy tale", "tiara sparkle gown women pink", "tulle princess dress women pastel"],
    "twee":                ["twee aesthetic dress women vintage floral", "Peter Pan collar dress women cute", "bow headband cardigan women quirky"],
    "flowercore":          ["floral crown flower girl dress women", "botanical print dress women garden", "daisy floral cottagecore dress women"],
    "blokette":            ["blokette aesthetic outfit women football", "jersey mini skirt sporty women kit", "sporty girly outfit women trainers"],
    "90s supermodel":      ["90s slip dress women minimalist", "Calvin Klein style minimal dress women", "90s fashion blazer trouser women"],
    "party girl":          ["sequin mini dress party women night out", "rhinestone bodycon dress women", "metallic going out outfit women glam"],
    "glazed donut":        ["glazed donut aesthetic outfit women neutral", "pearl shimmer top women minimal", "neutral monochrome glossy outfit women"],
    "academia fashion":    ["academic blazer trousers women gender neutral", "smart casual collegiate outfit women", "knit vest button down women layered"],
    "dreamcore":           ["dreamcore aesthetic pastel outfit women", "dreamy sheer dress women surreal", "vaporwave pastel vintage outfit women"],
}


async def _search(query: str) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(
                _SERPAPI_URL,
                params={
                    "engine": "google_shopping",
                    "q": query,
                    "api_key": settings.serpapi_key,
                    "num": 8,
                },
            )
            r.raise_for_status()
        items = r.json().get("shopping_results", [])
        results = []
        for item in items:
            link = item.get("link") or item.get("product_link", "")
            if not link:
                continue
            results.append({
                "title": item.get("title", ""),
                "link": link,
                "source": item.get("source", ""),
                "thumbnail": item.get("thumbnail", ""),
                "price": item.get("price"),
            })
        return results
    except Exception:
        return []


async def recommend(
    vibe_profile: dict[str, float],
    max_results: int = 48,
) -> list[dict]:
    """
    Pick top 5 styles by score, run 3 queries each (15 total in parallel),
    interleave results so all styles are represented, then deduplicate.
    """
    top_styles = sorted(vibe_profile.items(), key=lambda x: x[1], reverse=True)[:5]

    # Gather 3 queries per style
    style_queries: list[tuple[str, str]] = []
    for style, _ in top_styles:
        for q in (_QUERIES.get(style) or [])[:3]:
            style_queries.append((style, q))

    if not style_queries:
        return []

    all_results = await asyncio.gather(*[_search(q) for _, q in style_queries])

    # Interleave: take one result from each style batch in round-robin
    # so the final list isn't dominated by just the #1 style
    buckets: list[list[dict]] = list(all_results)
    seen: set[str] = set()
    merged: list[dict] = []

    while any(buckets) and len(merged) < max_results:
        for bucket in buckets:
            while bucket:
                item = bucket.pop(0)
                if item["link"] not in seen:
                    seen.add(item["link"])
                    merged.append(item)
                    break

    return merged[:max_results]
