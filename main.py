# -*- coding: utf-8 -*-
"""StellarGuard —— 星盾，守护执行器 v1.0.0

文本后处理：清洗工具调用标记、按标点断句、防漏发 DSML 代码。
兼容 Amo_Guard 的 process() 接口。
"""
from __future__ import annotations
import re
from typing import Any, Dict, List
try:
    from astrbot.api import logger
    from astrbot.api.star import Context, Star
    from astrbot.api.event import filter as evt_filter, AstrMessageEvent
except ImportError:
    raise

PLUGIN_VERSION = "1.0.1"

# 工具调用标记正则（DSML、XML 形式）
_TOOL_MARKUP_RE = re.compile(
    r"<\|{1,2}DSML\|{1,2}.*?(?:/>|</.*?>)|\[\[(?:switch|tool):[^\]]*\]\]",
    re.DOTALL | re.IGNORECASE,
)
# parameter name="text" 里的正文提取
_PARAM_TEXT_RE = re.compile(r'parameter\s+name="text"\s*>(.*?)</parameter', re.DOTALL)

# 强制断句的句末标点
_SENTENCE_END = re.compile(r"([。！？…!?]+)")


def strip_tool_markup(text: str) -> str:
    """先提取 parameter name="text" 的正文，再删整块标记。"""
    # 先尝试从工具调用里提出真正的话
    m = _PARAM_TEXT_RE.search(text)
    if m:
        inner = m.group(1).strip()
        if inner:
            return _TOOL_MARKUP_RE.sub("", inner).strip()
    return _TOOL_MARKUP_RE.sub("", text).strip()


def has_tool_markup(text: str) -> bool:
    """是否包含工具调用标记。"""
    return bool(_TOOL_MARKUP_RE.search(text))


def split_sentences(text: str, min_len: int = 8) -> List[str]:
    """按句末标点拆分成列表，每段 >= min_len 字才独立成条，否则并入上一条。"""
    parts = _SENTENCE_END.split(text)
    out: List[str] = []
    buf = ""
    for part in parts:
        buf += part
        if _SENTENCE_END.fullmatch(part) and len(buf) >= min_len:
            out.append(buf.strip())
            buf = ""
    if buf.strip():
        if out:
            out[-1] += buf.strip()
        else:
            out.append(buf.strip())
    return [s for s in out if s]


class StellarGuard(Star):
    def __init__(self, context: Context, config: Dict[str, Any] | None = None) -> None:
        super().__init__(context)
        cfg = config or {}
        self._enabled: bool = bool(cfg.get("enable", True))
        self._split_sentences: bool = bool(cfg.get("split_sentences", True))
        self._min_len: int = max(1, int(cfg.get("min_sentence_len") or 8))
        logger.info(f"[StellarGuard] v{PLUGIN_VERSION} 初始化，断句={'开' if self._split_sentences else '关'}")

    def process(self, text: str) -> List[str]:
        """公开接口：供星缀调用的文本后处理。

        返回处理后的文本列表（可能拆成多条）。
        失败返回原文。
        """
        if not self._enabled or not text:
            return [text] if text else []
        try:
            cleaned = strip_tool_markup(text)
            if not cleaned:
                return []
            if self._split_sentences:
                return split_sentences(cleaned, self._min_len)
            return [cleaned]
        except Exception as e:
            logger.debug(f"[StellarGuard] 处理失败: {e}")
            return [text]

    @evt_filter.on_llm_response()
    async def guard_response(self, event: AstrMessageEvent, resp) -> None:
        """拦截 LLM 回复，清洗工具标记。"""
        if not self._enabled:
            return
        try:
            msg = resp.result_message
            if msg is None:
                return
            new_segs = []
            changed = False
            for seg in (msg.message or []):
                if not hasattr(seg, "text"):
                    new_segs.append(seg)
                    continue
                raw = seg.text
                if has_tool_markup(raw):
                    cleaned = strip_tool_markup(raw)
                    if not cleaned:
                        changed = True
                        continue   # 整条丢掉
                    seg.text = cleaned
                    changed = True
                new_segs.append(seg)
            if changed:
                msg.message = new_segs
        except Exception as e:
            logger.debug(f"[StellarGuard] guard_response 失败: {e}")
