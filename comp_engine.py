class Comp_Engine:

    def __init__(self, tokenizer, file_out):
        self.tokenizer = tokenizer
        self.file_out = file_out
        
    def comp_class(self):
        self.tokenizer.advance()
        self.file_out.write("<class>\n")
        # Handle 'class'
        self.process_fixed("class")
        # Handle className
        self.process_chosen()
        # Handle '{'
        self.process_fixed("{")
        # Handle classVarDec
        self.comp_class_var_dec()
        # Handle subroutineDec
        self.comp_subroutine()
        # Handle '}'
        self.process_fixed("}")
        self.file_out.write("</class>")
        
    def comp_class_var_dec(self):
        self.file_out.write("<classVarDec>\n")
        # Handle 'static'|'field'
        if self.tokenizer.get_token() == "static": self.process_fixed("static")
        elif self.tokenizer.get_token() == "field": self.process_fixed("field")
        else: print("Syntax Error: '" + self.tokenizer.get_token() + "' was not 'static' or 'field'!")
        # Handle type
        self.comp_type()
        # Handle varName
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
        # Handle subroutineName
        self.process_chosen()
        # Handle '('
        self.process_fixed("(")
        # Handle parameterList
        self.comp_parameter_list()
        # Handle ')'
        self.process_fixed(")")
        # Handle subroutineBody
        self.comp_subroutine_body()
        self.file_out.write("</subroutineDec>\n")
        
    def comp_subroutine_body(self):
        self.file_out.write("<subroutineBody>\n")
        # Handle '{'
        self.process_fixed("{")
        # Handle varDec*
        if self.tokenizer.get_token() == "var": self.comp_var_dec()
        # Handle statements
        self.comp_statements()
        # Handle '}'
        self.process_fixed("}")
        self.file_out.write("</subroutineBody>\n")
        
    def comp_type(self):
        # Handle 'int'|'char'|'boolean'|className
        if self.tokenizer.get_token() == "int": self.process_fixed("int")
        elif self.tokenizer.get_token() == "char": self.process_fixed("char")
        elif self.tokenizer.get_token() == "boolean": self.process_fixed("boolean")
        else: self.process_chosen()

    def comp_parameter_list(self):
        pass
        
    def comp_var_dec(self):
        pass
        
    def comp_statements(self):
        pass
        
    def comp_let(self):
        pass
        
    def comp_if(self):
        pass
        
    def comp_while(self):
        pass
        
    def comp_do(self):
        pass
        
    def comp_return(self):
        pass
        
    def comp_expression(self):
        pass
        
    def comp_term(self):
        pass
        
    def comp_expression_list(self):
        pass
    
    # Handle keyword|symbol
    def process_fixed(self, token):
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
    
    # Handle identifier|integerConstant|StringConstant
    def process_chosen(self):
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
