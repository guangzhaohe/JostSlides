#!/usr/bin/env python3
"""Build, present and extend local meeting decks. Nothing here publishes or uploads."""
import argparse
from datetime import date
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from slidekit.project import ROOT, DEFAULT_DECK, load_deck, validate
from slidekit.build import build, capture_widgets
from slidekit.server import PresentationHandler


def new_deck(name, title, *, root=ROOT):
    date_value = date.fromisoformat(name)
    if date_value.isoformat() != name:
        raise ValueError('Use YYYY-MM-DD')
    if not title.strip():
        raise ValueError('A meeting needs a title')
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') or 'meeting'
    meta = {'id': f'{slug}-{name}', 'title': title, 'date': name,
            'date_label': date_value.strftime('%B ') + str(date_value.day) + date_value.strftime(', %Y'),
            'export_stem': f'{slug}-{name}', 'theme': 'black', 'font': 'Jost'}
    directory = root / 'decks' / name
    if directory.exists():
        raise ValueError(f'Deck already exists; edit {directory / "deck.py"}')
    directory.mkdir(parents=True)
    (directory / 'deck.py').write_text((ROOT / 'templates/deck.py.tmpl').read_text().replace('__META__', repr(meta)))
    return directory / 'deck.py'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ['build', 'serve', 'check', 'export']:
        sub = commands.add_parser(command)
        sub.add_argument('--deck', default=DEFAULT_DECK, help=f'Meeting folder (default: {DEFAULT_DECK})')
        if command == 'serve':
            sub.add_argument('--port', type=int, default=8769)
    new = commands.add_parser('new')
    new.add_argument('date', help='YYYY-MM-DD')
    new.add_argument('--title', default='New presentation')
    commands.add_parser('list')
    args = parser.parse_args(argv)
    try:
        if args.command == 'new':
            print('Created', new_deck(args.date, args.title))
            print(f'Edit the slides, then run: python slides.py serve --deck {args.date}')
            return
        if args.command == 'list':
            for file in sorted((ROOT / 'decks').glob('*/deck.py')):
                deck = load_deck(file.parent.name)
                print(f'{deck.name}  {len(deck.slides):2} slides  {deck.meta["title"]}')
            return
        deck = load_deck(args.deck)
        if args.command == 'check':
            validate(deck, text_bounds=True)
            ids = [load_deck(p.parent.name).meta['id'] for p in (ROOT / 'decks').glob('*/deck.py')]
            if len(ids) != len(set(ids)):
                raise ValueError('Two meetings share a note-storage ID; give each new meeting a unique META.id')
            print(f'Checked {deck.name}: {len(deck.slides)} slides, stable IDs, text bounds and bundled evidence')
            return
        if args.command == 'serve' and not 1 <= args.port <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        if args.command == 'export':
            validate(deck, text_bounds=True)
        if args.command == 'serve':
            # The local showcase picker links to every deck, so prepare each one.
            for file in sorted((ROOT / 'decks').glob('*/deck.py')):
                build(load_deck(file.parent.name), activate=False)
        page = build(deck)
        print('Built', page)
        if args.command == 'export':
            from slidekit.export import export_deck
            capture_widgets(deck, page, page.parent)
            export_deck(deck, page.parent)
        if args.command == 'serve':
            handler = partial(PresentationHandler, directory=str(ROOT))
            with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
                print(f'Open http://localhost:{args.port} — notes save in this browser. Ctrl+C to stop.', flush=True)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print('\nStopped local server')
    except (ValueError, FileNotFoundError, OSError) as error:
        parser.exit(1, f'{error}\n')

if __name__ == '__main__':
    main()
