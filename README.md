# Discord 聊天机器人配置指南

## 📢 免责声明
**此代码仅供学习参考，造成的任何影响或账号封禁与作者无关！**

## ⚙️ 环境配置说明

### 基本设置
| 参数 | 说明 |
|------|------|
| `DcToken` | Discord 机器人令牌，不知道在哪的获取方法看最后的图片 |
| `ChannelId` | 要进行聊天的频道 ID |
| `MaxLoop` | 最大聊天次数（默认：100） |

你随便打开一个聊天频道，浏览器的URL，比如：
https://discord.com/channels/1209630079936630824/1316229370372690042 那ChannelId 就是1316229370372690042

### AI 个性化设置
| 参数 | 说明 |
|------|------|
| `MyDemand` | 机器人要求，使用示例如下 |

**示例 1**：`口气是中年人`
> 脚本会发送：我这里有几十条聊天纪录依次列出来了，帮我回复一句话来承接他们的内容，要求如下：口气是中年人，用英文(中文)回复

**示例 2**：`口气是中年人，身份是刚分手的有钱人，男的`
> 脚本会发送：我这里有几十条聊天纪录依次列出来了，帮我回复一句话来承接他们的内容，要求如下：口气是中年人，身份是刚分手的有钱人，男的，用英文(中文)回复

### 语言设置
| 参数 | 可选值 |
|------|------|
| `Language` | `English` 或 `Chinese`（控制 AI 回复的语言） |

### API 设置
| 参数 | 说明 |
|------|------|
| `GptKey` | OpenAI API 密钥 |

注册链接：https://api.v3.cm/register?aff=xDfN   介意可以删除邀请，注册充值好了后，在左侧边栏：令牌管理 获取你的KEY

### 时间间隔设置
⚠️ **注意**：最小时间应大于频道的慢速模式时间限制
| 参数 | 说明 |
|------|------|
| `MinSleep` | 最小间隔时间（秒） |
| `MaxSleep` | 最大间隔时间（秒） |

### 智能等待设置
当 `IsWait` 设为 `yes` 时，机器人会检查前 50 条消息。如果发现自己的消息，将暂停回复，以避免 AI 聊天过于明显。

| 参数 | 说明 |
|------|------|
| `IsWait` | `yes` 或 `no`（是否启用智能等待） |
| `YourID` | 你的 Discord ID（仅当 `IsWait=yes` 时需要） |
| `IsWaitTime` | 等待时间（秒）（仅当 `IsWait=yes` 时生效） |

在DC页面按下F12，然后点开设置找到下面的链接，可以获取Token和DiscordID
![Discord 机器人配置示例](https://github.com/sky887766/Discordchatbot/blob/main/id.jpg "配置文件示例")
![Discord 机器人配置示例](https://github.com/sky887766/Discordchatbot/blob/main/token.jpg "配置文件示例")

## 🚀 使用提示
1. 确保所有必要参数都已正确配置
2. 根据你的需求自定义 `MyDemand` 参数
3. 调整时间间隔以避免被 Discord 限制
4. 考虑使用 `IsWait` 功能以使机器人行为更自然

## 🔒 安全提示
- 请妥善保管你的 Discord Token 和 GPT API 密钥
- 建议将此配置文件设为私有，不要公开分享

---

*通过调整上述参数，你可以创建一个符合你期望行为的 Discord 聊天机器人。祝你使用愉快！*
