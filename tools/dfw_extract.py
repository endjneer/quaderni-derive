# -*- coding: utf-8 -*-
"""
Estrattore per file .dfw (Derive for Windows 6.x).

Formato osservato:
  - riga di intestazione ASCII "Derive version 6.10 DfW file saved on <data>\r"
  - 0x1A seguito da un blocco di impostazioni "Chiave:=Valore\r"
  - una sequenza di record "oggetto espressione", ciascuno contenente:
      * una stringa UTF-16LE con l'origine dell'espressione ("User" oppure
        la chiamata Derive che l'ha generata, es. "Simp(Solve(#11,z))")
      * un indice a 32 bit little-endian
      * la costante 01 00 00 00
      * una stringa in stile Pascal: 1 byte di lunghezza + testo ASCII
"""
import re, sys, os, json, glob

def utf16_strings(buf, minlen=3):
    """Tutte le stringhe UTF-16LE stampabili con offset."""
    out = []
    i = 0
    n = len(buf)
    while i + 1 < n:
        if 32 <= buf[i] < 127 and buf[i+1] == 0:
            j = i
            chars = []
            while j + 1 < n and 32 <= buf[j] < 127 and buf[j+1] == 0:
                chars.append(chr(buf[j])); j += 2
            if len(chars) >= minlen:
                out.append((i, ''.join(chars)))
            i = j
        else:
            i += 2 if buf[i] == 0 else 1
    return out

# 0x7F introduce un carattere non-ASCII codificato come 4 cifre esadecimali
# Unicode (es. 0x7F "03b5" -> epsilon). Va quindi accettato nel testo.
PRINTABLE = set(range(32, 127)) | {0x7F}

ESCAPE_RE = re.compile('([0-9a-fA-F]{4})')

def unescape(txt):
    """Converte le sequenze 0x7F+hex4 di Derive in caratteri Unicode."""
    return ESCAPE_RE.sub(lambda m: chr(int(m.group(1), 16)), txt)

def pascal_at(buf, pos):
    """Legge la stringa a lunghezza prefissa in pos.

    Lunghezza < 255 -> 1 byte. Altrimenti 0xFF seguito da un intero a 16 bit
    little-endian (usato dalle espressioni molto lunghe).
    Restituisce None se il blocco non e' testo stampabile plausibile.
    """
    if pos >= len(buf):
        return None
    if buf[pos] == 0xFF:
        if pos + 3 > len(buf):
            return None
        ln = int.from_bytes(buf[pos+1:pos+3], 'little')
        start = pos + 3
    else:
        ln = buf[pos]
        start = pos + 1
    if ln < 1 or start + ln > len(buf):
        return None
    s = buf[start:start+ln]
    if not all(b in PRINTABLE for b in s):
        return None
    return unescape(s.decode('latin-1'))

def extract(path):
    raw = open(path, 'rb').read()
    header_end = raw.find(b'\x1a')
    header = raw[:header_end].decode('latin-1', 'replace').strip() if header_end > 0 else ''

    settings = {}
    body_start = header_end + 1 if header_end > 0 else 0
    m = re.search(rb'DisplaySteps:=\w+\r', raw)
    settings_end = m.end() if m else body_start
    for k, v in re.findall(rb'([A-Za-z]+):=([^\r\n]*)\r', raw[body_start:settings_end]):
        settings[k.decode()] = v.decode('latin-1')

    # Marker di record: <idx:4 LE> 01 00 00 00 <len> <testo>
    items = []
    seen = set()
    for m in re.finditer(rb'\x01\x00\x00\x00', raw[settings_end:]):
        abs_pos = settings_end + m.start()
        if abs_pos < 4:
            continue
        idx = int.from_bytes(raw[abs_pos-4:abs_pos], 'little')
        if idx == 0 or idx > 5000:
            continue
        txt = pascal_at(raw, abs_pos + 4)
        if txt is None:
            continue
        if abs_pos in seen:
            continue
        seen.add(abs_pos)
        items.append({'idx': idx, 'pos': abs_pos, 'text': txt})

    # Origine: ultima stringa UTF-16 che precede il record
    u16 = utf16_strings(raw)
    for it in items:
        origin = ''
        for off, s in u16:
            if off < it['pos']:
                origin = s
            else:
                break
        it['origin'] = origin

    items.sort(key=lambda d: (d['idx'], d['pos']))
    # deduplica per indice tenendo la prima occorrenza
    dedup, taken = [], set()
    for it in items:
        if it['idx'] in taken:
            continue
        taken.add(it['idx']); dedup.append(it)

    return {'file': os.path.basename(path), 'header': header,
            'settings': settings, 'items': dedup}

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src = sys.argv[1]
    out = sys.argv[2]
    res = []
    for p in sorted(glob.glob(os.path.join(src, '*.dfw'))):
        res.append(extract(p))
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    for r in res:
        print('=' * 70)
        print(r['file'], '|', r['header'], '|', len(r['items']), 'espressioni')
        for it in r['items']:
            print('  #%-3d [%s] %s' % (it['idx'], it['origin'][:28], it['text']))
