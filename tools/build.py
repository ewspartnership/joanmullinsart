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
BASE = 'https://joanmullinsart.co.uk/'
# Enquiry form. Leave FORM_ENDPOINT empty until a form service is set up (for example Web3Forms:
# FORM_ENDPOINT = 'https://api.web3forms.com/submit' and FORM_KEY = the access key it emails you).
# While it is empty, the form opens the visitor's email program with the message filled in,
# and shows the message and address to copy if nothing opens.
FORM_ENDPOINT = ''
FORM_KEY = ''

works = json.load(open(os.path.join(ROOT, 'data', 'works.json')))
by_id = {w['id']: w for w in works}
e = lambda s: html.escape(str(s), quote=True)

GALLERIES = [
    # slug, name, tile work id, line under the tile, intro, group order
    ('landscapes', 'Landscapes', '091', 'Throughout her career',
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

def price_html(w):
    """The price for display, with the draft gap shown where Joan hasn't priced an available painting."""
    t = e(price_line(w))
    if DRAFT and w['status'] == 'available' and not w['price']:
        t += ' ' + draft('[Joan to price]')
    return t

def medium_short(w):
    m = w['medium']
    return m[:1].upper() + m[1:] if m else ''

def page(title, body, current='', desc='', image='img/joan.jpg', ld=''):
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
<link rel="canonical" href="{BASE}%%PATH%%">
<meta property="og:site_name" content="Joan Mullins, painter">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc or 'Paintings and drawings by Joan Mullins, painter, Nantwich, Cheshire.')}">
<meta property="og:url" content="{BASE}%%PATH%%">
<meta property="og:image" content="{BASE}{image}">
<meta name="twitter:card" content="summary_large_image">
{ld}{robots}<link rel="preconnect" href="https://fonts.googleapis.com">
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
<script src="site.js"></script>
</body>
</html>
'''

def card(w, ratio=''):
    sub = price_line(w)  # the medium is on the painting's own page; draft gaps are left to the painting's page
    return (f'<a class="card" href="{row_href(w)}" style="--r:{w["img"][0]/w["img"][1]:.3f}">'
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


gslug = lambda g: re.sub('[^a-z]+', '-', g.lower()).strip('-')

def row_href(w):
    """The gallery (or group) page and the painting's row on it. Every link to a painting goes here."""
    if not w['on_site']:
        return f'sold.html#w-{w["id"]}'
    slug, name, *_rest, groups = GAL[w['gallery']]
    present = [g for g in groups if any(x['group'] == g for x in on_site(name))]
    if len(present) > 1 and w['group'] in present:
        return f'g-{slug}-{gslug(w["group"])}.html#w-{w["id"]}'
    return f'g-{slug}.html#w-{w["id"]}'

def sort_key(w):
    n = w['no'].lstrip('P')
    return (0 if w['no'].startswith('P') else 1, int(n) if n.isdigit() else 0)


# Three rooms, all made by Steph in ChatGPT (10 Nov), with the wood calmed and the wall made the same soft white.
# s = px per cm at the wall; cx = the picture's centre, by = its lowest edge, in px from the left and bottom.
ROOMS = {
    # A walnut cabinet about 90 cm wide; the picture hangs centred over it, 20 cm above its top.
    # Steph's second ChatGPT version (10 Nov): the same cabinet and place, one dried stem; wall evened to soft white and the walnut calmed.
    'cabinet': dict(src='img/room.jpg', thumb='img/room-thumb.jpg', rw=1039, rh=1513, s=7.6, cx=516, by=781,
                    where='Above a cabinet about 90 cm wide.'),
    # A side table about 65 cm across with a lamp, books and a mug, beside a chair; Steph's picture (recoloured by her, 10 Nov; wall then matched to soft white and the wood made a richer walnut),
    # cropped from 1024 x 1536 to x 120-1024, y 300-1420. The picture hangs between the lamp and the chair, 25 cm above the table top.
    # A walnut writing desk by a window with a small fern, for the tiniest paintings, hung low enough to look at sitting down.
    # Cropped from 1086 x 1448 to y 150-1215, with the A5 outline ChatGPT drew painted out, the wall matched and the wood calmed.
    # The outline (14.8 x 21 cm) gives about 13 px = 1 cm. The picture hangs centred on the wall between the window and the edge
    # of the picture (ChatGPT's outline sat too far left), 20 cm above the desk top.
    'desk': dict(src='img/room-desk.jpg', thumb='img/room-desk-thumb.jpg', rw=1086, rh=1065, s=13.0, cx=616, by=521,
                 where='Above a writing desk, hung to be seen sitting down.'),
    'table': dict(src='img/room-small.jpg', thumb='img/room-small-thumb.jpg', rw=904, rh=1120, s=7.6, cx=460, by=618,
                  where='Above a side table about 65 cm across.'),
}
TINY = 35    # cm: no bigger than this as hung goes above the desk
SMALL = 45   # cm: no bigger than this as hung (with any mount and frame) goes beside the side table and chair

def hung(w):
    """Style, frame, mount widths and the hung size in cm."""
    paper = 'paper' in w['medium'].lower()
    if paper:
        if w['gallery'] == 'Illustrated poems':
            # Measured from Joan's own framing of one of her poems (Steph's photo, 10 Nov): about 1.6 cm of the sheet shows
            # round the painting, then about 3.5 cm of mount and a 1.9 cm mid-brown wood frame. mx/mt/mb include the sheet.
            style, fw, mx, mt, mb = 'poem', 1.9, 5.1, 5.3, 5.3
        else:
            # Other works on paper: a typical wide mount and a thin charcoal frame (Steph's choice, 10 Nov).
            style, fw, mx, mt, mb = 'mounted', 1.2, 7, 7, 8
    elif w.get('framed'):
        style, fw, mx, mt, mb = 'oak', 3, 0, 0, 0
    else:
        style, fw, mx, mt, mb = 'bare', 0, 0, 0, 0
    pw, ph = shown_size(w)
    return style, fw, mx, mt, mb, pw + 2 * (fw + mx), ph + 2 * fw + mt + mb

def shown_size(w):
    """The painting's size on the wall in cm. The picture is never stretched: it keeps the photo's shape, with its longer side
    at the recorded longer side. (Where the photo and the recorded size disagree, as for Nos. 21 and 128, that's a question for Joan.)"""
    pw, ph = w['img']
    long = max(w['h'], w['w'])
    return (long, long * ph / pw) if pw >= ph else (long * pw / ph, long)

def room_for(w):
    if not (w['h'] and w['w']):
        return None
    tw, th = hung(w)[-2:]
    big = max(tw, th)
    return ROOMS['desk' if big <= TINY else 'table' if big <= SMALL else 'cabinet']

def wall_view(w):
    """The painting at true size on a wall, when its size is known: small ones beside a side table, the rest above a cabinet.
    Works on paper are shown mounted: poems in a frame like Joan's own, others in a typical mount and thin black frame (not included unless recorded as framed);
    oils recorded as framed are shown in a plain oak frame; other oils hang bare."""
    r = room_for(w)
    if not r:
        return '', ''
    paper = 'paper' in w['medium'].lower()
    style, fw, mx, mt, mb, tw, th = hung(w)
    if paper and not w.get('framed'):
        note = f'Shown in a typical mount and frame, which are not included. The painting itself is {size(w)}.'
    elif paper:
        note = f'Shown framed. The painting itself is {size(w)}.'
    elif w.get('framed'):
        note = f'Shown in its oak frame. The painting itself is {size(w)}.'
    else:
        note = f'Shown at its real size, {size(w)}.'
    return note + ' ' + r['where'] + ' The room is an illustration.', f'''<div class="wall" style="--rw:{r["rw"]};--rh:{r["rh"]};--s:{r["s"]};--cx:{r["cx"]};--by:{r["by"]}">
<img class="room" src="{r["src"]}" alt="" width="{r["rw"]}" height="{r["rh"]}" loading="lazy">
<div class="hang {style}" style="--tw:{tw:g};--th:{th:g};--fw:{fw:g};--mx:{mx:g};--mt:{mt:g};--mb:{mb:g}">
<img src="img/t/{w["id"]}.jpg" alt="{e(w["title"])} shown at its real size on a wall" loading="lazy"></div>
</div>'''

ZOOM = ('<dialog id="zoom" class="zoom" aria-label="Larger picture"><button type="button" class="zoom-close" aria-label="Close the larger picture">'
        '<span aria-hidden="true">×</span><span class="zoom-label">Close</span></button><img alt=""></dialog>')

def view_buttons(w):
    return (f'<div class="views" role="group" aria-label="Choose a view of {e(w["title"])}">'
            f'<button type="button" class="view-btn" data-view="painting" aria-pressed="true"><img src="img/t/{w["id"]}.jpg" alt="">The painting</button>'
            f'<button type="button" class="view-btn" data-view="wall" aria-pressed="false"><img src="{room_for(w)["thumb"]}" alt="">On a wall</button></div>')

def gallery_nav(current=''):
    """Links to the other galleries, for the foot of every gallery page, so nobody has to scroll back up."""
    items = [(f'g-{slug}.html', name) for slug, name, *_ in GALLERIES] + [('sold.html', 'Sold'), ('for-sale.html', 'Paintings for sale')]
    links = ''.join(f'<a href="{h}">{e(n)}</a>' for h, n in items if n != current)
    return f'<nav class="jump more-groups" aria-label="Other galleries"><span>Other galleries:</span>{links}</nav>'

pages = {}

# ---------- Home ----------
new = sorted([w for w in works if w['on_site'] and w['year'] == '2026'], key=sort_key)
hero = by_id.get('143') or (new[0] if new else None)
home = []
if hero:
    home.append(f'''<section class="wrap hero"><figure>
<a href="{row_href(hero)}"><img src="img/w/{hero["id"]}.jpg" alt="{e(hero["alt"])}" width="{hero["img"][0]}" height="{hero["img"][1]}"></a>
<figcaption><span>New painting · <a href="{row_href(hero)}"><em>{e(hero["title"])}</em></a>, {e(hero["medium"].lower())}, {e(hero["year"])}</span>
<a href="new.html">All new paintings</a></figcaption></figure></section>''')
home.append(f'''<section class="wrap intro">
<p class="lede">Paintings and drawings, {draft("[earliest surviving year]")} to now</p>
<p>Over more than sixty years, Joan Mullins has worked across a remarkable range of subjects and styles, from closely observed landscapes and botanical studies to intricate compositions drawn entirely from imagination. These galleries bring together the different strands of a lifetime’s painting.</p>
</section>
<section class="wrap block"><h2 class="eyebrow">The galleries</h2>{tiles()}<p class="after-tiles"><a href="for-sale.html">See all {len([w for w in works if w['on_site'] and w['status'] == 'available'])} paintings for sale</a></p></section>
<section class="band"><div class="wrap about-strip">
<img src="img/joan.jpg" alt="Joan Mullins smiling, in a coral cardigan and patterned scarf, with her paintings on the wall behind her">
<div class="copy"><h2>About Joan</h2>
<p>Born in Bulawayo, in what was then Rhodesia, Joan studied English literature and fine art at the University of Natal, graduating in 1963.</p>
<p>Most of the work shown here dates from after she settled in England in 1979. Much of what she made before then was sold, lost or left behind in moves between Rhodesia, South Africa and Ireland, though a few earlier pieces survive. {draft("[Joan to OK this line]")}</p>
<a href="about.html">Read her story</a></div></div></section>
<section class="wrap ask"><h2>Ask about a painting</h2>
<p>Prices are shown with each painting. To buy one or arrange to see it, get in touch with Joan.</p>
<p class="ask-links"><a class="button" href="enquire.html">Enquire</a> <a href="enquire.html#buying">How buying works</a></p></section>''')
pages['index.html'] = page('Joan Mullins, painter, Nantwich, Cheshire', '\n'.join(home), 'Home')

# ---------- Gallery index ----------
pages['gallery.html'] = page('Gallery · Joan Mullins', f'''<section class="wrap block">
<h1>Gallery</h1>
<p class="lead">{len([w for w in works if w["on_site"]])} paintings and drawings in seven galleries, with a section for work that has sold.</p>
{tiles()}<p class="after-tiles"><a href="for-sale.html">See all {len([w for w in works if w['on_site'] and w['status'] == 'available'])} paintings for sale</a></p></section>''', 'Gallery')

# ---------- Exhibition layout: one painting per row, its details beside it ----------
gslug = lambda g: re.sub('[^a-z]+', '-', g.lower()).strip('-')

def ask_link(w):
    return f'<a href="enquire.html#w-{w["id"]}">Ask about this painting</a>'

def details(w):
    rows = [('Medium', e(medium_short(w))), ('Size', e(size(w))), ('Year', e(w['year'])), ('Inspired by', e(w['place'])),
            ('Price', price_html(w)), ('Catalogue no.', e(w['no']))]
    return ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows if v)

def exhibit(w):
    dl = details(w)
    text = ''.join(f'<p>{e(p)}</p>' for p in w['text'].split('\n') if p.strip())
    share = (f'<button type="button" class="share-btn" data-url="{BASE}w-{w["id"]}.html" data-title="{e(w["title"])}, by Joan Mullins">'
             f'<svg aria-hidden="true" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
             f'<path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"/><path d="M12 3v12"/><path d="M7 8l5-5 5 5"/></svg><span>Share</span></button>')
    links = ([ask_link(w)] if w['status'] == 'available' else []) + [share]
    wall_note, wall = wall_view(w)
    panes = (f'<div class="pane" data-pane="painting"><a href="img/w/{w["id"]}.jpg" data-zoom title="See it larger">'
             f'<img src="img/w/{w["id"]}.jpg" alt="{e(w["alt"] or w["title"])}" loading="lazy" width="{w["img"][0]}" height="{w["img"][1]}"></a></div>')
    if wall:
        panes += f'<div class="pane" data-pane="wall">{wall}<p class="pane-note">{e(wall_note)}</p></div>' + view_buttons(w)
    return (f'<article class="ex" data-status="{w["status"]}" id="w-{w["id"]}"><div class="ex-pic viewer">{panes}</div>'
            f'<div class="ex-info"><h2>{e(w["title"])}</h2>'
            f'<dl>{dl}</dl>{text}<p class="ex-links">{" · ".join(links)}</p></div></article>')

def exhibition(ws, switch=True):
    n = sum(w['status'] == 'available' for w in ws)
    sw = (f'<p class="forsale-switch"><label><input type="checkbox" class="only-sale"> Show only paintings for sale ({n} of {len(ws)})</label></p>'
          if switch and 0 < n < len(ws) else '')
    return sw + '<div class="exhibition">' + ''.join(exhibit(w) for w in ws) + '</div>' + ZOOM

GROUP_TILES = {'Trees and woodland': '142', 'Sea and shore': '009',
               'Countryside': '179', 'Buildings and old places': '178'}   # chosen by Steph, 10 Nov

def group_tile_pick(ws):
    """A clear, roughly landscape-shaped picture for a group's tile, preferring one that's for sale."""
    chosen = [w for w in ws if w['id'] == GROUP_TILES.get(w['group'])]
    if chosen: return chosen[0]
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
{gallery_nav(name)}
</section>''', 'Gallery', f'{g}: {name.lower()} by Joan Mullins, painter, Nantwich, Cheshire.')
        body = head + '<div class="tiles">' + ''.join(out) + '</div>' + gallery_nav(name) + '</section>'
    else:
        body = head + exhibition(ws) + gallery_nav(name) + '</section>'
    pages[f'g-{slug}.html'] = page(f'{name} · Joan Mullins', body, 'Gallery',
                                   f'{name} by Joan Mullins, painter, Nantwich, Cheshire. {intro}')

# ---------- Sold and new ----------
sold = sorted([w for w in works if w['status'] == 'sold'], key=sort_key)
pages['sold.html'] = page('Sold · Joan Mullins', f'''<section class="wrap block">
<nav class="crumbs" aria-label="Breadcrumb"><a href="gallery.html">Gallery</a> › Sold</nav>
<h1>Sold</h1><p class="lead">Paintings that have found homes.</p>
{exhibition(sold, False)}{gallery_nav('Sold')}</section>''', 'Gallery')
pages['new.html'] = page('New paintings · Joan Mullins', f'''<section class="wrap block">
<nav class="crumbs" aria-label="Breadcrumb"><a href="gallery.html">Gallery</a> › New paintings</nav>
<h1>New paintings</h1><p class="lead">Finished in the last twelve months. {draft("[Draft: shows every painting dated 2026 until months are recorded]")}</p>
{exhibition(new)}{gallery_nav()}</section>''', 'Gallery')

# ---------- Paintings for sale ----------
fs = []
for slug, name, *_ in GALLERIES:
    ws = [w for w in gallery_works(name) if w['status'] == 'available']
    if ws:
        fs.append(f'<h2 class="group" id="{slug}">{e(name)} <span class="count">{len(ws)}</span></h2><div class="grid">' + ''.join(card(w) for w in ws) + '</div>')
pages['for-sale.html'] = page('Paintings for sale · Joan Mullins', f'''<section class="wrap block">
<nav class="crumbs" aria-label="Breadcrumb"><a href="gallery.html">Gallery</a> › Paintings for sale</nav>
<h1>Paintings for sale</h1><p class="lead">Every painting Joan has for sale, gallery by gallery. Select one to see its size, price and how it looks on a wall. <a href="enquire.html#buying">How buying works</a></p>
{"".join(fs)}{gallery_nav('Paintings for sale')}</section>''', 'Gallery', 'Original paintings for sale by Joan Mullins, painter, Nantwich, Cheshire.')

# ---------- Work pages ----------
def artwork_ld(w):
    d = {'@context': 'https://schema.org', '@type': 'VisualArtwork', 'name': w['title'],
         'creator': {'@type': 'Person', 'name': 'Joan Mullins', 'jobTitle': 'Painter', 'address': {'@type': 'PostalAddress', 'addressLocality': 'Nantwich', 'addressRegion': 'Cheshire', 'addressCountry': 'GB'}},
         'artMedium': w['medium'], 'image': BASE + f'img/w/{w["id"]}.jpg', 'url': BASE + f'w-{w["id"]}.html'}
    if w['h'] and w['w']:
        d['height'] = {'@type': 'Distance', 'name': f"{w['h']} cm"}; d['width'] = {'@type': 'Distance', 'name': f"{w['w']} cm"}
    if re.fullmatch(r'\d{4}', w['year'] or ''):
        d['dateCreated'] = w['year']
    if w['text']:
        d['description'] = w['text']
    if w['status'] == 'available' and w['price']:
        d['offers'] = {'@type': 'Offer', 'price': w['price'], 'priceCurrency': 'GBP', 'availability': 'https://schema.org/InStock',
                       'areaServed': 'GB', 'url': BASE + f'w-{w["id"]}.html'}
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'

for w in works:
    # A painting's own page is what a shared link or a search result points at. Link previews (WhatsApp,
    # Facebook) and search engines read its title, picture and details; a person opening it is passed
    # straight on to the painting's row in its gallery. Without JavaScript the page still shows the painting.
    target = row_href(w)
    text = ''.join(f'<p>{e(p)}</p>' for p in w['text'].split('\n') if p.strip())
    ask = f'<a class="button" href="enquire.html#w-{w["id"]}">Ask about this painting</a>' if w['status'] == 'available' else ''
    body = f'''<script>location.replace({json.dumps(target)});</script>
<article class="wrap work">
<figure><img src="img/w/{w["id"]}.jpg" alt="{e(w["alt"] or w["title"])}" width="{w["img"][0]}" height="{w["img"][1]}"></figure>
<div class="info"><h1>{e(w["title"])}</h1>
<dl>{details(w)}</dl>{text}{ask}
<p><a href="{target}">See it in the gallery</a></p></div>
</article>'''
    pages[f'w-{w["id"]}.html'] = page(f'{w["title"]} · Joan Mullins', body, 'Gallery',
                                      f'{w["title"]}, {w["medium"].lower()}, by Joan Mullins, painter, Nantwich, Cheshire.',
                                      image=f'img/w/{w["id"]}.jpg', ld=artwork_ld(w))

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
<h2>Where her work has been shown</h2>
<ul class="cv">
<li>Society of Women Artists, Westminster Hall, London {draft("[year or years]")}</li>
<li>Society for Art of Imagination, Mall Galleries, London {draft("[year or years]")}</li>
<li>Royal Horticultural Society {draft("[what and when: submissions, shows, any medals]")}</li>
<li>{draft("[Exhibitions in Cheshire and Hampshire, with years]")}</li>
<li>Wirral Open Studios, West Kirby, 2024 and 2025</li>
</ul>
<h2>Memberships and awards</h2>
<p>{draft("[Any societies Joan belongs or belonged to, and any awards or prizes]")}</p>
</div></section>''', 'About', 'About Joan Mullins, painter, born in Bulawayo, living and painting in Nantwich, Cheshire.')

# ---------- Enquire ----------
for_sale = [w for slug, name, *_ in GALLERIES for w in gallery_works(name) if w['status'] == 'available']
options = ''.join(f'<option value="w-{w["id"]}">{e(w["title"])} (No. {e(w["no"])}, {e(price_line(w))})</option>' for w in for_sale)
form_attrs = f'action="{e(FORM_ENDPOINT)}" method="post"' if FORM_ENDPOINT else 'action="#" method="post" data-mailto="' + EMAIL + '"'
key_field = f'<input type="hidden" name="access_key" value="{e(FORM_KEY)}"><input type="hidden" name="subject" value="Enquiry from joanmullinsart.co.uk">' if FORM_ENDPOINT and FORM_KEY else ''
form_gap = '' if FORM_ENDPOINT else f'<p class="small">{draft("[Draft: until a form service is set up, sending opens your email program with the message filled in]")}</p>'
pages['enquire.html'] = page('Enquire · Joan Mullins', f'''<section class="wrap enquire">
<h1>Ask about a painting</h1>
<p class="lead">To buy a painting, ask a question or arrange to see one, send Joan a message. She replies personally.</p>
<form class="enq" id="enq" {form_attrs}>
{key_field}
<label for="f-painting">Which painting?</label>
<select id="f-painting" name="painting"><option value="">A general question</option>{options}</select>
<label for="f-name">Your name</label>
<input id="f-name" name="name" autocomplete="name" required>
<label for="f-email">Your email address</label>
<input id="f-email" name="email" type="email" autocomplete="email" required>
<label for="f-message">Your message</label>
<textarea id="f-message" name="message" rows="6" required placeholder="For example: is it still available, could I come and see it, what would postage to my town cost?"></textarea>
<button class="button" type="submit">Send to Joan</button>
{form_gap}
<div class="enq-fallback" id="enq-fallback" hidden>
<p>If your email program didn’t open, copy this message and send it to <span class="addr">{EMAIL}</span>:</p>
<textarea id="enq-copy" rows="7" readonly></textarea>
<button type="button" class="button-quiet" id="enq-copy-btn">Copy the message</button>
</div>
</form>
<p class="small">Or email Joan directly: <span class="addr">{EMAIL}</span></p>

<h2 id="buying">How buying works</h2>
<ol class="steps">
<li><b>Ask.</b> Send a message about the painting you like. Joan will confirm it’s still available, and tell you the postage cost if you’d like it sent.</li>
<li><b>Agree.</b> Joan emails you the details: the price, postage or collection, and how to pay.</li>
<li><b>Pay.</b> By bank transfer, or in cash if you collect. Joan sends or hands over the painting once the payment has arrived. {draft('[Joan to confirm how she takes payment]')}</li>
<li><b>Receive it.</b> Collect it from Nantwich, or Joan posts it within the UK, well packed and by a tracked, insured service.</li>
<li><b>Change your mind?</b> If it was posted to you, you can return it within 14 days of it arriving for a full refund. Joan’s email confirming the sale explains how.</li>
</ol>
<p>Every painting is an original by Joan. Works on paper are sold unframed unless the painting’s page says otherwise. {draft("[Framing available on request? Joan to say]")}</p>
<h2>Cards and prints</h2>
<p>Cards and prints of Joan’s work are sold through her <a href="{ETSY}">Etsy shop</a>.</p>
<h2>Your details</h2>
<p>Your name and email are used only to reply to your enquiry and arrange any sale. They are not shared. This website uses no cookies or tracking.</p>
<p class="small">Joan Mullins, Nantwich, Cheshire.</p>
</section>''', 'Enquire', 'Ask Joan Mullins about buying a painting. Collection from Nantwich, Cheshire, or UK postage.')

pages['404.html'] = page('Page not found · Joan Mullins', '''<section class="wrap enquire"><h1>Page not found</h1>
<p>That page isn’t here. Try the <a href="gallery.html">gallery</a> or the <a href="index.html">home page</a>.</p></section>''')

for name, s in pages.items():
    path = '' if name == 'index.html' else name
    open(os.path.join(ROOT, name), 'w').write(s.replace('%%PATH%%', path))
urls = ''.join(f'<url><loc>{BASE}{"" if n == "index.html" else n}</loc></url>' for n in pages if n != '404.html')
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
print(len(pages), 'pages written')
