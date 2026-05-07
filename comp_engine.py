from errors import JackSyntaxError

OPS = frozenset("+-*/&|<>=")
UNARY_OPS = frozenset("-~")
KEYWORD_CONSTANTS = frozenset({"true", "false", "null", "this"})
SEGMENT_MAPPING = {"static":"static", "field":"this", "arg":"argument", "var":"local"}
OP_MAPPING = {"+":"add", "-":"sub", "&":"and", "|":"or", "<":"lt", ">":"gt", "=":"eq"}

class CompEngine:
    """Parses a stream of tokens and generates intermediate VM code according to the Jack grammar."""

    def __init__(self, tokenizer, symbol_table, code_writer):
        self.tokenizer = tokenizer
        self.symbol_table = symbol_table
        self.code_writer = code_writer
        self.label_count = 0
        
    def comp_class(self):
        self.tokenizer.advance()
        # Handle 'class' className
        self._consume("class")
        self.class_name = self._consume_identifier()
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
        # Add static/field variable to class-level symbol table
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
        if sub_kind not in ("constructor", "function", "method"):
            raise JackSyntaxError(f"Expected 'constructor', 'function', or 'method' but got '{sub_kind}'")
        self._consume(sub_kind)
        # Add current object to subroutine-level symbol table
        if sub_kind == "method":
            self.symbol_table.define("this", self.class_name, "arg")
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
            # Add argument variable to subroutine-level symbol table
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
        self.code_writer.write_function(f"{self.class_name}.{sub_name}", n_vars)
        # Generate setup code for special cases
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
        # Add local variable to subroutine-level symbol table
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
        name = self._consume_identifier()
        # Handle ('[' expression ']')?
        if self.tokenizer.get_token() == "[":
            self._push_variable(name)
            self._consume("[")
            self.comp_expression()
            self._consume("]")
            # Array access by *(arr+expression1) = expression2
            self.code_writer.write_arithmetic("add")
            self._consume("=")
            self.comp_expression()
            self.code_writer.write_pop("temp", 0)
            self.code_writer.write_pop("pointer", 1)
            self.code_writer.write_push("temp", 0)
            self.code_writer.write_pop("that", 0)
        # Handle '=' expression
        else:
            self._consume("=")
            self.comp_expression()
            # Store result in corresponding memory segment
            kind = self.symbol_table.kind_of(name)
            self.code_writer.write_pop(SEGMENT_MAPPING[kind], self.symbol_table.index_of(name))
        # Handle ';'
        self._consume(";")
        
    def comp_if(self):
        # Keep nested labels globally distinct
        self.label_count += 1
        local_count = self.label_count
        # Handle 'if' '('
        self._consume("if")
        self._consume("(")
        # Handle expression ')'
        self.comp_expression()
        self._consume(")")
        # Realize if-else branching with labels
        self.code_writer.write_arithmetic("not")
        self.code_writer.write_if(f"IF_FALSE{local_count}")
        # Handle '{' statements '}'
        self._consume("{")
        self.comp_statements()
        self._consume("}")
        self.code_writer.write_goto(f"IF_END{local_count}")
        # Handle ('else' '{' statements '}')?
        self.code_writer.write_label(f"IF_FALSE{local_count}")
        if self.tokenizer.get_token() == "else":
            self._consume("else")
            self._consume("{")
            self.comp_statements()
            self._consume("}")
        self.code_writer.write_label(f"IF_END{local_count}")
        
    def comp_while(self):
        # Keep nested labels globally distinct
        self.label_count += 1
        local_count = self.label_count
        # Handle 'while' '('
        self._consume("while")
        self._consume("(")
        # Realizes while loops with labels
        self.code_writer.write_label(f"WHILE_TRUE{local_count}")
        # Handle expression ')'
        self.comp_expression()
        self._consume(")")
        self.code_writer.write_arithmetic("not")
        self.code_writer.write_if(f"WHILE_END{local_count}")
        # Handle '{' statements '}'
        self._consume("{")
        self.comp_statements()
        self._consume("}")
        self.code_writer.write_goto(f"WHILE_TRUE{local_count}")
        self.code_writer.write_label(f"WHILE_END{local_count}")
        
    def comp_do(self):
        # Handle 'do' subroutineCall ';'
        self._consume("do")
        prefix = self._consume_identifier()
        self.comp_subroutine_call(prefix)
        # Discard return value
        self.code_writer.write_pop("temp", 0)
        self._consume(";")
        
    def comp_return(self):
        # Handle 'return' expression? ';'
        self._consume("return")
        if self.tokenizer.get_token() != ";":
            self.comp_expression()
        else:
            # Return 0 by convention if void
            self.code_writer.write_push("constant", 0)
        self.code_writer.write_return()
        self._consume(";")
        
    def comp_expression(self):
        # Handle term (op term)*
        self.comp_term()
        while self.tokenizer.get_token() in OPS:
            op = self.tokenizer.get_token()
            self._consume(op)
            self.comp_term()
            # Postfix handling of stack arithmetic
            if op == "*":
                self.code_writer.write_call("Math.multiply", 2)
            elif op == "/":
                self.code_writer.write_call("Math.divide", 2)
            else:
                self.code_writer.write_arithmetic(OP_MAPPING[op])
        
    def comp_term(self):
        # Pushes term's value on the stack
        token = self.tokenizer.get_token()
        ttype = self.tokenizer.token_type()
        # Handle integerConstant
        if ttype == "INT_CONST":
            integer = self.tokenizer.int_val()
            self.code_writer.write_push("constant", integer)
            self.tokenizer.advance()
        # Handle stringConstant    
        elif ttype == "STRING_CONST":
            string = self.tokenizer.str_val()
            self.code_writer.write_push("constant", len(string))
            self.code_writer.write_call("String.new", 1)
            # Iterative construction of string constant
            for char in string:
                self.code_writer.write_push("constant", ord(char))
                self.code_writer.write_call("String.appendChar", 2)
            self.tokenizer.advance()
        # Handle keywordConstant
        elif token in KEYWORD_CONSTANTS:
            if token == "true":
                self.code_writer.write_push("constant", 1)
                self.code_writer.write_arithmetic("neg")
            elif token in ("false", "null"):
                self.code_writer.write_push("constant", 0)
            else: # token == "this"
                self.code_writer.write_push("pointer", 0)
            self._consume(token)
        # Handle unaryOp term
        elif token in UNARY_OPS:
            self._consume(token)
            self.comp_term()
            # Postfix handling of stack arithmetic
            if token == "-":
                self.code_writer.write_arithmetic("neg")
            else: # token == "~"
                self.code_writer.write_arithmetic("not")
        # Handle '(' expression ')'
        elif token == "(":
            self._consume("(")
            self.comp_expression()
            self._consume(")")
        # Handle varName|varName '[' expression ']'|subroutineCall
        elif ttype == "IDENTIFIER":
            name = self._consume_identifier()
            # Handle '[' expression ']'
            if self.tokenizer.get_token() == "[":
                self._push_variable(name)
                self._consume("[")
                self.comp_expression()
                self._consume("]")
                # Array access by *(arr+expression)
                self.code_writer.write_arithmetic("add")
                self.code_writer.write_pop("pointer", 1)
                self.code_writer.write_push("that", 0)
            # Handle subroutineCall
            elif self.tokenizer.get_token() in ("(", "."):
                self.comp_subroutine_call(name)
            # Handle varName
            else:
                self._push_variable(name)
        else:
            raise JackSyntaxError(f"Expected a valid term but got '{token}'")
        
    def comp_subroutine_call(self, prefix):
        n_args = 0
        # Handle '.' subroutineName
        if self.tokenizer.get_token() == ".":
            self._consume(".")
            sub_name = self._consume_identifier()
            # In case of obj.method()   
            if self.symbol_table.kind_of(prefix) is not None:
                obj_type = self.symbol_table.type_of(prefix)
                self._push_variable(prefix)
                n_args += 1
                name = f"{obj_type}.{sub_name}"
            # In case of Class.function() or Class.constructor()
            else:
                name = f"{prefix}.{sub_name}"
        # In case of method()
        else:
            self.code_writer.write_push("pointer", 0)
            n_args += 1
            name = f"{self.class_name}.{prefix}"
        # Handle '(' expressionList ')'
        self._consume("(")
        n_args += self.comp_expression_list()
        self._consume(")")
        self.code_writer.write_call(name, n_args)
        
    def comp_expression_list(self):
        # Handle (expression (',' expression)*)?
        count = 0
        if self.tokenizer.get_token() != ")":
            self.comp_expression()
            count += 1
            # Handle (',' expression)*
            while self.tokenizer.get_token() == ",":
                self._consume(",")
                self.comp_expression()
                count += 1
        return count
                
    def comp_type(self):
        # Handle 'int'|'char'|'boolean'|className
        type_ = self.tokenizer.get_token()
        if type_ in ("int", "char", "boolean"):
            self._consume(type_)
            return type_
        else:
            return self._consume_identifier()
            
    def _push_variable(self, name):
        # Push variable from memory segment on the stack
        kind = self.symbol_table.kind_of(name)
        if kind is None:
            raise JackSyntaxError(f"Undefined variable '{name}'")
        self.code_writer.write_push(SEGMENT_MAPPING[kind], self.symbol_table.index_of(name))
    
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
