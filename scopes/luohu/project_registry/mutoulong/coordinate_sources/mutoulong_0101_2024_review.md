# 木头龙01-01地块总平图附件核查

核查日期：2026-10-14。本轮继续查找官方CAD及坐标资料，成功取得此前台账之外的01-01地块公示页和附件。原件保留在本地，不覆盖历史图纸或原下载失败记录。

## 实际取得

- [公示正文](https://www.szlh.gov.cn/lhqzfhjsj/gkmlpt/content/11/11206/post_11206089.html)：发布于2024-03-25，指向木头龙01-01地块、宗地H218-0048，说明本次修改涉及轴网坐标等内容。
- [修改后总平面图PDF](https://www.szlh.gov.cn/lhqzfhjsj/attachment/1/1430/1430086/11206089.pdf)：643848字节，1页。SHA-256为`671102aac2318dd4a570a76c3e37907f58a5a8bad563a62cae41587a3097017d`。
- 公示页列出的附件为该PDF；本轮没有从该页面取得DWG、DXF或嵌入CAD附件。不能据此断言原CAD不存在或其他渠道不提供。

## 文件结构检查

PyMuPDF检查结果：页面可提取文字0字符，矢量路径0条，图像引用1个；PDF嵌入文件0个。图像尺寸19880×14033像素，采用JBIG2Decode编码。因此，这是承载图纸影像的PDF，不是本轮已取得的可编辑CAD或可提取矢量红线。

已渲染并查看全页、技术经济指标表和说明/图签局部。表中名称、面积等来自人工读图，不是程序OCR识别结果。

## 图上可读信息

| 内容 | 图上记录 | 适用范围 |
|---|---|---|
| 地块和宗地 | 01-01；H218-0048 | 不能代替01-02或全部拆除范围 |
| 建设用地面积 | 1799.86平方米 | 宗地建设用地，不是全项目拆除面积 |
| 规定地上、地下功能 | 商业 | 不将该地块当作住宅开发范围 |
| 图号 | AW-S-0201a | 本次公示图版本线索 |
| 图签日期、比例 | 2024.01；1:300 | 与公示发布日期2024-03-25分开记录 |
| 说明栏单位 | 尺寸标注、标高、坐标单位为米 | 单位说明不等于坐标基准或投影参数 |

图上可见用地红线、建筑轮廓、局部尺寸和相邻01-02地块示意。本轮没有接受可用的全局界址坐标表，没有确认该图的深圳独立坐标/CGCS2000口径，也没有进行地理配准。

## 对当前研究的用途

本图可以支持01-01地块宗地、功能和图纸版本的核查，但不能替代2019年前后的历史拆除边界。地块建设范围、更新单元范围、历史拆除范围及周边既有住宅必须分开。

正式处理组及距离计算保持不变，仍待独立核定。下一步优先取得历史拆除范围的原CAD或可公开界址表及坐标说明；如仅取得01-01商业地块CAD，也应单独归档，不能扩展为全部项目红线。

## 可复核命令

本地归档目录为`D:/js/shenzhen-housing-policy-predictability-proposal/data/raw/`，文件名分别为`mutoulong_0101_notice_20261014.html`与`mutoulong_0101_plan_20261014.pdf`。原件未进入公开Git仓库，其他复核者可从上面的官方链接取得对应文件，再与台账哈希比较。

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'D:/js/shenzhen-housing-policy-predictability-proposal/data/raw/mutoulong_0101_plan_20261014.pdf'
```

```python
import fitz
document = fitz.open("mutoulong_0101_plan_20261014.pdf")
assert len(document) == 1
assert document.embfile_count() == 0
page = document[0]
assert len(page.get_text()) == 0
assert len(page.get_drawings()) == 0
assert len(page.get_images(full=True)) == 1
```

机器检查与人工读图结果分列记录在[核查JSON](mutoulong_0101_2024_audit.json)。未向政府或开发主体提交资料申请，也未购买或执行第三方CAD工具。
