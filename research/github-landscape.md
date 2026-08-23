# GitHub 同类工具调研：桌面微信批量关注公众号

调研日期：2026-08-23

## 结论

在本次检索到的公开 GitHub 仓库中，只有
[`Hello-Mr-Crab/pywechat`](https://github.com/Hello-Mr-Crab/pywechat)
明确实现了“打开公众号搜索、输入名称、打开结果、可选点击关注”这一核心链路。它是最直接的实现参考，但其现有函数不等同于一个可无人值守执行任意名单的可靠 skill：源码按名称正则选择首个结果，点击关注后直接返回，未见精确主体校验、关注状态回读、断点恢复、批次去重、验证码或频率限制检测。

`wxauto`、`WeChatFerry/wcferry`、`PyWxDump` 均不能从当前 README 或源码证明具备搜索并关注公众号的完整能力。没有找到任何仓库能可靠证明可以绕过微信验证码或风控；这不应成为本 skill 的功能或承诺。

### “后台订阅”与个人微信“关注”不是同一状态

本次没有找到微信官方公开 API 或开源项目，能够在不控制个人微信客户端、也不使用内部协议/Hook 的情况下，让任意公众号进入个人微信账号的关注列表。微信公众平台公开 API 使用运营方公众号的 `appid`、`secret` 和 `access_token` 管理该运营方自己的粉丝、内容与消息，并不提供“个人微信关注任意其他公众号”的接口：[获取 Access token](https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html)、[获取用户列表](https://developers.weixin.qq.com/doc/offiaccount/User_Management/Getting_a_User_List.html)。

GitHub 上确实存在跨平台的服务端“订阅”，但它们订阅的是文章源：

- [`adennng/wechat-query-skill`](https://github.com/adennng/wechat-query-skill) 通过 `/api/public/searchbiz` 与 `/api/rss/subscribe` 建立服务侧文章订阅，需要 Docker，以及公众号管理员微信扫码登录；它不改变个人微信关注列表。
- [`cq0206/wechat2rss`](https://github.com/cq0206/wechat2rss) 基于微信读书会话生成 RSS，可用 Docker 跨 Windows、macOS、Linux 部署；添加源需要微信公众号分享链接，README 明确提示添加过快会被封控。它同样不改变个人微信关注列表。

因此，“后台优先”只有在用户接受“后台文章订阅”作为目标时才成立。如果验收标准仍是个人微信资料页显示 `已关注`，目前有一手代码证据的非 Hook 路径仍是桌面 UI 自动化。

## 对比矩阵

| 项目 | 当前资料声明的微信版本 | 搜索公众号 | 点击关注 | 注入 / Hook | 风控绕过 | 维护与许可证 | 作为本 skill 基础的适合度 |
|---|---|---|---|---|---|---|---|
| [Hello-Mr-Crab/pywechat](https://github.com/Hello-Mr-Crab/pywechat) | 3.9.12.x、4.1.6+；Windows 7/10/11 | **是**。`search_official_account` 打开公众号入口并输入名称 | **是**。`subscribe=True` 时点击关注按钮 | README 明确称 pure UI Automation、不涉及逆向 Hook | 未证明；文档反而提醒避免频繁自动化 | 2026-08-20 仍有提交；LGPL-2.1 | **高，适合参考交互路径；不宜原样作为无人值守批处理实现** |
| [cluic/wxauto](https://github.com/cluic/wxauto) | README 仅声明微信 3.9.X | 未证明；源码 `ContactWnd.Search` 只声明“搜索好友” | 未证明 | UI Automation；未见该链路需要注入/Hook | 未证明 | 2026-04-13 最新提交；Apache-2.0；README 禁止生产和商业用途 | **低**。交互原语可参考，但版本和能力均不满足当前目标 |
| [lich0821/WeChatFerry](https://github.com/lich0821/WeChatFerry) | 最新公开版本 `v39.5.2`；README 版本规则表明 `39` 对应微信 3.9 | 未证明 | 未证明 | **是**。README 将 `sdk` 标为“注入及启动模块” | 未证明 | 仓库已归档；最后提交 2026-03-21，最后 release 2026-03-28；MIT | **低**。RPC/数据库能力丰富，但没有目标动作，且 Hook 与当前无注入方案方向相反 |
| [xaoyaoo/PyWxDump](https://github.com/xaoyaoo/PyWxDump) | 当前仓库不再提供版本支持 | 未证明 | 未证明 | 当前代码已删除，无法从现仓库验证 | 未证明 | 作者于 2025-10-20 删除全部代码和历史，明确“不再可用、无技术支持”；当前无许可证文件 | **不适合** |
| [adennng/wechat-query-skill](https://github.com/adennng/wechat-query-skill) | 不控制个人桌面微信 | 可通过公众号后台接口搜索 | 只能添加服务侧文章订阅，不是微信账号“关注” | Docker 服务 + 公众号后台登录态 | 未证明 | 2026-04-13 最新提交；仓库许可证元数据未识别 | **场景不等价**。可参考 skill 组织方式，不能实现本目标 |
| [cq0206/wechat2rss](https://github.com/cq0206/wechat2rss) | 不控制个人桌面微信；Docker 跨平台 | 通过分享链接添加文章源 | RSS 文章订阅，不是微信账号“关注” | 微信读书扫码会话 | README 明示添加过快会封控 | MIT；支持 Docker 部署 | **适合跨平台文章采集，不适合个人关注列表变更** |

维护时间取自对应仓库截至调研日可见的最新提交或 release。它只说明公开仓库近期活动，不代表兼容性或生产支持承诺。

## 一手证据

### 1. pywechat：唯一直接命中核心动作的项目

- README 声明它基于 `pywinauto` 做 Windows PC 微信 pure UI Automation，不涉及逆向 Hook，并声明支持微信 3.9.12.x 与 4.1.6+：[`README.md`](https://github.com/Hello-Mr-Crab/pywechat/blob/73e09e07170ea84c54c26bc5306f373a16ea839f/README.md#L5-L17)。
- 源码的 `search_official_account(name, ..., subscribe=False)` 会打开搜索、点击“公众号”、输入名称、回车、按 `title_re=name` 找结果；当 `subscribe=True` 且关注按钮存在时执行 `click_input()`：[`WeChatTools.py`](https://github.com/Hello-Mr-Crab/pywechat/blob/73e09e07170ea84c54c26bc5306f373a16ea839f/src/pyweixin/WeChatTools.py#L1503-L1538)。
- 该实现只等待结果和按钮后点击并返回。上述函数内没有精确昵称/认证主体二次核验，也没有点击后的“已关注”回读、批次状态或人机挑战处理。这是对该段源码的直接观察，不是对仓库其他未检索代码的绝对否定。
- 微信 4.1 文档说明：新账号可能没有可用 UI 树，只能使用 UI 树可见账号或 OCR；同时建议不要频繁添加好友或发送骚扰信息：[`Weixin4.0.md`](https://github.com/Hello-Mr-Crab/pywechat/blob/73e09e07170ea84c54c26bc5306f373a16ea839f/Weixin4.0.md)。
- 许可证为 LGPL-2.1：[`LICENSE`](https://github.com/Hello-Mr-Crab/pywechat/blob/73e09e07170ea84c54c26bc5306f373a16ea839f/LICENSE)。因此可参考其可见交互流程；若复制或链接其代码，需要单独审查 LGPL 义务。

### 2. wxauto：有 UI Automation 和好友搜索，但没有公众号关注证据

- README 只声明 Windows 与微信 3.9.X，并明确项目用于 UIAutomation 技术交流，禁止实际生产和商业用途：[`README.md`](https://github.com/cluic/wxauto/blob/05e5a52379c99f401dc512acfdd811b3d701da8b/README.md#L1-L19)。
- `ContactWnd.Search` 的注释和实现仅说明“搜索好友”，操作通讯录搜索框：[`elements.py`](https://github.com/cluic/wxauto/blob/05e5a52379c99f401dc512acfdd811b3d701da8b/wxauto/elements.py#L581-L613)。当前公开 API 中没有查到“公众号搜索并点击关注”的对应方法。
- 许可证文件为 Apache-2.0：[`LICENSE`](https://github.com/cluic/wxauto/blob/05e5a52379c99f401dc512acfdd811b3d701da8b/LICENSE)。许可证允许性不消除 README 另列的用途限制，公开发布前不应将其当作可直接复用的生产依赖。

### 3. WeChatFerry / wcferry：能力面广，但目标动作缺失且依赖注入

- README 功能清单包括登录、联系人、数据库、消息、朋友圈、好友申请和群成员操作，但没有列出搜索或关注公众号：[`README.MD`](https://github.com/lich0821/WeChatFerry/blob/0f5c60a034fcac234cabd000b49c9200defa7f7d/README.MD#L17-L46)。
- README 的运行示例加载 `sdk.dll`，项目结构明确把 `sdk` 称为“注入及启动模块”：[`README.MD`](https://github.com/lich0821/WeChatFerry/blob/0f5c60a034fcac234cabd000b49c9200defa7f7d/README.MD#L146-L185)。
- 最新 release 是 [`v39.5.2`](https://github.com/lich0821/WeChatFerry/releases/tag/v39.5.2)，README 的版本规则说明 `39` 对应微信 3.9：[`README.MD`](https://github.com/lich0821/WeChatFerry/blob/0f5c60a034fcac234cabd000b49c9200defa7f7d/README.MD#L204-L217)。仓库主页当前显示已归档。
- 许可证为 MIT：[`LICENSE`](https://github.com/lich0821/WeChatFerry/blob/0f5c60a034fcac234cabd000b49c9200defa7f7d/LICENSE)。

### 4. PyWxDump：当前官方仓库已撤除，不能作为依赖

作者在当前 README 中声明于 2025-10-20 删除全部代码和提交历史，项目不再可下载、不可用且不再提供支持：[`README.md`](https://github.com/xaoyaoo/PyWxDump/blob/7f635fbacb2f346f2bbc9f94f6c956e2b07aad54/README.md#L1-L20)。因此无法从当前官方仓库验证旧版本是否曾间接支持相关行为，也不应基于非官方镜像恢复依赖。

### 5. wechat-query-skill：名字相近，实际是另一类“订阅”

其 README 要求用户拥有一个微信公众号，并由公众号管理员扫码登录；流程通过 `/api/public/searchbiz` 搜索，再用 `/api/rss/subscribe` 建立服务侧文章订阅：[`README.md`](https://github.com/adennng/wechat-query-skill/blob/eb0bfd97321b75f2197b66d895db835cbd021335/README.md#L1-L45)。这不是在已登录的个人桌面微信中点击“关注”。

### 6. wechat2rss：跨平台后台文章订阅，但不是个人关注

README 将项目定义为基于微信读书的微信公众号 RSS 生成器，使用 Docker 部署、扫码登录微信读书账号，并通过公众号分享链接添加源；它还明确提示添加频率过高可能触发封控：[`README.md`](https://github.com/cq0206/wechat2rss#readme)。其优势是服务端定时更新、跨平台和无人值守采集，代价是语义变成 RSS 文章源订阅，不能作为个人微信 `已关注` 的证明。

## 其他接近但不等价的项目

- [`fanyuantaier/wechatauto-replica`](https://github.com/fanyuantaier/wechatauto-replica)：README 声明面向微信 4.1.12+，包含本地数据库读取、UIA/OCR 发消息及开启 `Weixin.dll` Qt accessibility gate，但没有公众号搜索/关注 API 的一手证据；维护者还说明后续可投入时间有限。[README](https://github.com/fanyuantaier/wechatauto-replica/blob/main/README.md)
- [`raphael2025/weixin-auto-send`](https://github.com/raphael2025/weixin-auto-send)：已登录微信 4.x 下用 OCR/模拟输入搜索联系人或群并发消息；未证明支持公众号关注。[README](https://github.com/raphael2025/weixin-auto-send/blob/main/README.md)
- [`LAVARONG/wechat-automation-api`](https://github.com/LAVARONG/wechat-automation-api)：提供 UIA、HTTP 队列和 Agent Skill，但 README 的搜索流程用于查联系人并发消息，未证明支持公众号关注。[README](https://github.com/LAVARONG/wechat-automation-api#readme)

## 对本 skill 的取舍建议

1. **保持单一职责**：输入公众号名称列表，在用户已登录的桌面微信中依次搜索并关注；不要纳入文章抓取、消息机器人、数据库解密或公众号后台订阅。
2. **交互实现优先沿用现有可用的桌面控制能力**：`pywechat` 证明纯 UI Automation 路径可行，但不必引入其完整依赖；尤其不要复制 LGPL 代码来换取一个很短的交互步骤。
3. **无人值守不等于绕过人机挑战**：正常页面之间不要求人工逐项确认；一旦出现验证码、登录失效、频率限制或不唯一结果，应安全停止并输出剩余名单，不能尝试绕过。
4. **补足直接项目缺失的可靠性层**：精确名称与账号类型核验、已关注跳过、点击后回读、幂等断点、逐项结果记录、失败后可继续。
5. **不要承诺固定微信版本永久可用**：UI 树、窗口层级和搜索页面会随客户端升级变化。skill 应在执行前检测已登录状态和关键控件，失败时报告不兼容，而不是盲点坐标。
6. **先固定验收语义再选实现**：个人微信 `已关注` 选择桌面 UI；后台文章源选择 Docker/RSS。不要在同一个“订阅”动词下静默切换结果。
7. **跨工具兼容不等于跨平台动作已实现**：`SKILL.md`、中文文档和标准库清单脚本可同时被 Codex、Claude Code 读取并在三大桌面系统安装，但个人微信关注仍需要目标系统上可调用的桌面自动化适配器。当前 GitHub 一手证据只证明 Windows 路径。

## 检索边界

本次只使用 GitHub 仓库 README、源码、许可证、提交和 release 等一手资料。未使用博客、聚合站或非官方代码镜像。没有找到第二个能够从公开源码明确证明完整执行“个人桌面微信搜索公众号并点击关注”的仓库；这表示本次检索未发现，不代表 GitHub 上绝对不存在。
