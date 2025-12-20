##  **How Classes Interact - Step by Step**

### **1. Starting Point: User Input** → **PetriNetGUI**
```python
# User enters in GUI:
# Places: "P0,P1,P2"
# Initial Marking: "P0=1,P2=1"
# Transitions: JSON format

# GUI creates PetriNet object
petri_net = PetriNet()
petri_net.add_place("P0")  # Adds places
petri_net.add_place("P1")
petri_net.add_place("P2")
```

### **2. Building the Model: PetriNet + Transition + Marking**
```python
# PetriNet stores:
# - List of places: ["P0", "P1", "P2"]
# - List of Transition objects
# - Initial Marking object

# Transition example:
transition = Transition("t1", {"P0": 1}, {"P1": 1})
# This means: "Take 1 token from P0, give 1 token to P1"

# Initial Marking:
marking = Marking(["P0", "P1", "P2"], [1, 0, 1])
# This means: P0 has 1 token, P1 has 0, P2 has 1
```

### **3. Running the Algorithm: KarpMillerAlgorithm Orchestrates**
```python
# Step-by-step what happens:

# 1. Algorithm starts with initial marking
algorithm = KarpMillerAlgorithm(petri_net)
root = algorithm.run()  # Begin!

# 2. Check enabled transitions
for transition in petri_net.transitions:
    if transition.is_enabled(marking):  # ← Transition checks Marking
        # t1 is enabled because P0 has ≥1 token
        
# 3. Fire transition
new_marking = transition.fire(marking)  # ← Transition modifies Marking
# Result: P0=0, P1=1, P2=1

# 4. Check for ω substitution
# If new marking "covers" ancestor marking:
# Example: [1,0,2] covers [1,0,1] (third component is larger)
# Then replace larger components with ω
# [1,0,2] becomes [1,0,ω]

# 5. Create tree structure
marking.children["t1"] = new_marking  # ← Marking stores its children
```

### **4. Omega (ω) - The "Infinity" Symbol**
```python
# Special properties:
omega = Omega()
print(omega > 1000000)  # True - ω is greater than any number
print(omega + 5)       # ω - ω plus anything is ω
print(omega - 3)       # ω - ω minus anything is ω

# Used when:
# New marking M' = [1,0,3]
# Ancestor marking M'' = [1,0,1]
# Since 3 > 1, replace 3 with ω: [1,0,ω]
```

##  **Complete Workflow Example**

Let's trace through a simple example:

### **Step 1: Setup**
```python
# User defines:
# Places: A,B
# Initial: A=1
# Transition: t1: A→B (takes from A, gives to B)

petri_net = PetriNet()
petri_net.add_places(["A", "B"])
petri_net.set_initial_marking({"A": 1})
petri_net.add_transition("t1", {"A": 1}, {"B": 1})
```

### **Step 2: Initial State**
```
Initial Marking: [A=1, B=0]  ← Stored as Marking object
Tag: "new"                    ← Ready to be processed
```

### **Step 3: Process Marking**
```python
# KarpMillerAlgorithm finds the "new" marking
# Checks enabled transitions:
t1.is_enabled([A=1, B=0])  # Returns True

# Fires t1:
new_marking = t1.fire([A=1, B=0])  # Returns [A=0, B=1]

# Add to tree:
initial.children["t1"] = new_marking
```

### **Step 4: Tree Grows**
```
Root: [A=1, B=0]
      |
      --t1-->
          [A=0, B=1]
```

### **Step 5: Algorithm Continues**
The algorithm repeats for each "new" marking until all are processed as "old" or "dead-end."

##  **Visual Representation of Interactions**

### **Data Flow:**
```
User Input 
    ↓
PetriNetGUI (Collects input)
    ↓
Creates → PetriNet (Model)
    ↓           ↓
    ↓       Transition objects
    ↓           ↓
    ↓       Marking objects
    ↓           ↓
KarpMillerAlgorithm (Processor)
    ↓
Analyzes → Omega substitutions
    ↓
Builds → Tree Structure
    ↓
PetriNetGUI (Displays results)
```

### **Method Calls Sequence:**
```
1. GUI.create_petri_net()
   │
   ├── PetriNet.add_place()
   ├── PetriNet.add_transition()
   └── PetriNet.set_initial_marking()
   
2. GUI.run_algorithm()
   │
   ├── KarpMillerAlgorithm.run()
   │   │
   │   ├── algorithm._find_new_marking()
   │   ├── transition.is_enabled(marking)
   │   ├── transition.fire(marking)
   │   ├── algorithm._covers(new, ancestor)
   │   │   ├── Omega() created if needed
   │   │   └── marking.values updated
   │   └── marking.children[trans_name] = new_marking
   │
   └── GUI._display_tree()
```

##  **Real Example Walkthrough**

### **Scenario: Unbounded Net**
```
Places: P0, P1, P2
Initial: P0=1, P2=1
t1: P0→P1  (1 token)
t2: P1→P0+P2  (creates extra token in P2)
```

### **What happens:**
```
Step 0: [P0=1, P1=0, P2=1]
        ↓ t1
Step 1: [P0=0, P1=1, P2=1]
        ↓ t2
Step 2: [P0=1, P1=0, P2=2]  ← P2 increased!
        ↓ t1
Step 3: [P0=0, P1=1, P2=2]
        ↓ t2
Step 4: [P0=1, P1=0, P2=3]  ← P2 increased again!
        
# Step 4 covers Step 2 (3 > 2 in P2)
# So algorithm replaces with ω:
Step 4 becomes: [P0=1, P1=0, P2=ω]
```

### **Tree Visualization:**
```
[P0=1, P1=0, P2=1]
  |
  --t1-->
  [P0=0, P1=1, P2=1]
    |
    --t2-->
    [P0=1, P1=0, P2=2]  ← Ancestor for comparison
      |
      --t1-->
      [P0=0, P1=1, P2=2]
        |
        --t2-->
        [P0=1, P1=0, P2=ω]  ← ω appears here!


This architecture makes the complex Karp-Miller algorithm accessible and maintainable!

