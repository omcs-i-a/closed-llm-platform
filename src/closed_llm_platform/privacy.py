import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MaskingResult:
    text: str
    pii_types: list[str]

    @property
    def applied(self) -> bool:
        return bool(self.pii_types)


_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "email",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "[REDACTED_EMAIL]",
    ),
    (
        "api_key",
        re.compile(r"\b(?:sk|pk|api|key|token)[-_][A-Za-z0-9._-]{6,}\b", re.IGNORECASE),
        "[REDACTED_API_KEY]",
    ),
    (
        "credit_card",
        re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
        "[REDACTED_CREDIT_CARD]",
    ),
    (
        "phone",
        re.compile(r"(?<!\w)(?:\+?\d{1,3}[ -]?)?(?:\(?\d{3}\)?[ -]?)\d{3}[ -]?\d{4}(?!\w)"),
        "[REDACTED_PHONE]",
    ),
)


def mask_pii(text: str) -> MaskingResult:
    masked = text
    pii_types: list[str] = []
    for pii_type, pattern, replacement in _PATTERNS:
        masked, count = pattern.subn(replacement, masked)
        if count:
            pii_types.append(pii_type)
    return MaskingResult(text=masked, pii_types=pii_types)
