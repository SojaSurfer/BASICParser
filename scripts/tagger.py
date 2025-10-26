import json
from collections import OrderedDict
from pathlib import Path

from ._types import OptionalTokens, TagsetType
from .basics import BASICToken
from .petscii import ASCII_CODES



def load_tagset(filepath: str | Path) -> TagsetType:
    """Load the tagset json file."""

    if isinstance(filepath, str):
        filepath = Path(filepath)

    with filepath.open("r") as file:
        tagset = json.load(file)

    tagset = OrderedDict(tagset)
    return tagset



class Tagger:
    """A tagger class retrieving the corresponding tag from the tagset. Since the construction of
    the tagset and the tagging rules are intertwined, it currently only supports the default
    tagset (scripts/tagset.json).
    """

    def __init__(self) -> None:
        self.tagset_path = Path(__file__).parent / "tagset.json"
        self.tagset = load_tagset(self.tagset_path)
        self.asciiCodes = {char: key for key, value in ASCII_CODES.items() for char in value}
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(tagset_path={self.tagset_path!s})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(tagset_path={self.tagset_path!r})"
    
    def parse_print(self, btoken: BASICToken, decoded_tokens: OptionalTokens = None) -> str:
        return self.tagset["strings"]["print"]["tag"]

    def parse_comment(self, btoken: BASICToken, decoded_tokens: OptionalTokens = None) -> str:
        return self.tagset["strings"]["comment"]["tag"]

    def parse_string(self, btoken: BASICToken, decoded_tokens: OptionalTokens = None) -> str:
        return self.tagset["strings"]["string"]["tag"]

    def parse_ascii(self, btoken: BASICToken, decoded_tokens: OptionalTokens = None) -> str:
        ascii_type = self.asciiCodes.get(btoken.value, "unknown")

        match ascii_type:
            case "letter":
                return self.tagset["variables"]["real"]["tag"]

            case "number":
                if decoded_tokens and decoded_tokens[-1].token == ".":
                    return self.tagset["numbers"]["real"]["tag"]
                return self.tagset["numbers"]["integer"]["tag"]

            case "sigil":
                return self.tagset["punctuations"]["type"]["tag"]

            case "punctuation":
                for tagging in self.tagset["punctuations"].values():
                    if btoken.token in tagging["values"]:
                        return tagging["tag"]
                return self.tagset["punctuations"]["other"]["tag"]

            case _:
                # msg = f"can not parse ascii btoken of value {btoken.value}"
                # raise ValueError(msg)
                return "unknown"

    def parse_command(self, btoken: BASICToken) -> str:
        operator = self._parse_operator(btoken)
        if operator is not None:
            return operator

        for tagging in self.tagset["commands"].values():
            if btoken.token in tagging["values"]:
                return tagging["tag"]

        for tagging in self.tagset["constants"].values():
            if btoken.token in tagging["values"]:
                return tagging["tag"]

        return self.tagset["unknown"]["unknown"]["tag"]
        # msg = f"can not parse command btoken of token {btoken.token}"
        # raise ValueError(msg)

    def _parse_operator(self, btoken: BASICToken) -> str | None:
        if btoken.value in (0xAA, 0xAB, 0xAC, 0xAD, 0xAE):
            return self.tagset["operators"]["arithmetic"]["tag"]

        elif btoken.value in (0xB1, 0xB2, 0xB3):
            return self.tagset["operators"]["relational"]["tag"]

        elif btoken.value in (0xA8, 0xAF, 0xB0):
            return self.tagset["operators"]["logical"]["tag"]

        return None
