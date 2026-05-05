class CodeWriter:
    """Generates and writes VM code to output file for a given VM command."""
    
    def __init__(self, file_out):
        self.file_out = file_out
        
    def write_push(self, segment, index):
        self.file_out.write(f"push {segment} {index}\n")
        
    def write_pop(self, segment, index):
        self.file_out.write(f"pop {segment} {index}\n")
        
    def write_arithmetic(self, command):
        self.file_out.write(f"{command}\n")
        
    def write_label(self, label):
        self.file_out.write(f"label {label}\n")
        
    def write_goto(self, label):
        self.file_out.write(f"goto {label}\n")
        
    def write_if(self, label):
        self.file_out.write(f"if-goto {label}\n")
        
    def write_call(self, name, n_args):
        self.file_out.write(f"call {name} {n_args}\n")
        
    def write_function(self, name, n_vars):
        self.file_out.write(f"function {name} {n_vars}\n")
        
    def write_return(self):
        self.file_out.write("return\n")
