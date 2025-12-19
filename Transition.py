"""
Transition Class
Represents a transition in Petri Net with input/output arcs
"""

from typing import Dict
from Marking import Marking
from Omega import Omega


class Transition:
    """Represents a transition with input and output arcs"""
    
    def __init__(self, name: str, input_arcs: Dict[str, int], output_arcs: Dict[str, int]):
        """
        Initialize a transition
        
        Args:
            name: Transition name
            input_arcs: Dictionary {place_name: weight}
            output_arcs: Dictionary {place_name: weight}
        """
        self.name = name
        self.input_arcs = input_arcs
        self.output_arcs = output_arcs
    
    def __str__(self):
        return f"Transition('{self.name}')"
    
    def __repr__(self):
        return f"Transition(name='{self.name}', in={self.input_arcs}, out={self.output_arcs})"
    
    def is_enabled(self, marking: Marking) -> bool:
        """
        Check if transition is enabled in given marking
        
        Args:
            marking: Current marking to check
            
        Returns:
            True if transition can fire, False otherwise
        """
        for place, required_tokens in self.input_arcs.items():
            if place not in marking.places:
                return False
            
            idx = marking.places.index(place)
            current_tokens = marking.values[idx]
            
            # ω always has enough tokens
            if isinstance(current_tokens, Omega):
                continue
            
            # Check if regular integer has enough tokens
            if current_tokens < required_tokens:
                return False
        
        return True
    
    def fire(self, marking: Marking) -> Marking:
        """
        Fire the transition on given marking
        
        Args:
            marking: Current marking
            
        Returns:
            New marking after firing
        """
        new_marking = marking.copy()
        
        # Remove tokens from input places
        for place, weight in self.input_arcs.items():
            idx = new_marking.places.index(place)
            current_val = new_marking.values[idx]
            
            # ω - n = ω (ω remains unchanged)
            if not isinstance(current_val, Omega):
                new_marking.values[idx] -= weight
        
        # Add tokens to output places
        for place, weight in self.output_arcs.items():
            idx = new_marking.places.index(place)
            current_val = new_marking.values[idx]
            
            # ω + n = ω (ω remains unchanged)
            if not isinstance(current_val, Omega):
                new_marking.values[idx] += weight
        
        return new_marking
    
    def get_input_vector(self, places: list) -> list:
        """Get input arc weights as vector matching places order"""
        vector = [0] * len(places)
        for place, weight in self.input_arcs.items():
            if place in places:
                idx = places.index(place)
                vector[idx] = weight
        return vector
    
    def get_output_vector(self, places: list) -> list:
        """Get output arc weights as vector matching places order"""
        vector = [0] * len(places)
        for place, weight in self.output_arcs.items():
            if place in places:
                idx = places.index(place)
                vector[idx] = weight
        return vector