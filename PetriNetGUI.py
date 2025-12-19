"""
PetriNetGUI Class
Tkinter-based graphical user interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from PetriNet import PetriNet
from KarpMillerAlgorithm import KarpMillerAlgorithm


class PetriNetGUI:
    """Graphical User Interface for Petri Net Analysis"""
    
    def __init__(self):
        """Initialize the GUI application"""
        self.petri_net = None
        self.algorithm = None
        
        self._setup_window()
        self._create_widgets()
        
    def _setup_window(self):
        """Setup main window properties"""
        self.root = tk.Tk()
        self.root.title("Karp-Miller Algorithm - Petri Nets Analyzer")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Left Panel - Input
        self._create_input_panel(main_container)
        
        # Right Panel - Output
        self._create_output_panel(main_container)
        
        # Bottom Panel - Properties
        self._create_properties_panel(main_container)
        
    def _create_input_panel(self, parent):
        """Create input panel with Petri Net definition"""
        input_frame = ttk.LabelFrame(parent, text="Petri Net Definition", padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Places
        ttk.Label(input_frame, text="Places:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(input_frame, text="Enter comma-separated place names:").grid(
            row=1, column=0, sticky=tk.W)
        self.places_entry = ttk.Entry(input_frame, width=40)
        self.places_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.places_entry.insert(0, "P0,P1,P2")
        
        # Initial Marking
        ttk.Label(input_frame, text="Initial Marking:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Label(input_frame, text="Format: Place=Value,Place=Value").grid(
            row=4, column=0, sticky=tk.W)
        ttk.Label(input_frame, text="Example: P0=1,P2=1 (unspecified places get 0)").grid(
            row=5, column=0, sticky=tk.W)
        self.marking_entry = ttk.Entry(input_frame, width=40)
        self.marking_entry.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.marking_entry.insert(0, "P0=1,P2=1")
        
        # Transitions
        ttk.Label(input_frame, text="Transitions:", font=('Arial', 10, 'bold')).grid(
            row=7, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Label(input_frame, text="JSON format with name, input, output:").grid(
            row=8, column=0, sticky=tk.W)
        
        # Text widget for transitions with scrollbar
        text_frame = ttk.Frame(input_frame)
        text_frame.grid(row=9, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.transitions_text = scrolledtext.ScrolledText(text_frame, width=45, height=12, wrap=tk.NONE)
        self.transitions_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Example transitions
        example = """[
  {
    "name": "t1",
    "input": {"P0": 1},
    "output": {"P1": 1}
  },
  {
    "name": "t2",
    "input": {"P1": 1},
    "output": {"P0": 1, "P2": 1}
  }
]"""
        self.transitions_text.insert("1.0", example)
        
        # Buttons frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=10, column=0, pady=20)
        
        ttk.Button(button_frame, text="Create Petri Net", 
                  command=self._create_petri_net, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Run Algorithm", 
                  command=self._run_algorithm, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear All", 
                  command=self._clear_all, width=15).grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Load Example", 
                  command=self._load_example, width=15).grid(row=2, column=0, columnspan=2)
        
    def _create_output_panel(self, parent):
        """Create output panel for coverability tree"""
        output_frame = ttk.LabelFrame(parent, text="Coverability Tree", padding="15")
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for output frame
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Tree display
        self.tree_display = scrolledtext.ScrolledText(
            output_frame, width=70, height=30, wrap=tk.NONE,
            font=('Courier', 10))
        self.tree_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_bar = ttk.Label(output_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def _create_properties_panel(self, parent):
        """Create properties analysis panel"""
        properties_frame = ttk.LabelFrame(parent, text="Properties Analysis", padding="15")
        properties_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Configure grid
        properties_frame.columnconfigure(0, weight=1)
        
        # Properties display
        self.properties_display = scrolledtext.ScrolledText(
            properties_frame, width=100, height=8, 
            font=('Courier', 9))
        self.properties_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def _create_petri_net(self):
        """Create Petri Net from user input"""
        try:
            # Clear previous results
            self.tree_display.delete("1.0", tk.END)
            self.properties_display.delete("1.0", tk.END)
            
            # Parse places
            places_str = self.places_entry.get().strip()
            if not places_str:
                raise ValueError("Please enter at least one place")
            
            places = [p.strip() for p in places_str.split(",") if p.strip()]
            if not places:
                raise ValueError("No valid places found")
            
            # Create Petri Net
            self.petri_net = PetriNet("UserPetriNet")
            for place in places:
                self.petri_net.add_place(place)
            
            # Parse initial marking
            marking_dict = {}
            marking_str = self.marking_entry.get().strip()
            if marking_str:
                for pair in marking_str.split(","):
                    pair = pair.strip()
                    if "=" in pair:
                        place, value = pair.split("=", 1)
                        place = place.strip()
                        value = value.strip()
                        
                        if place not in places:
                            raise ValueError(f"Place '{place}' not in places list")
                        
                        try:
                            marking_dict[place] = int(value)
                            if marking_dict[place] < 0:
                                raise ValueError(f"Token count for '{place}' cannot be negative")
                        except ValueError:
                            raise ValueError(f"Invalid token count for '{place}': '{value}'")
            
            # Set default 0 for unspecified places
            for place in places:
                if place not in marking_dict:
                    marking_dict[place] = 0
            
            self.petri_net.set_initial_marking(marking_dict)
            
            # Parse transitions
            transitions_json = self.transitions_text.get("1.0", tk.END).strip()
            if not transitions_json:
                raise ValueError("Please define at least one transition")
            
            transitions_data = json.loads(transitions_json)
            
            for i, trans_data in enumerate(transitions_data):
                if "name" not in trans_data:
                    raise ValueError(f"Transition {i}: Missing 'name' field")
                if "input" not in trans_data:
                    raise ValueError(f"Transition {trans_data['name']}: Missing 'input' field")
                if "output" not in trans_data:
                    raise ValueError(f"Transition {trans_data['name']}: Missing 'output' field")
                
                self.petri_net.add_transition(
                    trans_data["name"],
                    trans_data.get("input", {}),
                    trans_data.get("output", {})
                )
            
            # Update status
            self.status_bar.config(text=f"Petri Net created: {len(places)} places, {len(transitions_data)} transitions")
            messagebox.showinfo("Success", "Petri Net created successfully!")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON format:\n{str(e)}")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create Petri Net:\n{str(e)}")
    
    def _run_algorithm(self):
        """Run the Karp-Miller algorithm"""
        try:
            if self.petri_net is None:
                messagebox.showwarning("Warning", "Please create a Petri Net first!")
                return
            
            # Clear previous tree
            self.tree_display.delete("1.0", tk.END)
            self.properties_display.delete("1.0", tk.END)
            
            # Run algorithm
            self.algorithm = KarpMillerAlgorithm(self.petri_net)
            root = self.algorithm.run()
            
            # Display tree
            self._display_tree(root)
            
            # Analyze properties
            self._analyze_properties()
            
            # Update status
            stats = self.algorithm.get_statistics()
            self.status_bar.config(text=f"Algorithm completed: {stats['total_nodes']} nodes, "
                                      f"ω present: {stats['has_omega']}")
            
        except Exception as e:
            messagebox.showerror("Algorithm Error", f"Failed to run algorithm:\n{str(e)}")
    
    def _display_tree(self, node, level=0, prefix=""):
        """Recursively display the coverability tree"""
        indent = "  " * level
        
        # Format marking with colors
        marking_parts = []
        for p, v in zip(node.places, node.values):
            if str(v) == "ω":
                marking_parts.append(f"{p}=\033[91m{v}\033[0m")  # Red for ω
            else:
                marking_parts.append(f"{p}={v}")
        
        marking_str = " | ".join(marking_parts)
        
        # Add tag with color
        tag_color = {
            "old": "\033[93m",  # Yellow
            "dead-end": "\033[91m",  # Red
            "new": "\033[92m",  # Green
            "": "\033[0m"  # Default
        }.get(node.tag, "\033[0m")
        
        node_line = f"{prefix}{indent}{marking_str} [{tag_color}{node.tag}\033[0m]\n"
        self.tree_display.insert(tk.END, node_line)
        
        # Display children
        for trans_name, child in node.children.items():
            trans_line = f"{prefix}{indent}  --\033[94m{trans_name}\033[0m-->\n"
            self.tree_display.insert(tk.END, trans_line)
            self._display_tree(child, level + 1, prefix)
    
    def _analyze_properties(self):
        """Analyze and display Petri Net properties"""
        if not self.algorithm:
            return
        
        stats = self.algorithm.get_statistics()
        
        analysis = "=" * 60 + "\n"
        analysis += "PROPERTIES ANALYSIS\n"
        analysis += "=" * 60 + "\n\n"
        
        # Boundedness
        if stats['has_omega']:
            analysis += "✗ UNBOUNDED NETWORK\n"
            analysis += "   The Petri Net is unbounded (ω symbols present)\n"
            analysis += "   Some places can accumulate infinite tokens\n"
        else:
            analysis += "✓ BOUNDED NETWORK\n"
            analysis += "   All places have finite maximum token counts\n"
        
        analysis += "\n"
        
        # Dead markings
        if stats['dead_end_nodes'] > 0:
            analysis += f"✗ DEAD MARKINGS DETECTED: {stats['dead_end_nodes']}\n"
            analysis += "   Some states have no enabled transitions\n"
        else:
            analysis += "✓ NO DEAD MARKINGS\n"
            analysis += "   All states have at least one enabled transition\n"
        
        analysis += "\n"
        
        # Cycles
        if stats['old_nodes'] > 0:
            analysis += f"✓ CYCLES DETECTED: {stats['old_nodes']}\n"
            analysis += "   The net contains repetitive behavior patterns\n"
        else:
            analysis += "✗ NO CYCLES DETECTED\n"
            analysis += "   All paths lead to terminal states\n"
        
        analysis += "\n" + "=" * 60 + "\n"
        analysis += "STATISTICS\n"
        analysis += "=" * 60 + "\n\n"
        
        analysis += f"Total nodes in coverability tree: {stats['total_nodes']}\n"
        analysis += f"Maximum tree depth: {stats['max_depth']}\n"
        analysis += f"Unique markings: {stats['unique_markings']}\n"
        analysis += f"New nodes: {stats['new_nodes']}\n"
        analysis += f"Old nodes: {stats['old_nodes']}\n"
        analysis += f"Dead-end nodes: {stats['dead_end_nodes']}\n"
        
        self.properties_display.insert("1.0", analysis)
    
    def _clear_all(self):
        """Clear all inputs and outputs"""
        self.tree_display.delete("1.0", tk.END)
        self.properties_display.delete("1.0", tk.END)
        self.places_entry.delete(0, tk.END)
        self.marking_entry.delete(0, tk.END)
        self.transitions_text.delete("1.0", tk.END)
        self.petri_net = None
        self.algorithm = None
        self.status_bar.config(text="Cleared")
    
    def _load_example(self):
        """Load example Petri Net"""
        self.places_entry.delete(0, tk.END)
        self.places_entry.insert(0, "P0,P1,P2,P3")
        
        self.marking_entry.delete(0, tk.END)
        self.marking_entry.insert(0, "P0=2,P2=1")
        
        example = """[
  {
    "name": "t1",
    "input": {"P0": 1},
    "output": {"P1": 2}
  },
  {
    "name": "t2",
    "input": {"P1": 1, "P2": 1},
    "output": {"P0": 1, "P3": 1}
  },
  {
    "name": "t3",
    "input": {"P3": 1},
    "output": {"P2": 1}
  }
]"""
        
        self.transitions_text.delete("1.0", tk.END)
        self.transitions_text.insert("1.0", example)
        
        self.status_bar.config(text="Example loaded")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = PetriNetGUI()
    app.run()


if __name__ == "__main__":
    main()