from __future__ import annotations

_DEFAULT_API_BASE_BY_NAME: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "siliconflow": "https://api.siliconflow.cn/v1",
    "volcengine": "https://ark.cn-beijing.volces.com/api/v3",
    "dashscope": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "moonshot": "https://api.moonshot.ai/v1",
    "minimax": "https://api.minimax.io/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "vllm": "http://localhost:8000/v1",
    "ollama": "http://localhost:11434/v1",
    "lmstudio": "http://localhost:1234/v1",
    "aihubmix": "https://aihubmix.com/v1",
}


def get_default_api_base(provider_name: str) -> str:
    normalized = (provider_name or "").strip().lower().replace("-", "_")
    return _DEFAULT_API_BASE_BY_NAME.get(normalized, "")
