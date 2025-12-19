"""
KarpMillerAlgorithm Class
Implements the Karp-Miller algorithm for coverability trees
"""

from typing import List, Set, Optional
from PetriNet import PetriNet
from Marking import Marking
from Transition import Transition
from Omega import Omega


class KarpMillerAlgorithm:
    """Implementation of the Karp-Miller algorithm for coverability trees"""
    
    def __init__(self, petri_net: PetriNet):
        """
        Initialize algorithm with a Petri Net
        
        Args:
            petri_net: The Petri Net to analyze
        """
        self.petri_net = petri_net
        self.root = None  # Root of coverability tree
        self.nodes = []  # All nodes in the tree
        self.visited_set = set()  # Set of visited markings (for optimization)
    
    def run(self) -> Marking:
        """
        Execute the Karp-Miller algorithm
        
        Returns:
            Root marking of the coverability tree
        """
        # Step 1: Label the initial marking as root and tag it "new"
        self.root = self.petri_net.get_initial_marking().copy()
        self.root.tag = "new"
        self.root.path_to_root = [self.root]
        self.nodes = [self.root]
        self.visited_set = set()
        
        # Step 2: While "new" markings exist
        while any(node.tag == "new" for node in self.nodes):
            # Find a new marking
            M = self._find_new_marking()
            if M is None:
                break
            
            # Step 2a: Remove "new" tag
            M.tag = ""
            
            # Step 2b: Check if M is identical to a marking on path to root
            if self._is_duplicate_on_path(M):
                M.tag = "old"
                continue
            
            # Step 2c: Check if no transitions enabled
            enabled_transitions = self._get_enabled_transitions(M)
            if not enabled_transitions:
                M.tag = "dead-end"
                continue
            
            # Step 2d: For each enabled transition
            for transition in enabled_transitions:
                self._process_transition(M, transition)
        
        return self.root
    
    def _find_new_marking(self) -> Optional[Marking]:
        """Find and return a marking with 'new' tag"""
        for node in self.nodes:
            if node.tag == "new":
                return node
        return None
    
    def _get_enabled_transitions(self, marking: Marking) -> List[Transition]:
        """Get all enabled transitions in a marking"""
        enabled = []
        for transition in self.petri_net.transitions:
            if transition.is_enabled(marking):
                enabled.append(transition)
        return enabled
    
    def _is_duplicate_on_path(self, marking: Marking) -> bool:
        """
        Check if marking is identical to any marking on path from root
        
        Args:
            marking: Marking to check
            
        Returns:
            True if duplicate found, False otherwise
        """
        # Check all ancestors except self
        for ancestor in marking.path_to_root[:-1]:
            if self._markings_equal(marking, ancestor):
                return True
        return False
    
    def _process_transition(self, M: Marking, transition: Transition) -> None:
        """
        Process firing a transition from marking M
        
        Args:
            M: Current marking
            transition: Transition to fire
        """
        # Step 2d.i: Obtain marking M' from firing t
        M_prime = transition.fire(M)
        M_prime.parent = M
        M_prime.path_to_root = M.path_to_root + [M_prime]
        
        # Step 2d.ii: Check for coverable markings on path
        self._apply_omega_if_covered(M_prime, M.path_to_root)
        
        # Step 2d.iii: Introduce M' as node
        M_prime.tag = "new"
        M.children[transition.name] = M_prime
        self.nodes.append(M_prime)
    
    def _apply_omega_if_covered(self, M_prime: Marking, path: List[Marking]) -> None:
        """
        Apply ω substitution if M' covers an ancestor
        
        Args:
            M_prime: New marking to check
            path: Path from root to parent
        """
        for M_double_prime in path:
            if self._covers(M_prime, M_double_prime) and not self._markings_equal(M_prime, M_double_prime):
                # Replace with ω where M'(p) > M''(p)
                for i in range(len(M_prime.values)):
                    if self._greater_than(M_prime.values[i], M_double_prime.values[i]):
                        M_prime.values[i] = Omega()
                break  # Only need to check first coverable ancestor
    
    def _markings_equal(self, m1: Marking, m2: Marking) -> bool:
        """Check if two markings are equal"""
        if len(m1.values) != len(m2.values):
            return False
        return all(v1 == v2 for v1, v2 in zip(m1.values, m2.values))
    
    def _covers(self, m1: Marking, m2: Marking) -> bool:
        """
        Check if m1 covers m2 (m1 ≥ m2 component-wise)
        
        Args:
            m1: First marking
            m2: Second marking
            
        Returns:
            True if m1 covers m2
        """
        for v1, v2 in zip(m1.values, m2.values):
            if not self._greater_or_equal(v1, v2):
                return False
        return True
    
    def _greater_than(self, v1, v2) -> bool:
        """Check if v1 > v2 (with ω handling)"""
        if isinstance(v1, Omega) and not isinstance(v2, Omega):
            return True
        if not isinstance(v1, Omega) and not isinstance(v2, Omega):
            return v1 > v2
        return False
    
    def _greater_or_equal(self, v1, v2) -> bool:
        """Check if v1 ≥ v2 (with ω handling)"""
        if isinstance(v1, Omega) and isinstance(v2, Omega):
            return True
        if isinstance(v1, Omega):
            return True
        if isinstance(v2, Omega):
            return False
        return v1 >= v2
    
    def get_tree_structure(self) -> dict:
        """
        Get tree structure as nested dictionary
        
        Returns:
            Dictionary representing the tree
        """
        def _build_tree(node: Marking) -> dict:
            children = {}
            for trans_name, child in node.children.items():
                children[trans_name] = _build_tree(child)
            
            return {
                "marking": node.get_dict(),
                "tag": node.tag,
                "children": children
            }
        
        return _build_tree(self.root)
    
    def get_statistics(self) -> dict:
        """Get statistics about the coverability tree"""
        stats = {
            "total_nodes": len(self.nodes),
            "new_nodes": sum(1 for n in self.nodes if n.tag == "new"),
            "old_nodes": sum(1 for n in self.nodes if n.tag == "old"),
            "dead_end_nodes": sum(1 for n in self.nodes if n.tag == "dead-end"),
            "has_omega": any(
                isinstance(val, Omega)
                for node in self.nodes
                for val in node.values
            ),
            "max_depth": self._calculate_max_depth(),
            "unique_markings": len(set(hash(node) for node in self.nodes))
        }
        return stats
    
    def _calculate_max_depth(self) -> int:
        """Calculate maximum depth of the tree"""
        max_depth = 0
        for node in self.nodes:
            depth = len(node.path_to_root)
            if depth > max_depth:
                max_depth = depth
        return max_depth
    
    def print_tree(self, node: Marking = None, level: int = 0, show_tags: bool = True) -> None:
        """
        Print the coverability tree
        
        Args:
            node: Starting node (defaults to root)
            level: Current depth level
            show_tags: Whether to show node tags
        """
        if node is None:
            node = self.root
        
        indent = "  " * level
        marking_str = " | ".join(f"{p}={v}" for p, v in zip(node.places, node.values))
        
        if show_tags and node.tag:
            print(f"{indent}{marking_str} [{node.tag}]")
        else:
            print(f"{indent}{marking_str}")
        
        for trans_name, child in node.children.items():
            print(f"{indent}  --{trans_name}-->")
            self.print_tree(child, level + 1, show_tags)