import struct
from pathlib import Path
from typing import Generator

from rich import traceback

from scripts.basics import BASICFile, BASICToken
from scripts.petscii import (
    ASCII_CODES,
    ASSEMBLY_CHARS,
    BYTE_TO_CMD,
    BYTE_TO_CTRL,
)
from scripts.tagger import Tagger
from scripts.tagset import TAGSET
from scripts.typing import TagsetType



traceback.install()
""" Current problems:
- number -.1 is split into "-" and ".1"
- invalid files: inv-mc, spukhaus2, 
- pingi2 line 6030ff:  <6030 "{rvs_on}" rvs ON>
- roulette line 10ff:    <10 * * * * * * * * * * * * * * * * * *>
    skip non-valid BASIC statemtents? -> line-number not followed by a keyword or quoted string
- ? zu PRINT

Pipeline: Detokeniser -> Lexer -> Chunker -> Tagger
PETSCII codec!
"""


class Lexer:
    """A class to decode a Commodore BASIC binary file."""

    def __init__(self, tagset: TagsetType) -> None:
        self.tagger = Tagger(tagset)
        self.tagset = tagset

        self.filename: Path
        self.asciiCodes = {char: key for key, value in ASCII_CODES.items() for char in value}

    def detokenize_basic_file(self, filename: str | Path) -> BASICFile:
        """Detokenizes a BASIC file from the given filename.

        This method reads a tokenized BASIC file, processes each line within a specified range,
        detokenizes the content, and adds the detokenized lines to a new BASICFile object.

        Args:
            filename (str | Path): The path to the tokenized BASIC file to be detokenized.

        Returns:
            BASICFile: An object containing the detokenized lines of the BASIC file.
        """
        if isinstance(filename, str):
            filename = Path(filename)
        elif not isinstance(filename, Path):
            msg = f"Expected 'filename' to be of type str or Path, found type {type(filename)}"
            raise TypeError(msg)

        self.filename = filename

        bfile = BASICFile()
        lines_inbetween = (0, 2**16)

        for ln, txt in self._detokenize_line():
            if lines_inbetween[0] <= ln <= lines_inbetween[1]:
                detokenized_line = self._lex_line(ln, txt)
                bfile.add_line(detokenized_line, ln)

                # bfile.printLine()

            if ln >= lines_inbetween[1]:
                break

        return bfile

    def _detokenize_line(self) -> Generator[tuple[int, bytes], None, None]:
        """Parse a tokenized Commodore-BASIC source file into (lineno, content bytes) tuples.

        Assumption:
        - first 2 bytes are header (skip)
        - each line: 2-byte little-endian line number,
                    two-byte pointer to next line?
                    tokenized text ending in 0x00,
        """

        with self.filename.open("rb") as file:
            binary = file.read()

        text = b""
        pos = 2  # skip header
        end = len(binary)
        while pos < end - 4:
            # pointer
            (ptr,) = struct.unpack_from("<H", binary, pos)
            pos += 2

            # read line number
            (lineno,) = struct.unpack_from("<H", binary, pos)
            pos += 2

            if lineno == 0 and set(binary[pos:]) == {0}:  # rest of file contains only zero bytes
                return None

            # read text until the 0x00 terminator
            try:
                eol = binary.index(0x00, pos)
            except ValueError:
                print(f"No EOL 0x00 found after byte {pos}, assuming EOF")
                eol = len(binary)
                return None

            text = binary[pos:eol]
            pos = eol + 1  # skip the 0x00

            yield (lineno, text)

        return None

    def _lex_line(self, lineno: int, line: bytes) -> list[BASICToken]:
        hexbytes: list[int]

        hexbytes = [line[0]] if len(line) == 1 else list(line)

        self.comment_cmd = False
        self.print_cmd = False
        self.string_decl = False
        self.is_data_block = False
        self.parenthesis = 0
        self.last_char: BASICToken
        self.append_btoken = True
        self.decoded_tokens: list[BASICToken] = []

        for value in hexbytes:
            btoken = BASICToken(value, lineno)

            if btoken.is_whitespace() and not self._within_string_like_expression():
                continue

            if self.string_decl:
                self._decode_string(btoken)

            elif self.comment_cmd:
                self._decode_comment_statement(btoken)

            elif value < 0x20:
                # ASCII control char outside of print statement, unclear why
                btoken.token = BYTE_TO_CTRL.get(btoken.byte, str(btoken.byte))
                btoken.syntax = self.tagger.parse_string(btoken)

                if self.string_decl:
                    self.append_btoken = False

            elif 0x20 <= value <= 0x7F:
                # value is an ASCII printable character
                self._decode_ascii(btoken)

            elif value >= 0x80:
                # BASIC command statement
                self._decode_cmd(btoken)

            else:
                btoken.token = str(btoken.byte)
                btoken.syntax = "?_unknown"
                self.append_btoken = True

            self._disambiguate_unary_signs()

            if self.append_btoken:
                self.decoded_tokens.append(btoken)
            else:
                if self.decoded_tokens:
                    self.decoded_tokens[-1] += btoken
                else:
                    self.decoded_tokens.append(btoken)

            # self.last_char = btoken
            self.last_char = self.decoded_tokens[-1]
            self._check_for_system_var()

        self._check_line_language()

        return self.decoded_tokens

    def _decode_cmd(self, btoken: BASICToken) -> None:
        self.append_btoken = True

        if (
            btoken.value in (0xB1, 0xB2, 0xB3)
            and self.last_char.value in (0xB1, 0xB2, 0xB3)
            and btoken.value != self.last_char.value
        ):
            # 2-byte relational operator like <=, >=, <>, =>, =<
            self.append_btoken = False

        elif btoken.value == 0x83 and not self.decoded_tokens:
            self.is_data_block = True

        self.print_cmd = btoken.value in (0x98, 0x99) if not self.print_cmd else self.print_cmd  # PRINT & PRINT#
        self.comment_cmd = btoken.value in (0x8F,)  # REM

        if self.string_decl:
            btoken.token = BYTE_TO_CTRL.get(btoken.byte, str(btoken.byte))
            btoken.syntax = self.tagger.parse_string(btoken)
            self.append_btoken = False
        else:
            btoken.token = BYTE_TO_CMD[btoken.byte]
            btoken.syntax = self.tagger.parse_command(btoken)

            # disambiguate equal sign
            if btoken.value == 0xB2 and self.decoded_tokens:
                self._disambiguate_equal_sign(btoken)

        return None

    def _decode_string(self, btoken: BASICToken) -> None:
        # BASIC commands are not available in a string
        if btoken.byte == b'"':
            # first ", start of print statement
            self.parenthesis += 1
            btoken.token = '"'
            self.append_btoken = True

            if self.parenthesis == 2:
                # second ", end of print statement
                self.parenthesis = 0
                self.append_btoken = False
                self.string_decl = False

        elif self.parenthesis == 0:
            # no <"> after PRINT, expect variable or command
            self.append_btoken = True

            if btoken.value < 0x20:
                # ASCII control char outside of print statement, unclear why
                btoken.token = BYTE_TO_CTRL.get(btoken.byte, str(btoken.byte))
                btoken.syntax = self.tagger.parse_string(btoken)

            elif 0x20 <= btoken.value <= 0x7F:
                # btoken.value is an ASCII printable character
                self._decode_ascii(btoken)

            elif btoken.value >= 0x80:
                # BASIC command statement
                self._decode_cmd(btoken)

            else:
                btoken.token = str(btoken.byte)
                btoken.syntax = "?_unknown"

        else:
            # anything in between "" in the print statement
            btoken.token = BYTE_TO_CTRL.get(btoken.byte, btoken.byte.decode("ascii", errors="replace").lower())
            if btoken.value > 0x80 and btoken.byte not in BYTE_TO_CTRL:
                # add those to the BYTE_TO_CTRL dict
                print(btoken, btoken.lineno, [b.token for b in self.decoded_tokens])
            self.append_btoken = False

            btoken.syntax = self.tagset["strings"]["string"]["tag"]
        return None

    def _decode_comment_statement(self, btoken: BASICToken) -> None:
        btoken.syntax = self.tagset["strings"]["comment"]["tag"]
        if btoken.value < 0x20:
            btoken.token = BYTE_TO_CTRL.get(btoken.byte, str(btoken.byte))
        elif btoken.value < 0x80:
            btoken.token = btoken.byte.decode("ascii", errors="replace").lower()
        else:
            btoken.token = BYTE_TO_CTRL.get(btoken.byte, btoken.byte.decode("ascii", errors="replace"))

        if self.last_char.value not in (0x8F,):
            # a comment where at least one char was placed already
            self.append_btoken = False

        return None

    def _decode_ascii(self, btoken: BASICToken) -> None:
        btoken.token = chr(btoken.value).lower()

        btoken.syntax = self.tagger.parse_ascii(btoken, self.decoded_tokens)

        if self._belongs_to_previous_byte(btoken):
            # assumption: either multi-char var name or multi-digit number
            self.append_btoken = False
        else:
            self.append_btoken = True

        if btoken.byte == b'"':
            self.parenthesis += 1
            self.string_decl = True

            if self.parenthesis == 2:
                self.string_decl = False
                self.parenthesis = 0

        if self.string_decl:
            btoken.syntax = self.tagger.parse_string(btoken)
        elif btoken.is_digit() or btoken.token == ".":
            self._disambiguate_dot(btoken)

        elif btoken.is_sigil():
            if self.decoded_tokens and self.decoded_tokens[-1].is_alpha():
                if btoken.token == "$":
                    self.decoded_tokens[-1].syntax = self.tagset["variables"]["string"]["tag"]
                else:
                    self.decoded_tokens[-1].syntax = self.tagset["variables"]["integer"]["tag"]
            else:
                btoken.syntax = self.tagset["punctuations"]["other"]["tag"]

        elif btoken.token == "(" and self.decoded_tokens and self.decoded_tokens[-1].syntax.startswith("V"):
            # disambiguate parenthesis, could hint at an array variable
            self.decoded_tokens[-1].syntax = f"VA{self.decoded_tokens[-1].syntax[-1]}"

        # if self.is_data_block and btoken.is_letter():
        if self.is_data_block and btoken.token != ",":
            btoken.syntax = self.tagset["data"]["data"]["tag"]
        return None

    def _belongs_to_previous_byte(self, btoken: BASICToken) -> bool:
        if self.last_char is None:
            return False
        elif (
            (btoken.is_letter() and self.last_char.is_letter())  # v, a -> va  (variable)
            or (btoken.is_digit() and self.last_char.is_digit())  # 1, 2 -> 12  (number)
            or (btoken.is_digit() and self.last_char.is_letter())  # v, 1 -> v2  (variable)
            or self.string_decl  # "hell, o -> "hello (string literal)
            or (btoken.is_sigil() and self.last_char.syntax.startswith("V"))  # v, $ -> v$  (variable)
        ):
            return True

        return False

    def _within_string_like_expression(self) -> bool:
        return any([self.print_cmd, self.comment_cmd, self.string_decl])

    def _check_line_language(self) -> None:
        tokenized_line = [b.token for b in self.decoded_tokens]
        if (
            tokenized_line
            and tokenized_line[0].lower() == "data"
            and all(
                (char in ASSEMBLY_CHARS for token in tokenized_line[1:] for char in token),
            )
        ):
            for b in self.decoded_tokens:
                b.language = "ASSEMBLY"

        return None

    def _disambiguate_unary_signs(self) -> None:
        last = self.last_char
        tokens = self.decoded_tokens

        # only care when last token is a “+” or “–”
        if last and last.token in ("+", "-"):
            # are we the very first token on the line?
            is_first = len(tokens) == 1

            # or did the token before last *not* look like an expression?
            # i.e. not a variable (V...), not a number (N...), and not a closing ')'
            prev = tokens[-2]
            syntax = prev.syntax or ""
            is_nonexpr = not (syntax.startswith(("V", "N", "S")) or prev.token == ")")

            if is_first or is_nonexpr:
                # it’s a unary sign, so re-tag as part of the literal
                tokens[-1].syntax = self.tagset["operators"]["unary"]["tag"]
                # self.append_btoken = False  # for now separate unary sign

        return None

    def _disambiguate_dot(self, btoken: BASICToken) -> None:
        """Add the current token to the previous token if the current token is a dot and
        the previous token was a digit or the current token is a digit and the previous token was a dot.
        """

        if self.last_char is not None and (
            (btoken.token == "." and self.last_char.is_digit()) or self.last_char.token[-1] == "."
        ):
            btoken.syntax = self.tagset["numbers"]["real"]["tag"]
            self.decoded_tokens[-1].syntax = btoken.syntax
            self.append_btoken = False

        return None

    def _disambiguate_equal_sign(self, btoken: BASICToken) -> None:
        btoken.syntax = self.tagset["operators"]["assignment"]["tag"]

        for prior_token in self.decoded_tokens[::-1]:
            if prior_token.token == "IF":
                # relational equal sign
                btoken.syntax = self.tagger.parse_command(btoken)
                break
            elif prior_token.token in (":", ";", "THEN"):
                # end of command span, since "IF" was not found it is an assignment
                break

    def _check_for_system_var(self) -> None:
        last_token = self.decoded_tokens[-1]
        if last_token.syntax and last_token.syntax.startswith("V"):
            if last_token.token.lower() in ("ti$", "time$"):
                self.decoded_tokens[-1].syntax = self.tagset["system"]["time"]["tag"]

            elif last_token.token.lower() in ("st", "status"):
                self.decoded_tokens[-1].syntax = self.tagset["system"]["IO"]["tag"]

        elif len(self.decoded_tokens) > 2 and self.decoded_tokens[-2].token.lower() in ("ti", "time"):
            self.decoded_tokens[-2].syntax = self.tagset["system"]["time"]["tag"]

        return None
