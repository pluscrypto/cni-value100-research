from pathlib import Path
import json,zipfile,hashlib
import pandas as pd
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from openpyxl.styles import Font,PatternFill,Alignment
P=Path(__file__).resolve().parents[1];D=P/'data';O=P/'output';R=P/'raw'
Q=json.loads((D/'reviewed.json').read_text());X=json.loads((D/'supplement.json').read_text());sources=json.loads((D/'sources.json').read_text())
def pct(v):return f'{float(v)*100:.2f}%'
readme='''# 国证价值100（980081）深度研究核对包

研究执行日：2026-10-05 UTC。国内行情和样本：2026-09-30。
主报告：国证价值100_深度研究.html。完整单文件，图表/来源/筛选/7项CSV下载可离线打开。

## 证据边界
官方身份字段发布日期2012-12-28；官方样本展示及首个完整OHLC起点2024-10-29。
尚未取得980081完整旧规则、原始修订公告和版本回溯链；不能证明现行规则自2012年实盘运行。
full_backtest_mixed表示历史混合序列（回溯/原规则实绩/重编边界无法完全拆分），不是13.75年现行实绩。
post_20241029仅为保守观察边界，不冒充已核验的官方现行发布日期。
ETF实际成立2025-06-30，上市2025-07-08；实际历史约15个月。

## 文件及单位
data目录是关键数据与计算结果；raw目录只包含报告实际选用的证据（含PDF或原始API/网页），不包括失败请求。
sources.csv列明每项来源、日期、文件及证据级别；evidence_manifest.csv给出原始文件SHA-256。
所有收益、波动、亏损占比、相关性及情景增长率以小数存储：0.10代表10%，不是0.10%。
成分CSV中的“权重（%）”以百分数存储：7.96代表7.96%；总市值列为亿元；权重四舍五入总和99.95%，未归一。
company_evidence中的net_profit_bn、ocf_bn单位为十亿元人民币（bn）；换为亿元要乘10；财务期2026-06-30。
海外MSCI为美元NET；美国ETF为美元NAV再投（已含基金费，不等于个人税后）。人民币折算未扣渠道/个人税。
ETF市场量为手（100份）；approx_turnover仅以收盘价乘量的近似，非精确交易所成交额。
scenario是明确假设，不是预测或置信区间；starting_pe=8.3532，仅扣年管理/托管0.20%，忽略其余摩擦。
fund_half_year_turnover是含申赎的基金交易强度代理，不是纯指数换手，也不外推为全年。

## 复现（离线，使用本包原始文件）
Python 3.12推荐。安装requirements.txt后，在本目录按顺序运行：
python scripts/metadata.py
python scripts/analyze.py
python scripts/supplement.py
python scripts/charts.py
python scripts/report.py
python scripts/deliverables.py

图表用Noto Sans CJK SC（无此字体可改为系统中文字体），SVG及PNG为独立可分享图。
所有计算读取保存的raw文件，不需要重新联网。浏览器QA脚本qa.py另需Chromium；本包保存QA结果。
HTML/PPTX与CSV采用同一份reviewed.json等计算结果；计算方法详见报告第13节。
滚动窗口按月末、重叠，不能把历史胜率作为未来概率。没有历史PE分位、独立alpha或全100家现金归因的伪造值。

## 策略结论
有条件值得长期关注或作为价值补充；独特长期alpha尚未证明。
当前低PE有价格起点优势，但盈利下滑、集中与证据缺口使“足够安全边际”尚未得到确认。
'''
(P/'README.md').write_text(readme)
(P/'requirements.txt').write_text('pandas>=2.2\nnumpy>=2.0\nmatplotlib>=3.9\nscipy>=1.14\nopenpyxl>=3.1\nbeautifulsoup4>=4.12\npython-pptx>=1.0\nxlrd>=2.0\nplaywright>=1.50\n')
# Workbook preserves fraction units, with an explicit unit sheet.
with pd.ExcelWriter(O/'国证价值100_核对工作簿.xlsx',engine='openpyxl') as writer:
 pd.DataFrame([['as_of','2026-10-05 UTC；国内行情2026-09-30'],['returns','小数收益：0.1=10%；年度末2026为YTD'],['weights','权重（%）列是百分数；99.95%是公开四舍五入'],['financial_bn','利润/OCF bn单位十亿元，乘10为亿元'],['full_backtest_mixed','历史混合，非现行规则13.75年实绩'],['post_20241029','保守观察边界，非已核验发布日'],['scenarios','假设，不是预测；只扣0.20%管理托管费'],['fx','人民币/美元；折算未扣个人渠道和税费'] ],columns=['item','meaning']).to_excel(writer,sheet_name='说明与单位',index=False)
 names={'performance_metrics':'收益风险','rolling_summary':'滚动汇总','rolling_windows':'滚动明细','annual_returns':'逐年收益','drawdown_episodes':'回撤恢复','dividend_wedge':'股息再投差异','constituents_20260930':'价值100现行权重','sector_weights_20260930':'行业权重','competitors':'12个核心竞品','csi_latest_valuation':'国内最新估值','company_evidence_20260630':'半年报样本','scenario_returns':'情景假设结果','scenario_sensitivity':'情景敏感性','entry_path_summary':'买入路径汇总','entry_path_windows':'买入路径明细','etf_159263_nav_daily':'ETF真实净值','fund_index_comparison':'基金指数对照','etf_price_nav_premium':'ETF折溢价','product_catalog':'官方产品目录','domestic_total_return_daily':'国内全收益日值','domestic_price_daily':'国内价格日值','overseas_etf_usd_cny_10y':'海外ETF汇率折算','overseas_msci_annual_usd_cny':'海外年度折算','sources':'来源登记','evidence_manifest':'原始证据校验','monthly_correlation_full':'月收益相关','daily_correlation_recent':'短窗日收益相关'}
 names['feeder_common_period']='联接真实收益对照';names['source_link_checks']='来源链接检查'
 for file in sorted(D.glob('*.csv')):
  if file.stem not in names:continue
  df=pd.read_csv(file,dtype={'样本代码':str,'fundCode':str,'code':str})
  df.to_excel(writer,sheet_name=names[file.stem],index=False)
 for sh in writer.book:
  sh.freeze_panes='A2';sh.auto_filter.ref=sh.dimensions
  for cell in sh[1]:cell.font=Font(name='Microsoft YaHei',bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='17384B');cell.alignment=Alignment(wrap_text=True,vertical='top')
  sh.row_dimensions[1].height=32
  for col in sh.columns:
   length=max(len(str(c.value or '')) for c in list(col)[:80]);sh.column_dimensions[col[0].column_letter].width=min(55,max(12,length+2))
# PPTX: twenty 16:9 slides, same data; simple geometry and capped text length for reliable opening.
pr=Presentation();pr.slide_width=Inches(13.333);pr.slide_height=Inches(7.5)
INK='17384B';TEAL='087E8B';MUTED='53697B';WHITE='FFFFFF';PALE='EDF5F6';SAND='FCF3E4'
def rect(sl,x,y,w,h,color):
 z=sl.shapes.add_shape(1,Inches(x),Inches(y),Inches(w),Inches(h));z.fill.solid();z.fill.fore_color.rgb=RGBColor.from_string(color);z.line.fill.background();return z
def text(sl,x,y,w,h,value,size=22,color=INK,bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.word_wrap=True;tf.margin_left=Inches(.02);tf.margin_right=Inches(.02);tf.margin_top=Inches(.02);tf.margin_bottom=0
 for i,line in enumerate(value.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Noto Sans CJK SC';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(9);p.line_spacing=1.2
 return sh
def slide(title,subtitle='',note=''):
 sl=pr.slides.add_slide(pr.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=RGBColor.from_string(WHITE);rect(sl,0,0,13.333,.12,TEAL)
 text(sl,.65,.38,12,.7,title,28,bold=True)
 if subtitle:text(sl,.65,1.13,12,.55,subtitle,14,MUTED)
 rect(sl,.65,6.97,12,.012,'DCE5E9');text(sl,.65,7.06,11.4,.28,note or '国证价值100（980081）｜研究执行2026-10-05；国内行情/权重2026-09-30',10,MUTED);text(sl,12.3,7.04,.4,.3,str(len(pr.slides)),10,MUTED)
 return sl
def picture(sl,name,x=.7,y=1.9,w=11.9):
 from PIL import Image
 path=O/'charts'/(name+'.png');iw,ih=Image.open(path).size;limit_h=4.25
 width=min(w,limit_h*iw/ih);sl.shapes.add_picture(str(path),Inches(x+(w-width)/2),Inches(y),width=Inches(width))
def cards(sl,entries,y=1.9):
 for i,(heading,content) in enumerate(entries):
  x=.7+(i%2)*6.15;yy=y+(i//2)*2.15;rect(sl,x,yy,5.85,1.94,PALE);text(sl,x+.2,yy+.13,5.45,.4,heading,18,TEAL,True);text(sl,x+.2,yy+.66,5.45,1.13,content,18)
def ppttable(sl,headers,rows,x=.7,y=1.9,w=11.9,h=4.6,size=14,widths=None):
 tb=sl.shapes.add_table(len(rows)+1,len(headers),Inches(x),Inches(y),Inches(w),Inches(h)).table
 if widths:
  for col,v in zip(tb.columns,widths):col.width=Inches(v)
 for i,row in enumerate([headers]+rows):
  for j,val in enumerate(row):
   c=tb.cell(i,j);c.text=str(val);c.margin_left=Inches(.12);c.margin_top=Inches(.08);c.margin_bottom=Inches(.04);c.vertical_anchor=MSO_ANCHOR.TOP;c.fill.solid();c.fill.fore_color.rgb=RGBColor.from_string(INK if i==0 else PALE if i%2 else WHITE)
   for pa in c.text_frame.paragraphs:pa.font.name='Noto Sans CJK SC';pa.font.size=Pt(size);pa.font.bold=i==0;pa.font.color.rgb=RGBColor.from_string(WHITE if i==0 else INK)
 return tb
sl=slide('国证价值100是否值得长期持有？','深度研究结论版 · 20页 · 完整证据、计算与来源见HTML', '执行2026-10-05｜中国行情2026-09-30｜不是个人仓位建议')
text(sl,.8,2.15,11.8,1.3,'有条件值得关注，\n当前安全边际尚未证明。',36,TEAL,True)
text(sl,.8,4.1,11.6,1.65,'现金分红与低价盈利提供经济基础；盈利衰退与集中风险可能抵销低估值。\n现行版本观察不足两年，最老ETF约15个月，不能把13.75年曲线当作现行实绩。',23)
sl=slide('六个问题，先给明确答案','结论分开：机制、证据、价格和目标')
cards(sl,[('长期价值：有条件','跨周期现金盈利兑现、成本可控，且能承受多年机会成本。'),('当前买入：证据不足','PE TTM 8.35倍较低；正常化利润、分红覆盖与所需回报仍要核验。'),('赚钱 / 亏损','赚现金与盈利、可能的重估；亏利润永久下降、派息削减和风格失宠。'),('独特优势：未证明','组合设计有特色；剥离行业/价值/现金流后的alpha尚无证据。')])
sl=slide('身份与三条时间线','官方发布日期字段≠今天规则已经实盘运行', 'S01/S02/S03/S05/S10/S11｜版本档案缺口会实质改变长期判断')
ppttable(sl,['时间','事实','能证明什么'],[['2012-12-28 / 12-31','官网发布日期字段 / 指数基日','原始版本与重编回溯链未取得；不能视为现行13.75年实绩。'],['2024-10-29','样本展示及完整OHLC起点','选作保守现行观察边界；不是已核验正式发布日。'],['2025-06-30 / 07-08','最老ETF成立 / 上市','才有真实基金投资表现，约15个月。']],h=3.8,size=18,widths=[2.3,4.1,5.5])
text(sl,.8,6.1,11.8,.55,'排除错误旧版本线索：CN6027官方文件是西藏综合指数。',16,MUTED)
sl=slide('现行规则：价值＋历史质量，仍有定义缺口','选样与权重不是等权100家优质公司', 'S01｜ROE稳定不保证未来利润稳定；自由现金流率/倾斜因子未完整定义')
cards(sl,[('先剔除','规模/流动性后20%、亏损；ROE均值后20%、波动前20%、FCF率后50%。'),('再选100只','非金融：E/P＋股息率＋FCF率；金融/地产只用前两项。'),('权重','价值得分倾斜×自由流通市值；调仓时单股8%、二级行业20%上限。'),('每季调整','更换只数≤50%，不是资金换手≤50%；随后权重可漂移。')])
sl=slide('收益机制：什么是价值创造，什么是风险补偿','不把分红、回购、EPS增长和FCF重复相加', 'S01/S39；研究判断｜没有成分/财务/除数链，不做精确盈利与调仓归因')
ppttable(sl,['来源','机制','边界'],[['盈利/现金增长','资本回报超过成本，支持每股现金增长','EPS已含净回购/稀释；不再加回购收益率。'],['现金分红','企业现金向股东转移，再投参与复利','除息抵减价格；不是额外免费收益。'],['估值与再平衡','买入低价、重估或维持价值暴露','重估依赖市场；调仓可能产生摩擦或错失趋势。'],['行业/风格风险','价值、金融、周期等风险补偿','历史高收益不能直接认定独立alpha。']],size=17,widths=[2.2,4.6,5.1])
sl=slide('现金股息是可观测的贡献，非未来票息','全收益与价格增长倍数之比，再几何年化', 'S05/S06；自行计算｜分红增益不是当前官方股息率；不能直接相加')
ppttable(sl,['区间','价格年化','全收益年化','分红再投几何增益'],[['历史混合序列',pct(Q['dividend_wedge'][0]['pr_cagr']),pct(Q['dividend_wedge'][0]['tr_cagr']),pct(Q['dividend_wedge'][0]['reinvestment_geometric_wedge'])],['2024-10-29后',pct(Q['dividend_wedge'][1]['pr_cagr']),pct(Q['dividend_wedge'][1]['tr_cagr']),pct(Q['dividend_wedge'][1]['reinvestment_geometric_wedge'])]],h=2.6,size=22)
text(sl,.85,5.2,11.5,1.1,'(1+全收益年化) = (1+价格年化) × (1+股息几何增益)\n分红覆盖和每股盈利比历史派息数字更重要。',23)
sl=slide('历史混合序列表现好，不能当作冻结规则实绩','相同人民币全收益；2012-12-31—2026-09-30', 'S06/S07/S19；自行计算｜灰区含回溯/无法复原版本；未扣基金费用和税费')
picture(sl,'history',y=1.85,w=11.45)
sl=slide('现行观察不足两年：强于300，但不是最低回撤','2024-10-29—2026-09-30，相同人民币全收益', 'S06/S07/S19；自行计算｜价值100累计23.93%、MDD−15.80%；没有现行3/5/10年实绩')
picture(sl,'recent',y=1.85,w=11.6)
sl=slide('滚动持有：零亏损历史窗口不是未来概率','月末窗口高度重叠；全部来自历史混合序列', 'S06/S07；自行计算｜106个5年窗口约2个不重叠块，46个10年约1个')
rs=[r for r in Q['rolling'] if r['name']=='价值100']
ppttable(sl,['持有','窗口数','最差累计','中位年化','亏损窗口','胜300窗口'],[[str(int(r['horizon_years']))+'年',r['windows'],pct(r['min_cumulative']),pct(r['median_annualized']),pct(r['loss_share']),pct(r['beat_300_share'])] for r in rs],size=18,h=3.8)
text(sl,.8,6.05,11.7,.55,'2018-01末至2021-01末：价值100仍亏约0.72%，沪深300约赚33.64%。',17,MUTED)
sl=slide('亏损之后，恢复需要时间','每日收盘毛全收益，2013起序列不包括2008系统性危机', 'S06/S07；自行计算｜2015高点恢复728天；2018高点恢复888天；2026峰值尚未恢复')
picture(sl,'drawdown',y=1.8,w=11.65)
text(sl,.8,6.28,11.8,.45,'永久利润损失、信用恶化、现金分红失去覆盖，不能靠“等情绪变好”解决。',17,MUTED)
sl=slide('绝对赚钱，也可能有很高机会成本','相对资产比的峰谷与恢复，不是两个收益率百分点差', 'S06/S07/S19；自行计算｜含历史混合/对照回溯，不能预设未来恢复期限')
picture(sl,'relative',y=1.8,w=11.35)
text(sl,.8,6.3,11.8,.4,'相对红利质量恢复曾需3539天；相对自由现金流截至9月末仍未恢复。',17,MUTED)
sl=slide('长期有效性：机制合理，独特alpha未验证','需要同池、同成本、公告后数据和冻结规则的样本外对照')
cards(sl,[('已有支持','现金机制合理；长期混合曲线有支持；近期观察和真实ETF提供初步证据。'),('偏差风险','规则自由度、回溯优化、版本更新、历史成分缺失、前视与幸存者问题。'),('简单对照','纯E/P→加股息→加FCF→加质量→行业上限→价值倾斜，逐项检验增量。'),('最大未知','利润/现金与调仓的精确贡献、普通价值/行业风险控制后的净alpha。')])
sl=slide('国内替代：选择不同的经济约束','不是只按过去收益选冠军', 'S15/S16/S17/S18/S19/S38｜完整12个对象与日期见HTML可筛选表')
ppttable(sl,['对象','优先研究的需求','相对价值100'],[['300价值','简洁大盘价值','质量筛选较少，复杂规则增量未证明。'],['红利 / 红利低波','高股息或历史低波','不保证低风险；目标并非回撤最小。'],['红利质量','愿为盈利质量付更高价格','估值17.47倍，可能有成长/重估风险。'],['自由现金流','不想承担银行会计与信贷风险','排除金融，FCF/EV；持仓/收益仍部分重合。'],['300 / 全指','市场广覆盖、减轻风格押注','核心研究更直接；仍有系统性风险。']],size=16)
sl=slide('海外对照：价值可长期落后宽基','美元ETF同区间、同净值再投；人民币折算另列', 'S25/S26/S29/S30；2016-06-30—2026-06-30；未扣个人税/渠道，不与国内毛收益排名')
picture(sl,'overseas_fx',y=1.85,w=11.2)
text(sl,.8,6.25,11.8,.5,'MSCI Value也曾2007—2009实绩回撤61.22%；便宜不是危机免疫。',17,MUTED)
sl=slide('当前组合：低PE，集中并不低','2026-09-30：PE TTM 8.3532×；PB 0.65×；前十大47.65%', 'S03/S04｜一级可选消费35%不违反二级行业20%上限；有效等权数约30.47')
picture(sl,'sector',x=.8,y=1.85,w=9.6)
text(sl,10.6,2.3,2,.5,'前三大',18,MUTED);text(sl,10.6,2.9,2,1,'22.76%',29,TEAL,True);text(sl,10.6,4.1,2,1.8,'格力\n海信家电\n兴业银行',18)
sl=slide('最新报表反证：历史质量有滞后','财务2026-06-30，权重2026-09-30；只覆盖32.08%，不作全指数归因', 'S31/S32/S33/S34/S35/S36｜OCF合并口径；半年度季节性；兴业同比依据法定摘要检索')
ppttable(sl,['公司','权重','归母利润同比','经营现金流同比 / 风险'],[['格力','7.96%','−7.87%','−33.60%'],['海信家电','7.77%','−20.16%','−39.21%'],['老板电器','4.35%','−18.75%','现金转负至−3.62亿元'],['上汽','4.97%','−14.38%','+158.13%；包含财务公司金融资产配置影响'],['兴业银行','7.03%','约−4.66%','银行不使用一般FCF；NIM1.60%、不良1.08%']],size=17)
sl=slide('情景：低估值也可能十年仍亏','假设：悲观g−2%/p30%/PE6；基准2%/40%/8；乐观5%/45%/10', '情景假设；初始PE8.3532，仅扣0.20%年费；增长、派息、PE均不是预测或概率')
picture(sl,'scenarios',x=.85,y=1.9,w=10.4)
text(sl,.85,6.28,11.7,.4,'利润下降40%时正常化PE约13.92倍；基准10年6.33%不等于足够风险补偿。',16,MUTED)
sl=slide('真实ETF净值：低年费不等于无摩擦','159263：管理0.15%＋托管0.05%；成立至2026-09-30同收盘基准', 'S05/S06/S09/S10/S11/S13｜净值13.34% vs 毛全收益16.71%；差3.37pp不能只归年费')
picture(sl,'fund',y=1.9,w=11.6)
sl=slide('买入路径与配置：现金有机会成本','同一初始本金、现金假设1.5%；5年106个重叠历史混合窗口', 'S06/S19/S37/S38；自行计算｜分批不必更优；没有ETF五年实际历史；不提供个人仓位')
ppttable(sl,['路径','五年累计中位数','超过一次买入比例'],[['一次买入','106.80%','基准'],['4次季度分批','92.28%','32.08%'],['12个月定投','91.45%','29.25%']],h=2.6,size=22)
text(sl,.85,5.05,11.5,1.4,'与300：29只重合，覆盖价值100一侧61.46%权重。\n与FCF：40只，权重重合36.47%，收益相关高；与成长0同名不等于对冲。',20)
sl=slide('必要条件与可推翻证据：长期持有不能免于复核','策略值得关注与当前买入吸引力分别结论')
cards(sl,[('必要条件','利润与股东现金跨周期兑现、派息不靠债、价格补偿充分、规则和成本可靠。'),('重评信号','盈利与现金共同萎缩、银行信用成本上升、分红覆盖恶化、交易/税费差距扩大。'),('推翻逻辑','永久现金创造下降；财务/治理失真；实盘剥离风格后无增量且成本较高。'),('下一步证据','保存每季完整权重；补旧规则/修订公告；跟踪现金覆盖、资本开支与净回报。')])
assert len(pr.slides)==20
pr.save(O/'国证价值100_结论版.pptx')
# Include only cited valid sources; calculations reproduce without network.
files=set()
for s in sources:
 for f in s['local_files']:
  if (R/f).exists():files.add(R/f)
files.update(D.glob('*'));files.update((P/'scripts').glob('*.py'));files.update([P/'README.md',P/'requirements.txt',P/'PROGRESS.md'])
with zipfile.ZipFile(O/'国证价值100_数据与计算.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in sorted(files):z.write(f,str(f.relative_to(P)))
 for f in sorted((O/'charts').glob('*')):z.write(f,'charts/'+f.name)
# A small checkpoint that does not contain the full HTML/zip again.
(O/'交付说明.txt').write_text(readme)
print(f'Saved workbook, {len(pr.slides)}-slide PPTX and reproducible evidence ZIP ({(O/"国证价值100_数据与计算.zip").stat().st_size/1024/1024:.1f} MB).')
