# 更新日志

## 1.0.3

- 补齐 `CHANGELOG.md`（AstrBot 启动告警消除）。

## 1.0.2

- `_conf_schema.json` 改为 AstrBot 扁平字典格式，修复插件加载失败。

## 1.0.1

- 去掉 `@register` 装饰器，改为 `class StellarGuard(Star)` 直接继承。
- 移除未使用的 `Plain` 导入，减少版本兼容风险。

## 1.0.0

- 对外接口 `process(text)`，供星缀调用，返回清洗并断句后的多条文本。
- `strip_tool_markup()`：先提取 `parameter name="text"` 里的正文，再删整块
  `<|DSML| ...>` 标记 —— 直接整块删会把真正想说的话一起删掉。
- `has_tool_markup()`：检测是否存在工具调用标记。
- `split_sentences()`：按句末标点（。！？…）拆分，短句并入上一条，
  避免「！！！」被拆成多条。
- `guard_response()` 拦截 LLM 回复，清洗后仍为空的整条丢弃。
