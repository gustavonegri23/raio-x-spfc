/*
  Coletor Raio-X SPFC · roda no navegador, numa aba aberta em https://www.sofascore.com
  Uso (pelo Claude, com a ferramenta javascript_tool do navegador do app):
    1) cole este arquivo inteiro e execute;
    2) await RX.tudo()            -> coleta tudo (leva de 2 a 6 minutos)
    3) RX.partes()                -> diz em quantos pedaços de 40.000 caracteres o resultado foi dividido
    4) RX.parte(0), RX.parte(1)…  -> devolve cada pedaço; junte todos, na ordem, num arquivo data/rodadas/rodada-NN.json
  Se a coleta passar do tempo limite da ferramenta, rode por etapas:
    await RX.e1(); await RX.e2(); await RX.e3(); await RX.e4(); RX.exportar();
*/
window.RX = (function () {
  const TEAM = 1981, UT = 325, SEASON = 87678; // São Paulo · Brasileirão Série A · 2026
  const j = u => fetch(u).then(r => r.ok ? r.json() : null).catch(() => null);
  const F = ['rating','appearances','matchesStarted','minutesPlayed','goals','assists','expectedGoals','expectedAssists','bigChancesCreated','bigChancesMissed','keyPasses','accuratePasses','accuratePassesPercentage','accurateFinalThirdPasses','accurateLongBalls','successfulDribbles','totalContest','tackles','interceptions','clearances','ballRecovery','totalDuelsWonPercentage','aerialDuelsWonPercentage','totalShots','shotsOnTarget','headedGoals','leftFootGoals','rightFootGoals','goalsFromOutsideTheBox','penaltyGoals','touchesInOppBox','accurateCrosses','totalCross','saves','savesPercentage','goalsConceded','cleanSheet','expectedGoalsConceded','kilometersCoveredPer90','topSpeed','defensiveContributions','yellowCards','errorLeadToGoal','dribbledPast'];
  const SIT = {'regular':'r','assisted':'a','fast-break':'f','corner':'c','set-piece':'s','free-kick':'k','penalty':'p','throw-in-set-piece':'t'};
  const BP = {'right-foot':'R','left-foot':'L','head':'H','other':'O'};
  const st = { players: [], idx: {}, events: [], games: [], log: [] };
  const say = m => { st.log.push(new Date().toISOString().slice(11,19) + ' ' + m); return m; };

  /* Etapa 1 · elenco, estatísticas da temporada e mapas de calor */
  async function e1() {
    const sq = await j(`/api/v1/team/${TEAM}/players`);
    const list = [];
    for (const it of sq.players) {
      const p = it.player;
      const s = await j(`/api/v1/player/${p.id}/unique-tournament/${UT}/season/${SEASON}/statistics/overall`);
      if (s && s.statistics && s.statistics.minutesPlayed >= 90) list.push({ p, s: s.statistics });
    }
    list.sort((a, b) => b.s.minutesPlayed - a.s.minutesPlayed);
    const GX = 16, GY = 10;
    for (const o of list) {
      const h = await j(`/api/v1/player/${o.p.id}/unique-tournament/${UT}/season/${SEASON}/heatmap/overall`);
      const pts = (h && h.points) || [], g = Array(GX * GY).fill(0);
      for (const q of pts) { const xi = Math.min(GX - 1, Math.floor(q.x / 100 * GX)), yi = Math.min(GY - 1, Math.floor(q.y / 100 * GY)); g[yi * GX + xi] += (q.count || 1); }
      const mx = Math.max(...g) || 1; o.hm = g.map(v => Math.round(v / mx * 9)).join('');
    }
    st.players = list; st.idx = {}; list.forEach((o, i) => st.idx[o.p.id] = i);
    return say('e1: ' + list.length + ' jogadores');
  }

  /* Etapa 2 · jogos do Brasileirão: escalação, nota, gols, chutes, formação, distância do time */
  async function e2() {
    let evs = [];
    for (let p = 0; p < 8; p++) { const r = await j(`/api/v1/team/${TEAM}/events/last/${p}`); if (!r) break; evs = evs.concat(r.events); if (!r.hasNextPage) break; }
    st.events = evs.filter(e => e.tournament?.uniqueTournament?.id === UT && e.season?.id === SEASON && e.status?.type === 'finished').sort((a, b) => a.roundInfo.round - b.roundInfo.round);
    st.games = [];
    for (const e of st.events) {
      const home = e.homeTeam.id === TEAM;
      const [lu, inc, sm, ts] = await Promise.all([j(`/api/v1/event/${e.id}/lineups`), j(`/api/v1/event/${e.id}/incidents`), j(`/api/v1/event/${e.id}/shotmap`), j(`/api/v1/event/${e.id}/statistics`)]);
      const side = lu ? (home ? lu.home : lu.away) : null;
      const pl = (side?.players || []).filter(x => x.statistics && x.statistics.minutesPlayed && st.idx[x.player.id] !== undefined)
        .map(x => ({ id: x.player.id, pos: x.position || '', r: x.statistics.rating || '', min: x.statistics.minutesPlayed, sub: x.substitute ? 1 : 0 }));
      const ev = inc?.incidents || [], shots = sm?.shotmap || [];
      let td = '';
      if (ts && ts.statistics) { const all = ts.statistics.find(s => s.period === 'ALL') || ts.statistics[0]; for (const gr of all.groups) for (const it of gr.statisticsItems) if (it.name === 'Distance covered') td = (home ? it.home : it.away) + '/' + (home ? it.away : it.home); }
      st.games.push({ e, home, side, pl, ev, shots, td,
        rd: e.roundInfo.round, ts: e.startTimestamp, opp: home ? (e.awayTeam.shortName || e.awayTeam.name) : (e.homeTeam.shortName || e.homeTeam.name),
        gf: home ? e.homeScore.current : e.awayScore.current, ga: home ? e.awayScore.current : e.homeScore.current, form: side?.formation || '' });
    }
    return say('e2: ' + st.games.length + ' jogos');
  }

  /* Etapa 3 · GPS por jogador por jogo */
  async function e3() {
    for (const g of st.games) {
      if (!g.td) { g.gps = ''; continue; }
      const rows = await Promise.all(g.pl.map(async x => {
        const a = await j(`/api/v1/event/${g.e.id}/player/${x.id}/statistics`); const s = a && a.statistics;
        if (!s || s.kilometersCovered == null) return null;
        return [st.idx[x.id], s.kilometersCovered, s.numberOfSprints ?? '', s.topSpeed ?? '', s.metersCoveredHighSpeedRunningKm ?? '', s.metersCoveredSprintingKm ?? ''].join(':');
      }));
      g.gps = rows.filter(Boolean).join(' ');
    }
    return say('e3: GPS ok');
  }

  /* Etapa 4 · próximos 5 adversários, desfalques e tabela casa/fora */
  async function e4() {
    const nx = await j(`/api/v1/team/${TEAM}/events/next/0`);
    const ev = (nx?.events || []).filter(e => e.tournament?.uniqueTournament?.id === UT).slice(0, 5);
    const stH = await j(`/api/v1/unique-tournament/${UT}/season/${SEASON}/standings/home`), stA = await j(`/api/v1/unique-tournament/${UT}/season/${SEASON}/standings/away`), stT = await j(`/api/v1/unique-tournament/${UT}/season/${SEASON}/standings/total`);
    const row = (s, id) => { const r = s?.standings?.[0]?.rows?.find(x => x.team.id === id); return r ? { pos: r.position, v: r.wins, e: r.draws, d: r.losses, gp: r.scoresFor, gc: r.scoresAgainst, pts: r.points } : null; };
    st.tabela = (stT?.standings?.[0]?.rows || []).map(r => [r.position, r.team.shortName || r.team.name, r.matches, r.wins, r.draws, r.losses, r.scoresFor, r.scoresAgainst, r.points]);
    st.proximos = [];
    for (const e of ev) {
      const home = e.homeTeam.id === TEAM, opp = home ? e.awayTeam : e.homeTeam;
      const [s, lu, tp] = await Promise.all([j(`/api/v1/team/${opp.id}/unique-tournament/${UT}/season/${SEASON}/statistics/overall`), j(`/api/v1/event/${e.id}/lineups`), j(`/api/v1/team/${opp.id}/unique-tournament/${UT}/season/${SEASON}/top-players/overall`)]);
      const T = tp?.topPlayers || {}, pick = (k, c = 3) => (T[k] || []).slice(0, c).map(x => x.player.shortName + ' ' + Math.round((x.statistics[k] ?? 0) * 100) / 100);
      const S = s?.statistics || {};
      st.proximos.push({ rd: e.roundInfo?.round, ts: e.startTimestamp, home, opp: opp.name,
        desfalquesSPFC: lu ? ((home ? lu.home : lu.away)?.missingPlayers || []).map(m => m.player.shortName + ' (' + m.type + ')') : [],
        desfalquesAdv: lu ? ((home ? lu.away : lu.home)?.missingPlayers || []).map(m => m.player.shortName + ' (' + m.type + ')') : [],
        mandoAdv: row(home ? stA : stH, opp.id),
        stats: Object.fromEntries(['matches','goalsScored','goalsConceded','averageBallPossession','bigChancesCreated','bigChancesAgainst','errorsLeadingToGoal','aerialDuelsWonPercentage','duelsWonPercentage','accuratePassesPercentage','fastBreakGoals','headedGoals','totalCrosses','cleanSheets'].map(k => [k, S[k] != null ? Math.round(S[k] * 100) / 100 : null])),
        artilheiros: pick('goals'), garcons: pick('assists'), notas: pick('rating'), criadores: pick('bigChancesCreated', 2) });
    }
    return say('e4: ' + st.proximos.length + ' próximos jogos');
  }

  /* Monta o JSON no formato que a página e o montar.py esperam */
  function exportar() {
    const P = st.players.map(o => [o.p.name, o.p.position, o.p.shirtNumber || o.p.jerseyNumber || '', o.p.dateOfBirthTimestamp ? new Date(o.p.dateOfBirthTimestamp * 1000).getUTCFullYear() : '', F.map(f => { const v = o.s[f]; return v == null ? '' : Math.round(v * 100) / 100; }).join(','), o.hm]);
    const G = st.games.map(g => {
      const goalsUs = g.ev.filter(i => i.incidentType === 'goal' && i.isHome === g.home).map(i => {
        const sh = g.shots.find(z => z.isHome === g.home && z.shotType === 'goal' && Math.abs(z.time - i.time) <= 1) || {};
        const who = i.player ? (st.idx[i.player.id] !== undefined && i.incidentClass !== 'ownGoal' ? st.idx[i.player.id] : i.player.shortName) : '';
        const as = i.assist1 ? (st.idx[i.assist1.id] !== undefined ? st.idx[i.assist1.id] : i.assist1.shortName) : '';
        return [who, i.time + (i.addedTime ? '+' + i.addedTime : ''), i.incidentClass, as, sh.bodyPart || '', sh.situation || '', sh.xg != null ? Math.round(sh.xg * 100) / 100 : '', sh.playerCoordinates ? Math.round(sh.playerCoordinates.x) : '', sh.playerCoordinates ? Math.round(sh.playerCoordinates.y) : ''].join('|');
      }).join(';');
      return [g.rd, g.ts, g.home ? 1 : 0, g.opp, g.gf, g.ga, g.form, g.pl.map(x => [st.idx[x.id], x.pos, x.r, x.min, x.sub].join(':')).join(' '), goalsUs];
    });
    const GPS = { season: st.players.map((o, i) => [i, o.s.kilometersCovered ?? '', o.s.numberOfSprints ?? '', o.s.topSpeed ?? '', o.s.metersCoveredHighSpeedRunning ?? '', o.s.metersCoveredSprinting ?? '', o.s.kilometersCoveredPer90 ? Math.round(o.s.kilometersCoveredPer90 * 100) / 100 : ''].join(':')).join(' '),
      games: st.games.map(g => g.rd + '#' + g.td + '#' + (g.gps || '')) };
    // SHOTMAP v2, 17 caracteres por chute: rodada(2) mando(1) lado(1) x(2) y(2) xg(2) tipo(1) minuto(2) jogador(2, '--' se adversário) jogada(1) corpo(1)
    const p2 = n => String(Math.max(0, Math.min(99, Math.round(n || 0)))).padStart(2, '0');
    let SHOTMAP = '';
    for (const g of st.games) for (const s of g.shots) {
      const us = s.isHome === g.home ? 1 : 0;
      const pl = us && st.idx[s.player?.id] !== undefined ? p2(st.idx[s.player.id]) : '--';
      SHOTMAP += p2(g.rd) + (g.home ? 1 : 0) + us + p2(s.playerCoordinates?.x) + p2(s.playerCoordinates?.y) + p2((s.xg || 0) * 100) + ((s.shotType || 'm')[0]) + p2(s.time) + pl + (SIT[s.situation] || '?') + (BP[s.bodyPart] || '?');
    }
    // gols de todos (a favor e contra) e minutos em campo, para o diagnóstico de gols e as duplas
    const GOLS = [], CAMPO = [];
    for (const g of st.games) {
      const ev = g.ev; const end = Math.min(130, Math.max(90, ...ev.filter(i => ['goal', 'substitution', 'card'].includes(i.incidentType)).map(i => (i.time || 0) + (i.addedTime > 0 ? i.addedTime : 0))));
      ev.filter(i => i.incidentType === 'goal').forEach(i => {
        const us = i.isHome === g.home ? 1 : 0, sh = g.shots.find(z => z.shotType === 'goal' && z.isHome === i.isHome && Math.abs(z.time - i.time) <= 1);
        GOLS.push([g.rd, g.home ? 1 : 0, us, i.time, i.addedTime || 0, i.incidentClass, i.player ? (us && i.incidentClass !== 'ownGoal' && st.idx[i.player.id] !== undefined ? st.players[st.idx[i.player.id]].p.name : i.player.shortName) : '', i.assist1 ? (st.idx[i.assist1.id] !== undefined ? st.players[st.idx[i.assist1.id]].p.name : i.assist1.shortName) : '', sh ? (SIT[sh.situation] || '?') : (i.incidentClass === 'penalty' ? 'p' : '?'), sh ? (BP[sh.bodyPart] || '?') : '?', sh ? Math.round(sh.playerCoordinates?.x) : '', sh ? Math.round((sh.xg || 0) * 100) : '', g.gf, g.ga].join('|'));
      });
      const on = {};
      (g.side?.players || []).forEach(p => { const k = st.idx[p.player.id]; if (k !== undefined && !p.substitute) on[k] = [0, end]; });
      ev.filter(i => i.incidentType === 'substitution' && i.isHome === g.home).forEach(i => { const t = i.time + (i.addedTime || 0), ki = st.idx[i.playerIn?.id], ko = st.idx[i.playerOut?.id]; if (ko !== undefined && on[ko]) on[ko][1] = t; if (ki !== undefined) on[ki] = [t, end]; });
      ev.filter(i => i.incidentType === 'card' && (i.incidentClass === 'red' || i.incidentClass === 'yellowRed') && i.isHome === g.home).forEach(i => { const k = st.idx[i.player?.id]; if (k !== undefined && on[k]) on[k][1] = i.time; });
      CAMPO.push(g.rd + '#' + Object.entries(on).map(([k, v]) => k + ':' + v[0] + ':' + v[1]).join(' ') + '#' + ((g.side?.players || []).filter(p => !p.substitute).map(p => st.idx[p.player.id]).filter(x => x !== undefined).join(',')));
    }
    const rodada = Math.max(...st.games.map(g => g.rd));
    const out = { rodada, coletado: new Date().toISOString(), SOFA: { F, P, G }, GPS, SHOTMAP, GOLS, CAMPO, tabela: st.tabela || [], proximos: st.proximos || [] };
    st.out = JSON.stringify(out);
    return say('exportar: rodada ' + rodada + ', ' + st.out.length + ' caracteres');
  }
  async function tudo() { await e1(); await e2(); await e3(); await e4(); return exportar(); }
  const N = 40000;
  return { e1, e2, e3, e4, exportar, tudo, partes: () => Math.ceil((st.out || '').length / N), parte: i => (st.out || '').slice(i * N, (i + 1) * N), log: () => st.log, _st: st };
})();
'RX pronto: rode await RX.tudo()';
