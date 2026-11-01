#!/usr/bin/env python3
"""
Raio-X SPFC · validar.py
Checagens automáticas de uma coleta antes de publicar. O montar.py chama este módulo
e para se houver ERRO (a não ser que receba --forcar). AVISO não bloqueia, mas vai para o resumo.

Uso direto:  python3 ferramentas/validar.py            (rodada mais recente)
             python3 ferramentas/validar.py 34
Só usa a biblioteca padrão do Python.
"""
import json, os, sys, glob
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_ROD = os.path.join(RAIZ, 'data', 'rodadas')
CHAVES = ['rodada', 'coletado', 'SOFA', 'GPS', 'SHOTMAP', 'GOLS', 'CAMPO', 'tabela', 'proximos']


def validar(o, ant=None):
    """Devolve (erros, avisos), listas de frases em português."""
    E, A = [], []
    falta = [k for k in CHAVES if k not in o]
    if falta:
        E.append('Campos ausentes na coleta: ' + ', '.join(falta) + '.')
        return E, A
    if o.get('incompleto'):
        A.append('Coleta marcada como incompleta pelo coletor: faltou ' + ', '.join(o['incompleto']) + '.')

    G = o['SOFA']['G']
    rds = [g[0] for g in G]
    rod = o['rodada']
    # 1. rodadas únicas, rodada nova presente
    dup = [r for r, n in Counter(rds).items() if n > 1]
    if dup:
        E.append(f'Rodadas duplicadas nos jogos: {dup}.')
    if rod not in rds:
        E.append(f'A rodada {rod} não está entre os jogos coletados.')
    faltam = sorted(set(range(1, rod + 1)) - set(rds))
    if faltam:
        A.append(f'Rodadas sem jogo coletado (adiado ou falha): {faltam}.')
    if ant and rod <= ant['rodada']:
        E.append(f'A rodada coletada ({rod}) não é posterior à anterior ({ant["rodada"]}).')

    # 2. gols de GOLS batem com o placar de cada jogo
    gols = [x.split('|') for x in o['GOLS']]
    pg = defaultdict(lambda: [0, 0])
    for g in gols:
        pg[int(g[0])][0 if g[2] == '1' else 1] += 1
    for g in G:
        a, b = pg.get(g[0], [0, 0])
        if (a, b) != (g[4], g[5]):
            E.append(f'R{g[0]} {g[3]}: placar {g[4]}x{g[5]}, mas a lista de gols tem {a}x{b}.')

    # 3. SHOTMAP bem formado e coerente com o placar
    S = o['SHOTMAP']
    if len(S) % 17:
        E.append(f'SHOTMAP com {len(S)} caracteres, não é múltiplo de 17 (formato v2).')
    else:
        sh = [S[i:i + 17] for i in range(0, len(S), 17)]
        gs = defaultdict(lambda: [0, 0])
        for s in sh:
            if s[10] == 'g':
                gs[int(s[0:2])][0 if s[3] == '1' else 1] += 1
        for g in G:
            # gol contra não aparece como chute do autor: o mapa pode ter menos gols, nunca mais
            a, b = gs.get(g[0], [0, 0])
            if a > g[4] or b > g[5]:
                E.append(f'R{g[0]} {g[3]}: o mapa de chutes tem {a}x{b} gols, mais que o placar {g[4]}x{g[5]}.')
            elif (a, b) != (g[4], g[5]):
                A.append(f'R{g[0]} {g[3]}: mapa de chutes com {a}x{b} gols para placar {g[4]}x{g[5]} (gol contra ou chute sem registro).')
        xg = [int(s[8:10]) for s in sh]
        if any(v > 99 for v in xg):
            E.append('xG acima de 0,99 em algum chute.')

    # 4. escalações: 11 titulares, minutos e notas plausíveis
    # só a rodada nova: rodadas antigas têm jogadores que já saíram do elenco e não são coletados
    for c in o['CAMPO']:
        rd, on, st = c.split('#')
        n = len([x for x in st.split(',') if x != ''])
        if int(rd) == rod and n != 11:
            A.append(f'R{rd}: {n} titulares identificados no elenco coletado (esperado 11).')
    for g in G:
        for t in (g[7].split() if g[7] else []):
            q = t.split(':')
            r = float(q[2]) if q[2] else None
            m = int(q[3])
            if r is not None and not (3 <= r <= 10):
                E.append(f'R{g[0]}: nota fora da escala ({r}).')
            if m > 130:
                E.append(f'R{g[0]}: jogador com {m} minutos.')

    # 5. tabela confere com a campanha calculada
    pts = sum(3 if g[4] > g[5] else 1 if g[4] == g[5] else 0 for g in G)
    sp = next((r for r in o['tabela'] if r[1] == 'São Paulo'), None)
    if not sp:
        E.append('São Paulo não encontrado na tabela.')
    else:
        if sp[2] != len(G):
            E.append(f'Tabela diz {sp[2]} jogos; a coleta tem {len(G)}.')
        if sp[8] != pts:
            E.append(f'Tabela diz {sp[8]} pontos; os resultados coletados somam {pts}.')
        if (sp[6], sp[7]) != (sum(g[4] for g in G), sum(g[5] for g in G)):
            E.append('Gols pró/contra da tabela não batem com a soma dos jogos.')

    # 6. próximos jogos
    if not o['proximos'] and rod < 38:
        A.append('Nenhum próximo jogo coletado (etapa 4 pode ter falhado).')
    # 7. GPS
    gps = [x for x in o['GPS'].get('games', []) if x.split('#')[1]]
    if len(gps) < len(G) * 0.6:
        A.append(f'GPS em só {len(gps)} de {len(G)} jogos.')
    return E, A


def carregar(n=None):
    arqs = sorted(glob.glob(os.path.join(DIR_ROD, 'rodada-*.json')))
    alvo = arqs[-1] if n is None else os.path.join(DIR_ROD, f'rodada-{int(n):02d}.json')
    i = arqs.index(alvo) if alvo in arqs else -1
    ant = json.load(open(arqs[i - 1], encoding='utf-8')) if i > 0 else None
    return json.load(open(alvo, encoding='utf-8')), ant


if __name__ == '__main__':
    o, ant = carregar(sys.argv[1] if len(sys.argv) > 1 else None)
    E, A = validar(o, ant)
    for x in E:
        print('ERRO  ', x)
    for x in A:
        print('AVISO ', x)
    print(f'rodada {o["rodada"]}: {len(E)} erro(s), {len(A)} aviso(s)')
    sys.exit(1 if E else 0)
