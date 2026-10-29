# 南京理工大学 · 紫金兰杉

**用 Blender 制作的春日校园微缩模型，以南京理工大学孝陵卫校园为原型。**

暖白色建筑、砖红色屋顶、青绿色水景和紫色二月兰共同组成一座可编辑的校园沙盘。包含致远楼、弧形图书馆、二道门意象、校风碑意象、兵器博物馆、教学街区、宿舍、运动场、水杉林、紫霞湖与三迎桥。

这是有资料依据的艺术化重构：校园范围、距离、地标尺寸和部分朝向经过压缩与重新编排；普通楼栋为风格化概括，校门、校风碑与博物馆为简化意象。不能用作校园导航、测绘或建筑施工依据。

## 交付内容

- `NJUST_Violet_Spring.blend`：Blender 原生工程，含材质、灯光、5 个预设相机。中文字体已打包，可继续编辑。
- `NJUST_Violet_Spring.glb`：便于其他三维软件和浏览器加载的模型。
- `index.html`：本地交互预览；双击 `打开校园预览.cmd` 启动，可旋转、缩放和切换地标视角。
- `renders/01_campus_hero.png`：校园整体，2800 × 2300。
- `renders/02_violet_garden.png`：水杉与二月兰，2100 × 1500。
- `renders/03_architecture.png`：校园建筑轴线，2100 × 1600。
- `renders/04_campus_plan.png`：俯视总览，2000 × 2000。
- `renders/05_lake_bridge.png`：紫霞湖与三迎桥，2100 × 1500。
- `build_campus.py`：确定性建模与渲染脚本，随机种子 1953。
- `scene_manifest.json`：模型对象、顶点和相机清单。

## 在 Blender 里使用

打开 `.blend` 后，使用鼠标中键旋转视图、滚轮缩放，数字小键盘 0 切回相机。右侧 Outliner 中按场景分组组织了建筑、道路、植被、水景与细部。独立树木使用共享网格，花瓣与窗框细节按材质合并，便于平衡编辑性与性能。

五个相机位于 `13 · Studio, lights & cameras` 集合。选中相机后按 Ctrl + 数字小键盘 0 设为当前相机，F12 渲染。工程采用 Blender 5.1.2、Cycles、OptiX GPU、AgX 色彩管理。没有兼容显卡时可在 Render Properties 选择 CPU。

重建命令（会覆盖本目录同名输出）：

```powershell
& 'D:\blender\blender.exe' --background --python '.\build_campus.py'
& 'D:\blender\blender.exe' --background '.\NJUST_Violet_Spring.blend' --python '.\export_preview.py'
```

## 参考资料

检索与制作日期：2026-09-09。以下照片只用于观察体量与景观特色，未贴到模型表面。

1. [南京理工大学本科招生信息网：校园地图](https://zsb.njust.edu.cn/detail?id=565) — 页面提供的 2025 年版校园地图；用于理解主要校园轴线、教学区、运动区、生活区及水域关系。
2. [南京理工大学钟声新闻网：理工大，何以为“大”](https://zs.njust.edu.cn/8d/f3/c4621a298483/page.htm) — 校方航拍、致远楼周边、图书馆、兵器博物馆、水杉与二月兰、三迎桥、时间广场照片；用于建模外形与配色参考。局部参考图片保存在 `references/official*.jpg`，版权归原作者及发布方。
3. [南京理工大学官微：最佳游览路线](https://www.sohu.com/a/421177646_675999) — 用于核对各地标名称及游览顺序。
4. [南京理工大学：办学特色综述](https://zs.njust.edu.cn/2024/0611/c4621a335520/page.psp) — 校园环境与建筑特色说明。
5. [二道门历史照片条目](https://commons.wikimedia.org/wiki/File:The_School_Motto_Gate_in_Nanjing_University_of_Science_and_Technology_2012-05.JPG) — 作者：猫猫的日记本，2012-05-05，CC BY-SA 3.0；核对校训门位置说明，原始图片未能在本地下载，未直接用于几何描摹。

网页预览使用本地 Three.js 依赖（MIT，许可证见 `vendor/THREE-LICENSE`）；不需要连接 CDN。预览效果与 Cycles 成片会有光照和材质差异，以 `renders` 中的图片为最终渲染效果。
