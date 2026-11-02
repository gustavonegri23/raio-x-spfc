import re,json,statistics as st,sys
s=open(sys.argv[1],encoding='utf8').read()
J=lambda k: json.loads(re.search(r'window\.'+k+r'=(.*?);\n',s,re.S).group(1))
SOFA=J('SOFA');GPS=J('GPS');SH=J('SHOTMAP')
P=SOFA['P'];F=SOFA['F']
def st_(p):
    v=p[4].split(',');return {F[i]:(float(x) if x not in('',None) else None) for i,x in enumerate(v)}
idx={i:p[0] for i,p in enumerate(P)}
EXCLUIR={'Enzo Díaz'}  # treina fora do elenco
P=[p if p[0] not in EXCLUIR else [p[0],p[1],p[2],p[3],','.join(['']*len(F)),p[5]] for p in P]
G=SOFA['G']; home={g[0]:g[2] for g in G}; res={g[0]:(g[4],g[5]) for g in G}
# GPS por jogo
gp={}
for t in GPS['games']:
    q=t.split('#');rd=int(q[0])
    if not q[1]:continue
    a,b=[float(x.split()[0]) for x in q[1].split('/')];gp[rd]=(a,b,q[2])
H=[gp[r] for r in gp if home.get(r)==1];A=[gp[r] for r in gp if home.get(r)==0]
print('GPS jogos casa',len(H),'fora',len(A))
print(' SP km casa %.1f fora %.1f | adv casa %.1f fora %.1f'%(st.mean(x[0] for x in H),st.mean(x[0] for x in A),st.mean(x[1] for x in H),st.mean(x[1] for x in A)))
tot=sum(x[0] for x in gp.values());print(' total SP km rastreado %.0f em %d jogos'%(tot,len(gp)))
# top speed por jogo (max), quem
best=[]
for rd,(a,b,rows) in gp.items():
    for z in rows.split():
        p=z.split(':')
        if len(p)>3 and p[3]:best.append((float(p[3]),idx[int(p[0])],rd,'casa' if home[rd] else 'fora')) if idx[int(p[0])] not in EXCLUIR else None
best.sort(reverse=True);print(' top velocidades',best[:5])
# season gps
gs=[]
for z in GPS['season'].split():
    a=z.split(':');i=int(a[0])
    if idx[i] in EXCLUIR: continue
    gs.append(dict(n=idx[i],km=float(a[1]) if a[1] else 0,spr=int(a[2]) if a[2] else 0,top=float(a[3]) if a[3] else 0,k90=float(a[6]) if a[6] else None,min=st_(P[i])['minutesPlayed'] or 0))
print(' km total top',sorted([(round(g['km'],1),g['n']) for g in gs],reverse=True)[:5])
print(' km/90 top',sorted([(g['k90'],g['n']) for g in gs if g['k90'] and g['min']>=450],reverse=True)[:6])
print(' top speed',sorted([(g['top'],g['n']) for g in gs if g['top']],reverse=True)[:6])
print(' sprints/90',sorted([(round(g['spr']/g['min']*90,1),g['n'],g['spr']) for g in gs if g['min']>=450],reverse=True)[:6])
# shotmap
sh=[SH[i:i+17] for i in range(0,len(SH),17)]
def agg(f):
    r=[x for x in sh if f(x)];return len(r),sum(int(x[8:10])/100 for x in r),sum(x[10]=='g' for x in r)
for m,lab in (('1','casa'),('0','fora')):
    for side,sl in (('1','SP'),('0','ADV')):
        n,xg,g=agg(lambda x:x[2]==m and x[3]==side)
        print(f' chutes {lab} {sl}: {n} xG {xg:.1f} gols {g}')
print(' tipos',sorted(set(x[10] for x in sh)), 'jogada',sorted(set(x[15] for x in sh)),'corpo',sorted(set(x[16] for x in sh)))
# distance of shots: x coord (00-99?) SP side
def far(x):return int(x[4:6])
for side in '10':
    xs=[far(x) for x in sh if x[3]==side];print(' x medio side',side, round(st.mean(xs),1), 'fora area(x>17?)')
# player ratings casa x fora from G lineups
from collections import defaultdict
rt=defaultdict(lambda:{'c':[],'f':[]})
for g in G:
    for z in g[7].split():
        a=z.split(':')
        if a[2] and idx[int(a[0])] not in EXCLUIR:rt[idx[int(a[0])]]['c' if g[2] else 'f'].append(float(a[2]))
diff=[(round(st.mean(v['c'])-st.mean(v['f']),2),k,round(st.mean(v['c']),2),round(st.mean(v['f']),2),len(v['c']),len(v['f'])) for k,v in rt.items() if len(v['c'])>=6 and len(v['f'])>=6]
diff.sort();print(' nota casa-fora (menor->maior)',diff[:4],'...',diff[-4:])
# goals minute casa/fora from G goal strings
gm={'c':[],'f':[]}
for g in G:
    for z in (g[8] or '').split(';'):
        if z: gm['c' if g[2] else 'f'].append(eval(z.split('|')[1]))
for k in gm: v=gm[k];print(' gols SP',k,len(v),'após 75min',sum(m>75 for m in v),'1ºT',sum(m<=45 for m in v))
# formations
from collections import Counter
print(' formações',Counter(g[6] for g in G).most_common(6))
# extra per player curios
for p in P:
    d=st_(p)
    if (d['minutesPlayed'] or 0)>=900:
        pass
top=lambda key,n=4,mn=900:sorted([(d[key],p[0]) for p in P for d in [st_(p)] if (d['minutesPlayed'] or 0)>=mn and d[key] is not None],reverse=True)[:n]
for k in ['successfulDribbles','tackles','ballRecovery','accurateLongBalls','dribbledPast','aerialDuelsWonPercentage','accuratePassesPercentage','keyPasses','touchesInOppBox','goalsFromOutsideTheBox','yellowCards']:
    print(' ',k,top(k))
