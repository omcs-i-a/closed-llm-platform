import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailDecision:
    status: str
    reasons: list[str]
    matched_patterns: list[str]


_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(?:the\s+)?(?:system|developer)\s+prompt", re.IGNORECASE),
    re.compile(r"disregard\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(?:in\s+)?developer\s+mode", re.IGNORECASE),
)


def inspect_prompt(prompt: str) -> GuardrailDecision:
    matched = [pattern.pattern for pattern in _INJECTION_PATTERNS if pattern.search(prompt)]
    if matched:
        return GuardrailDecision(
            status="flagged",
            reasons=["prompt_injection"],
            matched_patterns=matched,
        )
    return GuardrailDecision(status="allowed", reasons=[], matched_patterns=[])
