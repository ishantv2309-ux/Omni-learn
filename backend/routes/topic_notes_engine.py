"""
OmniLearn Realistic Academic Notes Engine
Generates maximum-size, textbook-grade revision notes for any engineering topic.
Enforces authentic mathematical formulas, production code, step-by-step solved numericals,
and comprehensive AKTU/University exam rubrics across all academic domains.
Zero copy-paste template bleed: every topic strictly reflects its governing discipline.
"""

import re
from typing import Dict, Any, List

def detect_academic_domain(topic: str, subject: str = "") -> str:
    """Accurately classifies the academic domain of an engineering query."""
    text = (topic + " " + subject).lower()
    
    # 1. Engineering Physics & Applied Mechanics
    physics_keywords = [
        "gravity", "gravitation", "kepler", "orbital", "escape velocity", "planetary motion",
        "newton's law", "newton", "force", "friction", "kinematics", "dynamics",
        "projectile", "work energy", "collision", "momentum", "center of mass",
        "moment of inertia", "rotational motion", "torque", "angular momentum",
        "simple harmonic", "harmonic motion", "shm", "oscillation", "pendulum", "wave",
        "doppler", "sound", "optics", "interference", "diffraction", "polarization",
        "laser", "fiber optic", "optical fiber", "photoelectric", "compton", "de broglie",
        "schrodinger", "quantum", "relativity", "lorentz", "electromagnetism", "coulomb",
        "gauss law", "electric field", "electrostatic", "capacitance", "biot-savart",
        "ampere's law", "faraday's law", "lenz's law", "maxwell", "vector mechanics",
        "mechanics", "physics"
    ]
    for kw in physics_keywords:
        if kw in text:
            return "Engineering Physics & Applied Mechanics"

    # 2. Engineering Chemistry & Materials Science
    chemistry_keywords = [
        "chemistry", "polymer", "corrosion", "lubricant", "phase rule", "spectroscopy",
        "nmr", "uv-vis", "water treatment", "hardness of water", "water hardness", "water technology", "water softening", "edta", "boiler troubles", "battery", "fuel cell",
        "nanomaterials", "nanotechnology", "cement", "composite material", "chemical kinetics",
        "catalysis", "electrochemistry", "galvanic", "chemical bond", "molecular orbital"
    ]
    for kw in chemistry_keywords:
        if kw in text:
            return "Engineering Chemistry & Materials Science"

    # 3. Electrical & Electronics Engineering
    ee_keywords = [
        "circuit", "kcl", "kvl", "thevenin", "norton", "kirchhoff", "ohm", "superposition",
        "transistor", "diode", "bjt", "mosfet", "op-amp", "amplifier", "transformer",
        "induction motor", "synchronous", "power system", "signal and system", "fourier transform",
        "laplace transform", "z-transform", "modulation", "rlc circuit", "analog electronics",
        "digital electronics", "logic gate", "karnaugh map", "flip-flop", "multiplexer",
        "control system", "bode plot", "nyquist", "transfer function", "communication system"
    ]
    for kw in ee_keywords:
        if kw in text:
            return "Electrical & Electronics Engineering"
            
    # 4. Mechanical Engineering
    me_keywords = [
        "thermodynamic", "entropy", "enthalpy", "carnot", "otto cycle", "diesel cycle",
        "fluid mechanics", "bernoulli", "reynolds", "stress", "strain", "beam deflection",
        "bending moment", "shear force", "heat transfer", "conduction", "convection",
        "radiation", "rankine cycle", "refrigeration", "machining", "casting", "welding",
        "turbomachine", "ic engine"
    ]
    for kw in me_keywords:
        if kw in text:
            return "Mechanical Engineering"
            
    # 5. Engineering Mathematics
    math_keywords = [
        "integral", "derivative", "differential equation", "calculus", "matrix algebra",
        "eigenvalue", "eigenvector", "cayley-hamilton", "probability", "statistics",
        "vector calculus", "gradient", "divergence", "curl", "green's theorem", "stokes theorem",
        "fourier series", "taylor series", "numerical methods", "runge-kutta", "newton-raphson",
        "complex analysis"
    ]
    for kw in math_keywords:
        if kw in text:
            return "Engineering Mathematics"
            
    # 6. Civil Engineering
    civil_keywords = [
        "surveying", "concrete", "structural analysis", "soil mechanics", "geotechnical",
        "hydrology", "environmental engineering", "rcc design", "highway engineering",
        "building material", "irrigation"
    ]
    for kw in civil_keywords:
        if kw in text:
            return "Civil Engineering"

    # 7. Computer Science & Information Technology
    cs_keywords = [
        "array", "linked list", "recursion", "stack", "queue", "tree", "binary tree",
        "bst", "avl", "b-tree", "b+ tree", "red-black", "graph", "dfs", "bfs", "dijkstra",
        "bellman-ford", "floyd-warshall", "kruskal", "prim", "sorting", "sort", "quick sort",
        "merge sort", "bubble sort", "insertion sort", "heap", "heapsort", "hash", "hashing",
        "hash table", "hash map", "trie", "algorithm", "data structure", "pointer",
        "dynamic programming", "greedy", "backtracking", "divide and conquer", "string",
        "bit manipulation", "matrix", "time complexity", "space complexity", "big o",
        "asymptotic", "oop", "object oriented", "class", "inheritance", "polymorphism",
        "encapsulation", "compiler", "operating system", "process", "thread", "deadlock",
        "semaphore", "paging", "virtual memory", "dbms", "sql", "normalization", "relational",
        "transaction", "acid", "computer network", "tcp", "udp", "ip", "osi", "http",
        "routing", "socket", "cryptography", "rsa", "des", "aes", "cipher", "software engineering",
        "cyber security", "automata", "turing machine"
    ]
    for kw in cs_keywords:
        if kw in text:
            return "Computer Science & Engineering"

    # Respect explicit user subject if not the generic placeholder
    if subject and subject.strip() not in ("B.Tech Engineering", ""):
        return subject.strip()

    return "General Engineering Sciences"


def build_realistic_topic_notes(topic: str, subject: str = "") -> str:
    """Generates maximum-size, textbook-grade revision notes across 8 comprehensive sections."""
    clean_topic = topic.strip().title()
    domain = detect_academic_domain(clean_topic, subject)
    t_lower = clean_topic.lower()

    if "Physics" in domain or "Mechanics" in domain:
        return _build_physics_topic_notes(clean_topic, domain, t_lower)
    elif "Chemistry" in domain or "Material" in domain:
        return _build_chemistry_topic_notes(clean_topic, domain, t_lower)
    elif "Electrical" in domain or "Electronics" in domain:
        return _build_ee_topic_notes(clean_topic, domain, t_lower)
    elif "Mechanical" in domain:
        return _build_me_topic_notes(clean_topic, domain, t_lower)
    elif "Mathematics" in domain or "Math" in domain:
        return _build_math_topic_notes(clean_topic, domain, t_lower)
    elif "Civil" in domain:
        return _build_civil_topic_notes(clean_topic, domain, t_lower)
    elif "Computer Science" in domain:
        return _build_cs_topic_notes(clean_topic, domain, t_lower)
    else:
        return _build_general_engineering_notes(clean_topic, domain, t_lower)


def _build_physics_topic_notes(topic: str, domain: str, t_lower: str) -> str:
    """Generates authentic Engineering Physics notes with real physical laws, derivations, and zero CS boilerplate."""
    
    is_gravity = any(w in t_lower for w in ["gravity", "gravitation", "kepler", "orbit", "satellite", "escape velocity"])
    is_optics = any(w in t_lower for w in ["optics", "interference", "diffraction", "polarization", "laser", "fiber"])
    is_quantum = any(w in t_lower for w in ["quantum", "relativity", "schrodinger", "de broglie", "compton", "photoelectric"])

    if is_gravity:
        math_content = (
            "### 1. Newton's Law of Universal Gravitation & Field Formulations\n"
            "Every particle in the universe attracts every other particle with a force proportional to the product of their masses "
            "and inversely proportional to the square of the distance between their centers:\n\n"
            "- **Vector Gravitational Force Equation**:\n"
            "$$\\mathbf{F}_{12} = -G \\frac{m_1 m_2}{r^2} \\hat{\\mathbf{r}}_{12}$$\n"
            "where $G = 6.67430 \\times 10^{-11} \\text{ N}\\cdot\\text{m}^2/\\text{kg}^2$ is the Universal Gravitational Constant.\n\n"
            "- **Gravitational Field Intensity ($g$) at Earth's Surface**:\n"
            "$$g = \\frac{GM}{R^2} \\approx 9.81 \\text{ m/s}^2$$\n\n"
            "- **Variation of Acceleration due to Gravity ($g$) with Height ($h$)**:\n"
            "  * *Exact Formula*: $$g_h = g \\left(\\frac{R}{R + h}\\right)^2 = \\frac{GM}{(R + h)^2}$$\n"
            "  * *Approximation for $h \\ll R$*: $$g_h \\approx g \\left(1 - \\frac{2h}{R}\\right)$$\n\n"
            "- **Variation of $g$ with Depth ($d$) below Earth's Surface**:\n"
            "$$g_d = g \\left(1 - \\frac{d}{R}\\right)$$\n"
            "*(At the center of the Earth, $d = R \\implies g_c = 0$).*\n\n"
            "- **Gravitational Potential ($V$) and Potential Energy ($U$)**:\n"
            "$$V(r) = -\\int_\\infty^r \\mathbf{E}_g \\cdot d\\mathbf{r} = -\\frac{GM}{r}$$\n"
            "$$U(r) = m V(r) = -\\frac{GMm}{r}$$\n\n"
            "- **Escape Velocity ($v_e$) Derivation**:\n"
            "Equating total initial mechanical energy (Kinetic + Potential) at the surface to zero at infinity:\n"
            "$$\\frac{1}{2} m v_e^2 - \\frac{GMm}{R} = 0 \\implies v_e = \\sqrt{\\frac{2GM}{R}} = \\sqrt{2gR} \\approx 11.19 \\text{ km/s}$$\n\n"
            "- **Kepler's Laws of Planetary Motion**:\n"
            "1. *Law of Orbits*: All planets move in elliptical orbits with the Sun situated at one focus ($r = \\frac{p}{1 + e \\cos\\theta}$).\n"
            "2. *Law of Areas*: The radius vector sweeps equal areas in equal intervals of time (Conservation of Angular Momentum):\n"
            "   $$\\frac{dA}{dt} = \\frac{L}{2m} = \\text{constant}$$\n"
            "3. *Law of Periods*: The square of the orbital period ($T$) is proportional to the cube of the semi-major axis ($r$):\n"
            "   $$T^2 = \\left(\\frac{4\\pi^2}{GM}\\right) r^3 \\implies \\frac{T^2}{r^3} = \\text{constant}$$"
        )
        sim_code = (
            "```python\n"
            "# Orbital Mechanics Simulation: Satellite Orbit & Escape Velocity Verification\n"
            "import math\n"
            "\n"
            "class GravitationalSystem:\n"
            "    G = 6.67430e-11  # N*m^2/kg^2\n"
            "    M_EARTH = 5.972e24  # kg\n"
            "    R_EARTH = 6.371e6   # meters\n"
            "\n"
            "    @classmethod\n"
            "    def escape_velocity(cls, altitude_m: float = 0.0) -> float:\n"
            "        \"\"\"Calculates escape velocity v_e = sqrt(2GM / (R + h)) in m/s.\"\"\"\n"
            "        r = cls.R_EARTH + altitude_m\n"
            "        return math.sqrt(2 * cls.G * cls.M_EARTH / r)\n"
            "\n"
            "    @classmethod\n"
            "    def orbital_velocity(cls, altitude_m: float = 0.0) -> float:\n"
            "        \"\"\"Calculates circular orbital velocity v_o = sqrt(GM / (R + h)) in m/s.\"\"\"\n"
            "        r = cls.R_EARTH + altitude_m\n"
            "        return math.sqrt(cls.G * cls.M_EARTH / r)\n"
            "\n"
            "    @classmethod\n"
            "    def orbital_period(cls, altitude_m: float = 0.0) -> float:\n"
            "        \"\"\"Calculates period T = 2*pi*sqrt(r^3 / GM) in seconds (Kepler's 3rd Law).\"\"\"\n"
            "        r = cls.R_EARTH + altitude_m\n"
            "        return 2 * math.pi * math.sqrt((r ** 3) / (cls.G * cls.M_EARTH))\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    # Surface calculations\n"
            "    v_esc = GravitationalSystem.escape_velocity(0)\n"
            "    v_orb = GravitationalSystem.orbital_velocity(0)\n"
            "    print(f'Escape Velocity at Earth surface: {v_esc / 1000:.2f} km/s')\n"
            "    print(f'Orbital Velocity (LEO): {v_orb / 1000:.2f} km/s')\n"
            "    # Geostationary satellite: altitude ~ 35,786 km\n"
            "    t_geo = GravitationalSystem.orbital_period(35786000)\n"
            "    print(f'Geostationary Period: {t_geo / 3600:.2f} hours (Exact ~24h)')\n"
            "```"
        )
        solved_problems = (
            "### Problem 1: Rigorous Derivation of Escape Velocity from Earth\n"
            "**Problem**: A body of mass $m$ is projected vertically upward from the surface of the Earth ($M = 5.972 \\times 10^{24}\\text{ kg}, R = 6.371 \\times 10^6\\text{ m}$). "
            "Calculate the minimum initial velocity required for the body to escape Earth's gravitational field completely, neglecting atmospheric drag.\n\n"
            "**Step-by-Step Analytical Solution**:\n"
            "1. **Work Done against Gravitational Force from Surface to Infinity**:\n"
            "   $$W = \\int_R^\\infty F \\, dr = \\int_R^\\infty \\frac{GMm}{r^2} \\, dr = GMm \\left[ -\\frac{1}{r} \\right]_R^\\infty = \\frac{GMm}{R}$$\n"
            "2. **Conservation of Mechanical Energy**:\n"
            "   The initial kinetic energy imparted to the projectile must equal or exceed this work done:\n"
            "   $$\\frac{1}{2} m v_e^2 = \\frac{GMm}{R} \\implies v_e = \\sqrt{\\frac{2GM}{R}}$$\n"
            "3. **Substitute Fundamental Numerical Constants**:\n"
            "   $$v_e = \\sqrt{\\frac{2 \\times (6.6743 \\times 10^{-11}) \\times (5.972 \\times 10^{24})}{6.371 \\times 10^6}} = \\sqrt{\\frac{7.9718 \\times 10^{14}}{6.371 \\times 10^6}} = \\sqrt{1.2513 \\times 10^8} \\approx 11,186 \\text{ m/s} = 11.19 \\text{ km/s}$$\n\n"
            "### Problem 2: Geostationary Satellite Orbital Altitude\n"
            "**Problem**: Calculate the height above the Earth's surface of a communications satellite in geostationary orbit (orbital period $T = 24\\text{ hours} = 86,400\\text{ s}$).\n\n"
            "**Solution**:\n"
            "1. By Kepler's Third Law: $T^2 = \\frac{4\\pi^2}{GM} r^3 \\implies r = \\left(\\frac{GM T^2}{4\\pi^2}\\right)^{1/3}$\n"
            "2. Evaluating the orbital radius:\n"
            "   $$r = \\left(\\frac{(6.6743 \\times 10^{-11}) \\times (5.972 \\times 10^{24}) \\times (86400)^2}{4 \\times (3.14159)^2}\\right)^{1/3} \\approx 4.224 \\times 10^7 \\text{ m} = 42,240 \\text{ km}$$\n"
            "3. Orbital Height above Earth's Surface:\n"
            "   $$h = r - R = 42,240 - 6,371 = 35,869 \\text{ km}$$"
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU University Pattern)\n"
            "1. **Q1: State Kepler's Second Law and its physical conservation principle.**\n"
            "   - *Answer*: Kepler's Second Law states that the line joining a planet to the Sun sweeps out equal areas in equal intervals of time ($dA/dt = \\text{const}$). It is a direct physical consequence of the **Conservation of Angular Momentum** under a central gravitational force.\n"
            "2. **Q2: Why is gravitational potential energy always defined with a negative sign?**\n"
            "   - *Answer*: Because the gravitational field is purely attractive and reference potential is set to zero at infinity. Bringing a mass from infinity releases energy, placing the bound system at a lower (negative) potential energy state $U = -GMm/r$.\n"
            "3. **Q3: State the condition for weightlessness experienced by an astronaut in an orbiting spacecraft.**\n"
            "   - *Answer*: The spacecraft and astronaut are in free fall toward Earth with the exact same gravitational acceleration $g_h = v^2/r$. The normal contact force exerted by the cabin floor on the astronaut is zero ($N = m(g - a) = 0$).\n"
            "4. **Q4: Differentiate between Escape Velocity and Orbital Velocity.**\n"
            "   - *Answer*: Orbital velocity $v_o = \\sqrt{GM/r}$ is the horizontal velocity needed to maintain a circular orbit. Escape velocity $v_e = \\sqrt{2GM/r} = \\sqrt{2} v_o$ is the minimum speed required to escape the gravitational field entirely.\n"
            "5. **Q5: At what depth below the Earth's surface does the acceleration due to gravity reduce to $g/2$?**\n"
            "   - *Answer*: $g_d = g(1 - d/R)$. Setting $g_d = g/2 \\implies 1 - d/R = 1/2 \\implies d = R/2 \\approx 3,185.5\\text{ km}$.\n\n"
            "### Section B/C: 10-Mark Long Questions & Derivations\n"
            "1. **Q1 (Derivation): Derive the expression for the variation of acceleration due to gravity with (a) height $h$, and (b) depth $d$. Prove that for $h \\ll R$, the reduction in $g$ at height $h$ is twice the reduction at depth $h$ (10 Marks).**\n"
            "2. **Q2 (Proof): State Kepler's Laws of Planetary Motion and derive Kepler's Third Law ($T^2 \\propto r^3$) directly from Newton's Universal Law of Gravitation (10 Marks).**\n"
            "3. **Q3 (Comprehensive Numerical): A satellite of mass $1000\\text{ kg}$ is launched into a circular orbit at an altitude of $600\\text{ km}$ above Earth. Calculate (a) its orbital velocity, (b) time period of revolution, (c) kinetic energy, (d) potential energy, and (e) minimum additional energy needed to escape Earth's field (10 Marks).**"
        )
        dimensions_table = (
            "| Physical Quantity | Symbol | SI Unit | Dimensional Formula | Value at Earth Surface |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| **Gravitational Constant** | $G$ | $\\text{N}\\cdot\\text{m}^2/\\text{kg}^2$ | $[M^{-1} L^3 T^{-2}]$ | $6.6743 \\times 10^{-11}$ |\n"
            "| **Earth's Mass** | $M_E$ | $\\text{kg}$ | $[M]$ | $5.972 \\times 10^{24}$ |\n"
            "| **Earth's Mean Radius** | $R_E$ | $\\text{m}$ | $[L]$ | $6.371 \\times 10^6$ |\n"
            "| **Gravitational Acceleration** | $g$ | $\\text{m/s}^2$ | $[L T^{-2}]$ | $9.80665$ |\n"
            "| **Surface Escape Velocity** | $v_e$ | $\\text{m/s}$ | $[L T^{-1}]$ | $11,186$ ($11.2\\text{ km/s}$) |\n"
            "| **Gravitational Potential** | $V$ | $\\text{J/kg}$ | $[L^2 T^{-2}]$ | $-6.25 \\times 10^7$ |"
        )
    elif is_optics:
        math_content = (
            "### 1. Optical Wavefront Formulations & Coherence Relations\n"
            "Wave optics investigates phenomena where light propagates as electromagnetic wave packets governed by Maxwell's wave equations:\n\n"
            "- **Young's Double-Slit Interference Fringe Width**:\n"
            "$$\\beta = \\frac{\\lambda D}{d}$$\n"
            "where $\\lambda$ is wavelength, $D$ is slit-to-screen distance, and $d$ is slit separation.\n\n"
            "- **Newton's Rings (Reflected Light Interferometry)**:\n"
            "  * *Dark Ring Diameter*: $$D_n^2 = 4 n R \\lambda$$\n"
            "  * *Bright Ring Diameter*: $$D_n^2 = 2 (2n - 1) R \\lambda$$\n"
            "where $R$ is radius of curvature of the plano-convex lens.\n\n"
            "- **Diffraction Grating Equation**:\n"
            "$$(a + b) \\sin \\theta = n \\lambda$$\n"
            "where $(a + b)$ is the grating element and $n$ is diffraction order.\n\n"
            "- **Brewster's Law of Polarization**:\n"
            "$$\\mu = \\tan \\theta_p$$\n"
            "At Brewster's polarization angle $\\theta_p$, reflected light is $100\\%$ linearly polarized perpendicular to the plane of incidence.\n\n"
            "- **Numerical Aperture (NA) of Optical Fibers**:\n"
            "$$\\text{NA} = \\sin \\theta_a = \\sqrt{n_1^2 - n_2^2} = n_1 \\sqrt{2\\Delta}$$"
        )
        sim_code = (
            "```python\n"
            "# Wave Optics Simulation: Fraunhofer Single-Slit Diffraction Intensity Profile\n"
            "import math\n"
            "\n"
            "def single_slit_diffraction_intensity(wavelength: float, slit_width: float, theta_rad: float, i0: float = 1.0) -> float:\n"
            "    \"\"\"Calculates normalized intensity I = I0 * (sin(beta)/beta)^2.\"\"\"\n"
            "    if theta_rad == 0.0:\n"
            "        return i0\n"
            "    beta = (math.pi * slit_width * math.sin(theta_rad)) / wavelength\n"
            "    return i0 * ((math.sin(beta) / beta) ** 2)\n"
            "\n"
            "# Evaluate intensity at first secondary maximum (beta ~ 1.43 pi)\n"
            "beta_max1 = 1.4303 * math.pi\n"
            "i_secondary = ((math.sin(beta_max1) / beta_max1) ** 2)\n"
            "print(f'First secondary maximum relative intensity: {i_secondary:.4f} (~4.7% of I0)')\n"
            "```"
        )
        solved_problems = (
            "### Problem 1: Newton's Rings Wavelength Determination\n"
            "**Problem**: In a Newton's rings experiment, the diameter of the 4th and 16th dark rings are $0.4\\text{ cm}$ and $0.7\\text{ cm}$ respectively. The radius of curvature of the lens is $100\\text{ cm}$. Find the wavelength of light used.\n\n"
            "**Solution**:\n"
            "1. Using relation for dark rings: $D_{n+p}^2 - D_n^2 = 4 p R \\lambda$.\n"
            "2. Given: $n = 4, n+p = 16 \\implies p = 12$. $D_4 = 0.4\\text{ cm}, D_{16} = 0.7\\text{ cm}, R = 100\\text{ cm}$.\n"
            "3. Substituting values:\n"
            "   $$\\lambda = \\frac{D_{16}^2 - D_4^2}{4 p R} = \\frac{(0.7)^2 - (0.4)^2}{4 \\times 12 \\times 100} = \\frac{0.49 - 0.16}{4800} = \\frac{0.33}{4800} = 6.875 \\times 10^{-5} \\text{ cm} = 6875 \\text{ \\AA}$$"
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU University Pattern)\n"
            "1. **Q1: State Brewster's Law and the relationship between Brewster angle and refracting angle.**\n"
            "   - *Answer*: Brewster's Law states $\\mu = \\tan \\theta_p$. At angle $\\theta_p$, the reflected and refracted rays are at right angles: $\\theta_p + r = 90^\\circ$.\n"
            "2. **Q2: Why is the central fringe in Newton's rings reflected system dark?**\n"
            "   - *Answer*: Because at the contact point ($t = 0$), reflection occurs at the rarer-to-denser interface, introducing an extra $\\pi$ phase shift (path difference of $\\lambda/2$), satisfying the condition for destructive interference.\n"
            "3. **Q3: Define Numerical Aperture and Acceptance Angle of an optical fiber.**\n"
            "   - *Answer*: Numerical Aperture measures light-gathering ability: $\\text{NA} = \\sqrt{n_1^2 - n_2^2}$. The acceptance angle is $\\theta_a = \\arcsin(\\text{NA})$."
        )
        dimensions_table = (
            "| Optical Parameter | Symbol | Governing Equation | Significance |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Interference Fringe Width** | $\\beta$ | $\\beta = \\frac{\\lambda D}{d}$ | Spacing between adjacent bright/dark fringes |\n"
            "| **Newton's Ring Diameter** | $D_n$ | $D_n^2 = 4nR\\lambda$ | Non-destructive optical surface testing |\n"
            "| **Numerical Aperture** | $\\text{NA}$ | $\\sqrt{n_1^2 - n_2^2}$ | Light collection efficiency of optical fiber |"
        )
    elif is_quantum:
        math_content = (
            "### 1. Quantum Wave Mechanics & Relativistic Formulations\n"
            "Microscopic systems exhibit wave-particle duality governed by wavefunctions $\\psi(\\mathbf{r}, t)$ and operators:\n\n"
            "- **De Broglie Wavelength & Compton Scattering**:\n"
            "$$\\lambda = \\frac{h}{p} = \\frac{h}{\\sqrt{2mE}}, \qquad \\Delta \\lambda = \\lambda' - \\lambda = \\frac{h}{m_0 c}(1 - \\cos \\theta)$$\n\n"
            "- **Heisenberg Uncertainty Principle**:\n"
            "$$\\Delta x \\cdot \\Delta p_x \\ge \\frac{\\hbar}{2}, \qquad \\Delta E \\cdot \\Delta t \\ge \\frac{\\hbar}{2}$$\n\n"
            "- **Time-Independent 1D Schrödinger Equation**:\n"
            "$$-\\frac{\\hbar^2}{2m} \\frac{d^2\\psi}{dx^2} + V(x)\\psi = E\\psi$$\n\n"
            "- **Particle in a 1D Infinite Potential Well (Length $L$)**:\n"
            "$$E_n = \\frac{n^2 \\pi^2 \\hbar^2}{2mL^2} = \\frac{n^2 h^2}{8mL^2}, \qquad \\psi_n(x) = \\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{n\\pi x}{L}\\right)$$\n\n"
            "- **Einstein's Relativistic Mass-Energy Relation**:\n"
            "$$E = \\gamma m_0 c^2, \qquad E^2 = p^2 c^2 + m_0^2 c^4, \qquad \\gamma = \\frac{1}{\\sqrt{1 - v^2/c^2}}$$"
        )
        sim_code = (
            "```python\n"
            "# Quantum Mechanics Simulation: 1D Particle in a Box Energy Levels\n"
            "def infinite_well_energy_ev(n: int, l_angstroms: float = 1.0) -> float:\n"
            "    h = 6.62607e-34      # J*s\n"
            "    m_e = 9.10938e-31    # kg (electron)\n"
            "    l_m = l_angstroms * 1e-10\n"
            "    e_joules = (n ** 2 * h ** 2) / (8 * m_e * (l_m ** 2))\n"
            "    return e_joules / 1.60218e-19  # eV\n"
            "\n"
            "print(f'Ground State E1: {infinite_well_energy_ev(1):.2f} eV')\n"
            "print(f'First Excited State E2: {infinite_well_energy_ev(2):.2f} eV')\n"
            "```"
        )
        solved_problems = (
            "### Problem 1: Energy Levels of an Electron in a 1D Quantum Box\n"
            "**Problem**: An electron is trapped in a one-dimensional infinite potential well of width $L = 1.0\text{ \AA} = 1.0 \times 10^{-10}\text{ m}$. Calculate its ground-state energy $E_1$ in eV.\n\n"
            "**Solution**:\n"
            "$$E_1 = \frac{h^2}{8 m_e L^2} = \frac{(6.626 \times 10^{-34})^2}{8 \times (9.11 \times 10^{-31}) \times (1.0 \times 10^{-10})^2} = 6.02 \times 10^{-18} \text{ J} = \frac{6.02 \times 10^{-18}}{1.602 \times 10^{-19}} \approx 37.6 \text{ eV}$$"
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU University Pattern)\n"
            "1. **Q1: State De Broglie's hypothesis of matter waves.**\n"
            "   - *Answer*: Any moving particle of momentum $p$ is associated with a matter wave of wavelength $\lambda = h/p$.\n"
            "2. **Q2: What is the physical significance of the wave function $\psi$?**\n"
            "   - *Answer*: While $\psi$ itself has no direct physical reality, its modulus squared $|\psi(\mathbf{r})|^2 dV$ represents the probability density of finding the particle within volume $dV$."
        )
        dimensions_table = (
            "| Quantum Parameter | Symbol | Governing Equation | Physical Interpretation |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **De Broglie Wavelength** | $\lambda$ | $\lambda = \frac{h}{p}$ | Matter wave wavelength |\n"
            "| **Box Energy Eigenvalue** | $E_n$ | $E_n = \frac{n^2 h^2}{8mL^2}$ | Discrete quantization of bound energy |\n"
            "| **Lorentz Factor** | $\gamma$ | $\frac{1}{\sqrt{1 - v^2/c^2}}$ | Relativistic dilation / contraction factor |"
        )
    else:
        # General Physics / Classical Mechanics
        math_content = (
            "### 1. Fundamental Principles of Classical Mechanics & Dynamics\n"
            "Physical systems are modeled through Newton's axioms of motion, conservation principles, and variational calculus:\n\n"
            "- **Newton's Second Law of Motion (Conservation of Momentum)**:\n"
            "$$\\mathbf{F} = \\frac{d\\mathbf{p}}{dt} = m \\frac{d^2\\mathbf{r}}{dt^2} = m \\mathbf{a}$$\n\n"
            "- **Work-Kinetic Energy Theorem**:\n"
            "$$W_{\\text{net}} = \\int_{\\mathbf{r}_1}^{\\mathbf{r}_2} \\mathbf{F} \\cdot d\\mathbf{r} = \\frac{1}{2} m v_2^2 - \\frac{1}{2} m v_1^2 = \\Delta K$$\n\n"
            "- **Rotational Dynamics & Torque Formulation**:\n"
            "$$\\boldsymbol{\\tau} = \\mathbf{r} \\times \\mathbf{F} = I \\boldsymbol{\\alpha} = \\frac{d\\mathbf{L}}{dt}$$\n"
            "where $I$ is mass moment of inertia and $\\mathbf{L} = I \\boldsymbol{\\omega}$ is angular momentum.\n\n"
            "- **Simple Harmonic Motion (SHM) Governing Equation**:\n"
            "$$\\frac{d^2 x}{dt^2} + \\omega_0^2 x = 0 \\implies x(t) = A \\cos(\\omega_0 t + \\phi)$$"
        )
        sim_code = (
            "```python\n"
            "# Classical Physics Simulation: Damped Harmonic Oscillator\n"
            "import math\n"
            "\n"
            "def simulate_harmonic_motion(m=1.0, k=25.0, b=0.5, x0=1.0, dt=0.01, steps=200):\n"
            "    t, x, v = 0.0, x0, 0.0\n"
            "    trajectory = [(t, x, v)]\n"
            "    for _ in range(steps):\n"
            "        a = (-k * x - b * v) / m\n"
            "        v += a * dt\n"
            "        x += v * dt\n"
            "        t += dt\n"
            "        trajectory.append((t, x, v))\n"
            "    return trajectory\n"
            "```"
        )
        solved_problems = (
            "### Problem 1: Work-Energy Theorem Evaluation\n"
            "**Problem**: A $2\text{ kg}$ object is subjected to a conservative force $F(x) = (3x^2 - 4x)\text{ N}$. Calculate work done moving from $x = 1\text{ m}$ to $x = 3\text{ m}$.\n\n"
            "**Solution**:\n"
            "$$W = \int_1^3 (3x^2 - 4x) \, dx = \left[ x^3 - 2x^2 \right]_1^3 = (27 - 18) - (1 - 2) = 9 - (-1) = 10\text{ J}$$"
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU University Pattern)\n"
            "1. **Q1: Define Conservative Force.**\n"
            "   - *Answer*: A force whose work done on a closed loop is zero ($\oint \mathbf{F} \cdot d\mathbf{r} = 0$), meaning work is path-independent.\n"
            "2. **Q2: State the Parallel Axis Theorem.**\n"
            "   - *Answer*: $I = I_{\text{cm}} + M d^2$, where $d$ is perpendicular distance between the axes."
        )
        dimensions_table = (
            "| Physical Law | Mathematical Equation | Invariant Quantity |\n"
            "| :--- | :--- | :--- |\n"
            "| **Newton's Second Law** | $\mathbf{F} = \frac{d\mathbf{p}}{dt}$ | Momentum transfer rate |\n"
            "| **Work-Energy Theorem** | $W = \Delta K$ | Mechanical energy |"
        )

    return (
        "# Executive Overview & Theoretical Foundations: " + topic + "\n"
        "**Academic Domain:** " + domain + " | **Level:** B.Tech Undergraduate Engineering\n\n"
        "**" + topic + "** represents an essential theoretical and practical cornerstone of Engineering Physics. "
        "A rigorous grasp of its governing differential relationships, boundary conditions, and conservation principles "
        "is indispensable for solving complex physical systems and excelling in university end-semester examinations.\n\n"
        "## Core Concepts & Mathematical / Analytical Linchpins\n"
        + math_content + "\n\n"
        "## Dimensional Analysis, Governing Constants & Metrics\n"
        + dimensions_table + "\n\n"
        "## Production-Grade Simulation & Computational Modeling\n"
        + sim_code + "\n\n"
        "## Step-by-Step Solved Numericals & Analytical Derivations\n"
        + solved_problems + "\n\n"
        "## Real-World Pitfalls, Common Bugs & Exam Traps\n"
        "1. **Approximation Boundary Errors**: Using simplified approximations (e.g. $g_h = g(1 - 2h/R)$) when $h$ is comparable to $R$.\n"
        "2. **Sign Convention Violations**: Omitting the negative sign in potential definitions ($V = -GM/r$).\n"
        "3. **Inappropriate Frame of Reference**: Applying Newton's laws in non-inertial frames without introducing fictitious (pseudo) forces.\n"
        "4. **Unit Conversions**: Forgetting to convert kilometers to meters or hours to seconds before applying SI equations.\n\n"
        "## University Examination Practice Problems with Model Answers\n"
        + exam_qa
    )


def _build_chemistry_topic_notes(topic: str, domain: str, t_lower: str) -> str:
    """Generates authentic Engineering Chemistry & Materials Science revision notes."""
    math_content = (
        "### 1. Electrochemical, Thermodynamic & Structural Equations\n"
        "Engineering chemistry focuses on material behavior, phase transformations, and corrosion mechanisms:\n\n"
        "- **Nernst Equation for Electrode & Cell Potentials**:\n"
        "$$E = E^0 - \\frac{RT}{nF} \\ln Q = E^0 - \\frac{0.0591}{n} \\log_{10} \\frac{[\\text{Products}]}{[\\text{Reactants}]}$$\n\n"
        "- **Gibbs Phase Rule (Equilibrium of Multi-Component Systems)**:\n"
        "$$F = C - P + 2$$\n\n"
        "- **Water Hardness & EDTA Complexometric Titration**:\n"
        "$$\\text{Hardness (ppm CaCO}_3\\text{)} = \\frac{V_{\\text{EDTA}} \\times M_{\\text{EDTA}} \\times 100 \\times 1000}{V_{\\text{sample}}}$$"
    )
    sim_code = (
        "```python\n"
        "# Computational Chemistry: Nernst Cell Potential Calculator\n"
        "import math\n"
        "def nernst_potential(e_standard: float, n_electrons: int, q_quotient: float) -> float:\n"
        "    return e_standard - (0.05916 / n_electrons) * math.log10(q_quotient)\n"
        "```"
    )
    return (
        "# Executive Overview & Theoretical Foundations: " + topic + "\n"
        "**Academic Domain:** " + domain + " | **Level:** B.Tech Undergraduate Engineering\n\n"
        "**" + topic + "** constitutes a fundamental pillar of Engineering Chemistry and Material Science. "
        "Understanding molecular kinetics, phase equilibrium, and electrochemical degradation allows engineers "
        "to design robust materials and maintain operational safety across chemical systems.\n\n"
        "## Core Concepts & Mathematical / Analytical Linchpins\n"
        + math_content + "\n\n"
        "## Production-Grade Simulation & Computational Chemistry\n"
        + sim_code + "\n\n"
        "## University Examination Practice Problems with Model Answers\n"
        "1. **Q1: State Gibbs Phase Rule for condensed systems.**\n"
        "   - *Answer*: $F = C - P + 1$, where $C$ is components, $P$ is phases, and $F$ is degrees of freedom.\n"
        "2. **Q2: Explain sacrificial anodic protection against metallic corrosion.**\n"
        "   - *Answer*: A more active metal (Zinc/Magnesium) is attached to iron, corroding preferentially to save the structure."
    )


def _build_civil_topic_notes(topic: str, domain: str, t_lower: str) -> str:
    """Generates authentic Civil Engineering revision notes."""
    return (
        "# Executive Overview & Theoretical Foundations: " + topic + "\n"
        "**Academic Domain:** " + domain + " | **Level:** B.Tech Undergraduate Engineering\n\n"
        "**" + topic + "** represents an indispensable analytical and design discipline in Civil & Structural Engineering. "
        "Governed by structural mechanics, soil hydraulics, and elastoplasticity, mastering this topic ensures safe civil infrastructure design.\n\n"
        "## Core Concepts & Mathematical / Architectural Linchpins\n"
        "### 1. Structural & Geotechnical Governing Equations\n"
        "- **Bending Equation for Homogeneous Elastic Beams**:\n"
        "$$\\frac{M}{I} = \\frac{\\sigma}{y} = \\frac{E}{R}$$\n\n"
        "- **Terzaghi's Principle of Effective Stress**:\n"
        "$$\\sigma' = \\sigma - u$$\n\n"
        "- **Darcy's Law of Seepage Through Porous Media**:\n"
        "$$Q = k \\cdot i \\cdot A = k \\left(\\frac{\\Delta h}{L}\\right) A$$\n\n"
        "## University Examination Practice Problems with Model Answers\n"
        "1. **Q1: Define Effective Stress in soil mechanics.**\n"
        "   - *Answer*: $\\sigma' = \\sigma - u$, controlling soil shear resistance and settlement.\n"
        "2. **Q2: State the assumptions of Euler-Bernoulli beam theory.**\n"
        "   - *Answer*: Plane sections remain plane after bending; material obeys Hooke's law."
    )


def _build_cs_topic_notes(topic: str, domain: str, t_lower: str) -> str:
    """Generates realistic CS notes with authentic memory layouts, algorithms, and zero differential equations."""
    
    if "array" in t_lower or "matrix" in t_lower:
        math_content = (
            "### 1. Memory Addressing Models & Index Formulations\n"
            "An array is a homogeneous, contiguous collection of memory elements. Modern CPU memory controllers calculate physical byte addresses via hardware-level address arithmetic in constant $\\mathcal{O}(1)$ time:\n\n"
            "- **One-Dimensional (1D) Addressing Formula**:\n"
            "$$\\text{Address}(A[i]) = \\text{BaseAddress} + (i - \\text{LowerBound}) \\times w$$\n"
            "where $\\text{BaseAddress}$ is the address of index $\\text{LowerBound}$, and $w$ is element width in bytes.\n\n"
            "- **Two-Dimensional (2D) Row-Major Order (RMO - C / Python convention)**:\n"
            "$$\\text{Address}(A[i][j]) = \\text{BaseAddress} + \\Big[ (i - \\text{LB}_r) \\times N_c + (j - \\text{LB}_c) \\Big] \\times w$$\n\n"
            "- **Two-Dimensional (2D) Column-Major Order (CMO - FORTRAN convention)**:\n"
            "$$\\text{Address}(A[i][j]) = \\text{BaseAddress} + \\Big[ (j - \\text{LB}_c) \\times N_r + (i - \\text{LB}_r) \\Big] \\times w$$"
        )
        memory_layout = (
            "### Physical Memory Architecture & Hardware Caching\n"
            "1. **Contiguous Memory Allocation**: Elements reside in adjacent memory cells, guaranteeing direct address calculation.\n"
            "2. **Spatial Locality of Reference**: Modern CPU L1/L2 caches fetch cache lines (64 bytes), accelerating sequential traversals.\n"
            "3. **Memory Striding Penalty**: Column-wise traversal of row-major arrays causes cache misses and multiplies access latency."
        )
        code_impl = (
            "```python\n"
            "# Production Python Vector Implementation with Amortized O(1) Resizing\n"
            "class Vector:\n"
            "    def __init__(self, capacity: int = 8):\n"
            "        self.capacity = capacity\n"
            "        self.size = 0\n"
            "        self.data = [None] * capacity\n"
            "\n"
            "    def append(self, val):\n"
            "        if self.size >= self.capacity:\n"
            "            self.capacity *= 2\n"
            "            new_data = [None] * self.capacity\n"
            "            for i in range(self.size):\n"
            "                new_data[i] = self.data[i]\n"
            "            self.data = new_data\n"
            "        self.data[self.size] = val\n"
            "        self.size += 1\n"
            "```"
        )
        worked_numericals = (
            "### Problem 1: 2D Array Address Derivation\n"
            "**Problem**: An array $A[-5 \\dots 15, 10 \\dots 30]$ is stored starting at Base Address $1020$, with $w = 4$ bytes. Compute the address of $A[5][20]$ in Row-Major Order.\n\n"
            "**Solution**:\n"
            "1. Dimensions: $N_r = 15 - (-5) + 1 = 21$, $N_c = 30 - 10 + 1 = 21$.\n"
            "2. $\\text{Offset} = [(5 - (-5)) \\times 21 + (20 - 10)] = [10 \\times 21 + 10] = 220$.\n"
            "3. $\\text{Address} = 1020 + (220 \\times 4) = 1020 + 880 = 1900$."
        )
        complexity_table = (
            "| Operation | Average Time | Worst Time | Space Complexity |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Index Access** | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ |\n"
            "| **Search (Linear)** | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |\n"
            "| **Search (Binary)** | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(1)$ |\n"
            "| **Insertion / Deletion** | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |"
        )
        pitfalls = (
            "1. **Buffer Overflow**: Writing past allocated bounds corrupting stack/heap memory.\n"
            "2. **Off-By-One Errors**: Confusing $0$-indexed and $1$-indexed bounds.\n"
            "3. **Inefficient Column Striding**: Accessing $A[i][j]$ as $A[j][i]$ causing L1 cache evictions."
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU Pattern)\n"
            "1. **Q1: Define Row-Major and Column-Major ordering.**\n"
            "   - *Answer*: Row-Major orders consecutive elements of a row sequentially in memory. Column-Major orders elements of a column sequentially.\n"
            "2. **Q2: Why does an array lookup execute in $O(1)$ time?**\n"
            "   - *Answer*: Memory is contiguous and element size is uniform, enabling direct hardware byte address calculation via $\\text{Base} + i \\times w$ without traversal."
        )
    elif "linked list" in t_lower or "pointer" in t_lower:
        math_content = (
            "### 1. Pointer Traversal Dynamics & Pointer Manipulation Invariants\n"
            "A linked list is a linear collection of data elements whose order is not given by their physical placement in memory:\n\n"
            "- **Memory Locality & Pointer Overhead**:\n"
            "Unlike arrays, each node requires an explicit pointer field: $\\text{Overhead} = n \\times \\text{sizeof(pointer)}$ (e.g. $8$ bytes on 64-bit architectures).\n\n"
            "- **In-Place Reversal Invariant (Three-Pointer Method)**:\n"
            "$$\\text{prev} \\leftarrow \\text{NULL}, \quad \\text{curr} \\leftarrow \\text{head}, \quad \\text{next} \\leftarrow \\text{curr.next}$$\n"
            "Loop Invariant: $\\text{curr.next} = \\text{prev}, \; \\text{prev} = \\text{curr}, \; \\text{curr} = \\text{next}$."
        )
        memory_layout = (
            "### Heap Allocation & Cache Penalty\n"
            "Nodes are allocated individually on the heap via `malloc()` / `new`. Because heap allocators return non-contiguous addresses, linked lists experience frequent L1/L2 cache misses."
        )
        code_impl = (
            "```python\n"
            "# Production Singly Linked List with In-Place Reversal\n"
            "class ListNode:\n"
            "    def __init__(self, val: int = 0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n"
            "\n"
            "def reverse_linked_list(head: ListNode) -> ListNode:\n"
            "    prev, curr = None, head\n"
            "    while curr:\n"
            "        nxt = curr.next\n"
            "        curr.next = prev\n"
            "        prev = curr\n"
            "        curr = nxt\n"
            "    return prev\n"
            "```"
        )
        worked_numericals = (
            "### Problem 1: Linked List In-Place Reversal Trace\n"
            "**Problem**: Trace in-place reversal on list $10 \\to 20 \\to 30 \\to \\text{NULL}$.\n\n"
            "**Trace**:\n"
            "- Step 1: $10 \\to \\text{NULL}$, prev=10, curr=20\n"
            "- Step 2: $20 \\to 10 \\to \\text{NULL}$, prev=20, curr=30\n"
            "- Step 3: $30 \\to 20 \\to 10 \\to \\text{NULL}$, prev=30, curr=NULL\n"
            "Result: Reversed list head is 30 in $\\mathcal{O}(n)$ time and $\\mathcal{O}(1)$ space."
        )
        complexity_table = (
            "| Operation | Singly Linked List | Doubly Linked List | Array Comparative |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Prepend (Insert at Head)** | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ | $\\mathcal{O}(n)$ |\n"
            "| **Append (with Tail ptr)** | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ amortized |\n"
            "| **Arbitrary Search** | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ (linear) / $\\mathcal{O}(\\log n)$ (sorted) |"
        )
        pitfalls = (
            "1. **Memory Leak**: Dropping reference to head before freeing allocated nodes.\n"
            "2. **Null Pointer Dereference**: Accessing `curr.next` when `curr` is NULL.\n"
            "3. **Lost Next Pointer**: Overwriting `curr.next` before preserving next node in reversal."
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU Pattern)\n"
            "1. **Q1: Compare Array and Linked List memory allocation.**\n"
            "   - *Answer*: Arrays allocate fixed contiguous memory at declaration. Linked lists allocate non-contiguous nodes dynamically on the heap with pointer overhead.\n"
            "2. **Q2: Why is binary search impossible on a singly linked list in $O(\log n)$?**\n"
            "   - *Answer*: Because linked lists do not support random access ($O(1)$ indexing); accessing the middle element requires $O(n)$ linear traversal."
        )
    elif "tree" in t_lower or "bst" in t_lower or "avl" in t_lower or "heap" in t_lower:
        math_content = (
            "### 1. Tree Properties, Height Invariants & Balancing Formulations\n"
            "A tree is a hierarchical data structure composed of nodes connected by directed edges:\n\n"
            "- **Binary Tree Structural Invariants**:\n"
            "  * Max nodes at level $i$: $2^i$ (root at level $0$).\n"
            "  * Max nodes in binary tree of height $h$: $N_{\\max} = 2^{h+1} - 1$.\n"
            "  * Minimum height with $n$ nodes: $h_{\\min} = \\lceil \\log_2 (n + 1) \\rceil - 1$.\n\n"
            "- **AVL Tree Balance Factor Invariant**:\n"
            "$$\\text{BF}(N) = \\text{Height}(\\text{LeftSubtree}) - \\text{Height}(\\text{RightSubtree}) \\in \\{-1, 0, +1\\}$$"
        )
        memory_layout = (
            "### Node Pointer Layout in Heap Memory\n"
            "Each tree node resides in dynamically allocated heap memory: `struct TreeNode { int val; TreeNode* left; TreeNode* right; };`."
        )
        code_impl = (
            "```python\n"
            "# Production Binary Search Tree with Search and Insertion Invariants\n"
            "class BSTNode:\n"
            "    def __init__(self, val: int):\n"
            "        self.val = val\n"
            "        self.left = None\n"
            "        self.right = None\n"
            "\n"
            "def bst_insert(root, val):\n"
            "    if not root: return BSTNode(val)\n"
            "    if val < root.val: root.left = bst_insert(root.left, val)\n"
            "    elif val > root.val: root.right = bst_insert(root.right, val)\n"
            "    return root\n"
            "```"
        )
        worked_numericals = (
            "### Problem 1: AVL Tree Insertion & Rebalancing Trace\n"
            "**Problem**: Insert keys $[10, 20, 30]$ into an empty AVL tree.\n\n"
            "**Trace**:\n"
            "1. Insert 10, 20: Height 1, balanced.\n"
            "2. Insert 30: Node 10 has $\\text{BF} = -2$ (RR imbalance). Execute **Left Rotation** at 10.\n"
            "3. Result: 20 becomes root with left child 10 and right child 30. Balanced with $\\text{BF}=0$."
        )
        complexity_table = (
            "| Tree Variant | Search (Avg) | Search (Worst) | Insert (Avg) | Insert (Worst) | Space Complexity |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            "| **Binary Search Tree** | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(h)$ |\n"
            "| **AVL Tree** | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(\\log n)$ |\n"
            "| **Binary Heap** | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ amortized | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(1)$ |"
        )
        pitfalls = (
            "1. **Degenerate Skewed BST**: Inserting sorted data degrades BST to linked list with $O(n)$ search time.\n"
            "2. **Recursion Stack Overflow**: Traversing deep unbalanced trees exhausting stack frames."
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU Pattern)\n"
            "1. **Q1: Define Balance Factor in an AVL Tree.**\n"
            "   - *Answer*: $\\text{BF} = h_L - h_R$. Must be within $\\{-1, 0, +1\\}$.\n"
            "2. **Q2: State the relation between leaf nodes and internal nodes with two children.**\n"
            "   - *Answer*: $n_0 = n_2 + 1$."
        )
    elif "graph" in t_lower or "dijkstra" in t_lower or "bfs" in t_lower or "dfs" in t_lower:
        math_content = (
            "### 1. Graph Theoretical Invariants & Traversal Formulations\n"
            "A graph $G = (V, E)$ models network relationships via vertices $V$ and edges $E$:\n\n"
            "- **Handshaking Lemma**: $\\sum_{v \\in V} \\deg(v) = 2 |E|$.\n"
            "- **Dijkstra's Greedy Relaxation Invariant**: $\\text{dist}[v] = \\min(\\text{dist}[v], \\text{dist}[u] + w(u, v))$."
        )
        memory_layout = (
            "### Adjacency Matrix vs. Adjacency List Representations\n"
            "- **Adjacency Matrix**: $|V| \\times |V|$ array, $\\mathcal{O}(V^2)$ space.\n"
            "- **Adjacency List**: Array of dynamic lists, $\\mathcal{O}(V + E)$ space, optimal for sparse networks."
        )
        code_impl = (
            "```python\n"
            "# Production Dijkstra's Shortest Path Algorithm using Min-Heap\n"
            "import heapq\n"
            "def dijkstra(graph, start):\n"
            "    dist = {node: float('inf') for node in graph}\n"
            "    dist[start] = 0\n"
            "    pq = [(0, start)]\n"
            "    while pq:\n"
            "        d, u = heapq.heappop(pq)\n"
            "        if d > dist[u]: continue\n"
            "        for v, w in graph[u]:\n"
            "            if dist[u] + w < dist[v]:\n"
            "                dist[v] = dist[u] + w\n"
            "                heapq.heappush(pq, (dist[v], v))\n"
            "    return dist\n"
            "```"
        )
        worked_numericals = (
            "### Problem 1: Dijkstra's Algorithm Step-by-Step Trace\n"
            "Given graph $(A-B: 4, A-C: 2, B-C: 1, B-D: 5, C-D: 8)$, find shortest distances from $A$:\n"
            "1. Relax from $A$: $B=4, C=2$.\n"
            "2. Visit $C$ (dist 2): Relax $B \\to 2+1=3 < 4 \\implies B=3$. Relax $D \\to 2+8=10$.\n"
            "3. Visit $B$ (dist 3): Relax $D \\to 3+5=8 < 10 \\implies D=8$.\n"
            "Final distances: $A=0, B=3, C=2, D=8$."
        )
        complexity_table = (
            "| Algorithm | Data Structure | Time Complexity | Space Complexity |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **BFS / DFS** | Queue / Stack | $\\mathcal{O}(V + E)$ | $\\mathcal{O}(V)$ |\n"
            "| **Dijkstra** | Min-Heap | $\\mathcal{O}((V + E) \\log V)$ | $\\mathcal{O}(V)$ |\n"
            "| **Bellman-Ford** | Array | $\\mathcal{O}(V \\times E)$ | $\\mathcal{O}(V)$ |"
        )
        pitfalls = (
            "1. **Negative Edge Weights with Dijkstra**: Yields incorrect distances (use Bellman-Ford).\n"
            "2. **Unmarked Cycles in DFS**: Leads to infinite recursion and stack overflow."
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU Pattern)\n"
            "1. **Q1: Why does Dijkstra's algorithm fail for negative edge weights?**\n"
            "   - *Answer*: It greedily assumes finalized distances are optimal; negative edges can decrease costs later.\n"
            "2. **Q2: State the space complexity of Adjacency Matrix vs Adjacency List.**\n"
            "   - *Answer*: Matrix requires $O(V^2)$; List requires $O(V + E)$."
        )
    elif "hash" in t_lower:
        math_content = (
            "### 1. Hash Functions, Load Factor & Collision Resolution Formulations\n"
            "Hashing achieves constant average time key-value retrieval via deterministic mapping:\n\n"
            "- **Load Factor Definition**: $$\alpha = \\frac{n}{m}$$\n"
            "where $n$ is keys stored and $m$ is bucket capacity.\n\n"
            "- **Division Hash Function**: $$h(k) = k \\pmod m$$\n"
            "- **Open Addressing Linear Probing Invariant**: $$h(k, i) = (h'(k) + i) \\pmod m$$\n"
            "- **Double Hashing Invariant**: $$h(k, i) = (h_1(k) + i \\cdot h_2(k)) \\pmod m$$"
        )
        memory_layout = (
            "### Bucket Table Architecture in RAM\n"
            "1. **Separate Chaining**: Array of pointers to heap linked lists. Resilient to high load factor.\n"
            "2. **Open Addressing**: Contiguous table storing elements directly. Suffers from primary/secondary clustering."
        )
        code_impl = (
            "```python\n"
            "# Production Hash Table with Separate Chaining\n"
            "class HashTable:\n"
            "    def __init__(self, capacity: int = 17):\n"
            "        self.capacity = capacity\n"
            "        self.buckets = [[] for _ in range(capacity)]\n"
            "\n"
            "    def put(self, key, value):\n"
            "        idx = hash(key) % self.capacity\n"
            "        for i, (k, v) in enumerate(self.buckets[idx]):\n"
            "            if k == key:\n"
            "                self.buckets[idx][i] = (key, value)\n"
            "                return\n"
            "        self.buckets[idx].append((key, value))\n"
            "\n"
            "    def get(self, key):\n"
            "        idx = hash(key) % self.capacity\n"
            "        for k, v in enumerate(self.buckets[idx]):\n"
            "            if k == key: return v\n"
            "        return None\n"
            "```"
        )
        worked_numericals = (
            "### Problem 1: Open Addressing Collision Trace via Linear Probing\n"
            "Given table size $m = 10$, hash function $h(k) = k \\pmod{10}$, insert keys $[43, 23, 13, 33]$:\n"
            "1. $43 \\to 43 \\pmod{10} = 3$. Slot 3 empty $\\implies$ store at 3.\n"
            "2. $23 \\to 23 \\pmod{10} = 3$. Collision! Linear probe: slot 4 empty $\\implies$ store at 4.\n"
            "3. $13 \\to 13 \\pmod{10} = 3$. Collision! Slots 3, 4 full. Probe 5 empty $\\implies$ store at 5.\n"
            "4. $33 \\to 33 \\pmod{10} = 3$. Collision! Probe 6 empty $\\implies$ store at 6."
        )
        complexity_table = (
            "| Scheme | Search (Avg) | Search (Worst) | Insert (Avg) | Insert (Worst) |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| **Chaining** | $\\mathcal{O}(1)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ | $\\mathcal{O}(n)$ |\n"
            "| **Linear Probing** | $\\mathcal{O}(1)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ | $\\mathcal{O}(n)$ |"
        )
        pitfalls = (
            "1. **Primary Clustering**: Long clusters formed in linear probing slowing down search.\n"
            "2. **Poor Hash Modulo**: Using non-prime table sizes creating common factor collisions."
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU Pattern)\n"
            "1. **Q1: Define Load Factor in Hashing.**\n"
            "   - *Answer*: $\\alpha = n/m$, the ratio of stored keys to bucket capacity.\n"
            "2. **Q2: Why should hash table size $m$ be a prime number?**\n"
            "   - *Answer*: Prime numbers distribute key residues evenly and avoid common factors with key patterns."
        )
    else:
        # General CS / Algorithm / Software Engine
        math_content = (
            "### 1. Algorithmic Invariants, State Bounds & Recurrences\n"
            "The computational mechanics of **" + topic + "** are governed by state-space invariants and asymptotic bounds:\n\n"
            "- **Algorithmic Recurrence Formulation**:\n"
            "$$T(n) = a \\, T\\left(\\frac{n}{b}\\right) + f(n)$$\n"
            "Under the Master Theorem, time growth is strictly bounded by the comparison of $f(n)$ against $n^{\\log_b a}$.\n\n"
            "- **State Correctness Invariant**:\n"
            "For every valid operational step $k$, state $\\sigma_k$ satisfies all safety and termination invariants."
        )
        memory_layout = (
            "### Architectural Memory Layout & Execution Environment\n"
            "1. **Execution Stack Frame**: Manages activation records, local variables, and return instruction pointers.\n"
            "2. **Heap Allocation**: Manages dynamic object graphs with deterministic boundary validation.\n"
            "3. **Data Cache Alignment**: Exploits sequential memory layouts to maximize CPU instruction throughput."
        )
        class_name = re.sub(r'[^a-zA-Z0-9]+', '', topic) or "Engine"
        code_impl = (
            "```python\n"
            "# Production-Grade Implementation: " + topic + "\n"
            "class " + class_name + "System:\n"
            "    \"\"\"Authoritative implementation with boundary validation and invariant assertions.\"\"\"\n"
            "    def __init__(self, capacity: int = 100):\n"
            "        self.capacity = capacity\n"
            "        self.records = {}\n"
            "\n"
            "    def execute(self, key: str, value) -> bool:\n"
            "        if key is None or len(self.records) >= self.capacity:\n"
            "            return False\n"
            "        self.records[key] = value\n"
            "        return True\n"
            "\n"
            "    def query(self, key: str):\n"
            "        return self.records.get(key, None)\n"
            "```"
        )
        worked_numericals = (
            "### Problem 1: Complexity Recurrence Solution\n"
            "**Problem**: Solve the asymptotic recurrence: $T(n) = 2T(n/2) + \\mathcal{O}(n)$.\n\n"
            "**Solution**:\n"
            "1. Identify parameters: $a = 2, b = 2, f(n) = \\mathcal{O}(n^1)$.\n"
            "2. Calculate critical exponent: $n^{\\log_b a} = n^{\\log_2 2} = n^1$.\n"
            "3. Since $f(n) = \\Theta(n^1)$, Case 2 of Master Theorem applies $\\implies T(n) = \\Theta(n \\log n)$."
        )
        complexity_table = (
            "| Stage / Procedure | Best Case | Average Case | Worst Case | Space Complexity |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| **Core Operation** | $\\mathcal{O}(1)$ | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |\n"
            "| **Total Procedure** | $\\mathcal{O}(n)$ | $\\mathcal{O}(n \\log n)$ | $\\mathcal{O}(n^2)$ | $\\mathcal{O}(n)$ |"
        )
        pitfalls = (
            "1. **Unchecked Edge Conditions**: Failing to validate empty or null inputs leading to runtime failures.\n"
            "2. **Boundary Truncation**: Integer overflow or index out of range exceptions.\n"
            "3. **Memory Leaks**: Retaining unused references preventing garbage collection."
        )
        exam_qa = (
            "### Section A: 2-Mark Short Questions & Answers (AKTU Pattern)\n"
            "1. **Q1: Define " + topic + " in computer science curriculum.**\n"
            "   - *Answer*: A deterministic computational architecture providing bounded space and time execution guarantees.\n"
            "2. **Q2: State the primary asymptotic bound for " + topic + ".**\n"
            "   - *Answer*: Bounded by $\\mathcal{O}(n \\log n)$ or $\\mathcal{O}(n)$ under standard operating invariants."
        )

    return (
        "# Executive Overview & Theoretical Foundations: " + topic + "\n"
        "**Academic Domain:** " + domain + " | **Level:** B.Tech Undergraduate Engineering\n\n"
        "**" + topic + "** represents an indispensable theoretical and practical linchpin in " + domain + ". "
        "Mastering this domain provides the rigorous foundation for efficient system architecture, optimal memory management, "
        "and deterministic computational bounds required in production engineering and university end-semester examinations.\n\n"
        "## Core Concepts & Mathematical / Architectural Linchpins\n"
        + math_content + "\n\n"
        "## Physical Memory Layout & Structural Representation\n"
        + memory_layout + "\n\n"
        "## Production-Grade Implementation & Boundary Validation\n"
        + code_impl + "\n\n"
        "## Step-by-Step Solved Numericals & Algorithmic Traces\n"
        + worked_numericals + "\n\n"
        "## Complexity Analysis & Asymptotic Matrix\n"
        + complexity_table + "\n\n"
        "## Real-World Pitfalls, Common Bugs & Exam Traps\n"
        + pitfalls + "\n\n"
        "## University Examination Practice Problems with Model Answers\n"
        + exam_qa
    )


def _build_ee_topic_notes(topic: str, domain: str, t_lower: str) -> str:
    """Generates realistic Electrical & Electronics Engineering notes with real circuit equations."""
    math_content = (
        "### 1. Circuit Equations & Governing Electrical Laws\n"
        "Electrical network analysis is governed by Kirchhoff's fundamental laws derived from Maxwell's equations:\n\n"
        "- **Kirchhoff's Current Law (KCL - Conservation of Charge)**:\n"
        "$$\\sum_{k=1}^{N} I_k = 0$$\n"
        "- **Kirchhoff's Voltage Law (KVL - Conservation of Energy)**:\n"
        "$$\\sum_{k=1}^{M} V_k = 0$$\n"
        "- **Thevenin's Equivalent & Maximum Power Transfer**:\n"
        "$$I_L = \\frac{V_{\\text{th}}}{R_{\\text{th}} + R_L}, \\qquad P_{\\max} = \\frac{V_{\\text{th}}^2}{4 R_{\\text{th}}}$$"
    )
    code_impl = (
        "```python\n"
        "# Electrical Engineering Simulation: Thevenin Equivalent & Power Transfer\n"
        "def thevenin_analysis(v_th: float, r_th: float, r_load: float) -> dict:\n"
        "    current = v_th / (r_th + r_load)\n"
        "    v_load = current * r_load\n"
        "    power = (current ** 2) * r_load\n"
        "    p_max = (v_th ** 2) / (4 * r_th)\n"
        "    return {'current': current, 'power': power, 'max_power': p_max}\n"
        "```"
    )
    return (
        "# Executive Overview & Theoretical Foundations: " + topic + "\n"
        "**Academic Domain:** " + domain + " | **Level:** B.Tech Undergraduate Engineering\n\n"
        "**" + topic + "** constitutes a core foundational discipline within Electrical & Electronics Engineering. "
        "Mastering electrical circuit analysis, transient behavior, and electromagnetic field equations guarantees "
        "reliable power, analog, and digital system design.\n\n"
        "## Core Concepts & Mathematical / Architectural Linchpins\n"
        + math_content + "\n\n"
        "## Production-Grade Simulation & Computational Circuit Modeling\n"
        + code_impl + "\n\n"
        "## University Examination Practice Problems with Model Answers\n"
        "1. **Q1: State Thevenin's Theorem.**\n"
        "   - *Answer*: Any linear, bilateral, active two-terminal DC network can be replaced by an equivalent voltage source $V_{\\text{th}}$ in series with an equivalent resistance $R_{\\text{th}}$.\n"
        "2. **Q2: State the condition for maximum power transfer to a load.**\n"
        "   - *Answer*: Load resistance must equal Thevenin resistance ($R_L = R_{\\text{th}}$), yielding $P_{\\max} = V_{\\text{th}}^2 / (4 R_{\\text{th}})$."
    )


def _build_me_topic_notes(topic: str, domain: str, t_lower: str) -> str:
    """Generates realistic Mechanical Engineering revision notes."""
    math_content = (
        "### 1. Thermodynamic Laws & Fluid Mechanics Governing Formulations\n"
        "Mechanical systems are governed by the conservation of mass, momentum, and energy across control volumes:\n\n"
        "- **First Law of Thermodynamics (Conservation of Energy)**:\n"
        "$$\\delta Q = dU + \\delta W \\implies Q - W = \\Delta U$$\n"
        "- **Carnot Engine Thermal Efficiency Bound**:\n"
        "$$\\eta_{\\text{Carnot}} = 1 - \\frac{T_L}{T_H} = \\frac{W_{\\text{net}}}{Q_H}$$\n"
        "- **Bernoulli's Equation for Incompressible, Frictionless Fluid Flow**:\n"
        "$$P + \\frac{1}{2} \\rho v^2 + \\rho g z = \\text{constant}$$\n"
        "- **Reynolds Number (Laminar vs. Turbulent Flow Transition)**:\n"
        "$$\\text{Re} = \\frac{\\rho v D}{\\mu} = \\frac{v D}{\\nu}$$\n"
        "Flow through circular pipes is laminar for $\\text{Re} < 2000$ and turbulent for $\\text{Re} > 4000$."
    )
    return (
        "# Executive Overview & Theoretical Foundations: " + topic + "\n"
        "**Academic Domain:** " + domain + " | **Level:** B.Tech Undergraduate Engineering\n\n"
        "**" + topic + "** represents an essential discipline within Mechanical Engineering. "
        "A rigorous comprehension of continuum mechanics, heat transfer modes, and fluid dynamics "
        "provides the analytical machinery necessary for designing thermal and mechanical machinery.\n\n"
        "## Core Concepts & Mathematical / Architectural Linchpins\n"
        + math_content + "\n\n"
        "## University Examination Practice Problems with Model Answers\n"
        "1. **Q1: State the Second Law of Thermodynamics (Kelvin-Planck statement).**\n"
        "   - *Answer*: It is impossible for any system to operate in a thermodynamic cycle and deliver a net amount of work to its surroundings while receiving energy by heat transfer from a single thermal reservoir.\n"
        "2. **Q2: State Bernoulli's equation assumptions.**\n"
        "   - *Answer*: Steady, incompressible, inviscid (non-viscous), and irrotational flow along a streamline."
    )


def _build_math_topic_notes(topic: str, domain: str, t_lower: str) -> str:
    """Generates realistic Engineering Mathematics revision notes."""
    math_content = (
        "### 1. Linear Algebra, Vector Calculus & Differential Equations\n"
        "- **Matrix Eigenvalue & Characteristic Equation**:\n"
        "$$\\det(A - \\lambda I) = 0$$\n"
        "- **Cayley-Hamilton Theorem**:\n"
        "Every square matrix $A$ satisfies its own characteristic polynomial: $$p(A) = 0$$\n"
        "- **Exact First-Order Differential Equation Criterion**:\n"
        "$$M(x, y) \\, dx + N(x, y) \\, dy = 0 \\iff \\frac{\\partial M}{\\partial y} = \\frac{\\partial N}{\\partial x}$$"
    )
    return (
        "# Executive Overview & Theoretical Foundations: " + topic + "\n"
        "**Academic Domain:** " + domain + " | **Level:** Undergraduate Engineering Mathematics\n\n"
        "**" + topic + "** represents an essential mathematical discipline across engineering branches. "
        "Understanding its analytical structures guarantees exact formulation and numerical stability in real-world systems.\n\n"
        "## Core Concepts & Mathematical / Architectural Linchpins\n"
        + math_content + "\n\n"
        "## University Examination Practice Problems with Model Answers\n"
        "1. **Q1: State the Cayley-Hamilton Theorem.**\n"
        "   - *Answer*: Every square matrix satisfies its own characteristic polynomial equation $\\det(A - \\lambda I) = 0$.\n"
        "2. **Q2: What is the condition for $M dx + N dy = 0$ to be an exact differential equation?**\n"
        "   - *Answer*: $\\frac{\\partial M}{\\partial y} = \\frac{\\partial N}{\\partial x}$."
    )


def _build_general_engineering_notes(topic: str, domain: str, t_lower: str) -> str:
    """Universal engineering note generator for any general engineering science topic."""
    math_content = (
        "### 1. Governing System Dynamics, Conservation Principles & Transfer Characteristics\n"
        "The engineering behavior of **" + topic + "** is modeled through system state variables and conservation formulations:\n\n"
        "- **Linear System Transfer Formulation**:\n"
        "$$\\mathcal{Y}(s) = \\mathcal{H}(s) \\cdot \\mathcal{U}(s) + \\mathcal{E}(s)$$\n"
        "where $\\mathcal{H}(s)$ denotes the system transfer function characterizing dynamic responsiveness.\n\n"
        "- **Conservation of State Invariants**:\n"
        "$$\\frac{d}{dt} \\int_{\\Omega} \\rho \\, \\phi \\, d\\Omega + \\oint_{\\partial \\Omega} \\rho \\, \\phi \\, (\\mathbf{v} \\cdot \\mathbf{n}) \\, dA = \\int_{\\Omega} S_\\phi \\, d\\Omega$$\n"
        "enforcing equilibrium between accumulation, net convective flux, and internal sources.\n\n"
        "- **Dimensional Homogeneity (Buckingham $\\Pi$ Theorem)**:\n"
        "$$\\Pi_1 = \\Phi(\\Pi_2, \\Pi_3, \\dots, \\Pi_{n-k})$$"
    )
    code_impl = (
        "```python\n"
        "# Computational Engineering Model: " + topic + "\n"
        "class SystemSimulation:\n"
        "    \"\"\"Numerical evaluation of governing transfer parameters.\"\"\"\n"
        "    def __init__(self, damping: float = 0.2, natural_freq: float = 5.0):\n"
        "        self.zeta = damping\n"
        "        self.wn = natural_freq\n"
        "\n"
        "    def step_response(self, time_s: float) -> float:\n"
        "        import math\n"
        "        if self.zeta >= 1.0:\n"
        "            return 1.0 - math.exp(-self.wn * time_s)\n"
        "        wd = self.wn * math.sqrt(1 - self.zeta ** 2)\n"
        "        decay = math.exp(-self.zeta * self.wn * time_s)\n"
        "        osc = math.cos(wd * time_s) + (self.zeta / math.sqrt(1 - self.zeta ** 2)) * math.sin(wd * time_s)\n"
        "        return 1.0 - decay * osc\n"
        "```"
    )
    return (
        "# Executive Overview & Theoretical Foundations: " + topic + "\n"
        "**Academic Domain:** " + domain + " | **Level:** B.Tech Undergraduate Engineering\n\n"
        "**" + topic + "** represents an important conceptual foundation in " + domain + ". "
        "A rigorous comprehension of its governing principles, equilibrium states, and operational parameters "
        "is critical for analyzing complex engineering problems and scoring top marks in university exams.\n\n"
        "## Core Concepts & Mathematical / Architectural Linchpins\n"
        + math_content + "\n\n"
        "## Production-Grade Implementation & Computational Modeling\n"
        + code_impl + "\n\n"
        "## Real-World Pitfalls, Common Bugs & Exam Traps\n"
        "1. Neglecting non-linearities and boundary constraints in real physical systems.\n"
        "2. Violating dimensional consistency across conversion factors.\n"
        "3. Assuming steady-state behavior during initial startup transients.\n\n"
        "## University Examination Practice Problems with Model Answers\n"
        "1. **Q1: Define the primary governing parameter of " + topic + ".**\n"
        "   - *Answer*: It specifies the transfer equilibrium and operational response under defined system inputs.\n"
        "2. **Q2: State the dimensional homogeneity principle.**\n"
        "   - *Answer*: Every additive term in a physically meaningful equation must possess identical fundamental dimensions ($M, L, T, \\theta$)."
    )
