"""Una categoria per DESTINAZIONE (sotto i 3 reparti Italia / Croazia e Grecia / Spagna e Mediterraneo).
Cosa fa: legge _data/catalogo.json, ricava la destinazione dal nome prodotto ("Gallipoli - 3 notti - ..."),
crea una categoria figlia (campo genitore) per ognuna, sposta i prodotti, toglie "Weekend d'estate"
(i weekend finiscono nella loro destinazione), crea i file _negozio/ e en/negozio/categoria/.
Rilanciabile: riscrive sempre tutto da zero. Dopo: python automation/allinea_hash.py en
"""
import json, re, os, unicodedata

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, '_data', 'catalogo.json')
d = json.load(open(P, encoding='utf-8'))

REPARTI = ['estate-italia', 'estate-isole', 'estate-spagna']
EN = {  # nome inglese (solo dove cambia)
    'Salento mare (Otranto)': 'Salento seaside (Otranto)', 'Riviera Romagnola': 'Romagna Riviera',
    'Isola di Pag (Zrce)': 'Pag Island (Zrce)', 'Maiorca': 'Mallorca', 'Barcellona': 'Barcelona',
}


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


# reparto di appartenenza = categoria "non weekend" in cui compare la destinazione
dest = {}  # nome -> dict
for p in d['prodotti']:
    nome = re.match(r'(.+?) - \d+ nott', p['nome']).group(1)
    e = dest.setdefault(nome, {'reparto': None, 'icona': p.get('icona', '')})
    if p['categoria'] in REPARTI:
        e['reparto'] = p['categoria']
for nome, e in dest.items():
    assert e['reparto'], nome  # ogni destinazione ha almeno un pacchetto "non weekend"

for p in d['prodotti']:
    p['categoria'] = slug(re.match(r'(.+?) - \d+ nott', p['nome']).group(1))

reparti = [c for c in d['categorie'] if c['id'] in REPARTI]
cats = []
for r in reparti:
    cats.append(r)
    for nome, e in dest.items():
        if e['reparto'] == r['id']:
            en = EN.get(nome, nome)
            cats.append({'nome': nome, 'id': slug(nome), 'icona': e['icona'], 'genitore': r['id'],
                         'tr': {'en': {'nome': en}}})
d['categorie'] = cats
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
open(P, 'a', encoding='utf-8').write('\n')

# shop-categorie.json (elenco semplice usato dai menu/admin)
json.dump([{'nome': c['nome'], 'slug': c['id']} for c in cats],
          open(os.path.join(R, '_data', 'shop-categorie.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# pagine categoria
os.makedirs(os.path.join(R, 'en', 'negozio', 'categoria'), exist_ok=True)
for w in ('estate-weekend',):
    for f in (os.path.join(R, '_negozio', 'categoria-%s.md' % w), os.path.join(R, 'en', 'negozio', 'categoria', '%s.md' % w)):
        if os.path.exists(f):
            os.remove(f)
for c in cats:
    if c['id'] in REPARTI:
        continue
    en = c['tr']['en']['nome']
    open(os.path.join(R, '_negozio', 'categoria-%s.md' % c['id']), 'w', encoding='utf-8', newline='\n').write(
        '---\nlayout: negozio-categoria\ntitle: "%s"\ncid: %s\npermalink: /negozio/categoria/%s/\n'
        'description: "Pacchetti giovani a %s: alloggio ed eventi, 18+."\nref: shop-cat-%s\n---\n'
        % (c['nome'], c['id'], c['id'], c['nome'], c['id']))
    open(os.path.join(R, 'en', 'negozio', 'categoria', '%s.md' % c['id']), 'w', encoding='utf-8', newline='\n').write(
        '---\nlayout: negozio-categoria\ntitle: "%s"\ncid: %s\npermalink: /en/shop/category/%s/\n'
        'description: "Youth packages in %s: stay and events, 18+."\nlang: en\nlocale: en\nref: shop-cat-%s\n'
        'tr: tradotto\ntr_hash: x\n---\n' % (en, c['id'], slug(en), en, c['id']))
print(len(cats) - len(REPARTI), 'destinazioni,', len(d['prodotti']), 'prodotti')
