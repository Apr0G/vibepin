import re
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

from vibepin.core.config import settings

_SERPAPI_URL = "https://serpapi.com/search.json"

# ── Domains that are never stores ────────────────────────────────────────────
_NON_RETAIL_BLACKLIST = {
    # Social / image boards
    "pinterest.com", "pinterest.co.uk", "pin.it",
    "instagram.com", "facebook.com", "twitter.com", "x.com",
    "tiktok.com", "tumblr.com", "reddit.com",
    "youtube.com", "youtu.be",
    # Blogs / publishing
    "blogspot.com", "wordpress.com", "medium.com", "substack.com",
    "squarespace.com", "wix.com",
    # Reference / wiki
    "wikipedia.org", "wikimedia.org",
    # Fashion editorial / media
    "vogue.com", "elle.com", "harpersbazaar.com", "cosmopolitan.com",
    "glamour.com", "whowhatwear.com", "refinery29.com", "popsugar.com",
    "buzzfeed.com", "who.com.au", "instyle.com", "marieclaire.com",
    "wgsn.com", "lookbook.nu", "chictopia.com", "polyvore.com",
    "thecut.com", "fashionista.com", "manrepeller.com", "byrdie.com",
    "stylist.co.uk", "grazia.co.uk", "harpers.co.uk",
}

# ── URL path patterns that indicate editorial / content pages ─────────────────
# Even if the domain isn't blacklisted, these paths are articles, not products.
_EDITORIAL_PATH_RE = re.compile(
    r"/("
    r"article|articles|post|posts|blog|blogs|news|editorial|"
    r"story|stories|feature|features|guide|guides|"
    r"review|reviews|trend|trends|lookbook|outfit|inspiration|"
    r"tag|tags|category|categories|topic|topics|search|"
    r"how-to|style-guide|get-the-look"
    r")s?[/-]",
    re.IGNORECASE,
)

# ── Inditex group (kept for reference — no longer used for filtering) ─────────
_OLD_RETAIL_ALLOWLIST_STUB = {
    "zara.com", "bershka.com", "pullandbear.com", "stradivarius.com",
    "massimodutti.com", "oysho.com", "zarahoma.com", "zarakids.com",

    # ── H&M group ─────────────────────────────────────────────────────────────
    "hm.com", "cos.com", "arket.com", "weekday.com", "monki.com",
    "otherstories.com", "stories.com", "cheapmonday.com",

    # ── Other fast fashion ────────────────────────────────────────────────────
    "mango.com", "uniqlo.com", "primark.com", "forever21.com",
    "shein.com", "romwe.com", "zaful.com", "fashionnova.com",
    "boohoo.com", "prettylittlething.com", "nastygal.com",
    "missguided.com", "missselfridge.com", "quiz.co.uk",
    "joesandwich.com", "reserved.com", "cropp.com", "sinsay.com",
    "mohito.com", "house.pl",

    # ── UK high street ────────────────────────────────────────────────────────
    "riverisland.com", "newlook.com", "dorothyperkins.com",
    "warehouse.co.uk", "wallis.co.uk", "topshop.com", "topman.com",
    "next.co.uk", "nextdirect.com", "fatface.com", "whitestuff.com",
    "joules.com", "boden.co.uk", "lauraashley.com", "ghost.co.uk",
    "karen-millen.com", "coast-stores.com", "dune.co.uk", "schuh.co.uk",
    "office.co.uk", "kurtgeiger.com", "lkbennett.com", "monsoon.co.uk",
    "accessorize.com", "mintvelvet.co.uk", "hush-uk.com", "cefinn.com",
    "rixo.co.uk", "frenchconnection.com", "phase-eight.com", "tedbaker.com",
    "reiss.com", "whistles.com", "hobbs.com", "oasisfashion.com",
    "littlewoods.com", "simplybe.co.uk", "bonmarche.co.uk", "peacocks.co.uk",
    "georgeclothing.com", "figleaves.com", "bravissimo.com",

    # ── US mass market ────────────────────────────────────────────────────────
    "gap.com", "oldnavy.com", "bananarepublic.com", "jcrew.com",
    "jcrewfactory.com", "madewell.com", "ae.com", "aerie.com",
    "abercrombie.com", "hollisterco.com", "express.com", "loft.com",
    "anntaylor.com", "whbm.com", "chicos.com", "soma.com",
    "talbots.com", "landsend.com", "llbean.com", "orvis.com",
    "patagonia.com", "rei.com", "eddybauer.com", "columbia.com",
    "jcpenney.com", "kohls.com", "target.com", "walmart.com",
    "belk.com", "dillards.com", "vonmaur.com", "bealls.com",
    "maurices.com", "dressbarn.com", "catherines.com",

    # ── US mid-range & contemporary ──────────────────────────────────────────
    "revolve.com", "shopbop.com", "anthropologie.com", "freepeople.com",
    "urbanoutfitters.com", "reformation.com", "everlane.com",
    "clubmonaco.com", "theory.com", "vince.com", "joie.com",
    "alice-olivia.com", "aliceandolivia.com", "dvf.com",
    "rebeccaminkoff.com", "toryburch.com", "katespade.com",
    "coach.com", "michaelkors.com", "kors.com", "dkny.com",
    "tahari.com", "eileenfisher.com", "allsaints.com",
    "rag-bone.com", "ragbone.com", "frame.store", "agolde.com",
    "paige.com", "motherdenim.com", "citizensofhumanity.com",
    "7forallmankind.com", "currentelliott.com", "grlfrnd.com",
    "jbrandjeans.com", "baldwinjeans.com", "3x1.us",
    "staud.clothing", "cult-gaia.com", "simon-miller.com",
    "loefflerrandall.com", "kayu.com", "lizadonnelly.com",
    "shopspring.com", "intermix.com", "forward.com",
    "moda-operandi.com", "shopbazaar.com", "lulus.com",
    "showpo.com", "missguided.us",

    # ── US department stores ──────────────────────────────────────────────────
    "nordstrom.com", "nordstromrack.com", "bloomingdales.com",
    "saksfifthavenue.com", "saks.com", "neimanmarcus.com",
    "lastcall.com", "macys.com", "lordandtaylor.com",
    "selfridges.com", "harveynichols.com", "harrods.com",
    "johnlewis.com", "marksandspencer.com", "debenhams.com",

    # ── Luxury conglomerates / multi-brand ───────────────────────────────────
    "net-a-porter.com", "mrporter.com", "farfetch.com", "ssense.com",
    "matchesfashion.com", "mytheresa.com", "ounass.com",
    "luisaviaroma.com", "antonioli.eu", "biffi.com",
    "yoox.com", "24s.com", "cettire.com", "italist.com",
    "coggles.com", "oki-ni.com", "endclothing.com",
    "dover-street-market.com", "slam-jam.com", "kith.com",
    "bodega.com", "wolf-and-badger.com", "trouva.com",

    # ── Luxury / designer ─────────────────────────────────────────────────────
    "gucci.com", "prada.com", "louisvuitton.com", "dior.com",
    "chanel.com", "burberry.com", "versace.com", "valentino.com",
    "bottegaveneta.com", "alexandermcqueen.com", "balenciaga.com",
    "givenchy.com", "loewe.com", "celine.com", "ysl.com",
    "saintlaurent.com", "moncler.com", "brunellocucinelli.com",
    "loropiana.com", "maxmara.com", "tods.com", "ferragamo.com",
    "jimmychoo.com", "manoloblahnik.com", "christianlouboutin.com",
    "rogervivier.com", "aquazzura.com", "gianvitorossi.com",
    "oscardelarenta.com", "carolinaherrera.com", "eliesaab.com",
    "marchesa.com", "moschino.com", "diesel.com", "dsquared2.com",
    "stone-island.com", "cp-company.com", "miu-miu.com", "miumiu.com",
    "marni.com", "jilsander.com", "therow.com", "proenzaschouler.com",
    "altuzarra.com", "thakoon.com", "dereklamnyc.com",
    "torybirch.com", "marcjacobs.com", "kenzo.com", "lanvin.com",
    "rochas.com", "balmain.com", "amiri.com", "rhude.com",
    "offwhite.com", "palm-angels.com", "gcds.it", "msgm.it",
    "ambush-global.com", "sacai.jp", "comme-des-garcons.com",
    "yohji.com", "isseymiyake.com", "kansai.jp",
    "maison-margiela.com", "maisonmargiela.com", "sies-marjan.com",
    "tibi.com", "nanushka.com", "patrizia-pepe.com", "pinko.com",
    "marella.com", "emporio-armani.com", "armani.com",
    "boss.com", "hugoboss.com", "lacoste.com", "guess.com",
    "ralphlauren.com", "tommyhilfiger.com", "calvinklein.com",
    "stuartweitzman.com", "mulberry.com", "aspinaloflondon.com",
    "longchamp.com",

    # ── Scandinavian / Northern European ─────────────────────────────────────
    "acnestudios.com", "ganni.com", "toteme-studio.com",
    "filippa-k.com", "tiger-of-sweden.com", "stinegunhansen.com",
    "baum-und-pferdgarten.com", "rotate.com", "remain.com",
    "stand-studio.com", "holzweiler.com", "gestuz.com",
    "stinegoya.com", "lovechild1979.com", "samsoe.com",
    "marimekko.com", "arket.com", "cknk.se",

    # ── French / Southern European ────────────────────────────────────────────
    "sandro-paris.com", "claudiepierlot.com", "ba-sh.com",
    "rouje.com", "apc.fr", "isabelmarant.com", "jacquemus.com",
    "vanessabruno.com", "iro-paris.com", "maje.com",
    "zadig-et-voltaire.com", "sezane.com", "desigual.com",
    "pepe-jeans.com", "camper.com", "eseoese.com",
    "patrizia-pepe.com", "twinset.com", "iceberg.com",
    "pinko.com", "luisa-spagnoli.com", "elena-miro.com",

    # ── German / Central European ─────────────────────────────────────────────
    "aboutyou.com", "zalando.com", "zalando.de", "zalando.co.uk",
    "zalando.fr", "boozt.com", "marc-o-polo.com", "s-oliver.com",
    "esprit.com", "bogner.com", "gerry-weber.com", "riani.de",
    "comma-fashion.com", "luisa-cerano.com", "cinque.de",

    # ── Australian / NZ ───────────────────────────────────────────────────────
    "davidjones.com.au", "myer.com.au", "countryroad.com.au",
    "witchery.com.au", "seed.com.au", "the-iconic.com.au",
    "iconic.com.au", "dotti.com.au", "portmans.com.au",
    "saba.com.au", "gorman.com.au", "zimmermann.com",
    "aje.com.au", "scanlantheodore.com.au", "aliceintheevenings.com",
    "cue.com.au", "ojay.com.au", "birdsnest.com.au",
    "city-chic.com.au", "lorna-jane.com.au", "lornajane.com",

    # ── Asian fashion ─────────────────────────────────────────────────────────
    "yesstyle.com", "kooding.com", "stylenanda.com",
    "mixxmix.com", "w-concept.com", "wconcept.us",
    "chuu.com", "iampretty.co.kr",

    # ── Denim specialists ─────────────────────────────────────────────────────
    "levis.com", "wrangler.com", "lee.com", "pepe-jeans.com",

    # ── Shoes ─────────────────────────────────────────────────────────────────
    "stevemadden.com", "aldoshoes.com", "aldo.com", "clarks.com",
    "vans.com", "converse.com", "ugg.com", "sorel.com",
    "drschollsshoes.com", "fitflop.com", "havaianas.com",
    "birkenstock.com", "naturalizer.com", "skechers.com",
    "ecco.com", "geox.com", "asics.com", "hoka.com",
    "salomon.com", "merrell.com", "timberland.com", "drmartens.com",
    "nine-west.com", "ninewest.com", "charlotteolympia.com",
    "on-running.com", "on.com", "brooks.com", "saucony.com",
    "newbalance.com", "columbia.com", "keenfootwear.com",
    "sanuk.com", "teva.com", "chaco.com", "dansko.com",
    "mephisto.com", "sebago.com", "sperry.com", "sperryshoes.com",
    "loake.co.uk", "grenson.com", "barker.co.uk", "trickers.com",
    "crockett-jones.com", "church-footwear.com",

    # ── Sportswear / activewear ───────────────────────────────────────────────
    "nike.com", "adidas.com", "puma.com", "underarmour.com",
    "lululemon.com", "gymshark.com", "skims.com", "spanx.com",
    "fabletics.com", "athleta.com", "sweatybetty.com",
    "vuori.com", "aloyoga.com", "alo.com", "outdoorvoices.com",
    "beyondyoga.com", "splits59.com", "varley.com",
    "pe-nation.com", "castore.com", "represent-clo.com",
    "pas-normal-studios.com", "rapha.cc", "asics.com",

    # ── Lingerie / swimwear ───────────────────────────────────────────────────
    "victoriassecret.com", "intimissimi.com", "calvinklein.com",
    "thirdlove.com", "wacoal.com", "freya.com", "panache.co.uk",
    "fantasie.com", "simone-perele.com", "hanky-panky.com",
    "aerie.com", "summersalt.com", "cupshe.com", "triangl.com",
    "mondayswimwear.com", "seafolly.com", "jets.com.au",
    "hunza-g.com", "melissa-odabash.com", "zimmermann.com",
    "agentprovocateur.com", "wolfandwhistle.com",

    # ── Plus size ─────────────────────────────────────────────────────────────
    "torrid.com", "lanebryant.com", "eloquii.com",
    "addition-elle.com", "navabi.com", "evans.co.uk",

    # ── Resale / rental ───────────────────────────────────────────────────────
    "therealreal.com", "vestiairecollective.com", "depop.com",
    "poshmark.com", "tradesy.com", "thredup.com", "rebag.com",
    "fashionphile.com", "renttherunway.com", "nuuly.com",

    # ── Accessories / jewellery ───────────────────────────────────────────────
    "pandora.net", "tiffany.com", "swarovski.com", "mejuri.com",
    "missoma.com", "astridandmiyu.com", "wolfandbadger.com",
    "catbird.com", "gorjana.com", "kendrascott.com",
    "baublebar.com", "charleskeith.com", "lovisa.com",
    "claires.com", "accessorize.com",

    # ── Bags / leather goods ──────────────────────────────────────────────────
    "mulberry.com", "aspinaloflondon.com", "radley.co.uk",
    "fiorelli.com", "kipling.com", "longchamp.com",
    "fjallraven.com", "herschel.com", "eastpak.com",
    "samsonite.com", "tumi.com",
}  # _OLD_RETAIL_ALLOWLIST_STUB — not used for filtering


def _host(link: str) -> str:
    try:
        h = urlparse(link).hostname or ""
        return h.removeprefix("www.")
    except Exception:
        return ""


def _is_store(link: str, price: str | None) -> bool:
    # Signal 1: SerpAPI returned a price → definitely a product page
    if price:
        return True

    h = _host(link)

    # Signal 2: Known non-retail domain → skip
    if any(h == d or h.endswith("." + d) for d in _NON_RETAIL_BLACKLIST):
        return False

    # Signal 3: URL path looks like editorial/content → skip
    path = urlparse(link).path
    if _EDITORIAL_PATH_RE.search(path):
        return False

    # Everything else is assumed to be a store
    return True


def _extract_price(item: dict) -> str | None:
    raw = item.get("price")
    if not raw:
        return None
    if isinstance(raw, dict):
        return raw.get("value")
    return str(raw)


def _parse(data: dict) -> list[dict]:
    results = []
    candidates = data.get("shopping_results") or data.get("visual_matches", [])

    for item in candidates:
        link = item.get("link", "")
        if not link:
            continue
        price = _extract_price(item)
        if not _is_store(link, price):
            continue
        results.append({
            "title": item.get("title", ""),
            "link": link,
            "source": item.get("source", ""),
            "thumbnail": item.get("thumbnail", ""),
            "price": price,
        })

    seen: set[str] = set()
    unique = []
    for r in sorted(results, key=lambda x: x["price"] is None):
        if r["link"] not in seen:
            seen.add(r["link"])
            unique.append(r)

    return unique[:12]


async def search(image_url: str) -> list[dict]:
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": settings.serpapi_key,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.get(_SERPAPI_URL, params=params)
            r.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Lens search failed ({exc.response.status_code}). Check your SERPAPI_KEY.",
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Lens request error: {exc}")

    return _parse(r.json())


async def raw(image_url: str) -> dict:
    """Return the unprocessed SerpAPI response — for debugging only."""
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": settings.serpapi_key,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(_SERPAPI_URL, params=params)
        r.raise_for_status()
    return r.json()
