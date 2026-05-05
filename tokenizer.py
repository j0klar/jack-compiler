from errors import JackSyntaxError

KEYWORDS = frozenset({"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"})
SYMBOLS = frozenset("{}()[].,;+-*/&|<>=~")

class Tokenizer:
    """Tokenizes a single .jack-file into a stream of categorized tokens."""

    def __init__(self, file_in):
        self.cursor = 0
        self.token = None
        self.tokens = []
        
        with open(file_in) as stream:
            chars = stream.read()
            i = 0
            while i < len(chars):
                # Handle space, tab & newline
                if chars[i].isspace():
                    i += 1
                    continue
                 # Handle comments (// \n)    
                elif chars[i] == "/":
                    if chars[i+1] == "/":
                        while chars[i] != "\n":
                            i += 1
                        continue
                    # Handle comments (/* */, /** */)
                    elif chars[i+1] == "*":
                        i += 2
                        while not (chars[i] == "*" and chars[i+1] == "/"):
                            i += 1
                        i += 2
                        continue
                    else:
                        self.tokens.append(chars[i])
                        i += 1
                        continue
                # Handle string literals        
                elif chars[i] == "\"":
                    token = chars[i]
                    i += 1
                    while chars[i] != "\"":
                        token += chars[i]
                        i += 1
                    self.tokens.append(token + "\"")
                    i += 1
                    continue
                # Handle integer constants    
                elif chars[i].isdecimal():
                    token = chars[i]
                    i += 1
                    while chars[i].isdecimal():
                        token += chars[i]
                        i += 1
                    self.tokens.append(token)
                    continue
                # Handle keywords & identifiers
                elif chars[i].isalpha() or chars[i] == "_":
                    token = chars[i]
                    i += 1
                    while chars[i].isalnum() or chars[i] == "_":
                        token += chars[i]
                        i += 1
                    self.tokens.append(token)
                    continue
                # Handle symbols    
                elif chars[i] in SYMBOLS:
                    self.tokens.append(chars[i])
                    i += 1
                    continue
                else:
                    raise JackSyntaxError(f"Invalid character '{chars[i]}' at position {i}")
                    
    def more_tokens(self):
        return self.cursor < len(self.tokens)
        
    def advance(self):
        if self.more_tokens():
            self.token = self.tokens[self.cursor]
            self.cursor += 1
        
    def token_type(self):
        if self.token in KEYWORDS: return "KEYWORD"
        elif self.token in SYMBOLS: return "SYMBOL"
        elif self.token[0] == "\"": return "STRING_CONST"
        elif self.token.isdecimal(): return "INT_CONST"
        else: return "IDENTIFIER"
        
    def get_token(self):
        return self.token
        
    def int_val(self):
        return int(self.token)
        
    def str_val(self):
        return self.token[1:-1]
