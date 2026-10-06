from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd,numpy as np,json,re
from scipy.optimize import brentq
P=Path(__file__).resolve().parents[1];R=P/'raw';D=P/'data'
# Parse dated official Federal Reserve table, omit NA days.
s=BeautifulSoup((R/'fed_fx.txt').read_text(),'html.parser');out=[]
for row in s.find('table').find_all('tr'):
 c=[e.get_text(' ',strip=True) for e in row.find_all(['td','th'])]
 if len(c)>=2:
  try:out.append((pd.to_datetime(c[0],format='%d-%b-%y'),float(c[1])))
  except (ValueError,TypeError):pass
f=pd.DataFrame(out,columns=['date','CNY_per_USD']).set_index('date').sort_index();f.to_csv(D/'fed_usdcny_daily.csv')
annual=[]
for n,name in [('msci_v','MSCI World Value'),('msci_qnet','MSCI World Quality')]:
 txt=(R/(n+'.txt')).read_text();rr=re.findall(r'\b(20(?:1[2-9]|2[0-5]))\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)',txt)
 for y,a,b in rr:
  annual.append({'year':int(y),'name':name,'usd_net_return':float(a)/100})
  if n=='msci_v':annual.append({'year':int(y),'name':'MSCI World','usd_net_return':float(b)/100})
a=pd.DataFrame(annual).query('year>=2013').copy()
for i,row in a.iterrows():
 st=f.loc[:str(int(row.year)-1)+'-12-31'].iloc[-1,0];en=f.loc[:str(int(row.year))+'-12-31'].iloc[-1,0]
 a.loc[i,'fx_return']=en/st-1;a.loc[i,'cny_net_before_channel_costs']=(1+row.usd_net_return)*en/st-1
a=a.sort_values(['name','year']);a.to_csv(D/'overseas_msci_annual_usd_cny.csv',index=False,encoding='utf-8-sig')
summary=[]
for name,g in a.groupby('name'):
 summary.append({'name':name,'period':'2012-12-31→2025-12-31','usd_cagr':float((1+g.usd_net_return).prod()**(1/len(g))-1),'cny_cagr_before_channel_costs':float((1+g.cny_net_before_channel_costs).prod()**(1/len(g))-1)})
st=f.loc[:'2016-06-30'].iloc[-1,0];en=f.loc[:'2026-06-30'].iloc[-1,0];u=[]
for name,r in [('IVE',.1173),('IWD',.1133),('IVV',.1547)]:u.append({'name':name,'start':'2016-06-30','end':'2026-06-30','USD_CAGR':r,'CNY_CAGR_before_channel_costs':float(((1+r)**10*en/st)**.1-1),'fx_start':float(st),'fx_end':float(en)})
pd.DataFrame(u).to_csv(D/'overseas_etf_usd_cny_10y.csv',index=False,encoding='utf-8-sig');(D/'overseas_summary.json').write_text(json.dumps({'msci_annual':summary,'etf_10y':u},ensure_ascii=False,indent=2))
# Secondary market history with units cross-checked against latest quote amount.
j=json.loads((R/'tencent_price.txt').read_text());z=pd.DataFrame(j['data']['sz159263']['day'],columns=['date','open','close','high','low','volume_lots']);z['date']=pd.to_datetime(z.date);z=z.set_index('date').astype(float).loc[:'2026-09-30'];z.to_csv(D/'etf_159263_market_price_daily.csv',encoding='utf-8-sig')
nav=pd.read_csv(D/'etf_159263_nav_daily.csv',index_col=0,parse_dates=True).iloc[:,0];z=z.join(nav.rename('nav'),how='inner');z['premium']=z.close/z.nav-1;z['approx_turnover_yuan']=z.close*z.volume_lots*100;z.to_csv(D/'etf_price_nav_premium.csv',encoding='utf-8-sig')
tr=pd.read_csv(D/'domestic_total_return_daily.csv',index_col=0,parse_dates=True);m=tr.groupby(tr.index.to_period('M')).tail(1).pct_change().dropna();m.corr().to_csv(D/'monthly_correlation_full.csv',encoding='utf-8-sig');tr.loc['2024-10-29':].pct_change().corr().to_csv(D/'daily_correlation_recent.csv',encoding='utf-8-sig')
cons=pd.read_csv(D/'constituents_20260930.csv',dtype={'样本代码':str}).set_index('样本代码');g=pd.read_excel(R/'growth_cons2.bin');g['样本代码']=g['样本代码'].astype(str).str.zfill(6);g.to_csv(D/'growth_constituents_20260930.csv',index=False,encoding='utf-8-sig')
csi=pd.read_excel(R/'csi300cons3.bin');csi['成份券代码Constituent Code']=csi['成份券代码Constituent Code'].astype(str).str.zfill(6);csi.to_csv(D/'csi300_constituents.csv',index=False,encoding='utf-8-sig');cs=set(csi['成份券代码Constituent Code']);shared=cons.index.intersection(cs)
growthshared=cons.index.intersection(g['样本代码'])
def model(pe0=8.3532,g=.02,pay=.4,pe1=8,n=10):
 u=1/pe0;e=1
 for k in range(1,n+1):
  e*=1+g;pe=pe0*(pe1/pe0)**(k/n);price=e*pe;u*=1+pay/pe
 return (u*price*.998**n)**(1/n)-1
avg=5944990.87*365/(181*.0015)
ann=pd.read_csv(D/'annual_returns.csv',index_col=0);logs=np.log1p(ann['价值100']);tops=logs.nlargest(3)
extra={'csi300_shared_names':len(shared),'value100_weight_in_csi300':float(cons.loc[shared,'权重（%）'].sum()),'growth_shared_names':len(growthshared),'required_eps_growth_for_8pct_in_base':brentq(lambda x:model(g=x)-.08,-.1,.2),'required_start_pe_for_8pct_in_base':brentq(lambda x:model(pe0=x)-.08,2,20),'dividend_halving_stagnation_pe6':{str(n):model(g=0,pay=.2,pe1=6,n=n) for n in [5,10]},'fund_avg_nav_from_management_fee':avg,'fund_half_year_turnover_min_buy_sell_over_avg_nav':min(10084088735.12,7166778460.59)/avg,'reported_equity_trading_fee_over_avg_nav':6307198.06/avg,'latest_price':float(z.close.iloc[-1]),'latest_premium':float(z.premium.iloc[-1]),'premium_max_abs':float(z.premium.abs().max()),'approx_20day_turnover_yuan':float(z.approx_turnover_yuan.tail(20).mean()),'top3_years_log_growth_share':float(tops.sum()/logs.sum()),'top3_years':list(map(int,tops.index)),'current_index_drawdown':float(tr['价值100'].iloc[-1]/tr['价值100'].max()-1)}
(D/'supplement.json').write_text(json.dumps(extra,ensure_ascii=False,indent=2))
# Dated illustrative company evidence. OCF is consolidated and not directly distributable cash to ordinary shareholders.
financial=[{'code':'000651','name':'格力电器','weight_pct':7.96,'financial_date':'2026-06-30','net_profit_bn':13.27759088257,'net_profit_yoy':-.0787,'ocf_bn':18.80883239246,'ocf_yoy':-.3360,'revenue_yoy':-.0815,'source':'S33'}, {'code':'000921','name':'海信家电','weight_pct':7.77,'financial_date':'2026-06-30','net_profit_bn':1.65802837134,'net_profit_yoy':-.2016,'ocf_bn':3.23512708888,'ocf_yoy':-.3921,'revenue_yoy':-.0522,'source':'S31'}, {'code':'002508','name':'老板电器','weight_pct':4.35,'financial_date':'2026-06-30','net_profit_bn':.57823510190,'net_profit_yoy':-.1875,'ocf_bn':-.36229092591,'ocf_yoy':-1.7087,'revenue_yoy':-.1378,'source':'S32'}, {'code':'601166','name':'兴业银行','weight_pct':7.03,'financial_date':'2026-06-30','net_profit_bn':41.131,'net_profit_yoy':-.0466,'ocf_bn':None,'ocf_yoy':None,'revenue_yoy':-.0025,'source':'S36'}, {'code':'600104','name':'上汽集团','weight_pct':4.97,'financial_date':'2026-06-30','net_profit_bn':5.15231816171,'net_profit_yoy':-.1438,'ocf_bn':54.30287792042,'ocf_yoy':1.5813,'revenue_yoy':None,'source':'S34/S35'}]
pd.DataFrame(financial).to_csv(D/'company_evidence_20260630.csv',index=False,encoding='utf-8-sig')
common=pd.read_csv(D/'fund_index_comparison.csv',index_col=0,parse_dates=True).loc['2025-09-23':]
rows=[{'object':c,'start':'2025-09-23 closing','end':'2026-09-30','cumulative':float(common[c].iloc[-1]/common[c].iloc[0]-1)} for c in common]
rows += [{'object':'联接A025497','start':'2025-09-23成立（1.0000）','end':'2026-09-30','cumulative':.0805},{'object':'联接C025498','start':'2025-09-23成立（1.0000）','end':'2026-09-30','cumulative':.0772}]
pd.DataFrame(rows).to_csv(D/'feeder_common_period.csv',index=False,encoding='utf-8-sig')
print('Saved supplemental calculations and financial evidence.')
