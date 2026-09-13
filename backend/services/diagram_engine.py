# -*- coding: utf-8 -*-
"""
Diagram Engine for OmniLearn
Generates responsive, textbook-grade vector diagrams (SVG) and dynamic
Mermaid.js architectural representations for academic subjects.
"""

from typing import Dict, Any, List, Optional

class DiagramEngine:
    @staticmethod
    def build_diagram(topic_query: str, topic_title: str, domain: str) -> Dict[str, Any]:
        """Synthesizes a responsive, interactive architectural diagram for the requested topic."""
        t_low = (topic_query or "").strip().lower()
        title = topic_title or topic_query.title()

        # 1. Binary Tree & Tree Data Structures
        if any(k in t_low for k in ["binary tree", "bst", "binary search tree", "avl", "red black", "tree traversal", "b tree", "b+ tree", "tree", "trie"]):
            return {
                "title": f"{title}: Hierarchical Node Topology & Recursive Subtrees",
                "subtitle": "Level-by-level binary branching with BST invariants and O(log n) search height",
                "badge": "Data Structures",
                "type": "svg",
                "svg_content": DiagramEngine._binary_tree_svg(),
                "mermaid_code": (
                    "graph TD\n"
                    "  Root((50<br/>Root)) -->|left <| L30((30))\n"
                    "  Root -->|right >| R70((70))\n"
                    "  L30 --> L20((20<br/>Leaf))\n"
                    "  L30 --> R40((40<br/>Leaf))\n"
                    "  R70 --> L60((60<br/>Leaf))\n"
                    "  R70 --> R80((80<br/>Leaf))\n"
                    "  style Root fill:#6366f1,stroke:#a5b4fc,stroke-width:2px,color:#fff\n"
                    "  style L30 fill:#0284c7,stroke:#bae6fd,stroke-width:2px,color:#fff\n"
                    "  style R70 fill:#0284c7,stroke:#bae6fd,stroke-width:2px,color:#fff\n"
                    "  style L20 fill:#10b981,stroke:#a7f3d0,stroke-width:2px,color:#fff\n"
                    "  style R40 fill:#10b981,stroke:#a7f3d0,stroke-width:2px,color:#fff\n"
                    "  style L60 fill:#10b981,stroke:#a7f3d0,stroke-width:2px,color:#fff\n"
                    "  style R80 fill:#10b981,stroke:#a7f3d0,stroke-width:2px,color:#fff"
                ),
                "explanation": "Every node contains at most two children. The binary search tree invariant guarantees that all left descendant keys are smaller and all right descendant keys are larger, providing guaranteed O(log n) search time in balanced trees.",
                "legend": [
                    {"color": "#6366f1", "label": "Root Node (Origin / Level 0)"},
                    {"color": "#0284c7", "label": "Internal Subtree Roots (Level 1)"},
                    {"color": "#10b981", "label": "Leaf Nodes (Base Cases / Level 2)"},
                    {"color": "#818cf8", "label": "Directed Edges (Left <, Right >)"}
                ]
            }

        # 2. Contiguous Arrays & Memory Layout
        if any(k in t_low for k in ["array", "contiguous", "vector", "dynamic array", "matrix", "buffer"]):
            return {
                "title": f"{title}: Contiguous Memory Allocation & O(1) Random Access",
                "subtitle": "Direct pointer arithmetic offset: Address(A[i]) = Base + (i × sizeof(T))",
                "badge": "Memory Architecture",
                "type": "svg",
                "svg_content": DiagramEngine._array_svg(),
                "mermaid_code": (
                    "graph LR\n"
                    "  subgraph Array_Memory [Base Address: 0x1000]\n"
                    "    A0[\"Index [0]<br/>Value: 12<br/>@ 0x1000\"]\n"
                    "    A1[\"Index [1]<br/>Value: 99<br/>@ 0x1004\"]\n"
                    "    A2[\"Index [2] ★<br/>Value: 37<br/>@ 0x1008\"]\n"
                    "    A3[\"Index [3]<br/>Value: 45<br/>@ 0x100C\"]\n"
                    "    A4[\"Index [4]<br/>Value: 88<br/>@ 0x1010\"]\n"
                    "  end\n"
                    "  A0 --> A1 --> A2 --> A3 --> A4\n"
                    "  style A2 fill:#10b981,stroke:#6ee7b7,stroke-width:3px,color:#fff"
                ),
                "explanation": "Arrays store homogeneous elements in strictly adjacent physical memory addresses. Because element sizes are uniform, the CPU hardware calculates any index address instantly via base-pointer arithmetic in O(1) time.",
                "legend": [
                    {"color": "#3b82f6", "label": "Contiguous Memory Slots"},
                    {"color": "#10b981", "label": "Active O(1) Direct Indexed Slot"},
                    {"color": "#60a5fa", "label": "Zero-Based Index (0..n-1)"},
                    {"color": "#94a3b8", "label": "Physical Byte Addresses"}
                ]
            }

        # 3. Singly & Doubly Linked Lists
        if any(k in t_low for k in ["linked list", "singly linked", "doubly linked", "circular linked", "pointer"]):
            return {
                "title": f"{title}: Discontiguous Node Topology & Pointer Chaining",
                "subtitle": "Dynamic heap node linking with Head reference and terminal NULL pointer",
                "badge": "Data Structures",
                "type": "svg",
                "svg_content": DiagramEngine._linked_list_svg(),
                "mermaid_code": (
                    "graph LR\n"
                    "  HEAD[HEAD] --> N1\n"
                    "  subgraph N1 [Node 1 @ 0x1A40]\n"
                    "    D1[Data: 15] --- P1[Next]\n"
                    "  end\n"
                    "  P1 --> N2\n"
                    "  subgraph N2 [Node 2 @ 0x3C80]\n"
                    "    D2[Data: 42] --- P2[Next]\n"
                    "  end\n"
                    "  P2 --> N3\n"
                    "  subgraph N3 [Node 3 @ 0x9F10]\n"
                    "    D3[Data: 89] --- P3[Next]\n"
                    "  end\n"
                    "  P3 --> NULL[NULL / Ø]\n"
                    "  style HEAD fill:#f59e0b,stroke:#fcd34d,color:#fff\n"
                    "  style NULL fill:#ef4444,stroke:#fca5a5,color:#fff"
                ),
                "explanation": "Nodes are individually allocated across non-contiguous heap memory, each holding a data payload and a pointer to the subsequent node. Insertions and deletions execute in O(1) time once the position is located.",
                "legend": [
                    {"color": "#f59e0b", "label": "Head Pointer (Entry Reference)"},
                    {"color": "#0284c7", "label": "Data Payload Field"},
                    {"color": "#6366f1", "label": "Next Pointer Reference"},
                    {"color": "#f87171", "label": "Terminal NULL Indicator"}
                ]
            }

        # 4. Stack (LIFO)
        if any(k in t_low for k in ["stack", "lifo", "call stack", "push pop"]):
            return {
                "title": f"{title}: Last-In, First-Out (LIFO) Execution Model",
                "subtitle": "Push and Pop operations restricted strictly to the Top of Stack in O(1) time",
                "badge": "Abstract Data Type",
                "type": "svg",
                "svg_content": DiagramEngine._stack_svg(),
                "mermaid_code": (
                    "graph TD\n"
                    "  PUSH[\"↓ Push(x)\"] --> TOP\n"
                    "  TOP[\"Element 4 (TOP) ★\"] -->|Pop() ↑| OUT[\"Return x\"]\n"
                    "  TOP --> E3[\"Element 3\"]\n"
                    "  E3 --> E2[\"Element 2\"]\n"
                    "  E2 --> E1[\"Element 1 (Bottom / Base)\"]\n"
                    "  style TOP fill:#ec4899,stroke:#fbcfe8,stroke-width:2px,color:#fff\n"
                    "  style E1 fill:#6d28d9,stroke:#c4b5fd,color:#fff"
                ),
                "explanation": "A stack enforces strict LIFO access. The most recently inserted element is always the first to be retrieved, serving as the fundamental engine for function recursion call frames, undo buffers, and syntax parsing.",
                "legend": [
                    {"color": "#ec4899", "label": "Top of Stack (Active Frame)"},
                    {"color": "#8b5cf6", "label": "Stacked Elements"},
                    {"color": "#34d399", "label": "Push Operation (Insert)"},
                    {"color": "#f472b6", "label": "Pop Operation (Remove)"}
                ]
            }

        # 5. Queue (FIFO)
        if any(k in t_low for k in ["queue", "fifo", "priority queue", "deque", "circular queue"]):
            return {
                "title": f"{title}: First-In, First-Out (FIFO) Pipeline Architecture",
                "subtitle": "Dual-pointer stream: Enqueue at Rear and Dequeue at Front with O(1) guarantees",
                "badge": "Abstract Data Type",
                "type": "svg",
                "svg_content": DiagramEngine._queue_svg(),
                "mermaid_code": (
                    "graph LR\n"
                    "  IN[\"Enqueue &rarr;\"] --> REAR[\"Rear: Data 4\"]\n"
                    "  REAR --> D3[\"Data 3\"]\n"
                    "  D3 --> D2[\"Data 2\"]\n"
                    "  D2 --> FRONT[\"Front: Data 1\"]\n"
                    "  FRONT --> OUT[\"&rarr; Dequeue\"]\n"
                    "  style REAR fill:#f59e0b,stroke:#fcd34d,color:#fff\n"
                    "  style FRONT fill:#10b981,stroke:#a7f3d0,stroke-width:2px,color:#fff"
                ),
                "explanation": "Queues maintain order of arrival. Elements enter at the Rear and exit from the Front, powering CPU task scheduling, print spoolers, BFS graph traversals, and asynchronous message brokers.",
                "legend": [
                    {"color": "#f59e0b", "label": "Rear Pointer (Enqueue Ingestion)"},
                    {"color": "#10b981", "label": "Front Pointer (Dequeue Ejection)"},
                    {"color": "#0284c7", "label": "In-Flight Data Elements"},
                    {"color": "#38bdf8", "label": "Direction of Flow (FIFO)"}
                ]
            }

        # 6. Hash Table & Hashing
        if any(k in t_low for k in ["hash table", "hash map", "hashmap", "hashing", "hash function", "collision"]):
            return {
                "title": f"{title}: Hash Mapping & Separate Chaining Collision Resolution",
                "subtitle": "Deterministic key-to-index mapping with O(1) average lookup performance",
                "badge": "Data Structures",
                "type": "svg",
                "svg_content": DiagramEngine._hash_table_svg(),
                "mermaid_code": (
                    "graph LR\n"
                    "  subgraph Keys [Keys]\n"
                    "    K1[\"Alice\"]\n"
                    "    K2[\"Bob\"]\n"
                    "    K3[\"Charlie\"]\n"
                    "  end\n"
                    "  HF[\"Hash Function<br/>h(k) = sum(k) % M\"]\n"
                    "  K1 --> HF\n"
                    "  K2 --> HF\n"
                    "  K3 --> HF\n"
                    "  subgraph Buckets [Bucket Array]\n"
                    "    B0[\"Bucket [0]\"]\n"
                    "    B1[\"Bucket [1]\"]\n"
                    "    B2[\"Bucket [2]\"]\n"
                    "  end\n"
                    "  HF -->|h(Alice)=1| B1\n"
                    "  HF -->|h(Bob)=0| B0\n"
                    "  HF -->|h(Charlie)=1 (Collision)| B1\n"
                    "  B1 --> C1[\"Alice: 95\"] --> C2[\"Charlie: 88\"]\n"
                    "  style HF fill:#8b5cf6,stroke:#c4b5fd,color:#fff\n"
                    "  style B1 fill:#0284c7,stroke:#38bdf8,stroke-width:2px,color:#fff\n"
                    "  style C1 fill:#10b981,stroke:#6ee7b7,color:#fff\n"
                    "  style C2 fill:#10b981,stroke:#6ee7b7,color:#fff"
                ),
                "explanation": "Keys are passed through a hash function that calculates an array index. When distinct keys produce identical hash indices (a collision), separate chaining links them sequentially, preserving O(1) average access.",
                "legend": [
                    {"color": "#3b82f6", "label": "Input Key Payloads"},
                    {"color": "#8b5cf6", "label": "Deterministic Hash Function"},
                    {"color": "#0284c7", "label": "Fixed Bucket Array"},
                    {"color": "#10b981", "label": "Chained Linked List (Collisions)"}
                ]
            }

        # 7. Graphs & Shortest Path (Dijkstra / Bellman-Ford)
        if any(k in t_low for k in ["graph", "dijkstra", "bellman ford", "floyd warshall", "shortest path", "dfs", "spanning tree", "kruskal", "prim"]):
            return {
                "title": f"{title}: Weighted Directed Graph & Shortest Path Tree",
                "subtitle": "Greedy relaxation finding minimum-cost paths from source to destination",
                "badge": "Graph Theory & Algorithms",
                "type": "svg",
                "svg_content": DiagramEngine._graph_svg(),
                "mermaid_code": (
                    "graph LR\n"
                    "  A((A<br/>Start: 0)) -->|wt: 4| B((B))\n"
                    "  A ==>|wt: 2| C((C<br/>dist: 2))\n"
                    "  C ==>|wt: 1| D((D<br/>dist: 3))\n"
                    "  B -->|wt: 5| D\n"
                    "  C -->|wt: 7| E((E<br/>Dest))\n"
                    "  D ==>|wt: 3| E\n"
                    "  style A fill:#10b981,stroke:#a7f3d0,stroke-width:3px,color:#fff\n"
                    "  style C fill:#6366f1,stroke:#a5b4fc,stroke-width:2px,color:#fff\n"
                    "  style D fill:#6366f1,stroke:#a5b4fc,stroke-width:2px,color:#fff\n"
                    "  style E fill:#f59e0b,stroke:#fcd34d,stroke-width:3px,color:#fff\n"
                    "  linkStyle 1,2,5 stroke:#10b981,stroke-width:3.5px;"
                ),
                "explanation": "Graphs model networks of vertices connected by weighted edges. Shortest path algorithms iteratively relax edge distances, discovering the optimal global route with minimum cumulative weight.",
                "legend": [
                    {"color": "#10b981", "label": "Source Vertex & Shortest Path"},
                    {"color": "#f59e0b", "label": "Target / Destination Vertex"},
                    {"color": "#6366f1", "label": "Intermediate Network Vertices"},
                    {"color": "#94a3b8", "label": "Alternate Weighted Edges"}
                ]
            }

        # 8. Operating System & Process State Machine
        if any(k in t_low for k in ["operating system", "os", "process", "thread", "process scheduling", "deadlock", "virtual memory", "paging", "concurrency", "cpu scheduling"]):
            return {
                "title": f"{title}: 5-State Process Lifecycle & Kernel Dispatch",
                "subtitle": "State transitions managed by the kernel scheduler and Process Control Block (PCB)",
                "badge": "Systems & OS",
                "type": "svg",
                "svg_content": DiagramEngine._os_svg(),
                "mermaid_code": (
                    "stateDiagram-v2\n"
                    "  [*] --> New: Process Creation\n"
                    "  New --> Ready: Admitted\n"
                    "  Ready --> Running: Scheduler Dispatch\n"
                    "  Running --> Ready: Interrupt / Time Slice\n"
                    "  Running --> Waiting: I/O or Event Wait\n"
                    "  Waiting --> Ready: I/O Completion\n"
                    "  Running --> Terminated: Exit\n"
                    "  Terminated --> [*]"
                ),
                "explanation": "Operating systems manage program execution through distinct lifecycle states. The CPU scheduler switches processes between Ready and Running states using time slices, moving blocked processes to Waiting until I/O events resolve.",
                "legend": [
                    {"color": "#3b82f6", "label": "Initial & Terminal States (New, Terminated)"},
                    {"color": "#10b981", "label": "Active CPU Execution (Running)"},
                    {"color": "#f59e0b", "label": "Blocked / Waiting (I/O Bound)"},
                    {"color": "#60a5fa", "label": "Scheduler & Interrupt Transitions"}
                ]
            }

        # 9. Computer Networks & OSI / TCP-IP Model
        if any(k in t_low for k in ["computer networks", "networking", "osi", "osi model", "tcp", "ip", "udp", "http", "routing", "ethernet"]):
            return {
                "title": f"{title}: Layered Protocol Architecture & Encapsulation Stack",
                "subtitle": "End-to-end data packet encapsulation from Application layer to Physical bitstream",
                "badge": "Computer Networks",
                "type": "svg",
                "svg_content": DiagramEngine._osi_svg(),
                "mermaid_code": (
                    "graph TD\n"
                    "  L7[\"Layer 7: Application (HTTP, DNS, SSH) • Data\"]\n"
                    "  L4[\"Layer 4: Transport (TCP, UDP) • Segments + Ports\"]\n"
                    "  L3[\"Layer 3: Network (IP, ICMP) • Packets + IP Addresses\"]\n"
                    "  L2[\"Layer 2: Data Link (Ethernet, Wi-Fi) • Frames + MACs\"]\n"
                    "  L1[\"Layer 1: Physical (Fiber, Copper, Radio) • Bitstream\"]\n"
                    "  L7 -->|Encapsulate Header| L4\n"
                    "  L4 -->|Add IP Header| L3\n"
                    "  L3 -->|Add MAC Header/Trailer| L2\n"
                    "  L2 -->|Modulate Signals| L1\n"
                    "  style L7 fill:#8b5cf6,stroke:#c4b5fd,color:#fff\n"
                    "  style L4 fill:#3b82f6,stroke:#93c5fd,color:#fff\n"
                    "  style L3 fill:#0284c7,stroke:#7dd3fc,color:#fff\n"
                    "  style L2 fill:#10b981,stroke:#6ee7b7,color:#fff\n"
                    "  style L1 fill:#f59e0b,stroke:#fcd34d,color:#fff"
                ),
                "explanation": "Network communications rely on modular layers. As payload data travels down the stack, each layer encapsulates the packet by prepending its own protocol header containing addressing, sequence numbers, and error-check codes.",
                "legend": [
                    {"color": "#8b5cf6", "label": "Application Layer (End-User Software)"},
                    {"color": "#3b82f6", "label": "Transport Layer (End-to-End Reliability)"},
                    {"color": "#0284c7", "label": "Network Layer (Logical Routing & IP)"},
                    {"color": "#10b981", "label": "Data Link Layer (Hop-to-Hop MAC Framing)"}
                ]
            }

        # 10. Physics & Mechanics (Newton's Laws, Force Vectors)
        if any(k in t_low for k in ["physics", "newton", "force", "motion", "gravity", "kinematics", "dynamics", "friction", "mechanics"]):
            return {
                "title": f"{title}: Free Body Diagram & Vector Force Equilibrium",
                "subtitle": "Newton's Second Law: Vector sum of applied, normal, frictional, and gravitational forces",
                "badge": "Classical Mechanics",
                "type": "svg",
                "svg_content": DiagramEngine._physics_svg(),
                "mermaid_code": (
                    "graph TD\n"
                    "  FN[\"F_N (Normal Force) ↑\"]\n"
                    "  FG[\"F_g = mg (Gravity) ↓\"]\n"
                    "  FA[\"F_applied →\"]\n"
                    "  FK[\"f_k = μ_k F_N (Friction) ←\"]\n"
                    "  M((\"Mass (m)\"))\n"
                    "  M --- FN\n"
                    "  M --- FG\n"
                    "  M --- FA\n"
                    "  M --- FK\n"
                    "  style M fill:#3b82f6,stroke:#93c5fd,stroke-width:2px,color:#fff\n"
                    "  style FN fill:#10b981,stroke:#a7f3d0,color:#fff\n"
                    "  style FG fill:#ef4444,stroke:#fca5a5,color:#fff\n"
                    "  style FA fill:#0284c7,stroke:#bae6fd,color:#fff\n"
                    "  style FK fill:#f59e0b,stroke:#fcd34d,color:#fff"
                ),
                "explanation": "Free body diagrams isolate all vector forces acting upon a physical system. The net unbalanced force determines acceleration according to F_net = m × a, establishing dynamical equilibrium.",
                "legend": [
                    {"color": "#3b82f6", "label": "Physical Inertial Body (Mass m)"},
                    {"color": "#34d399", "label": "Normal Support Force (Perpendicular)"},
                    {"color": "#f87171", "label": "Gravitational Downward Force (Weight)"},
                    {"color": "#38bdf8", "label": "Applied Dynamic Force Vector"}
                ]
            }

        # 11. Mathematics & Calculus (Definite Integrals & Curves)
        if any(k in t_low for k in ["math", "calculus", "derivative", "integral", "integration", "differential equation", "riemann"]):
            return {
                "title": f"{title}: Geometric Interpretation of the Definite Integral",
                "subtitle": "Accumulated area under curve y = f(x) over interval [a, b] via Riemann summation",
                "badge": "Mathematical Analysis",
                "type": "svg",
                "svg_content": DiagramEngine._calculus_svg(),
                "mermaid_code": (
                    "graph LR\n"
                    "  A[\"Lower Bound: x = a\"] --> INT[\"Definite Integral<br/>∫_a^b f(x) dx\"]\n"
                    "  B[\"Upper Bound: x = b\"] --> INT\n"
                    "  FUNC[\"Function Curve y = f(x)\"] --> INT\n"
                    "  INT --> RES[\"Net Accumulation<br/>F(b) - F(a)\"]\n"
                    "  style INT fill:#3b82f6,stroke:#93c5fd,stroke-width:2px,color:#fff\n"
                    "  style RES fill:#10b981,stroke:#a7f3d0,stroke-width:2px,color:#fff"
                ),
                "explanation": "Integration calculates continuous accumulation. The definite integral calculates the exact area bounded between the function curve f(x) and the x-axis across interval [a, b], established by the Fundamental Theorem of Calculus.",
                "legend": [
                    {"color": "#38bdf8", "label": "Continuous Function Curve y = f(x)"},
                    {"color": "#3b82f6", "label": "Definite Integral Accumulated Area"},
                    {"color": "#818cf8", "label": "Interval Boundaries (a, b)"},
                    {"color": "#34d399", "label": "Infinitesimal Slice (f(x) dx)"}
                ]
            }

        # 12. Smart Universal Academic Diagram Fallback (Works for ANY unseen topic)
        return {
            "title": f"{title}: Architectural System Model & Functional Workflow",
            "subtitle": f"High-level operational pipeline, governing transformations, and verified outputs in {domain}",
            "badge": domain or "Academic Intelligence",
            "type": "svg",
            "svg_content": DiagramEngine._universal_svg(),
            "mermaid_code": (
                "graph LR\n"
                f"  IN[\"Input / Parameters<br/>Initial State S₀\"] --> PROC[\"{title}<br/>Core Mechanism & Rules\"]\n"
                "  PROC --> OUT[\"Validated Result<br/>Optimal Output / Application\"]\n"
                "  OUT -.->|Feedback Loop / Verification| IN\n"
                "  style IN fill:#3b82f6,stroke:#93c5fd,color:#fff\n"
                "  style PROC fill:#8b5cf6,stroke:#c4b5fd,stroke-width:2px,color:#fff\n"
                "  style OUT fill:#10b981,stroke:#a7f3d0,color:#fff"
            ),
            "explanation": f"This architectural model illustrates the foundational workflow for {title}. Input states are processed according to domain-governing rules and constraints, producing validated deterministic outcomes with continuous feedback validation.",
            "legend": [
                {"color": "#3b82f6", "label": "Input Parameters / Initial State"},
                {"color": "#8b5cf6", "label": "Core Algorithmic / Physical Mechanism"},
                {"color": "#10b981", "label": "Validated Output / Verified State"},
                {"color": "#60a5fa", "label": "Convergence / Feedback Loop"}
            ]
        }

    # =========================================================================
    # VECTOR SVG GENERATORS (Responsive, pure XML compliant, dark/light ready)
    # =========================================================================

    @staticmethod
    def _binary_tree_svg() -> str:
        return """<svg viewBox="0 0 580 270" class="w-full h-auto max-h-[320px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="treeRoot" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366f1" />
      <stop offset="100%" stop-color="#4338ca" />
    </linearGradient>
    <linearGradient id="treeBranch" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="100%" stop-color="#0369a1" />
    </linearGradient>
    <linearGradient id="treeLeaf" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>
    <filter id="treeGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.25"/>
    </filter>
  </defs>

  <!-- Level Grid Indicators -->
  <line x1="30" y1="46" x2="550" y2="46" stroke="currentColor" stroke-opacity="0.12" stroke-dasharray="4" />
  <text x="35" y="40" fill="currentColor" fill-opacity="0.5" font-size="10" font-weight="700" font-family="system-ui">Level 0 • Height = 2</text>

  <line x1="30" y1="126" x2="550" y2="126" stroke="currentColor" stroke-opacity="0.12" stroke-dasharray="4" />
  <text x="35" y="120" fill="currentColor" fill-opacity="0.5" font-size="10" font-weight="700" font-family="system-ui">Level 1 • Subtrees</text>

  <line x1="30" y1="210" x2="550" y2="210" stroke="currentColor" stroke-opacity="0.12" stroke-dasharray="4" />
  <text x="35" y="204" fill="currentColor" fill-opacity="0.5" font-size="10" font-weight="700" font-family="system-ui">Level 2 • Leaf Nodes</text>

  <!-- Connector Edges -->
  <line x1="290" y1="46" x2="180" y2="126" stroke="#818cf8" stroke-width="2.5" stroke-linecap="round" />
  <rect x="210" y="74" width="46" height="18" rx="4" fill="#1e1b4b" fill-opacity="0.85" />
  <text x="233" y="87" text-anchor="middle" fill="#c7d2fe" font-size="10" font-weight="700" font-family="monospace">left &lt;</text>

  <line x1="290" y1="46" x2="400" y2="126" stroke="#818cf8" stroke-width="2.5" stroke-linecap="round" />
  <rect x="325" y="74" width="46" height="18" rx="4" fill="#1e1b4b" fill-opacity="0.85" />
  <text x="348" y="87" text-anchor="middle" fill="#c7d2fe" font-size="10" font-weight="700" font-family="monospace">&gt; right</text>

  <line x1="180" y1="126" x2="120" y2="210" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" />
  <line x1="180" y1="126" x2="235" y2="210" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" />
  <line x1="400" y1="126" x2="345" y2="210" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" />
  <line x1="400" y1="126" x2="460" y2="210" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" />

  <!-- Root Node -->
  <g filter="url(#treeGlow)">
    <circle cx="290" cy="46" r="23" fill="url(#treeRoot)" stroke="#a5b4fc" stroke-width="2.5" />
    <text x="290" y="51" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="800" font-family="system-ui">50</text>
  </g>
  <text x="290" y="18" text-anchor="middle" fill="#818cf8" font-size="11" font-weight="700" font-family="system-ui">Root (Parent)</text>

  <!-- Level 1 Nodes -->
  <g filter="url(#treeGlow)">
    <circle cx="180" cy="126" r="20" fill="url(#treeBranch)" stroke="#bae6fd" stroke-width="2" />
    <text x="180" y="131" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="system-ui">30</text>
  </g>
  <g filter="url(#treeGlow)">
    <circle cx="400" cy="126" r="20" fill="url(#treeBranch)" stroke="#bae6fd" stroke-width="2" />
    <text x="400" y="131" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="system-ui">70</text>
  </g>

  <!-- Level 2 Leaves -->
  <g filter="url(#treeGlow)">
    <circle cx="120" cy="210" r="18" fill="url(#treeLeaf)" stroke="#a7f3d0" stroke-width="2" />
    <text x="120" y="215" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="700" font-family="system-ui">20</text>
  </g>
  <g filter="url(#treeGlow)">
    <circle cx="235" cy="210" r="18" fill="url(#treeLeaf)" stroke="#a7f3d0" stroke-width="2" />
    <text x="235" y="215" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="700" font-family="system-ui">40</text>
  </g>
  <g filter="url(#treeGlow)">
    <circle cx="345" cy="210" r="18" fill="url(#treeLeaf)" stroke="#a7f3d0" stroke-width="2" />
    <text x="345" y="215" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="700" font-family="system-ui">60</text>
  </g>
  <g filter="url(#treeGlow)">
    <circle cx="460" cy="210" r="18" fill="url(#treeLeaf)" stroke="#a7f3d0" stroke-width="2" />
    <text x="460" y="215" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="700" font-family="system-ui">80</text>
  </g>

  <!-- Invariant Banner -->
  <rect x="140" y="244" width="300" height="22" rx="6" fill="currentColor" fill-opacity="0.08" />
  <text x="290" y="259" text-anchor="middle" fill="currentColor" fill-opacity="0.8" font-size="11" font-weight="600" font-family="system-ui">BST Invariant: Left Subtree &lt; Node &lt; Right Subtree</text>
</svg>"""

    @staticmethod
    def _array_svg() -> str:
        return """<svg viewBox="0 0 580 240" class="w-full h-auto max-h-[300px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cellGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#1d4ed8" />
    </linearGradient>
    <linearGradient id="activeCellGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>
    <filter id="boxShadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="4" stdDeviation="3" flood-opacity="0.2"/>
    </filter>
  </defs>

  <text x="40" y="32" fill="currentColor" fill-opacity="0.6" font-size="11" font-weight="700" font-family="monospace">Base Address: 0x1000 | Type: int32 (4 bytes / slot)</text>

  <g transform="translate(40, 50)" filter="url(#boxShadow)">
    <g transform="translate(0, 0)">
      <rect width="90" height="70" rx="8" fill="url(#cellGrad)" stroke="#93c5fd" stroke-width="2" />
      <text x="45" y="42" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="800" font-family="system-ui">12</text>
      <text x="45" y="92" text-anchor="middle" fill="#60a5fa" font-size="12" font-weight="700" font-family="monospace">Index [0]</text>
      <text x="45" y="112" text-anchor="middle" fill="currentColor" fill-opacity="0.5" font-size="10" font-family="monospace">0x1000</text>
    </g>
    <g transform="translate(100, 0)">
      <rect width="90" height="70" rx="8" fill="url(#cellGrad)" stroke="#93c5fd" stroke-width="2" />
      <text x="45" y="42" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="800" font-family="system-ui">99</text>
      <text x="45" y="92" text-anchor="middle" fill="#60a5fa" font-size="12" font-weight="700" font-family="monospace">Index [1]</text>
      <text x="45" y="112" text-anchor="middle" fill="currentColor" fill-opacity="0.5" font-size="10" font-family="monospace">0x1004</text>
    </g>
    <g transform="translate(200, 0)">
      <rect width="90" height="70" rx="8" fill="url(#activeCellGrad)" stroke="#6ee7b7" stroke-width="2.5" />
      <text x="45" y="42" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="800" font-family="system-ui">37</text>
      <text x="45" y="92" text-anchor="middle" fill="#34d399" font-size="12" font-weight="800" font-family="monospace">Index [2]</text>
      <text x="45" y="112" text-anchor="middle" fill="#34d399" font-size="10" font-weight="700" font-family="monospace">0x1008</text>
    </g>
    <g transform="translate(300, 0)">
      <rect width="90" height="70" rx="8" fill="url(#cellGrad)" stroke="#93c5fd" stroke-width="2" />
      <text x="45" y="42" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="800" font-family="system-ui">45</text>
      <text x="45" y="92" text-anchor="middle" fill="#60a5fa" font-size="12" font-weight="700" font-family="monospace">Index [3]</text>
      <text x="45" y="112" text-anchor="middle" fill="currentColor" fill-opacity="0.5" font-size="10" font-family="monospace">0x100C</text>
    </g>
    <g transform="translate(400, 0)">
      <rect width="90" height="70" rx="8" fill="url(#cellGrad)" stroke="#93c5fd" stroke-width="2" />
      <text x="45" y="42" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="800" font-family="system-ui">88</text>
      <text x="45" y="92" text-anchor="middle" fill="#60a5fa" font-size="12" font-weight="700" font-family="monospace">Index [4]</text>
      <text x="45" y="112" text-anchor="middle" fill="currentColor" fill-opacity="0.5" font-size="10" font-family="monospace">0x1010</text>
    </g>
  </g>

  <g transform="translate(35, 178)">
    <rect width="510" height="50" rx="10" fill="currentColor" fill-opacity="0.07" stroke="currentColor" stroke-opacity="0.15" />
    <text x="255" y="21" text-anchor="middle" fill="currentColor" fill-opacity="0.95" font-size="12" font-weight="700" font-family="monospace">Address(A[i]) = Base + (i × sizeof(elem))</text>
    <text x="255" y="38" text-anchor="middle" fill="#10b981" font-size="11" font-weight="700" font-family="system-ui, -apple-system, sans-serif">Direct Pointer Offset ➔ O(1) Constant Random Access</text>
  </g>
</svg>"""

    @staticmethod
    def _linked_list_svg() -> str:
        return """<svg viewBox="0 0 600 240" class="w-full h-auto max-h-[300px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="llData" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="100%" stop-color="#0369a1" />
    </linearGradient>
    <linearGradient id="llNext" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366f1" />
      <stop offset="100%" stop-color="#4338ca" />
    </linearGradient>
    <marker id="llArrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#38bdf8" />
    </marker>
    <filter id="nodeShadow" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.25"/>
    </filter>
  </defs>

  <g transform="translate(15, 60)">
    <rect width="55" height="32" rx="6" fill="#f59e0b" />
    <text x="27" y="21" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="800" font-family="system-ui">HEAD</text>
    <line x1="58" y1="16" x2="82" y2="16" stroke="#f59e0b" stroke-width="2.5" marker-end="url(#llArrow)" />
  </g>

  <g transform="translate(90, 45)" filter="url(#nodeShadow)">
    <rect width="60" height="60" rx="6" fill="url(#llData)" stroke="#bae6fd" stroke-width="1.5" />
    <text x="30" y="36" text-anchor="middle" fill="#ffffff" font-size="16" font-weight="800" font-family="system-ui">15</text>
    <text x="30" y="16" text-anchor="middle" fill="#bae6fd" font-size="9" font-weight="700" font-family="system-ui">DATA</text>
    <rect x="60" width="36" height="60" rx="6" fill="url(#llNext)" stroke="#c7d2fe" stroke-width="1.5" />
    <circle cx="78" cy="30" r="5" fill="#a5b4fc" />
    <text x="78" y="16" text-anchor="middle" fill="#c7d2fe" font-size="9" font-weight="700" font-family="system-ui">NEXT</text>
    <line x1="82" y1="30" x2="128" y2="30" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#llArrow)" />
    <text x="48" y="78" text-anchor="middle" fill="currentColor" fill-opacity="0.45" font-size="10" font-family="monospace">@0x1A40</text>
  </g>

  <g transform="translate(230, 45)" filter="url(#nodeShadow)">
    <rect width="60" height="60" rx="6" fill="url(#llData)" stroke="#bae6fd" stroke-width="1.5" />
    <text x="30" y="36" text-anchor="middle" fill="#ffffff" font-size="16" font-weight="800" font-family="system-ui">42</text>
    <text x="30" y="16" text-anchor="middle" fill="#bae6fd" font-size="9" font-weight="700" font-family="system-ui">DATA</text>
    <rect x="60" width="36" height="60" rx="6" fill="url(#llNext)" stroke="#c7d2fe" stroke-width="1.5" />
    <circle cx="78" cy="30" r="5" fill="#a5b4fc" />
    <text x="78" y="16" text-anchor="middle" fill="#c7d2fe" font-size="9" font-weight="700" font-family="system-ui">NEXT</text>
    <line x1="82" y1="30" x2="128" y2="30" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#llArrow)" />
    <text x="48" y="78" text-anchor="middle" fill="currentColor" fill-opacity="0.45" font-size="10" font-family="monospace">@0x3C80</text>
  </g>

  <g transform="translate(370, 45)" filter="url(#nodeShadow)">
    <rect width="60" height="60" rx="6" fill="url(#llData)" stroke="#bae6fd" stroke-width="1.5" />
    <text x="30" y="36" text-anchor="middle" fill="#ffffff" font-size="16" font-weight="800" font-family="system-ui">89</text>
    <text x="30" y="16" text-anchor="middle" fill="#bae6fd" font-size="9" font-weight="700" font-family="system-ui">DATA</text>
    <rect x="60" width="36" height="60" rx="6" fill="url(#llNext)" stroke="#c7d2fe" stroke-width="1.5" />
    <text x="78" y="36" text-anchor="middle" fill="#f87171" font-size="11" font-weight="800" font-family="monospace">Ø</text>
    <text x="78" y="16" text-anchor="middle" fill="#c7d2fe" font-size="9" font-weight="700" font-family="system-ui">NEXT</text>
    <text x="48" y="78" text-anchor="middle" fill="currentColor" fill-opacity="0.45" font-size="10" font-family="monospace">@0x9F10</text>
  </g>

  <g transform="translate(485, 60)">
    <text x="0" y="18" fill="#f87171" font-size="14" font-weight="800" font-family="monospace">NULL</text>
    <text x="0" y="32" fill="currentColor" fill-opacity="0.5" font-size="10" font-family="system-ui">(End of List)</text>
  </g>

  <g transform="translate(40, 165)">
    <rect width="520" height="46" rx="8" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.15" />
    <text x="20" y="24" fill="currentColor" font-size="12" font-weight="700" font-family="system-ui">Non-Contiguous Memory Allocation</text>
    <text x="20" y="38" fill="currentColor" fill-opacity="0.7" font-size="11" font-family="system-ui">Nodes reside anywhere in heap memory connected by explicit 8-byte pointer references.</text>
  </g>
</svg>"""

    @staticmethod
    def _stack_svg() -> str:
        return """<svg viewBox="0 0 560 270" class="w-full h-auto max-h-[320px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="stackGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8b5cf6" />
      <stop offset="100%" stop-color="#6d28d9" />
    </linearGradient>
    <linearGradient id="topGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ec4899" />
      <stop offset="100%" stop-color="#be185d" />
    </linearGradient>
    <marker id="stackArr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 z" fill="#f472b6" />
    </marker>
  </defs>

  <path d="M 180 50 L 180 230 L 380 230 L 380 50" fill="none" stroke="currentColor" stroke-opacity="0.3" stroke-width="4" stroke-linecap="round" />

  <rect x="195" y="185" width="170" height="36" rx="6" fill="url(#stackGrad)" stroke="#c4b5fd" stroke-width="1.5" />
  <text x="280" y="208" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700" font-family="system-ui">Element 1 (Bottom)</text>

  <rect x="195" y="142" width="170" height="36" rx="6" fill="url(#stackGrad)" stroke="#c4b5fd" stroke-width="1.5" />
  <text x="280" y="165" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700" font-family="system-ui">Element 2</text>

  <rect x="195" y="99" width="170" height="36" rx="6" fill="url(#stackGrad)" stroke="#c4b5fd" stroke-width="1.5" />
  <text x="280" y="122" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700" font-family="system-ui">Element 3</text>

  <rect x="195" y="56" width="170" height="36" rx="6" fill="url(#topGrad)" stroke="#fbcfe8" stroke-width="2" />
  <text x="280" y="79" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="800" font-family="system-ui">Element 4 (TOP)</text>

  <line x1="440" y1="74" x2="385" y2="74" stroke="#f472b6" stroke-width="2.5" marker-end="url(#stackArr)" />
  <text x="448" y="78" fill="#f472b6" font-size="12" font-weight="800" font-family="monospace">TOP Pointer</text>

  <g transform="translate(40, 70)">
    <text x="0" y="0" fill="#34d399" font-size="12" font-weight="800" font-family="system-ui">↓ PUSH(x)</text>
    <text x="0" y="16" fill="currentColor" fill-opacity="0.6" font-size="10" font-family="system-ui">Adds element to Top</text>
    <text x="0" y="34" fill="#34d399" font-size="10" font-weight="700" font-family="monospace">Time: O(1)</text>
  </g>

  <g transform="translate(40, 150)">
    <text x="0" y="0" fill="#f472b6" font-size="12" font-weight="800" font-family="system-ui">↑ POP()</text>
    <text x="0" y="16" fill="currentColor" fill-opacity="0.6" font-size="10" font-family="system-ui">Removes element from Top</text>
    <text x="0" y="34" fill="#f472b6" font-size="10" font-weight="700" font-family="monospace">Time: O(1)</text>
  </g>

  <text x="280" y="255" text-anchor="middle" fill="currentColor" fill-opacity="0.75" font-size="11" font-weight="700" font-family="system-ui">LIFO Invariant: Last-In, First-Out • Top Access Only</text>
</svg>"""

    @staticmethod
    def _queue_svg() -> str:
        return """<svg viewBox="0 0 580 240" class="w-full h-auto max-h-[300px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="qGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="100%" stop-color="#0369a1" />
    </linearGradient>
    <marker id="qArr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 z" fill="#38bdf8" />
    </marker>
  </defs>

  <line x1="80" y1="65" x2="500" y2="65" stroke="currentColor" stroke-opacity="0.25" stroke-width="3" stroke-linecap="round" />
  <line x1="80" y1="145" x2="500" y2="145" stroke="currentColor" stroke-opacity="0.25" stroke-width="3" stroke-linecap="round" />

  <g transform="translate(130, 75)">
    <rect width="70" height="60" rx="8" fill="url(#qGrad)" stroke="#7dd3fc" stroke-width="1.5" />
    <text x="35" y="35" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="700" font-family="system-ui">Data 4</text>
    <text x="35" y="78" text-anchor="middle" fill="#f59e0b" font-size="11" font-weight="700" font-family="monospace">REAR</text>
  </g>

  <g transform="translate(215, 75)">
    <rect width="70" height="60" rx="8" fill="url(#qGrad)" stroke="#7dd3fc" stroke-width="1.5" />
    <text x="35" y="35" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="700" font-family="system-ui">Data 3</text>
  </g>

  <g transform="translate(300, 75)">
    <rect width="70" height="60" rx="8" fill="url(#qGrad)" stroke="#7dd3fc" stroke-width="1.5" />
    <text x="35" y="35" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="700" font-family="system-ui">Data 2</text>
  </g>

  <g transform="translate(385, 75)">
    <rect width="70" height="60" rx="8" fill="url(#qGrad)" stroke="#38bdf8" stroke-width="2" />
    <text x="35" y="35" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="800" font-family="system-ui">Data 1</text>
    <text x="35" y="78" text-anchor="middle" fill="#10b981" font-size="11" font-weight="700" font-family="monospace">FRONT</text>
  </g>

  <line x1="45" y1="105" x2="115" y2="105" stroke="#f59e0b" stroke-width="2.5" marker-end="url(#qArr)" />
  <text x="80" y="50" text-anchor="middle" fill="#f59e0b" font-size="11" font-weight="800" font-family="system-ui">ENQUEUE →</text>
  <text x="80" y="125" text-anchor="middle" fill="currentColor" fill-opacity="0.5" font-size="9" font-family="monospace">In at Rear</text>

  <line x1="465" y1="105" x2="535" y2="105" stroke="#10b981" stroke-width="2.5" marker-end="url(#qArr)" />
  <text x="500" y="50" text-anchor="middle" fill="#10b981" font-size="11" font-weight="800" font-family="system-ui">→ DEQUEUE</text>
  <text x="500" y="125" text-anchor="middle" fill="currentColor" fill-opacity="0.5" font-size="9" font-family="monospace">Out at Front</text>

  <text x="290" y="200" text-anchor="middle" fill="currentColor" fill-opacity="0.8" font-size="11" font-weight="700" font-family="system-ui">FIFO Invariant: First-In, First-Out • O(1) Push/Pop Guaranteed</text>
</svg>"""

    @staticmethod
    def _hash_table_svg() -> str:
        return """<svg viewBox="0 0 600 280" class="w-full h-auto max-h-[320px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="htKey" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#1d4ed8" />
    </linearGradient>
    <linearGradient id="htFunc" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8b5cf6" />
      <stop offset="100%" stop-color="#6d28d9" />
    </linearGradient>
    <linearGradient id="htBucket" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="100%" stop-color="#0369a1" />
    </linearGradient>
    <linearGradient id="htChain" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>
    <marker id="htArr" markerWidth="8" markerHeight="8" refX="5" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#818cf8" />
    </marker>
    <marker id="htChainArr" markerWidth="8" markerHeight="8" refX="5" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#34d399" />
    </marker>
  </defs>

  <g transform="translate(20, 45)">
    <text x="0" y="-12" fill="currentColor" fill-opacity="0.6" font-size="11" font-weight="700" font-family="system-ui">KEYS (INPUT)</text>
    <rect x="0" y="0" width="105" height="34" rx="6" fill="url(#htKey)" />
    <text x="52" y="21" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="monospace">"Alice"</text>
    <rect x="0" y="50" width="105" height="34" rx="6" fill="url(#htKey)" />
    <text x="52" y="71" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="monospace">"Bob"</text>
    <rect x="0" y="100" width="105" height="34" rx="6" fill="url(#htKey)" />
    <text x="52" y="121" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="monospace">"Charlie"</text>
  </g>

  <g transform="translate(170, 70)">
    <rect width="130" height="74" rx="10" fill="url(#htFunc)" stroke="#c4b5fd" stroke-width="2" />
    <text x="65" y="32" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="800" font-family="system-ui">Hash Function</text>
    <text x="65" y="52" text-anchor="middle" fill="#e0e7ff" font-size="11" font-weight="700" font-family="monospace">h(k) = sum(k) % M</text>
  </g>

  <path d="M 125 62 C 145 62, 145 100, 165 100" fill="none" stroke="#818cf8" stroke-width="2" marker-end="url(#htArr)" />
  <path d="M 125 112 C 145 112, 145 107, 165 107" fill="none" stroke="#818cf8" stroke-width="2" marker-end="url(#htArr)" />
  <path d="M 125 162 C 145 162, 145 114, 165 114" fill="none" stroke="#818cf8" stroke-width="2" marker-end="url(#htArr)" />
  <line x1="302" y1="107" x2="350" y2="107" stroke="#818cf8" stroke-width="2.5" marker-end="url(#htArr)" />

  <g transform="translate(355, 30)">
    <text x="15" y="-8" fill="currentColor" fill-opacity="0.6" font-size="11" font-weight="700" font-family="system-ui">BUCKETS</text>
    <rect x="0" y="0" width="60" height="34" rx="4" fill="url(#htBucket)" stroke="#7dd3fc" stroke-width="1.5" />
    <text x="30" y="21" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="monospace">[0]</text>
    <rect x="0" y="40" width="60" height="34" rx="4" fill="url(#htBucket)" stroke="#38bdf8" stroke-width="2" />
    <text x="30" y="61" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="800" font-family="monospace">[1]</text>
    <rect x="0" y="80" width="60" height="34" rx="4" fill="url(#htBucket)" stroke="#7dd3fc" stroke-width="1.5" />
    <text x="30" y="101" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="monospace">[2]</text>
    <rect x="0" y="120" width="60" height="34" rx="4" fill="url(#htBucket)" stroke="#7dd3fc" stroke-width="1.5" />
    <text x="30" y="141" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="monospace">[3]</text>
    <rect x="0" y="160" width="60" height="34" rx="4" fill="url(#htBucket)" stroke="#7dd3fc" stroke-width="1.5" />
    <text x="30" y="181" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700" font-family="monospace">[4]</text>

    <line x1="62" y1="57" x2="88" y2="57" stroke="#34d399" stroke-width="2" marker-end="url(#htChainArr)" />
    <rect x="92" y="42" width="70" height="30" rx="4" fill="url(#htChain)" />
    <text x="127" y="61" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="700" font-family="monospace">Alice:95</text>
    <line x1="164" y1="57" x2="188" y2="57" stroke="#34d399" stroke-width="2" marker-end="url(#htChainArr)" />
    <rect x="192" y="42" width="78" height="30" rx="4" fill="url(#htChain)" />
    <text x="231" y="61" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="700" font-family="monospace">Charlie:88</text>
  </g>

  <g transform="translate(20, 240)">
    <rect width="560" height="32" rx="6" fill="currentColor" fill-opacity="0.08" />
    <text x="280" y="21" text-anchor="middle" fill="currentColor" fill-opacity="0.8" font-size="11" font-weight="700" font-family="system-ui">Average Lookup: O(1) • Collision Handling via Separate Chaining • Worst Case: O(n)</text>
  </g>
</svg>"""

    @staticmethod
    def _graph_svg() -> str:
        return """<svg viewBox="0 0 580 270" class="w-full h-auto max-h-[320px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grSrc" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>
    <linearGradient id="grDest" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b" />
      <stop offset="100%" stop-color="#d97706" />
    </linearGradient>
    <linearGradient id="grNode" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366f1" />
      <stop offset="100%" stop-color="#4338ca" />
    </linearGradient>
    <marker id="grArr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#94a3b8" />
    </marker>
    <marker id="grPathArr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#10b981" />
    </marker>
  </defs>

  <line x1="80" y1="120" x2="220" y2="50" stroke="#94a3b8" stroke-width="2" marker-end="url(#grArr)" />
  <text x="145" y="75" fill="currentColor" fill-opacity="0.6" font-size="11" font-weight="700" font-family="monospace">wt: 4</text>
  <line x1="220" y1="50" x2="380" y2="50" stroke="#94a3b8" stroke-width="2" marker-end="url(#grArr)" />
  <text x="300" y="42" fill="currentColor" fill-opacity="0.6" font-size="11" font-weight="700" font-family="monospace">wt: 5</text>
  <line x1="220" y1="190" x2="380" y2="190" stroke="#94a3b8" stroke-width="2" marker-end="url(#grArr)" />
  <text x="300" y="208" fill="currentColor" fill-opacity="0.6" font-size="11" font-weight="700" font-family="monospace">wt: 7</text>

  <line x1="80" y1="120" x2="220" y2="190" stroke="#10b981" stroke-width="3.5" marker-end="url(#grPathArr)" />
  <rect x="135" y="160" width="38" height="18" rx="4" fill="#064e3b" />
  <text x="154" y="173" text-anchor="middle" fill="#6ee7b7" font-size="11" font-weight="800" font-family="monospace">wt: 2</text>

  <line x1="220" y1="190" x2="380" y2="50" stroke="#10b981" stroke-width="3.5" marker-end="url(#grPathArr)" />
  <rect x="290" y="112" width="38" height="18" rx="4" fill="#064e3b" />
  <text x="309" y="125" text-anchor="middle" fill="#6ee7b7" font-size="11" font-weight="800" font-family="monospace">wt: 1</text>

  <line x1="380" y1="50" x2="500" y2="120" stroke="#10b981" stroke-width="3.5" marker-end="url(#grPathArr)" />
  <rect x="430" y="75" width="38" height="18" rx="4" fill="#064e3b" />
  <text x="449" y="88" text-anchor="middle" fill="#6ee7b7" font-size="11" font-weight="800" font-family="monospace">wt: 3</text>

  <g transform="translate(80, 120)">
    <circle r="24" fill="url(#grSrc)" stroke="#a7f3d0" stroke-width="2.5" />
    <text y="5" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="800" font-family="system-ui">A</text>
    <text y="36" text-anchor="middle" fill="#10b981" font-size="10" font-weight="700" font-family="system-ui">Start (0)</text>
  </g>
  <g transform="translate(220, 50)">
    <circle r="22" fill="url(#grNode)" stroke="#c7d2fe" stroke-width="2" />
    <text y="5" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700" font-family="system-ui">B</text>
  </g>
  <g transform="translate(220, 190)">
    <circle r="22" fill="url(#grNode)" stroke="#c7d2fe" stroke-width="2" />
    <text y="5" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700" font-family="system-ui">C</text>
    <text y="34" text-anchor="middle" fill="#6ee7b7" font-size="10" font-weight="700" font-family="monospace">dist: 2</text>
  </g>
  <g transform="translate(380, 50)">
    <circle r="22" fill="url(#grNode)" stroke="#c7d2fe" stroke-width="2" />
    <text y="5" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700" font-family="system-ui">D</text>
    <text y="34" text-anchor="middle" fill="#6ee7b7" font-size="10" font-weight="700" font-family="monospace">dist: 3</text>
  </g>
  <g transform="translate(500, 120)">
    <circle r="24" fill="url(#grDest)" stroke="#fde68a" stroke-width="2.5" />
    <text y="5" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="800" font-family="system-ui">E</text>
    <text y="36" text-anchor="middle" fill="#f59e0b" font-size="10" font-weight="700" font-family="system-ui">Dest (Cost: 6)</text>
  </g>

  <text x="290" y="252" text-anchor="middle" fill="currentColor" fill-opacity="0.8" font-size="11" font-weight="700" font-family="system-ui">Dijkstra Shortest Path: A → C (2) → D (1) → E (3) • Total Optimal Cost = 6</text>
</svg>"""

    @staticmethod
    def _os_svg() -> str:
        return """<svg viewBox="0 0 580 270" class="w-full h-auto max-h-[320px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="osState" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#1d4ed8" />
    </linearGradient>
    <linearGradient id="osRunning" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>
    <linearGradient id="osWait" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b" />
      <stop offset="100%" stop-color="#b45309" />
    </linearGradient>
    <marker id="osArr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#60a5fa" />
    </marker>
  </defs>

  <g transform="translate(30, 85)">
    <rect width="70" height="50" rx="8" fill="url(#osState)" stroke="#93c5fd" stroke-width="1.5" />
    <text x="35" y="30" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="800" font-family="system-ui">NEW</text>
  </g>
  <line x1="102" y1="110" x2="158" y2="110" stroke="#60a5fa" stroke-width="2" marker-end="url(#osArr)" />
  <text x="130" y="102" text-anchor="middle" fill="currentColor" fill-opacity="0.6" font-size="9" font-weight="700" font-family="system-ui">Admitted</text>

  <g transform="translate(160, 85)">
    <rect width="85" height="50" rx="8" fill="url(#osState)" stroke="#93c5fd" stroke-width="2" />
    <text x="42" y="30" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="800" font-family="system-ui">READY</text>
  </g>

  <path d="M 247 100 L 328 100" fill="none" stroke="#60a5fa" stroke-width="2" marker-end="url(#osArr)" />
  <text x="288" y="93" text-anchor="middle" fill="#38bdf8" font-size="9" font-weight="700" font-family="system-ui">Scheduler Dispatch</text>

  <path d="M 330 120 C 290 140, 280 140, 247 125" fill="none" stroke="#f87171" stroke-width="2" marker-end="url(#osArr)" />
  <text x="288" y="152" text-anchor="middle" fill="#f87171" font-size="9" font-weight="700" font-family="system-ui">Interrupt / Time Slice</text>

  <g transform="translate(330, 85)">
    <rect width="95" height="50" rx="8" fill="url(#osRunning)" stroke="#6ee7b7" stroke-width="2.5" />
    <text x="47" y="30" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="800" font-family="system-ui">RUNNING</text>
  </g>

  <line x1="427" y1="110" x2="478" y2="110" stroke="#60a5fa" stroke-width="2" marker-end="url(#osArr)" />
  <text x="452" y="102" text-anchor="middle" fill="currentColor" fill-opacity="0.6" font-size="9" font-weight="700" font-family="system-ui">Exit</text>

  <g transform="translate(480, 85)">
    <rect width="80" height="50" rx="8" fill="url(#osState)" stroke="#93c5fd" stroke-width="1.5" />
    <text x="40" y="30" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="800" font-family="system-ui">TERMINATED</text>
  </g>

  <path d="M 377 137 L 377 195 L 340 195" fill="none" stroke="#f59e0b" stroke-width="2" marker-end="url(#osArr)" />
  <text x="410" y="175" fill="#f59e0b" font-size="9" font-weight="700" font-family="system-ui">I/O or Event Wait</text>

  <g transform="translate(235, 175)">
    <rect width="105" height="48" rx="8" fill="url(#osWait)" stroke="#fcd34d" stroke-width="2" />
    <text x="52" y="28" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="800" font-family="system-ui">WAITING / BLOCKED</text>
  </g>

  <path d="M 235 195 L 202 195 L 202 140" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#osArr)" />
  <text x="150" y="180" fill="#34d399" font-size="9" font-weight="700" font-family="system-ui">I/O Completion</text>

  <text x="290" y="252" text-anchor="middle" fill="currentColor" fill-opacity="0.8" font-size="11" font-weight="700" font-family="system-ui">Classic 5-State Process Model • Managed by Kernel PCB (Process Control Block)</text>
</svg>"""

    @staticmethod
    def _osi_svg() -> str:
        return """<svg viewBox="0 0 580 270" class="w-full h-auto max-h-[320px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="osiL7" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6d28d9"/></linearGradient>
    <linearGradient id="osiL4" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#1d4ed8"/></linearGradient>
    <linearGradient id="osiL3" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0284c7"/><stop offset="100%" stop-color="#0369a1"/></linearGradient>
    <linearGradient id="osiL2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#10b981"/><stop offset="100%" stop-color="#047857"/></linearGradient>
    <linearGradient id="osiL1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#b45309"/></linearGradient>
  </defs>

  <g transform="translate(40, 25)">
    <g transform="translate(0, 0)">
      <rect width="360" height="34" rx="6" fill="url(#osiL7)" />
      <text x="15" y="21" fill="#ffffff" font-size="12" font-weight="800" font-family="system-ui">Layer 7: Application</text>
      <text x="210" y="21" fill="#e0e7ff" font-size="11" font-weight="600" font-family="system-ui">HTTP, DNS, SSH, TLS</text>
      <rect x="375" y="0" width="125" height="34" rx="6" fill="currentColor" fill-opacity="0.08" />
      <text x="437" y="21" text-anchor="middle" fill="currentColor" font-size="11" font-weight="700" font-family="monospace">User Data / Payload</text>
    </g>

    <g transform="translate(0, 42)">
      <rect width="360" height="34" rx="6" fill="url(#osiL4)" />
      <text x="15" y="21" fill="#ffffff" font-size="12" font-weight="800" font-family="system-ui">Layer 4: Transport</text>
      <text x="210" y="21" fill="#dbeafe" font-size="11" font-weight="600" font-family="system-ui">TCP / UDP (Port Addressing)</text>
      <rect x="375" y="0" width="125" height="34" rx="6" fill="currentColor" fill-opacity="0.08" />
      <text x="437" y="21" text-anchor="middle" fill="#60a5fa" font-size="11" font-weight="700" font-family="monospace">Segments (Ports)</text>
    </g>

    <g transform="translate(0, 84)">
      <rect width="360" height="34" rx="6" fill="url(#osiL3)" />
      <text x="15" y="21" fill="#ffffff" font-size="12" font-weight="800" font-family="system-ui">Layer 3: Network</text>
      <text x="210" y="21" fill="#e0f2fe" font-size="11" font-weight="600" font-family="system-ui">IPv4 / IPv6, ICMP, Routing</text>
      <rect x="375" y="0" width="125" height="34" rx="6" fill="currentColor" fill-opacity="0.08" />
      <text x="437" y="21" text-anchor="middle" fill="#38bdf8" font-size="11" font-weight="700" font-family="monospace">Packets (IP Addr)</text>
    </g>

    <g transform="translate(0, 126)">
      <rect width="360" height="34" rx="6" fill="url(#osiL2)" />
      <text x="15" y="21" fill="#ffffff" font-size="12" font-weight="800" font-family="system-ui">Layer 2: Data Link</text>
      <text x="210" y="21" fill="#d1fae5" font-size="11" font-weight="600" font-family="system-ui">Ethernet, Wi-Fi 802.11</text>
      <rect x="375" y="0" width="125" height="34" rx="6" fill="currentColor" fill-opacity="0.08" />
      <text x="437" y="21" text-anchor="middle" fill="#34d399" font-size="11" font-weight="700" font-family="monospace">Frames (MAC Addr)</text>
    </g>

    <g transform="translate(0, 168)">
      <rect width="360" height="34" rx="6" fill="url(#osiL1)" />
      <text x="15" y="21" fill="#ffffff" font-size="12" font-weight="800" font-family="system-ui">Layer 1: Physical</text>
      <text x="210" y="21" fill="#fef3c7" font-size="11" font-weight="600" font-family="system-ui">Copper, Fiber, Radio Waves</text>
      <rect x="375" y="0" width="125" height="34" rx="6" fill="currentColor" fill-opacity="0.08" />
      <text x="437" y="21" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="700" font-family="monospace">Bitstream (01101)</text>
    </g>
  </g>

  <text x="290" y="248" text-anchor="middle" fill="currentColor" fill-opacity="0.8" font-size="11" font-weight="700" font-family="system-ui">Data Encapsulation: Headers prepended as payload travels down the protocol stack</text>
</svg>"""

    @staticmethod
    def _physics_svg() -> str:
        return """<svg viewBox="0 0 580 270" class="w-full h-auto max-h-[320px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="massGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#1d4ed8" />
    </linearGradient>
    <marker id="physArr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#38bdf8" />
    </marker>
    <marker id="physRed" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#f87171" />
    </marker>
    <marker id="physGreen" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#34d399" />
    </marker>
  </defs>

  <line x1="60" y1="180" x2="520" y2="180" stroke="currentColor" stroke-opacity="0.4" stroke-width="3" />
  <line x1="100" y1="180" x2="90" y2="195" stroke="currentColor" stroke-opacity="0.2" stroke-width="2" />
  <line x1="180" y1="180" x2="170" y2="195" stroke="currentColor" stroke-opacity="0.2" stroke-width="2" />
  <line x1="260" y1="180" x2="250" y2="195" stroke="currentColor" stroke-opacity="0.2" stroke-width="2" />
  <line x1="340" y1="180" x2="330" y2="195" stroke="currentColor" stroke-opacity="0.2" stroke-width="2" />
  <line x1="420" y1="180" x2="410" y2="195" stroke="currentColor" stroke-opacity="0.2" stroke-width="2" />

  <rect x="230" y="100" width="120" height="80" rx="8" fill="url(#massGrad)" stroke="#93c5fd" stroke-width="2" />
  <text x="290" y="145" text-anchor="middle" fill="#ffffff" font-size="16" font-weight="800" font-family="system-ui">Mass (m)</text>

  <line x1="290" y1="100" x2="290" y2="25" stroke="#34d399" stroke-width="3" marker-end="url(#physGreen)" />
  <text x="290" y="15" text-anchor="middle" fill="#34d399" font-size="12" font-weight="800" font-family="system-ui">F_N (Normal Force)</text>

  <line x1="290" y1="180" x2="290" y2="245" stroke="#f87171" stroke-width="3" marker-end="url(#physRed)" />
  <text x="290" y="260" text-anchor="middle" fill="#f87171" font-size="12" font-weight="800" font-family="system-ui">F_g = mg (Weight)</text>

  <line x1="350" y1="140" x2="450" y2="140" stroke="#38bdf8" stroke-width="3.5" marker-end="url(#physArr)" />
  <text x="460" y="145" fill="#38bdf8" font-size="12" font-weight="800" font-family="system-ui">F_applied</text>

  <line x1="230" y1="178" x2="150" y2="178" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#physArr)" />
  <text x="140" y="174" text-anchor="end" fill="#fbbf24" font-size="11" font-weight="700" font-family="system-ui">f_k = μ_k F_N</text>

  <text x="80" y="45" fill="currentColor" fill-opacity="0.85" font-size="12" font-weight="700" font-family="monospace">F_net = m × a</text>
  <text x="80" y="65" fill="currentColor" fill-opacity="0.6" font-size="11" font-family="system-ui">a = (F_applied - f_k) / m</text>
</svg>"""

    @staticmethod
    def _calculus_svg() -> str:
        return """<svg viewBox="0 0 580 270" class="w-full h-auto max-h-[320px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="calcArea" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.45" />
      <stop offset="100%" stop-color="#1d4ed8" stop-opacity="0.05" />
    </linearGradient>
    <marker id="calcArr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="currentColor" />
    </marker>
  </defs>

  <line x1="60" y1="210" x2="520" y2="210" stroke="currentColor" stroke-opacity="0.5" stroke-width="2" marker-end="url(#calcArr)" />
  <text x="525" y="214" fill="currentColor" font-size="12" font-weight="700" font-family="system-ui">x</text>

  <line x1="80" y1="230" x2="80" y2="30" stroke="currentColor" stroke-opacity="0.5" stroke-width="2" marker-end="url(#calcArr)" />
  <text x="75" y="22" fill="currentColor" font-size="12" font-weight="700" font-family="system-ui">y</text>

  <path d="M 160 210 L 160 145 C 220 70, 320 60, 400 135 L 400 210 Z" fill="url(#calcArea)" stroke="none" />
  <path d="M 100 180 C 160 145, 220 70, 320 60 C 370 55, 420 160, 480 170" fill="none" stroke="#38bdf8" stroke-width="3" />
  <text x="320" y="45" fill="#38bdf8" font-size="13" font-weight="800" font-family="monospace">y = f(x)</text>

  <line x1="160" y1="210" x2="160" y2="145" stroke="#818cf8" stroke-width="2" stroke-dasharray="4" />
  <circle cx="160" cy="210" r="4" fill="#818cf8" />
  <text x="160" y="228" text-anchor="middle" fill="#818cf8" font-size="13" font-weight="800" font-family="system-ui">a</text>

  <line x1="400" y1="210" x2="400" y2="135" stroke="#818cf8" stroke-width="2" stroke-dasharray="4" />
  <circle cx="400" cy="210" r="4" fill="#818cf8" />
  <text x="400" y="228" text-anchor="middle" fill="#818cf8" font-size="13" font-weight="800" font-family="system-ui">b</text>

  <rect x="270" y="65" width="22" height="145" fill="#10b981" fill-opacity="0.3" stroke="#34d399" stroke-width="1.5" />
  <text x="281" y="140" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="800" font-family="monospace">f(x)dx</text>

  <g transform="translate(180, 240)">
    <rect width="220" height="26" rx="5" fill="currentColor" fill-opacity="0.08" />
    <text x="110" y="18" text-anchor="middle" fill="currentColor" font-size="12" font-weight="700" font-family="monospace">∫_a^b f(x) dx = F(b) - F(a)</text>
  </g>
</svg>"""

    @staticmethod
    def _universal_svg() -> str:
        return """<svg viewBox="0 0 580 250" class="w-full h-auto max-h-[300px] select-none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="uInp" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#1d4ed8"/></linearGradient>
    <linearGradient id="uProc" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6d28d9"/></linearGradient>
    <linearGradient id="uOut" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#10b981"/><stop offset="100%" stop-color="#047857"/></linearGradient>
    <marker id="uArr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 1 L 7 4 L 0 7 z" fill="#818cf8" />
    </marker>
  </defs>

  <g transform="translate(30, 80)">
    <rect width="130" height="70" rx="8" fill="url(#uInp)" />
    <text x="65" y="32" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="800" font-family="system-ui">Input / State (S₀)</text>
    <text x="65" y="52" text-anchor="middle" fill="#bfdbfe" font-size="10" font-family="system-ui">Initial Parameters</text>
  </g>

  <line x1="162" y1="115" x2="222" y2="115" stroke="#818cf8" stroke-width="2.5" marker-end="url(#uArr)" />

  <g transform="translate(225, 65)">
    <rect width="150" height="100" rx="10" fill="url(#uProc)" stroke="#c4b5fd" stroke-width="2" />
    <text x="75" y="38" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="800" font-family="system-ui">Core Execution</text>
    <text x="75" y="58" text-anchor="middle" fill="#e0e7ff" font-size="11" font-weight="700" font-family="monospace">Transformation Φ</text>
    <text x="75" y="78" text-anchor="middle" fill="#c7d2fe" font-size="10" font-family="system-ui">Governing Invariant</text>
  </g>

  <line x1="377" y1="115" x2="437" y2="115" stroke="#818cf8" stroke-width="2.5" marker-end="url(#uArr)" />

  <g transform="translate(440, 80)">
    <rect width="120" height="70" rx="8" fill="url(#uOut)" />
    <text x="60" y="32" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="800" font-family="system-ui">Validated Output</text>
    <text x="60" y="52" text-anchor="middle" fill="#a7f3d0" font-size="10" font-family="system-ui">Terminal State</text>
  </g>

  <path d="M 500 152 C 500 205, 100 205, 100 152" fill="none" stroke="#60a5fa" stroke-width="2" stroke-dasharray="4" marker-end="url(#uArr)" />
  <text x="300" y="215" text-anchor="middle" fill="#60a5fa" font-size="11" font-weight="700" font-family="system-ui">Feedback / Convergence / Validation Cycle</text>
</svg>"""
