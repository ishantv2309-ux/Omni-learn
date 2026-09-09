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
            domain: "⚖️ Law, Ethics & Jurisprudence",
            title: "Damnum Sine Injuria & Due Process",
            formula: "$$\\text{Damnum} \\neq \\text{Injuria} \\quad \\Big| \\quad \\textit{Audi alteram partem}$$",
            searchQuery: "Damnum Sine Injuria",
            insight: "Actual financial or material loss without the violation of an authorized legal right provides no ground for damages; and every individual has the natural right to be heard.",
            aura1: "rgba(244, 63, 94, 0.35)",
            aura2: "rgba(245, 158, 11, 0.3)"
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

    // Rich Academic & Intellectual Words across multiple disciplines
    const ACADEMIC_WORDS_BANK = [
        // Computer Science & AI
        { text: "Algorithm", domain: "cs" },
        { text: "Neural Networks", domain: "cs" },
        { text: "Recursion", domain: "cs" },
        { text: "Complexity", domain: "cs" },
        { text: "Turing Machine", domain: "cs" },
        { text: "Data Structures", domain: "cs" },
        { text: "Cryptography", domain: "cs" },
        { text: "Graph Theory", domain: "cs" },
        { text: "Heuristics", domain: "cs" },
        { text: "P vs NP", domain: "cs" },
        { text: "O(n log n)", domain: "cs" },
        { text: "Quantum Gate", domain: "cs" },
        { text: "Compiler", domain: "cs" },
        { text: "Binary Tree", domain: "cs" },
        { text: "Asymptote", domain: "cs" },
        { text: "Cybernetics", domain: "cs" },

        // Physics & Cosmology
        { text: "Thermodynamics", domain: "physics" },
        { text: "Superposition", domain: "physics" },
        { text: "Electromagnetism", domain: "physics" },
        { text: "General Relativity", domain: "physics" },
        { text: "Entropy", domain: "physics" },
        { text: "Wavefunction", domain: "physics" },
        { text: "E = mc²", domain: "physics" },
        { text: "Spacetime", domain: "physics" },
        { text: "Kinematics", domain: "physics" },
        { text: "Gravitation", domain: "physics" },
        { text: "Photon", domain: "physics" },
        { text: "Schrödinger", domain: "physics" },
        { text: "F = ma", domain: "physics" },
        { text: "Astrophysics", domain: "physics" },
        { text: "Optics", domain: "physics" },

        // Mathematics & Calculus
        { text: "Calculus", domain: "math" },
        { text: "Linear Algebra", domain: "math" },
        { text: "Differential Eq", domain: "math" },
        { text: "Integration", domain: "math" },
        { text: "Eigenvalue", domain: "math" },
        { text: "Topology", domain: "math" },
        { text: "Vector Space", domain: "math" },
        { text: "Probability", domain: "math" },
        { text: "∫ f(x)dx", domain: "math" },
        { text: "e^(iπ) + 1 = 0", domain: "math" },
        { text: "Riemann Sum", domain: "math" },
        { text: "Convergence", domain: "math" },
        { text: "Stochastic", domain: "math" },
        { text: "Isomorphism", domain: "math" },
        { text: "Fourier Transform", domain: "math" },

        // Biology, Neuroscience & Chemistry
        { text: "Neuroscience", domain: "bio" },
        { text: "Synapse", domain: "bio" },
        { text: "Photosynthesis", domain: "bio" },
        { text: "Metabolism", domain: "bio" },
        { text: "Molecular Genetics", domain: "bio" },
        { text: "Cellular", domain: "bio" },
        { text: "DNA Helix", domain: "bio" },
        { text: "RNA Polymerase", domain: "bio" },
        { text: "Neuroplasticity", domain: "bio" },
        { text: "Equilibrium", domain: "bio" },
        { text: "Homeostasis", domain: "bio" },
        { text: "Catalyst", domain: "bio" },
        { text: "Gibbs Energy", domain: "bio" },
        { text: "ATP Synthase", domain: "bio" },

        // Jurisprudence, Philosophy & Social Sciences
        { text: "Jurisprudence", domain: "law" },
        { text: "Epistemology", domain: "law" },
        { text: "Due Process", domain: "law" },
        { text: "Damnum Sine Injuria", domain: "law" },
        { text: "Dialectic", domain: "law" },
        { text: "Axiom", domain: "law" },
        { text: "Empirical", domain: "law" },
        { text: "Aequitas", domain: "law" },
        { text: "Hermeneutics", domain: "law" },
        { text: "Audi Alteram", domain: "law" },
        { text: "Cognition", domain: "law" },

        // Intellectual Inquiry & Method
        { text: "Synthesis", domain: "inquiry" },
        { text: "Hypothesis", domain: "inquiry" },
        { text: "Theorem", domain: "inquiry" },
        { text: "Discovery", domain: "inquiry" },
        { text: "Inquiry", domain: "inquiry" },
        { text: "Pedagogy", domain: "inquiry" },
        { text: "Analysis", domain: "inquiry" },
        { text: "Paradigm Shift", domain: "inquiry" }
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

        // Spawn words
        createParticles();
        animateCanvas();
    }

    let dpr = 1;
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
    }

    function createParticles() {
        particles = [];
        const w = window.innerWidth;
        const h = window.innerHeight;
        // Higher density of words across desktop and mobile screens
        const count = Math.min(92, Math.max(52, Math.floor((w * h) / 17000)));

        // Shuffle words bank
        const pool = [...ACADEMIC_WORDS_BANK].sort(() => 0.5 - Math.random());

        for (let i = 0; i < count; i++) {
            const wordObj = pool[i % pool.length];
            const depth = Math.random(); // 0 (far) to 1 (near)
            
            // Varied font sizes, weights and base alpha based on depth
            const fontSize = depth > 0.75 ? 15 : depth > 0.4 ? 13 : 11.5;
            const fontWeight = depth > 0.75 ? "600" : depth > 0.4 ? "500" : "400";
            const baseAlpha = depth > 0.75 
                ? (Math.random() * 0.18 + 0.32) 
                : depth > 0.4 
                    ? (Math.random() * 0.15 + 0.22) 
                    : (Math.random() * 0.12 + 0.14);

            const speedMultiplier = depth > 0.75 ? 0.35 : depth > 0.4 ? 0.28 : 0.20;

            particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                vx: (Math.random() - 0.5) * speedMultiplier,
                vy: (Math.random() - 0.5) * speedMultiplier,
                text: wordObj.text,
                domain: wordObj.domain,
                size: fontSize,
                weight: fontWeight,
                depth: depth,
                alpha: baseAlpha,
                baseAlpha: baseAlpha
            });
        }
    }

    function getWordColor(domain, isDark, alpha) {
        if (isDark) {
            switch (domain) {
                case "physics": return `rgba(134, 168, 207, ${alpha})`;  // Serene Periwinkle
                case "cs":      return `rgba(165, 180, 252, ${alpha})`;  // Soft Indigo
                case "math":    return `rgba(195, 142, 180, ${alpha})`;  // Orchid Rose
                case "bio":     return `rgba(110, 231, 183, ${alpha})`;  // Pale Mint
                case "law":     return `rgba(225, 203, 215, ${alpha})`;  // Lavender Blush
                default:        return `rgba(148, 163, 184, ${alpha})`;  // Slate Silver
            }
        } else {
            switch (domain) {
                case "physics": return `rgba(38, 66, 90, ${alpha})`;     // Prussian Blue
                case "cs":      return `rgba(67, 56, 202, ${alpha})`;    // Deep Indigo
                case "math":    return `rgba(140, 75, 120, ${alpha})`;   // Deep Rose
                case "bio":     return `rgba(15, 118, 110, ${alpha})`;   // Deep Teal
                case "law":     return `rgba(90, 50, 80, ${alpha})`;     // Plum Slate
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
        const baseLineColor = isDark ? "rgba(134, 168, 207, " : "rgba(79, 70, 229, ";

        // Update and draw particles
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];

            // Move
            p.x += p.vx;
            p.y += p.vy;

            // Soft wrap around edges
            if (p.x < -60) p.x = w + 60;
            if (p.x > w + 60) p.x = -60;
            if (p.y < -30) p.y = h + 30;
            if (p.y > h + 30) p.y = -30;

            // Mouse proximity gentle interaction
            const dx = mouse.x - p.x;
            const dy = mouse.y - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            let isHovered = false;

            if (dist < mouse.radius && dist > 1) {
                const force = (mouse.radius - dist) / mouse.radius;
                p.x -= (dx / dist) * force * 1.8;
                p.y -= (dy / dist) * force * 1.8;
                p.alpha = Math.min(0.92, p.baseAlpha + force * 0.55);
                isHovered = true;
            } else {
                p.alpha += (p.baseAlpha - p.alpha) * 0.05;
            }

            // Draw Word
            ctx.font = `${p.weight} ${p.size}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            if (isHovered) {
                // Subtle glowing aura around hovered words
                ctx.save();
                ctx.shadowColor = isDark ? "rgba(195, 142, 180, 0.7)" : "rgba(79, 70, 229, 0.6)";
                ctx.shadowBlur = 10;
                ctx.fillStyle = isDark ? `rgba(255, 255, 255, ${p.alpha})` : `rgba(30, 27, 75, ${p.alpha})`;
                ctx.fillText(p.text, p.x, p.y);
                ctx.restore();
            } else {
                ctx.fillStyle = getWordColor(p.domain, isDark, p.alpha);
                ctx.fillText(p.text, p.x, p.y);
            }

            // Connect nearby word nodes with subtle constellation webs
            const maxLineDist = 120;
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const lineDx = p.x - p2.x;
                const lineDy = p.y - p2.y;
                const lineDist = Math.sqrt(lineDx * lineDx + lineDy * lineDy);

                if (lineDist < maxLineDist) {
                    const factor = (1 - lineDist / maxLineDist);
                    let lineAlpha = factor * (isDark ? 0.12 : 0.07);
                    if (isHovered) lineAlpha *= 2.2;

                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `${baseLineColor}${lineAlpha})`;
                    ctx.lineWidth = isHovered ? 1.0 : 0.65;
                    ctx.stroke();
                }
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

    // Initialize on DOMContentLoaded
    document.addEventListener("DOMContentLoaded", () => {
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
    });
})();
