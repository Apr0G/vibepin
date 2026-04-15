"""
Archetype text descriptions by image category.

Structure:
  ARCHETYPE_TEXTS[archetype][category] = [phrase1, phrase2, ...]
  - "fashion"  → person wearing an outfit
  - "interior" → room / home decor photo
  - "aesthetic"→ mood board / beauty / flat lay / nature texture

Each list is averaged into one text embedding (ensemble).
Missing categories fall back to "fashion" descriptions.
"""

ARCHETYPE_TEXTS: dict[str, dict[str, list[str]]] = {

    "quiet luxury": {
        "fashion": [
            "photo of a woman in Loro Piana camel cashmere overcoat, The Row cream silk blouse, tailored wide-leg trousers, zero logos, single thin gold bracelet — expensive and invisible",
            "old money quiet luxury: Hermès scarf tied loosely, cream coat, tonal beige outfit, no streetwear, no branding, just expensive fabric and perfect cut",
        ],
        "interior": [
            "quiet luxury apartment: Calacatta marble island, cream bouclé sofa, single white orchid, no clutter, warm oak floor, indirect lighting — expensive nothingness",
        ],
        "aesthetic": [
            "quiet luxury flat lay: thick cashmere swatch, single pearl, cream linen, Diptyque candle, muted neutral palette — wealth without display",
        ],
    },

    "clean girl": {
        "fashion": [
            "photo of a woman with slicked-back low bun secured with a claw clip, large gold hoop earrings, fitted white ribbed tank top tucked into straight jeans, luminous glass skin",
            "clean girl daily look: gold chain, clear gloss lip, dewy foundation, gold hoops, white tee and jeans — effortless groomed minimal NOT high fashion",
        ],
        "interior": [
            "clean girl vanity: neatly arranged skincare serums and tools on marble tray, gold-rimmed mirror, white fresh flowers, organized and fresh NOT cluttered",
        ],
        "aesthetic": [
            "clean girl flat lay: The Ordinary serum, gold hoop on white surface, glass water bottle, matcha latte, lip gloss — daily beauty routine aesthetic",
        ],
    },

    "dark academia": {
        "fashion": [
            "photo of a woman in brown tweed blazer, plaid wool midi skirt, black opaque tights, leather oxford brogues, burgundy knit vest — scholarly NOT gothic, warm earthy tones",
            "dark academia: vintage wool overcoat with literary herringbone pattern, turtleneck, plaid trousers, loafers, leather satchel — university library aesthetic, no black leather",
        ],
        "interior": [
            "dark academia study: floor-to-ceiling wooden bookshelves packed with hardbacks, brass banker lamp, tufted leather chesterfield, antique globe, stacked books on desk",
        ],
        "aesthetic": [
            "dark academia flat lay: worn leather-bound book, fountain pen, black espresso, dried autumn leaf, antique map — sepia warm brown tones, scholarly NOT occult",
        ],
    },

    "light academia": {
        "fashion": [
            "photo of a woman in soft scholarly outfit: cream linen blouse, white pleated midi skirt, beige cardigan, tan ballet flats, delicate pearl earrings",
            "light academia fashion: pastel button-down shirt, wide-leg cream trousers, loafers, soft intellectual collegiate romantic look",
        ],
        "interior": [
            "light academia room: white plaster walls, dried flowers in a vase, vintage hardback books, sheer linen curtains, natural window light, antique writing desk",
        ],
        "aesthetic": [
            "light academia mood board: pressed wildflowers, cream stationery, soft watercolor painting, sunlit library, botanical illustration, vintage journal",
        ],
    },

    "cottagecore": {
        "fashion": [
            "photo of a woman in floral prairie dress with puff sleeves, white embroidered lace apron, woven straw basket, fresh wildflowers in hand",
            "cottagecore fashion: white smocked linen dress, gingham blouse, mushroom embroidery, peasant top, countryside pastoral garden look",
        ],
        "interior": [
            "cottagecore kitchen: dried herb bundles hanging from ceiling, vintage floral china, scrubbed wooden farmhouse table, wildflowers in mason jar, lace curtains",
        ],
        "aesthetic": [
            "cottagecore mood board: wild mushrooms, honey jar, morning dew on grass, fresh bread loaf, pressed flower book, garden harvest basket",
        ],
    },

    "fairycore": {
        "fashion": [
            "photo of a woman in sheer iridescent butterfly wings, sparkly pastel tulle dress, fresh flower crown, glitter dusted on cheekbones, gossamer chiffon",
            "fairycore outfit: ethereal layered chiffon dress, fairy wings, crystal mushroom jewelry, soft pastel colors, magical whimsical forest fairy",
        ],
        "interior": [
            "fairycore bedroom: warm fairy lights draped across ceiling, mushroom-shaped lamp, pressed flowers in frames, sheer canopy curtains, twinkling magical cozy",
        ],
        "aesthetic": [
            "fairycore mood board: glowing fairy lights, dewdrop on mushroom cap, pastel wildflowers, butterfly wings, sparkling forest clearing, ethereal soft light",
        ],
    },

    "Y2K": {
        "fashion": [
            "photo of a woman in 2000s outfit: low-rise metallic mini skirt, rhinestone crop top, butterfly hairclips, chunky platform boots, velvet Juicy Couture tracksuit",
            "Y2K fashion: frosted lilac eyeshadow, Von Dutch trucker hat, low rise flared jeans, visible thong waistband, glossy lip, early 2000s retro",
        ],
        "interior": [
            "Y2K bedroom aesthetic: inflatable transparent furniture, lava lamp, iridescent holographic curtains, chrome butterfly accessories, colorful LED strip lights",
        ],
        "aesthetic": [
            "Y2K mood board: frosted lip gloss, flip phone, butterfly clips, low-res grainy digital camera photo, metallic colors, early internet pop aesthetic",
        ],
    },

    "e-girl": {
        "fashion": [
            "photo of a woman in striped long sleeve layered under dark slip dress, heavy winged black eyeliner, split-dye colored hair, chunky silver chain necklace, platform boots, small heart drawn under eye",
            "e-girl outfit: Killstar alt clothing, thigh-high socks, gamer girl aesthetic, anime patch on jacket, pastel hair dye, TikTok alternative style",
        ],
        "aesthetic": [
            "e-girl mood board: ahegao hoodie, heart face sticker, glitchy edit, dark pastel, anime waifu, TikTok alt subculture aesthetic",
        ],
    },

    "grunge": {
        "fashion": [
            "photo of a woman in ripped black fishnet tights, oversized vintage Nirvana band tee, distressed denim jacket covered in pins, Dr Martens combat boots, flannel shirt tied at waist",
            "grunge fashion: 90s Seattle aesthetic, thrift store leather jacket, hole-ripped jeans, smudged dark kohl eyeliner, messy undone hair",
        ],
        "aesthetic": [
            "grunge mood board: Nirvana cassette tape, guitar pick, worn combat boot, dark flannel, disposable film camera photo, 90s alternative",
        ],
    },

    "punk": {
        "fashion": [
            "photo of a woman in black leather biker jacket covered in silver pyramid studs, tartan plaid kilt, safety pin detailing, mohawk or liberty spikes, fishnet arm warmers",
            "punk fashion: DIY battle jacket with patches, combat boots, anarchist aesthetic, spiked collar, rebellious anti-fashion street",
        ],
        "aesthetic": [
            "punk mood board: studded leather jacket, safety pins, band patches, ripped fishnet, spray-painted wall, concert ticket stub, anarchist symbol",
        ],
    },

    "goth": {
        "fashion": [
            "photo of a woman in all-black Victorian goth: black velvet corset top, full lace-trimmed skirt, platform Mary Janes, wide black choker, dark plum or black lipstick — no colour whatsoever",
            "goth fashion: silver skull and pentagram jewelry, extremely pale face powder, dramatic black eyeshadow, black lace parasol, bat wing sleeves — death and Victorian decay aesthetic",
        ],
        "interior": [
            "goth bedroom: matte black walls, tall black wax candelabra, skull collection, dark velvet floor-length curtains, gothic arch mirror, black roses — NO warm tones",
        ],
        "aesthetic": [
            "goth mood board: black roses wilting, white wax dripping down black candle, iron cemetery gate, Victorian mourning portrait, crescent moon — dark, death, decay",
        ],
    },

    "streetwear": {
        "fashion": [
            "photo of a woman in hype streetwear: oversized graphic print hoodie, wide-leg cargo pants, chunky Nike or New Balance sneakers, mini crossbody bag, dad cap",
            "streetwear outfit: Jordan 1 sneakers, Supreme or Off-White graphic tee, baggy sweatpants, bomber jacket, skate park urban fashion",
        ],
        "aesthetic": [
            "streetwear mood board: sneaker box, Supreme sticker, concrete skate park, graffiti mural wall, hype drop queue, street photography",
        ],
    },

    "techwear": {
        "fashion": [
            "photo of a woman in all-black tactical outfit: waterproof nylon zip jacket with multiple cargo pockets, utility harness straps, tapered joggers, futuristic boots",
            "techwear: ACRONYM or Y-3 modular jacket, urban ninja all-black, technical ripstop fabric, cyberpunk dark futuristic functional fashion",
        ],
        "aesthetic": [
            "techwear mood board: rain-slicked black nylon jacket, neon city reflection puddle, cyberpunk Tokyo alley, functional dark fashion",
        ],
    },

    "gorpcore": {
        "fashion": [
            "photo of a woman in outdoor technical wear: Patagonia fleece vest over long sleeve, Salomon trail runners, technical trail pants, Arc'teryx shell jacket, Nalgene bottle",
            "gorpcore fashion: outdoor gear worn fashionably, North Face puffer, hiking boot, functional wilderness-ready chic streetwear",
        ],
        "aesthetic": [
            "gorpcore mood board: topographic trail map, compass, Nalgene water bottle, fleece blanket, mountain peak sunrise, outdoor gear flat lay",
        ],
    },

    "athleisure": {
        "fashion": [
            "photo of a woman in luxury matching activewear set: ribbed high-waist leggings and sports bra, Lululemon or Alo Yoga, white leather sneakers, dewy no-makeup look",
            "athleisure outfit: premium gym wear, sculpted fit, Vuori or Gymshark set, pilates reformer studio aesthetic, luxury fitness",
        ],
        "aesthetic": [
            "athleisure mood board: reformer pilates studio, green smoothie, Lululemon mat, clean wellness aesthetic, morning routine, luxury gym",
        ],
    },

    "bohemian": {
        "fashion": [
            "photo of a woman in flowing boho maxi dress with ethnic block print, crochet crop top, long fringe leather bag, layered turquoise beaded necklaces, wide-brim felt hat",
            "bohemian fashion: Free People Coachella festival outfit, suede fringe vest, embroidered peasant blouse, desert earthy patchwork",
        ],
        "interior": [
            "bohemian living room: large macramé wall hanging, Moroccan kilim rug layered on floor, rattan peacock chair, hanging pothos and trailing plants, stacked cushions",
        ],
        "aesthetic": [
            "boho mood board: crystal collection, palo santo smoke, wildflower bunch, tarot deck spread, dreamcatcher, golden sunset desert festival",
        ],
    },

    "maximalist": {
        "fashion": [
            "photo of a woman in bold maximalist outfit: leopard print blouse clashing with red floral skirt, stacked statement necklaces, feather-trimmed sleeve, jewel tones",
            "maximalist fashion: more is more philosophy, color blocking, mixed prints, embellished everything, head-to-toe eclecticism",
        ],
        "interior": [
            "maximalist interior: gallery wall of mismatched art frames, colorful velvet furniture, bold patterned wallpaper, layered rugs, plants and collected objects everywhere",
        ],
        "aesthetic": [
            "maximalist mood board: jewel tone swatches, leopard print, layered vintage jewelry, eclectic gallery wall, bold color collage",
        ],
    },

    "minimalist": {
        "fashion": [
            "photo of a woman in stark monochrome outfit: all-white or all-black, zero accessories, no pattern, no logo, pure geometric silhouette, empty negative space",
            "Scandi minimalist: Cos or Acne Studios single colour head to toe, structural oversize coat, plain turtleneck, nothing decorative — pure form over ornament",
        ],
        "interior": [
            "minimalist interior: completely bare white walls, single concrete or oak furniture piece, totally empty surfaces, no decor, no plants — negative space IS the design",
        ],
        "aesthetic": [
            "minimalist flat lay: single black line on white paper, one empty ceramic, brutal white space — zero ornament, zero clutter, conceptual and cold",
        ],
    },

    "coquette": {
        "fashion": [
            "photo of a woman in coquette fashion: enormous satin bow tied at waist of blush slip dress, pearl choker, lace trim hem, ribbon headband — hyper-feminine bows and lace, flirtatious NOT innocent",
            "coquette: rosette appliqué corset top, tiered lace hem, Lana Del Rey Lolita-adjacent, pearl and pink layering — specifically decorative bows and seduction, NOT ballet, NOT kawaii",
        ],
        "interior": [
            "coquette boudoir bedroom: satin bow pillow, dusty pink walls, pearl fairy lights, antique vanity mirror with dried rose bouquet, lace trim on everything — flirtatious feminine boudoir",
        ],
        "aesthetic": [
            "coquette flat lay: oversized satin bow, dried pink rose, pearl bracelet on lace fabric, vintage perfume atomiser, ribbon — decorative and flirtatious, NOT innocent soft girl",
        ],
    },

    "balletcore": {
        "fashion": [
            "photo of a woman in balletcore: pink cashmere ballet wrap cardigan tied over leotard bodysuit, pink leg warmers scrunched over tights, satin ribbon pointe-style shoes, slicked-back bun",
            "balletcore: specifically ballet studio clothing worn as street fashion — wrap cardigan, leotard, legwarmer, tutu skirt — NOT just pink or feminine, distinctly dance studio aesthetic",
        ],
        "interior": [
            "ballet studio room aesthetic: wooden barre bolted to wall, floor-to-ceiling mirror, marley floor, pink satin pointe shoes hanging by ribbon, dance studio NOT just pink bedroom",
        ],
        "aesthetic": [
            "balletcore flat lay: worn satin pointe shoe with fraying ribbon, rosin powder box, tutu layers, barre casting shadow — specifically ballet equipment NOT just soft pink",
        ],
    },

    "barbiecore": {
        "fashion": [
            "photo of a woman in all hot pink outfit: bright fuchsia mini bodycon dress, pink feather boa trim, pink cowboy hat, neon pink platform heels, Barbie-doll aesthetic",
            "barbiecore fashion: maximum pink everything, plastic fantastic glamour, monochrome hot pink, Barbie box packaging inspired, playful maximalist",
        ],
        "interior": [
            "Barbie dream house bedroom: all-pink room, pink velvet headboard, sequin throw pillows, disco ball, hot pink shag carpet, Barbie dreamhouse aesthetic",
        ],
        "aesthetic": [
            "barbiecore mood board: hot pink everything flat lay, Barbie doll box, pink convertible car, bubble letters, bold fuchsia, plastic glamour aesthetic",
        ],
    },

    "coastal grandmother": {
        "fashion": [
            "photo of a woman in relaxed coastal outfit: wide-leg natural linen trousers, navy and white Breton stripe linen top, raffia straw hat, woven rattan tote",
            "coastal grandmother style: Hamptons beach house fashion, easy linen separates, natural fiber textures, Diane Keaton effortless comfortable chic",
        ],
        "interior": [
            "coastal grandmother living room: white slipcovered sofa, navy stripe throw, rattan accent chairs, driftwood sculpture, sea glass jar, linen window panels",
        ],
        "aesthetic": [
            "coastal grandmother mood board: raw linen fabric, sea glass collection, navy stripe, wicker basket, morning coffee on a porch, breezy beach house calm",
        ],
    },

    "preppy": {
        "fashion": [
            "photo of a woman in classic preppy outfit: polo shirt tucked into plaid mini skirt, argyle sweater vest, tortoiseshell headband, pearl earrings, tan loafers",
            "preppy fashion: Ralph Lauren Ivy League collegiate, tennis pleated skirt, navy blazer with gold buttons, Nantucket heritage old money",
        ],
        "interior": [
            "preppy dorm room: navy and hunter green palette, plaid wool blanket, lacrosse stick leaning on wall, bookshelf with trophies, wooden desk, collegiate pennants",
        ],
        "aesthetic": [
            "preppy mood board: tennis racket on grass, argyle pattern swatch, pearl necklace on blue fabric, country club, Ivy League campus brick building",
        ],
    },

    "French girl": {
        "fashion": [
            "photo of a woman in effortless Parisian outfit: classic Breton marinière stripe top, high-waisted straight leg jeans, ballet flats, classic red lip, navy beret",
            "French girl style: belted trench coat, simple silk neck scarf, gold thin ring, effortless chic, nonchalant Parisian je ne sais quoi",
        ],
        "interior": [
            "French girl Paris apartment: herringbone parquet floor, linen curtains, a few framed art prints, simple bistro table, fresh baguette and flowers, elegant minimal",
        ],
        "aesthetic": [
            "French girl mood board: café crème on zinc bar, Eiffel Tower, open red wine, Le Monde newspaper, Breton stripe, cobblestone street, effortless Parisian",
        ],
    },

    "tomboy": {
        "fashion": [
            "photo of a woman in relaxed tomboy outfit: baggy vintage Levi jeans, oversized flannel button-down shirt, Nike Air Force 1, backwards baseball cap, no jewelry",
            "tomboy style: androgynous cool-girl, skater girl, gender-neutral relaxed oversized fit, sporty casual laid-back",
        ],
        "aesthetic": [
            "tomboy mood board: basketball court, vintage band tee, worn skate shoe sole, flannel shirt, skateboard deck, sporty gender-neutral vibe",
        ],
    },

    "western": {
        "fashion": [
            "photo of a woman in western cowgirl outfit: tall tooled leather cowboy boots, fringe suede jacket, denim cut-off shorts, turquoise statement jewelry, concho belt",
            "western fashion: cowgirl chic, embroidered yoke shirt, bolo tie, Southwestern desert rodeo, bandana, country music aesthetic",
        ],
        "interior": [
            "western interior: reclaimed wood walls, cowhide rug, wrought iron chandelier, turquoise pottery accent, woven Navajo blanket, ranch house",
        ],
        "aesthetic": [
            "western mood board: desert golden hour cactus, worn leather boot, turquoise ring, Southwestern geometric pattern, rodeo dust, country life aesthetic",
        ],
    },

    "mob wife": {
        "fashion": [
            "photo of a woman in mob wife aesthetic: oversized leopard print faux fur coat, statement chunky gold necklace, oversized dark sunglasses, skin-tight dress",
            "mob wife style: mink stole, gold chain layering, dramatic animal print, excess Italian American glamour, powerful bold woman",
        ],
        "aesthetic": [
            "mob wife mood board: leopard fur coat, stacked gold rings, manicured red nails, designer logo bag, dramatic sunglasses, excess luxury aesthetic",
        ],
    },

    "office siren": {
        "fashion": [
            "photo of a woman in seductive power office look: structured blazer worn with plunging neckline, high-slit pencil skirt, pointed stiletto heels, slicked back bun, dark lip",
            "office siren: femme fatale corporate fashion, power woman tailored suit, unbuttoned blazer, fitted pantsuit, dangerous and polished",
        ],
        "aesthetic": [
            "office siren mood board: tailored blazer, red lipstick, glass office tower, power dressing woman, femme fatale corporate aesthetic",
        ],
    },

    "indie": {
        "fashion": [
            "photo of a woman in indie alternative outfit: vintage thrifted floral midi dress, 70s-era high-waist flared jeans, worn band tee, round wire-frame sunglasses, canvas tote",
            "indie fashion: art student, thrift store personal style, retro 70s print, platform Dr Martens, record store crate-digger eclectic",
        ],
        "interior": [
            "indie aesthetic bedroom: dense gallery wall of concert posters and art prints, record player with vinyl stack, string lights, thrifted furniture, trailing plants",
        ],
        "aesthetic": [
            "indie mood board: vinyl record, 35mm film camera, concert ticket stub, sunflower field, Polaroid photo strip, indie art zine, vintage found objects",
        ],
    },

    "soft girl": {
        "fashion": [
            "photo of a woman in soft girl TikTok aesthetic: baby pink oversized crewneck, pleated pastel mini skirt, butterfly hair clip barrettes, strawberry print, ruffle ankle socks — innocent girlhood",
            "soft girl: blush and lavender palette, excessive hair clips and bows, cloud and star motifs — NOT coquette (no lace boudoir), NOT balletcore (no dance), specifically innocent TikTok cute",
        ],
        "interior": [
            "soft girl teen bedroom: pink cloud LED neon sign, stuffed animal collection piled on bed, pastel cloud wall paint, kawaii cushions, butterfly fairy lights — teen girl TikTok room",
        ],
        "aesthetic": [
            "soft girl mood board: strawberry milk carton, pastel cloud, bear sticker, cherry blossom, butterfly clip — innocent sweet pastel girl NOT mature boudoir feminine",
        ],
    },

    "surfer": {
        "fashion": [
            "photo of a woman in surfer beach look: triangle bikini top with denim cut-off shorts, sun-bleached wavy salt-sprayed hair, shell anklet, worn flip flops",
            "surfer girl style: California beach casual, rashguard, board shorts, golden tan, ocean wave background, surf culture laid-back",
        ],
        "aesthetic": [
            "surfer mood board: hollow ocean wave, surfboard wax comb, golden sunset beach, sun-bleached hair, shell friendship bracelet, California coast life",
        ],
    },

    "regencycore": {
        "fashion": [
            "photo of a woman in Bridgerton Regency-era inspired gown: empire waist puff sleeve white muslin dress, opera-length gloves, flower bonnet, pearl drop earrings",
            "regencycore fashion: historical romance period drama inspired, corset bodice, floral embroidery, satin ribbon sash, ruffled neckline",
        ],
        "interior": [
            "Regency interior: ornate gold leaf frame mirrors, floral chintz wallpaper, mahogany writing desk, candelabra, velvet fainting chaise lounge",
        ],
        "aesthetic": [
            "regencycore mood board: wax seal letter, quill and inkwell, rose bouquet, Bridgerton ball scene, pastel watercolor romance, period drama styling",
        ],
    },

    "mermaidcore": {
        "fashion": [
            "photo of a woman in mermaid-inspired outfit: iridescent scale-sequin midi skirt, shell bralette crop top, ocean blue-green ombre palette, layered pearl jewelry",
            "mermaidcore fashion: holographic fabric, siren sea goddess, ocean shimmer clothing, seashell hair accessories, mermaid tail silhouette",
        ],
        "interior": [
            "mermaid aesthetic bedroom: ocean-blue and seafoam green palette, shell and coral collection displayed, iridescent decor, sea glass, net draped from ceiling",
        ],
        "aesthetic": [
            "mermaidcore mood board: conch shell, sea glass pieces, iridescent fish scale texture, ocean wave, coral, holographic shimmer, deep sea siren",
        ],
    },

    "angelcore": {
        "fashion": [
            "photo of a woman in ethereal angel outfit: white sheer flowing chiffon dress, large feathered wings, glowing halo headband, all-cloud-white palette, luminous makeup",
            "angelcore fashion: celestial divine aesthetic, all-white sheer layers, feather trim details, heavenly soft backlight, halo accessories",
        ],
        "interior": [
            "angelcore room: all-white fluffy cloud bedding, white feather throw, cloud wallpaper, soft glowing light, white feather mobile hanging, celestial star projector",
        ],
        "aesthetic": [
            "angelcore mood board: white swan feather, glowing golden halo, soft light through clouds, heavenly choir rays, pure white ethereal divine aesthetic",
        ],
    },

    "dollcore": {
        "fashion": [
            "photo of a woman styled as porcelain doll: Victorian doll dress with lace Peter Pan collar and bloomers, perfect ringlet curls, large satin ribbon bow, rosy painted cheeks",
            "dollcore aesthetic: BJD ball-jointed doll inspired, antique china doll, miniature lace details, frilly vintage toy dress, collector aesthetic",
        ],
        "interior": [
            "dollcore room: antique porcelain dolls arranged on shelf, Victorian dollhouse display, lace valance curtains, miniature tea set, delicate collector's room",
        ],
        "aesthetic": [
            "dollcore mood board: cracked porcelain doll face, lace trim, ringlet hair, antique toy box, vintage doll packaging, miniature Victorian aesthetic",
        ],
    },

    "vintage glamour": {
        "fashion": [
            "photo of a woman in 1950s retro glamour: polka-dot wiggle dress with full skirt, victory roll updo, classic red lipstick, winged cat-eye glasses, white gloves",
            "vintage glamour fashion: 1950s rockabilly pin-up, petticoat swing dress, nipped waist, powder room retro femme",
        ],
        "interior": [
            "1950s retro interior: pastel pink kitchen with chrome appliances, checkerboard floor, vintage Americana signage, diner-style bar stools, atomic era decor",
        ],
        "aesthetic": [
            "vintage glamour mood board: red lipstick on compact mirror, vintage Chanel No 5 bottle, polka dot fabric, retro Hollywood movie poster, 1950s aesthetic",
        ],
    },

    "old Hollywood": {
        "fashion": [
            "photo of a woman in old Hollywood golden age glamour: floor-length ivory silk bias-cut gown, long opera gloves, three-strand pearls, mink fur stole, finger-wave set",
            "old Hollywood style: Marilyn Monroe or Audrey Hepburn inspired, silver screen starlet, 1940s evening elegance, dramatic glamour",
        ],
        "interior": [
            "old Hollywood interior: gilded ornate mirrors, deep burgundy velvet drapes, silver vanity table, black and white film stills framed, crystal chandelier",
        ],
        "aesthetic": [
            "old Hollywood mood board: black and white film still, classic cinema marquee, pearl gloves on velvet, dramatic spotlight, golden age glamour",
        ],
    },

    "kawaii": {
        "fashion": [
            "photo of a woman in Japanese kawaii Harajuku Decora fashion: pastel rainbow outfit, layered colorful bows, plush bear backpack, sweet Lolita bubble skirt, candy accessories",
            "kawaii fashion: Shibuya Takeshita Dori street style, colorful layered accessories, cute Japanese Fairy-Kei fashion, Sanrio inspired",
        ],
        "interior": [
            "kawaii bedroom: pastel pink Japanese room, Sanrio Hello Kitty plush collection on shelf, LED star lights, neon sign, cute figurines, Pokémon decor",
        ],
        "aesthetic": [
            "kawaii mood board: Hello Kitty character, strawberry milk carton, pastel macaron, Japanese candy packaging, cute sticker sheet, Sanrio aesthetic",
        ],
    },

    "art hoe": {
        "fashion": [
            "photo of a woman in art student outfit: vintage corduroy overalls over colorful striped turtleneck, sunflower enamel pin, round wire-frame glasses, canvas museum tote bag",
            "art hoe fashion: thrifted creative eclectic, gallery opening outfit, chunky loafers, artistic layering, museum-visit aesthetic",
        ],
        "interior": [
            "art hoe bedroom: dense gallery wall of art prints and painted canvases, record player, stacked art books, multiple trailing plants, eclectic creative studio",
        ],
        "aesthetic": [
            "art hoe mood board: sunflower, Van Gogh Starry Night print, 35mm film camera, art museum ticket stub, vintage paint palette smear, creative aesthetic",
        ],
    },

    "VSCO girl": {
        "fashion": [
            "photo of a woman in VSCO aesthetic: oversized vintage graphic tee, Birkenstock sandals, dainty shell necklace, messy bun secured with scrunchie, friendship bracelets stacked",
            "VSCO girl style: Hydro Flask water bottle, save the turtles, beachy casual California, hair naturally wavy, effortless no-effort look",
        ],
        "aesthetic": [
            "VSCO girl mood board: scrunchie stack, Hydro Flask, puka shell necklace, VSCO filter golden hour sunset, beachy effortless California vibe",
        ],
    },

    "coconut girl": {
        "fashion": [
            "photo of a woman in tropical island aesthetic: hibiscus flower print bikini with pareo sarong wrap, large straw sun hat, coconut shell jewelry, woven tote bag",
            "coconut girl fashion: Hawaii resort wear, tropical print sundress, seashell earrings, warm skin, island breezy aesthetic",
        ],
        "aesthetic": [
            "coconut girl mood board: tropical hibiscus flower, fresh coconut half, turquoise lagoon water, palm leaf shadow, island golden hour sunset aesthetic",
        ],
    },

    "witchcore": {
        "fashion": [
            "photo of a woman in witchy dark feminine outfit: black flowing velvet maxi skirt, large amethyst crystal pendant, moon phase charm necklace, wide-brim witch hat",
            "witchcore fashion: herbalist cottage witch, dark mystical, pagan goddess draping, occult silver rings on every finger, dark earthy robes",
        ],
        "interior": [
            "witchcore room interior: crystal altar with selenite and obsidian, dried herb and flower bundles, black pillar candles, moon phase wall hanging, tarot card spread",
        ],
        "aesthetic": [
            "witchcore mood board: tarot card spread, crystal ball, full moon over trees, dried lavender bundle, black wax candle drip, occult symbols, dark feminine",
        ],
    },

    "après ski": {
        "fashion": [
            "photo of a woman in cozy mountain lodge outfit: oversized Nordic Fair Isle knit sweater, fur-trim Moncler puffer jacket, UGG snow boots, plaid wool scarf",
            "après ski style: luxury ski resort fashion, snow bunny chalet look, cozy Aspen winter chic, apres-ski bar outfit",
        ],
        "interior": [
            "après ski chalet interior: crackling stone fireplace, plaid Pendleton wool blankets piled on leather sofa, antler chandelier, pine wood beams, hot cocoa mugs",
        ],
        "aesthetic": [
            "après ski mood board: fireplace glow close-up, wool blanket texture, snow falling on window, steaming hot chocolate, ski lift chair, mountain lodge cozy aesthetic",
        ],
    },

    "princesscore": {
        "fashion": [
            "photo of a woman in fantasy princess ballgown: enormous layered tulle skirt, crystal and rhinestone tiara, puff sleeves, pastel powder blue or pink satin",
            "princesscore fashion: Disney storybook princess inspired, sparkle satin ball gown, floor-length ruffles, royal enchanted castle ball aesthetic",
        ],
        "interior": [
            "princess bedroom: white canopy bed draped in pink tulle, crown wall decor above headboard, sparkle throw blanket, rose gold fairy lights, castle tower window",
        ],
        "aesthetic": [
            "princesscore mood board: crystal tiara on velvet, rose petal confetti, fairy tale castle at dusk, enchanted forest, glittering stardust, storybook princess",
        ],
    },

    "twee": {
        "fashion": [
            "photo of a woman in quirky vintage twee outfit: Peter Pan collar floral dress, patent leather Mary Jane shoes, pastel bow headband, colourful patterned tights",
            "twee fashion: Zooey Deschanel indie girl, vintage quirky playful feminine, ukulele aesthetic, retro cartoon print dress",
        ],
        "interior": [
            "twee bedroom: vintage floral wallpaper, trinket shelf with antique finds, teacup and saucer collection, colourful floral duvet, whimsical art prints",
        ],
        "aesthetic": [
            "twee mood board: ukulele, polka dot ribbon, vintage ceramic teacup, daisy chain, old typewriter, quirky cute retro indie aesthetic",
        ],
    },

    "flowercore": {
        "fashion": [
            "photo of a woman in flower-filled outfit: fresh daisy and rose flower crown woven into hair, ditsy wildflower print wrap dress, pressed flower resin earrings",
            "flowercore fashion: garden party spring bloom, botanical floral print, wildflower hairpin, feminine nature-inspired, flower girl aesthetic",
        ],
        "interior": [
            "flowercore room: overflowing fresh flower arrangements in every corner, botanical print wallpaper, dried flower wreath on door, pressed flower frames, garden bedroom",
        ],
        "aesthetic": [
            "flowercore mood board: wildflower bouquet, pressed flower journal page, flower crown on grass, blooming rose garden path, botanical pencil illustration",
        ],
    },

    "blokette": {
        "fashion": [
            "photo of a woman in blokette aesthetic: oversized football soccer jersey worn as a mini dress, pleated micro skirt underneath, knee-high white socks, chunky trainers",
            "blokette style: feminine sporty football fan fashion, girly kit styling, soccer jersey miniskirt trend, stadium outfit",
        ],
        "aesthetic": [
            "blokette mood board: football jersey flat lay, soccer ball, stadium crowd, sporty feminine aesthetic, football kit girl",
        ],
    },

    "90s supermodel": {
        "fashion": [
            "photo of a woman in 90s runway minimalism: delicate spaghetti strap silk slip dress, over-the-knee leather boots, sleek center-parted hair, barely-there makeup",
            "90s supermodel fashion: Kate Moss Calvin Klein slip dress, Naomi Campbell runway strut, 90s fashion week backstage, minimal raw luxury",
        ],
        "aesthetic": [
            "90s supermodel mood board: black and white editorial fashion photo, slip dress on model, 90s Vogue magazine page, minimalist runway aesthetic",
        ],
    },

    "party girl": {
        "fashion": [
            "photo of a woman in going-out party outfit: tiny sequin silver mini dress, strappy barely-there heels, metallic mini clutch, dramatic false lashes, glitter eyeshadow",
            "party girl fashion: night club glam, rhinestone cutout bodycon dress, going out look, sparkle shimmer short dress, heels and full glam",
        ],
        "aesthetic": [
            "party girl mood board: disco ball close-up, champagne bubbles, sequin fabric texture, pink neon club sign, glam night out aesthetic",
        ],
    },

    "glazed donut": {
        "fashion": [
            "photo of a woman with glazed donut skin: luminous pearl-toned glossy skin, nude sheer lip gloss, hydrated plump dewy foundation, chrome glazed nails",
            "glazed donut aesthetic: Hailey Bieber clean girl glow, glass skin, pearl shimmer highlight, natural dewy fresh no-makeup beauty",
        ],
        "aesthetic": [
            "glazed donut mood board: glossy wet skin close-up, clear lip gloss wand, pearl shimmer highlight swatch, chrome nails, dewy fresh beauty flat lay",
        ],
    },

    "academia fashion": {
        "fashion": [
            "photo of a woman in unisex smart casual scholarly look: oversized herringbone wool blazer, straight-cut trousers, chunky knit sweater vest, leather loafers, canvas messenger bag",
            "academia fashion: gender-neutral collegiate intellectual, smart layered knits, library chic, studious aesthetic, professor core",
        ],
        "interior": [
            "study room interior: well-organized wooden desk under a reading lamp, colour-coded textbook stack, open planner, mug of tea, productive academic room",
        ],
        "aesthetic": [
            "academia mood board: highlighted textbook margin, coffee shop study session, organised stationery flat lay, scholarly campus aesthetic",
        ],
    },

    "dreamcore": {
        "fashion": [
            "photo of a woman in dreamy surreal pastel look: soft-focus hazy image, vintage analog film grain effect, nostalgic pastel clothing, floating dreamy quality",
            "dreamcore fashion: liminal dreamlike styling, vaporwave pastel outfit, nostalgic childhood garments, surreal editorial",
        ],
        "interior": [
            "dreamcore aesthetic room: surreal floating objects, hazy pastel light, nostalgic childhood toys scattered, liminal empty hallway aesthetic, dreamy soft-focus decor",
        ],
        "aesthetic": [
            "dreamcore mood board: empty school hallway at dusk, hazy pastel filter, nostalgic analog TV static, childhood dream logic, surreal liminal space",
        ],
    },
}
