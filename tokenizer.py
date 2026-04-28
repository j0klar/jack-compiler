KEYWORDS = frozenset({"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"})

SYMBOLS = frozenset("{}()[].,;+-*/&|<>=~")

class Tokenizer:
    """Tokenizes a single .jack-file into a stream of tokens."""

    def __init__(self, file):
        self.cursor = 0
        self.token = None
        self.tokens = []
        
        with open(file) as stream:
            chars = stream.read()
            i = 0
            
            while i < len(chars):
                if chars[i].isspace(): # Handle space, tab & newline
                    i += 1
                    continue
                    
                elif chars[i] == "/": # Handle comments (// \n)
                    if chars[i+1] == "/":
                        while chars[i] != "\n":
                            i += 1
                        continue   
                    elif chars[i+1] == "*": # Handle comments (/* */, /** */)
                        i += 2
                        while not (chars[i] == "*" and chars[i+1] == "/"):
                            i += 1
                        i += 2
                        continue
                    else:
                        self.tokens.append(chars[i])
                        i += 1
                        continue
                        
                elif chars[i] == "\"": # Handle string literals
                    token = chars[i]
                    i += 1
                    while chars[i] != "\"":
                        token += chars[i]
                        i += 1
                    self.tokens.append(token)
                    i += 1
                    continue
                    
                elif chars[i].isdecimal(): # Handle integer constants
                    token = chars[i]
                    i += 1
                    while chars[i].isdecimal():
                        token += chars[i]
                        i += 1
                    self.tokens.append(token)
                    continue
                
                elif chars[i].isalpha() or chars[i] == "_": # Handle keywords & identifiers
                    token = chars[i]
                    i += 1
                    while chars[i].isalnum() or chars[i] == "_":
                        token += chars[i]
                        i += 1
                    self.tokens.append(token)
                    continue
                    
                elif chars[i] in SYMBOLS: # Handle symbols
                    self.tokens.append(chars[i])
                    i += 1
                    continue
                    
                else:
                    print(char[i] + " is not a valid character!")
            
            print(self.tokens)
                    
    def more_tokens(self):
        return self.cursor < len(self.tokens)
        
    def advance(self):
        self.token = self.tokens[self.cursor]
        self.cursor += 1
        
    def token_type(self):
        if self.token in KEYWORDS: return "KEYWORD"
        elif self.token in SYMBOLS: return "SYMBOL"
        elif self.token[0] == "\"": return "STRING_CONST"
        elif self.token.isdecimal(): return "INT_CONST"
        elif self.token.isalnum() or "_" in self.token: return "IDENTIFIER"
        
    def keyword(self):
        return self.token
        
    def symbol(self):
        return self.token
        
    def identifier(self):
        return self.token
        
    def int_val(self):
        return int(self.token)
        
    def string_val(self):
        return self.token[1:-1]
