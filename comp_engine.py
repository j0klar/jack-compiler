from errors import JackSyntaxError

OPS = frozenset("+-*/&|<>=")
UNARY_OPS = frozenset("-~")
KEYWORD_CONSTANTS = frozenset({"true", "false", "null", "this"})

class CompEngine:
    """Parses a stream of tokens according to the Jack grammar and constructs a parse tree."""

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
        while self.tokenizer.get_token() in ("static", "field"): 
            self.comp_class_var_dec()
        # Handle subroutineDec*
        while self.tokenizer.get_token() in ("constructor", "function", "method"): 
            self.comp_subroutine()
        # Handle '}'
        self.process_fixed("}")
        self.file_out.write("</class>")
        
    def comp_class_var_dec(self):
        self.file_out.write("<classVarDec>\n")
        # Handle 'static'|'field'
        current_token = self.tokenizer.get_token()
        if current_token in ("static", "field"): 
            self.process_fixed(current_token)
        else: 
            raise JackSyntaxError(f"Expected 'static' or 'field' but got '{current_token}'")
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
        current_token = self.tokenizer.get_token()
        if current_token in ("constructor", "function", "method"):
            self.process_fixed(current_token)
        else: 
            raise JackSyntaxError(f"Expected 'constructor', 'function', or 'method' but got '{current_token}'")
        # Handle 'void'|type
        if self.tokenizer.get_token() == "void": 
            self.process_fixed("void")
        else: self.comp_type()
        # Handle subroutineName '('
        self.process_chosen()
        self.process_fixed("(")
        # Handle parameterList
        self.comp_parameter_list()
        # Handle ')' subroutineBody
        self.process_fixed(")")
        self.comp_subroutine_body()
        self.file_out.write("</subroutineDec>\n")
        
    def comp_parameter_list(self):
        self.file_out.write("<parameterList>\n")
        # Handle (type varName (',' type varName)*)?
        if self.tokenizer.get_token() != ")":
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
        while self.tokenizer.get_token() == "var":
            self.comp_var_dec()
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
        while self.tokenizer.get_token() in ("let", "if", "while", "do", "return"):
            getattr(self, "comp_" + self.tokenizer.get_token())()
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
        if self.tokenizer.get_token() == "else":
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
        self.process_chosen()
        self.comp_call_suffix()
        self.process_fixed(";")
        self.file_out.write("</doStatement>\n")
        
    def comp_return(self):
        self.file_out.write("<returnStatement>\n")
        # Handle 'return' expression? ';'
        self.process_fixed("return")
        if self.tokenizer.get_token() != ";":
            self.comp_expression()
        self.process_fixed(";")
        self.file_out.write("</returnStatement>\n")
        
    def comp_expression(self):
        self.file_out.write("<expression>\n")
        # Handle term
        self.comp_term()
        # Handle (op term)*
        while self.tokenizer.get_token() in OPS:
            self.process_fixed(self.tokenizer.get_token())
            self.comp_term()
        self.file_out.write("</expression>\n")
        
    def comp_term(self):
        self.file_out.write("<term>\n")
        current_token = self.tokenizer.get_token()
        token_type = self.tokenizer.token_type()
        # Handle integerConstant|stringConstant
        if token_type in ("INT_CONST", "STRING_CONST"):
            self.process_chosen()
        # Handle keywordConstant
        elif current_token in KEYWORD_CONSTANTS:
            self.process_fixed(current_token)
        # Handle unaryOp term
        elif current_token in UNARY_OPS:
            self.process_fixed(current_token)
            self.comp_term()
        # Handle '(' expression ')'
        elif current_token == "(":
            self.process_fixed("(")
            self.comp_expression()
            self.process_fixed(")")
        # Handle varName|varName '[' expression ']'|subroutineCall
        elif token_type == "IDENTIFIER":
            # Handle varName|subroutineName|className
            self.process_chosen()
            # Handle '[' expression ']'
            if self.tokenizer.get_token() == "[":
                self.process_fixed("[")
                self.comp_expression()
                self.process_fixed("]")
            # Handle subroutineCall
            elif self.tokenizer.get_token() in ("(", "."):
                self.comp_call_suffix()
        else:
            raise JackSyntaxError(f"Expected a valid term but got '{current_token}'")
        self.file_out.write("</term>\n")
        
    def comp_call_suffix(self):
        # Handle '(' expressionList ')'
        if self.tokenizer.get_token() == "(":
            self.process_fixed("(")
            self.comp_expression_list()
            self.process_fixed(")")
        # Handle '.' subroutineName '(' expressionList ')'
        elif self.tokenizer.get_token() == ".":
            self.process_fixed(".")
            self.process_chosen()
            self.process_fixed("(")
            self.comp_expression_list()
            self.process_fixed(")")
        
    def comp_expression_list(self):
        self.file_out.write("<expressionList>\n")
        # Handle (expression (',' expression)*)?
        if self.tokenizer.get_token() != ")":
            self.comp_expression()
            # Handle (',' expression)*
            while self.tokenizer.get_token() == ",":
                self.process_fixed(",")
                self.comp_expression()
        self.file_out.write("</expressionList>\n")
     
    def comp_type(self):
        # Handle 'int'|'char'|'boolean'|className
        if self.tokenizer.get_token() in ("int", "char", "boolean"):
            self.process_fixed(self.tokenizer.get_token())
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
            else: 
                raise JackSyntaxError(f"Expected keyword or symbol but got '{current_token}'")
        else: 
            raise JackSyntaxError(f"Expected '{token}' but got '{current_token}'")
        self.tokenizer.advance()
    
    def process_chosen(self):
        # Handle identifier|integerConstant|stringConstant
        current_token = self.tokenizer.get_token()
        token_type = self.tokenizer.token_type()
        if token_type == "IDENTIFIER": 
            self.file_out.write("<identifier> " + current_token + " </identifier>\n")
        elif token_type == "STRING_CONST": 
            self.file_out.write("<stringConstant> " + self.tokenizer.str_val() + " </stringConstant>\n")
        elif token_type == "INT_CONST": 
            self.file_out.write("<integerConstant> " + str(self.tokenizer.int_val()) + " </integerConstant>\n")
        else:
            raise JackSyntaxError(f"Expected identifier, string, or integer but got '{current_token}'")
        self.tokenizer.advance()
