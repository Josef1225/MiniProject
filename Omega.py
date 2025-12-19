"""
Omega (ω) Symbol Class
Represents infinity in Petri Nets with special properties:
- ω > n for all integers n
- ω ± n = ω
- ω ≥ ω
"""

class Omega:
    """Special ω symbol representing unbounded/infinite tokens"""
    
    def __init__(self):
        self.symbol = "ω"
    
    def __str__(self):
        return self.symbol
    
    def __repr__(self):
        return "Omega()"
    
    def __eq__(self, other):
        """ω == ω returns True, ω == anything else returns False"""
        return isinstance(other, Omega)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __gt__(self, other):
        """ω > n always True for any integer n"""
        return not isinstance(other, Omega)
    
    def __lt__(self, other):
        """ω is never less than anything"""
        return False
    
    def __ge__(self, other):
        """ω ≥ ω returns True, ω ≥ n always True"""
        return True
    
    def __le__(self, other):
        """ω ≤ only other ω"""
        return isinstance(other, Omega)
    
    def __add__(self, other):
        """ω + n = ω"""
        return self
    
    def __sub__(self, other):
        """ω - n = ω"""
        return self
    
    def __hash__(self):
        """Hash for dictionary/set operations"""
        return hash("omega")