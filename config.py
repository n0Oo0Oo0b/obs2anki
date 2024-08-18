"""
Configuration
"""

SEARCH_PATTERN = (
    r"(?m)^#anki/(?P<modelName>\S+)\s+(?P<deckName>\S+)"
    r"(?:\n(?P<tags>.+))?"
    r"\n{2,}"
    r"(?P<content>(?:\|[\s\S]*?\|\n)+)"
)

GLOBAL_TAGS = ["obs2anki"]
