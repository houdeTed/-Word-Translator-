import translators as ts

# 翻译服务优先级（搜狗已排除，返回加密数据）
SERVICES = ["youdao", "caiyun", "iciba", "alibaba"]


def translate(text: str, source: str = "en", target: str = "zh") -> str:
    text = text.strip()
    if not text:
        return ""

    for service in SERVICES:
        try:
            result = ts.translate_text(
                text,
                translator=service,
                from_language=source,
                to_language=target,
                timeout=5,
            )
            if result and result != text:
                return result
        except Exception:
            continue

    return "[翻译失败，请检查网络]"
