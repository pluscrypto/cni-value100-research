from pathlib import Path
import json,re,math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'raw'; DATA=ROOT/'data';DATA.mkdir(exist_ok=True)
CUTOFF=pd.Timestamp('2026-09-30');LIVE=pd.Timestamp('2024-10-29')
def cni(path):
    j=json.loads((RAW/path).read_text()); d=pd.DataFrame(j['data']['data'],columns=j['data']['item']);d['date']=pd.to_datetime(d['timestamp']);return d.set_index('date')['close'].astype(float).sort_index().loc[:CUTOFF]
def csi(path):
    j=json.loads((RAW/path).read_text());d=pd.DataFrame(j['data']);d['date']=pd.to_datetime(d.tradeDate);return d.set_index('date')['close'].astype(float).sort_index().loc[:CUTOFF]
TR={
 '价值100':cni('history_480081.json'),'自由现金流':cni('history_480092.json'),
 '沪深300':csi('csi_H00300.json'),'中证全指':csi('csi_H00985.json'),
 '300价值':csi('csi_H00919.json'),'中证红利':csi('csi_H00922.json'),
 '红利低波':csi('csi_H20269.json'),'红利质量':csi('csi_qtri.txt')}
PR={'价值100':cni('histo.txt'),'自由现金流':cni('history_980092.json'),'沪深300':csi('csi_000300_full.txt'),'中证全指':csi('csi_000985.json'),'300价值':csi('csi_000919.json'),'中证红利':csi('csi_000922.json'),'红利低波':csi('csi_H30269.json'),'红利质量':csi('csi_931468.json')}
# The CNI trading calendar is the primary valid-date set. Discard CSI-only 2018-06-18, an A-share holiday.
calendar=TR['价值100'].index
tr=pd.DataFrame({k:s.reindex(calendar) for k,s in TR.items()}).dropna()
pr=pd.DataFrame({k:s.reindex(calendar) for k,s in PR.items()}).dropna()
tr.to_csv(DATA/'domestic_total_return_daily.csv',encoding='utf-8-sig');pr.to_csv(DATA/'domestic_price_daily.csv',encoding='utf-8-sig')

def episodes(s):
    s=s.dropna(); h=s.cummax(); dd=s/h-1; out=[]; peak=s.index[0];start=None;trough=None
    for d in s.index:
        if dd.loc[d]>=-1e-12:
            if start is not None:
                out.append({'peak':str(peak.date()),'trough':str(trough.date()),'recovery':str(d.date()),'depth':float(dd.loc[trough]),'underwater_days':(d-peak).days,'recovery_after_trough_days':(d-trough).days,'censored':False})
            peak=d;start=None;trough=None
        else:
            if start is None:start=d;trough=d
            if dd.loc[d]<dd.loc[trough]:trough=d
    if start is not None:out.append({'peak':str(peak.date()),'trough':str(trough.date()),'recovery':None,'depth':float(dd.loc[trough]),'underwater_days':(s.index[-1]-peak).days,'recovery_after_trough_days':None,'censored':True})
    return sorted(out,key=lambda x:x['depth'])
def stats(s):
    s=s.dropna();yrs=(s.index[-1]-s.index[0]).days/365.2425;dd=s/s.cummax()-1; es=episodes(s);worst=es[0] if es else {}
    return {'start':str(s.index[0].date()),'end':str(s.index[-1].date()),'n':len(s),'years':yrs,'total':float(s.iloc[-1]/s.iloc[0]-1),'cagr':float((s.iloc[-1]/s.iloc[0])**(1/yrs)-1),'vol':float(s.pct_change().dropna().std(ddof=1)*np.sqrt(252)),'mdd':float(dd.min()),'worst_episode':worst,'longest_underwater':max(es,key=lambda x:x['underwater_days']) if es else {}}
rows=[]
for label,frame in [('full_backtest_mixed',tr),('post_20241029',tr.loc[LIVE:]),('last_5y',tr.loc['2021-09-30':])]:
    for n in frame:rows.append({'period':label,'name':n,**stats(frame[n])})
pd.DataFrame([{k:v for k,v in r.items() if not isinstance(v,dict)} for r in rows]).to_csv(DATA/'performance_metrics.csv',index=False,encoding='utf-8-sig')
monthly=tr.groupby(tr.index.to_period('M')).tail(1)
rollrows=[];summary=[]
for h in [12,36,60,120]:
    rr=monthly/monthly.shift(h)-1
    for name in tr:
        s=rr[name].dropna();a=(1+s)**(12/h)-1
        rel=s-rr['沪深300'].reindex(s.index)
        summary.append({'name':name,'horizon_years':h/12,'windows':len(s),'min_cumulative':float(s.min()),'max_cumulative':float(s.max()),'median_annualized':float(a.median()),'min_annualized':float(a.min()),'max_annualized':float(a.max()),'loss_share':float((s<0).mean()),'beat_300_share':float((rel>0).mean()),'approx_nonoverlap':int((len(monthly)-1)//h)})
        for i,dt in enumerate(s.index):
            loc=monthly.index.get_loc(dt);st=monthly.index[loc-h]
            rollrows.append({'name':name,'years':h/12,'start':str(st.date()),'end':str(dt.date()),'cumulative':float(s.loc[dt]),'annualized':float(a.loc[dt]),'excess_cumulative_vs_300':float(rel.loc[dt])})
pd.DataFrame(summary).to_csv(DATA/'rolling_summary.csv',index=False,encoding='utf-8-sig');pd.DataFrame(rollrows).to_csv(DATA/'rolling_windows.csv',index=False,encoding='utf-8-sig')
annual=tr.groupby(tr.index.to_period('Y')).tail(1).pct_change().dropna();annual.index=annual.index.year;annual.to_csv(DATA/'annual_returns.csv',encoding='utf-8-sig')
relative={name:stats(tr['价值100']/tr[name]) for name in tr if name!='价值100'}
pd.DataFrame(relative).T.to_json(DATA/'relative_stats.json',force_ascii=False,indent=2)
pd.DataFrame(episodes(tr['价值100'])).to_csv(DATA/'drawdown_episodes.csv',index=False,encoding='utf-8-sig')

# Dividend reinvestment wedge: log(TR ratio)-log(PR ratio); not a corporate earnings attribution.
wedges=[]
for period in [('all',tr.index[0]),('post_20241029',LIVE),('last5y',pd.Timestamp('2021-09-30'))]:
    name,st=period;t=TR['价值100'].loc[st:];p=PR['价值100'].reindex(t.index);y=(t.index[-1]-t.index[0]).days/365.2425
    tc=t.iloc[-1]/t.iloc[0];pc=p.iloc[-1]/p.iloc[0];w=tc/pc
    wedges.append({'period':name,'start':str(t.index[0].date()),'end':str(t.index[-1].date()),'tr_cagr':tc**(1/y)-1,'pr_cagr':pc**(1/y)-1,'reinvestment_log_contribution_per_year':math.log(w)/y,'reinvestment_geometric_wedge':w**(1/y)-1,'total_wedge':w-1})
pd.DataFrame(wedges).to_csv(DATA/'dividend_wedge.csv',index=False,encoding='utf-8-sig')

# Same initial capital 1. Cash earns assumed 1.5% effective annual; 12 monthly purchases first trading day.
# DCA means reserved initial cash, not salary contributions. No fees, use gross TRI, valuations at same final date.
schedule=[]
for h in [36,60,120]:
 for i in range(len(monthly)-h):
    st=monthly.index[i];en=monthly.index[i+h];s=tr['价值100'].loc[st:en]; endprice=s.iloc[-1]
    choices={'lump':[st], '4quarter':[st]+[s.index[s.index>=st+pd.DateOffset(months=m)][0] for m in [3,6,9]],'12monthly':[st]+[s.index[s.index>=st+pd.DateOffset(months=m)][0] for m in range(1,12)]}
    out={'years':h/12,'start':str(st.date()),'end':str(en.date())}
    for label,dates in choices.items():
      cash=1.;units=0.;prev=st
      for d in dates:
        cash*=1.015**((d-prev).days/365.2425);part=1./len(dates);units+=part/s.loc[d];cash-=part;prev=d
      cash*=1.015**((en-prev).days/365.2425);out[label]=float(units*endprice+cash-1)
    schedule.append(out)
pd.DataFrame(schedule).to_csv(DATA/'entry_path_windows.csv',index=False,encoding='utf-8-sig')
entry=pd.DataFrame(schedule);es=[]
for h,g in entry.groupby('years'):
 for k in ['lump','4quarter','12monthly']:
  es.append({'years':h,'strategy':k,'windows':len(g),'median_cumulative':float(g[k].median()),'min_cumulative':float(g[k].min()),'loss_share':float((g[k]<0).mean()),'beats_lump_share':float((g[k]>g.lump+1e-10).mean()) if k!='lump' else None})
pd.DataFrame(es).to_csv(DATA/'entry_path_summary.csv',index=False,encoding='utf-8-sig')

# Real ETF NAV history; no distributions through cutoff as independently checked on sponsor page.
txt=(RAW/'fundnav.txt').read_text();nav=json.loads(re.search(r'var Data_netWorthTrend\s*=\s*(\[.*?\]);',txt).group(1));nav=pd.DataFrame(nav);nav['date']=pd.to_datetime(nav.x,unit='ms',utc=True).dt.tz_convert('Asia/Shanghai').dt.tz_localize(None).dt.normalize();nav=nav.set_index('date').y.astype(float).sort_index().loc[:CUTOFF]
nav.to_csv(DATA/'etf_159263_nav_daily.csv',encoding='utf-8-sig')
fundstats=stats(nav);fundperiod=pd.concat([nav.rename('ETF净值'),TR['价值100'].reindex(nav.index).rename('指数全收益'),PR['价值100'].reindex(nav.index).rename('指数价格')],axis=1).dropna();fundperiod.to_csv(DATA/'fund_index_comparison.csv',encoding='utf-8-sig')
fs={k:stats(fundperiod[k]) for k in fundperiod}; deviations=fundperiod['ETF净值'].pct_change()-fundperiod['指数全收益'].pct_change();fs['calculated_te_total_return']=float(deviations.dropna().std()*np.sqrt(252))

cons=pd.read_csv(DATA/'constituents_20260930.csv',dtype={'样本代码':str});w=cons['权重（%）']/100;sector=cons.groupby('所属行业')['权重（%）'].sum().sort_values(ascending=False);sector.to_csv(DATA/'sector_weights_20260930.csv',encoding='utf-8-sig');top=cons.sort_values('权重（%）',ascending=False)
fc=pd.read_excel(RAW/'fcf_cons.bin');fc['样本代码']=fc['样本代码'].astype(str).str.zfill(6);fc.to_csv(DATA/'fcf_constituents_20260930.csv',index=False,encoding='utf-8-sig');a=cons.set_index('样本代码')['权重（%）']/100;b=fc.set_index('样本代码')['权重（%）']/100;idx=a.index.union(b.index);overlap=float(np.minimum(a.reindex(idx).fillna(0),b.reindex(idx).fillna(0)).sum());shared=len(a.index.intersection(b.index))
cons_summary={'top10_weight':float(top.head(10)['权重（%）'].sum()),'top3_weight':float(top.head(3)['权重（%）'].sum()),'hhi':float((w**2).sum()),'effective_count':float(1/(w**2).sum()),'sector_weights':sector.to_dict(),'fcf_shared_names':shared,'fcf_weight_overlap':overlap}

# Exact buy-and-hold model, constant annual payout fraction of earnings (not including buybacks).
PE0=8.3532;scenarios=[]
for label,g,payout,pe1 in [('悲观',-0.02,0.30,6.0),('基准',0.02,0.40,8.0),('乐观',0.05,0.45,10.0)]:
 for years in [5,10]:
  wealth=1.;price0=PE0;units=1/price0;earnings=1.
  for k in range(1,years+1):
   earnings*=1+g;pe=PE0*(pe1/PE0)**(k/years);price=earnings*pe;units*=1+payout*earnings/price
  terminal=units*price*(1-.002)**years
  scenarios.append({'scenario':label,'years':years,'eps_growth':g,'payout':payout,'starting_pe':PE0,'terminal_pe':pe1,'initial_dividend_yield':payout/PE0,'cumulative_return':terminal-1,'annualized_return':terminal**(1/years)-1,'cost_assumption':.002})
pd.DataFrame(scenarios).to_csv(DATA/'scenario_returns.csv',index=False,encoding='utf-8-sig')
# Shock sensitivity same model; payout separate from EPS growth already net of repurchases.
sens=[]
for g in [-.05,-.02,0,.02,.05]:
 for pe1 in [5,6,8,10,12]:
  units=1/PE0;earn=1
  for k in range(1,11):
   earn*=1+g;pe=PE0*(pe1/PE0)**(k/10);price=earn*pe;units*=1+.4/pe
  sens.append({'eps_growth':g,'terminal_pe':pe1,'cagr':(units*price*(1-.002)**10)**.1-1})
pd.DataFrame(sens).to_csv(DATA/'scenario_sensitivity.csv',index=False,encoding='utf-8-sig')

payload={'metrics':rows,'rolling':summary,'relative':relative,'dividend_wedge':wedges,'fund':fs,'constituents':cons_summary,'entry':es,'scenarios':scenarios,'qa':{'domestic_common_rows':len(tr),'common_start':str(tr.index[0].date()),'common_end':str(tr.index[-1].date()),'weights_sum':float(w.sum()),'duplicates':int(tr.index.duplicated().sum()),'missing_after_alignment':int(tr.isna().sum().sum()),'calendar_removed_csi_only_dates':sorted(set(TR['沪深300'].index.strftime('%Y-%m-%d'))-set(calendar.strftime('%Y-%m-%d'))) }}
(DATA/'reviewed.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False))
print(json.dumps(payload,ensure_ascii=False,indent=2))
