class Tokenizer:
    """Tokenizes a single .jack-file into a stream of tokens."""

    def __init__(self, file):
        self.token_count = 0
        self.token = ""
        self.tokens = []
        
        with open(file) as stream:
            chars = stream.read()
            comment = False
            token = ""
            i = 0
            
            while i < len(chars):
                if chars[i] in [" ", "\n"]:
                    i += 1
                    continue
                
                elif chars[i] == "/":
                    if chars[i+1] == "/":
                        comment = True
                        while comment:
                            if chars[i] == "\n":
                                comment = False
                            i += 1
                        continue   
                    elif chars[i+1] == "*":
                        comment = True
                        while comment:
                            if chars[i] == "*" and chars[i+1] == "/":
                                comment = False
                            i += 1
                        i += 1
                        continue
                        
                elif chars[i] == "\"":
                    i += 1
                    while chars[i] != "\"":
                        token += chars[i]
                        i += 1
                    self.tokens.append(token)
                    token = ""
                    i += 1
                    continue
                    
                elif chars[i].isdecimal():
                    token += chars[i]
                    i += 1
                    while chars[i].isdecimal():
                        token += chars[i]
                        i += 1
                    self.tokens.append(token)
                    token = ""
                    i += 1
                    continue
                    
                elif not chars[i].isalnum():
                    self.tokens.append(chars[i])
                    i += 1
                    continue

                i += 1
            
            print(self.tokens)
                    
    
    def more_tokens(self):
        return self.token_count < len(self.tokens)
        
    def advance(self):
        self.token = self.tokens[self.token_count]
        self.token_count += 1
        
    def token_type(self):
        pass
        
    def keyword(self):
        pass
        
    def symbol(self):
        pass
        
    def identifier(self):
        pass
        
    def int_val(self):
        pass
        
    def string_val(self):
        pass
