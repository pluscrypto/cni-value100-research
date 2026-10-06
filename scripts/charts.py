from pathlib import Path
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
P=Path(__file__).resolve().parents[1];D=P/'data';O=P/'output'/'charts';O.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'Noto Sans CJK SC','axes.unicode_minus':False,'svg.fonttype':'none','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#b0bdc7','axes.labelcolor':'#42566a','text.color':'#173347','xtick.color':'#42566a','ytick.color':'#42566a','figure.facecolor':'#ffffff','axes.facecolor':'#ffffff','grid.alpha':.22,'savefig.facecolor':'#ffffff'})
C={'价值100':'#087e8b','沪深300':'#8c96a4','自由现金流':'#e89f37','红利低波':'#7664b4','红利质量':'#a35172'}
def save(fig,name):
 fig.tight_layout();fig.savefig(O/(name+'.svg'),bbox_inches='tight');fig.savefig(O/(name+'.png'),dpi=180,bbox_inches='tight');plt.close(fig)
tr=pd.read_csv(D/'domestic_total_return_daily.csv',index_col=0,parse_dates=True)
fig,ax=plt.subplots(figsize=(10,4.8))
for n in ['价值100','沪深300','自由现金流','红利低波']:ax.plot(tr.index,tr[n]/tr[n].iloc[0],label=n,color=C[n],lw=2 if n=='价值100' else 1.4)
ax.axvspan(tr.index[0],pd.Timestamp('2024-10-29'),color='#eff2f5',alpha=.65,zorder=-5);ax.axvline(pd.Timestamp('2024-10-29'),color='#a35172',ls='--',lw=1);ax.text(pd.Timestamp('2015-01-01'),7.2,'灰区：含回溯／历史版本未复原',fontsize=10,color='#607388');ax.set_ylabel('期初资产 = 1 · 全收益');ax.set_xlabel('2012-12-31—2026-09-30');ax.legend(ncol=4,loc='upper left');ax.grid(axis='y');save(fig,'history')
live=tr.loc['2024-10-29':]
fig,ax=plt.subplots(figsize=(10,4.3))
for n in ['价值100','沪深300','红利低波','自由现金流']:ax.plot(live.index,100*(live[n]/live[n].iloc[0]-1),color=C[n],label=n,lw=2 if n=='价值100' else 1.4)
ax.set_ylabel('累计全收益（%）');ax.legend(ncol=4);ax.grid(axis='y');ax.set_xlabel('2024-10-29—2026-09-30 · 现行版本观察边界仍有待官方档案确认');save(fig,'recent')
fig,ax=plt.subplots(figsize=(10,4))
for n in ['价值100','沪深300']:ax.plot(tr.index,100*(tr[n]/tr[n].cummax()-1),color=C[n],label=n,lw=1.3)
ax.set_ylabel('距此前高点（%）');ax.set_xlabel('2012-12-31—2026-09-30 · 含回溯及版本不确定性');ax.legend();ax.grid(axis='y');save(fig,'drawdown')
fig,ax=plt.subplots(figsize=(10,4.5))
for n in ['沪深300','红利质量','自由现金流']:
 r=tr['价值100']/tr[n];ax.plot(tr.index,r/r.iloc[0],label='价值100 / '+n,color=C[n],lw=1.6)
ax.axhline(1,color='#b0bdc7',ls='--');ax.set_ylabel('相对资产比 · 起点 = 1');ax.set_xlabel('2012-12-31—2026-09-30 · 含回溯，不能视作现行规则实绩');ax.legend();ax.grid(axis='y');save(fig,'relative')
rw=pd.read_csv(D/'rolling_windows.csv',parse_dates=['start','end'])
for h in [1,3,5,10]:
 fig,ax=plt.subplots(figsize=(10,4.2))
 for n in ['价值100','沪深300','自由现金流']:
  q=rw[(rw.name==n)&(rw.years==h)];ax.plot(q.end,q.annualized*100,label=n,color=C[n],lw=1.7)
 ax.axhline(0,color='#ab5963',ls='--');ax.set_ylabel(f'{h}年持有年化收益（%）' if h>1 else '1年持有收益（%）');ax.set_xlabel('月末滚动终点 · 重叠窗口，含回溯／版本不确定性');ax.legend(ncol=3);ax.grid(axis='y');save(fig,'rolling'+str(h))
s=pd.read_csv(D/'sector_weights_20260930.csv',index_col=0).iloc[:,0].sort_values()
fig,ax=plt.subplots(figsize=(9,4.6));ax.barh(s.index,s.values,color=['#cbd6dd']*(len(s)-3)+['#368894','#368894','#087e8b']);ax.set_xlim(0,40)
for i,v in enumerate(s):ax.text(v+.4,i,f'{v:.2f}%',va='center',fontsize=10)
ax.set_xlabel('国证一级行业权重（%）· 2026-09-30');ax.grid(axis='x');save(fig,'sector')
sc=pd.read_csv(D/'scenario_returns.csv');fig,ax=plt.subplots(figsize=(8.7,4));labels=['悲观','基准','乐观'];x=np.arange(3)
for offset,h,color in [(-.18,5,'#76bac2'),(.18,10,'#087e8b')]:
 vals=sc[sc.years==h].set_index('scenario').loc[labels].annualized_return*100;bars=ax.bar(x+offset,vals,.34,label=f'{h}年',color=color)
 for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+(.45 if v>=0 else -.5),f'{v:.2f}%',ha='center',va='bottom' if v>=0 else 'top',fontsize=10)
ax.set_xticks(x,labels);ax.set_ylim(-7,16);ax.axhline(0,color='#b0bdc7');ax.set_ylabel('假设年化收益（%）');ax.legend();ax.set_xlabel('条件化模型 · 假设，不是预测 · 仅扣0.20%年费');save(fig,'scenarios')
f=pd.read_csv(D/'fund_index_comparison.csv',index_col=0,parse_dates=True);fig,ax=plt.subplots(figsize=(10,4.1))
for n,color in [('ETF净值','#a35172'),('指数全收益','#087e8b'),('指数价格','#8c96a4')]:ax.plot(f.index,100*(f[n]/f[n].iloc[0]-1),label=n,color=color,lw=1.7)
ax.set_ylabel('累计收益（%）');ax.legend(ncol=3);ax.set_xlabel('2025-06-30收盘—2026-09-30 · ETF净值已含实际基金费用');ax.grid(axis='y');save(fig,'fund')
fx=pd.read_csv(D/'overseas_etf_usd_cny_10y.csv');fig,ax=plt.subplots(figsize=(8.8,4));xx=np.arange(len(fx))
for offset,k,label,color in [(-.18,'USD_CAGR','美元基金净值','#8c96a4'),(.18,'CNY_CAGR_before_channel_costs','折算人民币','#087e8b')]:
 vals=fx[k]*100;bars=ax.bar(xx+offset,vals,.34,label=label,color=color)
 for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.15,f'{v:.2f}%',ha='center',fontsize=10)
ax.set_xticks(xx,['IVE · S&P 500 Value','IWD · Russell 1000 Value','IVV · S&P 500']);ax.set_ylim(0,19);ax.set_ylabel('10年年化（%）');ax.legend(ncol=2);ax.set_xlabel('2016-06-30—2026-06-30 · 人民币折算未扣渠道及个人税费');ax.grid(axis='y');save(fig,'overseas_fx')
print('Saved 12 SVG/PNG charts.')
