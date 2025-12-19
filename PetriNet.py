"""
PetriNet Class
Main class representing the Petri Net structure
"""

from typing import List, Dict, Optional
from Marking import Marking
from Transition import Transition


class PetriNet:
    """Main Petri Net class containing places, transitions, and markings"""
    
    def __init__(self, name: str = "PetriNet"):
        """
        Initialize an empty Petri Net
        
        Args:
            name: Name of the Petri Net
        """
        self.name = name
        self.places = []  # List of place names
        self.transitions = []  # List of Transition objects
        self.initial_marking = None  # Initial Marking object
    
    def __str__(self):
        return f"PetriNet('{self.name}', places={len(self.places)}, transitions={len(self.transitions)})"
    
    def add_place(self, name: str) -> None:
        """
        Add a place to the Petri Net
        
        Args:
            name: Name of the place
        """
        if name not in self.places:
            self.places.append(name)
        else:
            raise ValueError(f"Place '{name}' already exists")
    
    def add_places(self, names: List[str]) -> None:
        """
        Add multiple places
        
        Args:
            names: List of place names
        """
        for name in names:
            self.add_place(name)
    
    def add_transition(self, name: str, input_arcs: Dict[str, int], 
                       output_arcs: Dict[str, int]) -> Transition:
        """
        Add a transition to the Petri Net
        
        Args:
            name: Transition name
            input_arcs: Dictionary of input arcs {place: weight}
            output_arcs: Dictionary of output arcs {place: weight}
            
        Returns:
            The created Transition object
        """
        # Validate places exist
        all_places = set(self.places)
        input_places = set(input_arcs.keys())
        output_places = set(output_arcs.keys())
        
        if not input_places.issubset(all_places):
            missing = input_places - all_places
            raise ValueError(f"Input places not found: {missing}")
        
        if not output_places.issubset(all_places):
            missing = output_places - all_places
            raise ValueError(f"Output places not found: {missing}")
        
        # Check for duplicate transition names
        if any(t.name == name for t in self.transitions):
            raise ValueError(f"Transition '{name}' already exists")
        
        transition = Transition(name, input_arcs, output_arcs)
        self.transitions.append(transition)
        return transition
    
    def set_initial_marking(self, marking_dict: Dict[str, int]) -> None:
        """
        Set the initial marking
        
        Args:
            marking_dict: Dictionary {place_name: token_count}
        """
        values = []
        for place in self.places:
            if place in marking_dict:
                values.append(marking_dict[place])
            else:
                values.append(0)  # Default to 0 tokens
        
        self.initial_marking = Marking(self.places, values)
    
    def get_initial_marking(self) -> Marking:
        """
        Get the initial marking
        
        Returns:
            Initial Marking object
        """
        if self.initial_marking is None:
            # Default to all zeros
            values = [0] * len(self.places)
            self.initial_marking = Marking(self.places, values)
        return self.initial_marking
    
    def get_transition_by_name(self, name: str) -> Optional[Transition]:
        """
        Get transition by name
        
        Args:
            name: Transition name
            
        Returns:
            Transition object or None if not found
        """
        for transition in self.transitions:
            if transition.name == name:
                return transition
        return None
    
    def get_incidence_matrix(self):
        """
        Get incidence matrix (C = Output - Input)
        
        Returns:
            Matrix as list of lists
        """
        matrix = []
        for transition in self.transitions:
            row = []
            input_vec = transition.get_input_vector(self.places)
            output_vec = transition.get_output_vector(self.places)
            # C(p,t) = Output(p,t) - Input(p,t)
            row = [output_vec[i] - input_vec[i] for i in range(len(self.places))]
            matrix.append(row)
        return matrix
    
    def to_dict(self):
        """Convert Petri Net to dictionary for serialization"""
        return {
            "name": self.name,
            "places": self.places,
            "transitions": [
                {
                    "name": t.name,
                    "input": t.input_arcs,
                    "output": t.output_arcs
                }
                for t in self.transitions
            ],
            "initial_marking": self.initial_marking.get_dict() if self.initial_marking else {}
        }