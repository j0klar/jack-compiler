from errors import JackSyntaxError

OPS = frozenset("+-*/&|<>=")
UNARY_OPS = frozenset("-~")
KEYWORD_CONSTANTS = frozenset({"true", "false", "null", "this"})

class CompEngine:
    """Parses a stream of tokens and generates intermediate VM code according to the Jack grammar."""

    def __init__(self, tokenizer, symbol_table, code_writer):
        self.tokenizer = tokenizer
        self.symbol_table = symbol_table
        self.code_writer = code_writer
        
    def comp_class(self):
        self.tokenizer.advance()
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
        
    def comp_class_var_dec(self):
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
        
    def comp_subroutine(self):
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
        
    def comp_parameter_list(self):
        # Handle (type varName (',' type varName)*)?
        if self.tokenizer.get_token() != ")":
            self.comp_type()
            self.process_chosen()
            # Handle (',' type varName)*
            while self.tokenizer.get_token() == ",":
                self.process_fixed(",")
                self.comp_type()
                self.process_chosen()
        
    def comp_subroutine_body(self):
        # Handle '{' varDec*
        self.process_fixed("{")
        while self.tokenizer.get_token() == "var":
            self.comp_var_dec()
        # Handle statements '}'
        self.comp_statements()
        self.process_fixed("}")
        
    def comp_var_dec(self):
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
        
    def comp_statements(self):
        # Handle (letStatement|ifStatement|whileStatement|doStatement|returnStatement)*
        while self.tokenizer.get_token() in ("let", "if", "while", "do", "return"):
            getattr(self, "comp_" + self.tokenizer.get_token())()
        
    def comp_let(self):
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
        
    def comp_if(self):
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
        
    def comp_while(self):
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
        
    def comp_do(self):
        # Handle 'do' subroutineCall ';'
        self.process_fixed("do")
        self.process_chosen()
        self.comp_call_suffix()
        self.process_fixed(";")
        
    def comp_return(self):
        # Handle 'return' expression? ';'
        self.process_fixed("return")
        if self.tokenizer.get_token() != ";":
            self.comp_expression()
        self.process_fixed(";")
        
    def comp_expression(self):
        # Handle term
        self.comp_term()
        # Handle (op term)*
        while self.tokenizer.get_token() in OPS:
            self.process_fixed(self.tokenizer.get_token())
            self.comp_term()
        
    def comp_term(self):
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
        # Handle (expression (',' expression)*)?
        if self.tokenizer.get_token() != ")":
            self.comp_expression()
            # Handle (',' expression)*
            while self.tokenizer.get_token() == ",":
                self.process_fixed(",")
                self.comp_expression()
     
    def comp_type(self):
        # Handle 'int'|'char'|'boolean'|className
        if self.tokenizer.get_token() in ("int", "char", "boolean"):
            self.process_fixed(self.tokenizer.get_token())
        else: 
            self.process_chosen()
    
    def consume(self, token):
        # Advance tokenizer beyond the current token
        current_token = self.tokenizer.get_token()
        if current_token != token:
            raise JackSyntaxError(f"Expected '{token}' but got '{current_token}'")
        self.tokenizer.advance()
