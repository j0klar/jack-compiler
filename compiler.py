"""Performs compilation for one or more .jack-files and outputs one .vm-file each."""

from tokenizer import Tokenizer
from symbol_table import SymbolTable
from code_writer import CodeWriter
from comp_engine import CompEngine
from errors import JackSyntaxError
import sys, os

def main():
    path_in = sys.argv[1]
    try:
        # Compile single .jack-file
        if os.path.isfile(path_in) and path_in[-5:] == ".jack":
            _compile_file(path_in)
        # Compile directory of .jack-files
        elif os.path.isdir(path_in):
            for file_in in os.listdir(path_in):
                if file_in[-5:] == ".jack":
                    _compile_file(os.path.join(path_in, file_in))
        else:
            print(f"Error: '{path_in}' is not a .jack file or directory", file=sys.stderr)
            sys.exit(1)
    # Centralized error handling 
    except JackSyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(1)
           
def _compile_file(path):
    tokenizer = Tokenizer(path)
    with open(path[:-5]+".vm", "w") as file_out:
        symbol_table = SymbolTable()
        code_writer = CodeWriter(file_out)
        comp_engine = CompEngine(tokenizer, symbol_table, code_writer)
        comp_engine.comp_class()
    
if __name__ == "__main__":
    main()
