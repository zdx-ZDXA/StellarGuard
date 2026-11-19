# 🛡️ 星盾 StellarGuard

星缀套件的文本守护器，清洗工具调用标记、按标点断句。

## 功能

- 过滤 DSML 工具调用标记（防止代码块发到群里）
- 按句末标点拆分成多条发送
- 对外提供 `process()` 接口

## 配置

| 项 | 默认 | 说明 |
|---|---|---|
| enable | true | 总开关 |
| split_sentences | true | 按句断条 |
| min_sentence_len | 8 | 最短句长 |

---
v1.0.2 · 星缀套件 | https://github.com/zdx-ZDXA/StellarGuard
