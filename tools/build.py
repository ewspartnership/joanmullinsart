"""Build Joan Mullins' website from data/works.json.

Run from the repository root:  python3 tools/build.py
Pages are written to the repository root. To record a sale, change that
painting's "status" to "sold" (and remove its "price") in data/works.json,
then run this again and commit.
"""
import json, html, os, re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = True  # while True: pages ask search engines not to list them, and draft gaps show in brackets
EMAIL = 'enquiries@joanmullinsart.co.uk'
ETSY = 'https://www.etsy.com/shop/ArtistjoanmullinsCo'
SITE = 'joanmullinsart.co.uk'

works = json.load(open(os.path.join(ROOT, 'data', 'works.json')))
by_id = {w['id']: w for w in works}
e = lambda s: html.escape(str(s), quote=True)

GALLERIES = [
    # slug, name, tile work id, line under the tile, intro, group order
    ('landscapes', 'Landscapes', '133', 'Throughout her career',
     'Trees and woodland, the sea and shore, and the countryside of Cheshire, the Wirral and Hampshire.',
     ['Trees and woodland', 'Sea and shore', 'Countryside', 'Buildings and old places']),
    ('figurative-work', 'Figurative work', '066', 'Throughout her career',
     'Portraits, figures and heads, in pencil, ink, pastel, watercolour and oil.', []),
    ('botanical-work', 'Botanical work', '039', 'About 1980 to 2000',
     'Flowers and plants painted from life, with close attention to their structure.', []),
    ('watercolours-of-the-imagination', 'Watercolours of the imagination', '076', 'About the 1990s to 2013',
     'Compositions drawn entirely from imagination: figures, shells, the sea and designs.',
     ['Imaginative figures', 'Shell studies', 'Sea fantasies', 'Designs']),
    ('still-life', 'Still life', '019', '[Dates, from Joan]',
     'Bowls, jugs, fruit and flowers, arranged and painted in the studio.', []),
    ('illustrated-poems', 'Illustrated poems', 'p9', '2018 to 2020',
     'Favourite poems, hand-lettered and illustrated in ink and watercolour.', []),
    ('sea-imaginings', 'Sea imaginings', '171', 'Since moving to Nantwich',
     'Shells and the sea, transformed in paint.', []),
]
GAL = {g[1]: g for g in GALLERIES}

def draft(s):
    """Show [bracketed] gaps in the draft colour."""
    return re.sub(r'\[([^\]]+)\]', r'<span class="gap">[\1]</span>', s)

def size(w):
    if w['h'] and w['w']:
        return f"{w['h']} × {w['w']} cm"
    return ''

def price_line(w):
    if w['status'] == 'sold': return 'Sold'
    if w['status'] == 'nfs': return 'Not for sale'
    return f"£{w['price']:,}" if w['price'] else 'Price on request'

def medium_short(w):
    m = w['medium']
    return m[:1].upper() + m[1:] if m else ''

def page(title, body, current='', desc=''):
    nav = [('index.html', 'Home'), ('gallery.html', 'Gallery'), ('about.html', 'About'), ('enquire.html', 'Enquire')]
    links = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if n == current else ""}>{n}</a>' for h, n in nav)
    robots = '<meta name="robots" content="noindex">\n' if DRAFT else ''
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or 'Paintings and drawings by Joan Mullins, painter, Nantwich, Cheshire.')}">
{robots}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600&amp;family=Spectral:ital,wght@0,400;0,500;1,400&amp;display=swap">
<link rel="stylesheet" href="style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="wrap site-head">
<a class="brand" href="index.html"><span class="name">Joan Mullins</span><span class="tag">Painter · Nantwich, Cheshire</span></a>
<nav aria-label="Main">{links}</nav>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot"><div class="wrap">
<span>Joan Mullins, painter, Nantwich, Cheshire</span>
<a href="mailto:{EMAIL}">{EMAIL}</a>
<a href="{ETSY}">Cards and prints on Etsy</a>
</div></footer>
</body>
</html>
'''

def card(w, ratio=''):
    sub = price_line(w)  # the medium is on the painting's own page
    return (f'<a class="card" href="w-{w["id"]}.html" style="--r:{w["img"][0]/w["img"][1]:.3f}">'
            f'<img src="img/t/{w["id"]}.jpg" alt="{e(w["alt"] or w["title"])}" loading="lazy" width="{w["img"][0]}" height="{w["img"][1]}">'
            f'<em class="t">{e(w["title"])}</em><span class="s">{e(sub)}</span></a>')

def tiles():
    out = []
    for slug, name, tid, line, *_ in GALLERIES:
        t = by_id[tid]
        out.append(f'<a class="tile" href="g-{slug}.html"><img src="img/t/{tid}.jpg" alt="{e(t["alt"])}" loading="lazy">'
                   f'<span class="tn">{e(name)}</span><span class="ts">{draft(e(line))}</span></a>')
    t = by_id['104']
    out.append(f'<a class="tile" href="sold.html"><img src="img/t/104.jpg" alt="{e(t["alt"] or "Oil painting of birch trees in autumn")}" loading="lazy">'
               f'<span class="tn">Sold</span><span class="ts">Paintings that have found homes</span></a>')
    return '<div class="tiles">' + ''.join(out) + '</div>'

def on_site(g):
    return [w for w in works if w['on_site'] and w['gallery'] == g]

def sort_key(w):
    n = w['no'].lstrip('P')
    return (0 if w['no'].startswith('P') else 1, int(n) if n.isdigit() else 0)


def wall_view(w):
    """The painting drawn to scale on a wall above a sideboard, when its size is known."""
    if not (w['h'] and w['w']):
        return ''
    return f'''<section class="wrap wall-block" aria-labelledby="wall-h">
<h2 id="wall-h">See it on a wall</h2>
<div class="wall" style="--h:{w["h"]};--w:{w["w"]}" role="img" aria-label="{e(w["title"])}, {e(size(w))}, drawn to scale on a wall above a sofa 200 cm wide">
<img class="hung" src="img/t/{w["id"]}.jpg" alt="">
<div class="sofa" aria-hidden="true"><span class="back"></span><span class="seat"></span><span class="arm l"></span><span class="arm r"></span><span class="leg l"></span><span class="leg r"></span></div>
<div class="skirting" aria-hidden="true"></div>
</div>
<p class="small">Drawn to scale: the painting is {e(size(w))}{" without its frame" if w.get("framed") == "Y" else ""}, above a three-seater sofa 200 cm wide.</p>
</section>'''

pages = {}

# ---------- Home ----------
new = sorted([w for w in works if w['on_site'] and w['year'] == '2026'], key=sort_key)
hero = by_id.get('143') or (new[0] if new else None)
home = []
if hero:
    home.append(f'''<section class="wrap hero"><figure>
<a href="w-{hero["id"]}.html"><img src="img/w/{hero["id"]}.jpg" alt="{e(hero["alt"])}" width="{hero["img"][0]}" height="{hero["img"][1]}"></a>
<figcaption><span>New painting · <a href="w-{hero["id"]}.html"><em>{e(hero["title"])}</em></a>, {e(hero["medium"].lower())}, {e(hero["year"])}</span>
<a href="new.html">All new paintings</a></figcaption></figure></section>''')
home.append(f'''<section class="wrap intro">
<p class="lede">Paintings and drawings, {draft("[earliest surviving year]")} to now</p>
<p>Over more than sixty years, Joan Mullins has worked across a remarkable range of subjects and styles, from closely observed landscapes and botanical studies to intricate compositions drawn entirely from imagination. These galleries bring together the different strands of a lifetime’s painting.</p>
</section>
<section class="wrap block"><h2 class="eyebrow">The galleries</h2>{tiles()}</section>
<section class="band"><div class="wrap about-strip">
<img src="img/joan.jpg" alt="Joan Mullins smiling, in a coral cardigan and patterned scarf, with her paintings on the wall behind her">
<div class="copy"><h2>About Joan</h2>
<p>Born in Bulawayo, in what was then Rhodesia, Joan studied English literature and fine art at the University of Natal, graduating in 1963.</p>
<p>Most of the work shown here dates from after she settled in England in 1979. Much of what she made before then was sold, lost or left behind in moves between Rhodesia, South Africa and Ireland, though a few earlier pieces survive. {draft("[Joan to OK this line]")}</p>
<a href="about.html">Read her story</a></div></div></section>
<section class="wrap ask"><h2>Ask about a painting</h2>
<p>Prices are shown with each painting. To buy one or arrange to see it, get in touch with Joan.</p>
<a class="button" href="enquire.html">Enquire</a></section>''')
pages['index.html'] = page('Joan Mullins, painter, Nantwich, Cheshire', '\n'.join(home), 'Home')

# ---------- Gallery index ----------
pages['gallery.html'] = page('Gallery · Joan Mullins', f'''<section class="wrap block">
<h1>Gallery</h1>
<p class="lead">{len([w for w in works if w["on_site"]])} paintings and drawings in seven galleries, with a section for work that has sold.</p>
{tiles()}</section>''', 'Gallery')

# ---------- Exhibition layout: one painting per row, its details beside it ----------
gslug = lambda g: re.sub('[^a-z]+', '-', g.lower()).strip('-')

def ask_link(w):
    subj = f"Enquiry: {w['title']} (No. {w['no']})"
    return f'<a href="mailto:{EMAIL}?subject={quote(subj)}">Ask about this painting</a>'

def exhibit(w):
    rows = [('Medium', medium_short(w)), ('Size', size(w)), ('Year', w['year']), ('Inspired by', w['place']), ('Price', price_line(w))]
    dl = ''.join(f'<dt>{k}</dt><dd>{e(v)}</dd>' for k, v in rows if v)
    text = ''.join(f'<p>{e(p)}</p>' for p in w['text'].split('\n') if p.strip())
    links = [f'<a href="w-{w["id"]}.html">See it larger</a>'] + ([ask_link(w)] if w['status'] == 'available' else [])
    return (f'<article class="ex"><a class="ex-pic" href="w-{w["id"]}.html">'
            f'<img src="img/w/{w["id"]}.jpg" alt="{e(w["alt"] or w["title"])}" loading="lazy" width="{w["img"][0]}" height="{w["img"][1]}"></a>'
            f'<div class="ex-info"><div><h2><a href="w-{w["id"]}.html">{e(w["title"])}</a></h2><span class="no">No. {e(w["no"])}</span></div>'
            f'<dl>{dl}</dl>{text}<p class="ex-links">{" · ".join(links)}</p></div></article>')

def exhibition(ws):
    return '<div class="exhibition">' + ''.join(exhibit(w) for w in ws) + '</div>'

def group_tile_pick(ws):
    """A clear, roughly landscape-shaped picture for a group's tile, preferring one that's for sale."""
    good = [w for w in ws if 0.9 <= w['img'][0] / w['img'][1] <= 1.6]
    for pool in ([w for w in good if w['status'] == 'available'], good, ws):
        if pool: return pool[0]

def gallery_works(name):
    ws = sorted(on_site(name), key=sort_key)
    if name == 'Sea imaginings':
        ws.sort(key=lambda w: 0 if 'shell' in w['title'].lower() else 1)
    return ws

GROUP_PAGE = {}   # (gallery, group) -> page name
for slug, name, tid, line, intro, groups in GALLERIES:
    ws = gallery_works(name)
    present = [g for g in groups if any(w['group'] == g for w in ws)]
    head = (f'<section class="wrap block"><nav class="crumbs" aria-label="Breadcrumb"><a href="gallery.html">Gallery</a> › {e(name)}</nav>'
            f'<h1>{e(name)}</h1><p class="lead">{e(intro)} <span class="dates">{draft(e(line))}</span></p>')
    if len(present) > 1:
        # Big gallery: its groups as tiles, each group on its own page
        out = []
        for g in present:
            gw = [w for w in ws if w['group'] == g]
            pg = f'g-{slug}-{gslug(g)}.html'; GROUP_PAGE[(name, g)] = pg
            t = group_tile_pick(gw)
            n = len(gw)
            out.append(f'<a class="tile" href="{pg}"><img src="img/t/{t["id"]}.jpg" alt="{e(t["alt"])}" loading="lazy">'
                       f'<span class="tn">{e(g)}</span><span class="ts">{n} painting{"s" if n != 1 else ""}</span></a>')
            others = ''.join(f'<a href="g-{slug}-{gslug(o)}.html">{e(o)}</a>' for o in present if o != g)
            pages[pg] = page(f'{g} · {name} · Joan Mullins', f'''<section class="wrap block">
<nav class="crumbs" aria-label="Breadcrumb"><a href="gallery.html">Gallery</a> › <a href="g-{slug}.html">{e(name)}</a> › {e(g)}</nav>
<h1>{e(g)}</h1><p class="lead">{e(name)} · {n} painting{"s" if n != 1 else ""}</p>
{exhibition(gw)}
<nav class="jump more-groups" aria-label="Other groups in {e(name)}"><span>More {e(name.lower())}:</span>{others}</nav>
</section>''', 'Gallery', f'{g}: {name.lower()} by Joan Mullins, painter, Nantwich, Cheshire.')
        body = head + '<div class="tiles">' + ''.join(out) + '</div></section>'
    else:
        body = head + exhibition(ws) + '</section>'
    pages[f'g-{slug}.html'] = page(f'{name} · Joan Mullins', body, 'Gallery',
                                   f'{name} by Joan Mullins, painter, Nantwich, Cheshire. {intro}')

# ---------- Sold and new ----------
sold = sorted([w for w in works if w['status'] == 'sold'], key=sort_key)
pages['sold.html'] = page('Sold · Joan Mullins', f'''<section class="wrap block">
<nav class="crumbs" aria-label="Breadcrumb"><a href="gallery.html">Gallery</a> › Sold</nav>
<h1>Sold</h1><p class="lead">Paintings that have found homes.</p>
{exhibition(sold)}</section>''', 'Gallery')
pages['new.html'] = page('New paintings · Joan Mullins', f'''<section class="wrap block">
<nav class="crumbs" aria-label="Breadcrumb"><a href="gallery.html">Gallery</a> › New paintings</nav>
<h1>New paintings</h1><p class="lead">Finished in the last twelve months. {draft("[Draft: shows every painting dated 2026 until months are recorded]")}</p>
{exhibition(new)}</section>''', 'Gallery')

# ---------- Work pages ----------
for w in works:
    g = GAL.get(w['gallery'])
    gname = 'Sold' if (not w['on_site'] and w['status'] == 'sold') else w['gallery']
    ghref = 'sold.html' if gname == 'Sold' else f'g-{g[0]}.html'
    grp_page = GROUP_PAGE.get((w['gallery'], w['group'])) if gname != 'Sold' else None
    rows = [('Medium', medium_short(w)), ('Size', size(w)), ('Year', w['year']), ('Inspired by', w['place']), ('Price', price_line(w))]
    dl = ''.join(f'<dt>{k}</dt><dd>{e(v)}</dd>' for k, v in rows if v)
    text = ''.join(f'<p>{e(p)}</p>' for p in w['text'].split('\n') if p.strip()) if w['text'] else (
        f'<p>{draft("[A few lines from Joan about this painting]")}</p>' if w['on_site'] else '')
    if w['status'] == 'available':
        subj = f"Enquiry: {w['title']} (No. {w['no']})"
        ask = (f'<a class="button" href="mailto:{EMAIL}?subject={quote(subj)}">Ask about this painting</a>'
               f'<p class="small">Or email <span class="addr">{EMAIL}</span>, quoting No. {e(w["no"])}. UK only. '
               f'Collection from Nantwich is free; UK postage is quoted when you enquire.</p>')
    else:
        ask = ''
    pool = sold if gname == 'Sold' else [x for x in gallery_works(w['gallery']) if not grp_page or x['group'] == w['group']]
    others = [x for x in pool if x['id'] != w['id']]
    i = next((k for k, x in enumerate(pool) if x['id'] == w['id']), 0)
    more = (others[i:] + others[:i])[:3]
    body = f'''<nav class="wrap crumbs" aria-label="Breadcrumb"><a href="gallery.html">Gallery</a> › <a href="{ghref}">{e(gname)}</a> › {f'<a href="{grp_page}">{e(w["group"])}</a> › ' if grp_page else ''}{e(w["title"])}</nav>
<article class="wrap work">
<figure style="--r:{w["img"][0]/w["img"][1]:.3f}"><a href="img/w/{w["id"]}.jpg"><img src="img/w/{w["id"]}.jpg" alt="{e(w["alt"] or w["title"])}" width="{w["img"][0]}" height="{w["img"][1]}"></a>
<figcaption>Select the picture to see it larger</figcaption></figure>
<div class="info"><div><h1>{e(w["title"])}</h1><span class="no">No. {e(w["no"])}</span></div>
<dl>{dl}</dl>{text}{ask}</div>
</article>
{wall_view(w)}
<section class="band"><div class="wrap block"><h2>More from {e(w["group"] if grp_page else gname)}</h2>
<div class="grid three">{"".join(card(x) for x in more)}</div></div></section>'''
    pages[f'w-{w["id"]}.html'] = page(f'{w["title"]} · Joan Mullins', body, 'Gallery',
                                      f'{w["title"]}, {w["medium"].lower()}, by Joan Mullins, painter, Nantwich, Cheshire.')

# ---------- About ----------
pages['about.html'] = page('About Joan Mullins', f'''<section class="wrap about">
<img src="img/joan.jpg" alt="Joan Mullins smiling, in a coral cardigan and patterned scarf, with her paintings on the wall behind her">
<div class="copy"><h1>About Joan</h1>
<p>{draft("[A few lines in Joan’s own words, from her old welcome text, brought up to date]")}</p>
<p>Joan Mullins was born in Bulawayo, in what was then Rhodesia. She studied English literature and fine art at the University of Natal, graduating in 1963.</p>
<p>She settled in England in 1979, and has lived in Nantwich, Cheshire, since 2013. Most of the work on this site dates from after 1979. Much of what she made before then was sold, lost or left behind in moves between Rhodesia, South Africa and Ireland, though a few earlier pieces survive. {draft("[Joan to OK this]")}</p>
<p>Her botanical paintings were made with close attention to botanical detail; she submitted work to the Royal Horticultural Society and showed with the Society of Women Artists at Westminster Hall {draft("[years; member or exhibitor]")}.</p>
<p>Her imaginative work was shown with the Society for Art of Imagination at the Mall Galleries, London {draft("[years; member or exhibitor; any awards]")}.</p>
<p>She is still painting. <a href="new.html">See her newest work</a>, or <a href="gallery.html">browse the galleries</a>.</p>
</div></section>''', 'About', 'About Joan Mullins, painter, born in Bulawayo, living and painting in Nantwich, Cheshire.')

# ---------- Enquire ----------
pages['enquire.html'] = page('Enquire · Joan Mullins', f'''<section class="wrap enquire">
<h1>Ask about a painting</h1>
<p class="lead">To buy a painting, ask a question or arrange to see a painting, email Joan. Please give the painting’s name or number.</p>
<p class="addrline"><span class="addr">{EMAIL}</span></p>
<a class="button" href="mailto:{EMAIL}?subject=Enquiry">Email Joan</a>
<h2>Buying a painting</h2>
<ul>
<li>Prices are shown with each painting that is for sale.</li>
<li>Collection from Nantwich is free. UK postage is extra, and Joan will tell you the cost when you enquire.</li>
<li>Joan sells to buyers in the UK only.</li>
</ul>
<h2>Cards and prints</h2>
<p>Cards and prints of Joan’s work are sold through her <a href="{ETSY}">Etsy shop</a>.</p>
<h2>Your details</h2>
<p>Your email is used only to reply to your enquiry and arrange any sale. It is not shared. This website uses no cookies or tracking.</p>
<p class="small">Joan Mullins, Nantwich, Cheshire.</p>
</section>''', 'Enquire', 'Ask Joan Mullins about buying a painting. Collection from Nantwich, Cheshire, or UK postage.')

pages['404.html'] = page('Page not found · Joan Mullins', '''<section class="wrap enquire"><h1>Page not found</h1>
<p>That page isn’t here. Try the <a href="gallery.html">gallery</a> or the <a href="index.html">home page</a>.</p></section>''')

for name, s in pages.items():
    open(os.path.join(ROOT, name), 'w').write(s)
print(len(pages), 'pages written')
