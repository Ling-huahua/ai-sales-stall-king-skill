# 卖货物料生成器 Skill

这是一个 Codex Skill：用户上传一张或多张商品图后，帮助生成小红书、闲鱼、朋友圈、抖音等平台可发布的卖货物料，包括平台图片组、文案、短视频口播、分镜表、主播动作卡、定价策略和客服话术。

## 安装方式

在 Codex 里让助手安装这个 skill：

```text
请从 https://github.com/YOUR_GITHUB_USERNAME/ai-sales-stall-king-skill/tree/main/skills/ai-sales-stall-king 安装这个 skill
```

安装完成后，重启 Codex。

## 手动安装

也可以手动复制到 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R skills/ai-sales-stall-king ~/.codex/skills/ai-sales-stall-king
```

然后重启 Codex。

## 调用方式

安装后，可以在 Codex 输入框里用 `$` 调用：

```text
$ai-sales-stall-king 根据我上传的商品图生成卖货物料
```

也可以直接说：

```text
请用卖货物料生成器，根据我上传的商品图生成卖货物料。
```

## 使用提示

第一次使用时，skill 会先问两个轻量选择题：

- A：你要发哪些平台
- B：你需要哪些内容

建议先生成第一版整体效果；如果想让第二版更准，再补充成本价、尺码、库存、发货地、材质成分、更多细节图等信息。

