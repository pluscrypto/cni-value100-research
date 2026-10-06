# 国证价值100长期投资价值研究

研究对象：国证价值100指数（980081）。研究快照日期：2026-10-05；国内行情与成分权重：2026-09-30。

- [完整HTML报告](output/国证价值100_深度研究.html)：13节、12幅图、12个核心比较对象、100只现行成分股。
- [关键数据、原始证据与计算代码ZIP](output/国证价值100_数据与计算.zip)
- [30页签核对工作簿](output/国证价值100_核对工作簿.xlsx)
- [20页结论版PPTX](output/国证价值100_结论版.pptx)
- [来源登记](data/sources.csv)与[原始证据校验清单](data/evidence_manifest.csv)

在线阅读：[现有私有网页](https://cni-value100-research-20261005.xingzouj.chatgpt.site)（需要原账户访问）。本仓库为私有仓库，不启用GitHub Pages。

GitHub中的HTML文件页显示源码。可下载HTML后用浏览器打开，或本地运行：

```sh
python -m http.server 8000 --directory output
```

然后访问 `http://localhost:8000/`。图表、交互筛选和关键CSV均已内嵌，无需外部CDN。

## 项目结构

```text
data/          原始整理数据、计算结果、来源与QA结果
raw/           本研究实际采用的官方文件/API/网页快照
scripts/       离线复现、图表、HTML、工作簿和PPTX生成脚本
output/        可阅读报告、下载附件与独立SVG/PNG图表
requirements.txt
```

计算脚本将新结果写入 `output/`；已交付快照保留在Git历史中。第三方资料与行情的权利归其原权利人，来源与日期见登记；仓库不为这些原始资料另行授予开源许可。

---

# 国证价值100（980081）深度研究核对包

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
