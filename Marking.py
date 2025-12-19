"""
Marking Class
Represents a state (vector of tokens) in the Petri Net
"""

from typing import List, Union
from Omega import Omega


class Marking:
    """Represents a marking (state) in the Petri Net"""
    
    def __init__(self, places: List[str], values: List[Union[int, Omega]]):
        """
        Initialize a marking
        
        Args:
            places: List of place names in order
            values: List of token counts for each place
        """
        self.places = places  # List of place names
        self.values = values  # List of token counts (int or Omega)
        self.tag = "new"  # "new", "old", "dead-end"
        self.children = {}  # Dict: transition_name -> child_marking
        self.parent = None  # Parent marking in tree
        self.path_to_root = []  # List of markings from root to this node
    
    def __str__(self):
        """String representation of marking"""
        pairs = [f"{p}={v}" for p, v in zip(self.places, self.values)]
        return f"({', '.join(pairs)}) [{self.tag}]"
    
    def __repr__(self):
        return f"Marking({self.places}, {self.values}, tag='{self.tag}')"
    
    def __eq__(self, other):
        """Check if two markings are identical"""
        if not isinstance(other, Marking):
            return False
        if len(self.values) != len(other.values):
            return False
        return all(v1 == v2 for v1, v2 in zip(self.values, other.values))
    
    def __hash__(self):
        """Hash for set/dictionary operations"""
        return hash(tuple(str(v) for v in self.values))
    
    def copy(self):
        """Create a deep copy of the marking"""
        # Copy the values list (int values are immutable, Omega is singleton-like)
        values_copy = []
        for val in self.values:
            if isinstance(val, Omega):
                values_copy.append(Omega())
            else:
                values_copy.append(val)
        
        new_marking = Marking(self.places.copy(), values_copy)
        new_marking.tag = self.tag
        return new_marking
    
    def get_dict(self):
        """Convert marking to dictionary representation"""
        return {place: str(value) for place, value in zip(self.places, self.values)}
    
    def get_vector(self):
        """Get marking as vector (list of values)"""
        return self.values.copy()