/**
 * OmniLearn Isolated Dual-Engine AI Note Architecture
 * 
 * Mode 1: Unit-Wise AKTU Syllabus Engine (/api/generate-unit-notes)
 *         Tailored for AKTU End-Semester Exams (Unit 1 to 5, Section A 2-marks, Section B/C 10-marks, LaTeX equations)
 * Mode 2: Topic-Wise Deep Dive Engine (/api/generate-notes)
 *         Tailored for single concept/algorithm deep-dive revision notes strictly bound to the search query with temperature 0.1
 */

(function() {
    console.log("[OmniLearn] Initializing Dual AI Note Architecture...");

    // Maintain global aliases for backward compatibility
    if (typeof window !== "undefined") {
        if (typeof executeSearch !== "undefined") window.executeSearch = executeSearch;
        if (typeof handleSearch !== "undefined") window.handleSearch = handleSearch;
        if (typeof updateDashboardUI !== "undefined") {
            window.updateDashboardUI = updateDashboardUI;
        } else if (typeof renderDashboard !== "undefined") {
            window.updateDashboardUI = renderDashboard;
        }
    }

    // Official AKTU Subject Code Dictionary
    const AKTU_CODES = {
        "Engineering Mathematics - I": "BAS103",
        "Engineering Physics": "BAS101",
        "Engineering Chemistry": "BAS102",
        "Basic Electrical Engineering": "BEE101",
        "Data Structures": "KCS301",
        "Discrete Structures & Theory of Logic": "KCS303",
        "Computer Organization & Architecture": "KCS302",
        "Operating Systems": "KCS401",
        "Database Management Systems": "KCS403",
        "Design & Analysis of Algorithms": "KCS501",
        "Compiler Design": "KCS502",
        "Software Engineering": "KCS503",
        "Computer Networks": "KCS601",
        "Web Technology": "KCS602",
        "Artificial Intelligence & Machine Learning": "KCS701",
        "Cryptography & Network Security": "KCS702",
        "Big Data Analytics": "KCS703",
        "Internet of Things": "KCS801",
        "Digital Image Processing": "KCS802",
        "Software Testing & Quality": "KCS803"
    };

    function resolveSubjectCode(subjectName) {
        if (!subjectName) return "KCS301";
        if (AKTU_CODES[subjectName]) return AKTU_CODES[subjectName];
        for (const [key, code] of Object.entries(AKTU_CODES)) {
            if (subjectName.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(subjectName.toLowerCase())) {
                return code;
            }
        }
        return "KCS" + Math.floor(100 + Math.random() * 800);
    }

    // Strips prefixes like "Study Notes:", "AKTU Revision:", etc.
    function cleanQueryString(str) {
        if (!str || typeof str !== "string") return "";
        return str.replace(/^(Study Notes:\s*|Lecture Notes:\s*|AKTU Revision:\s*|Revision Notes:\s*)/i, "").trim();
    }

    /**
     * Extracts the EXACT user search query without hardcoded defaults
     * Priorities:
     * 1. Active search input elements (#mainSearchInput, #navSearchInput)
     * 2. URL search parameters (?q=..., ?topic=..., ?query=...)
     * 3. Global active query state variables
     */
    function getExactSearchQuery() {
        // 1. Search bar inputs
        const mainInput = document.getElementById("mainSearchInput");
        if (mainInput && mainInput.value && mainInput.value.trim()) {
            return mainInput.value.trim();
        }
        const navInput = document.getElementById("navSearchInput");
        if (navInput && navInput.value && navInput.value.trim()) {
            return navInput.value.trim();
        }

        // 2. URL search parameters (e.g. ?q=array or ?topic=linked+list)
        if (typeof window !== "undefined" && window.location && window.location.search) {
            const urlParams = new URLSearchParams(window.location.search);
            const qParam = urlParams.get("q") || urlParams.get("topic") || urlParams.get("query");
            if (qParam && qParam.trim()) {
                return qParam.trim();
            }
        }

        // 3. Active search state in app
        if (window.currentQuery && window.currentQuery.trim()) {
            return window.currentQuery.trim();
        }
        if (window.currentSearchData) {
            if (window.currentSearchData.query && window.currentSearchData.query.trim()) {
                return window.currentSearchData.query.trim();
            }
            if (window.currentSearchData.title && window.currentSearchData.title.trim()) {
                return cleanQueryString(window.currentSearchData.title);
            }
        }

        // 4. Hero title fallback if present
        const titleEl = document.getElementById("summaryTopicTitle");
        if (titleEl && titleEl.textContent && titleEl.textContent.trim()) {
            return cleanQueryString(titleEl.textContent);
        }

        return "";
    }
    window.getExactSearchQuery = getExactSearchQuery;

    // In-memory cache for fast repeat access
    const topicNotesCache = new Map();
    const aktuUnitNotesCache = new Map();

    /**
     * Scoped MathJax typesetting helper
     * Safely executes typesetPromise on container element without touching other DOM nodes
     */
    function triggerMathJaxRender(container) {
        const el = container || document.getElementById("modal-markdown-content") || document.getElementById("noteDetailModal");
        if (!el) return;

        if (window.MathJax && typeof window.MathJax.typesetPromise === "function") {
            try {
                window.MathJax.typesetPromise([el]).catch(err => {
                    console.warn("[OmniLearn MathJax] Promise notice:", err);
                });
            } catch (e) {
                console.warn("[OmniLearn MathJax] Execution notice:", e);
            }
        } else if (window.renderMathFormulas) {
            window.renderMathFormulas(el);
        }
    }
    window.triggerMathJaxRender = triggerMathJaxRender;

    /**
     * Mode 2: Topic-Wise Deep Dive Note Engine
     * Dynamically binds strictly to req.topic without hardcoded defaults
     */
    async function triggerTopicNoteGeneration(topic, subject) {
        let exactTopic = cleanQueryString(topic);
        if (!exactTopic) {
            exactTopic = getExactSearchQuery();
        }
        if (!exactTopic) {
            exactTopic = "Computer Science & Engineering";
        }

        const activeSubject = subject || (window.currentSearchData && (window.currentSearchData.category || window.currentSearchData.domain)) || "";

        const modalEl = document.getElementById("noteDetailModal");
        const titleEl = document.getElementById("noteModalTitle");
        const badgeEl = document.getElementById("noteModalSubjectBadge");
        const metaEl = document.getElementById("noteModalMeta");
        const contentEl = document.getElementById("modal-markdown-content");
        const viewFileBtn = document.getElementById("viewOriginalFileBtn");

        if (modalEl) modalEl.classList.remove("hidden");
        if (titleEl) titleEl.textContent = `Study Notes: ${exactTopic}`;
        if (badgeEl) badgeEl.textContent = activeSubject || "University Engineering";
        if (metaEl) {
            metaEl.innerHTML = `<i class="fa-solid fa-brain mr-1.5 text-indigo-400"></i> OmniLearn AI Academic Engine | Deep Revision Notes & LaTeX Derivations`;
        }
        if (viewFileBtn) viewFileBtn.classList.add("hidden");

        const cacheKey = `${exactTopic.toLowerCase()}__${activeSubject.toLowerCase()}`;
        if (topicNotesCache.has(cacheKey)) {
            const cachedNotes = topicNotesCache.get(cacheKey);
            renderParsedContent(cachedNotes, exactTopic, activeSubject);
            return;
        }

        // Show modern non-blocking glassmorphic loading indicator
        if (contentEl) {
            contentEl.innerHTML = `
                <div class="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
                    <div class="w-12 h-12 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin mb-4"></div>
                    <h4 class="text-base font-bold text-slate-100 mb-1">Synthesizing Topic Revision Notes</h4>
                    <p class="text-xs text-slate-400 max-w-md">Querying OmniLearn AI for theoretical derivations, step-by-step numericals, and LaTeX equations strictly for "${exactTopic}"...</p>
                    <div class="mt-4 flex items-center space-x-2 text-[11px] text-indigo-300/80 bg-indigo-500/10 px-3 py-1.5 rounded-full border border-indigo-500/20">
                        <i class="fa-solid fa-microchip"></i>
                        <span>AI Engine Active (Temp 0.1 - Zero Hallucination Mode)</span>
                    </div>
                </div>
            `;
        }

        const payload = { topic: exactTopic, subject: activeSubject };
        console.log("[OmniLearn Mode 2] Sending exact search payload to /api/generate-notes:", payload);

        try {
            const resp = await fetch("/api/generate-notes", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                const data = await resp.json();
                const notes = data.notes || "";
                topicNotesCache.set(cacheKey, notes);
                renderParsedContent(notes, exactTopic, data.subject || activeSubject);
            } else {
                throw new Error(`Server responded with status ${resp.status}`);
            }
        } catch (err) {
            console.warn("[OmniLearn] Topic note fetch notice, using academic fallback:", err);
            const fallback = (typeof generateAcademicFallbackNotes === "function") 
                ? generateAcademicFallbackNotes(exactTopic, activeSubject) 
                : `# Executive Overview: ${exactTopic}\n\nComprehensive university study notes strictly for ${exactTopic}.`;
            renderParsedContent(fallback, exactTopic, activeSubject);
        }
    }
    window.triggerTopicNoteGeneration = triggerTopicNoteGeneration;

    /**
     * Mode 1: AKTU Unit-Wise Syllabus Engine
     * Triggered dynamically from clicked button with dataset.unit and matching syllabus topics
     */
    async function triggerAktuUnitNoteGeneration(subjectCode, subjectName, unitNumber, topics) {
        const code = subjectCode || resolveSubjectCode(subjectName);
        const name = subjectName || "Engineering Curriculum";
        const unit = parseInt(unitNumber, 10);
        if (!unit || isNaN(unit)) {
            console.error("[OmniLearn] Invalid unit number passed:", unitNumber);
            return;
        }

        const topicsList = Array.isArray(topics) ? topics : (topics ? [topics] : []);

        const modalEl = document.getElementById("noteDetailModal");
        const titleEl = document.getElementById("noteModalTitle");
        const badgeEl = document.getElementById("noteModalSubjectBadge");
        const metaEl = document.getElementById("noteModalMeta");
        const contentEl = document.getElementById("modal-markdown-content");
        const viewFileBtn = document.getElementById("viewOriginalFileBtn");

        if (modalEl) modalEl.classList.remove("hidden");
        if (titleEl) titleEl.textContent = `${code}: Unit ${unit} - ${name}`;
        if (badgeEl) badgeEl.textContent = `AKTU B.Tech Unit ${unit}`;
        if (metaEl) {
            metaEl.innerHTML = `<i class="fa-solid fa-graduation-cap mr-1.5 text-indigo-400"></i> Official AKTU University Exam Engine | Section A (2-Mark) & Section B/C (10-Mark) Solutions`;
        }
        if (viewFileBtn) viewFileBtn.classList.add("hidden");

        // Bypass in-memory stale cache to ensure hard refresh and fresh generation
        const cacheKey = `${code}__unit_${unit}`;

        // Show glassmorphic loading spinner
        if (contentEl) {
            contentEl.innerHTML = `
                <div class="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
                    <div class="w-12 h-12 rounded-full border-2 border-emerald-500/30 border-t-emerald-500 animate-spin mb-4"></div>
                    <h4 class="text-base font-bold text-slate-100 mb-1">Compiling AKTU Unit ${unit} Exam Notes</h4>
                    <p class="text-xs text-slate-400 max-w-md">Synthesizing Section A 2-mark high frequency questions, Section B/C 10-mark derivations, and solved numericals for ${code} (${name})...</p>
                    <div class="mt-4 flex items-center space-x-2 text-[11px] text-emerald-300/80 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
                        <i class="fa-solid fa-file-lines"></i>
                        <span>AKTU End-Semester Pattern Active (Unit ${unit})</span>
                    </div>
                </div>
            `;
        }

        const payload = {
            subject_code: code,
            subject_name: name,
            unit_number: unit,
            unit: unit,
            aktu_syllabus_topics: topicsList
        };
        console.log("[OmniLearn Mode 1] Dispatching dynamic unit payload to /api/generate-unit-notes:", payload);

        try {
            const resp = await fetch(`/api/generate-unit-notes?t=${Date.now()}`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache"
                },
                cache: "no-store",
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                const data = await resp.json();
                const notes = data.unit_notes || data.notes || "";
                renderParsedContent(notes, `${code} Unit ${unit}`, name);
            } else {
                throw new Error(`Server responded with status ${resp.status}`);
            }
        } catch (err) {
            console.warn("[OmniLearn] AKTU unit note fetch notice, using fallback:", err);
            const fallback = (typeof _generateFallbackUnitNotes === "function")
                ? _generateFallbackUnitNotes(code, name, unit, topicsList)
                : `### AKTU End-Semester Examination Notes\n- Course Code: ${code}\n- Course Name: ${name}\n- Unit: ${unit}\n\n### Specific Notes on Important Topics\nOfficial revision notes for Unit ${unit}.`;
            renderParsedContent(fallback, `${code} Unit ${unit}`, name);
        }
    }
    window.triggerAktuUnitNoteGeneration = triggerAktuUnitNoteGeneration;

    /**
     * Injects formatted Markdown and triggers MathJax LaTeX typesetting
     */
    function renderParsedContent(markdownText, title, subject) {
        const contentEl = document.getElementById("modal-markdown-content");
        if (!contentEl) return;

        let cleanText = markdownText;
        if (typeof sanitizeStudyNotesContent === "function") {
            cleanText = sanitizeStudyNotesContent(markdownText);
        }

        let html = "";
        if (typeof marked !== "undefined" && typeof marked.parse === "function") {
            try {
                marked.setOptions({ gfm: true, breaks: true });
                html = marked.parse(cleanText);
            } catch (e) {
                console.error("[OmniLearn] Marked.js parse error:", e);
                html = `<pre class="whitespace-pre-wrap font-sans">${cleanText}</pre>`;
            }
        } else {
            html = `<div class="whitespace-pre-wrap font-sans text-sm">${cleanText}</div>`;
        }

        contentEl.innerHTML = html;

        // Update active note reference for Download TXT and Export PDF
        if (typeof window !== "undefined") {
            window.currentNote = {
                title: title,
                subject: subject,
                ocr_text: cleanText,
                uploaded_by: "OmniLearn AI Academic Engine"
            };
        }

        // Calculate and update reading time badge
        const words = cleanText.trim().split(/\s+/).length;
        const readTime = Math.max(1, Math.ceil(words / 200));
        const timeEl = document.getElementById("noteReadingTime");
        if (timeEl) {
            timeEl.innerHTML = `<i class="fa-regular fa-clock mr-1 text-indigo-400"></i> ~${readTime} min read`;
        }

        // Trigger scoped MathJax typesetting on this element
        triggerMathJaxRender(contentEl);
    }

    /**
     * Enhance viewSubjectUnits to inject dataset.unit buttons with exact syllabus topics
     */
    function enhanceYearSubjectsView() {
        const originalViewSubjectUnits = window.viewSubjectUnits;

        window.viewSubjectUnits = function(year, subjectIndex) {
            // Call original renderer first to populate structure safely
            if (typeof originalViewSubjectUnits === "function") {
                originalViewSubjectUnits(year, subjectIndex);
            }

            // Look up subject details
            const yearData = (typeof YEAR_SUBJECTS !== "undefined") ? YEAR_SUBJECTS[year] : null;
            if (!yearData) return;
            const subject = yearData.subjects ? yearData.subjects[subjectIndex] : null;
            if (!subject) return;

            const code = resolveSubjectCode(subject.name);
            const list = document.getElementById("yearSubjectsList");
            if (!list) return;

            // Prepend a sleek 5-Unit Quick Selector Bar with dynamic dataset.unit attributes
            const navBarId = "aktuUnitSelectorBar";
            let navBar = document.getElementById(navBarId);
            if (!navBar) {
                navBar = document.createElement("div");
                navBar.id = navBarId;
                navBar.className = "col-span-full mb-3 p-3 rounded-xl bg-slate-800/60 border border-slate-700/60 backdrop-blur-md shadow-md";
                
                let unitButtonsHtml = "";
                for (let u = 1; u <= 5; u++) {
                    const unitObj = (subject.units && subject.units[u - 1]) ? subject.units[u - 1] : null;
                    const unitTopics = unitObj ? [unitObj.name, unitObj.chapters] : [`Unit ${u} Core Concepts`];
                    const encodedTopics = encodeURIComponent(JSON.stringify(unitTopics));

                    unitButtonsHtml += `
                        <button type="button"
                                data-unit="${u}" 
                                data-subject-code="${code}" 
                                data-subject-name="${subject.name}" 
                                data-topics="${encodedTopics}"
                                class="aktu-unit-btn aktu-unit-quick-btn px-3 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 bg-indigo-600/30 hover:bg-indigo-600/80 text-indigo-200 hover:text-white border border-indigo-500/40 hover:border-indigo-400 shadow-xs flex items-center space-x-1.5 cursor-pointer">
                            <i class="fa-solid fa-bolt text-[10px] text-amber-300"></i>
                            <span>Unit ${u} Exam Notes</span>
                        </button>
                    `;
                }

                navBar.innerHTML = `
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div class="flex items-center space-x-2">
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 tracking-wider uppercase">${code}</span>
                            <span class="text-xs font-semibold text-slate-200">AKTU 5-Unit Dual AI Engine</span>
                        </div>
                        <div class="flex flex-wrap items-center gap-1.5">
                            ${unitButtonsHtml}
                        </div>
                    </div>
                `;

                if (list.children.length > 0) {
                    list.insertBefore(navBar, list.children[1] || list.children[0]);
                } else {
                    list.appendChild(navBar);
                }
            }

            // Enhance each unit card with dynamic dataset.unit attributes and matching topics
            const allUnitCards = list.querySelectorAll(".rounded-xl");
            allUnitCards.forEach((card) => {
                if (card.id === navBarId) return;

                // Extract actual unit number from the badge inside the card
                let unitNum = null;
                const badge = card.querySelector(".glass-badge");
                if (badge && badge.textContent) {
                    const match = badge.textContent.match(/Unit\s*(\d+)/i);
                    if (match) unitNum = parseInt(match[1], 10);
                }
                if (!unitNum) return;

                const actionsContainer = card.querySelector(".flex-shrink-0");
                if (actionsContainer) {
                    // Completely remove static "Download Notes" buttons/links
                    const oldDownloadBtns = actionsContainer.querySelectorAll("a, button");
                    oldDownloadBtns.forEach(btnEl => {
                        if (btnEl.textContent && btnEl.textContent.includes("Download Notes")) {
                            btnEl.remove();
                        }
                    });

                    // Retain ONLY the primary trigger button (AI Exam Notes)
                    if (!card.querySelector(".ai-unit-notes-btn")) {
                        const unitObj = (subject.units && subject.units[unitNum - 1]) ? subject.units[unitNum - 1] : null;
                        const topics = unitObj ? [unitObj.name, unitObj.chapters] : [`Unit ${unitNum} Syllabus Topics`];
                        const encodedTopics = encodeURIComponent(JSON.stringify(topics));

                        const btn = document.createElement("button");
                        btn.type = "button";
                        btn.setAttribute("data-unit", String(unitNum));
                        btn.setAttribute("data-subject-code", code);
                        btn.setAttribute("data-subject-name", subject.name);
                        btn.setAttribute("data-topics", encodedTopics);
                        btn.className = "aktu-unit-btn ai-unit-notes-btn inline-flex items-center justify-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 transition shadow-xs cursor-pointer";
                        btn.innerHTML = `<i class="fa-solid fa-brain text-[11px]"></i><span>Unit ${unitNum} Exam Notes</span>`;
                        
                        btn.onclick = function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            const uNum = parseInt(this.dataset.unit || this.getAttribute("data-unit"), 10);
                            const c = this.dataset.subjectCode || code;
                            const n = this.dataset.subjectName || subject.name;
                            let t = [];
                            try {
                                t = JSON.parse(decodeURIComponent(this.dataset.topics));
                            } catch (err) {
                                t = [this.dataset.topics];
                            }
                            triggerAktuUnitNoteGeneration(c, n, uNum, t);
                        };
                        
                        actionsContainer.appendChild(btn);
                    }
                }
            });

            // Also attach explicit onclick to Quick Selector Bar buttons
            if (navBar) {
                navBar.querySelectorAll("button[data-unit]").forEach(qBtn => {
                    qBtn.onclick = function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        const uNum = parseInt(this.dataset.unit || this.getAttribute("data-unit"), 10);
                        const c = this.dataset.subjectCode || code;
                        const n = this.dataset.subjectName || subject.name;
                        let t = [];
                        try {
                            t = JSON.parse(decodeURIComponent(this.dataset.topics));
                        } catch (err) {
                            t = [this.dataset.topics];
                        }
                        triggerAktuUnitNoteGeneration(c, n, uNum, t);
                    };
                });
            }
        };
    }

    /**
     * Download current study notes as plain text (AKTU_Notes.txt) via Blob URL creation
     */
    function downloadNotesAsTXT() {
        const noteArea = document.querySelector('#noteContentArea') || document.querySelector('#modal-markdown-content') || document.querySelector('.notes-reader-document');
        let text = noteArea ? (noteArea.innerText || noteArea.textContent || '') : '';
        if (!text.trim() && window.currentNote && window.currentNote.ocr_text) {
            text = window.currentNote.ocr_text;
        }
        if (!text.trim()) {
            alert("No note content found to download.");
            return;
        }
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = 'AKTU_Notes.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
    }

    /**
     * Export current study notes as PDF via window.open() print stream
     */
    function exportNotesAsPDF() {
        const noteArea = document.querySelector('#noteContentArea') || document.querySelector('#modal-markdown-content') || document.querySelector('.notes-reader-document');
        if (!noteArea) {
            alert("No note content available to export as PDF.");
            return;
        }

        const titleEl = document.getElementById("noteModalTitle");
        const docTitle = titleEl ? titleEl.textContent : "AKTU Study Notes";
        const contentHtml = noteArea.innerHTML;

        const printWindow = window.open('', '_blank', 'width=900,height=800');
        if (!printWindow) {
            alert("Please allow popups in your browser to export notes as PDF.");
            return;
        }

        printWindow.document.open();
        printWindow.document.write(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>${docTitle}</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
                <style>
                    @page { size: A4 portrait; margin: 15mm; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                        color: #0f172a;
                        background: #ffffff;
                        line-height: 1.6;
                        padding: 24px;
                        margin: 0;
                    }
                    h1, h2, h3, h4, h5, h6 { color: #1e293b; font-weight: 700; margin-top: 1.2em; margin-bottom: 0.5em; }
                    h1 { font-size: 1.6rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }
                    h2 { font-size: 1.3rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
                    h3 { font-size: 1.15rem; }
                    p { margin-bottom: 0.8em; }
                    pre { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; overflow-x: auto; font-size: 0.85rem; }
                    code { font-family: monospace; background: #f1f5f9; padding: 2px 4px; border-radius: 4px; font-size: 0.9em; }
                    blockquote { border-left: 4px solid #6366f1; padding-left: 12px; color: #475569; margin: 12px 0; font-style: italic; }
                    table { width: 100%; border-collapse: collapse; margin: 12px 0; }
                    th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; font-size: 0.9rem; }
                    th { background-color: #f8fafc; font-weight: 600; }
                    .katex-display { margin: 1em 0; overflow-x: auto; }
                    @media print {
                        body { padding: 0; }
                    }
                </style>
            </head>
            <body>
                <div class="print-container">
                    ${contentHtml}
                </div>
                <script>
                    window.onload = function() {
                        window.focus();
                        window.print();
                    };
                </script>
            </body>
            </html>
        `);
        printWindow.document.close();
    }

    // Attach export functions to window and legacy names
    if (typeof window !== "undefined") {
        window.downloadNotesAsTXT = downloadNotesAsTXT;
        window.exportNotesAsPDF = exportNotesAsPDF;
        window.handleDownloadTxt = downloadNotesAsTXT;
        window.handleExportPdf = exportNotesAsPDF;
        window.downloadCurrentNote = function(format) {
            if (format === 'pdf') {
                exportNotesAsPDF();
            } else {
                downloadNotesAsTXT();
            }
        };
    }

    /**
     * Intercept legacy openStudyNotesModal to route through triggerTopicNoteGeneration
     */
    function interceptLegacyModalCalls() {
        if (typeof window !== "undefined") {
            const originalModalFn = window.openStudyNotesModal;
            window.openStudyNotesModal = function(note) {
                const exactQuery = getExactSearchQuery();
                let topic = exactQuery;
                if (!topic && note && note.title) {
                    topic = cleanQueryString(note.title);
                }
                const subject = (note && note.subject) ? note.subject : "";
                triggerTopicNoteGeneration(topic, subject);
            };
        }
    }

    /**
     * Attach global event delegation for "View File" buttons, note cards, Unit buttons, and Modal Export buttons
     */
    function attachEventListeners() {
        // Direct event listeners on modal action buttons
        const dlTxtBtn = document.getElementById("downloadTxtBtn");
        if (dlTxtBtn) {
            dlTxtBtn.onclick = downloadNotesAsTXT;
        }

        const expPdfBtn = document.getElementById("exportPdfBtn");
        if (expPdfBtn) {
            expPdfBtn.onclick = exportNotesAsPDF;
        }

        document.addEventListener("click", function(e) {
            // Check if clicked element or parent is Download TXT
            const clickedDlTxt = e.target.closest("#downloadTxtBtn, #downloadNoteBtn");
            if (clickedDlTxt) {
                e.preventDefault();
                e.stopPropagation();
                downloadNotesAsTXT();
                return;
            }

            // Check if clicked element or parent is Export PDF
            const clickedExpPdf = e.target.closest("#exportPdfBtn, #printNotePdfBtn");
            if (clickedExpPdf) {
                e.preventDefault();
                e.stopPropagation();
                exportNotesAsPDF();
                return;
            }

            // Check if clicked element or parent is an AKTU unit button ([data-unit])
            const clickedUnitBtn = e.target.closest("[data-unit]");
            if (clickedUnitBtn && (clickedUnitBtn.classList.contains("aktu-unit-btn") || clickedUnitBtn.classList.contains("aktu-unit-quick-btn") || clickedUnitBtn.classList.contains("ai-unit-notes-btn") || clickedUnitBtn.textContent.includes("Exam Notes"))) {
                e.preventDefault();
                e.stopPropagation();

                // Dynamically grab unit number from button clicked (never hardcoded)
                const unitNumber = parseInt(clickedUnitBtn.dataset.unit || clickedUnitBtn.getAttribute("data-unit"), 10);
                const code = clickedUnitBtn.dataset.subjectCode || resolveSubjectCode(clickedUnitBtn.dataset.subjectName);
                const name = clickedUnitBtn.dataset.subjectName || "AKTU Curriculum";
                let topics = [];
                try {
                    if (clickedUnitBtn.dataset.topics) {
                        topics = JSON.parse(decodeURIComponent(clickedUnitBtn.dataset.topics));
                    }
                } catch (err) {
                    topics = clickedUnitBtn.dataset.topics ? [clickedUnitBtn.dataset.topics] : [];
                }

                console.log(`[OmniLearn Dynamic Unit Handler] Clicked Unit ${unitNumber} for ${code} (${name}), Topics:`, topics);
                triggerAktuUnitNoteGeneration(code, name, unitNumber, topics);
                return;
            }

            // Check if clicked element or parent is a .view-file-btn
            const viewFileBtn = e.target.closest(".view-file-btn");
            if (viewFileBtn) {
                e.preventDefault();
                e.stopPropagation();

                // Extract exact query without defaults
                let exactTopic = getExactSearchQuery();
                const noteCard = viewFileBtn.closest(".note-card") || viewFileBtn.closest("[data-topic]") || viewFileBtn.closest(".bg-white");
                if (!exactTopic && noteCard) {
                    const cardTitleEl = noteCard.querySelector("h4");
                    if (cardTitleEl && cardTitleEl.textContent) {
                        exactTopic = cleanQueryString(cardTitleEl.textContent);
                    }
                }

                const activeSubject = (window.currentSearchData && (window.currentSearchData.category || window.currentSearchData.domain)) || "";
                triggerTopicNoteGeneration(exactTopic, activeSubject);
                return;
            }

            // Check if clicked element or parent is the overview card expand notes button
            const expandNotesBtn = e.target.closest("#toggleDetailBtn");
            if (expandNotesBtn) {
                setTimeout(() => triggerMathJaxRender(), 200);
            }
        }, true);
    }

    // Initialize once DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function() {
            enhanceYearSubjectsView();
            interceptLegacyModalCalls();
            attachEventListeners();
            if (document.getElementById('downloadTxtBtn')) {
                document.getElementById('downloadTxtBtn').onclick = downloadNotesAsTXT;
            }
            if (document.getElementById('exportPdfBtn')) {
                document.getElementById('exportPdfBtn').onclick = exportNotesAsPDF;
            }
        });
    } else {
        enhanceYearSubjectsView();
        interceptLegacyModalCalls();
        attachEventListeners();
        if (document.getElementById('downloadTxtBtn')) {
            document.getElementById('downloadTxtBtn').onclick = downloadNotesAsTXT;
        }
        if (document.getElementById('exportPdfBtn')) {
            document.getElementById('exportPdfBtn').onclick = exportNotesAsPDF;
        }
    }

    console.log("[OmniLearn] Dual AI Note Architecture ready.");
})();


// A. CLEAN SEARCH SCOPE ERROR HANDLING
async function searchTopic(query) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (!response.ok) {
            showAcademicErrorCard(data.detail || "This topic is outside your academic syllabus. Only B.Tech & Engineering topics are allowed here.");
            return;
        }

        renderSearchResults(data);
    } catch (err) {
        console.error("Search Error:", err);
    }
}

function showAcademicErrorCard(message) {
    const container = document.querySelector('#resultsContainer') || document.body;
    container.innerHTML = `
        <div style="max-width: 600px; margin: 40px auto; padding: 28px; background: #1e1b4b; border: 1px solid #4338ca; border-radius: 12px; text-align: center; color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
            <div style="font-size: 48px; margin-bottom: 12px;">⚠️</div>
            <h3 style="font-size: 20px; font-weight: bold; margin-bottom: 8px;">Academic Scope Exceeded</h3>
            <p style="color: #c7d2fe; font-size: 14px; line-height: 1.5;">${message}</p>
        </div>
    `;
}

// B. DYNAMIC UNIT NOTES FETCHING
async function fetchUnitNotes(subjectCode, subjectName, unitNumber, topics) {
    try {
        const response = await fetch('/api/generate-unit-notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject_code: subjectCode,
                subject_name: subjectName,
                unit_number: parseInt(unitNumber),
                aktu_syllabus_topics: topics
            })
        });
        const data = await response.json();
        
        if (response.ok) {
            openNotesModal(data.unit_notes);
        }
    } catch (err) {
        console.error("Error fetching unit notes:", err);
    }
}

// C. WORKING TXT & PDF EXPORT HANDLERS
function downloadNotesAsTXT() {
    const content = document.querySelector('.modal-body') || document.querySelector('#noteContentArea');
    if (!content) return alert("No note content found to download!");

    const blob = new Blob([content.innerText], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "AKTU_Study_Notes.txt";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function exportNotesAsPDF() {
    const content = document.querySelector('.modal-body') || document.querySelector('#noteContentArea');
    if (!content) return alert("No note content found to export!");

    const printWindow = window.open('', '', 'height=750,width=950');
    printWindow.document.write('<html><head><title>AKTU Revision Notes</title>');
    printWindow.document.write('<style>body{font-family:Arial,sans-serif;padding:30px;line-height:1.6;color:#111;} pre,code{background:#f4f4f4;padding:8px;border-radius:4px;}</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write(content.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
    
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
}

// Attach export event listeners on modal load
function attachModalExportListeners() {
    const txtBtn = document.getElementById('downloadTxtBtn');
    const pdfBtn = document.getElementById('exportPdfBtn');
    
    if (txtBtn) txtBtn.onclick = downloadNotesAsTXT;
    if (pdfBtn) pdfBtn.onclick = exportNotesAsPDF;
}
async function fetchUnitNotesStream(subjectCode, subjectName, unitNumber, topicsArray) {
  const modalBody = document.querySelector('.modal-body') || document.querySelector('#noteContentArea');
  if (!modalBody) return;

  modalBody.innerHTML = '<div style="color: #818cf8; font-weight: bold;">Generating notes in real-time...</div><div id="streamTarget"></div>';
  const target = document.getElementById('streamTarget');

  try {
    const response = await fetch('/api/generate-unit-notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subject_code: subjectCode,
        subject_name: subjectName,
        unit_number: parseInt(unitNumber),
        aktu_syllabus_topics: topicsArray
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullMarkdown = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Append incoming text chunk instantly
      fullMarkdown += decoder.decode(value, { stream: true });
      target.innerHTML = parseMarkdownToHTML(fullMarkdown);
    }

    // Trigger MathJax formula rendering once complete
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([target]);
    }

  } catch (err) {
    console.error("Streaming error:", err);
    modalBody.innerHTML = '<div style="color: #ef4444;">Failed to generate notes. Please try again.</div>';
  }
}