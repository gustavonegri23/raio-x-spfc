#!/usr/bin/env python3
"""
Raio-X SPFC · montar.py
Lê data/rodadas/rodada-NN.json (saída do coletor.js) e gera:
  1. data/dados.js                    -> dados que a página carrega (SOFA, GPS, SHOTMAP, META)
  2. relatorios/resumo-rodada-NN.md   -> números-chave para reescrever highlights e insights,
                                         com a comparação contra a rodada anterior quando ela existir
Uso:  python3 ferramentas/montar.py            (usa a rodada mais recente em data/rodadas)
      python3 ferramentas/montar.py 34         (rodada específica)
Só usa a biblioteca padrão do Python.
"""
import json, os, sys, glob, statistics as stt
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_ROD = os.path.join(RAIZ, 'data', 'rodadas')
DIR_REL = os.path.join(RAIZ, 'relatorios')


def br(v, d=2):
    return f"{v:.{d}f}".replace('.', ',')


def carregar(n=None):
    arqs = sorted(glob.glob(os.path.join(DIR_ROD, 'rodada-*.json')))
    if not arqs:
        sys.exit('Nenhum arquivo em data/rodadas/')
    if n is None:
        alvo = arqs[-1]
    else:
        alvo = os.path.join(DIR_ROD, f'rodada-{int(n):02d}.json')
    ant = None
    i = arqs.index(alvo) if alvo in arqs else -1
    if i > 0:
        ant = json.load(open(arqs[i - 1], encoding='utf-8'))
    return json.load(open(alvo, encoding='utf-8')), ant


def escrever_dados(o):
    dst = os.path.join(RAIZ, 'data', 'dados.js')
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('/* Dados SofaScore · Série A 2026 · gerado por ferramentas/montar.py */\n')
        f.write('window.SHOTMAP=' + json.dumps(o['SHOTMAP']) + ';\n')
        f.write('window.GPS=' + json.dumps(o['GPS'], separators=(',', ':')) + ';\n')
        f.write('window.SOFA=' + json.dumps(o['SOFA'], ensure_ascii=False, separators=(',', ':')) + ';\n')
        f.write('window.META=' + json.dumps({'rodada': o['rodada'], 'coletado': o['coletado'][:10]}) + ';\n')
    return dst


def analisar(o):
    F = o['SOFA']['F']
    P = []
    for a in o['SOFA']['P']:
        vals = a[4].split(',')
        s = {f: (float(vals[k]) if vals[k] != '' else None) for k, f in enumerate(F)}
        P.append({'nome': a[0], 'pos': a[1], 's': s})
    G = []
    for g in o['SOFA']['G']:
        pl = []
        for t in (g[7].split() if g[7] else []):
            q = t.split(':')
            pl.append({'ix': int(q[0]), 'pos': q[1], 'r': float(q[2]) if q[2] else None, 'min': int(q[3]), 'sub': q[4] == '1'})
        G.append({'rd': g[0], 'home': g[2] == 1, 'opp': g[3], 'gf': g[4], 'ga': g[5], 'form': g[6], 'pl': pl})
    G.sort(key=lambda x: x['rd'])
    pts = lambda g: 3 if g['gf'] > g['ga'] else 1 if g['gf'] == g['ga'] else 0
    R = {}
    # campanha
    R['jogos'] = len(G)
    R['pts'] = sum(pts(g) for g in G)
    R['gp'] = sum(g['gf'] for g in G); R['gc'] = sum(g['ga'] for g in G)
    for lab, f in [('casa', lambda g: g['home']), ('fora', lambda g: not g['home'])]:
        z = [g for g in G if f(g)]
        R[lab] = {'j': len(z), 'pts': sum(pts(g) for g in z), 'gp': sum(g['gf'] for g in z), 'gc': sum(g['ga'] for g in z),
                  'aprov': round(sum(pts(g) for g in z) / (3 * len(z)) * 100) if z else 0}
    R['ultimos5'] = [(g['rd'], ('vs ' if g['home'] else '@ ') + g['opp'], f"{g['gf']}x{g['ga']}") for g in G[-5:]]
    tab = o.get('tabela', [])
    sp = next((r for r in tab if r[1] == 'São Paulo'), None)
    R['posicao'] = sp[0] if sp else None
    R['vizinhos'] = [r for r in tab if sp and abs(r[0] - sp[0]) <= 3]
    # formações
    fm = defaultdict(lambda: [0, 0, 0, 0])
    for g in G:
        a = fm[g['form']]; a[0] += 1; a[1] += pts(g); a[2] += g['gf']; a[3] += g['ga']
    R['formacoes'] = sorted(fm.items(), key=lambda x: -x[1][0])
    tres = lambda f: f[:1] in ('3', '5')
    # gols
    gols = [x.split('|') for x in o.get('GOLS', [])]
    bins = [(0, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 200)]
    def faixa(t):
        t = int(t)
        for i, (a, b) in enumerate(bins):
            if t <= b:
                return i
        return 5
    R['gols_faixa'] = {lado: [Counter(faixa(g[3]) for g in gols if g[2] == lado)[i] for i in range(6)] for lado in ('1', '0')}
    R['gols_tipo'] = {lado: Counter(g[8] for g in gols if g[2] == lado).most_common() for lado in ('1', '0')}
    R['gols_cabeca'] = {lado: sum(1 for g in gols if g[2] == lado and g[9] == 'H') for lado in ('1', '0')}
    R['gols_tarde_sofridos'] = [(int(g[0]), g[3] + (('+' + g[4]) if g[4] not in ('', '0') else '')) for g in gols if g[2] == '0' and int(g[3]) >= 80]
    porjogo = defaultdict(list)
    for g in gols:
        porjogo[int(g[0])].append((int(g[3]) + int(g[4] or 0) / 100, g[2]))
    prim = defaultdict(lambda: [0, 0])
    liderou_sem_vencer = []
    for g in G:
        ev = sorted(porjogo.get(g['rd'], []))
        k = 'sem gol' if not ev else ('marcou primeiro' if ev[0][1] == '1' else 'sofreu primeiro')
        prim[k][0] += 1; prim[k][1] += pts(g)
        a = b = 0; led = False
        for t, u in ev:
            a += u == '1'; b += u == '0'
            led = led or a > b
        if led and pts(g) < 3:
            liderou_sem_vencer.append((g['rd'], g['opp'], f"{g['gf']}x{g['ga']}", 3 - pts(g)))
    R['primeiro_gol'] = dict(prim)
    R['liderou_sem_vencer'] = liderou_sem_vencer
    # xG pelo mapa de chutes
    # SHOTMAP v2, 17 caracteres por chute: rodada(2) mando(1) lado(1) x(2) y(2) xg(2) tipo(1) minuto(2) jogador(2) jogada(1) corpo(1)
    S = o['SHOTMAP']; sh = [S[i:i + 17] for i in range(0, len(S), 17)]
    def xg(us, home=None):
        z = [s for s in sh if s[3] == us and (home is None or s[2] == home)]
        return round(sum(int(s[8:10]) for s in z) / 100, 1), sum(1 for s in z if s[10] == 'g'), len(z)
    R['xg'] = {'favor': xg('1'), 'contra': xg('0'), 'favor_casa': xg('1', '1'), 'favor_fora': xg('1', '0'), 'contra_casa': xg('0', '1'), 'contra_fora': xg('0', '0')}
    # jogadores: nota por recorte
    jog = []
    for i, p in enumerate(P):
        rows = [(g, e) for g in G for e in g['pl'] if e['ix'] == i and e['r'] is not None]
        def av(f):
            x = [e['r'] for g, e in rows if f(g, e)]
            return (round(stt.mean(x), 2), len(x)) if len(x) >= 2 else None
        best = max(rows, key=lambda r: r[1]['r']) if rows else None
        ult = [e['r'] for g, e in rows][-3:]
        jog.append({'nome': p['nome'], 'min': int(p['s']['minutesPlayed'] or 0), 'nota': p['s']['rating'], 'gols': int(p['s']['goals'] or 0), 'assist': int(p['s']['assists'] or 0),
                    'xg': p['s']['expectedGoals'], '3z': av(lambda g, e: tres(g['form'])), '4z': av(lambda g, e: not tres(g['form'])),
                    'casa': av(lambda g, e: g['home']), 'fora': av(lambda g, e: not g['home']),
                    'melhor': (best[0]['rd'], best[0]['opp'], best[1]['r']) if best else None, 'ultimas3': ult})
    R['jogadores'] = jog
    # duplas e impacto em campo
    campo = []
    for c in o.get('CAMPO', []):
        rd, on, st = c.split('#')
        iv = {}
        for t in on.split():
            k, a, b = t.split(':'); iv[int(k)] = (int(a), int(b))
        campo.append((int(rd), iv, [int(x) for x in st.split(',') if x != '']))
    gl = defaultdict(list)
    for g in gols:
        gl[int(g[0])].append((int(g[3]) + int(g[4] or 0) / 10, g[2] == '1'))
    res = {g['rd']: g for g in G}
    imp = []
    for k in range(min(20, len(P))):
        if P[k]['pos'] == 'G':
            continue
        mon = gfo = gao = moff = gff = gaf = 0
        for rd, iv, st in campo:
            end = max([b for a, b in iv.values()] + [90]); m = iv.get(k)
            for t, us in gl.get(rd, []):
                dentro = m and m[0] <= t <= m[1]
                if dentro: gfo += us; gao += (not us)
                else: gff += us; gaf += (not us)
            mm = (m[1] - m[0]) if m else 0; mon += mm; moff += end - mm
        if mon >= 450:
            imp.append((P[k]['nome'], mon, gfo, gao, round((gfo - gao) / mon * 90 - ((gff - gaf) / moff * 90 if moff else 0), 2)))
    R['impacto'] = sorted(imp, key=lambda x: -x[4])
    du = defaultdict(lambda: [0, 0])
    for rd, iv, st in campo:
        g = res.get(rd)
        if not g:
            continue
        st = [x for x in st if x < 20 and P[x]['pos'] != 'G']
        for a in range(len(st)):
            for b in range(a + 1, len(st)):
                key = tuple(sorted((st[a], st[b]))); du[key][0] += 1; du[key][1] += pts(g)
    dd = [(P[a]['nome'], P[b]['nome'], n, p, round(p / n, 2)) for (a, b), (n, p) in du.items() if n >= 8]
    dd.sort(key=lambda x: -x[4])
    R['duplas_top'] = dd[:6]; R['duplas_piores'] = dd[-6:]
    # GPS do time
    tg = []
    for t in o['GPS']['games']:
        rd, td, _ = t.split('#')
        if td:
            a, b = [float(x.split()[0]) for x in td.split('/')]; tg.append((int(rd), a, b))
    if tg:
        R['gps_time'] = (round(stt.mean(x[1] for x in tg), 1), round(stt.mean(x[2] for x in tg), 1), len(tg))
    R['proximos'] = o.get('proximos', [])
    return R


def md(R, ant=None, rod=None):
    L = [f"# Resumo da rodada {rod}", ""]
    L += [f"**Posição:** {R['posicao']}º · {R['pts']} pts em {R['jogos']} jogos · {R['gp']}:{R['gc']}"]
    if ant:
        L += [f"**Antes:** {ant['posicao']}º · {ant['pts']} pts em {ant['jogos']} jogos · {ant['gp']}:{ant['gc']}"]
    L += [f"**Casa:** {R['casa']['pts']} pts em {R['casa']['j']} ({R['casa']['aprov']}%) · {R['casa']['gp']}:{R['casa']['gc']}",
          f"**Fora:** {R['fora']['pts']} pts em {R['fora']['j']} ({R['fora']['aprov']}%) · {R['fora']['gp']}:{R['fora']['gc']}",
          "**Últimos 5:** " + ' · '.join(f"R{a} {b} {c}" for a, b, c in R['ultimos5']), "", "## Tabela (vizinhos)"]
    L += [f"- {r[0]}º {r[1]} {r[8]} pts ({r[2]} j, {r[6]}:{r[7]})" for r in R['vizinhos']]
    L += ["", "## Formações", "| Formação | J | Pts | Pts/j | GP | GC |", "|---|---|---|---|---|---|"]
    L += [f"| {k} | {v[0]} | {v[1]} | {br(v[1] / v[0])} | {v[2]} | {v[3]} |" for k, v in R['formacoes']]
    x = R['xg']
    L += ["", "## Gols e xG",
          f"- A favor: {x['favor'][1]} gols / xG {br(x['favor'][0], 1)} ({x['favor'][2]} chutes) · casa {x['favor_casa'][1]}/{br(x['favor_casa'][0], 1)} · fora {x['favor_fora'][1]}/{br(x['favor_fora'][0], 1)}",
          f"- Contra: {x['contra'][1]} gols / xG {br(x['contra'][0], 1)} ({x['contra'][2]} chutes) · casa {x['contra_casa'][1]}/{br(x['contra_casa'][0], 1)} · fora {x['contra_fora'][1]}/{br(x['contra_fora'][0], 1)}",
          f"- Por faixa (0-15,16-30,31-45,46-60,61-75,76+): marcados {R['gols_faixa']['1']} · sofridos {R['gols_faixa']['0']}",
          f"- Tipo marcados: {R['gols_tipo']['1']} · sofridos: {R['gols_tipo']['0']} (a=trabalhada, c=escanteio, s=bola parada, k=falta, f=contra-ataque, p=pênalti, r=individual)",
          f"- De cabeça: marcados {R['gols_cabeca']['1']} · sofridos {R['gols_cabeca']['0']}",
          f"- Sofridos a partir dos 80': {R['gols_tarde_sofridos']}",
          f"- Primeiro gol: {R['primeiro_gol']}",
          f"- Esteve na frente e não venceu: {R['liderou_sem_vencer']}"]
    if R.get('gps_time'):
        L += ["", f"## GPS do time", f"- Média SPFC {br(R['gps_time'][0], 1)} km · adversários {br(R['gps_time'][1], 1)} km · {R['gps_time'][2]} jogos rastreados"]
    L += ["", "## Impacto em campo (saldo por 90 com o jogador − sem ele)"]
    L += [f"- {n}: {'+' if d >= 0 else ''}{br(d)} ({gf}:{ga} com ele, {m} min)" for n, m, gf, ga, d in R['impacto']]
    L += ["", "## Duplas titulares (8+ jogos)", "Melhores:"] + [f"- {a} + {b}: {p} pts em {n} ({br(r)}/j)" for a, b, n, p, r in R['duplas_top']]
    L += ["Piores:"] + [f"- {a} + {b}: {p} pts em {n} ({br(r)}/j)" for a, b, n, p, r in R['duplas_piores']]
    L += ["", "## Jogadores (ordem de minutos)", "| Jogador | Min | Nota | G | A | 3 zag. | 4 zag. | Casa | Fora | Últimas 3 | Melhor jogo |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda t: f"{br(t[0])} ({t[1]})" if t else '—'
    for j in R['jogadores'][:24]:
        L.append(f"| {j['nome']} | {j['min']} | {br(j['nota']) if j['nota'] else '—'} | {j['gols']} | {j['assist']} | {f(j['3z'])} | {f(j['4z'])} | {f(j['casa'])} | {f(j['fora'])} | {', '.join(br(v, 1) for v in j['ultimas3'])} | {('R' + str(j['melhor'][0]) + ' ' + j['melhor'][1] + ' ' + br(j['melhor'][2], 1)) if j['melhor'] else '—'} |")
    if ant:
        L += ["", "## O que mudou desde a rodada anterior (nota média, ≥ 0,05)"]
        an = {j['nome']: j for j in ant['jogadores']}
        for j in R['jogadores'][:24]:
            a = an.get(j['nome'])
            if a and a['nota'] and j['nota'] and abs(j['nota'] - a['nota']) >= 0.05:
                L.append(f"- {j['nome']}: {br(a['nota'])} → {br(j['nota'])}")
    L += ["", "## Próximos jogos"]
    for p in R['proximos']:
        L.append(f"- R{p['rd']} {'vs' if p['home'] else '@'} {p['opp']} · mando do adversário: {p.get('mandoAdv')} · desfalques SPFC: {', '.join(p['desfalquesSPFC']) or '—'} · desfalques adv.: {', '.join(p['desfalquesAdv']) or '—'} · artilheiros: {', '.join(p['artilheiros'])} · criadores: {', '.join(p['criadores'])} · stats: {p['stats']}")
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    o, oa = carregar(sys.argv[1] if len(sys.argv) > 1 else None)
    d = escrever_dados(o)
    R = analisar(o)
    RA = analisar(oa) if oa else None
    os.makedirs(DIR_REL, exist_ok=True)
    out = os.path.join(DIR_REL, f"resumo-rodada-{o['rodada']:02d}.md")
    open(out, 'w', encoding='utf-8').write(md(R, RA, o['rodada']))
    print('ok:', d, out)
