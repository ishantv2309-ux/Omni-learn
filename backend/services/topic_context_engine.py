"""
Topic Context Engine for OmniLearn
Provides deep, textbook-grade academic context, structural invariants, variants,
complexity formulations, and historical trivia across all academic disciplines.
"""

def clean_title_casing(title: str) -> str:
    words = title.split()
    lower_words = {"a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by", "with", "in", "of"}
    result = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i == 0 or i == len(words) - 1 or lw not in lower_words:
            result.append(w.capitalize())
        else:
            result.append(lw)
    return " ".join(result)

class TopicContextEngine:
    @staticmethod
    def build_topic_diagram(clean_q: str, topic: str, detected_domain: str) -> dict:
        from backend.services.diagram_engine import DiagramEngine
        return DiagramEngine.build_diagram(clean_q, topic, detected_domain)

    @staticmethod
    def build_topic_context(clean_q: str, detected_domain: str) -> dict:
        data = TopicContextEngine._build_topic_context_raw(clean_q, detected_domain)
        # Normalize newlines for markdown rendering
        for k in ["overview", "theoretical_foundations", "core_formulations"]:
            if k in data and isinstance(data[k], str):
                data[k] = data[k].replace(chr(92) + "n", chr(10))
        data["diagram"] = TopicContextEngine.build_topic_diagram(clean_q, data.get("topic", clean_q), detected_domain)
        return data

    @staticmethod
    def _build_topic_context_raw(clean_q: str, detected_domain: str) -> dict:
        topic = clean_title_casing(clean_q.strip())
        t_low = clean_q.lower().strip()

        # 1. Binary Tree & Specialized Tree Variants
        if any(k in t_low for k in ["binary tree", "bst", "binary search tree", "avl", "red black", "tree traversal", "b tree", "b+ tree"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.4,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} demands structural recursion mastery, preserving logarithmic height bounds $O(\\log n)$, preventing degenerate $O(n)$ skewing, and executing self-balancing rotations.",
                "overview": (
                    f"A **{topic}** is a non-linear, hierarchical data structure composed of nodes connected by directed edges, "
                    f"originating from a single designated **root node**. Each node encapsulates a data payload and maintains references "
                    f"to at most two distinct child subtrees, conventionally designated as the **left child** and the **right child**. "
                    f"Nodes with zero children are termed **leaf nodes**, while non-leaf nodes are **internal nodes**.\n\n"
                    f"### Core Structural Invariants\n"
                    fr"- **Branching Degree Constraint**: Every node $u$ satisfies $\\text{{degree}}(u) \\le 2$, establishing a recursive binary decision hierarchy.\n"
                    fr"- **Recursive Subtree Topology**: Every child node is itself the root of an independent binary subtree. This recursive symmetry makes divide-and-conquer traversals ($\\text{{Pre-order}}$, $\\text{{In-order}}$, $\\text{{Post-order}}$, and $\\text{{Level-order / BFS}}$) the standard algorithmic execution model.\n"
                    fr"- **Logarithmic Height Scaling**: In a balanced binary tree with $n$ nodes, the height is bounded by $h = \\lfloor\\log_2 n\\rfloor$, guaranteeing that search, insertion, and deletion paths scale in $\\mathcal{{O}}(\\log n)$ time rather than $\\mathcal{{O}}(n)$ linear scans.\n"
                    fr"- **Node-to-Edge Invariant**: Any binary tree containing $n$ nodes contains exactly $n - 1$ edges with no cycles or isolated components.\n\n"
                    f"### Key Architectural Varieties\n"
                    fr"- **Full Binary Tree**: Every node contains strictly 0 or 2 children (no node has exactly 1 child).\n"
                    fr"- **Complete Binary Tree**: Every level except possibly the deepest is completely filled, and all leaf nodes in the last level are left-aligned (the exact structural invariant powering **Binary Heaps** and Priority Queues inside array buffers).\n"
                    fr"- **Binary Search Tree (BST)**: Enforces the key ordering property ($\\forall x \\in \\text{{Left}}(u), \\text{{key}}(x) < \\text{{key}}(u)$ and $\\forall y \\in \\text{{Right}}(u), \\text{{key}}(y) > \\text{{key}}(u)$), enabling ordered retrieval and fast lookups.\n"
                    fr"- **Self-Balancing Trees (AVL & Red-Black)**: Dynamically perform local tree rotations during writes to enforce height invariants and eliminate degenerate $\\mathcal{{O}}(n)$ skewed trees.\n\n"
                    f"### Computational Significance & Systems Role\n"
                    f"Binary trees resolve the fundamental trade-off between contiguous arrays (fast $\\mathcal{{O}}(1)$ random indexing but rigid $\\mathcal{{O}}(n)$ insertion shifts) "
                    f"and linked lists (fast $\\mathcal{{O}}(1)$ pointer insertions but slow $\\mathcal{{O}}(n)$ sequential search). They serve as the core structural foundation for "
                    f"**Abstract Syntax Trees (ASTs)** in compilers, the **Document Object Model (DOM)** in web browsers, **B/B+ Trees** in database indexing engines (PostgreSQL, MySQL), "
                    f"and **Huffman Trees** in lossless data compression."
                ),
                "theoretical_foundations": (
                    f"Formally grounded in graph theory as a directed acyclic connected graph $G = (V, E)$ with a unique root node $\\text{{in-degree}}(r) = 0$ "
                    f"and $|E| = |V| - 1$. The out-degree of every vertex is strictly bounded by $\\text{{out-degree}}(v) \\le 2$. "
                    f"Correctness of operations is formally established via structural induction over left and right subtrees. "
                    f"In balanced configurations, average path length from the root is $\\Theta(\\log n)$."
                ),
                "core_formulations": (
                    r"- **Maximum Node Capacity at Height $h$**: $$\sum_{i=0}^h 2^i = 2^{h+1} - 1$$\n"
                    r"- **Binary Search Tree (BST) Invariant**: $$\forall x \in \text{Left}(u), \, \text{key}(x) < \text{key}(u) \quad \land \quad \forall y \in \text{Right}(u), \, \text{key}(y) > \text{key}(u)$$\n"
                    r"- **Balanced Height Bound**: $$h = \lfloor \log_2 n \rfloor \implies \text{Search, Insert, Delete } \in \mathcal{O}(\log n)$$\n"
                    r"- **Degenerate / Skewed Tree Bound**: $$h = n - 1 \implies \text{Search, Insert, Delete } \in \mathcal{O}(n)$$\n"
                    r"- **AVL Tree Balance Factor**: $$\text{BF}(u) = \text{height}(\text{Left}(u)) - \text{height}(\text{Right}(u)) \in \{-1, 0, +1\}$$"
                ),
                "did_you_know": f"The binary search tree was independently discovered in 1960 by P.F. Windley, A.D. Booth, A.J.T. Colin, and T.N. Hibbard. In 1962, Soviet mathematicians Georgy Adelson-Velsky and Evgenii Landis invented the first self-balancing binary search tree (the AVL tree), ensuring guaranteed logarithmic operations."
            }

        # 2. General Trees & Tries
        if any(k in t_low for k in ["tree", "trie", "prefix tree"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.3,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} requires hierarchical recursive traversal comprehension, space-time trade-off evaluation, and edge case management across multi-way branch nodes.",
                "overview": (
                    f"A **{topic}** is a fundamental non-linear hierarchical data structure representing parent-child relationships across interconnected nodes. "
                    f"Unlike linear structures like arrays or linked lists, trees organize data in multi-level branches originating from a single **root node**. "
                    f"Each node can have multiple children, while every non-root node has exactly one parent node.\n\n"
                    f"### Core Invariants & Properties\n"
                    fr"- **Acyclic Connected Hierarchy**: A tree of $n$ nodes strictly contains $n - 1$ edges with zero cycles.\n"
                    fr"- **Unique Path Invariant**: There exists exactly one simple path between any pair of nodes in the tree.\n"
                    fr"- **Subtree Modularity**: Any child node serves as the root of an autonomous subtree, enabling recursive divide-and-conquer processing.\n\n"
                    f"### Key Variants\n"
                    fr"- **N-ary Tree**: Nodes can branch into up to $N$ children, widely used in file systems and organizational charts.\n"
                    fr"- **Trie (Prefix Tree)**: An ordered multi-way search tree where keys are strings formed by edges, powering search engine autocomplete and IP routing.\n"
                    fr"- **B-Trees & B+ Trees**: Self-balancing multi-way search trees designed for block storage, disk I/O reduction, and database indexes."
                ),
                "theoretical_foundations": f"Formally defined in discrete mathematics as an undirected connected graph without simple circuits. Directed trees define a partial ordering of vertices with a unique least element (the root).",
                "core_formulations": (
                    r"- **Tree Node-Edge Invariant**: $$|E| = |V| - 1$$\n"
                    r"- **Prefix Search Complexity (Trie)**: $$\mathcal{O}(L) \quad \text{where } L \text{ is string key length}$$\n"
                    r"- **B-Tree Disk Block Factor**: $$\text{Height} \le \lceil \log_{\lceil M/2 \rceil} ((N+1)/2) \rceil$$"
                ),
                "did_you_know": f"Edward Fredkin coined the term 'Trie' in 1960 from the word 're-TRIE-val', though it is commonly pronounced like 'try' to distinguish it from a general tree."
            }

        # 3. Array & Vector
        if any(k in t_low for k in ["array", "vector", "dynamic array", "matrix"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 4.5,
                "difficulty_level": "Beginner",
                "ai_evaluation": f"{topic} tests memory address calculation arithmetic, spatial cache locality awareness, and understanding the trade-off between $O(1)$ random indexing and $O(n)$ insertion shifting.",
                "overview": (
                    f"An **{topic}** is a fundamental linear data structure that stores elements of identical data type in a contiguous block of physical computer memory. "
                    f"Because memory addresses are strictly contiguous, each element can be accessed instantaneously via its numeric index through simple pointer arithmetic.\n\n"
                    f"### Core Structural Invariants\n"
                    fr"- **Contiguous Memory Allocation**: Elements occupy adjacent memory addresses $\text{{Base}} + i \times S$, with zero gap between consecutive slots.\n"
                    fr"- **Constant-Time Random Access**: Calculating the hardware memory address of $A[i]$ requires a single multiplication and addition, providing deterministic $O(1)$ read/write time.\n"
                    fr"- **Spatial Cache Locality**: Sequential arrangement enables modern CPU memory controllers to prefetch entire cache lines (typically 64 bytes), dramatically accelerating sequential scans compared to pointer-based structures.\n\n"
                    f"### Key Varieties & Engineering Realities\n"
                    fr"- **Static Array**: Fixed capacity defined at compile or initialization time. Cannot grow without allocating a new block.\n"
                    fr"- **Dynamic Array (Vector/ArrayList)**: Automatically grows by allocating a doubled memory buffer (amortized $O(1)$ append) when capacity is exhausted.\n"
                    fr"- **Multi-Dimensional Array / Matrix**: Arranged in row-major or column-major contiguous layout, vital for graphics, physics simulations, and deep learning tensors."
                ),
                "theoretical_foundations": f"Rooted in the Von Neumann computer architecture and random-access machine (RAM) model, where memory is an indexed sequence of addressable words.",
                "core_formulations": (
                    r"- **1D Contiguous Memory Offset**: $$\text{Address}(A[i]) = \text{Base} + i \times S$$\n"
                    r"- **2D Row-Major Offset**: $$\text{Address}(A[i][j]) = \text{Base} + (i \times N + j) \times S$$\n"
                    r"- **Operational Complexity**: Indexed Read/Write: $\mathcal{O}(1)$; Appending (Dynamic Array): Amortized $\mathcal{O}(1)$; Insertion/Deletion at Index: $\mathcal{O}(n)$."
                ),
                "did_you_know": f"John von Neumann and Alan Turing formalized linear contiguous store arrays in the 1940s. John Backus's 1957 FORTRAN implementation made multi-dimensional array arithmetic a standard programming abstraction."
            }

        # 4. Linked List
        if any(k in t_low for k in ["linked list", "singly linked", "doubly linked", "circular linked"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 5.8,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} requires pointer and reference integrity management, edge case handling (head/tail/null splicing), and trade-off evaluation between $O(1)$ pointer insertion and $O(n)$ sequential access.",
                "overview": (
                    f"A **{topic}** is a linear data structure wherein elements (called **nodes**) are stored discontinuously across computer heap memory. "
                    f"Each node contains a data payload and one or more explicit pointer references directing to the next (and optionally previous) node in the sequence.\n\n"
                    f"### Core Invariants & Mechanics\n"
                    fr"- **Pointer-Chained Topology**: Nodes do not require contiguous memory blocks. Memory is allocated dynamically per node upon insertion.\n"
                    fr"- **Constant-Time Splicing ($\\mathcal{{O}}(1)$)**: Inserting or deleting a node at a known pointer position only requires adjusting pointer addresses, avoiding the expensive $O(n)$ data shifting seen in arrays.\n"
                    fr"- **Sequential Access ($\\mathcal{{O}}(n)$)**: To reach the $k$-th element, the traversal must sequentially follow pointers from the head node.\n\n"
                    f"### Key Variations\n"
                    fr"- **Singly Linked List**: Each node contains a single `next` pointer.\n"
                    fr"- **Doubly Linked List**: Each node contains both `prev` and `next` pointers, enabling bidirectional traversal and $\\mathcal{{O}}(1)$ deletion given a node pointer.\n"
                    fr"- **Circular Linked List**: The tail node's `next` pointer loops back to the head node, ideal for round-robin CPU scheduling and circular media playlists."
                ),
                "theoretical_foundations": f"Developed as a fundamental dynamic data structure by Allen Newell, Cliff Shaw, and Herbert Simon at RAND Corporation in 1955-1956 for the IPL (Information Processing Language).",
                "core_formulations": (
                    r"- **Node Tuple Representation**: $$\text{Node}_i = \langle \text{data}, \&\text{Node}_{i+1} \rangle$$\n"
                    r"- **In-Place Reversal Invariant**: $$\text{next} = \text{curr}.\text{next}; \quad \text{curr}.\text{next} = \text{prev}; \quad \text{prev} = \text{curr}; \quad \text{curr} = \text{next}$$\n"
                    r"- **Operational Bounds**: Pointer Insertion/Deletion: $\mathcal{O}(1)$; Indexed Search/Traversal: $\mathcal{O}(n)$."
                ),
                "did_you_know": f"Linked lists were the fundamental foundation of Lisp (List Processing), invented by John McCarthy in 1958, which introduced automatic garbage collection to computer science."
            }

        # 5. Stack
        if any(k in t_low for k in ["stack", "lifo", "call stack"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 5.2,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} evaluates understanding of LIFO operational constraints, call stack frame allocation in runtime architectures, and expression evaluation parsing.",
                "overview": (
                    f"A **{topic}** is a restricted linear abstract data type operating under the strict **Last-In, First-Out (LIFO)** execution discipline. "
                    f"All element additions and removals are constrained to a single designated endpoint called the **top** of the stack.\n\n"
                    f"### Core Invariants & Operations\n"
                    fr"- **LIFO Principle**: The most recently added element is invariably the first to be retrieved or removed.\n"
                    fr"- **Atomic Primitive Operations**: `push(x)` to insert at top, `pop()` to remove from top, and `peek()` / `top()` to inspect the top element without removing it. All execute in deterministic $\\mathcal{{O}}(1)$ time.\n"
                    fr"- **Stack Pointer & Underflow/Overflow**: Governed by a top index pointer. Popping an empty stack triggers an underflow condition; pushing past capacity triggers overflow.\n\n"
                    f"### Essential Systems Applications\n"
                    fr"- **Call Stack**: Managing function invocation frames, return addresses, and local variables in CPU execution.\n"
                    fr"- **Syntax Parsing**: Parenthesis matching, XML/HTML tag validation, and Dijkstra's Shunting-yard expression parsing.\n"
                    fr"- **Backtracking**: Depth-First Search (DFS) state management, undo/redo mechanisms, and browser history."
                ),
                "theoretical_foundations": f"Formalized by Klaus Samelson and Friedrich L. Bauer in 1957 as a 'cellar' storage mechanism for mathematical formula evaluation, later standardized into the Von Neumann architectural call stack.",
                "core_formulations": (
                    r"- **Push State Delta**: $$\text{Push}(S, x) \implies S' = x \circ S, \quad \text{top}' = \text{top} + 1$$\n"
                    r"- **Pop State Delta**: $$\text{Pop}(S) \implies (x, S') \quad \text{where } x = \text{head}(S), \quad \text{top}' = \text{top} - 1$$\n"
                    r"- **Time Complexity**: Push: $\mathcal{O}(1)$; Pop: $\mathcal{O}(1)$; Peek: $\mathcal{O}(1)$."
                ),
                "did_you_know": f"Alan Turing used the terms 'bury' and 'unbury' in 1946 for subroutine calls, laying the mechanical groundwork for what Bauer and Samelson later patented as the pushdown stack."
            }

        # 6. Queue
        if any(k in t_low for k in ["queue", "fifo", "circular queue", "deque", "priority queue"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 5.4,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} tests understanding of FIFO order preservation, circular buffer pointer arithmetic, and concurrency synchronization in producer-consumer architectures.",
                "overview": (
                    f"A **{topic}** is a restricted linear data structure that enforces the strict **First-In, First-Out (FIFO)** sequencing discipline. "
                    f"Elements are exclusively appended at one end (the **rear** or **tail**) and removed from the opposite end (the **front** or **head**).\n\n"
                    f"### Core Invariants & Mechanics\n"
                    fr"- **FIFO Invariant**: The earliest element inserted into the structure is invariably the earliest to be extracted.\n"
                    fr"- **Constant-Time Operations ($\\mathcal{{O}}(1)$)**: `enqueue(x)` and `dequeue()` execute in strict $\\mathcal{{O}}(1)$ time using dual front/rear pointers.\n"
                    fr"- **Circular Buffer Arithmetic**: Avoids false overflow by wrapping pointers back to index 0 using modular arithmetic: $\\text{{index}} = (i + 1) \\pmod N$.\n\n"
                    f"### Key Variants\n"
                    fr"- **Circular Queue**: Eliminates wasted capacity by connecting the buffer's tail back to its head.\n"
                    fr"- **Double-Ended Queue (Deque)**: Permits insertion and removal at both front and rear ends.\n"
                    fr"- **Priority Queue**: Extracts elements according to numerical priority rather than chronological arrival, powered by Binary Heaps."
                ),
                "theoretical_foundations": f"Originating from queueing theory in mathematics (formalized by A.K. Erlang in telephone traffic engineering in 1909), and adopted by early multiprogramming OS kernels in the 1960s.",
                "core_formulations": (
                    r"- **Enqueue Transition**: $$\text{rear}_{\text{next}} = (\text{rear} + 1) \pmod N$$\n"
                    r"- **Dequeue Transition**: $$\text{front}_{\text{next}} = (\text{front} + 1) \pmod N$$\n"
                    r"- **Queue Full Condition**: $$(\text{rear} + 1) \pmod N = \text{front}$$\n"
                    r"- **Queue Empty Condition**: $$\text{front} = \text{rear}$$"
                ),
                "did_you_know": f"Danish mathematician A.K. Erlang founded queueing theory in 1909 to calculate how many telephone lines were needed to prevent calls from dropping, a model that now governs cloud load balancers and router queues."
            }

        # 7. Hash Table & Hashing
        if any(k in t_low for k in ["hash table", "hash map", "hashing", "hash set"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 6.8,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} tests hash function distribution analysis, collision resolution strategies (chaining vs open addressing), load factor threshold management, and amortized complexity bounds.",
                "overview": (
                    f"A **{topic}** is an associative data structure that stores key-value pairs, providing average-case $\\mathcal{{O}}(1)$ time complexity for insertions, deletions, and lookups. "
                    f"It transforms arbitrary key objects into integer bucket indices using a deterministic **hash function**.\n\n"
                    f"### Core Invariants & Mechanics\n"
                    fr"- **Deterministic Hash Mapping**: A given key $k$ always yields the identical hash code $h(k)$, mapped to a table slot via $h(k) \\pmod m$.\n"
                    fr"- **Collision Resolution**: Since the key space exceeds the bucket count (Pigeonhole Principle), collisions are resolved via **Separate Chaining** (linked list or balanced tree buckets) or **Open Addressing** (Linear Probing, Quadratic Probing, Double Hashing).\n"
                    fr"- **Load Factor Management**: The ratio $\\alpha = n / m$ (items divided by bucket capacity). When $\\alpha$ exceeds a threshold (typically 0.75), the table rehashes into a doubled bucket array to preserve $\\mathcal{{O}}(1)$ performance.\n\n"
                    f"### Systems Role\n"
                    f"Powers database indexes, compiler symbol tables, distributed caching systems (Redis, Memcached), cryptographic verifications, and associative dictionary types in Python, JavaScript, and Java."
                ),
                "theoretical_foundations": f"Pioneered by Hans Peter Luhn at IBM in 1953 using internal bucket chaining, and formally unified by Carter and Wegman in 1979 through Universal Hashing theory.",
                "core_formulations": (
                    r"- **Division Method Hash Function**: $$h(k) = k \pmod m$$\n"
                    r"- **Load Factor**: $$\alpha = \frac{n}{m} \quad (\text{ideal: } \alpha \le 0.75)$$\n"
                    r"- **Open Addressing Linear Probing**: $$h(k, i) = (h'(k) + i) \pmod m$$\n"
                    r"- **Time Complexity**: Average Case: $\mathcal{O}(1)$; Worst-Case (Collision Degradation): $\mathcal{O}(n)$."
                ),
                "did_you_know": f"Hans Peter Luhn conceived hashing at IBM in January 1953 while designing a mechanical chemical document search machine, inventing both hash lookup and separate chaining."
            }

        # 8. Graph & Graph Algorithms
        if any(k in t_low for k in ["graph", "dag", "shortest path", "dijkstra", "bfs", "dfs", "topological"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.8,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} requires topological abstraction, cyclic state detection, complexity trade-off analysis between adjacency representations, and mastery of traversal algorithms (BFS, DFS, Dijkstra).",
                "overview": (
                    f"A **{topic}** is a versatile non-linear data structure defined as a mathematical pair $G = (V, E)$, where $V$ is a set of **vertices** (or nodes) "
                    f"and $E$ is a set of **edges** (or arcs) representing pairwise connections between vertices. "
                    f"Graphs capture arbitrary network topologies without the hierarchical constraints of trees.\n\n"
                    f"### Core Invariants & Structural Taxonomies\n"
                    fr"- **Edge Directionality**: **Directed (Digraph)** where edges have arrows $(u \\to v)$, vs. **Undirected** where connections are symmetric.\n"
                    fr"- **Edge Weights**: Unweighted graphs treat all connections equally; weighted graphs assign real-valued costs, distances, or capacities to edges.\n"
                    fr"- **Acyclicity & DAGs**: A Directed Acyclic Graph (DAG) contains no directed cycles, enabling topological ordering essential for task scheduling and build systems.\n\n"
                    f"### Representation & Algorithmic Foundations\n"
                    fr"- **Adjacency Matrix**: $\\mathcal{{O}}(V^2)$ space with $\\mathcal{{O}}(1)$ edge verification, optimal for dense graphs.\n"
                    fr"- **Adjacency List**: $\\mathcal{{O}}(V + E)$ space with efficient neighbor iteration, the gold standard for sparse real-world networks.\n"
                    fr"- **Foundational Algorithms**: Breadth-First Search (shortest path in unweighted graphs), Depth-First Search (cycle detection, strongly connected components), Dijkstra (non-negative weighted shortest path), and Kruskal/Prim (Minimum Spanning Tree)."
                ),
                "theoretical_foundations": f"Graph theory originated in 1736 when Leonhard Euler solved the Seven Bridges of Königsberg problem, demonstrating that traversability depended on vertex degrees rather than physical geometry.",
                "core_formulations": (
                    r"- **Eulerian Degree Sum Invariant**: $$\sum_{v \in V} \text{deg}(v) = 2|E|$$\n"
                    r"- **Adjacency List Space Complexity**: $$\mathcal{O}(|V| + |E|)$$\n"
                    r"- **Dijkstra Shortest Path Bound**: $$\mathcal{O}((|V| + |E|) \log |V|) \quad \text{using Min-Heap}$$\n"
                    r"- **Dense Graph Edge Limit**: $$|E| \le \frac{|V|(|V|-1)}{2} \quad \text{(Undirected)}$$"
                ),
                "did_you_know": f"Leonhard Euler's 1736 paper on the Seven Bridges of Königsberg is universally regarded as the birth of both graph theory and the mathematical branch of topology."
            }

        # 9. Dynamic Programming
        if any(k in t_low for k in ["dynamic programming", "memoization", "tabulation", "optimal substructure"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 8.2,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} demands identifying optimal substructure, characterizing overlapping subproblem DAGs, formulating exact state transition recurrences, and proving space-time reduction.",
                "overview": (
                    f"**{topic}** is a powerful algorithmic paradigm for solving complex optimization problems by decomposing them into simpler overlapping subproblems, "
                    f"solving each subproblem exactly once, and storing their solutions to eliminate redundant exponential recalculations.\n\n"
                    f"### Two Mandatory Mathematical Prerequisites\n"
                    fr"- **Optimal Substructure**: An optimal solution to the overall problem contains within it optimal solutions to its component subproblems.\n"
                    fr"- **Overlapping Subproblems**: The recursive space contains repeated calls to the exact same subproblems, forming a Directed Acyclic Graph (DAG) rather than a tree.\n\n"
                    f"### Implementation Strategies\n"
                    fr"- **Top-Down with Memoization**: Retains the natural recursive call structure, caching results in a lookup table before returning.\n"
                    fr"- **Bottom-Up with Tabulation**: Iteratively fills an $N$-dimensional table starting from base cases up to the target state, eliminating call-stack overhead.\n\n"
                    f"### Algorithmic Impact\n"
                    f"Converts exponential $\\mathcal{{O}}(2^n)$ brute-force search spaces into deterministic polynomial $\\mathcal{{O}}(n \\cdot k)$ execution time, powering bioinformatics DNA sequence alignment (Needleman-Wunsch), Dijkstra shortest paths, Bellman-Ford, and resource knapsacks."
                ),
                "theoretical_foundations": f"Formulated by Richard Bellman in the 1950s at the RAND Corporation, encapsulating multi-stage decision processes governed by the Bellman Equation (Principle of Optimality).",
                "core_formulations": (
                    r"- **Bellman Principle of Optimality**: $$V(s) = \max_{a} \Big\{ R(s, a) + \gamma \sum_{s'} P(s' \mid s, a) V(s') \Big\}$$\n"
                    r"- **Recurrence Invariant**: $$\text{DP}[i] = \min / \max_{j < i} \big\{ \text{DP}[j] + \text{cost}(j, i) \big\}$$\n"
                    r"- **State Space Reduction**: $$\mathcal{O}(2^n) \implies \mathcal{O}(n \cdot W) \quad \text{(e.g., 0/1 Knapsack)}$$"
                ),
                "did_you_know": f"Richard Bellman deliberately chose the name 'Dynamic Programming' in the 1950s to conceal mathematical research from Secretary of Defense Charles Wilson, who notoriously hated the word 'research'."
            }

        # 10. Heap & Priority Queue
        if any(k in t_low for k in ["heap", "min heap", "max heap", "priority queue"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 6.6,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} tests complete binary tree array indexing rules ($2i+1, 2i+2$), heap-order invariant maintenance via bubble-up/down, and linear-time build-heap analysis.",
                "overview": (
                    f"A **{topic}** is a specialized tree-based data structure that satisfies the **Heap Property**. "
                    f"In a **Min-Heap**, the key of the parent node is always less than or equal to the keys of its children (root is minimum). "
                    f"In a **Max-Heap**, the key of the parent is always greater than or equal to its children (root is maximum).\n\n"
                    f"### Core Invariants & Compact Array Packing\n"
                    fr"- **Complete Binary Tree Invariant**: All levels are filled completely except possibly the lowest, which is filled from left to right. This guarantees minimum possible height $h = \\lfloor\\log_2 n\\rfloor$.\n"
                    fr"- **Zero-Pointer Contiguous Array Packing**: Rather than storing child pointers, a heap is mapped directly into an array: root at index 0, left child at $2i + 1$, right child at $2i + 2$, and parent at $\\lfloor(i-1)/2\\rfloor$.\n"
                    fr"- **Constant-Time Peak ($\\mathcal{{O}}(1)$)**: The extreme element (minimum or maximum) is always located at root index 0."
                ),
                "theoretical_foundations": fr"Invented by J.W.J. Williams in 1964 as part of the HeapSort algorithm, providing the fastest comparison-based sort with optimal in-place $O(n \log n)$ worst-case guarantees.",
                "core_formulations": (
                    r"- **Parent-Child Array Indices**: $$\text{Left}(i) = 2i + 1, \quad \text{Right}(i) = 2i + 2, \quad \text{Parent}(i) = \lfloor (i - 1)/2 \rfloor$$\n"
                    r"- **Min-Heap Invariant**: $$\forall i > 0, \, A[\text{Parent}(i)] \le A[i]$$\n"
                    r"- **Time Complexity**: Find-Min/Max: $\mathcal{O}(1)$; Insert: $\mathcal{O}(\log n)$; Extract-Min/Max: $\mathcal{O}(\log n)$; Build-Heap: $\mathcal{O}(n)$."
                ),
                "did_you_know": fr"While inserting $n$ elements into a heap one by one takes $O(n \log n)$ time, Robert W. Floyd published a famous 'sift-down' method in 1964 that constructs a complete heap in linear $O(n)$ time."
            }

        # 11. Binary Search
        if any(k in t_low for k in ["binary search", "bsearch", "divide and conquer search"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 5.2,
                "difficulty_level": "Intermediate",
                "ai_evaluation": fr"{topic} demands precise boundary condition validation ($L \le R$ vs $L < R$), overflow-safe midpoint calculation, and monotonic predicate search formulation.",
                "overview": (
                    f"**{topic}** is an efficient divide-and-conquer search algorithm that finds the position of a target value within a **monotonically sorted** sequence. "
                    f"By comparing the target value to the middle element of the active range, it eliminates exactly half of the remaining search space in each iteration.\n\n"
                    f"### Core Invariants & Mechanics\n"
                    fr"- **Monotonicity Requirement**: The underlying dataset or mathematical function must be sorted or satisfy a monotonic predicate ($P(x) \\implies P(x+1)$).\n"
                    fr"- **Logarithmic Reduction**: With each comparison, the search interval $[L, R]$ is reduced by 50%, guaranteeing at most $\\lfloor\\log_2 n\\rfloor + 1$ comparisons.\n"
                    fr"- **Overflow-Safe Midpoint**: Formulated as $M = L + \\lfloor(R - L)/2\\rfloor$ to prevent integer arithmetic overflow in computer hardware."
                ),
                "theoretical_foundations": f"First published by John Mauchly in 1946 on the EDVAC, binary search is the archetypal example of divide-and-conquer logarithmic reduction.",
                "core_formulations": (
                    r"- **Midpoint Calculation**: $$M = L + \left\lfloor \frac{R - L}{2} \right\rfloor$$\n"
                    r"- **Recurrence Relation**: $$T(n) = T(n/2) + \mathcal{O}(1) \implies T(n) = \Theta(\log n)$$\n"
                    r"- **Maximum Comparisons Bound**: $$C_{\text{max}} = \lfloor \log_2 n \rfloor + 1$$"
                ),
                "did_you_know": f"Although binary search was first mentioned in 1946, the first completely bug-free binary search implementation for arbitrary array sizes was only published by D.H. Lehmer in 1960. In 2006, Joshua Bloch revealed that the binary search in Java's standard library contained an integer overflow bug that had gone unnoticed for nine years!"
            }

        # 12. Operating System & Concurrency
        if any(k in t_low for k in ["operating system", "process", "thread", "virtual memory", "paging", "deadlock", "mutex", "semaphore"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.8,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} requires understanding kernel vs user privilege modes, memory hierarchy management, hardware-software synchronization, and resource contention state models.",
                "overview": (
                    f"In computer engineering, **{topic}** represents a foundational systems architecture concept responsible for managing hardware resources, "
                    f"enforcing memory isolation, and providing a deterministic execution abstraction for multi-threaded and multi-process software.\n\n"
                    f"### Core Architectural Invariants\n"
                    fr"- **Hardware Protection Rings**: Enforces separation between unprivileged User Mode (Ring 3) and privileged Kernel Mode (Ring 0) via CPU trap gates and system calls.\n"
                    fr"- **Resource Virtualization**: Converts raw physical hardware (CPU cores, RAM blocks, network cards) into clean, protected virtual abstractions (processes, virtual address spaces, sockets).\n"
                    fr"- **Concurrency & Race Freedom**: Enforces mutual exclusion across critical sections using hardware atomic primitives (Compare-And-Swap / CAS), semaphores, and spinlocks."
                ),
                "theoretical_foundations": f"Formally established through computer system architecture models pioneered by Edsger Dijkstra (multiprogramming THE multiprogramming system, 1968) and E.G. Coffman Jr. (deadlock characterization, 1971).",
                "core_formulations": (
                    r"- **Four Coffman Deadlock Conditions**: $$\text{Mutual Exclusion} \land \text{Hold \& Wait} \land \text{No Preemption} \land \text{Circular Wait}$$\n"
                    r"- **Virtual Memory Translation**: $$\text{Physical Address} = (\text{Page Frame} \times \text{Page Size}) + \text{Offset}$$\n"
                    r"- **Amdahl Speedup Bound**: $$S(s) = \frac{1}{(1 - p) + \frac{p}{s}}$$"
                ),
                "did_you_know": f"Edsger Dijkstra invented the semaphore in 1965 while designing the THE multiprogramming system at Eindhoven University of Technology, naming the two operations 'P' (from Dutch 'proberen', to test) and 'V' ('verhogen', to increment)."
            }

        # 13. Database & SQL
        if any(k in t_low for k in ["database", "dbms", "sql", "normalization", "acid", "relational"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.2,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} tests relational algebra formalisms, ACID transactional guarantee boundaries, schema normalization functional dependencies, and query indexing optimizations.",
                "overview": (
                    f"**{topic}** is a core discipline in data engineering and computer science dedicated to the systematic organization, storage, retrieval, "
                    f"and transactional integrity of structured data in multi-user environments.\n\n"
                    f"### Core Invariants & Principles\n"
                    fr"- **ACID Guarantees**: Enforces **Atomicity** (all-or-nothing execution), **Consistency** (state invariant validity), **Isolation** (concurrency serializability), and **Durability** (crash survival via Write-Ahead Logging / WAL).\n"
                    fr"- **Relational Calculus & Normalization**: Eliminates data redundancy and anomaly vulnerabilities through formal functional dependencies (1NF, 2NF, 3NF, BCNF).\n"
                    fr"- **Indexing & Storage Structures**: Employs self-balancing B+ Trees and LSM Trees (Log-Structured Merge-trees) to minimize mechanical disk I/O and SSD write amplification."
                ),
                "theoretical_foundations": f"Introduced by Edgar F. Codd in his landmark 1970 paper 'A Relational Model of Data for Large Shared Data Banks', establishing relational algebra as the mathematical foundation for modern databases.",
                "core_formulations": (
                    r"- **ACID Transaction Rule**: $$\text{State}_{t+1} = \text{Commit}(T) \implies \text{Valid}(\text{State}_{t+1})$$\n"
                    r"- **B+ Tree Node Fanout Bound**: $$\lceil M/2 \rceil \le \text{keys per node} \le M - 1$$\n"
                    r"- **Functional Dependency**: $$X \to Y \iff \forall t_1, t_2 \, (t_1[X] = t_2[X] \implies t_1[Y] = t_2[Y])$$"
                ),
                "did_you_know": f"E.F. Codd's relational database model was initially resisted by IBM executives because they were making enormous profits selling IMS (hierarchical database) mainframes, allowing Larry Ellison to read Codd's paper and build Oracle before IBM could market DB2!"
            }

        # 14. Computer Networks
        if any(k in t_low for k in ["computer network", "tcp", "udp", "osi", "networking", "socket", "dns", "http"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.0,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} requires protocol state machine analysis, packet encapsulation understanding, and trade-off evaluation between reliable stream transmission (TCP) and low-latency datagrams (UDP).",
                "overview": (
                    f"In computer science and telecommunications, **{topic}** encompasses the protocols, architectural abstractions, and hardware mediums "
                    f"that enable autonomous digital computers to reliably exchange data packets across distributed geographic topologies.\n\n"
                    f"### Core Invariants & Layered Abstractions\n"
                    fr"- **Protocol Layering**: Standardized under the OSI 7-Layer and TCP/IP 4-Layer models, where each layer encapsulates headers without exposing lower hardware implementations.\n"
                    fr"- **End-to-End Principle**: Operational state (e.g. reliability, sequence numbering, congestion control) is maintained at end hosts rather than inside intermediate packet switches or routers.\n"
                    fr"- **Reliability vs. Latency**: TCP provides connection-oriented, flow-controlled, byte-stream reliability via 3-way handshakes and sliding window acknowledgments; UDP provides connectionless, low-latency datagrams."
                ),
                "theoretical_foundations": f"Formalized by Vint Cerf and Bob Kahn in their seminal 1974 paper 'A Protocol for Packet Network Intercommunication', giving birth to the modern Internet protocol suite (TCP/IP).",
                "core_formulations": (
                    r"- **TCP Throughput (Mathis Formula)**: $$\text{Rate} \le \frac{\text{MSS}}{\text{RTT}} \times \frac{1}{\sqrt{p}}$$\n"
                    r"- **Bandwidth-Delay Product (BDP)**: $$\text{BDP} = \text{Bandwidth} \times \text{RTT}$$\n"
                    r"- **Little's Law (Queueing)**: $$L = \lambda W$$"
                ),
                "did_you_know": f"Vint Cerf and Bob Kahn sketched the earliest architecture of TCP on the back of an envelope in a hotel lobby in 1973, designing an internetwork that could survive nuclear interruptions without centralized coordination."
            }

        # 15. Physics
        if any(k in t_low for k in ["newton", "motion", "thermodynamics", "physics", "electromagnetism", "quantum", "gravity"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.6,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} requires rigorous calculus-based vector analysis, conservation law formulations, and dynamic equilibrium models.",
                "overview": (
                    f"**{topic}** is a foundational principle in physics that governs physical interactions, dynamic forces, and energy transfers. "
                    f"It establishes the deterministic laws by which physical bodies, fields, and states evolve through space and time.\n\n"
                    f"### Core Governing Laws & Invariants\n"
                    fr"- **Conservation Invariants**: Energy, momentum, and charge are strictly conserved across closed physical systems.\n"
                    fr"- **Deterministic Equations of State**: Relates applied force, mass, and acceleration or thermal state coordinates through differential equations.\n"
                    fr"- **Equilibrium & Potential Gradients**: Systems naturally evolve along paths minimizing potential energy and maximizing thermodynamic entropy."
                ),
                "theoretical_foundations": f"Formulated through classical Newtonian mechanics, Maxwellian field equations, and Lagrangian/Hamiltonian dynamics.",
                "core_formulations": (
                    r"- **Newton's Second Law**: $$\mathbf{F}_{\text{net}} = \frac{d\mathbf{p}}{dt} = m\mathbf{a}$$\n"
                    r"- **Conservation of Mechanical Energy**: $$E_{\text{total}} = K + U = \frac{1}{2}mv^2 + V(r) = \text{constant}$$\n"
                    r"- **Work-Energy Theorem**: $$W_{\text{net}} = \Delta K = \int \mathbf{F} \cdot d\mathbf{r}$$"
                ),
                "did_you_know": f"Isaac Newton formulated his three laws of motion and universal gravitation in 1665-1666 while Cambridge University was closed due to the Great Plague of London—a period Newton famously referred to as his 'annus mirabilis' (year of wonders)."
            }

        # 16. Mathematics
        if any(k in t_low for k in ["calculus", "linear algebra", "matrix", "eigen", "derivative", "integral", "probability"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.8,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} requires formal axiomatic reasoning, continuous mapping derivations, and coordinate-free algebraic or analytic formulations.",
                "overview": (
                    f"**{topic}** is a foundational discipline of mathematics that provides rigorous analytical tools for modeling continuous change, "
                    f"multi-dimensional transformations, and geometric invariants across abstract vector spaces.\n\n"
                    f"### Core Analytical Invariants\n"
                    fr"- **Continuity & Convergence**: Governed by epsilon-delta limits, sequence bounds, and completeness axioms.\n"
                    fr"- **Linearity & Mapping**: Preserves vector addition and scalar multiplication under linear operator transformations: $T(u + v) = T(u) + T(v)$.\n"
                    fr"- **Fundamental Duality**: Derivatives capture instantaneous rates of change; integrals compute cumulative area, unified by the Fundamental Theorem of Calculus."
                ),
                "theoretical_foundations": f"Constructed on real analysis axioms, vector space theory, and functional analysis formalized by Newton, Leibniz, Cauchy, and Hilbert.",
                "core_formulations": (
                    r"- **Fundamental Theorem of Calculus**: $$\int_a^b f'(x)\,dx = f(b) - f(a)$$\n"
                    r"- **Eigenvalue Characteristic Equation**: $$\det(\mathbf{A} - \lambda \mathbf{I}) = 0$$\n"
                    r"- **Taylor Series Expansion**: $$f(x) = \sum_{n=0}^\infty \frac{f^{(n)}(a)}{n!}(x - a)^n$$"
                ),
                "did_you_know": f"Calculus was invented independently in the late 17th century by both Isaac Newton in England and Gottfried Wilhelm Leibniz in Germany, leading to a fierce international priority dispute that split European mathematicians for decades."
            }

        # 17. Law & Jurisprudence
        if any(k in t_low for k in ["law", "damnum sine injuria", "tort", "constitutional", "jurisprudence"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 6.9,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} demands precise legal doctrine interpretation, statutory classification, and precedent analysis.",
                "overview": (
                    f"**{topic}** is an established legal doctrine defining substantive rights, civil liabilities, and procedural fairness within common law "
                    f"and statutory jurisprudence.\n\n"
                    f"### Core Legal Principles\n"
                    fr"- **Separation of Harm from Right Violation**: Distinguishes between actionable legal infringements (*injuria*) and non-actionable incidental business/economic damages (*damnum*).\n"
                    fr"- **Natural Justice**: Guarantees procedural fairness: *audi alteram partem* (hear the other side) and *nemo judex in causa sua* (no one can be judge in their own cause).\n"
                    fr"- **Judicial Precedent (*Stare Decisis*)**: Ensures consistency by binding lower courts to prior authoritative rulings."
                ),
                "theoretical_foundations": f"Derived from Roman legal maxims, English common law tort rulings, and modern constitutional due process.",
                "core_formulations": (
                    r"- **Core Legal Invariant**: $$\text{Damnum} \neq \text{Injuria} \implies \text{No Cause of Action}$$\n"
                    r"- **Tort Liability Rule**: $$\text{Liability} = \text{Duty of Care} + \text{Breach} + \text{Causation} + \text{Actionable Harm}$$\n"
                    r"- **Natural Justice Maxim**: $$\textit{Audi alteram partem} \quad \text{(Listen to both parties equally)}$$"
                ),
                "did_you_know": f"The famous landmark case for Damnum Sine Injuria is the Gloucester Grammar School Case of 1410, where a schoolmaster sued a rival who opened a competing school that forced tuition fees down from 40 pence to 12 pence. The court dismissed the lawsuit, ruling that honest commercial competition harms finances but violates no legal right."
            }

        # 18. Default Smart Adaptive Context Synthesizer (for ANY other academic topic)
        return {
            "topic": topic,
            "category": detected_domain,
            "difficulty_score": 7.2,
            "difficulty_level": "Intermediate" if any(k in t_low for k in ["intro", "basic", "linear", "search", "fundamentals"]) else "Advanced",
            "ai_evaluation": f"{topic} demands precise analytical reasoning, formal boundary condition validation, and comprehensive structural model evaluation in {detected_domain}.",
            "overview": (
                f"**{topic}** is an essential academic subject in **{detected_domain}**, establishing the structural principles, "
                f"operational logic, and formal methodologies required for rigorous problem solving and engineering implementation.\n\n"
                f"### Core Foundations & Invariants\n"
                fr"- **Governing Principles**: Operates under formal state constraints and conservation laws established by higher curriculum standards.\n"
                fr"- **Systematic Processing**: Provides deterministic execution guarantees, minimizing state error and computational overhead.\n"
                fr"- **Interdisciplinary Relevance**: Connects foundational analytical theory with practical systems engineering, testing, and optimization.\n\n"
                f"### Structural & Operational Classifications\n"
                fr"- **Foundational Mechanics**: Establishes structural baselines ensuring consistent behavioral guarantees across varied system environments.\n"
                fr"- **Optimization Vectors**: Identifies resource trade-offs, enabling high efficiency, scalability, and predictable performance."
            ),
            "theoretical_foundations": f"Theoretical study of {topic} is rooted in curriculum standards of {detected_domain}, establishing correctness through formal proofs, state transitions, and empirical verification.",
            "core_formulations": r"- **State Transformation**: $$S_{t+1} = \mathcal{F}(S_t, U_t)$$\n- **Asymptotic Bound**: $$\mathcal{O}(n \log n) \quad \text{or domain-standard analytical limit}$$",
            "did_you_know": f"Foundational concepts in {topic} continue to anchor core questions across university examinations and professional technical interviews."
        }
