# genera_pacchetti.py - genera il catalogo "Estate" (pacchetti DEMO) per validare la domanda. Si rilancia quando vuoi.
# GUIDA-SVILUPPO
# COSA FA: da una tabella di destinazioni (DEST, qui sotto) crea per OGNI destinazione x numero di notti x formula
#   (solo alloggio / alloggio + eventi) un prodotto in _data/catalogo.json, la sua pagina IT in _negozio/ e quella EN in en/negozio/,
#   piu' le 4 categorie (pagine IT/EN + _data/shop-categorie.json). Riscrive tutto da zero: i file generati NON vanno modificati a mano.
# COME SI USA:  python automation\genera_pacchetti.py   poi   python automation\allinea_hash.py en   poi   automation\controllo.ps1
# PER AGGIUNGERE UN PACCHETTO "all'infinito": aggiungi UNA riga a DEST (id, nomi, area, prezzo 7 notti, notti disponibili, emoji, testi) e rilancia.
# PUNTI CRITICI:
#  1) Sono pacchetti DEMO per misurare l'interesse (prezzi indicativi inventati, non offerte reali). Ogni scheda dice chiaramente
#     "pre-iscrizione senza impegno, nessun pagamento online": NON toglierlo finche' non ci sono partner e date vere.
#  2) Prezzi in CENTESIMI (come richiede catalogo.json). L'id categoria non deve essere "esempio".
#  3) Il file .md di ogni prodotto contiene solo l'id (pid): i testi vivono in catalogo.json (vedi _layouts/negozio-prodotto.html).
#  4) Le date sono estate 2027 (scrivi qui sotto in ANNO se cambia la stagione).
import json, os, glob, io
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANNO = '2027'

# area: italia | isole (Croazia e Grecia) | spagna (Spagna e Mediterraneo)
# (id, nome_it, nome_en, area, prezzo_7_notti_euro, notti_disponibili, emoji, vibe_it, vibe_en)
DEST = [
 ('gallipoli', 'Gallipoli', 'Gallipoli', 'italia', 520, [3, 5, 7], '\U0001F3D6', 'Mare, aperitivi in spiaggia e serate nei club del Salento', 'Sea, beach aperitifs and nights out at the Salento clubs'),
 ('salento-mare', 'Salento mare (Otranto)', 'Salento seaside (Otranto)', 'italia', 460, [5, 7], '\U0001F30A', 'Scogliere, acqua cristallina e serate tranquille', 'Cliffs, crystal clear water and relaxed evenings'),
 ('riviera-romagnola', 'Riviera Romagnola', 'Romagna Riviera', 'italia', 430, [3, 5, 7], '\U0001F389', 'Rimini e Riccione tra spiaggia, locali e serate a tema', 'Rimini and Riccione: beach, venues and themed nights'),
 ('ponza', 'Ponza', 'Ponza', 'italia', 560, [3, 5, 7], '\u26F5', 'Isola vicina a Roma, calette e giri in barca', 'An island close to Rome, coves and boat trips'),
 ('tropea', 'Tropea', 'Tropea', 'italia', 480, [5, 7], '\U0001F305', 'Spiaggia bianca, tramonti e vita da paese', 'White beaches, sunsets and village life'),
 ('alghero', 'Alghero', 'Alghero', 'italia', 520, [5, 7], '\U0001F3DD', 'Sardegna, mare turchese e centro storico', 'Sardinia, turquoise sea and old town'),
 ('pag-zrce', 'Isola di Pag (Zrce)', 'Pag Island (Zrce)', 'isole', 430, [5, 7], '\U0001F3B6', 'La spiaggia dei festival della Croazia', 'The Croatian festival beach'),
 ('hvar', 'Hvar', 'Hvar', 'isole', 650, [5, 7], '\U0001F6A4', 'Isole Pakleni di giorno, vita notturna la sera', 'Pakleni islands by day, nightlife by night'),
 ('corfu', 'Corfu', 'Corfu', 'isole', 520, [5, 7], '\U0001F3D6', 'Movida sul lungomare e spiagge', 'Seafront nightlife and beaches'),
 ('mykonos', 'Mykonos', 'Mykonos', 'isole', 880, [5, 7], '\U0001F379', 'Beach club e feste con gli amici', 'Beach clubs and parties with friends'),
 ('santorini', 'Santorini', 'Santorini', 'isole', 900, [5, 7], '\U0001F307', 'Tramonti, borghi bianchi e relax', 'Sunsets, white villages and relaxation'),
 ('zante', 'Zante', 'Zakynthos', 'isole', 560, [7], '\U0001F422', 'Mare, escursioni e serate a Laganas', 'Sea, excursions and nights in Laganas'),
 ('ibiza', 'Ibiza', 'Ibiza', 'spagna', 780, [3, 5, 7], '\U0001F3A7', 'Club, dj internazionali e beach party', 'Clubs, international DJs and beach parties'),
 ('lloret-de-mar', 'Lloret de Mar', 'Lloret de Mar', 'spagna', 460, [5, 7], '\U0001F31E', 'Costa Brava, spiaggia e locali', 'Costa Brava, beach and venues'),
 ('maiorca', 'Maiorca', 'Majorca', 'spagna', 650, [5, 7], '\U0001F3DD', 'Calette, beach club e feste a Palma', 'Coves, beach clubs and parties in Palma'),
 ('barcellona', 'Barcellona', 'Barcelona', 'spagna', 520, [3, 5], '\U0001F3D9', 'Citta e mare insieme, tapas e serate', 'City and sea together, tapas and nights out'),
 ('malta', 'Malta', 'Malta', 'spagna', 560, [5, 7], '\U0001F30D', 'Mare, inglese e serate a Paceville', 'Sea, English and nights in Paceville'),
 ('budva', 'Budva', 'Budva', 'spagna', 470, [5, 7], '\U0001F305', 'Montenegro economico, mare e movida', 'Affordable Montenegro, sea and nightlife'),
]
CAT = {
 'estate-italia': ('Estate in Italia', 'Summer in Italy', 'italy', '\U0001F3D6'),
 'estate-isole': ('Estate Croazia e Grecia', 'Summer in Croatia and Greece', 'croatia-greece', '\u26F5'),
 'estate-spagna': ('Estate Spagna e Mediterraneo', 'Summer in Spain and the Mediterranean', 'spain-mediterranean', '\U0001F31E'),
 'estate-weekend': ('Weekend d\'estate', 'Summer weekends', 'weekends', '\U0001F389'),
}
AREA_CAT = {'italia': 'estate-italia', 'isole': 'estate-isole', 'spagna': 'estate-spagna'}
FATT = {3: 0.48, 5: 0.75, 7: 1.0}

def euro5(x):
    return int(round(x / 5.0)) * 5

def put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

def yq(s):  # virgolette doppie nel front matter YAML
    return s.replace('\\', '\\\\').replace('"', '\\"')

# 1) pulizia: SOLO le pagine shop (esempi del template e pacchetti vecchi generati qui)
for pat in ('_negozio/*.md', 'en/negozio/*.md', 'en/negozio/categoria/*.md'):
    for f in glob.glob(os.path.join(ROOT, pat)):
        os.remove(f)

# 2) prodotti
prodotti = []
for (did, nit, nen, area, p7, notti, emo, vit, ven) in DEST:
    for n in notti:
        for party in (False, True):
            prezzo = euro5(p7 * FATT[n]) + (15 * n if party else 0)
            pid = '%s-%d-notti-%s' % (did, n, 'eventi' if party else 'alloggio')
            cat = 'estate-weekend' if n == 3 else AREA_CAT[area]
            f_it = 'Alloggio + eventi' if party else 'Solo alloggio'
            f_en = 'Stay + events' if party else 'Stay only'
            nome_it = '%s - %d notti - %s' % (nit, n, f_it)
            nome_en = '%s - %d nights - %s' % (nen, n, f_en)
            br_it = '%d notti a %s con ragazzi della tua et\u00e0. %s.' % (n, nit, vit)
            br_en = '%d nights in %s with people your age. %s.' % (n, nen, ven)
            inc_it = 'Include: pernottamento in appartamento o residence (camere multiple), coordinatore del gruppo, gruppo WhatsApp prima della partenza.'
            inc_en = 'Includes: accommodation in an apartment or residence (shared rooms), group coordinator, WhatsApp group before departure.'
            if party:
                inc_it += ' Ingresso a serate ed eventi selezionati con aperitivi.'
                inc_en += ' Entry to selected nights and events with aperitifs.'
            full_it = '\n'.join([
                '%d notti a %s, in gruppo con persone della tua et\u00e0. %s.' % (n, nit, vit), inc_it,
                'Non include: viaggio, pasti e spese personali.',
                'Partenze in programmazione: giugno-settembre %s. Prezzo indicativo da %d euro a persona.' % (ANNO, prezzo),
                'Pre-iscrizione senza impegno: nessun pagamento online. Ti ricontattiamo quando le date sono confermate.'])
            full_en = '\n'.join([
                '%d nights in %s, in a group with people your age. %s.' % (n, nen, ven), inc_en,
                'Not included: travel, meals and personal expenses.',
                'Departures being planned: June-September %s. Indicative price from %d euros per person.' % (ANNO, prezzo),
                'No-commitment pre-registration: no online payment. We will contact you when the dates are confirmed.'])
            prodotti.append({'tipo': 'digitale', 'id': pid, 'nome': nome_it, 'categoria': cat, 'prezzo_centesimi': prezzo * 100,
                'descrizione': br_it, 'descrizione_completa': full_it, 'immagine': '', 'icona': emo, 'visibile': True,
                'tr': {'en': {'nome': nome_en, 'descrizione': br_en, 'descrizione_completa': full_en}}})
            put(os.path.join(ROOT, '_negozio', pid + '.md'),
                '---\nlayout: negozio-prodotto\ntitle: "%s"\npid: %s\npermalink: /negozio/%s/\ndescription: "%s"\nref: shop-prod-%s\n---\n' % (yq(nome_it), pid, pid, yq(br_it), pid))
            put(os.path.join(ROOT, 'en', 'negozio', pid + '.md'),
                '---\nlayout: negozio-prodotto\ntitle: "%s"\npid: %s\npermalink: /en/shop/%s/\ndescription: "%s"\nlang: en\nlocale: en\nref: shop-prod-%s\ntr: tradotto\ntr_hash: 0\n---\n' % (yq(nome_en), pid, pid, yq(br_en), pid))

# 3) categorie (catalogo + pagine IT/EN + elenco per l'admin)
categorie = []
for cid, (cit, cen, slug_en, emo) in CAT.items():
    categorie.append({'nome': cit, 'id': cid, 'icona': emo, 'tr': {'en': {'nome': cen}}})
    put(os.path.join(ROOT, '_negozio', 'categoria-%s.md' % cid),
        '---\nlayout: negozio-categoria\ntitle: "%s"\ncid: %s\npermalink: /negozio/categoria/%s/\ndescription: "Pacchetti %s."\nref: shop-cat-%s\n---\n' % (yq(cit), cid, cid, yq(cit.lower()), cid))
    put(os.path.join(ROOT, 'en', 'negozio', 'categoria', '%s.md' % cid),
        '---\nlayout: negozio-categoria\ntitle: "%s"\ncid: %s\npermalink: /en/shop/category/%s/\ndescription: "%s packages."\nlang: en\nlocale: en\nref: shop-cat-%s\ntr: tradotto\ntr_hash: 0\n---\n' % (yq(cen), cid, slug_en, yq(cen), cid))

cpath = os.path.join(ROOT, '_data', 'catalogo.json')
with io.open(cpath, encoding='utf-8') as f:
    cat_json = json.load(f)
cat_json['categorie'] = categorie
cat_json['prodotti'] = prodotti
with io.open(cpath, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(cat_json, f, ensure_ascii=False, indent=2)
with io.open(os.path.join(ROOT, '_data', 'shop-categorie.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump([{'nome': v[0], 'slug': k} for k, v in CAT.items()], f, ensure_ascii=False, indent=2)
print('pacchetti: %d, categorie: %d' % (len(prodotti), len(categorie)))
