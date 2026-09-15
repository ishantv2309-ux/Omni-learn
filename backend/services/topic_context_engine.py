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
    def build_topic_context(clean_q: str, detected_domain: str, lang: str = "english") -> dict:
        data = TopicContextEngine._build_topic_context_raw(clean_q, detected_domain, lang=lang)
        # Normalize newlines for markdown rendering
        for k in ["overview", "theoretical_foundations", "core_formulations", "detailed_breakdown"]:
            if k in data and isinstance(data[k], str):
                data[k] = data[k].replace(chr(92) + "n", chr(10))
        data["diagram"] = TopicContextEngine.build_topic_diagram(clean_q, data.get("topic", clean_q), detected_domain)
        return data

    @staticmethod
    def _build_topic_context_raw(clean_q: str, detected_domain: str, lang: str = "english") -> dict:
        if (lang or "").strip().lower() == "hinglish":
            return TopicContextEngine._build_topic_context_hinglish(clean_q, detected_domain)
        topic = clean_title_casing(clean_q.strip())
        t_low = clean_q.lower().strip()

        # 0. Booth's Multiplication Algorithm (Computer Architecture / COA Exam Standard)
        if any(k in t_low for k in ["booth", "booths", "booth's"]):
            return {
                "topic": "Booth's Multiplication Algorithm",
                "category": detected_domain,
                "difficulty_score": 8.2,
                "difficulty_level": "Advanced",
                "ai_evaluation": "Booth's Algorithm is a high-frequency B.Tech CSE and GATE Computer Organization (COA) topic. It tests 2's complement signed arithmetic, hardware datapath register manipulation (AC, QR, BR, Qn+1, SC), Arithmetic Shift Right (ASR) sign preservation, and cycle-by-cycle state transition tracing.",
                "overview": (
                    "**Booth's Multiplication Algorithm** is a hardware-oriented multiplication algorithm that multiplies two signed binary integers in **Two's Complement** notation. "
                    "Invented by Andrew Donald Booth in 1950, it treats contiguous sequences of 1s in the multiplier as a difference of two powers of two: "
                    "$2^{k+m} - 2^k$. Instead of executing an addition for every individual 1 bit, it executes only **one addition at the start of a string of 1s and one subtraction at the end**, "
                    "skipping all intermediate additions via simple arithmetic shifts.\n\n"
                    "### Core Structural Invariants\n"
                    "- **Two's Complement Sign Preservation**: Operates directly on signed negative and positive numbers without requiring sign-magnitude conversion or correction cycles.\n"
                    "- **String Property Reduction**: Replaces a block of $m$ consecutive 1s ($2^{k+m} - 2^k$) with exactly one subtraction ($10$) and one addition ($01$), achieving sub-linear operations for grouped bits.\n"
                    "- **Constant Shift Guarantee**: Exactly $n$ Arithmetic Shift Right (`ASR`) operations are executed for $n$-bit operands, matching the sequence counter ($SC = n \\to 0$).\n"
                    "- **Arithmetic Sign Extension**: In every shift, the Most Significant Bit (MSB) of Accumulator `AC` ($AC[n-1]$) is preserved and copied into itself, guaranteeing mathematically sound arithmetic division by 2."
                ),
                "theoretical_foundations": (
                    "### Hardware Datapath & Register Architecture\n"
                    "The hardware implementation requires a dedicated arithmetic datapath consisting of:\n"
                    "- **AC (Accumulator Register)**: $n$-bit register initialized to $0000_2$. Holds intermediate partial sums and upper half of the final product.\n"
                    "- **QR (Multiplier Register)**: $n$-bit register holding the multiplier $Q$. Holds lower half of the final product upon completion.\n"
                    "- **BR (Multiplicand Register)**: $n$-bit register holding the multiplicand $M$. Remains constant throughout multiplication.\n"
                    "- **Qn+1 (Sign Bit Flip-Flop)**: 1-bit flip-flop appended to the right of $QR[0]$ ($Q_0$). Initialized to $0$.\n"
                    "- **SC (Sequence Counter)**: Initialized to word size $n$. Decremented by 1 after each arithmetic shift until $SC = 0$.\n"
                    "- **n-bit Parallel Adder/Subtractor ALU**: Executes $AC \\leftarrow AC + BR$ or $AC \\leftarrow AC - BR$ ($AC + \\overline{BR} + 1$) based on control logic."
                ),
                "core_formulations": (
                    "- **Bit-Pair Inspection Logic ($Q_0 Q_{n+1}$)**:\n"
                    "  * `00`: No arithmetic operation. Perform **Arithmetic Shift Right (ASR)** on $[AC, QR, Q_{n+1}]$, decrement $SC \\leftarrow SC - 1$.\n"
                    "  * `01`: $AC \\leftarrow AC + BR$, then perform **Arithmetic Shift Right (ASR)** on $[AC, QR, Q_{n+1}]$, decrement $SC \\leftarrow SC - 1$.\n"
                    "  * `10`: $AC \\leftarrow AC - BR$ ($AC + \\overline{BR} + 1$), then perform **Arithmetic Shift Right (ASR)** on $[AC, QR, Q_{n+1}]$, decrement $SC \\leftarrow SC - 1$.\n"
                    "  * `11`: No arithmetic operation. Perform **Arithmetic Shift Right (ASR)** on $[AC, QR, Q_{n+1}]$, decrement $SC \\leftarrow SC - 1$.\n"
                    "- **Arithmetic Shift Right Invariant**: $$ASR([AC, QR, Q_{n+1}]) \\implies Q_{n+1} \\leftarrow QR[0], \\; QR \\leftarrow [AC[0], QR[n-1..1]], \\; AC \\leftarrow [AC[n-1], AC[n-1..1]]$$\n"
                    "- **Computational Complexity**: Cycle count is strictly $\\Theta(n)$ where $n$ is word bit-width. Add/Sub operations: Best case $0$ (for $Q=0$ or $Q=-1$), Average case $\\sim n/2$, Worst case $n$ (alternating $01010101_2$ pattern)."
                ),
                "detailed_breakdown": (
                    "### 1. Core Concept & Invariants\n"
                    "Booth's Multiplication Algorithm multiplies two signed binary integers in 2's complement representation. "
                    "It exploits the identity that a block of $m$ consecutive 1s has numerical value $\\sum_{i=k}^{k+m-1} 2^i = 2^{k+m} - 2^k$. "
                    "Consequently, $m$ individual additions are compressed into a single subtraction ($10$) at the start of the sequence and a single addition ($01$) at the end.\n\n"
                    "### 2. Hardware / Memory Model (Registers & Architecture)\n"
                    "- **Accumulator (AC)**: $n$-bit register, initialized to all zeros ($0000_2$).\n"
                    "- **Multiplier Register (QR)**: $n$-bit register holding the multiplier $Q$.\n"
                    "- **Multiplicand Register (BR)**: $n$-bit register holding the multiplicand $M$.\n"
                    "- **Extra Bit ($Q_{n+1}$)**: 1-bit flip-flop initialized to $0$ immediately to the right of $QR[0]$.\n"
                    "- **Sequence Counter (SC)**: Initialized to $n$ ($4$ for 4-bit numbers).\n"
                    "- **ALU Datapath**: $n$-bit adder with 2's complement inverter enabling $AC + \\overline{BR} + 1$.\n\n"
                    "### 3. Step-by-Step Algorithm & State Transitions\n"
                    "1. Initialize $AC = 0$, $Q_{n+1} = 0$, $SC = n$, $BR = M$, $QR = Q$.\n"
                    "2. Examine bit pair $(Q_0, Q_{n+1})$:\n"
                    "   - If `01`: $AC \\leftarrow AC + BR$. Then Arithmetic Shift Right $[AC, QR, Q_{n+1}]$.\n"
                    "   - If `10`: $AC \\leftarrow AC - BR$. Then Arithmetic Shift Right $[AC, QR, Q_{n+1}]$.\n"
                    "   - If `00` or `11`: Arithmetic Shift Right $[AC, QR, Q_{n+1}]$ directly (no addition/subtraction).\n"
                    "3. Decrement $SC \\leftarrow SC - 1$.\n"
                    "4. If $SC > 0$, repeat from Step 2. When $SC = 0$, stop. Product is stored in $[AC, QR]$.\n\n"
                    "### 4. Worked Numerical Example & Complete Trace Table\n"
                    "**Problem**: Multiply Multiplicand $M = -5$ ($1011_2$ in 4-bit 2's complement) by Multiplier $Q = +7$ ($0111_2$).\n"
                    "- $BR = 1011_2$ ($-5$), $-BR = 0101_2$ ($+5$). $n = 4$, so $SC = 4$.\n\n"
                    "| Cycle / Step | $Q_0 Q_{n+1}$ | Operation | AC | QR | $Q_{n+1}$ | SC | Explanation |\n"
                    "|---|---|---|---|---|---|---|---|\n"
                    "| **Init** | - | Initial Values | 0000 | 0111 | 0 | 4 | $AC=0, QR=0111, Q_{n+1}=0, SC=4$ |\n"
                    "| **Cycle 1** | **10** | $AC \\leftarrow AC - BR$ ($0000 + 0101$) | 0101 | 0111 | 0 | 4 | Bit pair $10 \\implies$ Subtract $BR$ (Add $-BR$) |\n"
                    "| | | Arithmetic Shift Right (ASR) | **0010** | **1011** | **1** | **3** | Shift $[AC, QR, Q_{n+1}]$; MSB $0$ retained in $AC$ |\n"
                    "| **Cycle 2** | **11** | Shift only | **0001** | **0101** | **1** | **2** | Bit pair $11 \\implies$ Shift only, decrement SC |\n"
                    "| **Cycle 3** | **11** | Shift only | **0000** | **1010** | **1** | **1** | Bit pair $11 \\implies$ Shift only, decrement SC |\n"
                    "| **Cycle 4** | **01** | $AC \\leftarrow AC + BR$ ($0000 + 1011$) | 1011 | 1010 | 1 | 1 | Bit pair $01 \\implies$ Add $BR$ ($1011$) |\n"
                    "| | | Arithmetic Shift Right (ASR) | **1101** | **1101** | **0** | **0** | Shift $[AC, QR, Q_{n+1}]$; MSB $1$ retained in $AC$ |\n\n"
                    "**Result Verification**:\n"
                    "- Final register content in $[AC, QR] = 11011101_2$ (8-bit signed integer).\n"
                    "- Evaluating 2's complement: $-2^7 + 2^6 + 2^4 + 2^3 + 2^2 + 2^0 = -128 + 64 + 16 + 8 + 4 + 1 = -35_{10}$.\n"
                    "- Expected result: $(-5) \\times (+7) = -35_{10}$. **Computation is 100% verified and correct!**\n\n"
                    "### 5. Advantages, Trade-offs & Comparisons\n"
                    "- **Uniform Signed Handling**: Multiplies positive and negative numbers identically without sign pre-processing or post-complementing.\n"
                    "- **Speedup on Clustered 1s**: Strings of consecutive 1s require only 2 operations ($1$ add, $1$ sub), halving clock cycles for dense 1s.\n"
                    "- **Worst-Case Trade-off**: If the multiplier contains alternating bits (`01010101...`), Booth's algorithm requires $n$ additions/subtractions, offering no speed advantage over standard shift-and-add.\n\n"
                    "### 6. Common University Exam / GATE Questions\n"
                    "- **Q1 (GATE CSE)**: How many additions and subtractions are performed by Booth's algorithm when multiplying a multiplicand by $Q = 00111100_2$?\n"
                    "  *Answer*: Inspecting transitions from right to left ($Q_0 Q_{n+1}$): $00 \\to 0$ ops, $10 \\to 1$ subtract, $11 \\to 0$ ops, $01 \\to 1$ add. Total: **1 subtraction and 1 addition** (only 2 arithmetic operations instead of 4).\n"
                    "- **Q2 (University Semester Exam)**: Why is Arithmetic Shift Right (ASR) essential in Booth's algorithm instead of Logical Shift Right?\n"
                    "  *Answer*: ASR replicates the sign bit ($AC[n-1] \\to AC[n-1]$), which is mandatory to preserve the sign and magnitude of negative numbers in 2's complement division by 2.\n"
                    "- **Q3 (GATE CSE)**: What is the worst-case multiplier pattern for an $n$-bit Booth multiplier?\n"
                    "  *Answer*: Alternating bit patterns such as $01010101_2$ or $10101010_2$, which force an addition or subtraction on every single cycle ($n$ operations)."
                ),
                "did_you_know": "Andrew Donald Booth invented Booth's algorithm in 1950 while doing research on crystallographic structure calculations at Birkbeck College, London, because mechanical shifters were substantially faster than adders."
            }

        # 0B. LRU Page Replacement Algorithm (Operating Systems Exam Standard)
        if any(k in t_low for k in ["lru", "page replacement", "least recently used"]):
            return {
                "topic": "LRU Page Replacement Algorithm",
                "category": detected_domain,
                "difficulty_score": 7.8,
                "difficulty_level": "Advanced",
                "ai_evaluation": "LRU is an essential OS virtual memory topic in university exams and GATE. It requires understanding temporal locality, stack algorithms, Belady's Anomaly immunity, and reference string trace tables.",
                "overview": (
                    "**LRU (Least Recently Used) Page Replacement Algorithm** is a memory management algorithm used by operating systems to handle **page faults** in virtual memory. "
                    "When a page fault occurs and all physical page frames in RAM are occupied, LRU identifies and evicts the page that has **not been referenced for the longest period of time**. "
                    "It is grounded in the **Principle of Temporal Locality**—the empirical observation that memory locations accessed recently are likely to be accessed again in the near future.\n\n"
                    "### Core Structural Invariants\n"
                    "- **Stack Algorithm Property**: The set of pages in memory for $m$ frames is always a strict subset of the pages in memory for $m+1$ frames: $M(m, t) \\subseteq M(m+1, t)$.\n"
                    "- **Immunity to Belady's Anomaly**: Because LRU is a formal stack algorithm, increasing the number of allocated page frames **never increases the number of page faults** (unlike FIFO).\n"
                    "- **Optimal Proximity Approximation**: LRU approximates the theoretically optimal algorithm (Belady's MIN/OPT) by using past history as a proxy for future memory access patterns."
                ),
                "theoretical_foundations": (
                    "### Architectural & Data Structure Models\n"
                    "LRU requires tracking recency of access for every active page frame:\n"
                    "- **Doubly Linked List + Hash Map (Software Cache)**: A doubly linked list stores pages ordered by access recency (Head = MRU, Tail = LRU). A hash map provides $\\mathcal{O}(1)$ pointer lookups. Node eviction and promotion take $\\mathcal{O}(1)$ time.\n"
                    "- **Hardware Counter / Clock Registers**: CPU maintains an internal clock/counter register incremented on every memory reference. Each page table entry stores the timestamp of its last access.\n"
                    "- **Hardware Matrix (n x n Flip-Flop Array)**: When page $k$ is referenced, row $k$ is set to 1s and column $k$ is set to 0s. The row with the lowest binary value corresponds to the LRU page."
                ),
                "core_formulations": (
                    "- **Page Fault Rate**: $$P = \\frac{\\text{Total Page Faults}}{\\text{Total Memory References}}$$\n"
                    "- **Hit Ratio**: $$H = 1 - P = \\frac{\\text{Cache Hits}}{\\text{Total Memory References}}$$\n"
                    "- **Stack Property Formal Definition**: $$\\forall t, \\; S_t(n) \\subseteq S_t(n+1) \\implies \\text{Belady\\'s Anomaly is impossible}$$\n"
                    "- **Effective Memory Access Time (EMAT)**: $$EMAT = (1 - P) \\times t_m + P \\times t_s \\quad \\text{where } t_m \\text{ is RAM latency and } t_s \\text{ is page fault service time}$$"
                ),
                "detailed_breakdown": (
                    "### 1. Core Concept & Invariants\n"
                    "LRU replaces the page that has stayed unused for the longest interval. By temporal locality, pages accessed recently will be needed again shortly. "
                    "LRU belongs to the class of **stack algorithms**, mathematically guaranteeing that more memory frames never cause more page faults.\n\n"
                    "### 2. Hardware / Memory Model (Registers & Architecture)\n"
                    "- **Page Table Entry (PTE)**: Contains Valid/Invalid bit, Dirty/Modified bit, and Reference timestamp.\n"
                    "- **Physical Frames**: Allocation of $k$ frames in physical RAM.\n"
                    "- **LRU Stack**: Doubly linked list where the most recently used page is moved to the top and the least recently used page sits at the bottom.\n\n"
                    "### 3. Step-by-Step Algorithm & State Transitions\n"
                    "1. When CPU references page $p$, check if $p$ exists in physical frame buffer (Cache Hit).\n"
                    "2. If Hit: update $p$'s recency to Most Recently Used (MRU). Zero page fault.\n"
                    "3. If Miss (Page Fault):\n"
                    "   - If an empty frame exists: load $p$ into the empty slot and mark as MRU.\n"
                    "   - If all frames are full: evict the page at the LRU position. Write back to disk if Dirty bit is set. Load page $p$ into the freed frame and mark as MRU.\n\n"
                    "### 4. Worked Numerical Example & Complete Trace Table\n"
                    "**Problem**: Reference String: `7, 0, 1, 2, 0, 3, 0, 4, 2, 3` with **3 Page Frames** (initially empty).\n\n"
                    "| Ref Step | Page | Frame 1 | Frame 2 | Frame 3 | Hit / Miss | Evicted Page | Explanation |\n"
                    "|---|---|---|---|---|---|---|---|\n"
                    "| 1 | **7** | 7 | - | - | **Miss (Fault 1)** | None | Frame 1 loaded with 7 |\n"
                    "| 2 | **0** | 7 | 0 | - | **Miss (Fault 2)** | None | Frame 2 loaded with 0 |\n"
                    "| 3 | **1** | 7 | 0 | 1 | **Miss (Fault 3)** | None | Frame 3 loaded with 1 |\n"
                    "| 4 | **2** | 2 | 0 | 1 | **Miss (Fault 4)** | **7** | 7 was LRU (oldest referenced); replaced by 2 |\n"
                    "| 5 | **0** | 2 | 0 | 1 | **Hit** | None | 0 is in memory; recency updated to MRU |\n"
                    "| 6 | **3** | 2 | 0 | 3 | **Miss (Fault 5)** | **1** | 1 was LRU (since 0 was just referenced); replaced by 3 |\n"
                    "| 7 | **0** | 2 | 0 | 3 | **Hit** | None | 0 is in memory; recency updated to MRU |\n"
                    "| 8 | **4** | 4 | 0 | 3 | **Miss (Fault 6)** | **2** | 2 was LRU (0 & 3 referenced recently); replaced by 4 |\n"
                    "| 9 | **2** | 4 | 0 | 2 | **Miss (Fault 7)** | **3** | 3 was LRU; replaced by 2 |\n"
                    "| 10 | **3** | 3 | 0 | 2 | **Miss (Fault 8)** | **4** | 4 was LRU; replaced by 3 |\n\n"
                    "**Performance Summary**:\n"
                    "- Total Memory References = $10$\n"
                    "- Total Page Faults = **8**\n"
                    "- Total Hits = **2**\n"
                    "- Hit Ratio = $2 / 10 = 20\\%$, Page Fault Frequency = $8 / 10 = 80\\%$.\n\n"
                    "### 5. Advantages, Trade-offs & Comparisons\n"
                    "- **Immunity to Belady's Anomaly**: Stack algorithm property guarantees adding frames will never increase faults.\n"
                    "- **Superior to FIFO**: Exploits empirical access locality, outperforming First-In-First-Out on realistic workloads.\n"
                    "- **Hardware Overhead**: Pure LRU requires expensive hardware counters or pointer updating on *every* memory read/write. Consequently, modern OSes (Linux, Windows) use LRU approximations like **Clock (Second Chance) Algorithm**.\n\n"
                    "### 6. Common University Exam / GATE Questions\n"
                    "- **Q1 (GATE CSE)**: Which of the following page replacement algorithms suffers from Belady's Anomaly? (A) LRU (B) Optimal (C) FIFO (D) MRU\n"
                    "  *Answer*: **(C) FIFO**. LRU and Optimal are stack algorithms and are mathematically immune to Belady's Anomaly.\n"
                    "- **Q2 (University Semester Exam)**: Why do modern operating systems avoid implementing pure LRU in hardware?\n"
                    "  *Answer*: Updating recency timestamps or moving list nodes on every single memory reference causes intolerable bus contention and CPU cycle overhead. Systems use the Clock (Second Chance) algorithm with reference bits instead.\n"
                    "- **Q3 (GATE CSE)**: Given the reference string `1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5`, compare FIFO and LRU on 3 vs 4 frames to demonstrate Belady's anomaly.\n"
                    "  *Answer*: FIFO faults increase from 9 to 10 when frames increase from 3 to 4 (Belady's anomaly). Under LRU, faults strictly decrease (10 to 8), confirming the stack algorithm invariant."
                ),
                "did_you_know": "Laszlo Belady proved in 1969 that FIFO can cause more page faults when allocated more memory (Belady's Anomaly), which led to the mathematical formalization of 'stack algorithms' that prove LRU is strictly immune."
            }

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

    @staticmethod
    def _build_topic_context_hinglish(clean_q: str, detected_domain: str) -> dict:
        topic = clean_title_casing(clean_q.strip())
        t_low = clean_q.lower().strip()

        # 0. Booth's Multiplication Algorithm (Hinglish COA Exam Standard)
        if any(k in t_low for k in ["booth", "booths", "booth's"]):
            return {
                "topic": "Booth's Multiplication Algorithm",
                "category": detected_domain,
                "difficulty_score": 8.2,
                "difficulty_level": "Advanced",
                "ai_evaluation": "Booth's Algorithm B.Tech CSE aur GATE Computer Organization (COA) ka ek high-frequency topic hai. Ye 2's complement signed arithmetic, hardware registers (AC, QR, BR, Qn+1, SC), Arithmetic Shift Right (ASR) sign preservation, aur cycle-by-cycle trace tables test karta hai.",
                "overview": (
                    "**Booth's Multiplication Algorithm** ek powerful hardware-level multiplication algorithm hai jo do signed binary numbers ko unke **Two's Complement** format me directly multiply karta hai. "
                    "Andrew Donald Booth ne ise 1950 me invent kiya tha. Iska main idea ye hai ki jab multiplier me lagataar $1$s ka block aata hai ($2^{k+m} - 2^k$), to har $1$ ke liye baar-baar addition karne ke bajay "
                    "ye algorithm **block ke start me ek subtraction aur block ke end me ek addition** perform karta hai, aur baaki steps ko simple shift operation se skip kar deta hai.\n\n"
                    "### Core Structural Invariants\n"
                    "- **Two's Complement Sign Preservation**: Chahe number positive ho ya negative, ye algorithm directly 2's complement me kaam karta hai bina kisi sign conversion ke.\n"
                    "- **String Property Optimization**: Consecutive 1s ke sequence ko ye single subtraction ($10$) aur single addition ($01$) se solve kar leta hai.\n"
                    "- **Constant Shift Guarantee**: $n$-bit multiplier ke liye exactly $n$ cycles me Arithmetic Shift Right (ASR) execute hota hai jab tak Sequence Counter ($SC = 0$) na ho jaye.\n"
                    "- **Arithmetic Sign Extension**: Har shift step me Accumulator `AC` ka Most Significant Bit (sign bit) preserve rehta hai taaki negative sign barkaraar rahe."
                ),
                "theoretical_foundations": (
                    "### Hardware Datapath & Register Architecture\n"
                    "Booth's Algorithm ke liye hardware architecture me niche diye gaye registers use hote hain:\n"
                    "- **AC (Accumulator Register)**: $n$-bit register, starting me $0000$ par initialize hota hai. Partial product aur final answer ka upper half hold karta hai.\n"
                    "- **QR (Multiplier Register)**: $n$-bit register, isme multiplier $Q$ store hota hai. Final answer ka lower half isme aata hai.\n"
                    "- **BR (Multiplicand Register)**: $n$-bit register, isme multiplicand $M$ store rehta hai (ye pure process me change nahi hota).\n"
                    "- **Qn+1 (Extra Flip-Flop)**: 1-bit flip-flop jo $QR$ ke right me judta hai ($Q_0$ ke aage), starting me $0$ par set hota hai.\n"
                    "- **SC (Sequence Counter)**: Word size $n$ par set hota hai ($4$ for 4-bit) aur har cycle ke baad $1$ se decrement hota hai.\n"
                    "- **ALU Adder/Subtractor**: Control logic ke hisab se $AC + BR$ ya $AC - BR$ ($AC + \\overline{BR} + 1$) perform karta hai."
                ),
                "core_formulations": (
                    "- **Bit-Pair Inspection Rules ($Q_0 Q_{n+1}$)**:\n"
                    "  * `00`: Koi arithmetic operation nahi. Bas **Arithmetic Shift Right (ASR)** karo $[AC, QR, Q_{n+1}]$ par aur $SC \\leftarrow SC - 1$.\n"
                    "  * `01`: $AC \\leftarrow AC + BR$ karo, fir **Arithmetic Shift Right (ASR)** aur $SC \\leftarrow SC - 1$.\n"
                    "  * `10`: $AC \\leftarrow AC - BR$ (yaani $AC + \\overline{BR} + 1$) karo, fir **Arithmetic Shift Right (ASR)** aur $SC \\leftarrow SC - 1$.\n"
                    "  * `11`: Koi arithmetic operation nahi. Bas **Arithmetic Shift Right (ASR)** karo aur $SC \\leftarrow SC - 1$.\n"
                    "- **ASR Rule**: $$ASR([AC, QR, Q_{n+1}]) \\implies Q_{n+1} \\leftarrow QR[0], \\; QR \\leftarrow [AC[0], QR[n-1..1]], \\; AC \\leftarrow [AC[n-1], AC[n-1..1]]$$\n"
                    "- **Time Complexity**: $n$ bit word ke liye total $\\Theta(n)$ cycles. Best case: 0 add/sub (jab saare bits 0 ya 1 hon). Worst case: $n$ add/sub (jab alternating $01010101$ ho)."
                ),
                "detailed_breakdown": (
                    "### 1. Core Concept & Invariants\n"
                    "Booth's Algorithm signed 2's complement numbers ko efficiently multiply karta hai. Iska basic principle consecutive 1s ko identity $\\sum_{i=k}^{k+m-1} 2^i = 2^{k+m} - 2^k$ ke through compress karna hai. "
                    "Isse multiple additions ki jagah bas ek subtraction ($10$) aur ek addition ($01$) lagta hai.\n\n"
                    "### 2. Hardware / Memory Model (Registers & Architecture)\n"
                    "- **AC (Accumulator)**: $n$-bit register, initial value $0000$.\n"
                    "- **QR (Multiplier)**: $n$-bit register, multiplier $Q$ hold karta hai.\n"
                    "- **BR (Multiplicand)**: $n$-bit register, multiplicand $M$ hold karta hai.\n"
                    "- **$Q_{n+1}$ (Extra Flip-Flop)**: 1-bit flip-flop, initial value $0$.\n"
                    "- **SC (Sequence Counter)**: $n$ se shuru hota hai aur $0$ hone par stop karta hai.\n\n"
                    "### 3. Step-by-Step Algorithm & State Transitions\n"
                    "1. Registers initialize karo: $AC = 0$, $Q_{n+1} = 0$, $SC = n$, $BR = M$, $QR = Q$.\n"
                    "2. $Q_0$ aur $Q_{n+1}$ bit pair ko check karo:\n"
                    "   - Agar `01`: $AC = AC + BR$ karo, fir ASR karo.\n"
                    "   - Agar `10`: $AC = AC - BR$ karo, fir ASR karo.\n"
                    "   - Agar `00` ya `11`: Direct ASR karo (koi add/sub nahi).\n"
                    "3. Sequence Counter ko decrement karo: $SC = SC - 1$.\n"
                    "4. Agar $SC > 0$, to Step 2 repeat karo. Jab $SC = 0$ ho jaye, tab final product $[AC, QR]$ me ready hai.\n\n"
                    "### 4. Worked Numerical Example & Complete Trace Table\n"
                    "**Question**: Multiplicand $M = -5$ ($1011_2$ in 4-bit 2's complement) aur Multiplier $Q = +7$ ($0111_2$) ko Booth's Algorithm se multiply karo.\n"
                    "- Yahan $BR = 1011_2$ ($-5$), $-BR = 0101_2$ ($+5$), $SC = 4$.\n\n"
                    "| Cycle / Step | $Q_0 Q_{n+1}$ | Operation | AC | QR | $Q_{n+1}$ | SC | Explanation |\n"
                    "|---|---|---|---|---|---|---|---|\n"
                    "| **Init** | - | Initial State | 0000 | 0111 | 0 | 4 | $AC=0, QR=0111, Q_{n+1}=0, SC=4$ |\n"
                    "| **Cycle 1** | **10** | $AC \\leftarrow AC - BR$ ($0000 + 0101$) | 0101 | 0111 | 0 | 4 | Bit pair $10 \\implies$ Subtract $BR$ (Add $-BR$) |\n"
                    "| | | Arithmetic Shift Right (ASR) | **0010** | **1011** | **1** | **3** | Shift $[AC, QR, Q_{n+1}]$; MSB $0$ AC me preserve |\n"
                    "| **Cycle 2** | **11** | Shift only | **0001** | **0101** | **1** | **2** | Bit pair $11 \\implies$ Shift only, SC ghat kar 2 |\n"
                    "| **Cycle 3** | **11** | Shift only | **0000** | **1010** | **1** | **1** | Bit pair $11 \\implies$ Shift only, SC ghat kar 1 |\n"
                    "| **Cycle 4** | **01** | $AC \\leftarrow AC + BR$ ($0000 + 1011$) | 1011 | 1010 | 1 | 1 | Bit pair $01 \\implies$ Add $BR$ ($1011$) |\n"
                    "| | | Arithmetic Shift Right (ASR) | **1101** | **1101** | **0** | **0** | Shift $[AC, QR, Q_{n+1}]$; MSB $1$ AC me preserve |\n\n"
                    "**Result Verification**:\n"
                    "- Final answer in $[AC, QR] = 11011101_2$.\n"
                    "- 2's complement calculation: $-2^7 + 2^6 + 2^4 + 2^3 + 2^2 + 2^0 = -128 + 64 + 16 + 8 + 4 + 1 = -35_{10}$.\n"
                    "- Expected: $(-5) \\times (+7) = -35_{10}$. **Pura answer perfectly match karta hai!**\n\n"
                    "### 5. Advantages, Trade-offs & Comparisons\n"
                    "- **Direct Signed Multiplication**: Negative numbers ke liye alag se conversion ki zarurat nahi padti.\n"
                    "- **Continuous 1s Optimization**: Consecutive 1s ko bas 2 operations me handle karta hai, jisse clock cycles bachte hain.\n"
                    "- **Worst-Case Trade-off**: Agar bits alternate kar rahe hon (`01010101...`), to har cycle me operation hota hai aur standard method se koi speedup nahi milta.\n\n"
                    "### 6. Common University Exam / GATE Questions\n"
                    "- **Q1 (GATE CSE)**: $Q = 00111100_2$ ke liye Booth's algorithm kitne additions aur subtractions karega?\n"
                    "  *Answer*: Right to left check karo: $00 \\to 0$, $10 \\to 1$ subtract, $11 \\to 0$, $01 \\to 1$ add. Total: **1 subtraction aur 1 addition** (bas 2 operations).\n"
                    "- **Q2 (University Exam)**: Logical Shift Right ke bajay Arithmetic Shift Right (ASR) kyu zaroori hai?\n"
                    "  *Answer*: ASR sign bit ($AC[n-1]$) ko copy karta hai, jo 2's complement negative numbers ka sign maintain rakhne ke liye zaroori hai.\n"
                    "- **Q3 (GATE CSE)**: Booth's algorithm ka worst-case multiplier pattern kya hai?\n"
                    "  *Answer*: Alternating bit pattern jaise `01010101` ya `10101010`, jisme har cycle me add/sub hota hai."
                ),
                "did_you_know": "Andrew Donald Booth ne ye algorithm 1950 me invent kiya tha jab wo London University me crystallographic calculations karte the, kyunki us time mechanical shifters adders se kaafi fast the."
            }

        # 0B. LRU Page Replacement Algorithm (Hinglish OS Exam Standard)
        if any(k in t_low for k in ["lru", "page replacement", "least recently used"]):
            return {
                "topic": "LRU Page Replacement Algorithm",
                "category": detected_domain,
                "difficulty_score": 7.8,
                "difficulty_level": "Advanced",
                "ai_evaluation": "LRU Operating Systems virtual memory ka core topic hai jo university exams aur GATE dono me frequently pucha jaata hai. Isme temporal locality, stack property, Belady's anomaly immunity, aur trace table calculation test hoti hai.",
                "overview": (
                    "**LRU (Least Recently Used) Page Replacement Algorithm** operating system ka ek memory management algorithm hai jo virtual memory me **page faults** ko resolve karta hai. "
                    "Jab page fault hota hai aur RAM ke saare page frames bhare hote hain, to LRU us page ko select karke baahar nikaalta hai (evict karta hai) jo **sabse lambe time se use nahi hua ho**. "
                    "Ye **Principle of Temporal Locality** par based hai—yaani jo pages abhi recently access hue hain, unke aage bhi access hone ke chances sabse zyada hote hain.\n\n"
                    "### Core Structural Invariants\n"
                    "- **Stack Algorithm Property**: LRU ek mathematically proven stack algorithm hai, yaani $m$ frames me store hue pages hamesha $m+1$ frames ke subset hote hain ($M(m, t) \\subseteq M(m+1, t)$).\n"
                    "- **Belady's Anomaly se Azaad**: Stack property ki wajah se LRU me frames badhane par kabhi bhi page faults nahi badhte (FIFO ke opposite).\n"
                    "- **Near-Optimal Performance**: LRU past reference history ko use karke theoretical optimal algorithm (MIN/OPT) ko practical environment me approximate karta hai."
                ),
                "theoretical_foundations": (
                    "### Architecture & Data Structures\n"
                    "LRU ko implement karne ke liye ye models use hote hain:\n"
                    "- **Doubly Linked List + Hash Map (Standard O(1) Cache)**: Recency order ko track karne ke liye doubly linked list (Head = MRU, Tail = LRU) aur fast lookup ke liye hash map use hota hai. Eviction aur node movement dono $\\mathcal{O}(1)$ time me hote hain.\n"
                    "- **Hardware Counter / Timestamp**: Har memory reference par CPU ek hardware clock counter ko increment karta hai aur page table entry me timestamp save karta hai.\n"
                    "- **Hardware Matrix (n x n Matrix)**: Jab page $k$ access hota hai, to row $k$ ko $1$s aur column $k$ ko $0$s set kar diya jaata hai. Lowest row value wala page LRU page hota hai."
                ),
                "core_formulations": (
                    "- **Page Fault Rate**: $$P = \\frac{\\text{Total Page Faults}}{\\text{Total References}}$$\n"
                    "- **Hit Ratio**: $$H = 1 - P = \\frac{\\text{Cache Hits}}{\\text{Total References}}$$\n"
                    "- **Stack Property Invariant**: $$\\forall t, \\; S_t(n) \\subseteq S_t(n+1) \\implies \\text{Belady\\'s Anomaly impossible hai}$$\n"
                    "- **Effective Memory Access Time (EMAT)**: $$EMAT = (1 - P) \\times t_m + P \\times t_s$$"
                ),
                "detailed_breakdown": (
                    "### 1. Core Concept & Invariants\n"
                    "LRU us page ko evict karta hai jo sabse zyada time se unreferenced raha ho. Temporal locality principle ke mutabiq recently used pages ki dobara zarurat padti hai. "
                    "Ye ek **stack algorithm** hai, jisme memory frames badhane par kabhi bhi page faults nahi badhte.\n\n"
                    "### 2. Hardware / Memory Model (Registers & Architecture)\n"
                    "- **Page Table Entry (PTE)**: Valid/Invalid bit, Modified/Dirty bit, aur Access Timestamp hold karta hai.\n"
                    "- **Physical Frames**: RAM ke slots jisme active pages load hote hain.\n"
                    "- **Recency Tracker**: Doubly Linked List ya hardware counter jo least recently used page ko identify karta hai.\n\n"
                    "### 3. Step-by-Step Algorithm & State Transitions\n"
                    "1. Jab CPU kisi page $p$ ko request karta hai, check karo ki wo frame buffer me hai ya nahi.\n"
                    "2. Agar present hai (Hit): page $p$ ki recency update karke MRU position par le aao. Zero page fault.\n"
                    "3. Agar absent hai (Page Fault / Miss):\n"
                    "   - Agar frame empty hai: page $p$ ko empty frame me load karo aur MRU mark karo.\n"
                    "   - Agar frames full hain: LRU position wale page ko evict karo, disk me write-back karo (agar dirty bit set ho), aur page $p$ ko frame me load karke MRU mark karo.\n\n"
                    "### 4. Worked Numerical Example & Complete Trace Table\n"
                    "**Question**: Reference String: `7, 0, 1, 2, 0, 3, 0, 4, 2, 3` ko **3 Page Frames** me LRU Page Replacement se trace karo.\n\n"
                    "| Ref Step | Page | Frame 1 | Frame 2 | Frame 3 | Hit / Miss | Evicted Page | Explanation |\n"
                    "|---|---|---|---|---|---|---|---|\n"
                    "| 1 | **7** | 7 | - | - | **Miss (Fault 1)** | None | Frame 1 me 7 load hua |\n"
                    "| 2 | **0** | 7 | 0 | - | **Miss (Fault 2)** | None | Frame 2 me 0 load hua |\n"
                    "| 3 | **1** | 7 | 0 | 1 | **Miss (Fault 3)** | None | Frame 3 me 1 load hua |\n"
                    "| 4 | **2** | 2 | 0 | 1 | **Miss (Fault 4)** | **7** | 7 sabse purana tha (LRU); 2 se replace hua |\n"
                    "| 5 | **0** | 2 | 0 | 1 | **Hit** | None | 0 already memory me tha; recency MRU hui |\n"
                    "| 6 | **3** | 2 | 0 | 3 | **Miss (Fault 5)** | **1** | 1 LRU tha (kyunki 0 abhi use hua); 3 se replace |\n"
                    "| 7 | **0** | 2 | 0 | 3 | **Hit** | None | 0 already memory me tha; recency MRU hui |\n"
                    "| 8 | **4** | 4 | 0 | 3 | **Miss (Fault 6)** | **2** | 2 LRU tha (0 aur 3 recent the); 4 se replace |\n"
                    "| 9 | **2** | 4 | 0 | 2 | **Miss (Fault 7)** | **3** | 3 LRU tha; 2 se replace hua |\n"
                    "| 10 | **3** | 3 | 0 | 2 | **Miss (Fault 8)** | **4** | 4 LRU tha; 3 se replace hua |\n\n"
                    "**Performance Results**:\n"
                    "- Total Page References = $10$\n"
                    "- Total Page Faults = **8**\n"
                    "- Total Hits = **2**\n"
                    "- Hit Ratio = $2 / 10 = 20\\%$, Page Fault Rate = $8 / 10 = 80\\%$.\n\n"
                    "### 5. Advantages, Trade-offs & Comparisons\n"
                    "- **Belady's Anomaly se Safe**: Stack property ensure karti hai ki frames badhane par faults kabhi nahi badhenge.\n"
                    "- **FIFO se Behtar**: Temporal locality use karne se realistic programs me FIFO se kam page faults aate hain.\n"
                    "- **Hardware Overhead**: Har memory access par recency update karne me hardware cost high hota hai, isliye practical OSes **Clock (Second Chance)** algorithm use karte hain.\n\n"
                    "### 6. Common University Exam / GATE Questions\n"
                    "- **Q1 (GATE CSE)**: Inme se kaunsa algorithm Belady's Anomaly show karta hai? (A) LRU (B) Optimal (C) FIFO (D) MRU\n"
                    "  *Answer*: **(C) FIFO**. LRU aur Optimal stack algorithms hain aur inme Belady's Anomaly kabhi nahi hota.\n"
                    "- **Q2 (University Exam)**: Modern OS pure LRU implement kyu nahi karte?\n"
                    "  *Answer*: Har memory access par counter update karna ya list nodes move karna bahut slow hota hai. Isliye OS Clock algorithm use karte hain jisme bas ek Reference Bit lagta hai.\n"
                    "- **Q3 (GATE CSE)**: Belady's anomaly prove karne ke liye reference string `1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5` par FIFO vs LRU compare karo.\n"
                    "  *Answer*: FIFO me 3 frames par 9 faults aate hain aur 4 frames par 10 faults aate hain (faults badh gaye = anomaly). LRU me 3 frames par 10 faults aur 4 frames par 8 faults aate hain (faults kam hue = safe)."
                ),
                "did_you_know": "Laszlo Belady ne 1969 me prove kiya tha ki FIFO me zyada RAM dene par bhi zyada page faults ho sakte hain (Belady's Anomaly), jiske baad stack algorithms ki mathematical discovery hui jo LRU ki reliability prove karti hai."
            }

        # 1. Binary Tree
        if any(k in t_low for k in ["binary tree", "bst", "binary search tree", "avl", "red black", "tree traversal", "b tree"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.4,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} hierarchical pointer recursion, balance factor preservation (AVL/Red-Black), aur log(n) height bounds ko evaluate karta hai.",
                "overview": (
                    f"Ek **{topic}** ek hierarchical aur non-linear data structure hota hai jisme nodes directed edges se jude hote hain, "
                    f"aur iska starting point ek single **root node** hota hai. Har node ke pass apna data aur maximum do child subtrees ke references hote hain, "
                    f"jinhe conventionally **left child** aur **right child** kaha jata hai. Jin nodes ka koi child nahi hota unhe **leaf nodes** kehte hain.\n\n"
                    f"### Core Structural Invariants\n"
                    fr"- **Branching Degree Constraint**: Har node $u$ ka degree $\le 2$ hota hai, jo ek recursive binary decision tree banata hai.\n"
                    fr"- **Recursive Subtree Topology**: Har child node khud ek independent binary subtree ka root hota hai. Is symmetry ki wajah se divide-and-conquer traversals (Pre-order, In-order, Post-order, Level-order/BFS) naturally execute hote hain.\n"
                    fr"- **Logarithmic Height Scaling**: Ek balanced binary tree me height $h = \lfloor\log_2 n\rfloor$ hoti hai, jisse search, insert, aur delete operation linear $O(n)$ ke bajay fast $O(\log n)$ time me ho jaate hain.\n"
                    fr"- **Nodes aur Edges Rule**: $n$ nodes wale kisi bhi binary tree me exactly $n - 1$ edges hote hain, jisme koi cycle nahi hoti.\n\n"
                    f"### Key Architectural Varieties\n"
                    fr"- **Full Binary Tree**: Har node ke ya to 0 children honge ya exactly 2.\n"
                    fr"- **Complete Binary Tree**: Last level ko chhodkar sabhi levels fully packed hote hain aur last level ke leaf nodes left-aligned hote hain (yehi structure **Binary Heaps** aur Priority Queues me use hota hai).\n"
                    fr"- **Binary Search Tree (BST)**: Rule ye hota hai ki left subtree ke saare keys node se chhote aur right subtree ke saare keys node se bade honge, jisse ordered lookup milta hai.\n"
                    fr"- **Self-Balancing Trees (AVL & Red-Black)**: Jab data insert hota hai to ye trees dynamic rotations perform karke height ko balance rakhte hain taaki $O(n)$ worst-case skewing na ho."
                ),
                "theoretical_foundations": (
                    f"Graph theory ke according binary tree ek directed acyclic connected graph $G = (V, E)$ hai jisme root ka in-degree 0 hota hai aur $|E| = |V| - 1$. "
                    f"Balanced tree me root se leaf tak ka average distance hamesha $\\Theta(\\log n)$ rehta hai."
                ),
                "core_formulations": (
                    r"- **Max Node Capacity at Height $h$**: $$\sum_{i=0}^h 2^i = 2^{h+1} - 1$$\n"
                    r"- **BST Ordering Invariant**: $$\forall x \in \text{Left}(u), \, \text{key}(x) < \text{key}(u) \quad \land \quad \forall y \in \text{Right}(u), \, \text{key}(y) > \text{key}(u)$$\n"
                    r"- **Balanced Search Complexity**: $$h = \lfloor \log_2 n \rfloor \implies \text{Search, Insert, Delete } \in \mathcal{O}(\log n)$$\n"
                    r"- **AVL Balance Factor**: $$\text{BF}(u) = \text{height}(\text{Left}(u)) - \text{height}(\text{Right}(u)) \in \{-1, 0, +1\}$$"
                ),
                "did_you_know": f"1960 me BST ko discover kiya gaya tha, aur 1962 me Soviet mathematicians Adelson-Velsky aur Landis ne AVL tree invent kiya jo duniya ka pehla self-balancing binary search tree tha."
            }

        # 2. Array & Vector
        if any(k in t_low for k in ["array", "vector", "dynamic array", "matrix"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 4.5,
                "difficulty_level": "Beginner",
                "ai_evaluation": f"{topic} memory address calculation arithmetic, spatial cache locality, aur O(1) random indexing vs O(n) element shifting ke trade-off ko test karta hai.",
                "overview": (
                    f"Ek **{topic}** computer science ka sabse basic aur powerful linear data structure hai jo identical data type ke elements ko physical memory me ek continuous (contiguous) block me store karta hai. "
                    f"Kyunki memory slots bilkul adjacent hote hain, isliye kisi bhi element ko index number aur simple pointer arithmetic ke zariye instantly access kiya ja sakta hai.\n\n"
                    f"### Core Structural Invariants\n"
                    fr"- **Contiguous Memory Allocation**: Saare elements RAM me lagatar memory slots occupy karte hain, do elements ke beech zero gap hota hai.\n"
                    fr"- **Instant Random Access ($O(1)$)**: Kisi bhi element ka address calculate karne ke liye sirf ek multiplication aur addition chahiye, isliye read/write hamesha deterministic $O(1)$ constant time me hota hai.\n"
                    fr"- **Spatial Cache Locality**: Sequential layout ki wajah se CPU memory controller puri 64-byte cache line ko prefetch kar leta hai, jisse iteration process pointer-based structures se kayi guna tez ho jata hai.\n\n"
                    f"### Key Varieties & Practical Realities\n"
                    fr"- **Static Array**: Compile time pe fixed size allocate hota hai; size badhane ke liye naya memory block lena padta hai.\n"
                    fr"- **Dynamic Array (Vector/ArrayList)**: Jab capacity full ho jaati hai to automatically double capacity ka naya buffer allocate karke data copy karta hai (amortized $O(1)$ append).\n"
                    fr"- **Multi-Dimensional Array / Matrix**: Data row-major ya column-major layout me store hota hai, jo 3D graphics, gaming engines, aur deep learning tensors ka core foundation hai."
                ),
                "theoretical_foundations": f"Von Neumann computer architecture aur random-access machine (RAM) model par based hai, jahan memory indexed sequence of words hoti hai.",
                "core_formulations": (
                    r"- **1D Array Address Formula**: $$\text{Address}(A[i]) = \text{Base} + i \times S$$\n"
                    r"- **2D Row-Major Offset**: $$\text{Address}(A[i][j]) = \text{Base} + (i \times N + j) \times S$$\n"
                    r"- **Time Complexities**: Direct Index Access: $O(1)$; Dynamic Array Append: Amortized $O(1)$; Middle Insertion/Deletion: $O(n)$."
                ),
                "did_you_know": f"John von Neumann aur Alan Turing ne 1940s me contiguous memory arrays ko formalize kiya tha. 1957 me FORTRAN team ne multi-dimensional arrays ko programming languages ka permanent hissa bana diya."
            }

        # 3. Linked List
        if any(k in t_low for k in ["linked list", "singly linked", "doubly linked", "circular linked"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 5.8,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} me pointer integrity manage karna, edge cases (head, tail, null) handle karna, aur O(1) splicing vs O(n) traversal ka balance samajhna hota hai.",
                "overview": (
                    f"Ek **{topic}** ek dynamic linear data structure hai jisme elements (jinhe **nodes** kaha jata hai) heap memory me alag-alag jagah (discontiguous) store hote hain. "
                    f"Har node ke pass apna data payload hota hai aur agle node ka memory address direct karne ke liye ek explicit pointer reference hota hai.\n\n"
                    f"### Core Invariants & Mechanics\n"
                    fr"- **Pointer-Chained Topology**: Nodes ko contiguous block ki zarurat nahi hoti. Insertion ke waqt dynamic memory dynamically allocate hoti hai.\n"
                    fr"- **Constant-Time Splicing ($O(1)$)**: Agar pointer position pata ho, to node insert ya delete karna sirf pointers swap karke $O(1)$ me ho jata hai, data shifting ki zarurat nahi padti.\n"
                    fr"- **Sequential Access ($O(n)$)**: Kisi specific $k$-th element tak pahunchne ke liye head node se ek-ek karke pointers traverse karne padte hain.\n\n"
                    f"### Key Variations\n"
                    fr"- **Singly Linked List**: Har node me single `next` pointer hota hai.\n"
                    fr"- **Doubly Linked List**: Har node me `prev` aur `next` dono pointers hote hain, jisse bidirectional traversal aur fast deletion possible hota hai.\n"
                    fr"- **Circular Linked List**: Tail node ka `next` pointer wapas head node pe point karta hai (round-robin CPU scheduling ke liye ideal)."
                ),
                "theoretical_foundations": f"1955-1956 me Allen Newell, Cliff Shaw, aur Herbert Simon ne RAND Corporation me IPL language ke liye linked lists develop kiye the.",
                "core_formulations": (
                    r"- **Node Memory Structure**: $$\text{Node} = \{\text{Data: } T, \, \text{Next: } *\text{Node}\}$$\n"
                    r"- **Traversal Bound**: $$T(n) = \sum_{i=1}^k c \implies \mathcal{O}(k) \le \mathcal{O}(n)$$\n"
                    r"- **Head Insertion / Deletion**: $$\mathcal{O}(1) \text{ time, } \mathcal{O}(1) \text{ auxiliary space}$$"
                ),
                "did_you_know": f"Linked lists ko pehli baar AI reasoning aur symbolic processing ke liye invent kiya gaya tha taaki dynamic memory bina pre-allocation ke manage ho sake."
            }

        # 4. Stack
        if any(k in t_low for k in ["stack", "lifo"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 4.8,
                "difficulty_level": "Beginner",
                "ai_evaluation": f"{topic} Last-In First-Out execution logic, function call stack frames, syntax bracket parsing, aur O(1) push/pop operations ko test karta hai.",
                "overview": (
                    f"Ek **{topic}** ek linear abstract data type hai jo strict **LIFO (Last-In, First-Out)** principle follow karta hai. "
                    f"Iska matlab ye hai ki jo element sabse aakhir me insert hota hai, wahi sabse pehle bahar nikalta hai. Saare operations sirf ek single end (**Top**) se perform hote hain.\n\n"
                    f"### Core Invariants & Operations\n"
                    fr"- **Push Operation**: Naye element ko stack ke Top frame par place karta hai ($O(1)$ time).\n"
                    fr"- **Pop Operation**: Current Top element ko remove karke return karta hai ($O(1)$ time).\n"
                    fr"- **Peek/Top**: Top element ko bina delete kiye inspect karta hai ($O(1)$ time).\n"
                    fr"- **LIFO Invariant**: Insertion aur deletion ka sequence strictly reverse chronological order me bound hota hai."
                ),
                "theoretical_foundations": f"Computer architecture me Stack Pointer (SP) register hardware level par active function call frames aur local variables ko track karta hai.",
                "core_formulations": (
                    r"- **Push Operation**: $$\text{Top} \leftarrow \text{Top} + 1, \quad S[\text{Top}] \leftarrow x \implies \mathcal{O}(1)$$\n"
                    r"- **Pop Operation**: $$x \leftarrow S[\text{Top}], \quad \text{Top} \leftarrow \text{Top} - 1 \implies \mathcal{O}(1)$$"
                ),
                "did_you_know": f"Friedrich L. Bauer aur Klaus Samelson ne 1957 me stack data structure ka patent file kiya tha expression evaluation aur compiler parsing ke liye."
            }

        # 5. Queue
        if any(k in t_low for k in ["queue", "fifo"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 4.9,
                "difficulty_level": "Beginner",
                "ai_evaluation": f"{topic} First-In First-Out streaming fairness, circular buffer wraparound arithmetic, aur producer-consumer thread synchronization ko evaluate karta hai.",
                "overview": (
                    f"Ek **{topic}** ek linear abstract data type hai jo **FIFO (First-In, First-Out)** principle par kaam karta hai. "
                    f"Iska matlab jo element sabse pehle aata hai, wahi sabse pehle process hota hai. Isme do distinct ends hote hain: Rear (jahan se enqueue hota hai) aur Front (jahan se dequeue hota hai).\n\n"
                    f"### Core Invariants & Operations\n"
                    fr"- **Enqueue**: Naye element ko queue ke Rear end par add karta hai ($O(1)$ time).\n"
                    fr"- **Dequeue**: Queue ke Front se sabse purane element ko remove karta hai ($O(1)$ time).\n"
                    fr"- **Circular Buffer Mechanics**: Modulo arithmetic use karke array me space reuse kiya jata hai."
                ),
                "theoretical_foundations": f"Queuing theory aur asynchronous event-driven architectures ka bedrock hai, jo OS print spoolers aur network packet buffers me use hota hai.",
                "core_formulations": (
                    r"- **Circular Enqueue**: $$\text{Rear} \leftarrow (\text{Rear} + 1) \pmod N, \quad Q[\text{Rear}] \leftarrow x$$\n"
                    r"- **Circular Dequeue**: $$x \leftarrow Q[\text{Front}], \quad \text{Front} \leftarrow (\text{Front} + 1) \pmod N$$"
                ),
                "did_you_know": f"Agner Krarup Erlang ne 1909 me queuing theory develop ki thi Copenhagen telephone exchanges me traffic congestion calculate karne ke liye."
            }

        # 6. Hash Table
        if any(k in t_low for k in ["hash", "hash table", "hash map", "hashing"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 6.8,
                "difficulty_level": "Intermediate",
                "ai_evaluation": f"{topic} hash function uniformity, collision resolution strategies (chaining vs open addressing), load factor threshold, aur amortized O(1) bounds ko test karta hai.",
                "overview": (
                    f"Ek **{topic}** ek high-efficiency associative data structure hai jo keys ko values ke saath map karta hai. "
                    f"Ye ek mathematical **hash function** use karta hai jo arbitrary string ya object key ko numeric index me convert kar deta hai, jisse average case me instant $O(1)$ lookup milta hai.\n\n"
                    f"### Core Invariants & Mechanics\n"
                    fr"- **Deterministic Hash Mapping**: Same key hamesha same integer hash code produce karti hai.\n"
                    fr"- **Collision Resolution**: Jab do alag keys same index produce karti hain, to Chaining (linked list buckets) ya Open Addressing (Linear/Quadratic Probing) se solve kiya jata hai.\n"
                    fr"- **Load Factor Threshold**: Load factor $\alpha = n/m$ jab typically 0.75 cross karta hai, to table automatically resize ho jaati hai."
                ),
                "theoretical_foundations": f"Universal hashing aur probability distribution theory par based hai jahan uniform hashing assumption deterministic collision bounds prove karti hai.",
                "core_formulations": (
                    r"- **Hash Index Calculation**: $$\text{index} = h(\text{key}) \pmod M$$\n"
                    r"- **Load Factor**: $$\alpha = \frac{n}{M} \quad (\text{Threshold: } \alpha \le 0.75)$$\n"
                    r"- **Average Operational Time**: $$\text{Search, Insert, Delete} \in \mathcal{O}(1) \text{ Average, } \mathcal{O}(n) \text{ Worst-Case}$$"
                ),
                "did_you_know": f"Hans Peter Luhn ne IBM me 1953 me hash table ka concept invent kiya tha chemical information search karne ke liye."
            }

        # 7. Graph & Dijkstra
        if any(k in t_low for k in ["graph", "dijkstra", "bfs", "dfs", "shortest path"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.8,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} adjacency representations, priority queue greedy edge relaxation, non-negative weight invariant, aur O((V + E) log V) complexity ko evaluate karta hai.",
                "overview": (
                    f"Ek **{topic}** ek versatile non-linear data structure hai jo entities ke beech pairwise connections ko model karta hai. "
                    f"Isme vertices ya nodes ka set $V$ aur unhe jodne wale edges ka set $E$ hota hai. Google Maps routing, social networks, aur Internet routing protocols graphs par hi chalte hain.\n\n"
                    f"### Core Invariants & Mechanics\n"
                    fr"- **Graph Representation**: Sparse graphs ke liye Adjacency List ($O(V + E)$ space) aur dense graphs ke liye Adjacency Matrix ($O(V^2)$ space) standard formats hain.\n"
                    fr"- **Dijkstra Greedy Invariant**: Non-negative edge weights hone par, min-priority queue se extract kiya gaya vertex hamesha globally optimal shortest distance secure kar chuka hota hai.\n"
                    fr"- **Edge Relaxation**: Agar $d[u] + w(u, v) < d[v]$, to distance $d[v]$ update ho jata hai."
                ),
                "theoretical_foundations": f"Leonhard Euler ne 1736 me Seven Bridges of Königsberg problem solve karke graph theory ki foundation rakhi thi.",
                "core_formulations": (
                    r"- **Graph Definition**: $$G = (V, E) \quad \text{where } E \subseteq V \times V$$\n"
                    r"- **Dijkstra Relaxation Rule**: $$\text{if } d[u] + w(u, v) < d[v] \implies d[v] \leftarrow d[u] + w(u, v)$$\n"
                    r"- **Dijkstra Complexity with Min-Heap**: $$\mathcal{O}((V + E) \log V)$$"
                ),
                "did_you_know": f"Edsger Dijkstra ne 1956 me bina pen-paper ke sirf 20 minute me coffee peete waqt Dijkstra algorithm design kiya tha ARMAC computer ko test karne ke liye."
            }

        # 8. Operating System
        if any(k in t_low for k in ["operating system", "process", "thread", "deadlock", "paging", "scheduling"]):
            return {
                "topic": topic,
                "category": detected_domain,
                "difficulty_score": 7.2,
                "difficulty_level": "Advanced",
                "ai_evaluation": f"{topic} hardware virtualization, kernel vs user mode privileges, process lifecycle state transitions, aur concurrency synchronization ko test karta hai.",
                "overview": (
                    f"Ek **{topic}** computer hardware aur user programs ke beech ka master system software coordinator hai. "
                    f"Iska primary goal CPU, physical memory (RAM), storage disks, aur peripheral I/O devices ko efficiently multiplex aur secure karna hota hai.\n\n"
                    f"### Core Architectural Invariants\n"
                    fr"- **Dual-Mode Execution**: Hardware-enforced protection Ring 0 (Kernel Mode) aur Ring 3 (User Mode) me code isolate karke crash hone se bachata hai.\n"
                    fr"- **5-State Process Model**: Har program Process Control Block (PCB) me track hota hai: New $\to$ Ready $\leftrightarrow$ Running $\to$ Terminated (aur I/O wait me Blocked).\n"
                    fr"- **Virtual Memory & Paging**: MMU hardware page tables ke through logical addresses ko physical frames me translate karta hai, providing 100% memory isolation."
                ),
                "theoretical_foundations": f"Dijkstra ke THE multiprogramming system (1968) aur Ken Thompson/Dennis Ritchie ke UNIX architecture par modern OS systems grounded hain.",
                "core_formulations": (
                    r"- **Virtual Address Translation**: $$\text{Physical Address} = (\text{Frame Number} \times \text{Page Size}) + \text{Offset}$$\n"
                    r"- **CPU Utilization**: $$\text{Utilization} = 1 - p^n \quad (\text{where } p \text{ is I/O wait fraction, } n \text{ processes})$$"
                ),
                "did_you_know": f"1969 me Bell Labs me Ken Thompson ne ek discarded PDP-7 computer par pehla Unix system likha tha taaki wo Space Travel naam ka game khel sakein."
            }

        # Fallback for any other topic in Hinglish
        base_eng = TopicContextEngine._build_topic_context_raw(clean_q, detected_domain, lang="english")
        return {
            "topic": topic,
            "category": detected_domain,
            "difficulty_score": base_eng.get("difficulty_score", 6.5),
            "difficulty_level": base_eng.get("difficulty_level", "Intermediate"),
            "ai_evaluation": f"{topic} ke core theoretical principles, governing formulas, aur practical engineering trade-offs ko systematically analyze karta hai.",
            "overview": (
                f"**{topic}** academic curriculum aur modern technology ka ek essential concept hai jo {detected_domain} me core significance rakhta hai. "
                f"Iska primary focus efficiency badhana, operational bottlenecks door karna, aur system performance optimize karna hota hai.\n\n"
                f"### Core Concepts & Engineering Realities\n"
                f"- **Core Functionality**: Ye real-world problems ko solve karne ke liye structured rules aur mathematical models provide karta hai.\n"
                f"- **Practical Significance**: Software engineering, physical systems, aur analytical frameworks me iska direct application hota hai."
            ),
            "theoretical_foundations": base_eng.get("theoretical_foundations", f"Rooted in core principles of {detected_domain}."),
            "core_formulations": base_eng.get("core_formulations", r"- **Governing Formula**: $$\Phi(x) = \sum \text{Output}$$"),
            "did_you_know": base_eng.get("did_you_know", f"{topic} ke theoretical foundations kai decades ke collaborative scientific research par based hain.")
        }

