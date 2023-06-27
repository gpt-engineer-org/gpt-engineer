# GPT 工程师

[![Discord Follow](https://dcbadge.vercel.app/api/server/8tcDQ89Ej2?style=flat)](https://discord.gg/8tcDQ89Ej2)
[![GitHub Repo stars](https://img.shields.io/github/stars/AntonOsika/gpt-engineer?style=social)](https://github.com/AntonOsika/gpt-engineer)
[![Twitter Follow](https://img.shields.io/twitter/follow/antonosika?style=social)](https://twitter.com/AntonOsika)

**指定你想要它构建的内容，AI 会要求澄清，然后构建它。**

GPT Engineer 旨在易于适应、扩展，并使您的代理了解您希望代码的外观。它根据提示生成整个代码库。

[Demo](https://twitter.com/antonosika/status/1667641038104674306)

## 项目理念

- 简单获取价值
- 灵活且轻松地添加新的自己的“AI 步骤”。见`steps.py`。
- 逐步构建以下用户体验：
  1. 高水平提示
  2. 向人工智能提供反馈，随着时间的推移它会记住
- 人工智能和人类之间的快速切换
- 简单，所有计算都是“可恢复的”并保存到文件系统

## 用法

选择**稳定版本**或**开发版本**。

**稳定版本**：

- `pip install gpt-engineer`

**开发版本**：

- `git clone https://github.com/AntonOsika/gpt-engineer.git`

- `cd gpt-engineer`

- ```
  pip install -e .
  ```

  - （或者：`make install && source venv/bin/activate`对于 venv）

**设置**

使用具有 GPT4 访问权限的 api 密钥运行：

- `export OPENAI_API_KEY=[your api key]`

**运行**：

- 创建一个空文件夹。如果在存储库内，您可以运行：

  - `cp -r projects/example/ projects/my-new-project`

- 填写`prompt`新文件夹中的文件

- ```
  gpt-engineer projects/my-new-project
  ```

  - （注意，`gpt-engineer --help`让您查看所有可用选项。例如，`--steps use_feedback`让您改进/修复项目中的代码）

运行 gpt-engineer 即表示您同意我们的[ToS](https://github.com/AntonOsika/gpt-engineer/blob/main/TERMS_OF_USE.md)。

**结果**

- 检查生成的文件结果`projects/my-new-project/workspace`

## 特性

您可以通过编辑文件夹中的文件来指定AI代理的“身份” `preprompts`。

目前，编辑`preprompts`以及改进编写项目提示的方式是让代理记住项目之间的事情的方法。

中的每个步骤`steps.py`都会将其与 GPT4 的通信历史记录存储在日志文件夹中，并且可以使用`scripts/rerun_edited_message_logs.py`.

## 贡献

gpt-engineer 社区正在构建**开放平台，供开发人员修补和构建他们的个人代码生成工具箱**。

如果您有兴趣为此做出贡献，我们将很乐意邀请您！

[您可以在此处](https://github.com/AntonOsika/gpt-engineer/issues?q=is%3Aopen+is%3Aissue+label%3A"good+first+issue")检查是否有良好的优先问题。贡献文档[在这里](https://github.com/AntonOsika/gpt-engineer/blob/main/.github/CONTRIBUTING.md)。

我们目前正在寻找更多的维护者和社区组织者。如果您对官方职位感兴趣，请发送电子邮件至[anton.osika@gmail.com 。](mailto:anton.osika@gmail.com)

如果您想了解我们更广泛的雄心壮志，请查看[路线图](https://github.com/AntonOsika/gpt-engineer/blob/main/ROADMAP.md)，并加入 [Discord](https://discord.gg/8tcDQ89Ej2) 以获取有关如何为其做出贡献的意见。

## 例子

https://github.com/AntonOsika/gpt-engineer/assets/4467025/6e362e45-4a94-4b0d-973d-393a31d92d9b
