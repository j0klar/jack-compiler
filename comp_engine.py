class Comp_Engine:

    def __init__(self, tokenizer, file_out):
        self.tokenizer = tokenizer
        self.file_out = file_out
        
    def comp_class(self):
        self.tokenizer.advance()
        self.file_out.write("<class>\n")
        self.process_token("class")
        if self.tokenizer.token_type() == "IDENTIFIER": 
            self.file_out.write("  <identifier> " + self.tokenizer.get_token() + " </identifier>\n")
        else: print("Syntax error while processing " + self.tokenizer.get_token())
        self.process_token("{")
        self.comp_class_var_dec()
        self.comp_subroutine()
        self.process_token("}")
        self.file_out.write("</class>")
        
    def comp_class_var_dec(self):
        pass
        
    def comp_subroutine(self):
        pass
        
    def comp_parameter_list(self):
        pass
        
    def comp_subroutine_body(self):
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
        
    def process_token(self, token):
        current_token = self.tokenizer.get_token()
        if current_token == token:
            self.write_xml(token)
        else: print("Syntax error while processing " + current_token)
        self.tokenizer.advance()
            
    def write_xml(self, token):
        pass
