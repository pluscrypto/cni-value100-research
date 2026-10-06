from pathlib import Path
import json,hashlib
import pandas as pd
P=Path(__file__).resolve().parents[1];R=P/'raw';D=P/'data'
BASE='https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/'
sources=[]
def src(i,title,url,files,date,kind='官方原始资料',notes=''):
 sources.append(dict(id=i,title=title,url=url,local_files=files,data_date=date,retrieved_date='2026-10-05',kind=kind,notes=notes))
src('S01','国证价值100现行编制方案','https://www.cnindex.com.cn/docs/gz_980081.pdf',['gz_pdf.pdf','gz_pdf.txt'],'现行网页版本；PDF未标版本生效日',notes='自由现金流率完整定义及倾斜因子细节未披露')
src('S02','国证指数身份字段','https://www.cnindex.com.cn/index-intro?indexcode=980081',['intro2.json','intro3.txt','metadata2.txt'],'截至2026-10-05网页字段',notes='fbrq=2012-12-28，不等于已核验现行规则发布日期')
src('S03','国证指数全目录与估值','https://www.cnindex.com.cn/index/indexList?channelCode=-1&rows=2000&pageNum=1',['list.txt'],'行情2026-09-30；样本展示起点2024-10-29',notes='PE TTM与静态PE分别保存，不混用')
src('S04','国证价值100完整现行样本','https://www.cnindex.com.cn/sample-detail/download-history?indexcode=980081',['samples.bin'],'2026-09-30',notes='100只，权重加总99.95%，官方四舍五入')
src('S05','国证价值100价格日序列','https://hq.cnindex.com.cn/market/market/getIndexDailyDataWithDataFormat?indexCode=980081&startDate=2012-12-31&endDate=2026-09-30&frequency=day',['histo.txt'],'2012-12-31—2026-09-30',notes='2024-10-29前无OHLC，不能据此确认现行版本实绩')
src('S06','国证价值100全收益日序列','https://hq.cnindex.com.cn/market/market/getIndexDailyDataWithDataFormat?indexCode=480081&startDate=2012-12-31&endDate=2026-09-30&frequency=day',['history_480081.json'],'2012-12-31—2026-09-30',notes='全收益指数，未扣基金成本及投资人税费')
src('S07','中证指数国内对照日行情（示例沪深300全收益）','https://www.csindex.com.cn/csindex-home/perf/index-perf?indexCode=H00300&startDate=20121231&endDate=20260930',['csi_H00300.json','csi_H00985.json','csi_H00919.json','csi_H00922.json','csi_H20269.json','csi_qtri.txt','csi_000300_full.txt','csi_000985.json','csi_000919.json','csi_000922.json','csi_H30269.json','csi_931468.json'],'2012-12-31—2026-09-30',notes='将indexCode替换为各代码即可核对；用国证交易日历对齐，排除CSI多出的2018-06-18')
src('S08','国证官方跟踪产品目录','https://www.cnindex.com.cn/info/fund?indexCode=980081&pageNum=1&rows=100',['funds.txt'],'目录截至2026-10-05；规模多数截至2026-06-30',notes='新产品无规模数据不等于规模为零')
src('S09','易方达159263官方产品页','https://www.efunds.com.cn/fund/159263.shtml',['efunds_html.txt','efunds.md'],'净值和日期表2026-09-30',notes='只采用带日期表格；不使用页面无日期旧规模')
src('S10','159263 2026年中期报告','https://cdn.efunds.com.cn/owch/data/bulletin/20260831/易方达国证价值100交易型开放式指数证券投资基金2026年中期报告.pdf',['half_report.pdf','half_report.txt'],'财务2026-06-30；公布2026-08-31')
src('S11','159263更新招募说明书','https://cdn.efunds.com.cn/owch/data/bulletin/20260529/易方达国证价值100交易型开放式指数证券投资基金更新的招募说明书.pdf',['prospectus.pdf','prospectus.txt'],'2026-05-29')
src('S12','025497/025498联接更新招募说明书','https://cdn.efunds.com.cn/owch/data/bulletin/20260731/易方达国证价值100交易型开放式指数证券投资基金发起式联接基金更新的招募说明书.pdf',['linkpros.pdf','linkpros.txt','linkA.txt','linkC.txt'],'说明书2026-07-31；产品页2026-09-30')
src('S13','159263历史单位净值','https://fund.eastmoney.com/pingzhongdata/159263.js',['fundnav.txt'],'2025-06-30—2026-09-30','数据商；已核对官方关键日期','官方核对成立、2025年末、2026年中及最新净值；基金截至本报告无分红记录')
src('S14','159263市场价格及报价','https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sz159263,day,2025-07-08,2026-09-30,640,',['tencent_price.txt','quote_etf.txt'],'2025-07-08—2026-09-30','腾讯行情；非交易所原始逐笔','报价另见https://qt.gtimg.cn/q=sz159263；成交量单位按手，近20日金额为收盘价近似')
src('S15','沪深300价值方法与事实单',BASE+'000919_Index_Methodology_cn.pdf',['000919_rule.pdf','000919_rule.txt','000919_fact.pdf','000919_fact.txt'],'规则2025-01 V1.2；事实单2026-08-31')
src('S16','中证红利方法与事实单',BASE+'000922_Index_Methodology_cn.pdf',['000922_rule.pdf','000922_rule.txt','000922_fact.pdf','000922_fact.txt'],'规则2022-10 V1.2；事实单2026-08-31')
src('S17','中证红利低波动方法与事实单',BASE+'H30269_Index_Methodology_cn.pdf',['H30269_rule.pdf','H30269_rule.txt','H30269_fact.pdf','H30269_fact.txt'],'规则2020-12 V1.1；事实单2026-08-31')
src('S18','中证红利质量方法与事实单',BASE+'20231208180546-931468_Index_Methodology_cn.pdf',['q_method.pdf','q_method.txt','931468_fact.pdf','931468_fact.txt'],'规则2023-12 V1.2；事实单2026-08-31')
src('S19','国证自由现金流规则、行情与样本','https://www.cnindex.com.cn/docs/gz_980092.pdf',['fcf_rule2.pdf','fcf_rule2.txt','fcf_intro.json','fcf_cons.bin','history_980092.json','history_480092.json'],'现行方法；样本/行情2026-09-30')
src('S20','MSCI World Value美元净收益事实单','https://www.msci.com/documents/10199/255599/msci-world-value-index-usd-net.pdf',['msci_v.pdf','msci_v.txt'],'2026-09-30',notes='代码105868；1997-12-08前为回溯；股息按MSCI标准税率处理')
src('S21','MSCI World Quality美元净收益事实单','https://www.msci.com/documents/10199/255599/msci-world-quality-index-usd-net.pdf',['msci_qnet.pdf','msci_qnet.txt'],'2026-09-30',notes='代码702787；2012-12-18前为回溯；不使用同名毛收益PDF')
src('S22','S&P 500 Value指数主页','https://www.spglobal.com/spdji/en/indices/equity/sp-500-value/',['spv.txt','spv_plain.txt'],'截至2026-10-05网页',notes='价格SVX；全收益SPTRSVX由IVE基准字段核对')
src('S23','S&P美国风格指数方法','https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-us-style.pdf',['sp_style_method.pdf','sp_style_method.txt'],'现行官方方法')
src('S24','Russell美国指数方法','https://research.ftserussell.com/products/downloads/Russell-US-indexes.pdf',['russell_method.pdf','russell_method.txt'],'2026-08 V7.2',notes='2026年起半年重构，不沿用旧年度重构描述')
src('S25','IWD官方产品和业绩','https://www.ishares.com/us/products/239708/ishares-russell-1000-value-etf',['iwd.txt','iwd_plain.txt'],'收益表2026-06-30；PE2026-10-02',notes='基准RU10VATR；费用0.18%；基金美元净值再投收益')
src('S26','IVE官方产品和业绩','https://www.ishares.com/us/products/239728/ishares-sp-500-value-etf',['ive.txt','ive_plain.txt'],'收益表2026-06-30；PE2026-10-02',notes='基准SPTRSVX；费用0.18%；基金美元净值再投收益')
src('S27','SCHD官方产品页','https://www.schwabassetmanagement.com/products/schd',['schd.txt','schd_plain.txt'],'规模2026-10-02；PE/周转2026-08-31',notes='静态业绩表日期标签与异步内容存在歧义，未纳入精确收益比较；费用0.060%')
src('S28','Dow Jones股息指数方法','https://www.spglobal.com/spdji/en/documents/methodologies/methodology-dj-dividend-indices.pdf',['dj_method.pdf','dj_method.txt'],'现行官方方法',notes='DJUSDIV/DJUSDIVT；连续支付股息不等于连续提高股息')
src('S29','IVV官方产品和业绩','https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf',['ivv.txt','ivv_plain.txt'],'收益表2026-06-30',notes='相应宽基；费用0.03%')
src('S30','美联储H.10人民币兑美元历史','https://www.federalreserve.gov/releases/h10/hist/dat00_ch.htm',['fed_fx.txt'],'可得末值2026-09-25；收益折算只到可匹配日期',notes='单位人民币/美元；删除NA日期；不编造9月30日汇率')
src('S31','海信家电2026半年报','https://static.cninfo.com.cn/finalpage/2026-08-18/1225477556.PDF',['hisense_report.pdf','hisense_report.txt'],'财务2026-06-30；公告2026-08-18')
src('S32','老板电器2026半年报','https://igw.robam.com/upload/2026/08/31/17881640082037xbo64.pdf',['robam_report.pdf','robam_report.txt'],'财务2026-06-30；官网文件2026-08-31')
src('S33','格力电器2026半年报法定报告转载','https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?stockid=000651&id=12553937',['gree_filing.txt','gree_filing_plain.txt'],'财务2026-06-30','法定文件的新浪镜像；非公司原始站点')
src('S34','上汽集团官方财务数据表','https://www.saicmotor.com/chinese/tzzgx/jbqk/cwsj/index.shtml',['saic_data.txt','saic_data_plain.txt'],'2023—2025年度及2026-06-30')
src('S35','上汽2026半年报法定报告转载','https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?stockid=600104&id=12567755',['saic_filing.txt','saic_filing_plain.txt'],'财务2026-06-30','法定文件的新浪镜像；非公司原始站点')
src('S36','兴业银行半年业绩官方解读','https://www.cib.com.cn/cn/aboutCIB/about/news/2026/20260915.html',['cib_news.txt','cib_news_plain.txt'],'财务2026-06-30；发布2026-09-15',notes='部分同比来自法定报告摘要检索，证据级别单独说明')
src('S37','国证成长100现行样本','https://www.cnindex.com.cn/sample-detail/download-history?indexcode=980080',['growth_cons2.bin'],'2026-09-30',notes='只用于持仓重合；不拿0重合当风险对冲证明')
src('S38','沪深300完整样本名单','https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/cons/000300cons.xls',['csi300cons3.bin','csi_fact.pdf','csi_fact.txt','000985_fact.pdf','000985_fact.txt'],'样本2026-09-30；事实单2026-08-31',notes='名单无权重，仅计算价值100一侧被覆盖权重')
src('S39','Ken French数据资料库','https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html',['ff_library.txt'],'截至2026-10-05','学术数据说明',notes='价值和盈利因子机制背景；本报告未做中国因子回归，不能据此认定目标指数有alpha')
src('S40','红利质量全收益代码官方对应','https://www.csindex.com.cn/csindex-home/perf/get-derivative-index?indexCode=931468',['derivatives.txt'],'截至2026-10-05',notes='全收益921468；931469等近似代码不是该指数')
src('S41','CN6027官方方案：西藏综合指数','https://www.cnindex.com.cn/docs/gz_CN6027.pdf',['old_rule.pdf','old_rule.txt'],'现行官方文件','官方反证资料','排除将CN6027当作价值100旧版本的二手说法；不能补足980081旧规则链')
(D/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
pd.DataFrame([{**s,'local_files':';'.join(s['local_files'])} for s in sources]).to_csv(D/'sources.csv',index=False,encoding='utf-8-sig')
manifest=[]
for s in sources:
 for f in s['local_files']:
  path=R/f
  if path.exists():manifest.append({'source_id':s['id'],'path':'raw/'+f,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
pd.DataFrame(manifest).drop_duplicates(['source_id','path']).to_csv(D/'evidence_manifest.csv',index=False)
# Catalog dates use China time; missing/zero is NOT audited zero assets.
j=json.loads((R/'funds.txt').read_text());c=pd.DataFrame(j['data']['rows']);c['established_china_date']=pd.to_datetime(c.fundDate,unit='ms',utc=True).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d');c.to_csv(D/'product_catalog.csv',index=False,encoding='utf-8-sig')
# Current valuation fields, extracted without changing provider's calculation convention.
li=json.loads((R/'list.txt').read_text())['data']['rows'];vv=[]
for code in ['980081','980092']:
 r=next(x for x in li if x['indexcode']==code)
 # Persist the entire official row as an audit companion.
 (D/('official_metadata_'+code+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2))
for file in ['csi_000300_full.txt','csi_000985.json','csi_000919.json','csi_000922.json','csi_H30269.json','csi_931468.json']:
 r=json.loads((R/file).read_text())['data'][-1];vv.append({'code':r['indexCode'],'name':r['indexNameCnAll'],'date':r['tradeDate'],'pe_ttm_official_field_peg':r['peg'],'source':'S07'})
pd.DataFrame(vv).to_csv(D/'csi_latest_valuation.csv',index=False,encoding='utf-8-sig')
print('Saved source registry, verified-evidence manifest and product catalog.')
