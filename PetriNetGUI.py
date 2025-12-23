"""
PetriNetGUI Class
Tkinter-based GUI for Petri Net Analysis
(Coverability tree with simplified nodes + click for details)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import math

# Graph visualization imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Circle
from matplotlib import patheffects

from PetriNet import PetriNet
from KarpMillerAlgorithm import KarpMillerAlgorithm
from KarpMillerAlgorithm import Omega


class PetriNetGUI:
    def __init__(self):
        self.petri_net = None
        self.algorithm = None
        self.current_graph_window = None
        self.current_graph_canvas = None
        self.current_graph_fig = None
        self.current_graph_ax = None
        self.graph_nodes = {}  # Store node info for click handling

        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        self.root = tk.Tk()
        self.root.title("Karp-Miller Algorithm - Petri Nets Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(1100, 700)
        self.root.update_idletasks()
        width, height = 1200, 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        # Create main container with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create tabs
        self._create_input_tab()
        self._create_text_output_tab()
        
        # Properties panel at bottom
        self._create_properties_panel()

    # --------------------------- Input Tab ---------------------------
    def _create_input_tab(self):
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Input")
        
        input_panel = ttk.LabelFrame(input_frame, text="Petri Net Definition", padding="15")
        input_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(input_panel, text="Places (comma-separated):").grid(row=0, column=0, sticky="w")
        self.places_entry = ttk.Entry(input_panel, width=40)
        self.places_entry.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.places_entry.insert(0, "P0,P1,P2")

        ttk.Label(input_panel, text="Initial Marking (P0=1,P2=1):").grid(row=2, column=0, sticky="w")
        ttk.Label(input_panel, text="Format: Place=Value,Place=Value", font=('Arial', 8)).grid(row=3, column=0, sticky="w")
        self.marking_entry = ttk.Entry(input_panel, width=40)
        self.marking_entry.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        self.marking_entry.insert(0, "P0=1,P2=1")

        ttk.Label(input_panel, text="Transitions (JSON format):").grid(row=5, column=0, sticky="w")
        self.transitions_text = scrolledtext.ScrolledText(input_panel, width=50, height=12)
        self.transitions_text.grid(row=6, column=0, sticky="nsew", pady=(0, 10))

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

        button_frame = ttk.Frame(input_panel)
        button_frame.grid(row=7, column=0, pady=10)

        ttk.Button(button_frame, text="Create Petri Net", 
                  command=self._create_petri_net, width=20).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Run Algorithm", 
                  command=self._run_algorithm, width=20).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear All", 
                  command=self._clear_all, width=20).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(button_frame, text="Show Visual Graph", 
                  command=self._show_graph_view, width=20).grid(row=2, column=0, columnspan=2, pady=5)

        self.status_bar = ttk.Label(input_panel, 
                                   text="Ready - Enter Petri Net details", 
                                   relief=tk.SUNKEN, padding=3)
        self.status_bar.grid(row=8, column=0, sticky="ew", pady=(10, 0))

        input_panel.columnconfigure(0, weight=1)
        input_panel.rowconfigure(6, weight=1)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

    # --------------------------- Text Output Tab ---------------------------
    def _create_text_output_tab(self):
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Text Output")
        
        # Create paned window for tree and details
        paned = ttk.PanedWindow(text_frame, orient=tk.VERTICAL)
        paned.grid(row=0, column=0, sticky="nsew")
        
        # Tree display
        tree_frame = ttk.LabelFrame(paned, text="Coverability Tree", padding="10")
        self.tree_display = scrolledtext.ScrolledText(tree_frame, font=("Consolas", 10))
        self.tree_display.pack(fill="both", expand=True)
        paned.add(tree_frame, weight=2)
        
        # Node details panel (for graph clicks)
        details_frame = ttk.LabelFrame(paned, text="Node Details (Click nodes in visual graph)", padding="10")
        self.node_details_display = scrolledtext.ScrolledText(details_frame, height=6, font=("Consolas", 10))
        self.node_details_display.pack(fill="both", expand=True)
        paned.add(details_frame, weight=1)
        
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

    # --------------------------- Properties Panel ---------------------------
    def _create_properties_panel(self):
        properties_frame = ttk.LabelFrame(self.root, text="Properties Analysis", padding="10")
        properties_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.properties_display = scrolledtext.ScrolledText(properties_frame, height=6, font=("Consolas", 9))
        self.properties_display.pack(fill="both", expand=True)

        self.root.rowconfigure(1, weight=0)

    # --------------------------- Petri Net Creation ---------------------------
    def _create_petri_net(self):
        try:
            self.tree_display.delete("1.0", tk.END)
            self.properties_display.delete("1.0", tk.END)
            self.node_details_display.delete("1.0", tk.END)

            places = [p.strip() for p in self.places_entry.get().split(",") if p.strip()]
            self.petri_net = PetriNet("UserPetriNet")
            for p in places:
                self.petri_net.add_place(p)

            marking = {}
            marking_str = self.marking_entry.get().strip()
            if marking_str:
                for pair in marking_str.split(","):
                    pair = pair.strip()
                    if "=" in pair:
                        k, v = pair.split("=")
                        marking[k.strip()] = int(v.strip())
            for p in places:
                marking.setdefault(p, 0)
            self.petri_net.set_initial_marking(marking)

            transitions = json.loads(self.transitions_text.get("1.0", tk.END))
            for t in transitions:
                self.petri_net.add_transition(t["name"], t["input"], t["output"])

            self.status_bar.config(text="✓ Petri Net created")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --------------------------- Run Algorithm ---------------------------
    def _run_algorithm(self):
        if not self.petri_net:
            messagebox.showwarning("Warning", "Create a Petri Net first")
            return

        self.tree_display.delete("1.0", tk.END)
        self.properties_display.delete("1.0", tk.END)
        self.node_details_display.delete("1.0", tk.END)

        self.algorithm = KarpMillerAlgorithm(self.petri_net)
        root = self.algorithm.run()

        self._display_tree(root)
        self._analyze_properties()
        
        self.status_bar.config(text="✓ Algorithm completed - Click 'Show Visual Graph'")

    def _display_tree(self, node, level=0):
        indent = "    " * level
        marking = " | ".join(f"{p}={v}" for p, v in zip(node.places, node.values))
        self.tree_display.insert(tk.END, f"{indent}{marking} [{node.tag}]\n")
        for t, child in node.children.items():
            self.tree_display.insert(tk.END, f"{indent}  --> {t}\n")
            self._display_tree(child, level + 1)

    # --------------------------- Graph View ---------------------------
    def _show_graph_view(self):
        if not self.algorithm:
            messagebox.showwarning("Warning", "Run the algorithm first")
            return

        # Close previous graph window if exists
        if self.current_graph_window:
            try:
                self.current_graph_window.destroy()
            except:
                pass
        
        self.graph_nodes = {}  # Reset node storage
        
        win = tk.Toplevel(self.root)
        win.title("Coverability Tree - Visual Graph")
        win.geometry("1400x900")
        self.current_graph_window = win

        try:
            # Create figure with paned layout
            self.current_graph_fig, (self.current_graph_ax, details_ax) = plt.subplots(1, 2, figsize=(16, 10), 
                                                                                      gridspec_kw={'width_ratios': [3, 1]})
            self.current_graph_fig.patch.set_facecolor('#f5f5f5')
            
            # Build tree structure
            nodes = {}
            edges = []
            node_depths = {}
            
            def traverse(node, node_id, parent_id=None, transition=None, depth=0):
                """Traverse tree and collect nodes and edges"""
                # Create SIMPLE node label (just node number or small identifier)
                node_num = len(nodes) + 1
                if depth == 0:
                    label = f"Root\nM{node_num}"
                else:
                    label = f"M{node_num}"
                
                # Store full marking for click display
                full_marking = " | ".join(f"{p}={v}" for p, v in zip(node.places, node.values))
                if node.tag:
                    full_marking += f" [{node.tag}]"
                
                nodes[node_id] = {
                    'id': node_id,
                    'node': node,
                    'simple_label': label,
                    'full_marking': full_marking,
                    'node_number': node_num,
                    'x': 0,  # Will be set later
                    'y': 0,  # Will be set later
                    'children': [],
                    'depth': depth,
                    'parent': parent_id,
                    'incoming_transition': transition
                }
                node_depths[node_id] = depth
                
                if parent_id is not None and transition is not None:
                    edges.append({
                        'from': parent_id,
                        'to': node_id,
                        'label': transition
                    })
                
                # Add children
                for trans_name, child in node.children.items():
                    child_id = id(child)
                    nodes[node_id]['children'].append(child_id)
                    traverse(child, child_id, node_id, trans_name, depth + 1)
            
            # Start traversal from root
            if self.algorithm.root:
                traverse(self.algorithm.root, id(self.algorithm.root), depth=0)
            
            # Calculate max depth
            max_depth = max(node_depths.values()) if node_depths else 0
            
            # Calculate positions using hierarchical layout
            def calculate_layout(node_id, x_offset, depth):
                """Calculate positions for tree layout"""
                node = nodes[node_id]
                children = node['children']
                
                if not children:
                    # Leaf node
                    node['x'] = x_offset
                    node['y'] = -depth * 2.5
                    return x_offset + 4  # Spacing
                
                # Calculate positions for children first
                child_x = x_offset
                child_positions = []
                for child_id in children:
                    child_x = calculate_layout(child_id, child_x, depth + 1)
                    child_positions.append(nodes[child_id]['x'])
                
                # Position parent in middle of children
                if child_positions:
                    node['x'] = sum(child_positions) / len(child_positions)
                else:
                    node['x'] = x_offset
                node['y'] = -depth * 2.5
                
                return max(child_x, node['x'] + 4)
            
            if nodes:
                calculate_layout(id(self.algorithm.root), 0, 0)
            
            # Draw nodes with SIMPLE labels
            for node_id, node in nodes.items():
                petri_node = node['node']
                
                # Determine node type and color
                is_root = (node_id == id(self.algorithm.root))
                has_omega = any(isinstance(v, Omega) for v in petri_node.values)
                is_dead_end = not bool(petri_node.children)
                is_max_depth = (node['depth'] == max_depth)
                
                # Color selection
                if is_root:
                    color = '#fff2b2'  # Yellow
                    border_color = '#cc9900'
                    border_width = 3
                elif has_omega:
                    color = '#b2fab4'  # Light Green
                    border_color = '#009900'
                    border_width = 2
                elif is_dead_end:
                    color = '#f7b2b2'  # Light Red
                    border_color = '#990000'
                    border_width = 2
                elif is_max_depth:
                    color = '#ffd9b2'  # Orange
                    border_color = '#cc6600'
                    border_width = 2
                else:
                    color = '#e6f2ff'  # Light Blue
                    border_color = '#0066cc'
                    border_width = 2
                
                # Draw node as circle - FIXED: Proper picker usage
                node_radius = 0.8
                circle = Circle((node['x'], node['y']), node_radius, 
                               facecolor=color, edgecolor=border_color, 
                               linewidth=border_width, zorder=2,
                               picker=True)  # Set picker in constructor
                
                self.current_graph_ax.add_patch(circle)
                
                # Add SIMPLE label (just node number) - make it pickable too
                text = self.current_graph_ax.text(node['x'], node['y'], node['simple_label'],
                                                 fontsize=9, ha='center', va='center',
                                                 fontweight='bold', zorder=3,
                                                 picker=True)  # Text is also pickable
                
                # Store for click handling
                node['patch'] = circle
                node['text'] = text
                node['color'] = color
                node['border_color'] = border_color
                node['is_root'] = is_root
                self.graph_nodes[node_id] = node
            
            # Draw edges
            for edge in edges:
                from_node = nodes[edge['from']]
                to_node = nodes[edge['to']]
                
                dx = to_node['x'] - from_node['x']
                dy = to_node['y'] - from_node['y']
                length = math.sqrt(dx*dx + dy*dy)
                
                if length > 0:
                    dx /= length
                    dy /= length
                    
                    # Start and end points
                    start_x = from_node['x'] + dx * 0.8
                    start_y = from_node['y'] + dy * 0.8
                    end_x = to_node['x'] - dx * 0.8
                    end_y = to_node['y'] - dy * 0.8
                    
                    # Draw arrow
                    self.current_graph_ax.annotate('',
                                                  xy=(end_x, end_y),
                                                  xytext=(start_x, start_y),
                                                  arrowprops=dict(arrowstyle='->', 
                                                                color='#666666',
                                                                lw=2,
                                                                shrinkA=0,
                                                                shrinkB=0),
                                                  zorder=1)
                    
                    # Add transition label
                    label_x = start_x * 0.6 + end_x * 0.4
                    label_y = start_y * 0.6 + end_y * 0.4
                    
                    offset_x = -dy * 0.3
                    offset_y = dx * 0.3
                    
                    self.current_graph_ax.text(label_x + offset_x, 
                                              label_y + offset_y, 
                                              edge['label'],
                                              fontsize=9, 
                                              fontweight='bold',
                                              ha='center', 
                                              va='center',
                                              bbox=dict(boxstyle='round,pad=0.3',
                                                       facecolor='white',
                                                       edgecolor='lightgray',
                                                       alpha=0.9),
                                              zorder=4)
            
            # Set limits
            all_x = [node['x'] for node in nodes.values()]
            all_y = [node['y'] for node in nodes.values()]
            
            if all_x and all_y:
                x_min, x_max = min(all_x), max(all_x)
                y_min, y_max = min(all_y), max(all_y)
                
                x_padding = max(2.0, (x_max - x_min) * 0.2)
                y_padding = max(1.5, (y_max - y_min) * 0.2)
                
                self.current_graph_ax.set_xlim(x_min - x_padding, x_max + x_padding)
                self.current_graph_ax.set_ylim(y_min - y_padding, y_max + y_padding)
            
            self.current_graph_ax.set_aspect('equal')
            self.current_graph_ax.axis('off')
            self.current_graph_ax.set_title("Coverability Tree\n(Click nodes to see markings)", 
                                          fontsize=14, fontweight='bold', pad=20)
            
            # Setup details panel
            details_ax.axis('off')
            details_ax.set_title("Node Details", fontsize=12, fontweight='bold', pad=20)
            
            # Initial instruction text
            self.details_text = details_ax.text(0.5, 0.5, 
                                               "Click any node\nto see its\nfull marking here",
                                               transform=details_ax.transAxes,
                                               fontsize=11,
                                               ha='center', va='center',
                                               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
            
            # Add legend
            legend_text = (
                "Color Legend:\n"
                "• Yellow: Root node\n"
                "• Green: Contains ω\n"
                "• Red: Dead-end\n"
                "• Orange: Max depth\n"
                "• Blue: Regular node\n\n"
                "M# = Marking number\n"
                "(Click to see details)"
            )
            
            details_ax.text(0.02, 0.98, legend_text,
                           transform=details_ax.transAxes,
                           fontsize=9,
                           verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            # Add statistics
            if self.algorithm:
                stats = self.algorithm.get_statistics()
                stats_text = (f"Statistics:\n"
                             f"• Total nodes: {stats['total_nodes']}\n"
                             f"• Max depth: {max_depth}\n"
                             f"• ω present: {'Yes' if stats['has_omega'] else 'No'}\n"
                             f"• Dead ends: {stats['dead_end_nodes']}")
                
                details_ax.text(0.02, 0.02, stats_text,
                               transform=details_ax.transAxes,
                               fontsize=9,
                               verticalalignment='bottom',
                               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
            
            plt.tight_layout()
            
            # Create canvas
            self.current_graph_canvas = FigureCanvasTkAgg(self.current_graph_fig, master=win)
            self.current_graph_canvas.draw()
            
            # Add toolbar for zoom/pan
            toolbar = NavigationToolbar2Tk(self.current_graph_canvas, win)
            toolbar.update()
            
            # Pack canvas
            self.current_graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Connect click event
            self.current_graph_canvas.mpl_connect('pick_event', self._on_node_click)
            
            # Add control hints
            control_label = ttk.Label(win, 
                                     text="Click nodes to see markings | Use toolbar to: Zoom • Pan • Save • Reset",
                                     relief=tk.SUNKEN, padding=5)
            control_label.pack(side=tk.BOTTOM, fill=tk.X)
            
        except Exception as e:
            messagebox.showerror("Graph Error", f"Failed to create graph visualization:\n{str(e)}")
            import traceback
            traceback.print_exc()
            win.destroy()

    def _on_node_click(self, event):
        """Handle node click events"""
        # Check if artist is a circle (node) or text (node label)
        artist = event.artist
        
        # Find which node was clicked
        clicked_node = None
        for node_id, node in self.graph_nodes.items():
            if artist == node['patch'] or artist == node['text']:
                clicked_node = node
                break
        
        if clicked_node:
            # Highlight clicked node
            self._highlight_node(clicked_node)
            
            # Update details panel
            self._update_node_details(clicked_node)
            
            # Also update details in main GUI
            self._update_main_gui_details(clicked_node)
    
    def _highlight_node(self, node):
        """Highlight the clicked node"""
        # Reset all nodes to original colors
        for n in self.graph_nodes.values():
            n['patch'].set_edgecolor(n['border_color'])
            n['patch'].set_linewidth(2)
            if n.get('is_root', False):
                n['patch'].set_linewidth(3)  # Root keeps thicker border
        
        # Highlight clicked node
        node['patch'].set_edgecolor('#000000')  # Black border
        node['patch'].set_linewidth(3)
        
        # Add glow effect
        node['patch'].set_path_effects([
            patheffects.withStroke(linewidth=5, foreground='yellow', alpha=0.3)
        ])
        
        self.current_graph_canvas.draw()
    
    def _update_node_details(self, node):
        """Update the details panel in the graph window"""
        # Clear previous details
        if hasattr(self, 'details_text'):
            self.details_text.remove()
        
        # Create detailed information
        details = f"Marking M{node['node_number']}:\n"
        details += "=" * 30 + "\n"
        
        # Add full marking
        details += node['full_marking'] + "\n\n"
        
        # Add properties
        petri_node = node['node']
        details += "Properties:\n"
        details += "-" * 20 + "\n"
        
        if node['id'] == id(self.algorithm.root):
            details += "• Root node (initial marking)\n"
        
        if any(isinstance(v, Omega) for v in petri_node.values):
            details += "• Contains ω (unbounded)\n"
        
        if not petri_node.children:
            details += "• Dead-end (no outgoing transitions)\n"
        
        # Calculate max depth
        max_depth = max([n['depth'] for n in self.graph_nodes.values()])
        if node['depth'] == max_depth:
            details += "• Maximum depth node\n"
        
        if node['parent']:
            parent_num = self.graph_nodes[node['parent']]['node_number']
            details += f"• Parent: M{parent_num}\n"
        
        if node['incoming_transition']:
            details += f"• Incoming transition: {node['incoming_transition']}\n"
        
        if petri_node.children:
            details += f"• Children: {len(petri_node.children)} transition(s)\n"
            for t, child in petri_node.children.items():
                child_id = id(child)
                if child_id in self.graph_nodes:
                    child_num = self.graph_nodes[child_id]['node_number']
                    details += f"  - {t} → M{child_num}\n"
        
        # Update details panel
        self.details_text = self.current_graph_ax.figure.axes[1].text(
            0.5, 0.5, details,
            transform=self.current_graph_ax.figure.axes[1].transAxes,
            fontsize=10,
            ha='center', va='center',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8)
        )
        
        self.current_graph_canvas.draw()
    
    def _update_main_gui_details(self, node):
        """Update node details in the main GUI"""
        self.node_details_display.delete("1.0", tk.END)
        
        details = "=" * 60 + "\n"
        details += f"NODE DETAILS: Marking M{node['node_number']}\n"
        details += "=" * 60 + "\n\n"
        
        # Full marking
        details += "FULL MARKING:\n"
        details += "-" * 40 + "\n"
        details += node['full_marking'] + "\n\n"
        
        # Properties
        details += "PROPERTIES:\n"
        details += "-" * 40 + "\n"
        
        petri_node = node['node']
        
        if node['id'] == id(self.algorithm.root):
            details += "• Type: Root node (initial marking)\n"
        elif any(isinstance(v, Omega) for v in petri_node.values):
            details += "• Type: Contains ω (unbounded)\n"
        elif not petri_node.children:
            details += "• Type: Dead-end node\n"
        else:
            details += "• Type: Regular node\n"
        
        details += f"• Depth from root: {node['depth']}\n"
        details += f"• Node tag: {petri_node.tag if petri_node.tag else 'none'}\n"
        
        if node['parent']:
            parent_num = self.graph_nodes[node['parent']]['node_number']
            details += f"• Parent node: M{parent_num}\n"
        
        if node['incoming_transition']:
            details += f"• Reached via transition: {node['incoming_transition']}\n"
        
        if petri_node.children:
            details += f"• Outgoing transitions: {len(petri_node.children)}\n"
            for t, child in petri_node.children.items():
                child_id = id(child)
                if child_id in self.graph_nodes:
                    child_num = self.graph_nodes[child_id]['node_number']
                    details += f"  - {t} → M{child_num}\n"
        else:
            details += "• Outgoing transitions: None (terminal node)\n"
        
        self.node_details_display.insert("1.0", details)
        
        # Switch to text output tab to show details
        self.notebook.select(1)  # Index 1 is the text output tab

    # --------------------------- Analyze Properties ---------------------------
    def _analyze_properties(self):
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

    # --------------------------- Clear All ---------------------------
    def _clear_all(self):
        """Clear all inputs and outputs"""
        self.tree_display.delete("1.0", tk.END)
        self.properties_display.delete("1.0", tk.END)
        self.node_details_display.delete("1.0", tk.END)
        self.places_entry.delete(0, tk.END)
        self.marking_entry.delete(0, tk.END)
        self.transitions_text.delete("1.0", tk.END)
        
        # Reset to default example
        self.places_entry.insert(0, "P0,P1,P2")
        self.marking_entry.insert(0, "P0=1,P2=1")
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
        
        self.petri_net = None
        self.algorithm = None
        self.status_bar.config(text="Cleared - Example restored")
        
        # Close graph window if open
        if self.current_graph_window:
            try:
                self.current_graph_window.destroy()
                self.current_graph_window = None
            except:
                pass

    def run(self):
        self.root.mainloop()


def main():
    app = PetriNetGUI()
    app.run()


if __name__ == "__main__":
    main()