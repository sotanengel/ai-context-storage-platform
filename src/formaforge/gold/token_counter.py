"""Model-specific token counting service."""

from typing import Any


def _get_tiktoken_encoder() -> Any:
    try:
        import tiktoken

        return tiktoken.get_encoding("cl100k_base")
    except ImportError:
        return None


class TokenCounter:
    """Count tokens for a given text and target model."""

    def count(self, text: str, target_model: str = "generic") -> int:
        if not text:
            return 1

        match target_model:
            case "gpt4":
                enc = _get_tiktoken_encoder()
                if enc is not None:
                    return len(enc.encode(text))
                return self._byte4(text)
            case "gemini":
                return max(1, len(text.encode()) // 3)
            case _:
                return self._byte4(text)

    def _byte4(self, text: str) -> int:
        return max(1, len(text.encode()) // 4)
