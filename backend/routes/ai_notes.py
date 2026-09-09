"""
Isolated Dual-Engine AI Note Making Routes
Provides dedicated endpoints:
- POST /api/generate-notes (Topic-Wise deep dive notes)
- POST /api/generate-unit-notes (AKTU Unit 1-5 syllabus notes)
"""

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import re
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from backend.services.gemini_service import GeminiService
from backend import config

_THREAD_POOL = ThreadPoolExecutor(max_workers=4)
_TOPIC_NOTES_CACHE: Dict[str, Dict[str, Any]] = {}
_AKTU_UNIT_CACHE: Dict[str, Dict[str, Any]] = {}

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
    "You are a Distinguished Senior University Engineering Professor, Department Chair, and Chief Examination Evaluator. "
    "Your mandate is to generate exhaustive, authoritative, textbook-chapter grade academic revision notes of MAXIMUM DEPTH AND SIZE "
    "bound strictly and exclusively to the user's requested topic.\n"
    "CRITICAL DOMAIN & REALISM RULES:\n"
    "1. DOMAIN DISCRIMINATION & REALISTIC MATHEMATICS:\n"
    "   - For COMPUTER SCIENCE, DATA STRUCTURES, ALGORITHMS & SYSTEMS (e.g., Array, Linked List, Recursion, Stack, Queue, Tree, Graph, Hashing, Sorting, Pointer, OS, DBMS, Networks, Complexity):\n"
    "     * DO NOT generate differential equations, Laplace transforms, control systems, divergence/curl gradients, or thermodynamic laws.\n"
    "     * Formulate mathematical foundations STRICTLY relevant to CS: memory addressing formulas (e.g., Address(A[i]) = Base + (i - LB) * w), 2D Row-Major/Column-Major equations, asymptotic recurrence relations (e.g., Master Theorem, T(n) = aT(n/b) + f(n)), Big-O bounds ($O(1)$, $O(n)$, $O(\\log n)$), tree height/node theorems, collision probability, pointer arithmetic, and algorithmic state invariants.\n"
    "     * Include clean, complete, production-grade idiomatic code implementations (Python/C/C++) with thorough comments, edge-case handling, and boundary assertions.\n"
    "   - For CORE ENGINEERING & MATHEMATICS (e.g., Calculus, Linear Algebra, Circuits, Thermodynamics, Fluid Dynamics, Mechanics):\n"
    "     * Formulate authentic governing equations (e.g., Kirchhoff's laws, Thevenin equivalent, Maxwell's equations, Carnot efficiency, Bernoulli's equation, Navier-Stokes, Taylor series, differential equations) with complete step-by-step physical derivations.\n"
    "2. STRICT TOPIC BINDING: Every section, example, code snippet, and examination question must correspond directly to the exact requested topic without wandering or irrelevant template filler.\n"
    "3. MAXIMUM DEPTH & EXHAUSTIVE STRUCTURE: Do NOT abbreviate or truncate. Provide multi-page, comprehensive depth covering:\n"
    "   # Executive Overview & Theoretical Foundations\n"
    "   ## Core Concepts & Architectural / Mathematical Linchpins\n"
    "   ## Physical Memory Layout & Structural Representation\n"
    "   ## Production-Grade Implementation & Boundary Validation (Full working code in Python and C/C++)\n"
    "   ## Step-by-Step Solved Numericals & Algorithmic Traces (Real numbers, step-by-step calculation)\n"
    "   ## Complexity Analysis & Asymptotic Matrix (Best, Average, Worst, Auxiliary Space, Stability)\n"
    "   ## Real-World Pitfalls, Common Bugs & Exam Traps\n"
    "   ## University Examination Practice Problems with Model Answers (Section A 2-Mark & Section B/C 10-Mark Solved Questions)\n"
    "4. LATEX MATH: Render ALL mathematical expressions and variables in standard LaTeX ($inline$ and $$display$$)."
)

AKTU_UNIT_PROMPT = (
    "You are an official AKTU Senior University Engineering Professor, Exam Paper Setter, and Chief Evaluator. "
    "Your mandate is to generate high-yield, exhaustive active revision notes of MAXIMUM DEPTH AND SIZE tailored strictly for AKTU End-Semester Examinations.\n"
    "CRITICAL FORMAT RULES:\n"
    "1. Deep concept breakdowns with explicit formulas (e.g., Row-Major vs. Column-Major address equations, Big-O tables, recurrence relations, circuit models, RTL transfers) and complete C/C++ code snippets.\n"
    "2. Exactly 5 Fully Solved Section A (2-Mark) direct short questions with high-scoring model answers.\n"
    "3. Exactly 3 Fully Solved Section B/C (10-Mark) AKTU past-year numericals, comprehensive proofs, and derivations with step-by-step math solutions.\n"
    "4. Standard LaTeX ($inline$ and $$display$$) across all equations and variables."
)

from backend.routes.topic_notes_engine import detect_academic_domain, build_realistic_topic_notes

def detect_query_domain(topic: str, subject: str = "") -> str:
    """Accurately classifies the academic domain of a query using the realistic topic notes engine."""
    return detect_academic_domain(topic, subject)

def _generate_fallback_topic_notes(topic: str, subject: str) -> str:
    """Generates exhaustive, textbook-chapter grade realistic revision notes bound strictly to the topic."""
    return build_realistic_topic_notes(topic, subject)


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
    
    is_ds_subject = (
        clean_code == "KCS301" or
        ("data structure" in clean_name.lower() and not any(k in clean_name.lower() for k in ["organization", "architecture", "system", "network", "automata", "compiler", "discrete", "microprocessor"]))
    )
    
    if is_ds_subject:
        array_theme = "Arrays, Searching, Sorting & Asymptotic Analysis"
        array_math = (
            "#### 1. One-Dimensional & Multi-Dimensional Array Addressing\n"
            "In contiguous memory allocation, element addresses are computed in constant $O(1)$ time:\n\n"
            "- **1D Array Address Formula**:\n"
            "$$\\text{Address}(A[i]) = \\text{Base} + (i - \\text{LB}) \\times w$$\n\n"
            "- **2D Row-Major Order (RMO)**:\n"
            "$$\\text{Address}(A[i][j]) = \\text{Base} + \\Big( (i - \\text{LB}_r) \\times N_c + (j - \\text{LB}_c) \\Big) \\times w$$\n\n"
            "- **2D Column-Major Order (CMO)**:\n"
            "$$\\text{Address}(A[i][j]) = \\text{Base} + \\Big( (j - \\text{LB}_c) \\times N_r + (i - \\text{LB}_r) \\Big) \\times w$$\n\n"
            "#### 2. Asymptotic Complexity Comparison Table\n\n"
            "| Algorithm | Best Time | Average Time | Worst Time | Space Complexity |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| **Linear Search** | $O(1)$ | $O(n)$ | $O(n)$ | $O(1)$ |\n"
            "| **Binary Search** | $O(1)$ | $O(\\log n)$ | $O(\\log n)$ | $O(1)$ |\n"
            "| **Bubble / Insertion Sort** | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ |\n"
            "| **Merge Sort** | $O(n \\log n)$ | $O(n \\log n)$ | $O(n \\log n)$ | $O(n)$ |\n"
            "| **Quick Sort** | $O(n \\log n)$ | $O(n \\log n)$ | $O(n^2)$ | $O(\\log n)$ |\n\n"
            "#### 3. C/C++ Binary Search Implementation\n"
            "```c\n"
            "int binarySearch(int arr[], int low, int high, int key) {\n"
            "    while (low <= high) {\n"
            "        int mid = low + (high - low) / 2;\n"
            "        if (arr[mid] == key) return mid;\n"
            "        if (arr[mid] < key) low = mid + 1;\n"
            "        else high = mid - 1;\n"
            "    }\n"
            "    return -1;\n"
            "}\n"
            "```"
        )
        array_sec_a = (
            "1. **Q1: Define Big-O, Big-Omega, and Big-Theta asymptotic notations.**\n"
            "   - *Answer:* $O(g(n))$ defines an asymptotic upper bound ($f(n) \\le c \\cdot g(n)$); $\\Omega(g(n))$ defines an asymptotic lower bound ($f(n) \\ge c \\cdot g(n)$); $\\Theta(g(n))$ defines an asymptotically tight bound.\n\n"
            "2. **Q2: State the base address formula for an array in Row Major Order.**\n"
            "   - *Answer:* $\\text{Address}(A[i][j]) = \\text{Base} + [(i - \\text{LB}_1) \\times N_2 + (j - \\text{LB}_2)] \\times w$, where $N_2$ is number of columns.\n\n"
            "3. **Q3: What is the worst-case and best-case time complexity of Quick Sort?**\n"
            "   - *Answer:* Best-case is $O(n \\log n)$ when partition is balanced; worst-case is $O(n^2)$ when partition is completely skewed (already sorted list with extremal pivot).\n\n"
            "4. **Q4: Differentiate between Linear Search and Binary Search.**\n"
            "   - *Answer:* Linear search works on unsorted arrays in $O(n)$ time. Binary search requires a sorted array and executes in $O(\\log n)$ time using divide-and-conquer.\n\n"
            "5. **Q5: State the Best, Average, and Worst Case time complexity of Merge Sort and its auxiliary space complexity.**\n"
            "   - *Answer:* Merge Sort requires $O(n \\log n)$ time in Best, Average, and Worst cases via recurrence $T(n) = 2T(n/2) + O(n)$. Auxiliary space complexity is $O(n)$ for temporary merging arrays."
        )
        array_sec_b = (
            "1. **Q1 (Numerical / Derivation): Explain the working of Binary Search on a sorted array and prove its logarithmic time complexity (10 Marks).**\n"
            "   - *Solution*: At each step, the search interval is halved ($T(n) = T(n/2) + c$). Via Master Theorem with $a = 1, b = 2$ and $f(n) = c = O(n^0)$:\n"
            "     Since $n^{\\log_b a} = n^{\\log_2 1} = n^0 = 1$, Case 2 applies, proving $T(n) = \\Theta(\\log n)$. In the worst case, after $k$ divisions, $n / 2^k = 1 \\implies k = \\log_2 n$ comparisons.\n\n"
            "2. **Q2 (Numerical / Derivation): Calculate the address of $A[5][20]$ in an array $A[-5 \\dots 15, 10 \\dots 30]$ with Base Address 1020 and 4 bytes per element in both Row-Major and Column-Major order (10 Marks).**\n"
            "   - *Solution*: Given $\\text{LB}_1 = -5, \\text{UB}_1 = 15 \\implies N_r = 15 - (-5) + 1 = 21$. $\\text{LB}_2 = 10, \\text{UB}_2 = 30 \\implies N_c = 30 - 10 + 1 = 21$. $w = 4$.\n"
            "     - **Row-Major Order**:\n"
            "       $$\\text{Address} = 1020 + \\big( (5 - (-5)) \\times 21 + (20 - 10) \\big) \\times 4 = 1020 + (10 \\times 21 + 10) \\times 4 = 1020 + 880 = 1900$$\n"
            "     - **Column-Major Order**:\n"
            "       $$\\text{Address} = 1020 + \\big( (20 - 10) \\times 21 + (5 - (-5)) \\big) \\times 4 = 1020 + (210 + 10) \\times 4 = 1020 + 880 = 1900$$.\n\n"
            "3. **Q3 (Algorithmic / Code Trace): Explain the 3-Tuple representation of a Sparse Matrix and write a complete C function for Simple Transposition with time complexity analysis (10 Marks).**\n"
            "   - *Solution*: A sparse matrix with $m$ rows, $n$ columns, and $k$ non-zero elements is represented in a $(k+1) \\times 3$ array where row 0 holds $\\langle m, n, k \\rangle$, and each subsequent row holds $\\langle \\text{row}, \\text{col}, \\text{val} \\rangle$.\n"
            "     ```c\n"
            "     void transposeSparse(int a[][3], int b[][3]) {\n"
            "         int n = a[0][2], k = 1;\n"
            "         b[0][0] = a[0][1]; b[0][1] = a[0][0]; b[0][2] = n;\n"
            "         for (int col = 0; col < a[0][1]; col++) {\n"
            "             for (int p = 1; p <= n; p++) {\n"
            "                 if (a[p][1] == col) {\n"
            "                     b[k][0] = a[p][1]; b[k][1] = a[p][0]; b[k][2] = a[p][2];\n"
            "                     k++;\n"
            "                 }\n"
            "             }\n"
            "         }\n"
            "     }\n"
            "     ```\n"
            "     Time complexity is $O(n \\times k)$ where $n$ is columns and $k$ is non-zero elements. Fast Transpose optimizes this to $O(n + k)$ using position frequencies."
        )

        stack_theme = "Stacks, Queues, Circular Queues & Recursion"
        stack_math = (
            "#### 1. Stack and Queue Pointer Manipulations\n"
            "- **Stack LIFO Invariant**:\n"
            "  $$\\text{Push}: \\text{Top} = \\text{Top} + 1, \\quad \\text{Stack}[\\text{Top}] = \\text{Item}$$\n"
            "  $$\\text{Pop}: \\text{Item} = \\text{Stack}[\\text{Top}], \\quad \\text{Top} = \\text{Top} - 1$$\n\n"
            "- **Circular Queue Wrap-Around Condition**:\n"
            "$$\\text{Rear} = (\\text{Rear} + 1) \\pmod{\\text{MAX}}, \\quad \\text{Front} = (\\text{Front} + 1) \\pmod{\\text{MAX}}$$\n\n"
            "#### 2. C/C++ Stack Operations Code\n"
            "```c\n"
            "#define MAX 100\n"
            "int stack[MAX], top = -1;\n"
            "void push(int x) { if (top < MAX - 1) stack[++top] = x; }\n"
            "int pop() { return (top >= 0) ? stack[top--] : -1; }\n"
            "int peek() { return (top >= 0) ? stack[top] : -1; }\n"
            "```"
        )
        stack_sec_a = (
            "1. **Q1: State the Overflow and Underflow conditions in a Linear Queue.**\n"
            "   - *Answer:* Overflow occurs when $\\text{Rear} = \\text{MAX} - 1$ during Enqueue. Underflow occurs when $\\text{Front} = -1$ or $\\text{Front} > \\text{Rear}$ during Dequeue.\n\n"
            "2. **Q2: Why is a Circular Queue preferred over a Linear Queue?**\n"
            "   - *Answer:* Linear queues suffer from false overflow where vacated front space cannot be reused. Circular queues wrap pointers modulo $\\text{MAX}$ to fully utilize capacity.\n\n"
            "3. **Q3: Convert the infix expression $(A + B) \\times (C - D)$ into Postfix notation.**\n"
            "   - *Answer:* Step 1: $(AB+) \\times (CD-)$. Step 2: $AB+CD-\\times$. Postfix: `AB+CD-*`.\n\n"
            "4. **Q4: What role does the Call Stack play in executing recursive functions?**\n"
            "   - *Answer:* Each recursive call pushes an activation record (local variables, parameters, return address) onto the runtime call stack, popped in LIFO order upon base case return.\n\n"
            "5. **Q5: Differentiate between Direct and Indirect Recursion with a minimal code example.**\n"
            "   - *Answer:* Direct recursion occurs when a function calls itself directly (`void A() { A(); }`). Indirect recursion occurs when function `A()` calls `B()`, and `B()` in turn calls `A()`, forming a mutual call cycle."
        )
        stack_sec_b = (
            "1. **Q1 (Algorithmic / Code Trace): Write an algorithm to convert an Infix expression into Postfix notation using a Stack and trace for $K + L - M \\times N + (O \\text{ \textasciicircum } P) \\times W$ (10 Marks).**\n"
            "   - *Solution*: Scan infix from left to right. Operands go directly to output. Operators are pushed after popping any operator of greater or equal precedence. Parentheses `(` are pushed unconditionally; `)` pop until matching `(`.\n"
            "     Trace yields postfix expression: `K L + M N * - O P ^ W * +` with step-by-step stack transition table.\n\n"
            "2. **Q2 (Algorithmic / Code Trace): Explain the array implementation of a Circular Queue with full Enqueue and Dequeue boundary checks, tracing 6 successive operations (10 Marks).**\n"
            "   - *Solution*: Full condition: `(rear + 1) % MAX == front`. Empty condition: `front == -1`.\n"
            "     - Enqueue: `if ((rear + 1) % MAX == front) return OVERFLOW; if (front == -1) front = 0; rear = (rear + 1) % MAX; Q[rear] = val;`\n"
            "     - Dequeue: `if (front == -1) return UNDERFLOW; val = Q[front]; if (front == rear) { front = -1; rear = -1; } else { front = (front + 1) % MAX; }`.\n\n"
            "3. **Q3 (Numerical / Derivation): Solve the Tower of Hanoi problem for $n$ disks. Derive the mathematical recurrence relation for total moves and trace recursive state activation records for $n = 3$ disks (10 Marks).**\n"
            "   - *Solution*: To move $n$ disks from source $A$ to destination $C$ via auxiliary $B$:\n"
            "     Move $n-1$ disks from $A$ to $B$, move $n$-th disk from $A$ to $C$, move $n-1$ disks from $B$ to $C$.\n"
            "     $$T(n) = 2T(n-1) + 1$$\n"
            "     Solving by substitution: $T(n) = 2^n - 1$. For $n = 3$, $T(3) = 2^3 - 1 = 7$ total moves. Complete call stack tree traces depth 3."
        )

        list_theme = "Linked Lists (Singly, Doubly, Circular) & Dynamic Memory Allocation"
        list_math = (
            "#### 1. Node Structure & Pointer Linkage Formulation\n"
            "- **Singly Linked List (SLL) Node Structure**:\n"
            "$$\\text{Node} = \\langle \\text{Data}, \\text{Next} \\rangle, \\quad \\text{Next} \\in \\text{AddressSpace} \\cup \\{\\text{NULL}\\}$$\n\n"
            "- **Doubly Linked List (DLL) Invariant**:\n"
            "$$\\forall P \\ne \\text{NULL}: \\quad P\\to\\text{Next}\\to\\text{Prev} = P \\quad \\text{and} \\quad P\\to\\text{Prev}\\to\\text{Next} = P$$\n\n"
            "#### 2. C/C++ Linked List Node Structures\n"
            "```c\n"
            "struct SLLNode { int data; struct SLLNode* next; };\n"
            "struct DLLNode { int data; struct DLLNode* prev; struct DLLNode* next; };\n"
            "```"
        )
        list_sec_a = (
            "1. **Q1: What is a major advantage of a Linked List over an Array?**\n"
            "   - *Answer:* Dynamic size allocation without pre-allocated limits and constant $O(1)$ time insertion/deletion at known node pointers without shifting elements.\n\n"
            "2. **Q2: What is the time complexity to insert a node at the beginning of a Singly Linked List?**\n"
            "   - *Answer:* $O(1)$ constant time, because only head and new node's next pointer need adjustment.\n\n"
            "3. **Q3: What is a Circular Linked List and how does its traversal termination differ from a Singly Linked List?**\n"
            "   - *Answer:* The last node points back to the head node instead of NULL. Traversal terminates when `curr->next == head`.\n\n"
            "4. **Q4: Write the structure definition of a Doubly Linked List node in C.**\n"
            "   - *Answer:* `struct Node { int data; struct Node* prev; struct Node* next; };`\n\n"
            "5. **Q5: What is a Header Linked List and what algorithmic advantage does it provide?**\n"
            "   - *Answer:* A linked list containing a special dummy node at the beginning. It eliminates special-case checks for inserting or deleting the first node since `head` pointer never needs reassignment."
        )
        list_sec_b = (
            "1. **Q1 (Algorithmic / Code Trace): Write a complete C function to reverse a Singly Linked List iteratively and trace it with a 4-node example (10 Marks).**\n"
            "   - *Solution*: Algorithm uses three pointers: `prev = NULL`, `curr = head`, `next = NULL`.\n"
            "     ```c\n"
            "     struct SLLNode* reverseList(struct SLLNode* head) {\n"
            "         struct SLLNode *prev = NULL, *curr = head, *next = NULL;\n"
            "         while (curr != NULL) {\n"
            "             next = curr->next;  // Store next node\n"
            "             curr->next = prev;  // Reverse current node pointer\n"
            "             prev = curr;        // Advance prev\n"
            "             curr = next;        // Advance curr\n"
            "         }\n"
            "         return prev; // New head\n"
            "     }\n"
            "     ```\n"
            "     Tracing with `1 -> 2 -> 3 -> 4 -> NULL`: At termination, `prev` points to node 4 with reversed links `4 -> 3 -> 2 -> 1 -> NULL` in $O(n)$ time and $O(1)$ auxiliary space.\n\n"
            "2. **Q2 (Algorithmic / Code Trace): Discuss polynomial representation and addition using Singly Linked Lists with an illustrative worked example (10 Marks).**\n"
            "   - *Solution*: Each term is represented as `struct Poly { int coeff; int exp; struct Poly* next; };`.\n"
            "     Given $P_1(x) = 5x^4 + 2x^2 + 1$ and $P_2(x) = 4x^3 - 2x^2 + 3x$:\n"
            "     Traverse both simultaneously comparing exponents: if $e_1 == e_2$, add coefficients; if $e_1 > e_2$, insert $P_1$ term; if $e_1 < e_2$, insert $P_2$ term. Result: $P_{\\text{sum}}(x) = 5x^4 + 4x^3 + 3x + 1$ in $O(m + n)$ time.\n\n"
            "3. **Q3 (Algorithmic / Code Trace): Write complete C functions to insert and delete a node at an arbitrary $k$-th position in a Doubly Linked List with full boundary pointer checks (10 Marks).**\n"
            "   - *Solution*: For insertion of `newNode` after position $k$:\n"
            "     ```c\n"
            "     newNode->next = temp->next;\n"
            "     newNode->prev = temp;\n"
            "     if (temp->next != NULL) temp->next->prev = newNode;\n"
            "     temp->next = newNode;\n"
            "     ```\n"
            "     For deletion: `temp->prev->next = temp->next; if (temp->next != NULL) temp->next->prev = temp->prev; free(temp);` with edge cases for head, tail, and invalid $k$."
        )

        tree_theme = "Trees, Binary Search Trees (BST), AVL Trees & Heaps"
        tree_math = (
            "#### 1. Binary Tree Properties & AVL Balance Factor\n"
            "- **Maximum nodes in a binary tree of height $h$**: $N = 2^{h+1} - 1$\n"
            "- **AVL Tree Balance Factor Condition**:\n"
            "$$\\text{BF}(N) = \\text{Height}(\\text{LeftSubtree}) - \\text{Height}(\\text{RightSubtree}) \\in \\{-1, 0, +1\\}$$\n"
            "- **Heap Invariant (Max-Heap)**: $\\forall i: \\text{Parent}(i) \\ge \\text{Child}(i)$\n\n"
            "#### 2. C/C++ Tree Node Structure\n"
            "```c\n"
            "struct TreeNode {\n"
            "    int key, height;\n"
            "    struct TreeNode *left, *right;\n"
            "    struct TreeNode *parent;\n"
            "};\n"
            "```"
        )
        tree_sec_a = (
            "1. **Q1: Define a Strictly Binary Tree vs a Complete Binary Tree.**\n"
            "   - *Answer:* In a strictly binary tree, every node has either 0 or 2 children. In a complete binary tree, all levels are completely filled except possibly the last level (filled left-to-right).\n\n"
            "2. **Q2: What is the balance factor of a node in an AVL Tree?**\n"
            "   - *Answer:* $\\text{Balance Factor} = \\text{Height}(\\text{Left Subtree}) - \\text{Height}(\\text{Right Subtree}) \\in \\{-1, 0, +1\\}$.\n\n"
            "3. **Q3: What is the Inorder Traversal of a Binary Search Tree (BST)?**\n"
            "   - *Answer:* The inorder traversal (Left-Root-Right) of any valid BST always yields keys in strictly ascending sorted order.\n\n"
            "4. **Q4: State the time complexity for searching an element in an AVL Tree vs an unbalanced BST.**\n"
            "   - *Answer:* AVL Tree guarantees $O(\\log n)$ in all cases due to strict balance. An unbalanced BST can degrade to $O(n)$ in the worst case (skewed tree).\n\n"
            "5. **Q5: Define a Threaded Binary Tree and state its memory advantage over standard binary trees.**\n"
            "   - *Answer:* A binary tree where NULL pointers are replaced by threads pointing to inorder predecessor (left thread) and inorder successor (right thread), enabling stackless traversal without recursion overhead."
        )
        tree_sec_b = (
            "1. **Q1 (Numerical / Derivation): Construct an AVL Tree by inserting the following sequence of keys step by step: 21, 26, 30, 9, 4, 14, 28 and specify all rotations (LL, RR, LR, RL) performed (10 Marks).**\n"
            "   - *Solution*: Trace balance factor after every insertion. Applying RR rotation on inserting 30, LL rotation on inserting 4, and LR/RL rotations maintains height balance factors strictly within $\\{-1, 0, +1\\}$.\n\n"
            "2. **Q2 (Algorithmic / Code Trace): Explain Binary Search Tree (BST) node deletion covering all three cases: leaf node, single-child node, and two-child node (10 Marks).**\n"
            "   - *Solution*: Case 1 (Leaf): Free node, set parent link NULL. Case 2 (Single Child): Parent points to child. Case 3 (Two Children): Find Inorder Successor (minimum in right subtree), copy its value to target, recursively delete successor in $O(h)$ time.\n\n"
            "3. **Q3 (Algorithmic / Code Trace): Explain Heap Sort algorithm with building a Max-Heap on the array $[12, 11, 13, 5, 6, 7]$ and prove its $O(n \\log n)$ time complexity (10 Marks).**\n"
            "   - *Solution*: Heapify builds initial max-heap in $O(n)$ time. Repeatedly swap root with last element and sift down in $O(\\log n)$ per element. Total time: $O(n \\log n)$."
        )

        graph_theme = "Graphs, Graph Traversals (BFS, DFS), Minimum Spanning Tree & Shortest Path"
        graph_math = (
            "#### 1. Graph Representations & MST Formulations\n"
            "- **Adjacency Matrix Space**: $\\Theta(|V|^2)$\n"
            "- **Adjacency List Space**: $\\Theta(|V| + |E|)$\n"
            "- **Minimum Spanning Tree Condition**: Connected subgraph $T = (V, E')$ with $|E'| = |V| - 1$ minimizing $\\sum_{e \\in E'} w(e)$ without cycles.\n\n"
            "#### 2. C/C++ Graph Adjacency List Structure\n"
            "```c\n"
            "struct AdjListNode { int dest, weight; struct AdjListNode* next; };\n"
            "struct Graph { int V; struct AdjListNode** array; };\n"
            "```"
        )
        graph_sec_a = (
            "1. **Q1: What is the time and space complexity of Breadth First Search (BFS)?**\n"
            "   - *Answer:* Time complexity is $O(|V| + |E|)$ using adjacency lists. Space complexity is $O(|V|)$ for the FIFO queue and visited array.\n\n"
            "2. **Q2: Differentiate between Prim's and Kruskal's algorithms for MST.**\n"
            "   - *Answer:* Prim's grows a single tree vertex by vertex from an initial node. Kruskal's sorts all edges globally and adds minimum weight edges using Disjoint-Set Union (DSU) to avoid cycles.\n\n"
            "3. **Q3: What is the condition for Dijkstra's Shortest Path algorithm to be applicable?**\n"
            "   - *Answer:* All edge weights must be strictly non-negative ($w(u, v) \\ge 0$). It fails when negative edge weights exist (where Bellman-Ford is required).\n\n"
            "4. **Q4: Define a Connected Component in an Undirected Graph.**\n"
            "   - *Answer:* A maximal subgraph in which any two vertices are connected to each other by at least one valid path.\n\n"
            "5. **Q5: What is Topological Sorting and under what condition does it exist in a graph?**\n"
            "   - *Answer:* A linear ordering of vertices such that for every directed edge $(u, v)$, vertex $u$ appears before $v$. It exists if and only if the graph is a Directed Acyclic Graph (DAG)."
        )
        graph_sec_b = (
            "1. **Q1 (Numerical / Derivation): Apply Dijkstra's Algorithm to find the single-source shortest path from source vertex $A$ in a given weighted directed graph and tabulate distance steps (10 Marks).**\n"
            "   - *Solution*: Initialize $d[s] = 0, d[v] = \\infty$. Repeatedly pick vertex $u$ with minimum tentative distance and relax all outgoing edges $d[v] = \\min(d[v], d[u] + w(u, v))$. Total complexity with min-heap is $O((|V| + |E|) \\log |V|)$.\n\n"
            "2. **Q2 (Algorithmic / Code Trace): Find the Minimum Spanning Tree using Kruskal's algorithm and explain cycle detection using the Disjoint Set Union (Union-Find) data structure (10 Marks).**\n"
            "   - *Solution*: Sort edges in non-decreasing weight order ($O(E \\log E)$). For each edge $(u, v)$, test `Find(u) != Find(v)`. If disjoint, call `Union(u, v)` and add edge to MST until $|V| - 1$ edges are selected.\n\n"
            "3. **Q3 (Algorithmic / Code Trace): Explain the Breadth-First Search (BFS) and Depth-First Search (DFS) algorithms with queue/stack formulations, proving $O(|V| + |E|)$ complexity and application to bipartite graph testing (10 Marks).**\n"
            "   - *Solution*: BFS traverses level by level via FIFO queue; DFS explores branches via recursive call stack. Bipartite testing colours vertices in 2 alternating colors during BFS traversal; if any adjacent vertex shares the same color, the graph is non-bipartite."
        )

        # STRICT BOUNDARY SCOPE SELECTION (Negative Constraints Lock)
        topics_lower = f"{topics_str}".lower()
        is_linked_list = any(k in topics_lower for k in ["linked", "singly", "doubly", "circular linked", "node"])
        is_stack_queue = any(k in topics_lower for k in ["stack", "queue", "circular queue", "recursion", "infix", "postfix", "hanoi"])
        is_tree = any(k in topics_lower for k in ["tree", "binary tree", "bst", "avl", "b-tree", "traversal"])
        is_graph = any(k in topics_lower for k in ["graph", "bfs", "dfs", "dijkstra", "prim", "kruskal", "mst"])
        is_array = any(k in topics_lower for k in ["array", "searching", "sorting", "row major", "column major", "asymptotic"])

        if unit_num == 1 or (is_array and not (unit_num in [2, 3, 4, 5])):
            theme, math_block, sec_a, sec_b = array_theme, array_math, array_sec_a, array_sec_b
        elif unit_num == 2:
            if is_stack_queue and not is_linked_list:
                theme, math_block, sec_a, sec_b = stack_theme, stack_math, stack_sec_a, stack_sec_b
            else:
                # Unit 2 (Linked Lists): ZERO mention of Stacks, Queues, Circular Queues, Infix/Postfix conversion, or Tower of Hanoi!
                theme, math_block, sec_a, sec_b = list_theme, list_math, list_sec_a, list_sec_b
        elif unit_num == 3:
            if is_linked_list and not is_stack_queue:
                theme, math_block, sec_a, sec_b = list_theme, list_math, list_sec_a, list_sec_b
            else:
                # Unit 3 (Stacks/Queues): ZERO mention of Trees or Graphs!
                theme, math_block, sec_a, sec_b = stack_theme, stack_math, stack_sec_a, stack_sec_b
        elif unit_num == 4 or is_tree:
            theme, math_block, sec_a, sec_b = tree_theme, tree_math, tree_sec_a, tree_sec_b
        elif unit_num == 5 or is_graph:
            theme, math_block, sec_a, sec_b = graph_theme, graph_math, graph_sec_a, graph_sec_b
        elif is_linked_list:
            theme, math_block, sec_a, sec_b = list_theme, list_math, list_sec_a, list_sec_b
        elif is_stack_queue:
            theme, math_block, sec_a, sec_b = stack_theme, stack_math, stack_sec_a, stack_sec_b
        else:
            theme, math_block, sec_a, sec_b = array_theme, array_math, array_sec_a, array_sec_b
    else:
        combined_lower = f"{clean_name} {topics_str}".lower()
        is_cs_it = any(k in combined_lower for k in [
            "computer", "architecture", "organization", "system", "network", "operating", 
            "compiler", "database", "dbms", "logic", "microprocessor", "software", 
            "information", "cloud", "automata", "discrete"
        ])
        theme = f"Unit {unit_num} Core Foundations: {primary_topic}"

        if is_cs_it:
            is_pipelining = any(k in combined_lower for k in ["pipeline", "pipelining", "parallel processing", "vector processor"])
            is_cache_mem = any(k in combined_lower for k in ["cache", "memory hierarchy", "virtual memory", "associative", "paging"])
            is_rtl_coa = any(k in combined_lower for k in ["register transfer", "micro-operation", "bus", "rtl", "arithmetic logic", "shift micro", "alsu"]) or ("kcs302" in clean_code.lower() and unit_num == 1)

            if is_rtl_coa:
                math_block = (
                    f"#### 1. Register Transfer Language (RTL) & Micro-Operations\n"
                    f"- **Register Transfer Notation**:\n"
                    f"  $$P: \\quad R_2 \\leftarrow R_1$$\n"
                    f"  Denotes that if control signal $P = 1$, contents of register $R_1$ are transferred into $R_2$ synchronously on the next active clock edge.\n"
                    f"- **Memory Transfer Notations**:\n"
                    f"  $$\\text{{Read}}: \\quad DR \\leftarrow M[AR], \\qquad \\text{{Write}}: \\quad M[AR] \\leftarrow R_1$$\n"
                    f"- **Common Bus System Multiplexer Logic**:\n"
                    f"  For $k$ registers of $n$ bits each, a multiplexer-based common bus requires $n$ multiplexers of size $k \\times 1$. The selection lines $S_{{\\lceil \\log_2 k \\rceil - 1}} \\dots S_0$ determine which register drives the bus.\n"
                    f"- **Arithmetic Micro-Operations (2's Complement Subtraction)**:\n"
                    f"  $$R_3 \\leftarrow R_1 + \\overline{{R_2}} + 1$$\n"
                    f"- **Arithmetic Shift Overflow Condition**:\n"
                    f"  $$V = R_{{n-1}} \\oplus R_{{n-2}}$$\n"
                    f"  where $V = 1$ indicates arithmetic overflow due to sign-bit corruption."
                )
                sec_a = (
                    f"1. **Q1: Define Register Transfer Language (RTL) as used in {clean_name}.**\n"
                    f"   - *Answer:* A symbolic language used to describe internal micro-operation transfers between registers and memory units using format $P: R_2 \\leftarrow R_1$.\n\n"
                    f"2. **Q2: State the difference between Memory Read and Memory Write in RTL.**\n"
                    f"   - *Answer:* Read transfers word at address $AR$ into Data Register ($DR \\leftarrow M[AR]$). Write transfers register data into memory at address $AR$ ($M[AR] \\leftarrow R_1$).\n\n"
                    f"3. **Q3: How many multiplexers and selection lines are needed to construct a common bus for 8 registers of 16 bits each?**\n"
                    f"   - *Answer:* 16 multiplexers of size $8 \\times 1$, with 3 selection lines ($S_2, S_1, S_0$) since $2^3 = 8$.\n\n"
                    f"4. **Q4: Differentiate between Logical Shift and Arithmetic Shift.**\n"
                    f"   - *Answer:* Logical shift inserts 0 into the vacant bit position. Arithmetic shift preserves the sign bit ($R_{{n-1}}$) during shift right and detects overflow via $V = R_{{n-1}} \\oplus R_{{n-2}}$.\n\n"
                    f"5. **Q5: Write the micro-operation for selective-set and selective-clear.**\n"
                    f"   - *Answer:* Selective-set uses bitwise OR ($A \\leftarrow A \\lor B$). Selective-clear uses bitwise AND with inverted mask ($A \\leftarrow A \\land \\overline{{B}}$)."
                )
                sec_b = (
                    f"1. **Q1 (Architectural Trace): Design a 4-bit Common Bus System for four registers ($A, B, C, D$) using multiplexers and show the complete truth table (10 Marks).**\n"
                    f"   - *Solution*: Use four $4 \\times 1$ multiplexers ($MUX_0$ to $MUX_3$). Selection inputs $S_1 S_0$ determine which register drives the 4-bit common bus lines ($00 \\implies A, 01 \\implies B, 10 \\implies C, 11 \\implies D$).\n\n"
                    f"2. **Q2 (Numerical / Circuit Design): Draw and explain the 4-bit Arithmetic Circuit implemented with a Full Adder and Multiplexers with complete function table (10 Marks).**\n"
                    f"   - *Solution*: Mode inputs $S_1, S_0, C_\\text{{in}}$ control the $Y$ input of Full Adders to produce $D = A + Y + C_\\text{{in}}$, realizing Add, Add with Carry, Subtract ($A + \\overline{{B}} + 1$), Increment ($A + 1$), and Transfer.\n\n"
                    f"3. **Q3 (System / Comparative): Explain the One-Stage Arithmetic Logic Shift Unit (ALSU) with schematic diagram and function table (10 Marks).**\n"
                    f"   - *Solution*: Combines full adder arithmetic stage, bitwise logic operations ($AND, OR, XOR, NOT$), and shift multiplexers ($shr, shl$) selected via 4-bit selection code $S_3 S_2 S_1 S_0$ in single-clock latency."
                )
            elif is_cache_mem:
                math_block = (
                    f"#### 1. Memory Hierarchy & Cache Performance Formulations\n"
                    f"- **Average Memory Access Time (AMAT)**:\n"
                    f"  $$T_\\text{{avg}} = h \\cdot T_c + (1 - h) \\cdot T_m$$\n"
                    f"  where $h$ is cache hit ratio, $T_c$ is cache latency, and $T_m$ is main memory miss penalty.\n"
                    f"- **Cache Line Placement Relations**:\n"
                    f"  $$\\text{{Index}} = (\\text{{Block Address}}) \\pmod{{\\text{{Total Sets}}}}$$"
                )
                sec_a = (
                    f"1. **Q1: Define Hit Ratio and Miss Penalty in Cache Memory.**\n"
                    f"   - *Answer:* Hit ratio $h$ is fraction of memory references satisfied by cache ($0 \\le h \\le 1$). Miss penalty is time required to fetch the required block from main memory.\n\n"
                    f"2. **Q2: State the formula for Average Memory Access Time (AMAT).**\n"
                    f"   - *Answer:* $T_\\text{{avg}} = h \\cdot T_c + (1 - h) \\cdot T_m$.\n\n"
                    f"3. **Q3: Differentiate between Direct Mapping and Fully Associative Mapping.**\n"
                    f"   - *Answer:* Direct mapping assigns each memory block to exactly one specific cache line. Fully associative mapping allows a memory block to reside in any cache line.\n\n"
                    f"4. **Q4: What is the purpose of the Dirty Bit in a Write-Back cache?**\n"
                    f"   - *Answer:* The dirty bit flags whether a cache line has been modified, ensuring memory is only updated upon line eviction.\n\n"
                    f"5. **Q5: Differentiate between Spatial Locality and Temporal Locality.**\n"
                    f"   - *Answer:* Temporal locality refers to reusing recently accessed memory. Spatial locality refers to accessing contiguous memory addresses near recently accessed words."
                )
                sec_b = (
                    f"1. **Q1 (Numerical / Derivation): Calculate AMAT for a two-level cache hierarchy where $L1$ has hit time 1 ns and hit rate 95%, $L2$ has hit time 4 ns and hit rate 80%, and main memory latency is 50 ns (10 Marks).**\n"
                    f"   - *Solution*: $$T_\\text{{avg}} = T_{{L1}} + (1 - h_{{L1}}) \\times (T_{{L2}} + (1 - h_{{L2}}) \\times T_m) = 1 + 0.05 \\times (4 + 0.20 \\times 50) = 1 + 0.05 \\times 14 = 1.7 \\text{{ ns}}.$$\n\n"
                    f"2. **Q2 (Architectural Trace): Compare Direct Mapping, Associative Mapping, and Set-Associative Mapping with tag, line, and word offset field calculations for a 32-bit address space (10 Marks).**\n"
                    f"   - *Solution*: Derive division of 32-bit physical address into Tag, Set/Line Index, and Word Offset. Provide step-by-step memory trace for 8 sequential address references.\n\n"
                    f"3. **Q3 (System / Comparative): Discuss Cache Write Policies: Write-Through vs Write-Back with Write-Allocate vs No-Write-Allocate under heavy memory traffic (10 Marks).**\n"
                    f"   - *Solution*: Analyze bus bandwidth utilization, coherency overhead, and hardware implementation requirements for multiprocessor memory pipelines."
                )
            elif is_pipelining:
                math_block = (
                    f"#### 1. Pipelining & Parallel Execution Formulations\n"
                    f"- **Pipelined Execution Speedup**:\n"
                    f"  $$S = \\frac{{n \\cdot t_n}}{{(k + n - 1) \\cdot t_k}}$$\n"
                    f"- **Amdahl's Law (Parallel Speedup Limit)**:\n"
                    f"  $$S = \\frac{{1}}{{(1 - f) + \\frac{{f}}{{p}}}}$$\n"
                    f"  where $f$ is parallel fraction and $p$ is processor count."
                )
                sec_a = (
                    f"1. **Q1: Define Pipeline Speedup.**\n"
                    f"   - *Answer:* Ratio of execution time of $n$ tasks on a non-pipelined processor ($n \\cdot t_n$) to execution time on a $k$-stage pipeline ($(k + n - 1) \\cdot t_k$).\n\n"
                    f"2. **Q2: State Amdahl's Law formula for parallel processors.**\n"
                    f"   - *Answer:* $S = \\frac{{1}}{{(1 - f) + \\frac{{f}}{{p}}}}$, establishing the asymptotic speedup limit based on the serial fraction $1 - f$.\n\n"
                    f"3. **Q3: List the three primary pipeline hazards.**\n"
                    f"   - *Answer:* Structural hazards (resource conflicts), Data hazards (RAW, WAR, WAW dependencies), and Control hazards (branch/jump instructions).\n\n"
                    f"4. **Q4: How does Operand Forwarding resolve RAW data hazards?**\n"
                    f"   - *Answer:* Routes computed ALU results directly from execution stage registers back to the ALU input without waiting for write-back stage.\n\n"
                    f"5. **Q5: Define Pipeline Efficiency and Throughput.**\n"
                    f"   - *Answer:* Efficiency is $E = \\frac{{S}}{{k}}$. Throughput is instructions completed per second $TP = \\frac{{n}}{{(k + n - 1) \\cdot \\tau}}$."
                )
                sec_b = (
                    f"1. **Q1 (Numerical / Derivation): For a 5-stage pipeline executing 100 instructions with clock cycle 10 ns, calculate speedup, efficiency, and throughput compared to a 50 ns non-pipelined execution (10 Marks).**\n"
                    f"   - *Solution*: Non-pipelined time: $T_1 = 100 \\times 50 = 5000$ ns. Pipelined time: $T_k = (5 + 100 - 1) \\times 10 = 1040$ ns. Speedup $S = 5000 / 1040 = 4.808$. Efficiency $E = 4.808 / 5 = 96.16\\%$. Throughput $TP = 100 / 1040 \\text{{ ns}} = 96.15 \\text{{ MIPS}}$.\n\n"
                    f"2. **Q2 (Architectural Trace): Analyze Data Hazards in pipelined processors with timing space-time diagrams showing stall bubble insertion vs operand forwarding (10 Marks).**\n"
                    f"   - *Solution*: Trace code sequence: `ADD R1, R2, R3` followed by `SUB R4, R1, R5`. Demonstrate 2-cycle stall penalty without forwarding vs 0-cycle stall with EX-to-EX forwarding.\n\n"
                    f"3. **Q3 (System / Comparative): Compare RISC vs CISC pipeline architectures and branch handling methods: Delayed Branching vs Dynamic Branch Prediction (10 Marks).**\n"
                    f"   - *Solution*: Detailed comparative table analyzing branch target buffers (BTB), 2-bit saturating counters, instruction fetch unit design, and branch penalties."
                )
            else:
                math_block = (
                    f"#### 1. Technical Foundations for Unit {unit_num}: {primary_topic}\n"
                    f"- **Operational Invariant**:\n"
                    f"  The functional logic governing `{primary_topic}` enforces deterministic execution states across input parameters without resource deadlocks.\n"
                    f"- **Performance Latency Model**:\n"
                    f"  $$T_\\text{{total}} = \\sum_{{i=1}}^{{m}} \\tau_i + \\Delta t_\\text{{overhead}}$$"
                )
                sec_a = (
                    f"1. **Q1: Define {primary_topic} in the context of {clean_name}.**\n"
                    f"   - *Answer:* {primary_topic} constitutes a fundamental functional module in {clean_name}, governing instruction/state sequencing, resource allocation, and operational invariants.\n\n"
                    f"2. **Q2: State the primary role of {secondary_topic}.**\n"
                    f"   - *Answer:* It coordinates protocol handshaking, signal timing, and control lines to ensure deterministic execution.\n\n"
                    f"3. **Q3: What is the significance of timing and latency in {primary_topic}?**\n"
                    f"   - *Answer:* Clock cycles and propagation latency directly govern total execution time $T = I_c \\times \\text{{CPI}} \\times \\tau$.\n\n"
                    f"4. **Q4: List two practical engineering applications of {primary_topic}.**\n"
                    f"   - *Answer:* Real-time embedded controllers and high-throughput server pipelines rely directly on {primary_topic}.\n\n"
                    f"5. **Q5: State the key design trade-off associated with {primary_topic}.**\n"
                    f"   - *Answer:* Balancing hardware silicon area and power consumption against latency and throughput."
                )
                sec_b = (
                    f"1. **Q1 (Technical Derivation): Formulate the performance equations and timing analysis for {primary_topic} in Unit {unit_num} (10 Marks).**\n"
                    f"   - *Solution*: Draw the complete functional block schematic. Formulate the cycle latencies, stall overheads, and compute overall effective throughput using step-by-step arithmetic.\n\n"
                    f"2. **Q2 (Algorithmic / Architectural Trace): Provide the detailed architectural schematic and control sequence for {secondary_topic} (10 Marks).**\n"
                    f"   - *Solution*: Tabulate the state transition matrix or micro-operation sequence $T_0, T_1, T_2, \\dots$. Trace the data path, control words, and address latching step-by-step.\n\n"
                    f"3. **Q3 (System / Comparative): Compare and contrast the structural alternatives for {primary_topic} under AKTU university exam specifications (10 Marks).**\n"
                    f"   - *Solution*: Construct a rigorous comparative analysis covering design complexity, hardware cost, fault tolerance, and asymptotic performance."
                )
        else:
            from backend.routes.topic_notes_engine import build_realistic_topic_notes
            full_topic = f"{clean_name}: {primary_topic}"
            raw_academic_notes = build_realistic_topic_notes(full_topic, clean_name)
            if raw_academic_notes and len(raw_academic_notes) > 200:
                header = (
                    f"# {clean_code}: Unit {unit_num} - Comprehensive Revision & Exam Guide\n\n"
                    f"### AKTU End-Semester Examination Notes\n"
                    f"- Course Code: {clean_code}\n"
                    f"- Course Name: {clean_name}\n"
                    f"- Unit: {unit_num} - [{primary_topic}]\n"
                    f"- Allowed Topics: [{topics_str}]\n\n"
                )
                return header + raw_academic_notes

            math_block = (
                f"#### 1. Universal Engineering Foundations for Unit {unit_num} ({primary_topic})\n"
                f"Governing system state balance for {clean_name}:\n\n"
                f"$$\\frac{{d \\mathbf{{x}}(t)}}{{dt}} = \\mathbf{{A}} \\mathbf{{x}}(t) + \\mathbf{{B}} \\mathbf{{u}}(t)$$"
            )
            sec_a = (
                f"1. **Q1: Define {primary_topic} as examined in Unit {unit_num} of {clean_name}.**\n"
                f"   - *Answer:* Fundamental governing principle in {clean_name}.\n\n"
                f"2. **Q2: State the primary operational objective of {secondary_topic}.**\n"
                f"   - *Answer:* Coordinates state transitions and enforces equilibrium.\n\n"
                f"3. **Q3: What are the key boundary conditions applicable to Unit {unit_num}?**\n"
                f"   - *Answer:* Standard Dirichlet and Neumann boundary conditions.\n\n"
                f"4. **Q4: List two practical engineering applications of {primary_topic}.**\n"
                f"   - *Answer:* Real-time parameter estimation and process control.\n\n"
                f"5. **Q5: State the dimension and SI unit of the primary coefficient in {primary_topic}.**\n"
                f"   - *Answer:* Standard SI units derived from fundamental dimensional quantities.\n"
            )
            sec_b = (
                f"1. **Q1 (Derivation): Formulate the governing system equation of {primary_topic} from first principles for Unit {unit_num} (10 Marks).**\n"
                f"   - *Solution*: Apply conservation laws across differential volume $dV$ and deduce the governing equations.\n\n"
                f"2. **Q2 (Numerical): Solve the analytical problem on {secondary_topic} according to AKTU standards (10 Marks).**\n"
                f"   - *Solution*: Substitute boundary conditions and state intermediate steps clearly.\n\n"
                f"3. **Q3 (System): Analyze the transient response and stability bounds for Unit {unit_num} (10 Marks).**\n"
                f"   - *Solution*: Construct the characteristic transfer function and apply stability criteria.\n"
            )

    return (
        f"# {clean_code}: Unit {unit_num} - Comprehensive Revision & Exam Guide\n\n"
        f"### AKTU End-Semester Examination Notes\n"
        f"- Course Code: {clean_code}\n"
        f"- Course Name: {clean_name}\n"
        f"- Unit: {unit_num} - [{theme}]\n"
        f"- Allowed Topics: [{topics_str}]\n\n"
        f"## 1. Core Technical Concept Breakdown\n"
        f"### Specific Notes on Important Topics\n"
        f"**Official Unit {unit_num} Topics Covered:** [{topics_str}]\n\n"
        f"### Technical Formulations & Micro-Architectural Foundations\n"
        f"{math_block}\n\n"
        f"## 2. AKTU Exam Scoring Strategy & Pitfalls\n"
        f"### AKTU Exam Scoring Strategy & Common Marking Pitfalls\n"
        f"- **High-Yield Exam Topics**: Core areas tested frequently in AKTU end-sem exams for Unit {unit_num}.\n"
        f"- **High-Yield Areas**: Specific topics within [{topics_str}] tested every year.\n"
        f"- **Common Exam Mistakes**: 3 specific logic, step, or diagram errors students make in this unit.\n"
        f"- **Common Deductions**: 3 specific logic or formatting errors students make on these topics:\n"
        f"  1. Missing standard block, circuit, or data flow diagrams required for Section B questions in Unit {unit_num}.\n"
        f"  2. Incomplete intermediate steps or omitting justification of theorem conditions in 10-mark derivations.\n"
        f"  3. Failing to state asymptotic complexity, boundary assumptions, or final boxed units.\n\n"
        f"## 3. Section A: 2-Mark Short Questions & Answers\n"
        f"### Section A: 2-Mark Short Questions (5 Fully Solved with Solutions)\n"
        f"{sec_a}\n\n"
        f"## 4. Section B & C: 10-Mark Long Questions & Answers\n"
        f"### Section B/C: 10-Mark Long Questions & Numericals (3 Fully Solved with Solutions)\n"
        f"{sec_b}"
    )

def _sync_fetch_gemini_topic_notes(prompt: str) -> Optional[str]:
    candidate_models = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.1-flash-lite", "gemini-3-flash-preview"]
    try:
        from google.genai import types
        client = GeminiService.get_client()
        if not client:
            return None
        for model_name in candidate_models:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=[TOPIC_SYSTEM_PROMPT, prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=8192,
                    )
                )
                if resp and resp.text and len(resp.text.strip()) > 100:
                    return GeminiService.sanitize_study_notes(resp.text.strip())
            except Exception:
                continue
    except Exception:
        pass
    return None

@router.post("/api/generate-notes")
async def generate_topic_notes(req: TopicNoteRequest):
    """Generates comprehensive topic-wise deep dive revision notes strictly bound to req.topic with temperature 0.1."""
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    
    domain = detect_query_domain(topic, req.subject)
    user_subject = req.subject.strip() if req.subject and req.subject.strip() not in ("B.Tech Engineering", "") else ""
    subject = user_subject or domain or "Computer Science & Engineering"

    cache_key = f"{topic.lower()}::{subject.lower()}"
    if cache_key in _TOPIC_NOTES_CACHE:
        return _TOPIC_NOTES_CACHE[cache_key]
    
    if not config.is_gemini_mocked():
        try:
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

            loop = asyncio.get_running_loop()
            gemini_notes = await asyncio.wait_for(
                loop.run_in_executor(_THREAD_POOL, _sync_fetch_gemini_topic_notes, prompt),
                timeout=3.5
            )
            if gemini_notes and len(gemini_notes.strip()) > 100:
                res = {"topic": topic, "subject": subject, "notes": gemini_notes}
                _TOPIC_NOTES_CACHE[cache_key] = res
                return res
        except Exception as e:
            print(f"Gemini topic notes generation notice: {e}")

    # Robust domain-aware fallback (runs in ~1ms)
    fallback = _generate_fallback_topic_notes(topic, subject)
    res = {"topic": topic, "subject": subject, "notes": GeminiService.sanitize_study_notes(fallback)}
    _TOPIC_NOTES_CACHE[cache_key] = res
    return res


def _is_valid_aktu_notes(text: str, u: int, c: str, n: str) -> bool:
    required_sections = [
        "AKTU End-Semester Examination Notes",
        f"Unit: {u}",
        "Specific Notes on Important Topics",
        "AKTU Exam Scoring Strategy & Common Marking Pitfalls",
        "Section A: 2-Mark Short Questions (5 Fully Solved with Solutions)",
        "Section B/C: 10-Mark Long Questions & Numericals (3 Fully Solved with Solutions)",
        "1. **Q1", "2. **Q2", "3. **Q3", "4. **Q4", "5. **Q5"
    ]
    if not all(sec in text for sec in required_sections):
        return False
    lower_name = n.lower()
    clean_code = c.upper()
    if clean_code == "KCS301" or "data structure" in lower_name:
        if u == 2:
            if any(term in text for term in ["Stack", "Queue", "Circular Queue", "Infix", "Postfix", "Tower of Hanoi", "Hanoi"]):
                return False
        elif u == 3:
            if any(term in text for term in ["Tree", "Graph", "Binary Search Tree", "Dijkstra"]):
                return False
    elif "KCS302" in clean_code or "KCS401" in clean_code or "coa" in lower_name or "architecture" in lower_name:
        if u == 1:
            if any(term in text for term in ["Amdahl's Law", "State-Space", "Linked List", "Queue"]):
                return False
    return True

def _sync_fetch_gemini_unit_notes(prompt: str, u: int, c: str, n: str) -> Optional[str]:
    candidate_models = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.1-flash-lite", "gemini-3-flash-preview"]
    try:
        from google.genai import types
        client = GeminiService.get_client()
        if not client:
            return None
        for model_name in candidate_models:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        top_p=0.1,
                        max_output_tokens=8192,
                    )
                )
                if resp and resp.text and len(resp.text.strip()) > 100:
                    cleaned = GeminiService.sanitize_study_notes(resp.text.strip())
                    if _is_valid_aktu_notes(cleaned, u, c, n):
                        return cleaned
            except Exception:
                continue
    except Exception:
        pass
    return None

@router.post("/api/generate-unit-notes")
async def generate_aktu_unit_notes(req: UnitNoteRequest, response: Response):
    """Generates complete AKTU Unit 1-5 syllabus notes strictly bound to req.unit_number and req.subject_code."""
    # FORCE NO-CACHE HEADERS TO STOP BROWSERS FROM RETURNING OLD RESPONSES
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    code = req.subject_code.strip().upper()
    name = req.subject_name.strip()
    unit = req.unit_number if req.unit_number is not None else (req.unit if req.unit is not None else 1)
    req.unit_number = unit
    req.unit = unit
    topics = req.aktu_syllabus_topics or []
    topics_str = ", ".join(topics) if topics else f"Core curriculum topics for Unit {unit} of {name}"

    if not code or not name:
        raise HTTPException(status_code=400, detail="Subject code and subject name are required.")

    cache_key = f"{code}::unit{unit}::{topics_str.lower()}"
    if cache_key in _AKTU_UNIT_CACHE:
        cached = dict(_AKTU_UNIT_CACHE[cache_key])
        cached["timestamp"] = time.time()
        return cached

    # GROUND-TRUTH ENGINE PROMPT (NO BOILERPLATE TEMPLATES)
    aktu_unit_prompt = f"""
    [Generation Timestamp: {time.time()}]
    
You are an expert AKTU University Professor and Exam Specialist for {code} ({name}).

CRITICAL UNIT SCOPE RULES:
1. STRICT BOUNDARY ENFORCEMENT: Output revision notes ONLY for Unit {unit}.
2. SYLLABUS LIST: You MUST cover ONLY these topics: [{topics_str}].
3. NO TOPIC BLEED: 
   - Unit 1: Register Transfer, Microoperations, Bus Architecture, Addressing Modes, Stack Organization.
   - Unit 2: ALU, Booth's Algorithm, Restoring/Non-Restoring Division, Look-Ahead Carry Adder, IEEE 754 Floating Point.
   - Unit 3: Control Unit (Hardwired & Microprogrammed), RISC/CISC, Pipelining, Instruction Cycles.
   - Unit 4: Memory Hierarchy, 2D/2.5D RAM, Cache Mapping (Direct, Associative, Set-Associative), Virtual Memory, Page Replacement.
   - Unit 5: I/O Interface, Modes of Data Transfer (Programmed, Interrupt-Driven, DMA), Interrupt Hardware, Serial Communication.
4. FORBIDDEN OVERLAP: Do NOT output formulas or algorithms from other units.

REQUIRED OUTPUT FORMAT:

# {code}: Unit {unit} - Comprehensive Revision & Exam Guide

### AKTU End-Semester Examination Notes
- Course Code: {code}
- Course Name: {name}
- Unit: {unit}
- Allowed Topics: [{topics_str}]

## 1. Core Technical Concept Breakdown
### Specific Notes on Important Topics
- Provide exhaustive, step-by-step notes strictly for: [{topics_str}].
- Include relevant circuit block diagrams, RTL expressions, register transfers, timing models, or assembly instruction formats.

## 2. AKTU Exam Scoring Strategy & Pitfalls
### AKTU Exam Scoring Strategy & Common Marking Pitfalls
- **High-Yield Exam Topics**: Core areas tested frequently in AKTU end-sem exams for Unit {unit}.
- **Common Exam Mistakes**: 3 specific logic, step, or diagram errors students make in this unit.

## 3. Section A: 2-Mark Short Questions & Answers
### Section A: 2-Mark Short Questions (5 Fully Solved with Solutions)
Provide exactly 5 distinct 2-mark short questions with concise, complete answers based strictly on [{topics_str}].
You MUST format each question exactly as:
1. **Q1: [Question text]** -> Answer: ...
2. **Q2: [Question text]** -> Answer: ...
3. **Q3: [Question text]** -> Answer: ...
4. **Q4: [Question text]** -> Answer: ...
5. **Q5: [Question text]** -> Answer: ...

## 4. Section B & C: 10-Mark Long Questions & Answers
### Section B/C: 10-Mark Long Questions & Numericals (3 Fully Solved with Solutions)
Provide exactly 3 complete long-form exam questions with thorough derivations or solved numericals strictly based on [{topics_str}].
You MUST format each question exactly as:
1. **Q1: [Question text]** -> Solution: ...
2. **Q2: [Question text]** -> Solution: ...
3. **Q3: [Question text]** -> Solution: ...
"""

    if not config.is_gemini_mocked():
        try:
            loop = asyncio.get_running_loop()
            gemini_notes = await asyncio.wait_for(
                loop.run_in_executor(_THREAD_POOL, _sync_fetch_gemini_unit_notes, aktu_unit_prompt, unit, code, name),
                timeout=3.5
            )
            if gemini_notes:
                res = {
                    "subject_code": code,
                    "unit": unit,
                    "unit_number": unit,
                    "timestamp": time.time(),
                    "unit_notes": gemini_notes,
                    "notes": gemini_notes
                }
                _AKTU_UNIT_CACHE[cache_key] = res
                return res
        except Exception as e:
            print(f"Gemini client AKTU unit notes generation notice: {e}")

    # Robust high-yield AKTU exam unit fallback with LaTeX math (runs in <1ms)
    fallback = _generate_fallback_unit_notes(code, name, unit, topics)
    cleaned_fallback = GeminiService.sanitize_study_notes(fallback)
    res = {
        "subject_code": code,
        "unit": unit,
        "unit_number": unit,
        "timestamp": time.time(),
        "unit_notes": cleaned_fallback,
        "notes": cleaned_fallback
    }
    _AKTU_UNIT_CACHE[cache_key] = res
    return res
