# NJUST — 从模型到世界

48 秒双画幅校园建模展示短片。Blender 实际工程渲染 + Remotion 帧动画排版 + 本地合成电子配乐。

## 成片

- `output/NJUST_Bilibili_48s_1080p.mp4`：1920 × 1080，30 fps。
- `output/NJUST_Douyin_48s_1080p.mp4`：1080 × 1920，30 fps，独立竖版构图。
- `output/NJUST_Bilibili_Cover.png` / `NJUST_Douyin_Cover.png`：对应封面。
- `output/发布文案.md`：发布标题、简介、话题与章节时间。
- `index.html`：本地双版本预览页。

## 创作说明

影片前半部分用实际工程资产演示原始模型、线框、建筑体块、立面窗格、植被和材质升级。该部分是制作步骤重演，不是当时操作 Blender 的屏幕录像。后半部分为实际模型的校门、林间、湖桥及昼夜镜头。校园为艺术化压缩布局，并非测绘模型。

新增的建筑生长、夕照环绕、林间运动、夜景环绕镜头均由 Blender 渲染。竖版的全景镜头使用单独竖画幅相机渲染，并做缓慢推进；近景按竖版重新取景。

配乐由 `scripts/compose_score.py` 本地合成，120 BPM、48 kHz、立体声，包含鼓组、琶音、和弦、低音及过渡音效。未使用外部歌曲或音效采样。成片无旁白，字幕烧录。

## 继续编辑

本机：Node 位于 `D:/nodejs`，浏览器使用本机 Chrome。

```powershell
cd D:\entertain\njust-film
npm run dev
```

主合成 `NJUST-Bilibili`、`NJUST-Douyin` 均为 1440 帧；`Editable-Scenes` 中各片段可单独预览。

```powershell
npx remotion render NJUST-Bilibili output/NJUST_Bilibili_48s_1080p.mp4 --codec=h264 --crf=18 --audio-bitrate=320k
npx remotion render NJUST-Douyin output/NJUST_Douyin_48s_1080p.mp4 --codec=h264 --crf=18 --audio-bitrate=320k
```

源文件：`src/Film.tsx` 控制顺序；`Hook.tsx`、`Process.tsx`、`Campus.tsx` 控制镜头与文字；`Shared.tsx` 控制画幅适配、运动、字体、颜色及叠加层。所有动画均由帧数确定。

`scripts/render_film_assets.py` 读取 `D:/entertain/njust-refined/NJUST_Final.blend`，不覆盖该模型；`scripts/encode_assets.py` 将 Blender 帧序列编码为源镜头。`public/media`、`public/audio`、`public/fonts` 为合成依赖；`process` 保存新增原始渲染帧。字体来自本机 Windows，仅用于本项目渲染。

## 工作流参考

研究并采用了 [Remotion 官方视频制作 skills](https://github.com/remotion-dev/skills) 的分场景合成、帧动画、多画幅排版及本地资源工作流。只读取相关文档，未安装全局 skill。审查记录在 `references/SKILL_REVIEW.md`。

- https://www.remotion.dev/docs/cli/render
- https://www.remotion.dev/docs/media/video

最终文件信息与音视频解码检查保存在 `reports/delivery_validation.json`。
