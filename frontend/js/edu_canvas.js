/**
 * OmniLearn Interactive Educational Canvas & Dynamic Study Knowledge Panel
 * Provides:
 * 1. An interactive floating academic words & concepts constellation canvas reacting to mouse movement.
 * 2. Dynamic, periodically rotating academic concepts across diverse disciplines with full interactivity.
 * 3. High-DPI Retina rendering with domain-colorized academic terms.
 * 4. Keyboard shortcuts (⌘K / Ctrl+K / '/') to immediately focus search.
 */

(function () {
    // --- 1. Academic Concepts Deck for Dynamic Knowledge Panel ---
    const EDU_CONCEPTS = [
        {
            domain: "⚛️ Quantum Physics & Cosmology",
            title: "Heisenberg's Uncertainty Principle",
            formula: "$$\\Delta x \\cdot \\Delta p \\ge \\frac{\\hbar}{2}$$",
            searchQuery: "Quantum Mechanics",
            insight: "Physical precision has fundamental limits: determining a particle's exact position intrinsically increases the uncertainty of its linear momentum.",
            aura1: "rgba(59, 130, 246, 0.35)",
            aura2: "rgba(99, 102, 241, 0.3)"
        },
        {
            domain: "💻 Computer Science & Algorithms",
            title: "P vs NP & Asymptotic Lower Bounds",
            formula: "$$\\mathcal{O}(n \\log n) \\quad \\Big| \\quad P \\stackrel{?}{=} NP$$",
            searchQuery: "Dijkstra's Algorithm",
            insight: "Optimal comparison sorting cannot surpass O(n log n); whether every problem whose solution can be checked in polynomial time can also be solved quickly remains computing's deepest mystery.",
            aura1: "rgba(16, 185, 129, 0.35)",
            aura2: "rgba(79, 70, 229, 0.3)"
        },
        {
            domain: "📐 Pure Mathematics & Calculus",
            title: "Euler's Identity & The Fundamental Theorem",
            formula: "$$e^{i\\pi} + 1 = 0 \\quad \\Big| \\quad \\int_a^b f(x)dx = F(b) - F(a)$$",
            searchQuery: "Integration Techniques",
            insight: "Euler's Identity effortlessly links arithmetic, algebra, geometry, and calculus through the five most vital mathematical constants: e, i, π, 1, and 0.",
            aura1: "rgba(139, 92, 246, 0.35)",
            aura2: "rgba(236, 72, 153, 0.3)"
        },
        {
            domain: "🖥️ Computer Systems & Architecture",
            title: "Von Neumann Bottleneck & Amdahl's Law",
            formula: "$$S_{\\text{latency}}(s) = \\frac{1}{(1 - p) + \\frac{p}{s}} \\quad \\Big| \\quad \\text{Clock Cycles} = \\text{IC} \\times \\text{CPI}$$",
            searchQuery: "Computer Architecture",
            insight: "Throughput between CPU and memory forms a fundamental latency barrier; speedup from parallelization is governed strictly by the workload's serial fraction.",
            aura1: "rgba(245, 158, 11, 0.35)",
            aura2: "rgba(239, 68, 68, 0.3)"
        },
        {
            domain: "🧪 Chemistry & Thermodynamics",
            title: "Gibbs Free Energy & Second Law",
            formula: "$$\\Delta G = \\Delta H - T\\Delta S \\quad (\\Delta G < 0)$$",
            searchQuery: "Thermodynamics",
            insight: "A chemical process proceeds spontaneously at constant temperature and pressure if and only if the change in Gibbs Free Energy is strictly negative.",
            aura1: "rgba(6, 182, 212, 0.35)",
            aura2: "rgba(59, 130, 246, 0.3)"
        },
        {
            domain: "🧬 Cognitive Neuroscience & Biology",
            title: "Hebbian Synaptic Plasticity & Central Dogma",
            formula: "$$\\Delta w_{ij} = \\eta \\cdot x_i x_j \\quad \\Big| \\quad \\text{DNA} \\rightarrow \\text{RNA} \\rightarrow \\text{Protein}$$",
            searchQuery: "Linked List Inversion",
            insight: "Neurons that fire together wire together: repeated coordinated stimulation between synapses enhances transmission efficiency, forming the bedrock of memory.",
            aura1: "rgba(20, 184, 166, 0.35)",
            aura2: "rgba(139, 92, 246, 0.3)"
        }
    ];

    let currentConceptIndex = 0;
    let isPaused = false;
    let progressTimer = null;
    let progressPercent = 0;
    const ROTATION_INTERVAL_MS = 10000; // 10 seconds per concept
    const TICK_STEP_MS = 100;

    // --- 2. Interactive Constellation Canvas with Rich Academic Words ---
    let canvas, ctx;
    let particles = [];
    let mouse = { x: -9999, y: -9999, radius: 170 };
    let animationFrameId = null;

    // Extensive, High-Yield Computer Science & Science Terms Bank
    const ACADEMIC_WORDS_BANK = [
        // ==========================================
        // COMPUTER SCIENCE: DATA STRUCTURES & ALGORITHMS (cs)
        // ==========================================
        { text: "Algorithm", domain: "cs" },
        { text: "Red-Black Tree", domain: "cs" },
        { text: "AVL Tree Rotations", domain: "cs" },
        { text: "Dijkstra's Algorithm", domain: "cs" },
        { text: "Dynamic Programming", domain: "cs" },
        { text: "B+ Tree Index", domain: "cs" },
        { text: "Trie", domain: "cs" },
        { text: "Binary Search Tree", domain: "cs" },
        { text: "Min & Max Heap", domain: "cs" },
        { text: "Hash Table & Buckets", domain: "cs" },
        { text: "Recursion & Call Stack", domain: "cs" },
        { text: "Big-O Notation O(n log n)", domain: "cs" },
        { text: "Amortized Analysis", domain: "cs" },
        { text: "Divide & Conquer", domain: "cs" },
        { text: "Topological Sort", domain: "cs" },
        { text: "Breadth-First Search", domain: "cs" },
        { text: "Depth-First Search", domain: "cs" },
        { text: "Graph Theory", domain: "cs" },
        { text: "Bit Manipulation", domain: "cs" },
        { text: "Greedy Strategy", domain: "cs" },
        { text: "Floyd-Warshall", domain: "cs" },
        { text: "Bellman-Ford", domain: "cs" },
        { text: "A* Pathfinding", domain: "cs" },
        { text: "Disjoint Set (Union-Find)", domain: "cs" },
        { text: "Sliding Window", domain: "cs" },
        { text: "Two Pointers", domain: "cs" },
        { text: "Segment Tree", domain: "cs" },
        { text: "Fenwick Tree", domain: "cs" },

        // ==========================================
        // COMPUTER SCIENCE: SYSTEMS & ARCHITECTURE (cs)
        // ==========================================
        { text: "Von Neumann Architecture", domain: "cs" },
        { text: "RISC-V Instruction Set", domain: "cs" },
        { text: "CPU Pipelining", domain: "cs" },
        { text: "Branch Prediction", domain: "cs" },
        { text: "L1 / L2 / L3 Cache Hierarchy", domain: "cs" },
        { text: "Translation Lookaside Buffer (TLB)", domain: "cs" },
        { text: "ALU & Register File", domain: "cs" },
        { text: "Accumulator (AC)", domain: "cs" },
        { text: "Direct Memory Access (DMA)", domain: "cs" },
        { text: "Instruction Cycle (Fetch-Decode-Execute)", domain: "cs" },
        { text: "System Bus & Datapath", domain: "cs" },
        { text: "Interrupt Vector Table", domain: "cs" },
        { text: "Assembly & Opcode", domain: "cs" },
        { text: "Booth's Multiplier", domain: "cs" },

        // ==========================================
        // COMPUTER SCIENCE: OPERATING SYSTEMS & CONCURRENCY (cs)
        // ==========================================
        { text: "Operating System Kernel", domain: "cs" },
        { text: "Counting Semaphore", domain: "cs" },
        { text: "Mutual Exclusion (Mutex)", domain: "cs" },
        { text: "Deadlock (Coffman Conditions)", domain: "cs" },
        { text: "Virtual Memory Paging", domain: "cs" },
        { text: "LRU Page Replacement", domain: "cs" },
        { text: "Context Switch", domain: "cs" },
        { text: "Process Scheduling (Round Robin)", domain: "cs" },
        { text: "Thread Concurrency", domain: "cs" },
        { text: "System Call (Syscall)", domain: "cs" },
        { text: "Banker's Safety Algorithm", domain: "cs" },
        { text: "Fork & Exec", domain: "cs" },
        { text: "Inter-Process Comm (IPC)", domain: "cs" },
        { text: "Stack vs Heap Allocation", domain: "cs" },
        { text: "Belady's Anomaly", domain: "cs" },

        // ==========================================
        // COMPUTER SCIENCE: THEORY OF COMPUTATION & AUTOMATA (cs)
        // ==========================================
        { text: "Turing Machine", domain: "cs" },
        { text: "Halting Problem", domain: "cs" },
        { text: "P vs NP Problem", domain: "cs" },
        { text: "NP-Completeness (Cook-Levin)", domain: "cs" },
        { text: "Deterministic Finite Automaton (DFA)", domain: "cs" },
        { text: "Non-Deterministic Automaton (NFA)", domain: "cs" },
        { text: "Pushdown Automaton (PDA)", domain: "cs" },
        { text: "Context-Free Grammar (CFG)", domain: "cs" },
        { text: "Chomsky Hierarchy", domain: "cs" },
        { text: "Lambda Calculus", domain: "cs" },
        { text: "Pumping Lemma", domain: "cs" },
        { text: "Turing Completeness", domain: "cs" },
        { text: "Church-Turing Thesis", domain: "cs" },

        // ==========================================
        // COMPUTER SCIENCE: DATABASES & DISTRIBUTED SYSTEMS (cs)
        // ==========================================
        { text: "ACID Transactions", domain: "cs" },
        { text: "Two-Phase Locking (2PL)", domain: "cs" },
        { text: "CAP Theorem (Brewer)", domain: "cs" },
        { text: "Raft Consensus Protocol", domain: "cs" },
        { text: "Paxos Agreement", domain: "cs" },
        { text: "BCNF Normalization", domain: "cs" },
        { text: "Write-Ahead Logging (WAL)", domain: "cs" },
        { text: "Sharding & Partitioning", domain: "cs" },
        { text: "Distributed MapReduce", domain: "cs" },
        { text: "Distributed Hash Table (DHT)", domain: "cs" },
        { text: "Database Indexing", domain: "cs" },

        // ==========================================
        // COMPUTER SCIENCE: NETWORKS & CRYPTOGRAPHY (cs)
        // ==========================================
        { text: "TCP/IP Protocol Stack", domain: "cs" },
        { text: "TCP 3-Way Handshake (SYN-ACK)", domain: "cs" },
        { text: "Packet Routing & BGP", domain: "cs" },
        { text: "Subnetting & CIDR /24", domain: "cs" },
        { text: "DNS Resolution", domain: "cs" },
        { text: "TLS/SSL Cryptographic Handshake", domain: "cs" },
        { text: "Diffie-Hellman Key Exchange", domain: "cs" },
        { text: "RSA Asymmetric Encryption", domain: "cs" },
        { text: "Zero-Knowledge Proofs", domain: "cs" },
        { text: "Elliptic Curve Cryptography", domain: "cs" },
        { text: "AES-256 Symmetric Cipher", domain: "cs" },
        { text: "WebSocket Full-Duplex", domain: "cs" },
        { text: "Cybernetics", domain: "cs" },

        // ==========================================
        // COMPUTER SCIENCE: COMPILERS & RUNTIMES (cs)
        // ==========================================
        { text: "Compiler Architecture", domain: "cs" },
        { text: "Lexical & Syntax Analysis", domain: "cs" },
        { text: "Abstract Syntax Tree (AST)", domain: "cs" },
        { text: "LLVM Intermediate Representation", domain: "cs" },
        { text: "Bytecode Virtual Machine", domain: "cs" },
        { text: "JIT Compilation", domain: "cs" },
        { text: "Garbage Collection (Mark & Sweep)", domain: "cs" },
        { text: "Type Inference & Hindley-Milner", domain: "cs" },
        { text: "QuickSort & Dual-Pivot", domain: "cs" },
        { text: "MergeSort Divide & Conquer", domain: "cs" },
        { text: "Master Theorem Complexity", domain: "cs" },
        { text: "Kruskal's MST Algorithm", domain: "cs" },
        { text: "Prim's Spanning Tree", domain: "cs" },
        { text: "Tarjan's SCC Algorithm", domain: "cs" },
        { text: "Knuth-Morris-Pratt (KMP)", domain: "cs" },
        { text: "Rabin-Karp Rolling Hash", domain: "cs" },
        { text: "Bloom Filter Probabilistic Set", domain: "cs" },
        { text: "Consistent Hashing Ring", domain: "cs" },
        { text: "LRU & LFU Cache Eviction", domain: "cs" },
        { text: "Demand Paging & Page Fault", domain: "cs" },
        { text: "Thrashing & Working Set Model", domain: "cs" },
        { text: "Spinlock & Peterson's Solution", domain: "cs" },
        { text: "Producer-Consumer Problem", domain: "cs" },
        { text: "Dining Philosophers Sync", domain: "cs" },
        { text: "Superscalar Instruction Issue", domain: "cs" },
        { text: "Branch History Table & Predictor", domain: "cs" },
        { text: "SIMD Vector Registers", domain: "cs" },
        { text: "Microcode & Control Unit", domain: "cs" },
        { text: "UART / SPI / I2C Buses", domain: "cs" },
        { text: "LL(1) First & Follow Sets", domain: "cs" },
        { text: "LR(1) Canonical Collection", domain: "cs" },
        { text: "Recursive Descent Parsing", domain: "cs" },
        { text: "LALR Parser Generation", domain: "cs" },
        { text: "Static Single Assignment (SSA)", domain: "cs" },
        { text: "Mark-Compact Collector", domain: "cs" },
        { text: "Foreign Key Integrity", domain: "cs" },
        { text: "Clustered B+ Index", domain: "cs" },
        { text: "Cost-Based Query Optimization", domain: "cs" },
        { text: "Multi-Version Concurrency (MVCC)", domain: "cs" },
        { text: "Event Loop & Non-Blocking I/O", domain: "cs" },
        { text: "OSI 7-Layer Model", domain: "cs" },
        { text: "TCP Congestion Control (CUBIC)", domain: "cs" },
        { text: "Selective Repeat Protocol", domain: "cs" },
        { text: "HTTP/3 over QUIC", domain: "cs" },
        { text: "Public Key Infrastructure (PKI)", domain: "cs" },
        { text: "SHA-256 Cryptographic Hash", domain: "cs" },
        { text: "Elliptic Curve Diffie-Hellman", domain: "cs" },

        // ==========================================
        // ARTIFICIAL INTELLIGENCE & MACHINE LEARNING (ai)
        // ==========================================
        { text: "Deep Neural Networks", domain: "ai" },
        { text: "Backpropagation Algorithm", domain: "ai" },
        { text: "Transformer Attention Head", domain: "ai" },
        { text: "Self-Attention Mechanism", domain: "ai" },
        { text: "Stochastic Gradient Descent", domain: "ai" },
        { text: "Convolutional Neural Network", domain: "ai" },
        { text: "Recurrent NN & LSTM", domain: "ai" },
        { text: "Loss Function Optimization", domain: "ai" },
        { text: "Reinforcement Learning (Q-Learning)", domain: "ai" },
        { text: "Markov Decision Process (MDP)", domain: "ai" },
        { text: "Latent Representation Space", domain: "ai" },
        { text: "Vector Embeddings", domain: "ai" },
        { text: "Support Vector Machines (SVM)", domain: "ai" },
        { text: "Principal Component Analysis (PCA)", domain: "ai" },
        { text: "Softmax Probability", domain: "ai" },
        { text: "Generative AI", domain: "ai" },
        { text: "Cross-Entropy Loss", domain: "ai" },
        { text: "Overfitting Regularization (Dropout)", domain: "ai" },
        { text: "Self-Attention Query-Key-Value", domain: "ai" },
        { text: "Multi-Head Attention Heads", domain: "ai" },
        { text: "Transformer Positional Encoding", domain: "ai" },
        { text: "Residual Skip Connections", domain: "ai" },
        { text: "Batch Normalization & LayerNorm", domain: "ai" },
        { text: "AdamW Optimizer & Weight Decay", domain: "ai" },
        { text: "Gradient Vanishing & Explosion", domain: "ai" },
        { text: "ReLU & GELU Activation Functions", domain: "ai" },
        { text: "Autoencoders & Latent Space", domain: "ai" },
        { text: "Diffusion Probabilistic Models", domain: "ai" },
        { text: "Denoising Score Matching", domain: "ai" },
        { text: "RLHF Alignment", domain: "ai" },
        { text: "Deep Q-Networks (DQN)", domain: "ai" },
        { text: "Policy Gradient Theorem", domain: "ai" },
        { text: "Monte Carlo Tree Search (MCTS)", domain: "ai" },
        { text: "Cosine Similarity Metric", domain: "ai" },
        { text: "Precision, Recall & F1-Score", domain: "ai" },
        { text: "ROC-AUC Curve Analysis", domain: "ai" },

        // ==========================================
        // PHYSICS & QUANTUM MECHANICS (physics)
        // ==========================================
        { text: "Quantum Mechanics", domain: "physics" },
        { text: "Quantum Superposition", domain: "physics" },
        { text: "Quantum Entanglement", domain: "physics" },
        { text: "Thermodynamics & Second Law", domain: "physics" },
        { text: "Schrödinger Wavefunction Ψ", domain: "physics" },
        { text: "General Relativity", domain: "physics" },
        { text: "Special Relativity", domain: "physics" },
        { text: "Maxwell's Field Equations", domain: "physics" },
        { text: "Planck's Constant h", domain: "physics" },
        { text: "Cosmological Redshift", domain: "physics" },
        { text: "Statistical Entropy ΔS", domain: "physics" },
        { text: "Black Hole Event Horizon", domain: "physics" },
        { text: "Lorentz Invariance", domain: "physics" },
        { text: "Spacetime Metric Tensor", domain: "physics" },
        { text: "Photoelectric Effect", domain: "physics" },
        { text: "Quantum Tunneling", domain: "physics" },
        { text: "Bose-Einstein Condensate", domain: "physics" },
        { text: "Conservation of Momentum", domain: "physics" },
        { text: "Newtonian Kinematics", domain: "physics" },
        { text: "Electromagnetic Spectrum", domain: "physics" },
        { text: "Mass-Energy Equivalence E=mc²", domain: "physics" },
        { text: "Dark Matter & Energy", domain: "physics" },
        { text: "Superconductivity & Cooper Pairs", domain: "physics" },
        { text: "Wave-Particle Duality", domain: "physics" },
        { text: "Photon Quantization", domain: "physics" },
        { text: "Quantum Superposition |ψ⟩", domain: "physics" },
        { text: "EPR Paradox & Bell's Theorem", domain: "physics" },
        { text: "Hamiltonian Mechanics & Phase Space", domain: "physics" },
        { text: "Lagrangian Principle of Least Action", domain: "physics" },
        { text: "Carnot Engine Thermal Efficiency", domain: "physics" },
        { text: "Maxwell-Boltzmann Distribution", domain: "physics" },
        { text: "Gravitational Time Dilation", domain: "physics" },
        { text: "Lorentz Contraction & Spacetime", domain: "physics" },
        { text: "Heisenberg Matrix Mechanics", domain: "physics" },
        { text: "Cherenkov Radiation", domain: "physics" },
        { text: "Semiconductor Band Gap & Fermi Level", domain: "physics" },
        { text: "Josephson Junction & SQUIDs", domain: "physics" },
        { text: "Higgs Boson & Symmetry Breaking", domain: "physics" },

        // ==========================================
        // CHEMISTRY & MOLECULAR SCIENCE (chem)
        // ==========================================
        { text: "Gibbs Free Energy ΔG", domain: "chem" },
        { text: "Chemical Equilibrium", domain: "chem" },
        { text: "Covalent & Ionic Bonds", domain: "chem" },
        { text: "Le Chatelier's Principle", domain: "chem" },
        { text: "Reaction Enthalpy ΔH", domain: "chem" },
        { text: "Arrhenius Activation Energy", domain: "chem" },
        { text: "Atomic Orbital Hybridization (sp³)", domain: "chem" },
        { text: "Endothermic & Exothermic", domain: "chem" },
        { text: "Stoichiometry & Mole Fraction", domain: "chem" },
        { text: "Electronegativity (Pauling Scale)", domain: "chem" },
        { text: "NMR & Mass Spectroscopy", domain: "chem" },
        { text: "Redox Oxidation-Reduction", domain: "chem" },
        { text: "Heterogeneous Catalysis", domain: "chem" },
        { text: "Polymer Macromolecules", domain: "chem" },
        { text: "Periodic Table Valence", domain: "chem" },
        { text: "Thermodynamic Reversibility", domain: "chem" },
        { text: "Molecular Orbital Theory (HOMO-LUMO)", domain: "chem" },
        { text: "Transition State Theory & Complex", domain: "chem" },
        { text: "Nernst Equation & Cell Potential", domain: "chem" },
        { text: "Enzyme Kinetics (Michaelis-Menten)", domain: "chem" },
        { text: "van der Waals London Forces", domain: "chem" },
        { text: "Crystal Field Theory & d-Orbitals", domain: "chem" },
        { text: "Acid-Base Dissociation Constant pKa", domain: "chem" },
        { text: "Phase Rule & Triple Point", domain: "chem" },

        // ==========================================
        // MATHEMATICS & THEORETICAL FOUNDATIONS (math)
        // ==========================================
        { text: "Multivariable Calculus", domain: "math" },
        { text: "Linear Algebra & Vector Spaces", domain: "math" },
        { text: "Ordinary Differential Equations", domain: "math" },
        { text: "Continuous Fourier Transform", domain: "math" },
        { text: "Laplace Transform", domain: "math" },
        { text: "Riemann Zeta Function", domain: "math" },
        { text: "Euler's Identity e^(iπ) + 1 = 0", domain: "math" },
        { text: "Taylor Series Expansion", domain: "math" },
        { text: "Cauchy-Schwarz Inequality", domain: "math" },
        { text: "Eigenvalues & Eigenvectors", domain: "math" },
        { text: "Algebraic Topology", domain: "math" },
        { text: "Stochastic Itô Calculus", domain: "math" },
        { text: "Boolean Algebra & De Morgan", domain: "math" },
        { text: "Definite Integral ∫ f(x)dx", domain: "math" },
        { text: "Gaussian Probability Density", domain: "math" },
        { text: "Matrix Inversion & Determinant", domain: "math" },
        { text: "Markov Chain Transitions", domain: "math" },
        { text: "Bayesian Posterior Inference", domain: "math" },
        { text: "Abstract Group Theory", domain: "math" },
        { text: "Prime Number Theorem", domain: "math" },
        { text: "Differential Geometry", domain: "math" },
        { text: "Asymptotic Convergence", domain: "math" },
        { text: "Singular Value Decomposition (SVD)", domain: "math" },
        { text: "Fast Fourier Transform (FFT)", domain: "math" },
        { text: "Laplacian Matrix & Spectral Graphs", domain: "math" },
        { text: "Gradient Descent Optimization", domain: "math" },
        { text: "Hessian Matrix & Curvature", domain: "math" },
        { text: "Cauchy's Residue Theorem", domain: "math" },
        { text: "Gram-Schmidt Orthogonalization", domain: "math" },
        { text: "Poisson Probability Distribution", domain: "math" },
        { text: "Central Limit Theorem", domain: "math" },
        { text: "Monte Carlo Integration", domain: "math" },
        { text: "Convex Optimization & KKT Conditions", domain: "math" },
        { text: "Cayley-Hamilton Theorem", domain: "math" },

        // ==========================================
        // NEUROSCIENCE & COMPUTATIONAL BIOLOGY (bio)
        // ==========================================
        { text: "Computational Neuroscience", domain: "bio" },
        { text: "Synaptic Plasticity (LTP)", domain: "bio" },
        { text: "Neuronal Action Potential", domain: "bio" },
        { text: "CRISPR-Cas9 Gene Editing", domain: "bio" },
        { text: "Molecular Central Dogma", domain: "bio" },
        { text: "DNA & RNA Nucleotides", domain: "bio" },
        { text: "Axon Myelination & Dendrite", domain: "bio" },
        { text: "Hebbian Synaptic Learning", domain: "bio" },
        { text: "Cellular Automata", domain: "bio" },
        { text: "Gene Expression & Transcription", domain: "bio" },
        { text: "Protein Tertiary Folding", domain: "bio" },
        { text: "ATP Mitochondrial Synthase", domain: "bio" },
        { text: "Photosynthetic Electron Transport", domain: "bio" },
        { text: "Neuroplastic Memory Trace", domain: "bio" },
        { text: "Biological Homeostasis", domain: "bio" },
        { text: "Hodgkin-Huxley Neuron Model", domain: "bio" },
        { text: "Action Potential Depolarization (Na+/K+)", domain: "bio" },
        { text: "Synaptic Vesicle Exocytosis", domain: "bio" },
        { text: "Epigenetic DNA Methylation", domain: "bio" },
        { text: "CRISPR Cas9 Double-Strand Break", domain: "bio" },
        { text: "Signal Transduction Cascade", domain: "bio" },
        { text: "ATP Synthase Rotary Motor", domain: "bio" }
    ];

    function initCanvas() {
        canvas = document.getElementById("eduConstellationCanvas");
        if (!canvas) return;
        ctx = canvas.getContext("2d");
        resizeCanvas();

        window.addEventListener("resize", resizeCanvas);
        window.addEventListener("mousemove", (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });
        window.addEventListener("mouseleave", () => {
            mouse.x = -9999;
            mouse.y = -9999;
        });
        window.addEventListener("touchmove", (e) => {
            if (e.touches && e.touches[0]) {
                mouse.x = e.touches[0].clientX;
                mouse.y = e.touches[0].clientY;
            }
        }, { passive: true });
        window.addEventListener("touchend", () => {
            mouse.x = -9999;
            mouse.y = -9999;
        });

        // Spawn words
        createParticles();
        animateCanvas();
    }

    let dpr = 1;
    let resizeTimer = null;
    function resizeCanvas() {
        if (!canvas) return;
        dpr = window.devicePixelRatio || 1;
        canvas.width = window.innerWidth * dpr;
        canvas.height = window.innerHeight * dpr;
        canvas.style.width = `${window.innerWidth}px`;
        canvas.style.height = `${window.innerHeight}px`;
        if (ctx) {
            ctx.scale(dpr, dpr);
        }
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            createParticles();
        }, 250);
    }

    function createParticles() {
        particles = [];
        const w = window.innerWidth;
        const h = window.innerHeight;
        // Refined, clean density: 36 words on desktop, scaled gracefully across viewports
        const count = Math.min(36, Math.max(16, Math.floor((w * h) / 48000)));

        // Shuffle words bank
        const pool = [...ACADEMIC_WORDS_BANK].sort(() => 0.5 - Math.random());

        for (let i = 0; i < count; i++) {
            const wordObj = pool[i % pool.length];
            const depth = Math.random(); // 0 (far) to 1 (near)
            
            // Varied font sizes, weights and tasteful ambient alpha
            const fontSize = depth > 0.65 ? 12.5 : depth > 0.35 ? 11.5 : 10.5;
            const fontWeight = depth > 0.65 ? "500" : "400";
            const baseAlpha = depth > 0.65 
                ? (Math.random() * 0.12 + 0.46) 
                : depth > 0.35 
                    ? (Math.random() * 0.10 + 0.30) 
                    : (Math.random() * 0.08 + 0.18);

            const speedMultiplier = depth > 0.65 ? 0.22 : depth > 0.35 ? 0.18 : 0.14;
            const baseVx = (Math.random() - 0.5) * speedMultiplier;
            const baseVy = (Math.random() - 0.5) * speedMultiplier;

            // Spawn distributed across screen, avoiding central hero core
            let px = Math.random() * w;
            let py = Math.random() * h;
            if (px > w * 0.32 && px < w * 0.68 && py > h * 0.15 && py < h * 0.45) {
                px = Math.random() > 0.5 ? px + w * 0.25 : px - w * 0.25;
                if (px < 30) px = 30 + Math.random() * 80;
                if (px > w - 30) px = w - 30 - Math.random() * 80;
            }

            particles.push({
                x: px,
                y: py,
                vx: baseVx,
                vy: baseVy,
                baseVx: baseVx,
                baseVy: baseVy,
                text: wordObj.text,
                domain: wordObj.domain,
                size: fontSize,
                weight: fontWeight,
                depth: depth,
                alpha: baseAlpha,
                baseAlpha: baseAlpha,
                isHovered: false
            });
        }
    }

    function getWordColor(domain, isDark, alpha) {
        if (isDark) {
            switch (domain) {
                case "cs":      return `rgba(165, 180, 252, ${alpha})`;  // Soft Indigo / Terminal Blue
                case "ai":      return `rgba(244, 114, 182, ${alpha})`;  // Pink / Neon Magenta
                case "physics": return `rgba(147, 197, 253, ${alpha})`;  // Cosmic Blue
                case "chem":    return `rgba(103, 232, 249, ${alpha})`;  // Electric Cyan
                case "math":    return `rgba(196, 181, 253, ${alpha})`;  // Light Purple
                case "bio":     return `rgba(110, 231, 183, ${alpha})`;  // Luminous Mint
                default:        return `rgba(203, 213, 225, ${alpha})`;  // Slate 300
            }
        } else {
            switch (domain) {
                case "cs":      return `rgba(67, 56, 202, ${alpha})`;    // Deep Indigo
                case "ai":      return `rgba(190, 24, 93, ${alpha})`;    // Deep Magenta
                case "physics": return `rgba(29, 78, 216, ${alpha})`;    // Deep Blue
                case "chem":    return `rgba(14, 116, 144, ${alpha})`;   // Deep Cyan
                case "math":    return `rgba(126, 34, 206, ${alpha})`;   // Deep Purple
                case "bio":     return `rgba(15, 118, 110, ${alpha})`;   // Deep Teal
                default:        return `rgba(51, 65, 85, ${alpha})`;     // Slate Navy
            }
        }
    }

    function animateCanvas() {
        if (!canvas || !ctx) return;

        const w = window.innerWidth;
        const h = window.innerHeight;

        ctx.clearRect(0, 0, w, h);

        const isDark = (document.documentElement.getAttribute("data-theme") || "dark") === "dark";
        const baseLineColor = isDark ? "rgba(147, 197, 253, " : "rgba(79, 70, 229, ";

        // 1. First pass: Handle mouse interaction, damping, central clearance, and border wrapping
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];

            // Mouse proximity repulsion physics
            const dx = mouse.x - p.x;
            const dy = mouse.y - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < mouse.radius && dist > 1) {
                const force = (mouse.radius - dist) / mouse.radius;
                // Responsive repulsive impulse: pushes word away from cursor
                const repulse = force * force * 5.5;
                p.vx -= (dx / dist) * repulse;
                p.vy -= (dy / dist) * repulse;
                p.alpha = Math.min(0.92, p.baseAlpha + force * 0.40);
                p.isHovered = true;
            } else {
                p.alpha += (p.baseAlpha - p.alpha) * 0.05;
                p.isHovered = false;
            }

            // Soft drift away from the central hero brand area (so words don't cover OmniLearn logo/search)
            const cDx = p.x - (w * 0.5);
            const cDy = p.y - (h * 0.28);
            const heroClearanceX = Math.min(w * 0.28, 280);
            const heroClearanceY = Math.min(h * 0.20, 180);
            if (Math.abs(cDx) < heroClearanceX && Math.abs(cDy) < heroClearanceY) {
                p.vx += (cDx >= 0 ? 0.14 : -0.14);
                p.vy += (cDy >= 0 ? 0.12 : -0.12);
            }

            // Smooth damping back towards natural drift
            p.vx = p.vx * 0.92 + p.baseVx * 0.08;
            p.vy = p.vy * 0.92 + p.baseVy * 0.08;

            // Move particle
            p.x += p.vx;
            p.y += p.vy;

            // Soft wrap around edges
            if (p.x < -70) p.x = w + 70;
            if (p.x > w + 70) p.x = -70;
            if (p.y < -35) p.y = h + 35;
            if (p.y > h + 35) p.y = -35;
        }

        // 2. Second pass: Draw connected constellation webs and mutual word repulsion
        const maxLineDist = 160; // Clean, delicate constellation links
        const maxLineDistSq = maxLineDist * maxLineDist;
        const minWordSeparation = 130; // Generous distance so words never clump or collide

        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];

            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const lineDx = p.x - p2.x;
                const lineDy = p.y - p2.y;
                const distSq = lineDx * lineDx + lineDy * lineDy;

                if (distSq < maxLineDistSq) {
                    const lineDist = Math.sqrt(distSq);

                    // Mutual repulsion between words ("tend to remove from each other when hovered")
                    if (lineDist < minWordSeparation && lineDist > 0) {
                        const repelMultiplier = (p.isHovered || p2.isHovered) ? 3.0 : 0.6;
                        const sepForce = ((minWordSeparation - lineDist) / minWordSeparation) * repelMultiplier;
                        const pushX = (lineDx / lineDist) * sepForce;
                        const pushY = (lineDy / lineDist) * sepForce;
                        p.vx += pushX;
                        p.vy += pushY;
                        p2.vx -= pushX;
                        p2.vy -= pushY;
                    }

                    // Draw visible constellation lines between connected words
                    const factor = (1 - lineDist / maxLineDist);
                    let lineAlpha = factor * (isDark ? 0.18 : 0.12);
                    const isPairHovered = p.isHovered || p2.isHovered;

                    if (isPairHovered) {
                        lineAlpha = Math.min(0.75, lineAlpha * 2.5);
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = isDark ? `rgba(165, 180, 252, ${lineAlpha})` : `rgba(99, 102, 241, ${lineAlpha})`;
                        ctx.lineWidth = 1.1;
                        ctx.stroke();
                    } else {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = `${baseLineColor}${lineAlpha})`;
                        ctx.lineWidth = 0.65;
                        ctx.stroke();
                    }
                }
            }
        }

        // 3. Third pass: Draw all word labels on top of the constellation webs
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];

            ctx.font = `${p.weight} ${p.size}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            if (p.isHovered) {
                // Subtle glowing aura around hovered words
                ctx.save();
                ctx.shadowColor = isDark ? "rgba(165, 180, 252, 0.9)" : "rgba(79, 70, 229, 0.8)";
                ctx.shadowBlur = 14;
                ctx.fillStyle = isDark ? `rgba(255, 255, 255, ${p.alpha})` : `rgba(30, 27, 75, ${p.alpha})`;
                ctx.fillText(p.text, p.x, p.y);
                ctx.restore();
            } else {
                ctx.fillStyle = getWordColor(p.domain, isDark, p.alpha);
                ctx.fillText(p.text, p.x, p.y);
            }
        }

        animationFrameId = requestAnimationFrame(animateCanvas);
    }

    // --- 3. Dynamic Knowledge Panel Logic ---
    function renderCurrentEduConcept(animate = true) {
        const c = EDU_CONCEPTS[currentConceptIndex];
        if (!c) return;

        const card = document.getElementById("eduConceptCard");
        const domainBadge = document.getElementById("eduDomainBadge");
        const titleEl = document.getElementById("eduConceptTitle");
        const formulaEl = document.getElementById("eduConceptFormula");
        const insightEl = document.getElementById("eduConceptInsight");
        const aura1 = document.getElementById("ambientAura1");
        const aura2 = document.getElementById("ambientAura2");

        if (aura1 && c.aura1) aura1.style.background = c.aura1;
        if (aura2 && c.aura2) aura2.style.background = c.aura2;

        if (card && animate) {
            card.style.opacity = "0";
            card.style.transform = "translateY(4px)";
            setTimeout(() => {
                applyContent();
                card.style.opacity = "1";
                card.style.transform = "translateY(0)";
            }, 180);
        } else {
            applyContent();
        }

        function applyContent() {
            if (domainBadge) domainBadge.textContent = c.domain;
            if (titleEl) titleEl.textContent = c.title;
            if (formulaEl) {
                formulaEl.innerHTML = c.formula;
                if (window.renderMathInElement) {
                    try {
                        renderMathInElement(formulaEl, {
                            delimiters: [
                                { left: "$$", right: "$$", display: true },
                                { left: "$", right: "$", display: false }
                            ],
                            throwOnError: false
                        });
                    } catch (e) {
                        console.warn("KaTeX render error:", e);
                    }
                }
            }
            if (insightEl) insightEl.textContent = c.insight;
        }

        progressPercent = 0;
        updateProgressBar();
    }

    function updateProgressBar() {
        const bar = document.getElementById("eduTimerProgress");
        if (bar) bar.style.width = `${progressPercent}%`;
    }

    function startProgressLoop() {
        stopProgressLoop();
        progressTimer = setInterval(() => {
            if (!isPaused) {
                progressPercent += (TICK_STEP_MS / ROTATION_INTERVAL_MS) * 100;
                if (progressPercent >= 100) {
                    nextEduConcept();
                } else {
                    updateProgressBar();
                }
            }
        }, TICK_STEP_MS);
    }

    function stopProgressLoop() {
        if (progressTimer) {
            clearInterval(progressTimer);
            progressTimer = null;
        }
    }

    function nextEduConcept() {
        currentConceptIndex = (currentConceptIndex + 1) % EDU_CONCEPTS.length;
        renderCurrentEduConcept(true);
    }

    function prevEduConcept() {
        currentConceptIndex = (currentConceptIndex - 1 + EDU_CONCEPTS.length) % EDU_CONCEPTS.length;
        renderCurrentEduConcept(true);
    }

    function toggleEduRotation() {
        isPaused = !isPaused;
        const icon = document.getElementById("eduPauseIcon");
        if (icon) {
            icon.className = isPaused ? "fa-solid fa-play" : "fa-solid fa-pause";
        }
    }

    function exploreCurrentEduConcept() {
        const c = EDU_CONCEPTS[currentConceptIndex];
        if (!c) return;

        const query = c.searchQuery || c.title;
        if (typeof window.fillAndSearch === "function") {
            window.fillAndSearch(query);
        } else {
            const input = document.getElementById("mainSearchInput");
            if (input) {
                input.value = query;
                const form = document.getElementById("mainSearchForm");
                if (form) form.dispatchEvent(new Event("submit", { cancelable: true }));
            }
        }
    }

    // --- 4. Global Keyboard Shortcuts (⌘K, Ctrl+K, '/') ---
    function initKeyboardShortcuts() {
        document.addEventListener("keydown", (e) => {
            const isCmdK = (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k";
            const isSlash = e.key === "/" && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA";

            if (isCmdK || isSlash) {
                e.preventDefault();
                const landingScreen = document.getElementById("landingScreen");
                const mainInput = document.getElementById("mainSearchInput");
                const navInput = document.getElementById("navSearchInput");

                if (landingScreen && !landingScreen.classList.contains("hidden") && mainInput) {
                    mainInput.focus();
                    mainInput.select();
                } else if (navInput) {
                    navInput.focus();
                    navInput.select();
                }
            }
        });
    }

    // --- 5. Search Button Loading State Management ---
    function initSearchButtonState() {
        const form = document.getElementById("mainSearchForm");
        const btn = document.getElementById("mainSearchSubmitBtn");
        const btnIcon = document.getElementById("mainSearchBtnIcon");
        const btnText = document.getElementById("mainSearchBtnText");

        if (form) {
            form.addEventListener("submit", () => {
                if (btnIcon) btnIcon.className = "fa-solid fa-circle-notch fa-spin text-xs";
                if (btnText) btnText.textContent = "Exploring...";
                if (btn) btn.classList.add("opacity-90", "cursor-wait");

                setTimeout(() => {
                    if (btnIcon) btnIcon.className = "fa-solid fa-wand-magic-sparkles text-xs";
                    if (btnText) btnText.textContent = "Search";
                    if (btn) btn.classList.remove("opacity-90", "cursor-wait");
                }, 8000);
            });
        }
    }

    // Expose control functions to window
    window.nextEduConcept = nextEduConcept;
    window.prevEduConcept = prevEduConcept;
    window.toggleEduRotation = toggleEduRotation;
    window.exploreCurrentEduConcept = exploreCurrentEduConcept;

    function initEduCanvasApp() {
        // Ensure main search input placeholder is completely empty
        const mainInput = document.getElementById("mainSearchInput");
        if (mainInput) {
            mainInput.placeholder = "";
        }

        initCanvas();
        renderCurrentEduConcept(false);
        startProgressLoop();
        initKeyboardShortcuts();
        initSearchButtonState();

        const panel = document.getElementById("interactiveStudyPanel");
        if (panel) {
            panel.addEventListener("mouseenter", () => { isPaused = true; });
            panel.addEventListener("mouseleave", () => { isPaused = false; });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initEduCanvasApp);
    } else {
        initEduCanvasApp();
    }
})();
