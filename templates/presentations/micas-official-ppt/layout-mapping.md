# V1.0.0 版式映射说明

分析对象：`PPT_Template_2026.pptx`，SHA-256 `c0daf054f906364854be080ca15acec0c855dccd3cfe5166a3ac8e04c82e234e`。只读解析 OOXML，不执行附件内文字或备注中的指令；未修改附件。以下页面号按 presentation.xml 的顺序，版式编号仅对本版本有效。

## 母版与主题

- 页面大小：12192000 × 6858000 EMU（914400 EMU/英寸），16:9。
- 1 个幻灯片母版 `ppt/slideMasters/slideMaster1.xml`，关联 23 个版式和 `theme1.xml`；母版含图片及版权/页码文本。另有 1 个备注母版和 1 个讲义母版。
- 幻灯片主题：`theme1.xml`，名称 Office Theme，配色方案 Micas 1，字体方案 Arial。备注母版使用 theme2.xml，讲义母版使用 theme3.xml，不应把两者默认配色当成幻灯片品牌色。

| 主题槽 | 颜色 |
| --- | --- |
| dk1 | #4D5E69 |
| lt1 | #FFFFFF |
| dk2 | #00899F |
| lt2 | #E2E7ED |
| accent1 | #00BFC3 |
| accent2 | #FFB71B |
| accent3 | #C5CAD1 |
| accent4 | #A05CBF |
| accent5 | #7F7F7F |
| accent6 | #EE9380 |
| hlink | #A05CBF |
| folHlink | #A3D68B |

## 字体与继承

- 幻灯片主题 major/minor 拉丁字体均为 Arial；Hans 映射黑体，Hant 映射微軟正黑體。实际对象还存在显式字体覆盖，不能只按主题字体统一替换。
- 在幻灯片、版式、母版 XML 中发现的非空 typeface（含符号与主题引用）：
  `+mn-cs`, `+mn-ea`, `+mn-lt`, `Arial`, `Century Gothic`, `Montserrat Light`, `Montserrat Medium`, `微软雅黑`
- 未嵌入字体；字体引用不等于本机已安装。备注主题为 Helvetica/Calibri，讲义主题为 Calibri Light/Calibri。
- 解析顺序应考虑文本 run/段落直接格式、页面占位符、版式、母版与主题。保留字号、段落层级、缩进、颜色、裁剪及变换；不能因同为 body 就合并字段。

## 全部版式与占位符

占位符格式为 `type:idx`；缺省 type 为 obj，缺省 idx 为 0。没有占位符不代表没有文字，章节页的标题就在普通形状中。

| 版式部件 | 原始名称 | 占位符 | 示例页 |
| --- | --- | --- | --- |
| slideLayout1.xml | 1_Thank You | 无 | 1 |
| slideLayout2.xml | Cover 1 | body:10, body:21, body:22 | 2 |
| slideLayout3.xml | Cover 3a | body:10, body:21, body:22 | 3 |
| slideLayout4.xml | Cover 4 | body:10, body:21, body:22, pic:23 | 未实例化 |
| slideLayout5.xml | One column - color block title | body:1, title:0, body:10 | 4 |
| slideLayout6.xml | One column - subtitle - color block title | body:12, title:0, body:11, body:1 | 5 |
| slideLayout7.xml | Two column color block title | body:1, body:12, body:13, title:0 | 6 |
| slideLayout8.xml | Two column - subtitle - color block title | body:12, body:13, body:11, body:1, title:0 | 7 |
| slideLayout9.xml | One column | title:0, body:12, body:13 | 8 |
| slideLayout10.xml | One column - subtitle | body:10, body:11, title:0, body:12 | 9 |
| slideLayout11.xml | Two column  | body:1, body:12, title:0, body:13 | 10 |
| slideLayout12.xml | 1_Two column - subtitle | title:0, body:1, body:12, body:13, body:11 | 11 |
| slideLayout13.xml | Section Break 1 | 无 | 未实例化 |
| slideLayout14.xml | Section Break 2 | 无 | 13 |
| slideLayout15.xml | Photo bottom - text top | title:0, body:1, pic:21, body:10 | 12 |
| slideLayout16.xml | Solid color block left - 5 text boxes right | body:1, body:21, body:22, body:23, body:24, body:25, body:26, body:27, body:28, body:29, title:0, body:10 | 未实例化 |
| slideLayout17.xml | Photo left - 6 text blocks right | body:1, body:22, body:23, body:24, body:25, body:26, body:27, body:28, body:29, body:30, body:31, body:32, body:10, body:33 | 未实例化 |
| slideLayout18.xml | 1Photo left - 4 text blocks right | pic:21, body:23, body:24, body:25, body:26, body:27, body:28, body:29, body:30, body:10, title:0 | 未实例化 |
| slideLayout19.xml | Tombstones 1 | pic:21, pic:22, pic:23, pic:24, body:1, body:25, body:26, body:27, body:28, body:31, body:29, body:30, title:0, body:10 | 未实例化 |
| slideLayout20.xml | Our Team 4-Up | title:0, pic:21, body:1, body:22, pic:23, body:24, body:25, pic:26, body:27, body:28, pic:29, body:30, body:31, body:10 | 14 |
| slideLayout21.xml | Thank You | body:10, body:11, body:12, body:13, body:14 | 15 |
| slideLayout22.xml | 空白 | body:10, body:11 | 未实例化 |
| slideLayout23.xml | 1_空白 | dt:10, ftr:11, sldNum:12 | 未实例化 |

## 后续智能转换的语义映射建议

| 输入用途 | 目标与字段 |
| --- | --- |
| 封面 | L2/L3：body:22 标题、body:10 演讲者/副标题、body:21 日期；L4 另有 pic:23 |
| 目录 | 优先复制第 3 页示例并定点替换文本；不要只新建 L3 后假设已有 CONTENTS 目录内容 |
| 单栏 | L5 正文 body:1、演示名称 body:10；L6 正文 body:1、副标题 body:11、演示名称 body:12；L9 正文 body:13、演示名称 body:12；L10 正文 body:10、副标题 body:11、演示名称 body:12；标题均 title:0 |
| 双栏 | L7/L8/L11/L12：左右正文 body:1/body:12，演示名称 body:13；L8/L12 副标题 body:11；标题 title:0 |
| 图文 | L15：title:0、正文 body:1、图 pic:21、演示名称 body:10；L16–L19 为多文本/图文变体，按下列对象清单核对 |
| 章节 | L13/L14：普通形状内 Add Section Title / Add Subtitle，不可用占位符 API 盲填；第 13 页本身无形状，内容来自版式 |
| 团队 | L20：title:0；四人 (照片,姓名,职务) 分别为 (pic:21,body:1,body:22)、(pic:23,body:24,body:25)、(pic:26,body:27,body:28)、(pic:29,body:30,body:31)；body:10 为演示名称 |
| 结束 | L21：body:10 致谢、body:11/12 第一联系人/详情、body:13/14 第二联系人/详情；网站是普通形状；L1 无占位符，不应作为联系人页 |

这些是后续实现建议，不是已完成的转换能力。应以版本哈希、部件路径、占位符类型/idx 和具体对象共同定位，不能跨版式假定 idx 含义一致。普通形状 ID 只在所属部件中有效。对标题过长、正文过量、缺图或未知用途应提示人工选择或拆页，不能静默删减。保留母版、主题、媒体关系与装饰对象；不要把所有文本节点当作可替换内容。

## 对象定位清单

以下为各版式的文本/占位符对象。坐标为对象自身显式 xfrm 的 EMU（x,y,cx,cy）；缺省表示需要继承或该层未声明，并非零。存在组变换时还需应用组坐标变换。此清单辅助实现字段定位，不替代渲染验收。

### L1 — 1_Thank You

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |

### L2 — Cover 1

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 30 / Body Level One… | body:10 | Add presenter name or subtitle | 4558897,4348364,6891294,781419 |
| 31 / Text Placeholder 11 | body:21 | Add date or secondary info | 4558897,5354218,6894795,623889 |
| 45 / Body Level One… | body:22 | Add Presentation Title Here | 4558897,2761488,6950086,1545336 |

### L3 — Cover 3a

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 17 / Body Level One… | body:10 | Add presenter name or subtitle | 687733,3844272,6891294,781419 |
| 24 / Text Placeholder 11 | body:21 | Add date or secondary info | 687733,4850126,6894795,623889 |
| 25 / Body Level One… | body:22 | Add Presentation Title Here | 687733,2257396,6950086,1545336 |

### L4 — Cover 4

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 7 / Body Level One… | body:10 | Add presenter name or subtitle | 1700503,4020119,7536261,781419 |
| 8 / Text Placeholder 11 | body:21 | Add date or secondary info | 1687252,4880199,5667705,623889 |
| 9 / Body Level One… | body:22 | Add Presentation Title Here | 1700504,2433243,7589270,1545336 |
| 16 / Picture Placeholder 15 | pic:23 |  | 7663395,1569436,4537306,5431097 |

### L5 — One column - color block title

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 11 / TextBox 10 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 16 / Body Level One… | body:1 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 584647,964436,10925181,4954815 |
| 17 / Add Title | title:0 | Add Title | 586317,231689,10916086,617397 |
| 3 / Text Placeholder 2 | body:10 | Presentation Title | 1709738,6482631,2782887,265113 |

### L6 — One column - subtitle - color block title

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 11 / TextBox 10 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 16 / Text Placeholder 2 | body:12 | Presentation Title | 1709738,6482631,2782887,265113 |
| 19 / Add Title | title:0 | Add Title | 586317,231689,10916086,617397 |
| 24 / Text Placeholder 3 | body:11 | Add Subtitle | 584647,963391,10907712,319087 |
| 25 / Body Level One… | body:1 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 584647,1410839,10886343,4419600 |

### L7 — Two column color block title

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 3 / TextBox 2 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 10 / Body Level One… | body:1 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 584647,958217,5221067,4954815 |
| 11 / Body Level One… | body:12 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 6172200,958217,5221067,4954815 |
| 9 / Text Placeholder 2 | body:13 | Presentation Title | 1709738,6482631,2782887,265113 |
| 17 / Add Title | title:0 | Add Title | 586317,231689,10916086,617397 |

### L8 — Two column - subtitle - color block title

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 11 / TextBox 10 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 15 / Body Level One… | body:12 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 6172200,1411786,5221067,4444054 |
| 16 / Text Placeholder 2 | body:13 | Presentation Title | 1709738,6482631,2782887,265113 |
| 17 / Text Placeholder 3 | body:11 | Add Subtitle | 584647,963391,10907712,319087 |
| 18 / Body Level One… | body:1 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 584647,1410839,5320853,4419600 |
| 21 / Add Title | title:0 | Add Title | 586317,231689,10916086,617397 |

### L9 — One column

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 9 / Add Title | title:0 | Add Title | 586317,231689,10916086,617397 |
| 11 / TextBox 10 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 17 / Text Placeholder 2 | body:12 | Presentation Title | 1709738,6482631,2782887,265113 |
| 18 / Body Level One… | body:13 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 584647,863012,10925181,4954815 |

### L10 — One column - subtitle

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 7 / Body Level One… | body:10 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 584647,1309987,10925181,4752014 |
| 8 / Text Placeholder 3 | body:11 | Add Subtitle | 584647,853157,10907712,319087 |
| 14 / Add Title | title:0 | Add Title | 586317,231689,10916086,617397 |
| 17 / TextBox 16 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 22 / Text Placeholder 2 | body:12 | Presentation Title | 1709738,6482631,2782887,265113 |

### L11 — Two column 

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 10 / Body Level One… | body:1 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 584647,852127,5221067,4965700 |
| 11 / Body Level One… | body:12 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 6172200,852127,5359400,4965700 |
| 9 / Add Title | title:0 | Add Title | 586317,231689,10916086,617397 |
| 18 / TextBox 17 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 23 / Text Placeholder 2 | body:13 | Presentation Title | 1709738,6482631,2782887,265113 |

### L12 — 1_Two column - subtitle

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 11 / TextBox 10 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 14 / Add Title | title:0 | Add Title | 586317,231689,10916086,617397 |
| 9 / Body Level One… | body:1 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 584647,1309835,5221067,4765419 |
| 15 / Body Level One… | body:12 | Body Level OneBody Level TwoBody Level ThreeBody Level FourBody Level Five | 6172200,1309835,5221067,4765419 |
| 22 / Text Placeholder 2 | body:13 | Presentation Title | 1709738,6482631,2782887,265113 |
| 23 / Text Placeholder 3 | body:11 | Add Subtitle | 584647,853158,10907712,319087 |

### L13 — Section Break 1

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 16 / Add Title | 普通形状 | Add Section Title | 1532579,1239865,5875386,1587784 |
| 21 / Add Title | 普通形状 | Add Subtitle | 1532579,2887776,5236521,1587784 |

### L14 — Section Break 2

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 29 / Add Title | 普通形状 | Add Section Title | 1532579,1539789,5875386,1587784 |
| 30 / Add Title | 普通形状 | Add Subtitle | 1532579,3187700,5236521,1587784 |

### L15 — Photo bottom - text top

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 54 / Click to Add Title | title:0 | Click to Add Title | 335279,1329829,3698242,640699 |
| 55 / Body Level One… | body:1 | Click to add text | 4412512,808352,6341213,1682434 |
| 56 / Picture Placeholder 7 | pic:21 |  | 0,3234519,12192000,3623482 |
| 7 / TextBox 6 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |
| 8 / Text Placeholder 2 | body:10 | Presentation Title | 1709738,6482631,2782887,265113 |

### L16 — Solid color block left - 5 text boxes right

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 69 / Body Level One… | body:1 | Click to add subtitle | 4840642,538525,3307679,426395 |
| 70 / Text Placeholder 10 | body:21 | Click to add text | 4840642,918030,3307679,1370672 |
| 71 / Text Placeholder 10 | body:22 | Click to add subtitle | 8518298,538525,3307679,426395 |
| 72 / Text Placeholder 10 | body:23 | Click to add text | 8518298,918030,3307679,1370672 |
| 73 / Text Placeholder 10 | body:24 | Click to add subtitle | 4840642,2506260,3307679,428892 |
| 74 / Text Placeholder 10 | body:25 | Click to add text | 4840642,2888262,3307679,1371601 |
| 75 / Text Placeholder 10 | body:26 | Click to add subtitle | 8518298,2506260,3307679,428892 |
| 76 / Text Placeholder 10 | body:27 | Click to add text | 8518298,2888262,3307679,1371601 |
| 77 / Text Placeholder 10 | body:28 | Click to add subtitle | 4840642,4528932,3307679,428892 |
| 78 / Text Placeholder 10 | body:29 | Click to add text | 4840642,4910933,3307679,1450989 |
| 79 / Add Title | title:0 | Add Title | 0,1330960,4480560,1463040 |
| 20 / Text Placeholder 2 | body:10 | Presentation Title | 1709738,6482631,2782887,265113 |

### L17 — Photo left - 6 text blocks right

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 92 / Body Level One… | body:1 | Click to add subtitle | 4840642,538525,3307679,426395 |
| 93 / Text Placeholder 10 | body:22 | Click to add text | 4840642,918030,3307679,1370672 |
| 94 / Text Placeholder 10 | body:23 | Click to add subtitle | 8518298,538525,3307679,426395 |
| 95 / Text Placeholder 10 | body:24 | Click to add text | 8518298,918030,3307679,1370672 |
| 96 / Text Placeholder 10 | body:25 | Click to add subtitle | 4840642,2506260,3307679,428892 |
| 97 / Text Placeholder 10 | body:26 | Click to add text | 4840642,2888262,3307679,1371601 |
| 98 / Text Placeholder 10 | body:27 | Click to add subtitle | 8518298,2506260,3307679,428892 |
| 99 / Text Placeholder 10 | body:28 | Click to add text | 8518298,2888262,3307679,1371601 |
| 100 / Text Placeholder 10 | body:29 | Click to add subtitle | 4840642,4528932,3307679,428892 |
| 101 / Text Placeholder 10 | body:30 | Click to add text | 4840642,4910934,3307679,1356224 |
| 17 / Text Placeholder 10 | body:31 | Click to add subtitle | 8518298,4494798,3307679,428892 |
| 18 / Text Placeholder 10 | body:32 | Click to add text | 8518298,4876800,3307679,1371601 |
| 23 / Text Placeholder 2 | body:10 | Presentation Title | 1709738,6482631,2782887,265113 |
| 3 / Text Placeholder 2 | body:33 | Add Title | 150857,1513195,4213225,1128712 |

### L18 — 1Photo left - 4 text blocks right

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 89 / Picture Placeholder 8 | pic:21 |  | -2,0,4495803,6858000 |
| 94 / Text Placeholder 10 | body:23 | Click to add subtitle | 8518298,4182874,3307679,426395 |
| 95 / Text Placeholder 10 | body:24 | Click to add text | 8518298,4562379,3307679,1370672 |
| 96 / Text Placeholder 10 | body:25 | Click to add subtitle | 4840642,2015929,3307679,428892 |
| 97 / Text Placeholder 10 | body:26 | Click to add text | 4840642,2397931,3307679,1371601 |
| 98 / Text Placeholder 10 | body:27 | Click to add subtitle | 8518298,2015929,3307679,428892 |
| 99 / Text Placeholder 10 | body:28 | Click to add text | 8518298,2397931,3307679,1371601 |
| 100 / Text Placeholder 10 | body:29 | Click to add subtitle | 4840642,4184376,3307679,428892 |
| 101 / Text Placeholder 10 | body:30 | Click to add text | 4840642,4566377,3307679,1450989 |
| 19 / Text Placeholder 2 | body:10 | Presentation Title | 1709738,6482631,2782887,265113 |
| 20 / Add Title | title:0 | Add Title | 4850295,1099931,7063407,477078 |

### L19 — Tombstones 1

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 114 / Picture Placeholder 4 | pic:21 |  | 860447,2982740,603505,603505 |
| 115 / Picture Placeholder 4 | pic:22 |  | 3616080,2981420,603505,594361 |
| 116 / Picture Placeholder 4 | pic:23 |  | 6410742,2983163,603505,603505 |
| 117 / Picture Placeholder 4 | pic:24 |  | 9155487,3001928,594361,594360 |
| 118 / Body Level One… | body:1 | Click to add subtite | 740799,3608439,2510402,491510 |
| 119 / Text Placeholder 10 | body:25 | Click to add text | 740799,4127481,2510402,1704546 |
| 120 / Text Placeholder 10 | body:26 | Click to add subtitle | 3508580,3608439,2473121,491510 |
| 121 / Text Placeholder 10 | body:27 | Click to add text | 3508580,4127481,2485821,1704546 |
| 122 / Text Placeholder 10 | body:28 | Click to add subtitle | 6303400,3608439,2497701,491510 |
| 125 / Text Placeholder 10 | body:31 | Click to add text | 9071179,4127481,2523921,1704546 |
| 123 / Text Placeholder 10 | body:29 | Click to add text | 6303400,4127481,2485001,1704546 |
| 124 / Text Placeholder 10 | body:30 | Click to add subtitle | 9071179,3608439,2498521,491510 |
| 113 / Click to add title | title:0 | Click to add title | 838200,597991,10515600,994837 |
| 17 / Text Placeholder 2 | body:10 | Presentation Title | 1709738,6482631,2782887,265113 |

### L20 — Our Team 4-Up

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 383 / Click to add title | title:0 | Click to add title | 673100,544286,10883900,747930 |
| 384 / Picture Placeholder 9 | pic:21 |  | 897730,2427896,2099704,2115229 |
| 385 / Body Level One… | body:1 | Add name | 660400,4814561,2302433,447944 |
| 386 / Text Placeholder 10 | body:22 | Add title | 660400,5283200,2302434,447944 |
| 388 / Picture Placeholder 9 | pic:23 |  | 3667826,2427896,2099703,2115229 |
| 390 / Text Placeholder 10 | body:24 | Add name | 3474041,4814561,2302434,447944 |
| 391 / Text Placeholder 10 | body:25 | Add title | 3474040,5283200,2302433,447944 |
| 392 / Picture Placeholder 9 | pic:26 |  | 6437920,2427896,2099704,2115229 |
| 395 / Text Placeholder 10 | body:27 | Add name | 6244135,4814561,2302433,447944 |
| 396 / Text Placeholder 10 | body:28 | Add title | 6244135,5283200,2302434,447944 |
| 397 / Picture Placeholder 9 | pic:29 |  | 9208016,2427896,2099703,2115229 |
| 398 / Text Placeholder 10 | body:30 | Add name | 8992458,4814561,2302433,447944 |
| 399 / Text Placeholder 10 | body:31 | Add title | 8992458,5283200,2302433,447944 |
| 22 / Text Placeholder 2 | body:10 | Presentation Title | 1709738,6482631,2782887,265113 |
| 32 / TextBox 31 | 普通形状 | © 2026 Micas Networks   ／   ‹#› | 9847942,6516914,2073643,230830 |

### L21 — Thank You

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 4 / Text Placeholder 3 | body:10 | Thank you | 1673352,3072384,8842248,1361948 |
| 23 / Text Placeholder 3 | body:11 | Add Contact Name | 1673352,4800600,3257877,448056 |
| 24 / Text Placeholder 3 | body:12 | Add contact details | 1673352,5410200,3257877,448056 |
| 10 / Text Placeholder 3 | body:13 | Add Contact Name | 7391400,4800600,3257877,448056 |
| 12 / Text Placeholder 3 | body:14 | Add contact details | 7391400,5410200,3257877,448056 |
| 3 / TextBox 2 | 普通形状 | www.micasnetworks.com | 4876800,6259286,2371725,335915 |

### L22 — 空白

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 21 / 文本占位符 20 | body:10 | 编辑母版文本样式 | 731837,393895,5473235,281104 |
| 22 / 文本占位符 20 | body:11 | 编辑母版文本样式 | 731837,747971,5473235,174530 |

### L23 — 1_空白

| 对象 ID / 名称 | 占位符 | 文本提示 | 显式坐标 |
| --- | --- | --- | --- |
| 2 / 日期占位符 1 | dt:10 | 2026/5/13 | 838200,6356350,2743200,365125 |
| 3 / 页脚占位符 2 | ftr:11 |  | 4038600,6356350,4114800,365125 |
| 4 / 灯片编号占位符 3 | sldNum:12 | ‹#› | 8610600,6356350,2743200,365125 |
