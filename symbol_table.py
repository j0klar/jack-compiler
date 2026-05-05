class SymbolTable:
    """Manages symbol tables for the compiler at the class- and subroutine-level."""
    
    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}
        self.count = {"static":0, "field":0, "arg":0, "var":0}  
        
    def reset(self):
        self.subroutine_table = {}
        self.count.update({"arg":0, "var":0})
        
    def define(self, name, type_, kind):
        if kind in ("static", "field"):
            self.class_table[name] = (type_, kind, self.count[kind])
        else:
            self.subroutine_table[name] = (type_, kind, self.count[kind])
        self.count[kind] += 1
        
    def var_count(self, kind):
        return self.count[kind]
        
    def type_of(self, name):
        entry = self._lookup(name)
        return entry[0] if entry else None
        
    def kind_of(self, name):
        entry = self._lookup(name)
        return entry[1] if entry else None
        
    def index_of(self, name):
        entry = self._lookup(name)
        return entry[2] if entry else None
        
    def _lookup(self, name):
        return self.subroutine_table.get(name) or self.class_table.get(name)
