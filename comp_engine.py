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
        self._consume("class")
        self.class_name = self.tokenizer.get_token()
        self._consume_identifier()
        # Handle '{'
        self._consume("{")
        # Handle classVarDec*
        while self.tokenizer.get_token() in ("static", "field"): 
            self.comp_class_var_dec()
        # Handle subroutineDec*
        while self.tokenizer.get_token() in ("constructor", "function", "method"): 
            self.comp_subroutine()
        # Handle '}'
        self._consume("}")
        
    def comp_class_var_dec(self):
        # Handle 'static'|'field'
        kind = self.tokenizer.get_token()
        if kind in ("static", "field"):
            self._consume(kind)
        else:
            raise JackSyntaxError(f"Expected 'static' or 'field' but got '{kind}'")
        # Handle type varName
        type_ = self.comp_type()
        name = self._consume_identifier()
        # Add (name, type_, kind) to symbol table
        self.symbol_table.define(name, type_, kind)
        # Handle (',' varName)*
        while self.tokenizer.get_token() == ",":
            self._consume(",")
            name = self._consume_identifier()
            self.symbol_table.define(name, type_, kind)
        # Handle ';'
        self._consume(";")
        
    def comp_subroutine(self):
        self.symbol_table.reset()
        # Handle 'constructor'|'function'|'method'
        sub_kind = self.tokenizer.get_token()
        if sub_kind == "method":
            self._consume(sub_kind)
            self.symbol_table.define("this", self.class_name, "arg")
        elif sub_kind in ("constructor", "function"):
            self._consume(sub_kind)
        else: 
            raise JackSyntaxError(f"Expected 'constructor', 'function', or 'method' but got '{sub_kind}'")
        # Handle 'void'|type
        if self.tokenizer.get_token() == "void": 
            self._consume("void")
        else: 
            self.comp_type()
        # Handle subroutineName '('
        sub_name = self._consume_identifier()
        self._consume("(")
        # Handle parameterList
        self.comp_parameter_list()
        # Handle ')' subroutineBody
        self._consume(")")
        self.comp_subroutine_body(sub_name, sub_kind)
        
    def comp_parameter_list(self):
        # Handle (type varName (',' type varName)*)?
        if self.tokenizer.get_token() != ")":
            type_ = self.comp_type()
            name = self._consume_identifier()
            self.symbol_table.define(name, type_, "arg")
            # Handle (',' type varName)*
            while self.tokenizer.get_token() == ",":
                self._consume(",")
                type_ = self.comp_type()
                name = self._consume_identifier()
                self.symbol_table.define(name, type_, "arg")
        
    def comp_subroutine_body(self, sub_name, sub_kind):
        # Handle '{' varDec*
        self._consume("{")
        while self.tokenizer.get_token() == "var":
            self.comp_var_dec()
        n_vars = self.symbol_table.var_count("var")
        # Generate subroutine declaration VM code    
        self.code_writer.write_function(f"{self.class_name}.{sub_name}", n_vars)
        if sub_kind == "method":
            self.code_writer.write_push("argument", 0)
            self.code_writer.write_pop("pointer", 0)
        elif sub_kind == "constructor":
            n_fields = self.symbol_table.var_count("field")
            self.code_writer.write_push("constant", n_fields)
            self.code_writer.write_call("Memory.alloc", 1)
            self.code_writer.write_pop("pointer", 0)
        # Handle statements '}'
        self.comp_statements()
        self._consume("}")
        
    def comp_var_dec(self):
        # Handle 'var' type varName
        self._consume("var")
        type_ = self.comp_type()
        name = self._consume_identifier()
        self.symbol_table.define(name, type_, "var")
        # Handle (',' varName)*
        while self.tokenizer.get_token() == ",":
            self._consume(",")
            name = self._consume_identifier()
            self.symbol_table.define(name, type_, "var")
        # Handle ';'
        self._consume(";")
        
    def comp_statements(self):
        # Handle (letStatement|ifStatement|whileStatement|doStatement|returnStatement)*
        while self.tokenizer.get_token() in ("let", "if", "while", "do", "return"):
            getattr(self, "comp_" + self.tokenizer.get_token())()
        
    def comp_let(self):
        # Handle 'let' varName
        self._consume("let")
        self._consume_identifier()
        # Handle ('[' expression ']')?
        if self.tokenizer.get_token() == "[":
            self._consume("[")
            self.comp_expression()
            self._consume("]")
        # Handle '=' expression ';'
        self._consume("=")
        self.comp_expression()
        self._consume(";")
        
    def comp_if(self):
        # Handle 'if' '('
        self._consume("if")
        self._consume("(")
        # Handle expression ')'
        self.comp_expression()
        self._consume(")")
        # Handle '{' statements '}'
        self._consume("{")
        self.comp_statements()
        self._consume("}")
        # Handle ('else' '{' statements '}')?
        if self.tokenizer.get_token() == "else":
            self._consume("else")
            self._consume("{")
            self.comp_statements()
            self._consume("}")
        
    def comp_while(self):
        # Handle 'while' '('
        self._consume("while")
        self._consume("(")
        # Handle expression ')'
        self.comp_expression()
        self._consume(")")
        # Handle '{' statements '}'
        self._consume("{")
        self.comp_statements()
        self._consume("}")
        
    def comp_do(self):
        # Handle 'do' subroutineCall ';'
        self._consume("do")
        self._consume_identifier()
        self.comp_call_suffix()
        self._consume(";")
        
    def comp_return(self):
        # Handle 'return' expression? ';'
        self._consume("return")
        if self.tokenizer.get_token() != ";":
            self.comp_expression()
        else:
            self.code_writer.write_push("constant", 0)
        self.code_writer.write_return()
        self._consume(";")
        
    def comp_expression(self):
        # Handle term
        self.comp_term()
        # Handle (op term)*
        while self.tokenizer.get_token() in OPS:
            self._consume(self.tokenizer.get_token())
            self.comp_term()
        
    def comp_term(self):
        current_token = self.tokenizer.get_token()
        token_type = self.tokenizer.token_type()
        # Handle integerConstant|stringConstant
        if token_type in ("INT_CONST", "STRING_CONST"):
            self.tokenizer.advance()
        # Handle keywordConstant
        elif current_token in KEYWORD_CONSTANTS:
            self._consume(current_token)
        # Handle unaryOp term
        elif current_token in UNARY_OPS:
            self._consume(current_token)
            self.comp_term()
        # Handle '(' expression ')'
        elif current_token == "(":
            self._consume("(")
            self.comp_expression()
            self._consume(")")
        # Handle varName|varName '[' expression ']'|subroutineCall
        elif token_type == "IDENTIFIER":
            # Handle varName|subroutineName|className
            self._consume_identifier()
            # Handle '[' expression ']'
            if self.tokenizer.get_token() == "[":
                self._consume("[")
                self.comp_expression()
                self._consume("]")
            # Handle subroutineCall
            elif self.tokenizer.get_token() in ("(", "."):
                self.comp_call_suffix()
        else:
            raise JackSyntaxError(f"Expected a valid term but got '{current_token}'")
        
    def comp_call_suffix(self):
        # Handle '(' expressionList ')'
        if self.tokenizer.get_token() == "(":
            self._consume("(")
            self.comp_expression_list()
            self._consume(")")
        # Handle '.' subroutineName '(' expressionList ')'
        elif self.tokenizer.get_token() == ".":
            self._consume(".")
            self._consume_identifier()
            self._consume("(")
            self.comp_expression_list()
            self._consume(")")
        
    def comp_expression_list(self):
        # Handle (expression (',' expression)*)?
        if self.tokenizer.get_token() != ")":
            self.comp_expression()
            # Handle (',' expression)*
            while self.tokenizer.get_token() == ",":
                self._consume(",")
                self.comp_expression()
                
    def comp_type(self):
        # Handle 'int'|'char'|'boolean'|className
        type_ = self.tokenizer.get_token()
        if type_ in ("int", "char", "boolean"):
            self._consume(type_)
            return type_
        else:
            return self._consume_identifier()
    
    def _consume(self, token):
        # Advance tokenizer beyond the current token
        current_token = self.tokenizer.get_token()
        if current_token != token:
            raise JackSyntaxError(f"Expected '{token}' but got '{current_token}'")
        self.tokenizer.advance()
        
    def _consume_identifier(self):
        # Advance tokenizer and return the current token
        current_token = self.tokenizer.get_token()
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise JackSyntaxError(f"Expected identifier but got '{current_token}'")
        self.tokenizer.advance()
        return current_token
