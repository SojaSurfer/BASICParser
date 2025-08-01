import string

from basics import BASICToken



sigils = "$%!"
punctuations = [p for p in string.punctuation if p not in sigils]

ASCII_CODES = {
    "letter": [ord(char) for char in string.ascii_letters],
    "number": [ord(char) for char in string.digits],
    "sigil": [ord(char) for char in sigils],
    "punctuation": [ord(char) for char in punctuations],
}

ASSEMBLY_CHARS = string.digits + ", "


class Tagger:

    def __init__(self, tagset:dict) -> None:
        self.tagset = tagset
        self.asciiCodes = {char: key for key, value in ASCII_CODES.items() for char in value}

        return None

    
    def parse_print(self, btoken:BASICToken, decoded_tokens:list[BASICToken] = None) -> str:
        return self.tagset["strings"]["print"]["tag"]
    
    
    def parse_comment(self, btoken:BASICToken, decoded_tokens:list[BASICToken] = None) -> str:
        return self.tagset["strings"]["comment"]["tag"]

    def parse_string(self, btoken:BASICToken, decoded_tokens:list[BASICToken] = None) -> str:
        return self.tagset["strings"]["string"]["tag"]
    

    def parse_ascii(self, btoken:BASICToken, decoded_tokens:list[BASICToken] = None) -> str:
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

    
    def parse_command(self, btoken:BASICToken) -> str:
        
        operator = self._parse_operator(btoken)
        if operator is not None:
            return operator

        for tagging in self.tagset["commands"].values():
            if btoken.token in tagging["values"]:
                return tagging["tag"]
        
        for tagging in self.tagset["constants"].values():
            if btoken.token in tagging["values"]:
                return tagging["tag"]

        msg = f"can not parse command btoken of token {btoken.token}"
        raise ValueError(msg)

    
    def _parse_operator(self, btoken:BASICToken) -> str|None:
        if btoken.value in (0xAA, 0xAB, 0xAC, 0xAD, 0xAE):
            return self.tagset["operators"]["arithmetic"]["tag"]

        elif btoken.value in (0xB1, 0xB2, 0xB3):
            return self.tagset["operators"]["relational"]["tag"]

        elif btoken.value in (0xA8, 0xAF, 0xB0):
            return self.tagset["operators"]["logical"]["tag"]
        
        return None
    

    