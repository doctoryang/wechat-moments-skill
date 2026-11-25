# WeChat Moments Skill · 朋友圈照片精选与发布

供 Codex 使用的中文技能：查看本地照片、精选排序、撰写配文，并在当前请求已授权且具备桌面操作能力时发布微信朋友圈、核验结果。

## 能做什么

- 浏览指定文件夹，结合人物、合影和环境挑选照片，避免重复。
- 根据画面写自然简洁的中文配文，安排九宫格或其他合适张数。
- 在可操作微信的环境中完成上传、检查与发布，避免重复提交。
- 没有桌面控制能力时交付选片和配文，并明确说明尚未发布。

这是一套给智能体的工作指令，附带本地缩略图脚本。它不自带微信接口、登录能力或完整的桌面自动化程序。安装技能不会自动获得微信控制权限。图片浏览脚本可在支持 Python/Pillow 的系统运行；微信桌面操作参考目前面向 Windows，其他系统需要自行适配工具与界面。

## 安装

下载本仓库，将 `skills/wechat-moments` 整个文件夹复制到 Codex 的技能目录：

- 设置了 `CODEX_HOME`：放入该目录的 `skills` 子目录。
- 没有设置：放入用户目录下的 `.codex/skills`。

最终结构应为 `.codex/skills/wechat-moments/SKILL.md`。如果已有同名技能，先比较内容再决定是否替换。

缩略图辅助脚本需要 Python 3.10 或更新版本及 Pillow。在仓库根目录运行：

```shell
python -m pip install -r requirements.txt
```

让 Codex 在技能列表中识别 `wechat-moments` 后即可使用；若列表尚未更新，重新打开会话。

## 使用示例

只准备素材：

```text
使用 $wechat-moments，查看我指定文件夹的照片，挑选适合朋友圈的九张，
排好顺序并写一段自然的配文，先不要发布。
```

授权发布：

```text
使用 $wechat-moments，把我指定文件夹里的照片精选后发到微信朋友圈。
微信已经登录，配文温暖简洁，保留当前可见范围。
```

在提示中提供实际照片路径。选图、写配文与发布是不同范围的请求；技能不会把某次发布授权用于未来的新照片。

## 单独生成照片总览

在仓库根目录运行，替换示例路径：

```shell
python skills/wechat-moments/scripts/contact_sheet.py "path/to/photos" "work/preview"
```

脚本只读取源目录第一层，按文件名排序，每页最多 18 张。支持 JPEG、PNG、WebP、BMP、TIFF，实际解码能力取决于 Pillow；HEIC 和视频不在此脚本支持范围内。预览会按 EXIF 方向显示，无法读取的图片会在索引中记录错误。

生成 `contact-001.jpg` 等预览及 `image-index.json`。索引包含原图绝对路径，可能暴露个人目录信息。请将输出放在源目录之外；重复运行会覆盖同名预览和索引，旧的多余预览页不会自动删除，请使用新的输出目录。不要把生成物或私人照片提交到公开仓库。

## 仓库结构

```text
skills/wechat-moments/
  SKILL.md                  技能入口
  agents/openai.yaml        Codex 展示信息
  references/windows-ui.md Windows 操作经验
  scripts/contact_sheet.py 照片总览脚本
tests/                      使用合成图片的脚本测试
requirements.txt            Pillow 依赖
LICENSE                     MIT 许可证
```

## 验证

```shell
python -m unittest discover -s tests -v
```

测试仅使用临时目录中的合成图片，不操作微信。微信发布流程需要在用户已授权的实际桌面环境中核验。

## 分享到 GitHub

将本目录内容作为仓库根目录上传即可，包括隐藏文件 `.gitignore`。无需上传上一段对话、个人照片或本地生成的预览。仓库未绑定特定账号，也未包含 GitHub 凭据。

## 许可证

[MIT](LICENSE)。项目与微信、腾讯及 OpenAI 无隶属或官方背书关系。
