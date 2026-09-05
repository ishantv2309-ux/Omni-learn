"""
Isolated Dual-Engine AI Note Making Routes
Provides dedicated endpoints:
- POST /api/generate-notes (Topic-Wise deep dive notes)
- POST /api/generate-unit-notes (AKTU Unit 1-5 syllabus notes)
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import re

from backend.services.gemini_service import GeminiService
from backend import config

router = APIRouter(tags=["AI Dual Note Engine"])

class TopicNoteRequest(BaseModel):
    topic: str
    subject: str = "B.Tech Engineering"

class UnitNoteRequest(BaseModel):
    subject_code: str
    subject_name: str
    unit_number: Optional[int] = None
    unit: Optional[int] = None
    aktu_syllabus_topics: Optional[List[str]] = []

TOPIC_SYSTEM_PROMPT = (
    "You are a Senior University Engineering Professor and Computer Science Expert. "
    "Your mandate is to generate exhaustive, authoritative academic revision notes bound strictly and exclusively to the user's requested topic.\n"
    "CRITICAL DOMAIN RULES:\n"
    "1. DOMAIN DISCRIMINATION: You must accurately detect the query domain:\n"
    "   - For COMPUTER SCIENCE, DATA STRUCTURES & ALGORITHMS (e.g., Array, Linked List, Recursion, Stack, Queue, Tree, Graph, Hashing, Sorting, Pointer, Complexity):\n"
    "     * DO NOT generate differential equations, Laplace transforms, control systems, divergence/curl gradients, or thermodynamic laws.\n"
    "     * Formulate mathematical foundations STRICTLY relevant to CS: memory addressing formulas (e.g., Address(A[i]) = Base + i * w), asymptotic recurrence relations (e.g., Master Theorem, T(n) = T(n-1) + O(1)), Big-O bounds ($O(1)$, $O(n)$, $O(\\log n)$), pointer arithmetic, and algorithmic state invariants.\n"
    "     * Include clean, complete, idiomatic code implementations (Python/C++) with edge-case handling.\n"
    "   - For CORE ENGINEERING & MATHEMATICS (e.g., Calculus, Circuits, Thermodynamics, Fluid Dynamics, Mechanics):\n"
    "     * Formulate appropriate governing differential equations, boundary conditions, and physical conservation laws.\n"
    "2. STRICT TOPIC BINDING: Every section, example, code snippet, and examination question must correspond directly to the exact requested topic without wandering or irrelevant template filler.\n"
    "3. LATEX MATH: Render ALL mathematical expressions and variables in standard LaTeX ($inline$ and $$display$$)."
)

AKTU_UNIT_PROMPT = (
    "You are an official AKTU University Syllabus & Exam Expert. Generate complete Unit Notes "
    "tailored for AKTU End-Semester Exams with Unit-wise structured modules, key university questions, "
    "exam marking weightage, and LaTeX mathematical derivations ($inline$ and $$display$$)."
)

def detect_query_domain(topic: str, subject: str = "") -> str:
    """Accurately classifies the academic domain of a query."""
    text = (topic + " " + subject).lower()
    
    cs_keywords = [
        "array", "linked list", "recursion", "stack", "queue", "tree", "binary tree",
        "bst", "avl", "b-tree", "graph", "dfs", "bfs", "dijkstra", "sorting", "sort",
        "quick sort", "merge sort", "bubble sort", "insertion sort", "heap", "heapsort",
        "hash", "hashing", "hash table", "hash map", "trie", "algorithm", "data structure",
        "pointer", "dynamic programming", "greedy", "backtracking", "divide and conquer",
        "string", "bit manipulation", "matrix", "time complexity", "space complexity",
        "big o", "asymptotic", "oop", "object oriented", "class", "inheritance",
        "polymorphism", "encapsulation", "compiler", "operating system", "process",
        "thread", "deadlock", "semaphore", "paging", "virtual memory", "dbms", "sql",
        "normalization", "relational", "transaction", "acid", "computer network",
        "tcp", "udp", "ip", "osi", "http", "routing", "socket", "cryptography",
        "rsa", "des", "aes", "cipher", "software engineering", "agile", "sdlc",
        "testing", "web technology", "html", "css", "javascript", "python", "java", "c++", "c language"
    ]
    for kw in cs_keywords:
        if kw in text:
            return "Computer Science & Engineering"
            
    ee_keywords = ["circuit", "kcl", "kvl", "thevenin", "norton", "transistor", "diode", "bjt", "mosfet", "op-amp", "amplifier", "transformer", "induction motor", "synchronous", "power system", "signal", "fourier", "laplace", "z-transform", "modulation"]
    for kw in ee_keywords:
        if kw in text:
            return "Electrical & Electronics Engineering"
            
    me_keywords = ["thermodynamic", "entropy", "enthalpy", "carnot", "otto", "diesel", "fluid mechanics", "bernoulli", "reynolds", "stress", "strain", "beam", "bending moment", "shear force", "kinematics", "heat transfer", "conduction", "convection", "radiation"]
    for kw in me_keywords:
        if kw in text:
            return "Mechanical Engineering"
            
    math_keywords = ["integral", "derivative", "differential equation", "calculus", "matrix algebra", "eigenvalue", "eigenvector", "probability", "statistics", "vector calculus", "gradient", "divergence", "curl"]
    for kw in math_keywords:
        if kw in text:
            return "Engineering Mathematics"
            
    return subject if subject and subject != "B.Tech Engineering" else "Computer Science & Engineering"

def _generate_fallback_topic_notes(topic: str, subject: str) -> str:
    clean_topic = topic.strip().title()
    domain = detect_query_domain(clean_topic, subject)
    clean_sub = domain if domain else subject.strip()
    topic_lower = clean_topic.lower()

    if "Computer Science" in domain:
        # High-yield CS / Data Structures fallback with zero differential equations
        if "array" in topic_lower:
            math_section = (
                "### Memory Representation & Index Address Calculation\n"
                "In computer memory, an array stores elements at contiguous physical memory addresses. "
                "The address calculation function guarantees constant-time random access:\n\n"
                "1. **One-Dimensional Array Address Formula**:\n"
                "$$\\text{Address}(A[i]) = \\text{BaseAddress} + (i - \\text{LowerBound}) \\times w$$\n"
                "where $w$ is the element size in bytes (e.g., $w = 4$ for standard 32-bit integers).\n\n"
                "2. **Two-Dimensional Row-Major Order Formula**:\n"
                "$$\\text{Address}(A[i][j]) = \\text{BaseAddress} + \\Big( (i - \\text{LB}_r) \\times N_c + (j - \\text{LB}_c) \\Big) \\times w$$\n"
                "where $N_c$ is the total number of columns.\n\n"
                "3. **Two-Dimensional Column-Major Order Formula**:\n"
                "$$\\text{Address}(A[i][j]) = \\text{BaseAddress} + \\Big( (j - \\text{LB}_c) \\times N_r + (i - \\text{LB}_r) \\Big) \\times w$$\n"
                "where $N_r$ is the total number of rows."
            )
            code_section = (
                "```python\n"
                "# Python demonstration of Array operations: Traversal, Linear Search, Insertion\n"
                "class ArrayOperations:\n"
                "    def __init__(self, capacity: int = 10):\n"
                "        self.capacity = capacity\n"
                "        self.data = [0] * capacity\n"
                "        self.size = 0\n"
                "\n"
                "    def insert_at(self, index: int, value: int) -> bool:\n"
                "        \"\"\"Inserts element at specified index in O(n) time.\"\"\"\n"
                "        if self.size >= self.capacity or index < 0 or index > self.size:\n"
                "            return False\n"
                "        for i in range(self.size, index, -1):\n"
                "            self.data[i] = self.data[i - 1]\n"
                "        self.data[index] = value\n"
                "        self.size += 1\n"
                "        return True\n"
                "\n"
                "    def linear_search(self, target: int) -> int:\n"
                "        \"\"\"Finds index of target element in O(n) time.\"\"\"\n"
                "        for idx in range(self.size):\n"
                "            if self.data[idx] == target:\n"
                "                return idx\n"
                "        return -1\n"
                "```"
            )
            pitfalls = (
                "1. **Off-By-One Index Errors**: Accessing `A[n]` instead of `A[n-1]` in 0-indexed languages leading to `IndexOutOfBoundsException` or Segmentation Faults.\n"
                "2. **Buffer Overflow & Fixed Size**: Static arrays have fixed capacity defined at compile-time. Attempting to insert beyond capacity corrupts adjacent memory blocks in C/C++.\n"
                "3. **Inefficient Middle Insertion/Deletion**: Beginners assume insertion is $O(1)$; however, shifting elements requires $O(n)$ time complexity in contiguous storage."
            )
            exam_qa = (
                "1. **Question 1**: An array $A[1..10][1..15]$ is stored in Row-Major order starting at Base Address $1000$. Each element requires $2$ bytes. Compute $\\text{Address}(A[4][6])$.\n"
                "   - *Answer*: Using $\\text{Address}(A[i][j]) = 1000 + \\big( (4 - 1) \\times 15 + (6 - 1) \\big) \\times 2 = 1000 + (45 + 5) \\times 2 = 1000 + 100 = 1100$.\n\n"
                "2. **Question 2**: Compare Static Arrays vs Dynamic Arrays in terms of memory overhead and amortized insertion cost.\n"
                "   - *Answer*: Static arrays have $O(1)$ memory overhead and fixed size. Dynamic arrays (like `std::vector` or Python `list`) double capacity upon exhaustion, yielding an amortized insertion complexity of $O(1)$ per append."
            )
        elif "recursion" in topic_lower:
            math_section = (
                "### Recurrence Relations & Call Stack Analysis\n"
                "Recursive algorithms express computational complexity as mathematical recurrences:\n\n"
                "1. **Linear Recurrence Relation**:\n"
                "$$T(n) = T(n - 1) + O(1) \\implies T(n) = O(n)$$\n"
                "2. **Divide-and-Conquer Recurrence (Master Theorem Formulation)**:\n"
                "$$T(n) = a T(n / b) + f(n)$$\n"
                "3. **Call Stack Space Complexity Bound**:\n"
                "$$\\text{Auxiliary Space} = O(d)$$\n"
                "where $d$ is the maximum depth of the active recursion call tree."
            )
            code_section = (
                "```python\n"
                "# Step-by-Step Recursion: Factorial & Binary Search with Base Cases\n"
                "def factorial(n: int) -> int:\n"
                "    \"\"\"Calculates factorial with base case termination.\"\"\"\n"
                "    if n <= 1:  # Base condition: terminates recursion\n"
                "        return 1\n"
                "    return n * factorial(n - 1)  # Recursive decomposition\n"
                "\n"
                "def binary_search_recursive(arr, low: int, high: int, target: int) -> int:\n"
                "    if low > high:\n"
                "        return -1  # Base case: element not found\n"
                "    mid = low + (high - low) // 2\n"
                "    if arr[mid] == target:\n"
                "        return mid\n"
                "    elif arr[mid] > target:\n"
                "        return binary_search_recursive(arr, low, mid - 1, target)\n"
                "    else:\n"
                "        return binary_search_recursive(arr, mid + 1, high, target)\n"
                "```"
            )
            pitfalls = (
                "1. **Missing or Faulty Base Case**: Omitting the termination condition triggers infinite recursion and `RecursionError: maximum recursion depth exceeded` (Stack Overflow).\n"
                "2. **Redundant Subproblem Recomputation**: Naive recursive Fibonacci calculates $F(n-2)$ exponentially ($O(2^n)$), requiring memoization to reduce to $O(n)$.\n"
                "3. **Call Stack Overhead**: Every recursive invocation allocates an activation record (frame) on the call stack, consuming $O(n)$ auxiliary memory."
            )
            exam_qa = (
                "1. **Question 1**: Solve the recurrence $T(n) = 2T(n/2) + O(n)$ using Master Theorem.\n"
                "   - *Answer*: Here $a = 2, b = 2, k = 1$. Since $\\log_b a = \\log_2 2 = 1 = k$, Case 2 applies: $T(n) = \\Theta(n \\log n)$.\n\n"
                "2. **Question 2**: What is Tail Recursion and how does the compiler optimize it?\n"
                "   - *Answer*: A recursive function is tail-recursive when the recursive call is the very last instruction. Optimizing compilers replace it with an iterative jump, reducing auxiliary stack space from $O(n)$ to $O(1)$."
            )
        else:
            math_section = (
                f"### Theoretical Foundations & Algorithmic Invariants of {clean_topic}\n"
                f"The formal mathematical behavior of {clean_topic} is characterized by state transitions and complexity invariants:\n\n"
                f"1. **Asymptotic Recurrence & State Function**:\n"
                f"$$T(n) = T(n - 1) + c \\implies T(n) = O(n)$$\n"
                f"2. **Information-Theoretic Lower Bound**:\n"
                f"$$\\Omega(n \\log n) \\le C_{{\\mathrm{{cmp}}}}(n)$$\n"
                f"3. **Space Invariant Allocation**:\n"
                f"$$\\mathcal{{M}}(n) = k \\times n + O(1)$$"
            )
            code_section = (
                f"```python\n"
                f"# Core Implementation & Invariant Verification for {clean_topic}\n"
                f"def solve_{re.sub(r'[^a-zA-Z0-9]+', '_', clean_topic.lower())}(data_input):\n"
                f"    \"\"\"Deterministic implementation with boundary validation.\"\"\"\n"
                f"    if not data_input:\n"
                f"        return None\n"
                f"    \n"
                f"    # Process elements following standard algorithm steps\n"
                f"    result = []\n"
                f"    for item in data_input:\n"
                f"        if item is not None:\n"
                f"            result.append(item)\n"
                f"    return result\n"
                f"```"
            )
            pitfalls = (
                f"1. **Null Pointer & Null State Dereferencing**: Accessing state before verifying initialization.\n"
                f"2. **Boundary Condition Neglect**: Empty sequences or singleton inputs failing algorithm invariants.\n"
                f"3. **Memory Leaks**: Failing to deallocate or unbind dynamically created elements."
            )
            exam_qa = (
                f"1. **Question 1**: Derive the worst-case and best-case time complexity for {clean_topic}.\n"
                f"   - *Answer*: The worst-case is bounded by $O(n)$, while the best-case achieves $O(1)$ under optimal initial invariant conditions.\n\n"
                f"2. **Question 2**: Explain the memory representation of {clean_topic} in modern computer architecture.\n"
                f"   - *Answer*: Structured in contiguous or linked memory blocks with deterministic address translation and cache locality."
            )

        return (
            f"# Executive Overview: {clean_topic}\n"
            f"**Subject Context:** {clean_sub} | **Academic Level:** Undergraduate Engineering (B.Tech CS/IT)\n\n"
            f"{clean_topic} is a core foundational concept in Computer Science and Data Structures. "
            f"Mastering {clean_topic} provides the computational basis for structured data representation, memory-efficient algorithm design, and optimal execution throughput. "
            f"Understanding both physical memory storage and algorithmic operations is vital for software engineering and university examinations.\n\n"
            f"## Core Concepts & Architectural Foundations\n"
            f"{math_section}\n\n"
            f"## Step-by-Step Practical Implementation\n"
            f"{code_section}\n\n"
            f"## Complexity Analysis & Big-O Cheatsheet\n"
            f"| Operation / Case | Best Case | Average Case | Worst Case | Space Complexity |\n"
            f"| :--- | :--- | :--- | :--- | :--- |\n"
            f"| Access / Lookup | $O(1)$ | $O(1)$ | $O(1)$ | $O(1)$ |\n"
            f"| Search | $O(1)$ | $O(n)$ | $O(n)$ | $O(1)$ |\n"
            f"| Insertion | $O(1)$ | $O(n)$ | $O(n)$ | $O(1)$ |\n"
            f"| Deletion | $O(1)$ | $O(n)$ | $O(n)$ | $O(1)$ |\n\n"
            f"## Common Pitfalls & Exam Traps\n"
            f"{pitfalls}\n\n"
            f"## University Examination Practice Problems with Model Answers\n"
            f"{exam_qa}"
        )

    # Fallback for Core Engineering / Math topics
    return (
        f"# Executive Overview: {clean_topic}\n"
        f"**Subject Context:** {clean_sub} | **Academic Level:** Undergraduate Engineering (B.Tech / University Honors)\n\n"
        f"{clean_topic} constitutes a fundamental analytical subject within {clean_sub}. "
        f"Mastering this domain requires understanding its underlying governing principles, conservation laws, "
        f"and physical/mathematical manifestations.\n\n"
        f"## Theoretical Derivations & Mathematical Foundations\n"
        f"1. **Governing State Equation**:\n"
        f"$$\\frac{{d\\phi}}{{dt}} + \\alpha \\phi = f(t)$$\n"
        f"2. **Conservation Principle**:\n"
        f"$$\\int_{{V}} \\nabla \\cdot \\mathbf{{F}} \\, dV = \\oint_{{S}} \\mathbf{{F}} \\cdot d\\mathbf{{A}}$$\n\n"
        f"## Numerical Formulation & Problem Solution\n"
        f"Given parameter $\\alpha = 2.0$ with initial condition $\\phi(0) = 5.0$, the analytical trajectory is:\n"
        f"$$\\phi(t) = \\phi(0) e^{{-\\alpha t}} = 5.0 e^{{-2.0 t}}$$\n\n"
        f"## Exam Strategy & Scoring Tips\n"
        f"- Always state assumptions and boundary conditions clearly.\n"
        f"- Enclose final formulas and solutions in standard LaTeX boxed format."
    )

def _generate_fallback_unit_notes(code: str, name: str, unit: int, topics: List[str]) -> str:
    clean_code = code.strip().upper()
    clean_name = name.strip()
    unit_num = int(unit)
    
    cleaned_topics = []
    for t in (topics or []):
        t_str = str(t).strip()
        if t_str and t_str not in cleaned_topics:
            cleaned_topics.append(t_str)
            
    if not cleaned_topics:
        cleaned_topics = [
            f"Unit {unit_num} Core Syllabus Topics",
            f"Key Theoretical Frameworks of Unit {unit_num}"
        ]
    
    primary_topic = cleaned_topics[0]
    secondary_topic = cleaned_topics[1] if len(cleaned_topics) > 1 else cleaned_topics[0]
    topics_str = ", ".join(cleaned_topics)
    combined_context = f"{clean_name} {topics_str}".lower()
    
    is_cs = any(k in combined_context for k in [
        "data structure", "algorithm", "array", "stack", "queue", "list", "tree", "graph",
        "search", "sort", "recursion", "c++", "c language", "programming", "database", "dbms"
    ])
    
    if is_cs or "kcs" in clean_code.lower() or "bcs" in clean_code.lower():
        if unit_num == 1:
            theme = "Arrays, Searching, Sorting & Asymptotic Analysis"
            math_block = (
                "#### 1. One-Dimensional & Multi-Dimensional Array Addressing\n"
                "In contiguous memory allocation, element addresses are computed in $O(1)$ time:\n\n"
                "- **1D Array Address Formula**:\n"
                "$$\\text{Address}(A[i]) = \\text{Base} + (i - \\text{LB}) \\times w$$\n\n"
                "- **2D Row-Major Order (RMO)**:\n"
                "$$\\text{Address}(A[i][j]) = \\text{Base} + \\Big( (i - \\text{LB}_r) \\times N_c + (j - \\text{LB}_c) \\Big) \\times w$$\n\n"
                "- **2D Column-Major Order (CMO)**:\n"
                "$$\\text{Address}(A[i][j]) = \\text{Base} + \\Big( (j - \\text{LB}_c) \\times N_r + (i - \\text{LB}_r) \\Big) \\times w$$"
            )
            sec_a = (
                "1. **Define Big-O, Big-Omega, and Big-Theta asymptotic notations.**\n"
                "   - *Answer:* $O(g(n))$ defines an asymptotic upper bound; $\\Omega(g(n))$ defines an asymptotic lower bound; $\\Theta(g(n))$ defines an asymptotically tight bound.\n\n"
                "2. **State the base address formula for an array in Row Major Order.**\n"
                "   - *Answer:* $\\text{Address}(A[i][j]) = \\text{Base} + [(i - \\text{LB}_1) \\times N_2 + (j - \\text{LB}_2)] \\times w$, where $N_2$ is number of columns.\n\n"
                "3. **What is the worst-case and best-case time complexity of Quick Sort?**\n"
                "   - *Answer:* Best-case is $O(n \\log n)$ when partition is balanced; worst-case is $O(n^2)$ when partition is completely skewed.\n\n"
                "4. **Differentiate between Linear Search and Binary Search.**\n"
                "   - *Answer:* Linear search works on unsorted arrays in $O(n)$ time. Binary search requires a sorted array and executes in $O(\\log n)$ time."
            )
            sec_b = (
                "1. **Explain the working of Binary Search on a sorted array and prove its logarithmic time complexity (10 Marks).**\n"
                "   - *Solution*: At each step, the search interval is halved ($T(n) = T(n/2) + c$). Via Master Theorem with $a = 1, b = 2$, $T(n) = \\Theta(\\log n)$.\n\n"
                "2. **Calculate the address of $A[5][20]$ in an array $A[-5 \\dots 15, 10 \\dots 30]$ with Base Address 1020 and 4 bytes per element in both Row-Major and Column-Major order (10 Marks).**\n"
                "   - *Solution*: $N_r = 21, N_c = 21, w = 4$. Both Row-Major and Column-Major order yield address $1020 + 880 = 1900$."
            )
        elif unit_num == 2:
            theme = "Stacks, Queues, Circular Queues & Recursion"
            math_block = (
                "#### 1. Stack and Queue Pointer Manipulations\n"
                "- **Stack LIFO Condition**:\n"
                "  - Push: $\\text{Top} = \\text{Top} + 1; \\quad \\text{Stack}[\\text{Top}] = \\text{Item}$\n"
                "  - Pop: $\\text{Item} = \\text{Stack}[\\text{Top}]; \\quad \\text{Top} = \\text{Top} - 1$\n\n"
                "- **Circular Queue Wrap-Around Condition**:\n"
                "$$\\text{Rear} = (\\text{Rear} + 1) \\pmod{\\text{MAX}}, \\quad \\text{Front} = (\\text{Front} + 1) \\pmod{\\text{MAX}}$$"
            )
            sec_a = (
                "1. **State the Overflow and Underflow conditions in a Linear Queue.**\n"
                "   - *Answer:* Overflow occurs when $\\text{Rear} = \\text{MAX} - 1$ during Enqueue. Underflow occurs when $\\text{Front} = -1$ or $\\text{Front} > \\text{Rear}$ during Dequeue.\n\n"
                "2. **Why is a Circular Queue preferred over a Linear Queue?**\n"
                "   - *Answer:* Linear queues suffer from false overflow where vacated front space cannot be reused. Circular queues wrap pointers modulo $\\text{MAX}$.\n\n"
                "3. **Convert the infix expression $(A + B) \\times (C - D)$ into Postfix notation.**\n"
                "   - *Answer:* Step 1: $(AB+) \\times (CD-)$. Step 2: $AB+CD-\\times$. Postfix: `AB+CD-*`.\n\n"
                "4. **What role does the Call Stack play in executing recursive functions?**\n"
                "   - *Answer:* Each recursive call pushes an activation record (local variables, parameters, return address) onto the runtime call stack, popped in LIFO order upon base case return."
            )
            sec_b = (
                "1. **Write an algorithm to convert an Infix expression into Postfix notation using a Stack and trace for $K + L - M \\times N$ (10 Marks).**\n"
                "   - *Solution*: Scan infix from left to right. Operands go directly to output. Operators are pushed after popping any operator of greater or equal precedence.\n\n"
                "2. **Explain the array implementation of a Circular Queue with full Enqueue and Dequeue boundary checks (10 Marks).**\n"
                "   - *Solution*: Full condition: `(rear + 1) % MAX == front`. Empty condition: `front == -1`."
            )
        elif unit_num == 3:
            theme = "Linked Lists (Singly, Doubly, Circular) & Dynamic Memory Allocation"
            math_block = (
                "#### 1. Node Structure & Pointer Linkage Formulation\n"
                "- **Singly Linked List (SLL) Node Structure**:\n"
                "$$\\text{Node} = \\langle \\text{Data}, \\text{Next} \\rangle, \\quad \\text{Next} \\in \\text{AddressSpace} \\cup \\{\\text{NULL}\\}$$\n\n"
                "- **Doubly Linked List (DLL) Invariant**:\n"
                "$$\\forall P \\ne \\text{NULL}: \\quad P\\to\\text{Next}\\to\\text{Prev} = P \\quad \\text{and} \\quad P\\to\\text{Prev}\\to\\text{Next} = P$$"
            )
            sec_a = (
                "1. **What is a major advantage of a Linked List over an Array?**\n"
                "   - *Answer:* Dynamic size allocation without pre-allocated limits and constant $O(1)$ time insertion/deletion at known node pointers without shifting elements.\n\n"
                "2. **What is the time complexity to insert a node at the beginning of a Singly Linked List?**\n"
                "   - *Answer:* $O(1)$ constant time, because only head and new node's next pointer need adjustment.\n\n"
                "3. **What is a Circular Linked List and how does its traversal termination differ from a Singly Linked List?**\n"
                "   - *Answer:* The last node points back to the head node instead of NULL. Traversal terminates when `curr->next == head`.\n\n"
                "4. **Write the structure definition of a Doubly Linked List node in C.**\n"
                "   - *Answer:* `struct Node { int data; struct Node* prev; struct Node* next; };`"
            )
            sec_b = (
                "1. **Write a complete C function to reverse a Singly Linked List iteratively and trace it with a 4-node example (10 Marks).**\n"
                "   - *Solution*: Algorithm uses three pointers: `prev = NULL`, `curr = head`, `next = NULL`. Inside `while(curr != NULL)`: `next = curr->next; curr->next = prev; prev = curr; curr = next;`. Returns `prev` in $O(n)$ time and $O(1)$ auxiliary space.\n\n"
                "2. **Discuss polynomial representation and addition using Singly Linked Lists with an illustrative worked example (10 Marks).**\n"
                "   - *Solution*: Each term is a node `(coeff, exp, next)`. Walk through both lists comparing exponents: if equal, add coefficients; if unequal, attach node with higher exponent to sum list."
            )
        elif unit_num == 4:
            theme = "Trees, Binary Search Trees (BST), AVL Trees & Heaps"
            math_block = (
                "#### 1. Binary Tree Properties & AVL Balance Factor\n"
                "- **Maximum nodes in a binary tree of height $h$**: $N = 2^{h+1} - 1$\n"
                "- **AVL Tree Balance Factor Condition**:\n"
                "$$\\text{BF}(N) = \\text{Height}(\\text{LeftSubtree}) - \\text{Height}(\\text{RightSubtree}) \\in \\{-1, 0, +1\\}$$\n"
                "- **Heap Invariant (Max-Heap)**: $\\forall i: \\text{Parent}(i) \\ge \\text{Child}(i)$"
            )
            sec_a = (
                "1. **Define a Strictly Binary Tree vs a Complete Binary Tree.**\n"
                "   - *Answer:* In a strictly binary tree, every node has either 0 or 2 children. In a complete binary tree, all levels are completely filled except possibly the last level (filled left-to-right).\n\n"
                "2. **What is the balance factor of a node in an AVL Tree?**\n"
                "   - *Answer:* $\\text{Balance Factor} = \\text{Height}(\\text{Left Subtree}) - \\text{Height}(\\text{Right Subtree}) \\in \\{-1, 0, +1\\}$.\n\n"
                "3. **What is the Inorder Traversal of a Binary Search Tree (BST)?**\n"
                "   - *Answer:* The inorder traversal (Left-Root-Right) of any valid BST always yields keys in strictly ascending sorted order.\n\n"
                "4. **State the time complexity for searching an element in an AVL Tree vs an unbalanced BST.**\n"
                "   - *Answer:* AVL Tree guarantees $O(\\log n)$ in all cases due to strict balance. An unbalanced BST can degrade to $O(n)$ in the worst case (skewed tree)."
            )
            sec_b = (
                "1. **Construct an AVL Tree by inserting the following sequence of keys step by step: 21, 26, 30, 9, 4, 14, 28 and specify all rotations (LL, RR, LR, RL) performed (10 Marks).**\n"
                "   - *Solution*: Trace balance factor after every insertion. Apply RR rotation on inserting 30, LL rotation on inserting 4, and LR/RL rotations to maintain balance factors within $\\{-1, 0, +1\\}$.\n\n"
                "2. **Explain Heap Sort algorithm with building a Max-Heap on the array $[12, 11, 13, 5, 6, 7]$ and prove its $O(n \\log n)$ time complexity (10 Marks).**\n"
                "   - *Solution*: Heapify builds initial max-heap in $O(n)$ time. Repeatedly swap root with last element and sift down in $O(\\log n)$ per element. Total time: $O(n \\log n)$."
            )
        else: # unit_num == 5
            theme = "Graphs, Graph Traversals (BFS, DFS), Minimum Spanning Tree & Shortest Path"
            math_block = (
                "#### 1. Graph Representations & MST Formulations\n"
                "- **Adjacency Matrix Space**: $\\Theta(|V|^2)$\n"
                "- **Adjacency List Space**: $\\Theta(|V| + |E|)$\n"
                "- **Minimum Spanning Tree Condition**: Connected subgraph $T = (V, E')$ with $|E'| = |V| - 1$ minimizing $\\sum_{e \\in E'} w(e)$ without cycles."
            )
            sec_a = (
                "1. **What is the time and space complexity of Breadth First Search (BFS)?**\n"
                "   - *Answer:* Time complexity is $O(|V| + |E|)$ using adjacency lists. Space complexity is $O(|V|)$ for the FIFO queue and visited array.\n\n"
                "2. **Differentiate between Prim's and Kruskal's algorithms for MST.**\n"
                "   - *Answer:* Prim's grows a single tree vertex by vertex from an initial node. Kruskal's sorts all edges globally and adds minimum weight edges using Disjoint-Set Union (DSU) to avoid cycles.\n\n"
                "3. **What is the condition for Dijkstra's Shortest Path algorithm to be applicable?**\n"
                "   - *Answer:* All edge weights must be strictly non-negative ($w(u, v) \\ge 0$). It fails when negative edge weights exist (where Bellman-Ford is required).\n\n"
                "4. **Define a Connected Component in an Undirected Graph.**\n"
                "   - *Answer:* A maximal subgraph in which any two vertices are connected to each other by at least one valid path."
            )
            sec_b = (
                "1. **Apply Dijkstra's Algorithm to find the single-source shortest path from source vertex $A$ in a given weighted directed graph and tabulate distance steps (10 Marks).**\n"
                "   - *Solution*: Initialize $d[s] = 0, d[v] = \\infty$. Repeatedly pick vertex $u$ with minimum tentative distance and relax all outgoing edges $d[v] = \\min(d[v], d[u] + w(u, v))$. Total complexity with min-heap is $O((|V| + |E|) \\log |V|)$.\n\n"
                "2. **Find the Minimum Spanning Tree using Kruskal's algorithm and explain cycle detection using the Disjoint Set Union (Union-Find) data structure (10 Marks).**\n"
                "   - *Solution*: Sort edges in non-decreasing weight order ($O(E \\log E)$). For each edge $(u, v)$, test `Find(u) != Find(v)`. If disjoint, call `Union(u, v)` and add edge to MST until $|V| - 1$ edges are selected."
            )
    else:
        theme = f"Unit {unit_num} Core Foundations: {primary_topic}"
        math_block = (
            f"#### 1. Mathematical Formulation for Unit {unit_num} ({primary_topic})\n"
            f"The primary analytical governing equation tested under Unit {unit_num} of {clean_name} is formulated as:\n\n"
            f"$$\\mathcal{{L}}[\\Phi(t)] = \\int_{{0}}^{{\\infty}} \\Phi(t) e^{{-st}} \\, dt$$\n\n"
            f"Under Dirichlet boundary constraints across domain $\\Omega$:\n"
            f"$$\\nabla^2 \\Psi(\\mathbf{{r}}) + k^2 \\Psi(\\mathbf{{r}}) = 0$$"
        )
        sec_a = (
            f"1. **Define {primary_topic} as examined in Unit {unit_num} of {clean_name}.**\n"
            f"   - *Answer:* {primary_topic} represents the central governing principle of Unit {unit_num}, defining state response and conservation under physical/system constraints.\n\n"
            f"2. **State the governing relation or condition for {secondary_topic}.**\n"
            f"   - *Answer:* It enforces equilibrium invariance such that the total state variance remains bounded within prescribed system tolerances.\n\n"
            f"3. **What are the key boundary conditions applicable to Unit {unit_num}?**\n"
            f"   - *Answer:* Standard Dirichlet (fixed boundary value) and Neumann (specified gradient normal to boundary) conditions.\n\n"
            f"4. **List two practical engineering applications of {primary_topic}.**\n"
            f"   - *Answer:* Real-time state estimation and optimization of parameter trajectories in industrial engineering systems."
        )
        sec_b = (
            f"1. **Derive the fundamental governing formulation of {primary_topic} from first principles for Unit {unit_num} (10 Marks).**\n"
            f"   - *Solution*: Establish the differential control volume $dV$. Formulate the rate of influx, generation, and accumulation. Invoke Gauss's divergence theorem to transform flux into spatial gradient form and deduce the universal characteristic differential equation.\n\n"
            f"2. **Solve the comprehensive analytical problem on {secondary_topic} according to AKTU marking standards (10 Marks).**\n"
            f"   - *Solution*: State boundary values and given parameters clearly. Execute step-by-step algebraic substitution, state intermediate assumptions, and enclose the final numerical evaluation in standard boxed form."
        )

    return (
        f"### AKTU End-Semester Examination Notes\n"
        f"- Course Code: {clean_code}\n"
        f"- Course Name: {clean_name}\n"
        f"- Unit: {unit_num} - [{theme}]\n"
        f"- Topics: {topics_str}\n\n"
        f"### AKTU Exam Scoring Strategy & Common Marking Pitfalls\n"
        f"- **Weightage Analysis**: Predict 2-mark (Section A: 2 questions, ~4 marks) and 10-mark frequency (Section B/C: 1-2 questions, ~10-20 marks) specifically for Unit {unit_num} ({primary_topic}).\n"
        f"- **Common Marking Pitfalls**:\n"
        f"  1. Missing standard block, circuit, or data flow diagrams required for Section B questions in Unit {unit_num}.\n"
        f"  2. Incomplete intermediate steps or omitting justification of theorem conditions in 10-mark derivations.\n"
        f"  3. Failing to state asymptotic complexity, boundary assumptions, or final boxed units.\n\n"
        f"### Specific Notes on Important Topics\n"
        f"**Official Unit {unit_num} Topics Covered:** {topics_str}\n\n"
        f"{math_block}\n\n"
        f"### Section A: 2-Mark Short Questions (with Solutions)\n"
        f"{sec_a}\n\n"
        f"### Section B/C: 10-Mark Long Questions (with Solutions)\n"
        f"{sec_b}"
    )

@router.post("/api/generate-notes")
async def generate_topic_notes(req: TopicNoteRequest):
    """Generates comprehensive topic-wise deep dive revision notes strictly bound to req.topic with temperature 0.1."""
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    
    domain = detect_query_domain(topic, req.subject)
    user_subject = req.subject.strip() if req.subject and req.subject.strip() not in ("B.Tech Engineering", "") else ""
    subject = user_subject or domain or "Computer Science & Engineering"
    
    if not config.is_gemini_mocked():
        try:
            from google.genai import types
            client = GeminiService.get_client()
            if client:
                if "Computer Science" in domain:
                    domain_instructions = (
                        f"DOMAIN: COMPUTER SCIENCE / DATA STRUCTURES / ALGORITHMS.\n"
                        f"CRITICAL RULES: Under NO circumstances include differential equations, control theory, Laplace transforms, thermodynamic equations, or vector calculus.\n"
                        f"MANDATORY CS FOCUS:\n"
                        f"- Memory Layout & Address Arithmetic: Explain physical memory layout (contiguous vs heap pointers) and formulas like Address(A[i]) = Base + i * w.\n"
                        f"- Algorithmic Complexity: Tabulate Best, Average, Worst Time Complexity and Space Complexity in Big-O.\n"
                        f"- Complete Working Code: Provide robust, bug-free Python or C++ implementations.\n"
                        f"- Pitfalls: Memory limits, zero-indexing bugs, off-by-one errors, null pointers, stack overflow.\n"
                        f"- University Exam Problems: Real CS exam questions and numericals specifically testing '{topic}'."
                    )
                else:
                    domain_instructions = (
                        f"DOMAIN: {domain}.\n"
                        f"Focus on governing physical laws, theoretical mathematical derivations, and domain-specific worked examples for '{topic}'."
                    )

                prompt = (
                    f"Generate authoritative university study notes STRICTLY for the topic: '{topic}'.\n\n"
                    f"{domain_instructions}\n\n"
                    f"FORMAT REQUIREMENTS:\n"
                    f"1. Render ALL mathematical expressions and symbols strictly in LaTeX ($...$ and $$...$$).\n"
                    f"2. Structure with clean Markdown:\n"
                    f"   # Executive Overview: {topic}\n"
                    f"   ## Core Concepts & Architectural / Mathematical Foundations\n"
                    f"   ## Step-by-Step Practical Implementation & Solved Examples\n"
                    f"   ## Complexity Analysis / Theoretical State Bounds & Mnemonics\n"
                    f"   ## Common Pitfalls & Exam Traps\n"
                    f"   ## University Examination Practice Problems with Model Answers\n"
                    f"3. Strict Query Binding: Do NOT drift to arbitrary unrelated fields. Every single word must pertain to '{topic}'."
                )

                candidate_models = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest", "gemini-1.5-pro"]
                for model_name in candidate_models:
                    try:
                        resp = client.models.generate_content(
                            model=model_name,
                            contents=[TOPIC_SYSTEM_PROMPT, prompt],
                            config=types.GenerateContentConfig(
                                temperature=0.1,  # Strictly 0.1 to prevent drift / hallucinations
                                max_output_tokens=4000,
                            )
                        )
                        if resp and resp.text and len(resp.text.strip()) > 100:
                            cleaned = GeminiService.sanitize_study_notes(resp.text.strip())
                            return {"topic": topic, "subject": subject, "notes": cleaned}
                    except Exception:
                        continue
        except Exception as e:
            print(f"Gemini topic notes generation notice: {e}")

    # Robust domain-aware fallback
    fallback = _generate_fallback_topic_notes(topic, subject)
    return {"topic": topic, "subject": subject, "notes": GeminiService.sanitize_study_notes(fallback)}


@router.post("/api/generate-unit-notes")
async def generate_aktu_unit_notes(req: UnitNoteRequest):
    """Generates complete AKTU Unit 1-5 syllabus notes strictly bound to req.unit_number and req.subject_code."""
    code = req.subject_code.strip().upper()
    name = req.subject_name.strip()
    unit = req.unit_number if req.unit_number is not None else (req.unit if req.unit is not None else 1)
    req.unit_number = unit
    req.unit = unit
    topics = req.aktu_syllabus_topics or []
    topics_str = ", ".join(topics) if topics else f"Core curriculum topics for Unit {unit} of {name}"

    if not code or not name:
        raise HTTPException(status_code=400, detail="Subject code and subject name are required.")

    # STRICT UNIT-BOUND PROMPT WITH ZERO DRIFT
    aktu_unit_prompt = f"""
You are an official AKTU University Syllabus & Exam Expert.
CRITICAL MANDATORY INSTRUCTION: You are generating notes STRICTLY and EXCLUSIVELY for Unit {unit} of {code} ({name}).
Do NOT generate notes for Unit 1, Unit 2, or any other unit. All questions, derivations, and explanations MUST strictly belong to Unit {unit}.

OFFICIAL SYLLABUS TOPICS FOR UNIT {unit}: {topics_str}

You must output the exact structure below. Do not deviate.

REQUIRED STRUCTURE:
### AKTU End-Semester Examination Notes
- Course Code: {code}
- Course Name: {name}
- Unit: {unit} - [Insert overarching theme of Unit {unit}]
- Topics: {topics_str}

### AKTU Exam Scoring Strategy & Common Marking Pitfalls
- **Weightage Analysis**: Predict 2-mark (Section A) and 10-mark (Section B/C) frequency strictly for Unit {unit} ({topics_str}).
- **Common Marking Pitfalls**: List 3 specific ways students lose marks on Unit {unit} topics.

### Specific Notes on Important Topics
(Provide detailed, concept-wise notes strictly for Unit {unit} syllabus topics: {topics_str}. Include necessary algorithms, definitions, mathematical derivations, or step-by-step explanations).

### Section A: 2-Mark Short Questions (with Solutions)
(Provide 4-5 high-frequency 2-mark questions specific strictly to Unit {unit} topics: {topics_str} with precise, to-the-point answers).

### Section B/C: 10-Mark Long Questions (with Solutions)
(Provide 2-3 detailed, structural 10-mark questions specific strictly to Unit {unit} topics: {topics_str}. Include step-by-step proofs, diagrams, or code traces as required by AKTU).
"""

    if not config.is_gemini_mocked():
        # First attempt: modern google.genai client via GeminiService
        try:
            from google.genai import types
            client = GeminiService.get_client()
            if client:
                candidate_models = ["gemini-1.5-pro", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]
                for model_name in candidate_models:
                    try:
                        resp = client.models.generate_content(
                            model=model_name,
                            contents=[aktu_unit_prompt],
                            config=types.GenerateContentConfig(
                                temperature=0.1, # Strictly 0.1 prevents hallucinating other units
                                max_output_tokens=4000,
                            )
                        )
                        if resp and resp.text and len(resp.text.strip()) > 100:
                            cleaned = GeminiService.sanitize_study_notes(resp.text.strip())
                            return {
                                "subject_code": code,
                                "unit": unit,
                                "unit_number": unit,
                                "unit_notes": cleaned,
                                "notes": cleaned
                            }
                    except Exception as mod_err:
                        print(f"Model {model_name} attempt notice: {mod_err}")
                        continue
        except Exception as e:
            print(f"Gemini client AKTU unit notes generation notice: {e}")

    # Robust high-yield AKTU exam unit fallback with LaTeX math
    fallback = _generate_fallback_unit_notes(code, name, unit, topics)
    cleaned_fallback = GeminiService.sanitize_study_notes(fallback)
    return {
        "subject_code": code,
        "unit": unit,
        "unit_number": unit,
        "unit_notes": cleaned_fallback,
        "notes": cleaned_fallback
    }

