from tokenizer import Tokenizer
from comp_engine import Comp_Engine
import sys, os
    
def main():
    path_in = sys.argv[1]
    
    if os.path.isfile(path_in) and path_in[-5:] == ".jack":
        tokenizer = Tokenizer(path_in)
        
    elif os.path.isdir(path_in):
        dir_in = os.listdir(path_in)
        for file in dir_in:
            if file[-5:] == ".jack":
                tokenizer = Tokenizer(os.path.join(path_in, file))
    
if __name__ == "__main__":
    main()
