"""
Main Application File
Entry point for the Karp-Miller Algorithm implementation
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PetriNetGUI import PetriNetGUI
from PetriNet import PetriNet
from KarpMillerAlgorithm import KarpMillerAlgorithm
from Marking import Marking
from Transition import Transition
from Omega import Omega


def run_example():
    """Run a complete example programmatically"""
    print("=" * 70)
    print("KARP-MILLER ALGORITHM EXAMPLE")
    print("=" * 70)
    
    # Create a Petri Net
    print("\n1. Creating Petri Net...")
    net = PetriNet("ExampleNet")
    
    # Add places
    net.add_places(["P0", "P1", "P2"])
    
    # Set initial marking
    net.set_initial_marking({"P0": 1, "P2": 1})
    
    # Add transitions
    net.add_transition("t1", {"P0": 1}, {"P1": 1})
    net.add_transition("t2", {"P1": 1}, {"P0": 1, "P2": 1})
    
    print(f"   Places: {net.places}")
    print(f"   Initial marking: {net.initial_marking}")
    print(f"   Transitions: {[t.name for t in net.transitions]}")
    
    # Run Karp-Miller algorithm
    print("\n2. Running Karp-Miller Algorithm...")
    algorithm = KarpMillerAlgorithm(net)
    root = algorithm.run()
    
    # Print results
    print("\n3. Coverability Tree:")
    print("-" * 40)
    algorithm.print_tree(root)
    
    # Print statistics
    print("\n4. Statistics:")
    print("-" * 40)
    stats = algorithm.get_statistics()
    for key, value in stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Print properties
    print("\n5. Properties Analysis:")
    print("-" * 40)
    if stats['has_omega']:
        print("   ✗ The net is UNBOUNDED")
    else:
        print("   ✓ The net is BOUNDED")
    
    if stats['dead_end_nodes'] > 0:
        print(f"   ✗ Found {stats['dead_end_nodes']} dead marking(s)")
    else:
        print("   ✓ No dead markings")
    
    print("\n" + "=" * 70)


def main():
    """Main function with menu"""
    print("\n" + "=" * 70)
    print("KARP-MILLER ALGORITHM FOR PETRI NETS")
    print("=" * 70)
    
    while True:
        print("\nMAIN MENU:")
        print("1. Run GUI Application")
        print("2. Run Command-line Example")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Run GUI
            print("\nStarting GUI application...")
            app = PetriNetGUI()
            app.run()
            break  # Exit after GUI closes
            
        elif choice == "2":
            # Run command-line example
            run_example()
            continue
            
        elif choice == "3":
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()