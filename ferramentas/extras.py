"""
Raio-X SPFC · extras.py
Análises extras usadas pelo montar.py:
  - janelas de 15 minutos (gols e xG a favor e contra)
  - impacto das substituições (time e jogadores vindos do banco)
  - comparação com os vizinhos de tabela e com a média da Série A
  - placar das previsões (escalação sugerida × escalada, palpite × resultado)
  - retrospectiva da temporada (modo fim de temporada)
Só usa a biblioteca padrão do Python.
"""
import json, os, unicodedata, statistics as stt
from collections import defaultdict

JANELAS = [(0, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 200)]
ROT_JAN = ['0-15', '16-30', '31-45', '46-60', '61-75', '76+']


def _jan(t):
    for i, (a, b) in enumerate(JANELAS):
        if t <= b:
            return i
    return 5


def _shots(o):
    S = o['SHOTMAP']
    out = []
    for i in range(0, len(S) - 16, 17):
        s = S[i:i + 17]
        out.append({'rd': int(s[0:2]), 'us': s[3] == '1', 'xg': int(s[8:10]) / 100, 'gol': s[10] == 'g', 'min': int(s[11:13])})
    return out


def _gols(o):
    out = []
    for g in o['GOLS']:
        q = g.split('|')
        out.append({'rd': int(q[0]), 'us': q[2] == '1', 'min': int(q[3]), 'add': int(q[4] or 0)})
    return out


def _campo(o):
    out = {}
    for c in o['CAMPO']:
        rd, on, st = c.split('#')
        iv = {}
        for t in on.split():
            k, a, b = t.split(':')
            iv[int(k)] = (int(a), int(b))
        out[int(rd)] = {'iv': iv, 'tit': [int(x) for x in st.split(',') if x != '']}
    return out


def janelas(o):
    gl, sh = _gols(o), _shots(o)
    r = {'rot': ROT_JAN, 'gf': [0] * 6, 'gc': [0] * 6, 'xgf': [0.0] * 6, 'xgc': [0.0] * 6}
    for g in gl:
        r['gf' if g['us'] else 'gc'][_jan(g['min'])] += 1
    for s in sh:
        r['xgf' if s['us'] else 'xgc'][_jan(s['min'])] += s['xg']
    r['xgf'] = [round(v, 1) for v in r['xgf']]
    r['xgc'] = [round(v, 1) for v in r['xgc']]
    return r


def substituicoes(o, nomes):
    """Antes × depois da 1ª troca (por 90 min) e jogadores que entram do banco."""
    gl, sh, campo = _gols(o), _shots(o), _campo(o)
    gpj, spj = defaultdict(list), defaultdict(list)
    for g in gl:
        gpj[g['rd']].append(g)
    for s in sh:
        spj[s['rd']].append(s)
    antes = {'min': 0, 'gf': 0, 'gc': 0, 'xgf': 0.0, 'xgc': 0.0}
    depois = {'min': 0, 'gf': 0, 'gc': 0, 'xgf': 0.0, 'xgc': 0.0}
    primeiras, banco = [], defaultdict(lambda: {'ent': 0, 'min': 0, 'gf': 0, 'gc': 0, 'xgf': 0.0, 'xgc': 0.0})
    for rd, c in campo.items():
        iv = c['iv']
        fim = max([b for a, b in iv.values()] + [90])
        ent = sorted(a for a, b in iv.values() if a > 0)
        t1 = ent[0] if ent else fim
        if ent:
            primeiras.append(t1)
        for g in gpj[rd]:
            t = g['min'] + g['add'] / 10
            alvo = antes if t < t1 else depois
            alvo['gf' if g['us'] else 'gc'] += 1
        for s in spj[rd]:
            alvo = antes if s['min'] < t1 else depois
            alvo['xgf' if s['us'] else 'xgc'] += s['xg']
        antes['min'] += t1
        depois['min'] += fim - t1
        for k, (a, b) in iv.items():
            if a <= 0:
                continue
            p = banco[k]
            p['ent'] += 1
            p['min'] += b - a
            for g in gpj[rd]:
                t = g['min'] + g['add'] / 10
                if a <= t <= b:
                    p['gf' if g['us'] else 'gc'] += 1
            for s in spj[rd]:
                if a <= s['min'] <= b:
                    p['xgf' if s['us'] else 'xgc'] += s['xg']
    def p90(d):
        m = d['min'] or 1
        return {'min': d['min'], 'gf': d['gf'], 'gc': d['gc'], 'xgf90': round(d['xgf'] / m * 90, 2), 'xgc90': round(d['xgc'] / m * 90, 2),
                'saldo90': round((d['gf'] - d['gc']) / m * 90, 2)}
    lista = []
    for k, p in banco.items():
        if p['ent'] >= 4 and k < len(nomes):
            m = p['min'] or 1
            lista.append({'nome': nomes[k], 'ent': p['ent'], 'min': p['min'], 'gf': p['gf'], 'gc': p['gc'],
                          'xgSaldo90': round((p['xgf'] - p['xgc']) / m * 90, 2)})
    lista.sort(key=lambda x: -x['xgSaldo90'])
    return {'antes': p90(antes), 'depois': p90(depois),
            'minPrimeira': round(stt.mean(primeiras)) if primeiras else None, 'banco': lista}


def rivais(o):
    tab = o.get('tabela', [])
    if not tab:
        return None
    def linha(r):
        j = r[2] or 1
        return {'pos': r[0], 'time': r[1], 'j': r[2], 'pts': r[8], 'ppj': round(r[8] / j, 2), 'gpj': round(r[6] / j, 2), 'gcj': round(r[7] / j, 2),
                'saldo': r[6] - r[7], 'aprov': round(r[8] / (3 * j) * 100), 'proj38': round(r[8] / j * 38)}
    sp = next((r for r in tab if r[1] == 'São Paulo'), None)
    viz = [linha(r) for r in tab if sp and abs(r[0] - sp[0]) <= 3]
    J = sum(r[2] for r in tab) or 1
    media = {'time': 'Média da Série A', 'ppj': round(sum(r[8] for r in tab) / J, 2), 'gpj': round(sum(r[6] for r in tab) / J, 2),
             'gcj': round(sum(r[7] for r in tab) / J, 2), 'aprov': round(sum(r[8] for r in tab) / (3 * J) * 100)}
    return {'vizinhos': viz, 'media': media, 'casa': o.get('tabelaCasa'), 'fora': o.get('tabelaFora')}


# ---------- previsões ----------
def _norm(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower().replace('.', ' ').split()


def casar(curto, nomes):
    """'M. Antônio' -> 'Marcos Antônio'; 'Tolói' -> 'Rafael Tolói'. Devolve o nome completo ou None."""
    curto = curto.split('(')[0].strip()
    for n in nomes:
        if _norm(n) == _norm(curto):
            return n
    t = _norm(curto)
    cands = []
    for n in nomes:
        full = _norm(n)
        ok = True
        for x in t:
            if len(x) == 1:
                ok = ok and any(f.startswith(x) for f in full)
            else:
                ok = ok and x in full
        if ok:
            cands.append(n)
    return cands[0] if len(cands) == 1 else None


def previsoes(o, nomes, caminho):
    """Lê data/previsoes.json, preenche o resultado real dos jogos já disputados e devolve a lista + o placar."""
    if not os.path.exists(caminho):
        return [], None
    L = json.load(open(caminho, encoding='utf-8'))
    G = {g[0]: g for g in o['SOFA']['G']}
    campo = _campo(o)
    for p in L:
        g = G.get(p['rd'])
        if not g:
            continue
        gf, ga = g[4], g[5]
        res = 'V' if gf > ga else 'E' if gf == ga else 'D'
        tit = [nomes[k] for k in campo.get(p['rd'], {}).get('tit', []) if k < len(nomes)]
        sug = [casar(x, nomes) or x for x in p['xi']]
        acertos = [x for x in sug if x in tit]
        prob = p.get('prob')
        brier = None
        if prob:
            alvo = {'V': [1, 0, 0], 'E': [0, 1, 0], 'D': [0, 0, 1]}[res]
            brier = round(sum((prob[i] / 100 - alvo[i]) ** 2 for i in range(3)), 3)
        p['real'] = {'placar': f'{gf}x{ga}', 'res': res, 'xi': tit, 'acertosXI': len(acertos),
                     'foraDoPlano': [x for x in tit if x not in sug], 'naoUsados': [x for x in sug if x not in tit],
                     'acertouPalpite': p.get('palpite') == res, 'acertouModelo': _fav(prob) == res if prob else None, 'brier': brier}
    feitos = [p for p in L if p.get('real')]
    placar = None
    if feitos:
        placar = {'jogos': len(feitos),
                  'palpites': sum(1 for p in feitos if p['real']['acertouPalpite']),
                  'modelo': sum(1 for p in feitos if p['real']['acertouModelo']),
                  'xiMedio': round(stt.mean(p['real']['acertosXI'] for p in feitos), 1),
                  'brier': round(stt.mean(p['real']['brier'] for p in feitos if p['real']['brier'] is not None), 3)}
    return L, placar


def _fav(prob):
    return 'VED'[max(range(3), key=lambda i: prob[i])]


# ---------- fim de temporada ----------
def retrospectiva(R, o, prev, placar, br):
    G = sorted(o['SOFA']['G'], key=lambda g: g[0])
    pts = lambda g: 3 if g[4] > g[5] else 1 if g[4] == g[5] else 0
    turno = [g for g in G if g[0] <= 19]
    returno = [g for g in G if g[0] > 19]
    jog = [j for j in R['jogadores'] if j['nota'] and j['min'] >= 900]
    jog.sort(key=lambda j: -j['nota'])
    L = ['# Retrospectiva 2026 · Raio-X Tricolor', '',
         f"**Campanha:** {R['posicao']}º · {R['pts']} pts em {R['jogos']} jogos · {R['gp']}:{R['gc']}",
         f"**Turno × returno:** {sum(pts(g) for g in turno)} pts em {len(turno)} · {sum(pts(g) for g in returno)} pts em {len(returno)}",
         f"**Casa × fora:** {R['casa']['aprov']}% · {R['fora']['aprov']}%", '',
         '## Melhores notas (900+ min)'] + [f"- {j['nome']}: {br(j['nota'])} ({j['min']} min, {j['gols']} G, {j['assist']} A)" for j in jog[:5]]
    L += ['', '## Notas mais baixas (900+ min)'] + [f"- {j['nome']}: {br(j['nota'])} ({j['min']} min)" for j in jog[-5:]]
    art = sorted(R['jogadores'], key=lambda j: -(j['gols'] + j['assist']))[:5]
    L += ['', '## Participações em gol'] + [f"- {j['nome']}: {j['gols']} G + {j['assist']} A" for j in art]
    L += ['', '## Melhor e pior sequência']
    seq = [pts(g) for g in G]
    best = max(range(len(seq) - 4), key=lambda i: sum(seq[i:i + 5])) if len(seq) >= 5 else 0
    worst = min(range(len(seq) - 4), key=lambda i: sum(seq[i:i + 5])) if len(seq) >= 5 else 0
    L += [f"- Melhor: R{G[best][0]} a R{G[best + 4][0]}, {sum(seq[best:best + 5])} pts em 5",
          f"- Pior: R{G[worst][0]} a R{G[worst + 4][0]}, {sum(seq[worst:worst + 5])} pts em 5"]
    if placar:
        L += ['', '## Placar das previsões',
              f"- Palpites certos: {placar['palpites']} de {placar['jogos']} (favorito do modelo: {placar['modelo']})",
              f"- Titulares acertados por jogo: {br(placar['xiMedio'], 1)} de 11 · Brier do modelo: {br(placar['brier'], 3)}"]
    L += ['', '## Para 2027', '- Trocar `SEASON` no coletor.js e abrir `data/rodadas/2027/`.',
          '- Guardar `data/rodadas/` de 2026 e o `index.html` final como `arquivo/2026/`.']
    return '\n'.join(L) + '\n'
