"""Contrôles statiques ; ne remplace pas les tests HTTP et navigateur."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://alexandre.rogues.fr'
GOOGLE_VERIFICATION = 'ylva5NHAvvBIZWhkt4nmgTzVdqxMyYQFw1ojgWT32LI'
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.refs, self.images, self.headings = [], [], [], []
        self.meta, self.canonical, self.title, self.lang = {}, [], '', ''
        self.in_title = self.in_json = False
        self.in_head = False
        self.google_verifications = []
        self.json_text = ''
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'head': self.in_head = True
        if tag == 'meta' and a.get('name') == 'google-site-verification' and self.in_head:
            self.google_verifications.append(a.get('content', ''))
        if tag == 'html': self.lang = a.get('lang')
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'meta': self.meta[a.get('name', a.get('property'))] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a['href'])
        if tag == 'title': self.in_title = True
        if tag == 'script' and a.get('type') == 'application/ld+json': self.in_json = True
        if tag in ('h1','h2','h3','h4','h5','h6'): self.headings.append(int(tag[1]))
        if tag == 'img': self.images.append(a)
        for k in ('href','src'):
            if k in a: self.refs.append(a[k])
        if 'srcset' in a: self.refs.extend(x.strip().split()[0] for x in a['srcset'].split(','))
    def handle_endtag(self, tag):
        if tag == 'head': self.in_head = False
        if tag == 'title': self.in_title = False
        if tag == 'script': self.in_json = False
    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.in_json: self.json_text += data

paths = [ROOT/'index.html', *sorted((ROOT/'projets').glob('*/index.html'))]
pages = {f: Page(f) for f in paths}
home = pages[ROOT/'index.html']
assert home.google_verifications.count(GOOGLE_VERIFICATION) == 1, (
    'Accueil : balise google-site-verification attendue exactement une fois dans le <head>.'
)
for value in home.google_verifications:
    if value != GOOGLE_VERIFICATION:
        print(f'Attention : autre valeur google-site-verification conservée : {value!r}')
urls, titles, descriptions = [], set(), set()
for f, p in pages.items():
    url = BASE + '/' + str(f.parent.relative_to(ROOT)).strip('.')
    if not url.endswith('/'): url += '/'
    assert p.canonical == [url], f'Canonique : {f}'
    urls.append(url)
    assert p.lang == 'fr' and p.headings.count(1) == 1, f
    assert all(b <= a+1 for a,b in zip(p.headings,p.headings[1:])), f
    assert len(p.ids) == len(set(p.ids)), f
    assert p.title and p.title not in titles, f
    titles.add(p.title)
    description = p.meta['description']
    assert description and description not in descriptions, f
    descriptions.add(description)
    assert 'noindex' not in p.meta.get('robots','').lower(), f
    assert p.meta['og:title'] == p.meta['twitter:title'] == p.title, f
    assert p.meta['og:description'] == p.meta['twitter:description'] == description, f
    assert p.meta['og:url'] == url, f
    assert p.meta['og:image'] == p.meta['twitter:image'] == BASE+'/assets/partage.jpg', f
    assert p.meta['og:image:alt'] and p.meta['twitter:image:alt'], f
    assert 'localhost' not in str(p.meta) and '127.0.0.1' not in str(p.meta), f
    data = json.loads(p.json_text)
    assert data['@graph'][1]['url'] == url and data['@graph'][0]['name'] == 'Alexandre Rogues', f
    for a in p.images:
        assert a.get('alt') and int(a['width']) > 0 and int(a['height']) > 0, f
    for ref in p.refs:
        u = urlsplit(ref)
        if u.scheme: continue
        dest = ROOT/u.path.lstrip('/') if u.path.startswith('/') else f.parent/u.path
        if not u.path: dest = f
        if dest.is_dir(): dest /= 'index.html'
        assert dest.exists(), (f, ref)
        if u.fragment:
            assert u.fragment in pages[dest].ids, (f, ref)
ns = {'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
tree = ET.parse(ROOT/'sitemap.xml')
listed = [e.text for e in tree.findall('.//s:loc', ns)]
assert len(listed) == len(set(listed)) and set(listed) == set(urls)
assert 'Disallow: /' not in (ROOT/'robots.txt').read_text()
assert 'Sitemap: '+BASE+'/sitemap.xml' in (ROOT/'robots.txt').read_text()
assert (ROOT/'assets/partage.jpg').exists()
print(f'{len(pages)} pages validées : métadonnées, JSON-LD, titres, images, ressources, ancres, sitemap et validation Google dans le <head>.')
