"""Performs syntax analysis for one or more .jack-files and outputs one .xml-file each."""

from tokenizer import Tokenizer
from comp_engine import Comp_Engine
import sys, os
    
def main():
    path_in = sys.argv[1]
       
    if os.path.isfile(path_in) and path_in[-5:] == ".jack":
        tokenizer = Tokenizer(path_in)
        with open(path_in[:-5]+"F.xml", "w") as file_out:
            _tokenize_file(tokenizer, file_out)
        
    elif os.path.isdir(path_in):
        dir_in = os.listdir(path_in)
        for file in dir_in:
            if file[-5:] == ".jack":
                tokenizer = Tokenizer(os.path.join(path_in, file))
                with open(os.path.join(path_in, file[:-5]+"F.xml"), "w") as file_out:
                    _tokenize_file(tokenizer, file_out)

def _tokenize_file(tokenizer, file):
    file.write("<tokens>\n")
    while tokenizer.more_tokens():
        tokenizer.advance()
        if tokenizer.token_type() == "KEYWORD": 
            file.write("<keyword> " + tokenizer.get_token() + " </keyword>\n")
        elif tokenizer.token_type() == "SYMBOL":
            token = tokenizer.get_token()
            match token:
                case "<": token = "&lt;"
                case ">": token = "&gt;"
                case "&": token = "&amp;"
            file.write("<symbol> " + token + " </symbol>\n")
        elif tokenizer.token_type() == "IDENTIFIER": 
            file.write("<identifier> " + tokenizer.get_token() + " </identifier>\n")
        elif tokenizer.token_type() == "STRING_CONST": 
            file.write("<stringConstant> " + tokenizer.str_val() + " </stringConstant>\n")
        elif tokenizer.token_type() == "INT_CONST": 
            file.write("<integerConstant> " + str(tokenizer.int_val()) + " </integerConstant>\n")
    file.write("</tokens>")
    
if __name__ == "__main__":
    main()
