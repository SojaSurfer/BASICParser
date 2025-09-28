from pathlib import Path
from typing import Any, Self

import pandas as pd

from scripts.petscii import ASCII_CODES



class BASICToken:
    """A class that represents one token in the Commodore BASIC programming language."""

    def __init__(
        self,
        value: int,
        lineno: int,
        byte: bytes | None = None,
        byte_repr: str | None = None,
        token: str | None = None,
    ) -> None:
        self.value = value
        self.lineno = lineno

        self._byte = bytearray([value]) if byte is None else byte
        self.byte_repr: str = f"0x{value:02x}" if byte_repr is None else byte_repr
        self.token: str = "" if token is None else token

        self.syntax: str = ""
        self.language: str = "BASIC"

    @property
    def byte(self) -> bytes:
        """The bytes representation of the token."""
        return bytes(self._byte)

    def __str__(self) -> str:
        representation = (
            f"{self.__class__.__qualname__}({self.value}, {self.byte!r}, {self.byte_repr}, {self.token}, {self.syntax})"
        )
        return representation

    def __repr__(self) -> str:
        representation = (
            f"{self.__class__.__qualname__}(value={self.value!r}, byte={self.byte!r}, "
            f"byteRepr={self.byte_repr!r}, token={self.token!r}, syntax={self.syntax!r})"
        )
        return representation

    def __len__(self) -> int:
        return len(self.byte)

    def __add__(self, other: Self) -> Self:
        self._add_check_other(other)

        value = self.value  # hmm..
        byte = self.byte + other.byte
        byte_repr = self.byte_repr + other.byte_repr
        token = self.token + " " + other.token

        return self.__class__(value, self.lineno, byte=byte, byte_repr=byte_repr, token=token)

    def __iadd__(self, other: Self) -> Self:
        self._add_check_other(other)

        self.value = other.value  # hmm..
        self._byte = self.byte + other.byte
        self.byte_repr = self.byte_repr + " " + other.byte_repr
        self.token = self.token + other.token

        return self

    def _add_check_other(self, other: Any) -> None:
        if not isinstance(other, self.__class__):
            msg = "Can only add two BASICToken objects together"
            raise TypeError(msg)

        if self.lineno != other.lineno:
            msg = f"Self and other must be in the same line number to be added together, found {self.lineno} and {other.lineno}"
            raise ValueError(msg)
        elif self.language != other.language:
            msg = f"Self and other must be in the same language to be added together, found {self.language} and {other.language}"
            raise ValueError(msg)
        return None

    def is_whitespace(self) -> bool:
        """Check if token contains only an empty space."""
        return self.byte == b" "

    def is_digit(self) -> bool:
        """Check if token is an ASCII digit."""
        return self.value in ASCII_CODES["number"]

    def is_letter(self) -> bool:
        """Check if token is an ASCII letter."""
        return self.value in ASCII_CODES["letter"]

    def is_punctuation(self) -> bool:
        """Check if token is an ASCII punctuation but not a sigil."""
        return self.value in ASCII_CODES["punctuation"]

    def is_sigil(self) -> bool:
        """Check if token is an BASIC sigil."""
        return self.value in ASCII_CODES["sigil"]

    def is_alpha(self) -> bool:
        if not self.token:
            return False
        return self.token[0].lower() in "abcdefghijklmnopqrstuvwxyz"


class BASICFile:
    """A class that represents a Commodore BASIC file containing a dict with BASICToken elements."""

    def __init__(self) -> None:
        self.file: list[tuple[int, list[BASICToken]]] = []

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    # def __getitem__(self, index) -> list[BASICToken]:
    #     return self.file[index]

    # def print_line(self, index: int = -1) -> None:
    #     if index == -1:
    #         index = max(self.file.keys())

    #     token_line = " ".join([btoken.token for btoken in self.file[index]])
    #     print(f"{index:>5d} {token_line}")
    #     return None

    def add_line(self, tokens: list[BASICToken], lineno: int) -> None:
        self.file.append((lineno, tokens))
        return None

    def save_file(self, path: str | Path) -> None:
        """Save the BASIC file as an text file."""
        data = []
        for lineno, tokens in self.file:
            line = f"{lineno:>5d} {' '.join([tk.token for tk in tokens])}"

            data.append(line)

        with Path(path).open("w", encoding="utf-8") as file:
            file.write("\n".join(data))
        return None

    def save_table(self, path: str | Path) -> pd.DataFrame:
        """Save the BASIC file as an Excel file."""

        df = pd.DataFrame(columns=["line", "token_id", "bytes", "token", "syntax", "language"])

        for lineno, btokens in self.file:
            for idx, btoken in enumerate(btokens):
                df.loc[len(df)] = [lineno, idx, btoken.byte_repr, btoken.token, btoken.syntax, btoken.language]

        df.to_excel(path)
        return df
