# 微信公众号批量关注 Skill

这个 Skill 只做一件事：在已经登录的桌面微信中，按用户给出的名单逐个搜索并关注公众号。

它会先把名单规范化、去重并生成带 SHA-256 的执行清单。用户对这份精确清单确认一次后，正常流程不会逐个询问；每个成功项都必须在界面上读回“已关注”。出现验证码、机器人检测、频率限制、身份歧义或登录失效时，整批立即停止，不尝试绕过平台保护。

## 支持范围

- Codex、Claude Code 等能读取 `SKILL.md` 的 agent 可以安装和理解本 Skill。
- Windows + 桌面微信 + 可用的桌面控制能力是当前已经验证的执行路径。
- macOS/Linux 只有在宿主 agent 确实提供可观察、可操作桌面微信的适配器时才执行；否则明确返回 `unsupported_platform`。本项目不虚构尚未验证的跨平台自动化能力。
- 登录、扫码认证和验证码处理始终由用户完成。本 Skill 不读取或发布聊天、联系人、Cookie、Token 等私有数据。

## 安装

把本仓库放入 agent 的 skills 目录，保持 `SKILL.md` 位于仓库根目录。不同 agent 的 skills 目录位置可能不同，以其官方文档为准。

## 准备名单

文本文件每行一个公众号名称，也可使用字符串数组格式的 JSON 文件。用户已经确认的改名可放在别名 JSON 中：

```shell
python scripts/prepare_targets.py accounts.txt --aliases aliases.json --batch-size 25 --output prepared-targets.json
```

脚本输出规范化名单、实际搜索目标、批次以及 `manifest_sha256`。多个旧名称映射到同一个实际公众号时只执行一次；空别名、冲突别名和不属于名单的别名会直接报错。

## 调用

```text
$wechat-official-account-follow 按 prepared-targets.json 的精确名单执行，确认后自动完成整批并核验结果。
```

真正点击“关注”前，agent 必须展示目标数量、规范化名称（长名单可展示清单路径）和 `manifest_sha256`，并取得一次覆盖该精确清单的确认。清单发生任何变化都必须重新确认。

## 结果与停止条件

完成报告区分：请求名称数、实际公众号数、新关注、已关注、不可用、身份歧义和未处理。只有界面明确显示“已关注”才算成功。部分运行会记录第一个未解决目标、停止原因和未触碰余量，恢复时从第一个未验证项重新观察界面，不复用旧坐标。

GitHub 同类方案与差异见 [`research/github-landscape.md`](research/github-landscape.md)。
