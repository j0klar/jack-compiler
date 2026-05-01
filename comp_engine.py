class Comp_Engine:

    def __init__(self, tokenizer, file_out):
        self.tokenizer = tokenizer
        self.file_out = file_out
        
    def comp_class(self):
        self.tokenizer.advance()
        self.file_out.write("<class>\n")
        # Handle 'class' className
        self.process_fixed("class")
        self.process_chosen()
        # Handle '{'
        self.process_fixed("{")
        # Handle classVarDec*
        while self.tokenizer.get_token() in ["static", "field"]: self.comp_class_var_dec()
        # Handle subroutineDec*
        while self.tokenizer.get_token() in ["constructor", "function", "method"]: self.comp_subroutine()
        # Handle '}'
        self.process_fixed("}")
        self.file_out.write("</class>")
        
    def comp_class_var_dec(self):
        self.file_out.write("<classVarDec>\n")
        # Handle 'static'|'field'
        if self.tokenizer.get_token() == "static": self.process_fixed("static")
        elif self.tokenizer.get_token() == "field": self.process_fixed("field")
        else: print("Syntax Error: '" + self.tokenizer.get_token() + "' was not 'static' or 'field'!")
        # Handle type varName
        self.comp_type()
        self.process_chosen()
        # Handle (',' varName)*
        while self.tokenizer.get_token() == ",":
            self.process_fixed(",")
            self.process_chosen()
        # Handle ';'
        self.process_fixed(";")
        self.file_out.write("</classVarDec>\n")
        
    def comp_subroutine(self):
        self.file_out.write("<subroutineDec>\n")
        # Handle 'constructor'|'function'|'method'
        if self.tokenizer.get_token() == "constructor": self.process_fixed("constructor")
        elif self.tokenizer.get_token() == "function": self.process_fixed("function")
        elif self.tokenizer.get_token() == "method": self.process_fixed("method")
        else: print("Syntax Error: '" + self.tokenizer.get_token() + "' was not 'constructor', 'function', or 'method'!")
        # Handle 'void'|type
        if self.tokenizer.get_token() == "void": self.process_fixed("void")
        else: self.comp_type()
        # Handle subroutineName '('
        self.process_chosen()
        self.process_fixed("(")
        # Handle parameterList?
        if self.tokenizer.get_token() != ")":
            self.comp_parameter_list()
        # Handle ')' subroutineBody
        self.process_fixed(")")
        self.comp_subroutine_body()
        self.file_out.write("</subroutineDec>\n")
        
    def comp_parameter_list(self):
        self.file_out.write("<parameterList>\n")
        # Handle type varName
        self.comp_type()
        self.process_chosen()
        # Handle (',' type varName)*
        while self.tokenizer.get_token() == ",":
            self.process_fixed(",")
            self.comp_type()
            self.process_chosen()
        self.file_out.write("</parameterList>\n")
        
    def comp_subroutine_body(self):
        self.file_out.write("<subroutineBody>\n")
        # Handle '{' varDec*
        self.process_fixed("{")
        while self.tokenizer.get_token() == "var": self.comp_var_dec()
        # Handle statements '}'
        self.comp_statements()
        self.process_fixed("}")
        self.file_out.write("</subroutineBody>\n")
        
    def comp_var_dec(self):
        self.file_out.write("<varDec>\n")
        # Handle 'var' type varName
        self.process_fixed("var")
        self.comp_type()
        self.process_chosen()
        # Handle (',' varName)*
        while self.tokenizer.get_token() == ",":
            self.process_fixed(",")
            self.process_chosen()
        # Handle ';'
        self.process_fixed(";")
        self.file_out.write("</varDec>\n")
        
    def comp_statements(self):
        self.file_out.write("<statements>\n")
        # Handle (letStatement|ifStatement|whileStatement|doStatement|returnStatement)*
        if self.tokenizer.get_token() == "let": self.comp_let()
        elif self.tokenizer.get_token() == "if": self.comp_if()
        elif self.tokenizer.get_token() == "while": self.comp_while()
        elif self.tokenizer.get_token() == "do": self.comp_do()
        elif self.tokenizer.get_token() == "return": self.comp_return()
        self.file_out.write("</statements>\n")
        
    def comp_let(self):
        self.file_out.write("<letStatement>\n")
        # Handle 'let' varName
        self.process_fixed("let")
        self.process_chosen()
        # Handle ('[' expression ']')?
        if self.tokenizer.get_token() == "[":
            self.process_fixed("[")
            self.comp_expression()
            self.process_fixed("]")
        # Handle '=' expression ';'
        self.process_fixed("=")
        self.comp_expression()
        self.process_fixed(";")
        self.file_out.write("</letStatement>\n")
        
    def comp_if(self):
        self.file_out.write("<ifStatement>\n")
        # Handle 'if' '('
        self.process_fixed("if")
        self.process_fixed("(")
        # Handle expression ')'
        self.comp_expression()
        self.process_fixed(")")
        # Handle '{' statements '}'
        self.process_fixed("{")
        self.comp_statements()
        self.process_fixed("}")
        # Handle ('else' '{' statements '}')?
        if self.tokenizer.get_token == "else":
            self.process_fixed("else")
            self.process_fixed("{")
            self.comp_statements()
            self.process_fixed("}")
        self.file_out.write("</ifStatement>\n")
        
    def comp_while(self):
        self.file_out.write("<whileStatement>\n")
        # Handle 'while' '('
        self.process_fixed("while")
        self.process_fixed("(")
        # Handle expression ')'
        self.comp_expression()
        self.process_fixed(")")
        # Handle '{' statements '}'
        self.process_fixed("{")
        self.comp_statements()
        self.process_fixed("}")
        self.file_out.write("</whileStatement>\n")
        
    def comp_do(self):
        self.file_out.write("<doStatement>\n")
        # Handle 'do' subroutineCall ';'
        self.process_fixed("do")
        self.comp_term()
        self.process_fixed(";")
        self.file_out.write("</doStatement>\n")
        
    def comp_return(self):
        self.file_out.write("<returnStatement>\n")
        # Handle 'return' expression? ';'
        self.process_fixed("return")
        self.comp_expression()
        self.process_fixed(";")
        self.file_out.write("</returnStatement>\n")
        
    def comp_expression(self):
        pass
        
    def comp_term(self):
        pass
        
    def comp_expression_list(self):
        pass
     
    def comp_type(self):
        # Handle 'int'|'char'|'boolean'|className
        if self.tokenizer.get_token() == "int": self.process_fixed("int")
        elif self.tokenizer.get_token() == "char": self.process_fixed("char")
        elif self.tokenizer.get_token() == "boolean": self.process_fixed("boolean")
        else: self.process_chosen()
    
    def process_fixed(self, token):
        # Handle keyword|symbol
        current_token = self.tokenizer.get_token()
        token_type = self.tokenizer.token_type()
        if current_token == token:
            if token_type == "KEYWORD": 
                self.file_out.write("<keyword> " + current_token + " </keyword>\n")
            elif token_type == "SYMBOL":
                match current_token:
                    case "<": current_token = "&lt;"
                    case ">": current_token = "&gt;"
                    case "&": current_token = "&amp;"
                self.file_out.write("<symbol> " + current_token + " </symbol>\n")
            else: print("Syntax Error: '" + current_token + "' was not a keyword or symbol!")
        else: print("Syntax Error: '" + current_token + "' was not '" + token + "'!")
        self.tokenizer.advance()
    
    def process_chosen(self):
        # Handle identifier|integerConstant|StringConstant
        current_token = self.tokenizer.get_token()
        token_type = self.tokenizer.token_type()
        if token_type == "IDENTIFIER": 
            self.file_out.write("<identifier> " + current_token + " </identifier>\n")
        elif token_type == "STRING_CONST": 
            self.file_out.write("<stringConstant> " + self.tokenizer.str_val() + " </stringConstant>\n")
        elif token_type == "INT_CONST": 
            self.file_out.write("<integerConstant> " + str(self.tokenizer.int_val()) + " </integerConstant>\n")
        else: print("Syntax Error: '" + current_token + "' was not an identifier, string, or integer!")
        self.tokenizer.advance()
