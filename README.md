# joanmullinsart

The website of Joan Mullins, painter, Nantwich, Cheshire: joanmullinsart.co.uk (not live yet).

It is a plain static site: HTML pages, one stylesheet and the pictures in `img/`. There is no shop or checkout. Each painting that is for sale has an "Ask about this painting" button that opens an email to enquiries@joanmullinsart.co.uk, which forwards to Joan.

## How it is built

- `data/works.json` holds what the site shows about each painting: title, medium, size, year, place, status, price, description and picture description (alt text). The paintings are the ones ticked "On new website" in Joan's catalogue, plus every sold work except The Pink Cat.
- `tools/build.py` makes every page from that file. Run `python3 tools/build.py` from this folder, then commit.
- Pictures: `img/w/` (up to 1600 px, for a painting's own page) and `img/t/` (up to 720 px, for the galleries).

## Recording a sale

In `data/works.json`, set the painting's `"status"` to `"sold"` and its `"price"` to `null`, run the build, and commit. The painting then shows as Sold in its gallery and appears in the Sold section.

## Draft

While `DRAFT = True` in `tools/build.py`, every page asks search engines not to list it, and gaps still to fill show in [brackets]. Set it to `False` at launch.

## Refreshing from the catalogue

`tools/prepare.py` rebuilds `data/works.json` from a snapshot of the catalogue's records (see the notes at its top). It only remakes the pictures with `--images`; don't use that until the catalogue's copies match the pictures here (some were trimmed here first, on 10 Nov 2026).

## "On a wall"

Each painting with a known size can be seen at true scale on a wall, in one of three rooms chosen by its size as hung (with any mount and frame): above a writing desk (35 cm or under), beside a side table and chair (up to 45 cm), or above a cabinet (larger). The rooms are `img/room-desk.jpg`, `img/room-small.jpg` and `img/room.jpg`; their scale and hanging point are in `ROOMS` in `tools/build.py`. Works on paper are shown in a mount and thin charcoal frame (not included), the poems in a wood frame like Joan's own, and framed oils in an oak frame. Pictures hang by their middle, never lower than the room's minimum gap above the furniture.
