"""Make the website's public data file (and, with --images, its web-sized pictures) from a snapshot of Joan's catalogue.
Only fields that appear on the website go into data/works.json.

Inputs (in the chat's workspace, not in this repository):
  CAT  a folder of the catalogue's `works` records as JSON (ArtifactData list with out_dir), one file per work
  SRC  the catalogue's main pictures: photos/pXXXX.jpg files and asset-id .jpgs (Artifact read with paths / path)
Pictures: on 10 Nov 2026 the website copies of 15 works were trimmed or straightened here first (see the brief's
Next steps). Until the catalogue's own copies match, don't run --images, or those trims are lost; the pictures
in img/ are the ones to keep."""
import json, glob, os, sys
from PIL import Image, ImageOps

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = '/home/claude/cat2/works'
SRCDIR = '/home/claude/srcimg'
IMAGES = '--images' in sys.argv
W = {}
for f in glob.glob(CAT + '/*.json'):
    w = json.load(open(f)); W[w['n']] = w

def label(w):
    return w.get('label') or ('P%d' % (w['n'] - 1000) if w['n'] > 1000 else '%d' % w['n'])
def slug(w):
    return ('p%d' % (w['n'] - 1000)) if w['n'] > 1000 else '%03d' % w['n']
def src(art):
    return SRCDIR + '/' + art if art.startswith('photos/') else SRCDIR + '/a/' + art + '.jpg'
def num(x):
    if x in (None, ''): return None
    x = float(x); return int(x) if x == int(x) else x

STATUS = {'Available': 'available', 'NFS': 'nfs', 'Gifted': 'nfs', 'Sold': 'sold', '': 'available', None: 'available'}
sel = [w for w in W.values() if w.get('web_pick') == 'Y' or (w.get('status') == 'Sold' and w['n'] != 224)]
os.makedirs(REPO + '/img/w', exist_ok=True); os.makedirs(REPO + '/img/t', exist_ok=True); os.makedirs(REPO + '/data', exist_ok=True)
out = []
for w in sorted(sel, key=lambda w: w['n']):
    st = STATUS[w.get('status')]
    s = slug(w)
    if IMAGES or not os.path.exists(f'{REPO}/img/w/{s}.jpg'):
        im = ImageOps.exif_transpose(Image.open(src(w['art']))).convert('RGB')
        big = im.copy(); big.thumbnail((1600, 1600), Image.LANCZOS); big.save(f'{REPO}/img/w/{s}.jpg', quality=84, optimize=True, progressive=True)
        th = im.copy(); th.thumbnail((720, 720), Image.LANCZOS); th.save(f'{REPO}/img/t/{s}.jpg', quality=80, optimize=True, progressive=True)
    big = Image.open(f'{REPO}/img/w/{s}.jpg')
    out.append({
        'id': s, 'no': label(w), 'title': (w.get('title') or '').strip(),
        'gallery': w.get('category'), 'group': (w.get('subgroup') or '').strip(),
        'on_site': w.get('web_pick') == 'Y',
        'medium': (w.get('medium') or '').strip(), 'h': num(w.get('height_cm')), 'w': num(w.get('width_cm')),
        'year': str(w.get('year') or '').strip(), 'place': (w.get('place') or '').strip(),
        'status': st, 'price': num(w.get('price_gbp')) if st == 'available' else None,
        'text': (w.get('web_text') or '').strip(), 'alt': (w.get('alt_text') or '').strip(),
        'img': [big.width, big.height],
        'framed': w.get('framed') == 'Y',
    })
json.dump(out, open(REPO + '/data/works.json', 'w'), indent=1, ensure_ascii=False)
if IMAGES:
    p = ImageOps.exif_transpose(Image.open(SRCDIR + '/a/12c5eade9d3ea95991bcf3fce40191b8.jpg')).convert('RGB')   # Joan's portrait
    p.thumbnail((1000, 1000)); p.save(REPO + '/img/joan.jpg', quality=84, optimize=True, progressive=True)
print(len(out), 'works;', sum(o['on_site'] for o in out), 'on site')
