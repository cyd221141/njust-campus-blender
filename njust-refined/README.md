# 南京理工大学校园 · 精细化升级

打开 **NJUST_Final.blend**，使用场景 **Refined_Version**。原始场景保存在同一文件的 **Original_Backup**，另有 v00—v07 阶段文件可回退。

阶段文件保存在本机完整项目目录。`NJUST_Delivery.zip` 为便携交付包，包含最终工程、静帧、成片、脚本和文档；原始场景仍内嵌在最终工程中。

这是基于原模型布局的校园建筑可视化作品。建筑体量、校园距离与部分地标轮廓仍沿用艺术化原型，不应作为测绘级数字孪生或实际导航地图。

## 查看成果

- `index.html`：图片与视频展示页，可用浏览器打开。
- `renders/01_Day_Aerial.png`—`10_Lake.png`：10 张 Cycles 高清静帧。
- `animation/NJUST_Campus_Flythrough_18s.mp4`：18 秒、24 fps、1080p 漫游。
- `修改报告.md`：改动、参数、来源与未解决问题。

## Blender 操作

1. 在 Text Editor 中选择内嵌文本 **campus_controls.py**，点击 Run Script。
2. 在 3D View 中按 **N**，打开 **NJUST** 页签，可以切换 DAY / GOLDEN HOUR / NIGHT、Cycles / Eevee 与镜头。此脚本只注册本工程的界面，不需要安装插件。
3. 选择 `GN_` 开头的对象，在 Modifier 面板调整 Density、Random Seed、Scale Min、Scale Max、Rotation、Distance。Density 是已有采样点的保留概率，1 表示保留所有候选点。
4. 选择 **Cinematic** 镜头，时间范围 1—432，24 fps；按空格预览运动。正式出片使用下方脚本，每帧刷新近景细节 LOD。
5. 用户手动移动相机后，重新点击当前镜头按钮即可刷新普通物体的近景细节显示；植物 Geometry Nodes 持续跟踪活动相机参考点。

## 重渲染

在项目目录运行 PowerShell（根据安装位置修改 Blender 路径）：

```powershell
& 'D:\blender\blender.exe' -b NJUST_Final.blend -t 6 -P scripts/render_batch.py
& 'D:\blender\blender.exe' -b NJUST_Final.blend -t 6 -P scripts/render_animation.py
```

两个命令应**顺序执行**。动画脚本会跳过已经存在的 `frame_####.png`；需要从头重渲染时，将旧帧移动到备份文件夹后再运行。勿将不同版本的帧混用。

全部帧完成后，运行 `scripts/encode_video.ps1` 编码 MP4。本机脚本可以使用已准备的 FFmpeg；在其他机器上重做视频编码，需要先让 `ffmpeg` 命令可用。交付 ZIP 不包含逐帧 PNG 或 FFmpeg 程序，成片已经包含在内。

HDRI、标识图像与中文字体已随 `.blend` 打包。脚本使用 Blender 自带 Python；模型浏览和修改不依赖本地 `.runtime`。中文字体的再分发须遵守字体提供方许可。
