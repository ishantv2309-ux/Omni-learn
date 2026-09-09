// --- State Variables ---
let currentQuery = "";
let currentSearchData = null;
let bookmarks = [];
let chartInstance = null;
let currentNote = null;
let studyNotes = ""; // Current active query generated study notes
let completedRoadmapSteps = {}; // Map of query -> Set of step indices
let isSearching = false;
const searchResultCache = new Map(); // Client-side instant query cache

// --- Init on Page Load & URL Routing ("useEffect" Hook equivalent) ---
document.addEventListener("DOMContentLoaded", () => {
    fetchBookmarks();
    initUrlRouting();
    initSearchInputListeners();
    // Guarantee all form submissions prevent default page reloads
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            handleSearch(e);
        });
    });
});

function initSearchInputListeners() {
    const mainInput = document.getElementById("mainSearchInput");
    const navInput = document.getElementById("navSearchInput");
    [mainInput, navInput].forEach(input => {
        if (input) {
            input.addEventListener("keydown", (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    handleSearch(e, input.value);
                }
            });
        }
    });

    // Global Escape key listener to close modals
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeNoteModal();
            closeUploadModal();
            const settingsModal = document.getElementById("settingsModal");
            if (settingsModal) settingsModal.classList.add("hidden");
        }
    });

    // Delegated click listener for any .view-file-btn
    document.addEventListener("click", (e) => {
        const btn = e.target.closest(".view-file-btn");
        if (btn) {
            e.preventDefault();
            const modal = document.getElementById("noteDetailModal");
            if (modal && modal.classList.contains("hidden")) {
                openStudyNotesModal();
            }
        }
    });
}

// Listens to browser navigation (Back / Forward) and initial URL params
function initUrlRouting() {
    window.addEventListener("popstate", (event) => {
        const urlParams = new URLSearchParams(window.location.search);
        const queryFromUrl = urlParams.get("q") || urlParams.get("query") || urlParams.get("topic");
        if (queryFromUrl && queryFromUrl.trim()) {
            executeSearch(queryFromUrl.trim(), false);
        } else {
            resetSearch(false);
        }
    });

    // Handle cold page load with query parameter in URL (e.g. ?q=Dijkstra or ?query=Newton)
    const initialParams = new URLSearchParams(window.location.search);
    const initialQuery = initialParams.get("q") || initialParams.get("query") || initialParams.get("topic");
    if (initialQuery && initialQuery.trim()) {
        executeSearch(initialQuery.trim(), false);
    }
}

function setCardsLoadingState(query) {
    // Reveal dashboard screen immediately with skeleton UI on all cards
    showScreen("dashboardScreen");
    const navSearchContainer = document.getElementById("navSearchContainer");
    if (navSearchContainer) navSearchContainer.classList.remove("hidden");

    // Title & Badges
    const titleEl = document.getElementById("summaryTopicTitle");
    if (titleEl) titleEl.textContent = query;

    const domainBadge = document.getElementById("summaryDomainBadge");
    if (domainBadge) domainBadge.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1 text-indigo-500"></i> Analyzing Topic...';

    // Summary Skeleton
    const summaryContainer = document.getElementById("summaryText");
    if (summaryContainer) {
        summaryContainer.innerHTML = `
            <div class="animate-pulse space-y-2.5 my-2">
                <div class="h-4 bg-slate-200 rounded w-11/12"></div>
                <div class="h-4 bg-slate-200 rounded w-full"></div>
                <div class="h-4 bg-slate-200 rounded w-4/5"></div>
                <div class="h-4 bg-slate-200 rounded w-2/3"></div>
            </div>`;
    }

    // Reset expandable breakdown
    const detailedContainer = document.getElementById("detailedBreakdownContainer");
    if (detailedContainer) detailedContainer.classList.add("hidden");

    // Difficulty Skeleton
    const diffNum = document.getElementById("difficultyNumber");
    if (diffNum) diffNum.innerHTML = '<span class="animate-pulse text-slate-300">--</span>';
    const diffLevel = document.getElementById("difficultyLevelBadge");
    if (diffLevel) {
        diffLevel.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-slate-200 text-slate-600 animate-pulse";
        diffLevel.textContent = "Evaluating...";
    }
    const diffBar = document.getElementById("difficultyBar");
    if (diffBar) {
        diffBar.className = "h-3 rounded-full bg-slate-200 animate-pulse";
        diffBar.style.width = "25%";
    }
    const diffVerdict = document.getElementById("difficultyVerdict");
    if (diffVerdict) {
        diffVerdict.innerHTML = '<div class="animate-pulse h-3.5 bg-slate-200 rounded w-5/6 mt-1"></div>';
    }

    // Careers Skeleton
    const careersCard = document.getElementById("careersContainerCard");
    if (careersCard) careersCard.classList.remove("hidden");
    const careersContainer = document.getElementById("careersContainer");
    if (careersContainer) {
        careersContainer.innerHTML = `
            <div class="animate-pulse space-y-2.5">
                <div class="h-12 bg-slate-100 rounded-lg"></div>
                <div class="h-12 bg-slate-100 rounded-lg"></div>
            </div>`;
    }

    // Video Container Skeleton
    const videoContainer = document.getElementById("videoContainer");
    if (videoContainer) {
        videoContainer.innerHTML = `
            <div class="space-y-3 animate-pulse">
                <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <div class="w-full sm:w-44 h-24 bg-slate-200 rounded-lg shrink-0"></div>
                    <div class="flex-1 space-y-2 py-1">
                        <div class="h-4 bg-slate-200 rounded w-3/4"></div>
                        <div class="h-3 bg-slate-200 rounded w-1/2"></div>
                    </div>
                </div>
                <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <div class="w-full sm:w-44 h-24 bg-slate-200 rounded-lg shrink-0"></div>
                    <div class="flex-1 space-y-2 py-1">
                        <div class="h-4 bg-slate-200 rounded w-3/4"></div>
                        <div class="h-3 bg-slate-200 rounded w-1/2"></div>
                    </div>
                </div>
            </div>`;
    }

    // Web Resources Skeleton
    const resContainer = document.getElementById("resourcesContainer");
    if (resContainer) {
        resContainer.innerHTML = `
            <div class="animate-pulse space-y-2">
                <div class="h-12 bg-slate-50 rounded-lg border border-slate-100"></div>
                <div class="h-12 bg-slate-50 rounded-lg border border-slate-100"></div>
            </div>`;
    }

    // Fun Fact / Did You Know Skeleton
    const funFact = document.getElementById("funFactText");
    if (funFact) {
        funFact.innerHTML = '<div class="animate-pulse h-4 bg-amber-200/70 rounded w-4/5 my-1"></div>';
    }

    // Exam Frequency Subtitle
    const chartSub = document.getElementById("chartFrequencySubtitle");
    if (chartSub) {
        chartSub.textContent = `Analyzing examination trends (2021–2025) for "${query}"...`;
    }

    // Notes Skeleton
    const notesList = document.getElementById("notesList");
    if (notesList) {
        notesList.innerHTML = `
            <div class="animate-pulse space-y-2">
                <div class="h-10 bg-slate-100 rounded-lg"></div>
                <div class="h-10 bg-slate-100 rounded-lg"></div>
            </div>`;
    }

    // Roadmap Skeleton
    const roadmapTimeline = document.getElementById("roadmapTimeline");
    if (roadmapTimeline) {
        roadmapTimeline.innerHTML = `
            <div class="animate-pulse space-y-3">
                <div class="h-12 bg-slate-100 rounded-lg"></div>
                <div class="h-12 bg-slate-100 rounded-lg"></div>
                <div class="h-12 bg-slate-100 rounded-lg"></div>
            </div>`;
    }

    // If note detail modal is open during a new search, show clean skeleton loader
    const noteModal = document.getElementById("noteDetailModal");
    if (noteModal && !noteModal.classList.contains("hidden")) {
        showNoteModalLoadingSkeleton(query);
    }
}

// --- Central Reactive Search Controller ---
async function executeSearch(targetQuery, updateHistory = true) {
    const query = (targetQuery || "").trim();
    if (!query) return;

    console.log("Executing search for:", query);

    // Prevent re-triggering identical in-flight searches
    if (isSearching && query === currentQuery) return;
    isSearching = true;
    currentQuery = query;

    // Explicitly flush and invalidate stale/cached notes from prior searches
    studyNotes = "";
    currentNote = null;
    try {
        localStorage.removeItem("omni_active_note");
        localStorage.removeItem("omni_active_topic");
        sessionStorage.removeItem("omni_study_notes");
    } catch (e) {}

    // 1. Synchronize all search input elements across the page instantly
    const mainInput = document.getElementById("mainSearchInput");
    const navInput = document.getElementById("navSearchInput");
    const noteInput = document.getElementById("noteSearchInput");

    if (mainInput) mainInput.value = query;
    if (navInput) navInput.value = query;
    if (noteInput) {
        noteInput.value = "";
        noteInput.placeholder = `Search inside notes (OCR)...`;
    }

    // 2. Collapse and reset detailed notes container
    const detailedContainer = document.getElementById("detailedBreakdownContainer");
    if (detailedContainer) detailedContainer.classList.add("hidden");
    const btnText = document.getElementById("toggleDetailBtnText");
    const btnIcon = document.getElementById("toggleDetailBtnIcon");
    if (btnText) btnText.textContent = "Expand In-Depth Academic Notes";
    if (btnIcon) btnIcon.className = "fa-solid fa-chevron-down text-[10px] text-indigo-500 transition-transform duration-300 ml-1";

    // 3. Synchronize URL query parameter and browser document title
    if (updateHistory) {
        const newUrl = `${window.location.pathname}?q=${encodeURIComponent(query)}`;
        window.history.pushState({ query }, "", newUrl);
    }
    document.title = `${query} — OmniLearn Academic Hub`;

    const cacheKey = query.toLowerCase();
    let hasInstantRendered = false;

    // 4. Check client-side instant cache for zero-latency rendering
    let cachedData = searchResultCache.get(cacheKey);
    if (!cachedData) {
        try {
            const rawStored = sessionStorage.getItem("omni_cache_" + cacheKey);
            if (rawStored) {
                cachedData = JSON.parse(rawStored);
                searchResultCache.set(cacheKey, cachedData);
            }
        } catch (_) {}
    }

    if (cachedData && cachedData.summary && cachedData.difficulty_score !== undefined) {
        currentSearchData = cachedData;
        showScreen("dashboardScreen");
        const navSearchContainer = document.getElementById("navSearchContainer");
        if (navSearchContainer) navSearchContainer.classList.remove("hidden");
        updateDashboardUI(cachedData);
        hasInstantRendered = true;
    } else {
        // Activate Card-Level Skeleton Loading State only if not already rendered
        setCardsLoadingState(query);
    }

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        if (!response.ok) {
            let errorMsg = "";
            try {
                const errData = await response.json();
                errorMsg = errData.detail || errData.error || errData.overview;
            } catch (_) {}
            if (response.status === 400 && errorMsg) {
                alert(errorMsg);
                showScreen("landingScreen");
                return;
            }
            throw new Error(`HTTP Error! Status: ${response.status}`);
        }

        const data = await response.json();
        currentSearchData = data;
        searchResultCache.set(cacheKey, data);
        try {
            sessionStorage.setItem("omni_cache_" + cacheKey, JSON.stringify(data));
        } catch (_) {}

        // 5. Instantly and completely re-render all dashboard sections with dynamic data
        updateDashboardUI(data);

        // If note detail modal is open, dynamically populate with the newly arrived study notes
        const noteModal = document.getElementById("noteDetailModal");
        if (noteModal && !noteModal.classList.contains("hidden")) {
            const primaryNote = (data.notes && data.notes.length > 0) ? data.notes[0] : null;
            openNoteModal({
                id: 0,
                title: `Study Notes: ${data.title || query}`,
                subject: data.category || data.domain || "Academic Curriculum",
                uploaded_by: "OmniLearn AI Academic Engine",
                file_type: "txt",
                ocr_text: data.study_notes || data.notes_content || studyNotes,
                file_path: (primaryNote && primaryNote.file_path) ? primaryNote.file_path : ""
            });
        }

        // Smooth scroll to top of dashboard content if first render
        if (!hasInstantRendered) {
            window.scrollTo({ top: 0, behavior: "smooth" });
        }
    } catch (err) {
        console.error("Search fetch failed:", err);
        if (!hasInstantRendered) {
            alert("Search failed. Please verify the backend is running and Gemini API key is valid.");
            showScreen("landingScreen");
        }
    } finally {
        isSearching = false;
    }
}

// Alias updateDashboardUI to renderDashboard and expose to window
function updateDashboardUI(data) {
    if (!data) return;
    renderDashboard(data);
}
window.updateDashboardUI = updateDashboardUI;
window.executeSearch = executeSearch;

// Form submit handler for main and nav inputs
function handleSearch(event, explicitQuery) {
    if (event) {
        event.preventDefault();
        if (typeof event.stopPropagation === "function") event.stopPropagation();
    }

    if (explicitQuery && explicitQuery.trim()) {
        executeSearch(explicitQuery.trim(), true);
        return;
    }

    const mainInput = document.getElementById("mainSearchInput");
    const navInput = document.getElementById("navSearchInput");
    const landingVisible = !document.getElementById("landingScreen").classList.contains("hidden");

    let query = "";
    if (document.activeElement === navInput && navInput && navInput.value.trim()) {
        query = navInput.value.trim();
    } else if (document.activeElement === mainInput && mainInput && mainInput.value.trim()) {
        query = mainInput.value.trim();
    } else if (landingVisible) {
        query = mainInput ? mainInput.value.trim() : (navInput ? navInput.value.trim() : "");
    } else {
        query = navInput ? navInput.value.trim() : (mainInput ? mainInput.value.trim() : "");
    }

    if (query) {
        executeSearch(query, true);
    }
}
window.handleSearch = handleSearch;

function fillAndSearch(topic) {
    executeSearch(topic, true);
}

function resetSearch(updateHistory = true) {
    const mainInput = document.getElementById("mainSearchInput");
    const navInput = document.getElementById("navSearchInput");
    if (mainInput) mainInput.value = "";
    if (navInput) navInput.value = "";

    const navContainer = document.getElementById("navSearchContainer");
    if (navContainer) navContainer.classList.add("hidden");

    showScreen("landingScreen");
    currentQuery = "";
    currentSearchData = null;
    closeYearSubjects();

    if (updateHistory) {
        window.history.pushState({}, "", window.location.pathname);
    }
    document.title = "OmniLearn - All-in-One Student Learning Hub";
}

function showScreen(screenId) {
    const screens = ["landingScreen", "loadingScreen", "dashboardScreen"];
    screens.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (id === screenId) {
                el.classList.remove("hidden");
            } else {
                el.classList.add("hidden");
            }
        }
    });
}

// --- Dashboard Render Methods ---
function renderDashboard(data) {
    // 1. Render Summary, Domain and Difficulty
    const topicTitle = data.title || data.canonical_title || data.query;
    document.getElementById("summaryTopicTitle").textContent = topicTitle;
    
    // Set Domain / Category Badge
    const domainBadge = document.getElementById("summaryDomainBadge");
    if (domainBadge) {
        domainBadge.textContent = data.category || data.domain || "Academic Curriculum";
    }
    
    // Format and render concise summary/overview text
    const summaryContainer = document.getElementById("overview-text") || document.getElementById("summaryText");
    const overviewContent = (data.overview || data.summary || "").trim();
    if (!overviewContent) {
        summaryContainer.innerHTML = `
            <div class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-sm font-medium flex items-center">
                <i class="fa-solid fa-triangle-exclamation mr-2.5 text-rose-500 text-base"></i>
                <span>Educational Overview Unavailable: Gemini API payload did not return an academic overview.</span>
            </div>`;
    } else {
        summaryContainer.innerHTML = formatSummaryMarkdown(overviewContent);
    }
    renderMathFormulas(summaryContainer);
    
    // Populate expandable in-depth detailed breakdown directly with theoretical_foundations and core_formulations
    const detailedContainer = document.getElementById("detailedBreakdownContainer");
    if (detailedContainer) {
        // Reset to collapsed state by default
        detailedContainer.classList.add("hidden");
        const btnText = document.getElementById("toggleDetailBtnText");
        const btnIcon = document.getElementById("toggleDetailBtnIcon");
        if (btnText) btnText.textContent = "Expand In-Depth Academic Notes";
        if (btnIcon) btnIcon.className = "fa-solid fa-chevron-down text-[10px] text-indigo-500 transition-transform duration-300 ml-1";
        
        const tf = (data.theoretical_foundations || "").trim();
        const cf = (data.core_formulations || "").trim();
        const db = (data.detailed_breakdown || data.detailedBreakdown || "").trim();

        if (!tf && !db) {
            detailedContainer.innerHTML = `
                <div class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-semibold flex items-center">
                    <i class="fa-solid fa-circle-exclamation mr-2 text-rose-500 text-sm"></i>
                    <span>Theoretical Foundations Unavailable: Content missing from Gemini API response.</span>
                </div>`;
        } else if (tf || cf) {
            detailedContainer.innerHTML = `
                <div class="space-y-4">
                    ${tf ? `
                        <div class="theoretical-foundations">
                            <h3 class="text-sm font-bold text-slate-800 mb-1 flex items-center border-b border-slate-200 pb-1">
                                <i class="fa-solid fa-microchip text-indigo-600 mr-2 text-xs"></i>Theoretical Foundations
                            </h3>
                            <div class="text-slate-700 text-sm leading-relaxed">${formatSummaryMarkdown(tf)}</div>
                        </div>` : ''}
                    ${cf ? `
                        <div class="core-formulations">
                            <h3 class="text-sm font-bold text-slate-800 mb-1 flex items-center border-b border-slate-200 pb-1">
                                <i class="fa-solid fa-code text-indigo-600 mr-2 text-xs"></i>Core Formulations & Algorithms
                            </h3>
                            <div class="text-slate-700 text-sm leading-relaxed">${formatSummaryMarkdown(cf)}</div>
                        </div>` : ''}
                </div>`;
            renderMathFormulas(detailedContainer);
        } else {
            detailedContainer.innerHTML = formatDetailedMarkdown(db);
            renderMathFormulas(detailedContainer);
        }
    }
    
    // Render Difficulty Score & Badges
    const diffScore = Number(data.difficulty_score || data.difficultyScore) || 0;
    document.getElementById("difficultyNumber").textContent = diffScore > 0 ? diffScore.toFixed(1) : "--";
    
    const diffBar = document.getElementById("difficultyBar");
    const diffLevelBadge = document.getElementById("difficultyLevelBadge");
    diffBar.style.width = `${Math.min(diffScore * 10, 100)}%`;
    
    // Color-code difficulty bar & badge
    const explicitLevel = data.difficultyLevel;
    diffBar.className = "h-3 rounded-full transition-all duration-700 ease-out ";
    if (diffScore <= 4.0 || explicitLevel === "Beginner") {
        diffBar.classList.add("bg-gradient-to-r", "from-emerald-400", "to-emerald-500");
        if (diffLevelBadge) {
            diffLevelBadge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full glass-badge glass-badge-emerald";
            diffLevelBadge.textContent = explicitLevel || "Beginner Friendly";
        }
    } else if (diffScore <= 7.0 || explicitLevel === "Intermediate") {
        diffBar.classList.add("bg-gradient-to-r", "from-amber-400", "to-amber-500");
        if (diffLevelBadge) {
            diffLevelBadge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full glass-badge glass-badge-amber";
            diffLevelBadge.textContent = explicitLevel || "Intermediate";
        }
    } else {
        diffBar.classList.add("bg-gradient-to-r", "from-rose-500", "to-red-600");
        if (diffLevelBadge) {
            diffLevelBadge.className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full glass-badge glass-badge-rose";
            diffLevelBadge.textContent = explicitLevel || "Advanced Academic";
        }
    }
    
    const aiEval = (data.ai_evaluation || data.aiEvaluation || data.difficulty_reasons || "").trim();
    document.getElementById("difficultyVerdict").textContent = aiEval || "AI complexity evaluation unavailable from API.";
    
    // Update topic bookmark button status
    updateTopicBookmarkButton();

    // 2. Render Roadmap Timeline with Checklists
    renderRoadmap(data.roadmap);

    // Set global studyNotes state explicitly for the active search query
    studyNotes = (data.study_notes || data.notes_content || (data.notes && data.notes[0] ? data.notes[0].ocr_text : "")).trim();
    try {
        sessionStorage.setItem("omni_study_notes", studyNotes);
        localStorage.setItem("omni_active_topic", topicTitle);
    } catch (e) {}

    // 3. Render Notes Panel
    renderNotesList(data.notes);

    // 4. Render YouTube Videos
    renderYouTubeVideos(data.curated_videos || data.youtube_videos);

    // 5. Render Web Links
    renderWebResources(data.web_resources);

    // 5.5 Render Careers (roadmap.sh)
    renderCareers(data.careers, data.careerRelevance);

    // 6. Render Fun Fact / Did You Know
    renderFunFact(data.didYouKnow || data.did_you_know || data.fun_fact);

    // 7. Render Chart.js Analytics
    renderAnalyticsChart(data.pyqs, data.examFrequency || data.exam_frequency);

    // 8. Re-typeset all mathematical formulas via MathJax across the dashboard
    renderMathFormulas();
}

function toggleDetailedBreakdown() {
    const container = document.getElementById("detailedBreakdownContainer");
    const btnText = document.getElementById("toggleDetailBtnText");
    const btnIcon = document.getElementById("toggleDetailBtnIcon");
    if (!container) return;
    
    const isHidden = container.classList.contains("hidden");
    if (isHidden) {
        container.classList.remove("hidden");
        if (btnText) btnText.textContent = "Collapse In-Depth Notes";
        if (btnIcon) btnIcon.className = "fa-solid fa-chevron-up text-[10px] text-indigo-600 transition-transform duration-300 ml-1";
        renderMathFormulas(container);
    } else {
        container.classList.add("hidden");
        if (btnText) btnText.textContent = "Expand In-Depth Academic Notes";
        if (btnIcon) btnIcon.className = "fa-solid fa-chevron-down text-[10px] text-indigo-500 transition-transform duration-300 ml-1";
    }
}

function prepareMathMarkdown(rawText) {
    if (!rawText || typeof rawText !== 'string') return "";
    
    // 1. Unescape literal \n into real newlines
    let clean = rawText.replace(/\\n/g, '\n');

    // 2. Clean decorative borders and leading headline hashes
    clean = clean
        .replace(/^[=\-~_#*]{4,}\s*$/gm, '')
        .replace(/^#+\s+/gm, '')
        .replace(/^[=\-]{3,}.*$/gm, '');

    // 3. Detect and wrap C/C++ or Python code snippets if not inside backticks
    if (!clean.includes("```") && (clean.includes("malloc(") || clean.includes("sizeof(") || clean.includes("int main") || clean.includes("def ") || clean.includes("class "))) {
        clean = clean.replace(
            /((?:(?:int|char|float|double|void|\*|struct)\s+[\w*]+\s*=|if\s*\([^)]+\)\s*\{|malloc\()[^`]+?(?:;\s*\}|;))/g,
            "\n```c\n$1\n```\n"
        );
    }

    // 4. Wrap naked LaTeX commands in math delimiters ($...$ or $$...$$)
    const latexCmds = [
        '\\text{', '\\frac{', '\\mathcal{', '\\pmod', '\\times', '\\cdot',
        '\\sum', '\\int', '\\sqrt', '\\alpha', '\\beta', '\\theta', '\\Theta',
        '\\Omega', '\\leq', '\\geq', '\\approx'
    ];

    let lines = clean.split('\n');
    let processed = [];
    let inCode = false;

    for (let line of lines) {
        let trimmed = line.trim();
        if (trimmed.startsWith('```')) {
            inCode = !inCode;
            processed.push(line);
            continue;
        }
        if (inCode || !trimmed) {
            processed.push(line);
            continue;
        }

        // Already delimited with $$ or $ or \[
        if ((trimmed.startsWith('$$') && trimmed.endsWith('$$')) ||
            (trimmed.startsWith('$') && trimmed.endsWith('$')) ||
            (trimmed.startsWith('\\[') && trimmed.endsWith('\\]'))) {
            processed.push(line);
            continue;
        }

        const hasLatex = latexCmds.some(cmd => trimmed.includes(cmd));
        if (hasLatex) {
            if (!trimmed.includes('$')) {
                const colonIdx = trimmed.indexOf(':');
                if (colonIdx !== -1 && latexCmds.some(cmd => trimmed.slice(colonIdx).includes(cmd))) {
                    const prefix = trimmed.slice(0, colonIdx + 1);
                    const eq = trimmed.slice(colonIdx + 1).trim();
                    processed.push(prefix);
                    processed.push(`$$${eq}$$`);
                    continue;
                } else if (trimmed.includes('=') || trimmed.includes('\\\\') || trimmed.startsWith('\\text') || trimmed.startsWith('A[')) {
                    if (trimmed.includes('\\\\')) {
                        const parts = trimmed.split('\\\\').map(p => p.trim()).filter(Boolean);
                        for (const p of parts) {
                            processed.push(p.includes('$') ? p : `$$${p}$$`);
                        }
                        continue;
                    } else {
                        processed.push(`$$${trimmed}$$`);
                        continue;
                    }
                }
            } else {
                // Ensure \mathcal{...} without dollar signs are wrapped
                line = line.replace(/(?<!\$)\\mathcal\{[A-Za-z]\}(?:\([a-zA-Z0-9+\-* /]+\))?(?!\$)/g, '$$&$');
            }
        }
        processed.push(line);
    }

    return processed.join('\n');
}

function formatSummaryMarkdown(rawText) {
    if (!rawText) return "<p class='text-slate-500'>Comprehensive academic notes are being compiled for this syllabus topic.</p>";
    
    let clean = prepareMathMarkdown(rawText);

    if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        try {
            marked.setOptions({ gfm: true, breaks: true });
            return marked.parse(clean);
        } catch(e) {}
    }

    let formatted = clean
        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-800 font-bold">$1</strong>')
        .replace(/\*(.*?)\*/g, '<em class="italic text-slate-700">$1</em>')
        .replace(/`([^`]+)`/g, '<code class="bg-slate-100 text-indigo-700 px-1 py-0.5 rounded text-xs font-mono">$1</code>')
        .replace(/\n\n/g, '</p><p class="mt-2.5">')
        .replace(/\n/g, '<br>');
    return `<p>${formatted}</p>`;
}

function formatDetailedMarkdown(rawText) {
    if (!rawText) return "<p class='text-slate-400 italic'>No detailed notes available.</p>";
    
    // Convert headers, lists, code, and bolding
    let lines = rawText.split("\n");
    let htmlLines = [];
    let inList = false;
    
    for (let line of lines) {
        let trimmed = line.trim();
        if (!trimmed) {
            if (inList) {
                htmlLines.push("</ul>");
                inList = false;
            }
            continue;
        }
        
        if (trimmed.startsWith("#### ")) {
            if (inList) { htmlLines.push("</ul>"); inList = false; }
            htmlLines.push(`<h4 class="text-xs font-bold uppercase tracking-wider text-indigo-900 mt-3 mb-1">${trimmed.replace("#### ", "")}</h4>`);
        } else if (trimmed.startsWith("### ")) {
            if (inList) { htmlLines.push("</ul>"); inList = false; }
            htmlLines.push(`<h3 class="text-sm font-bold text-slate-800 mt-4 mb-1.5 flex items-center border-b border-slate-200 pb-1"><i class="fa-solid fa-graduation-cap text-indigo-600 mr-2 text-xs"></i>${trimmed.replace("### ", "")}</h3>`);
        } else if (trimmed.startsWith("## ")) {
            if (inList) { htmlLines.push("</ul>"); inList = false; }
            htmlLines.push(`<h2 class="text-base font-extrabold text-slate-900 mt-4 mb-2 pb-1 border-b border-indigo-100">${trimmed.replace("## ", "")}</h2>`);
        } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
            if (!inList) {
                htmlLines.push("<ul class='space-y-1.5 my-2 pl-4 list-disc marker:text-indigo-500'>");
                inList = true;
            }
            let itemContent = trimmed.substring(2).replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-800 font-semibold">$1</strong>');
            htmlLines.push(`<li class="text-xs text-slate-600 leading-relaxed">${itemContent}</li>`);
        } else {
            if (inList) { htmlLines.push("</ul>"); inList = false; }
            let pContent = trimmed.replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-800 font-semibold">$1</strong>');
            htmlLines.push(`<p class="text-xs text-slate-600 leading-relaxed my-2">${pContent}</p>`);
        }
    }
    
    if (inList) htmlLines.push("</ul>");
    return htmlLines.join("\n");
}

// --- Render Helper Blocks ---
function renderRoadmap(steps) {
    const container = document.getElementById("roadmapTimeline");
    const progressBadge = document.getElementById("roadmapProgressBadge");
    container.innerHTML = "";
    
    if (!steps || steps.length === 0) {
        container.innerHTML = `<p class="text-xs text-slate-400 italic">No roadmap steps calculated.</p>`;
        if (progressBadge) progressBadge.textContent = "0 Steps";
        return;
    }

    const qKey = (currentSearchData ? currentSearchData.query : currentQuery).toLowerCase();
    if (!completedRoadmapSteps[qKey]) {
        completedRoadmapSteps[qKey] = new Set();
    }
    const completedSet = completedRoadmapSteps[qKey];
    
    updateRoadmapProgressDisplay(steps.length, completedSet.size);
    
    steps.forEach((step, idx) => {
        const isDone = completedSet.has(idx);
        const stepEl = document.createElement("div");
        stepEl.className = `relative mb-4 last:mb-0 transition-all duration-200 ${isDone ? 'opacity-65' : ''}`;
        
        let typeBadgeColor = "glass-badge glass-badge-indigo";
        let dotColor = "border-slate-300 bg-white text-slate-400";
        let typeLabel = step.type || "Core";
        
        if (step.type === "prerequisite") {
            typeBadgeColor = "glass-badge glass-badge-indigo";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-blue-500 bg-blue-50 text-blue-600";
            typeLabel = "Prerequisite";
        } else if (step.type === "core") {
            typeBadgeColor = "glass-badge glass-badge-indigo";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-indigo-500 bg-indigo-50 text-indigo-600";
            typeLabel = "Core Principle";
        } else if (step.type === "deep_dive") {
            typeBadgeColor = "glass-badge glass-badge-amber";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-amber-500 bg-amber-50 text-amber-600";
            typeLabel = "Deep Dive";
        } else if (step.type === "practice") {
            typeBadgeColor = "glass-badge glass-badge-emerald";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-teal-500 bg-teal-50 text-teal-600";
            typeLabel = "Problem Practice";
        } else if (step.type === "advanced") {
            typeBadgeColor = "glass-badge glass-badge-purple";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-purple-500 bg-purple-50 text-purple-600";
            typeLabel = "Advanced Scope";
        }
        
        stepEl.innerHTML = `
            <span class="absolute -left-[23px] top-1 rounded-full border-2 ${dotColor} w-5 h-5 flex items-center justify-center text-[10px] font-bold shadow-sm cursor-pointer" onclick="toggleRoadmapStep(${idx})">
                ${isDone ? '<i class="fa-solid fa-check text-[9px]"></i>' : (idx + 1)}
            </span>
            <div class="bg-slate-50 hover:bg-slate-100/80 border border-slate-200/70 rounded-lg p-3 transition shadow-xs">
                <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center space-x-2">
                        <input type="checkbox" ${isDone ? 'checked' : ''} onchange="toggleRoadmapStep(${idx})" 
                               class="rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer h-3.5 w-3.5 border-slate-300">
                        <span class="text-[10px] font-bold uppercase tracking-wider ${typeBadgeColor} px-1.5 py-0.5 rounded">
                            ${typeLabel}
                        </span>
                    </div>
                    <span class="text-[10px] text-slate-500 font-medium flex items-center">
                        <i class="fa-regular fa-clock mr-1 text-slate-400"></i>${step.estimated_time || "2-3 hrs"}
                    </span>
                </div>
                <h4 class="font-bold text-xs text-slate-800 mt-1.5 ${isDone ? 'line-through text-slate-500' : ''}">${step.concept}</h4>
                <p class="text-xs text-slate-600 mt-1 leading-relaxed">${step.description}</p>
            </div>
        `;
        container.appendChild(stepEl);
    });
}

function toggleRoadmapStep(stepIndex) {
    if (!currentSearchData || !currentSearchData.roadmap) return;
    const qKey = (currentSearchData.query || currentQuery).toLowerCase();
    if (!completedRoadmapSteps[qKey]) {
        completedRoadmapSteps[qKey] = new Set();
    }
    
    if (completedRoadmapSteps[qKey].has(stepIndex)) {
        completedRoadmapSteps[qKey].delete(stepIndex);
    } else {
        completedRoadmapSteps[qKey].add(stepIndex);
    }
    
    // Re-render roadmap view
    renderRoadmap(currentSearchData.roadmap);
}

function updateRoadmapProgressDisplay(total, completed) {
    const progressBadge = document.getElementById("roadmapProgressBadge");
    if (!progressBadge) return;
    
    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
    progressBadge.textContent = `${completed} / ${total} Done (${pct}%)`;
    
    if (completed === total && total > 0) {
        progressBadge.className = "text-[11px] font-bold glass-badge glass-badge-emerald px-2.5 py-0.5 rounded-full";
    } else if (completed > 0) {
        progressBadge.className = "text-[11px] font-bold glass-badge glass-badge-indigo px-2.5 py-0.5 rounded-full";
    } else {
        progressBadge.className = "text-[11px] font-bold glass-badge glass-badge-purple px-2.5 py-0.5 rounded-full";
    }
}

function renderNotesList(notes) {
    const container = document.getElementById("notesList");
    if (!container) return;
    container.innerHTML = "";
    
    // If no notes returned from DB, construct a primary topic note using studyNotes or academic fallback
    let displayNotes = (notes && notes.length > 0) ? [...notes] : [];
    if (displayNotes.length === 0) {
        const topicTitle = (currentSearchData && (currentSearchData.title || currentSearchData.query)) || currentQuery || "Academic Topic";
        const primaryContent = studyNotes || generateAcademicFallbackNotes(topicTitle, (currentSearchData && (currentSearchData.category || currentSearchData.domain)));
        if (!studyNotes) {
            studyNotes = primaryContent;
            try { sessionStorage.setItem("omni_study_notes", studyNotes); } catch(e) {}
        }
        displayNotes.push({
            id: 0,
            title: `Study Notes: ${topicTitle}`,
            subject: (currentSearchData && (currentSearchData.category || currentSearchData.domain)) || "Academic Curriculum",
            uploaded_by: "OmniLearn AI Academic Engine",
            file_type: "txt",
            ocr_text: primaryContent,
            file_path: ""
        });
    }
    
    displayNotes.forEach((note, idx) => {
        const noteCard = document.createElement("div");
        noteCard.className = "bg-slate-50 border border-slate-100 hover:border-indigo-300 rounded-xl p-3.5 transition-all duration-200 cursor-pointer flex flex-col justify-between shadow-sm hover:shadow";
        noteCard.onclick = () => openNoteModal(note);
        
        // Clean snippet preview with raw markdown symbols stripped
        const rawContent = note.ocr_text || (idx === 0 ? studyNotes : "") || "";
        const snippet = stripMarkdownSymbols(rawContent).substring(0, 115);
        
        noteCard.innerHTML = `
            <div>
                <div class="flex items-center justify-between">
                    <span class="text-[10px] font-bold glass-badge glass-badge-indigo px-2 py-0.5 rounded-full capitalize">${note.subject || 'Academic'}</span>
                    <span class="text-[10px] font-medium text-slate-400 uppercase">${note.file_type || 'TXT'}</span>
                </div>
                <h4 class="font-bold text-xs text-slate-900 mt-2 line-clamp-1">${note.title}</h4>
                ${snippet ? `<p class="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">${snippet}...</p>` : ''}
            </div>
            <div class="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-200/60 text-[10px] text-slate-400">
                <span class="truncate max-w-[110px]"><i class="fa-regular fa-user mr-1 text-slate-400"></i>${note.uploaded_by || 'OmniLearn'}</span>
                <button type="button" class="view-file-btn text-indigo-600 hover:text-indigo-800 font-semibold flex items-center glass-btn px-2.5 py-1 rounded-md text-[10px]" style="cursor: pointer; position: relative; z-index: 10; pointer-events: auto;">
                    <span>View File &gt;</span>
                </button>
            </div>
        `;

        const viewFileBtn = noteCard.querySelector('.view-file-btn');
        if (viewFileBtn) {
            viewFileBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openStudyNotesModal(note);
            });
        }

        container.appendChild(noteCard);
    });
}

// Deep text searching inside notes via backend API
async function filterNotesLocal() {
    const val = document.getElementById("noteSearchInput").value.trim();
    if (!val) {
        // Restore default notes list from initial query
        if (currentSearchData) renderNotesList(currentSearchData.notes);
        return;
    }
    
    try {
        const response = await fetch(`/api/notes/search?query=${encodeURIComponent(val)}`);
        if (response.ok) {
            const matchedNotes = await response.json();
            renderNotesList(matchedNotes);
        }
    } catch (e) {
        console.error("Failed to execute note deep search:", e);
    }
}

function renderYouTubeVideos(videos) {
    const container = document.getElementById("videoContainer");
    container.innerHTML = "";
    
    if (!videos || videos.length === 0) {
        container.innerHTML = `<p class="text-xs text-slate-400 italic">No video tutorials found.</p>`;
        return;
    }
    
    videos.forEach(video => {
        const card = document.createElement("div");
        card.className = "flex flex-col sm:flex-row bg-slate-50 border border-slate-200/80 rounded-xl overflow-hidden hover:border-indigo-300 hover:shadow-md transition duration-200 group";
        
        card.innerHTML = `
            <div class="relative w-full sm:w-44 h-28 bg-slate-900 flex-shrink-0 cursor-pointer overflow-hidden" onclick="playVideo(this, '${video.video_id}')">
                <img src="${video.thumbnail_url}" alt="Thumbnail" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
                <div class="absolute inset-0 bg-black/25 flex items-center justify-center group-hover:bg-black/35 transition">
                    <div class="w-10 h-10 rounded-full bg-red-600/90 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition">
                        <i class="fa-solid fa-play text-sm ml-0.5"></i>
                    </div>
                </div>
            </div>
            <div class="p-3 flex flex-col justify-between flex-1 min-w-0">
                <div>
                    <h4 class="font-bold text-xs text-slate-800 line-clamp-2 leading-snug group-hover:text-indigo-600 transition">${video.title}</h4>
                    <div class="flex items-center space-x-1.5 mt-1.5">
                        <span class="text-[11px] font-semibold text-slate-600 truncate">${video.channel_title || "Educational Lecture"}</span>
                        <i class="fa-solid fa-circle-check text-[9px] text-blue-500" title="Verified Educational Source"></i>
                    </div>
                </div>
                <div class="flex justify-between items-center text-[10px] text-slate-500 mt-2.5 pt-2 border-t border-slate-200/60">
                    <span class="font-medium bg-slate-200/70 text-slate-700 px-1.5 py-0.5 rounded">${video.view_count || "Popular"}</span>
                    <a href="https://youtube.com/watch?v=${video.video_id}" target="_blank" class="text-indigo-600 hover:text-indigo-800 font-semibold flex items-center">
                        Open YouTube <i class="fa-solid fa-arrow-up-right-from-square ml-1 text-[9px]"></i>
                    </a>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

function playVideo(element, videoId) {
    // Replace thumbnail wrapper with embedded iframe
    element.parentElement.innerHTML = `
        <div class="w-full h-64 bg-black rounded-xl overflow-hidden shadow-inner">
            <iframe class="w-full h-full" src="https://www.youtube.com/embed/${videoId}?autoplay=1" 
                    title="YouTube video player" frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    allowfullscreen></iframe>
        </div>
    `;
}

function renderWebResources(resources) {
    const container = document.getElementById("resourcesContainer");
    container.innerHTML = "";
    
    if (!resources || resources.length === 0) {
        container.innerHTML = `<p class="text-xs text-slate-400 italic">No web links aggregated.</p>`;
        return;
    }
    
    resources.forEach(item => {
        const linkCard = document.createElement("div");
        linkCard.className = "bg-slate-50 border border-slate-100 rounded-lg p-3 hover:bg-slate-100 transition flex items-start space-x-3";
        
        linkCard.innerHTML = `
            <div class="text-blue-500 mt-0.5"><i class="fa-solid fa-globe text-sm"></i></div>
            <div class="min-w-0 flex-1">
                <a href="${item.url}" target="_blank" class="font-bold text-xs text-indigo-600 hover:underline hover:text-indigo-800 line-clamp-1">
                    ${item.title} <i class="fa-solid fa-arrow-up-right-from-square text-[9px] ml-0.5"></i>
                </a>
                <p class="text-[10px] text-slate-500 line-clamp-2 mt-1 leading-normal">${item.snippet}</p>
            </div>
        `;
        container.appendChild(linkCard);
    });
}

function renderFunFact(fact) {
    const el = document.getElementById("funFactText");
    if (!el) return;
    if (fact && fact.trim()) {
        el.textContent = fact;
    } else {
        el.textContent = "Trivia fact unavailable from Gemini API.";
    }
}

// Renders the trend chart indicating how often the topic appears over the years
function renderAnalyticsChart(pyqs, examFrequency) {
    const canvas = document.getElementById("frequencyChart");
    if (!canvas) return;
    
    const years = [2021, 2022, 2023, 2024, 2025];
    const counts = {};
    years.forEach(yr => { counts[yr] = 0; });
    
    let hasFrequency = false;
    if (Array.isArray(examFrequency) && examFrequency.length > 0) {
        if (typeof examFrequency[0] === 'number') {
            examFrequency.slice(0, 5).forEach((val, idx) => {
                if (idx < years.length) {
                    counts[years[idx]] = Number(val) || 0;
                    hasFrequency = true;
                }
            });
        } else {
            examFrequency.forEach(item => {
                if (item && item.year && counts[item.year] !== undefined) {
                    counts[item.year] = Number(item.count) || 0;
                    hasFrequency = true;
                }
            });
        }
    }

    if (!hasFrequency) {
        const safePyqs = Array.isArray(pyqs) ? pyqs : [];
        safePyqs.forEach(pyq => {
            if (pyq && counts[pyq.year] !== undefined) {
                counts[pyq.year]++;
            }
        });
    }
    
    const dataPoints = years.map(yr => counts[yr]);
    const totalCount = dataPoints.reduce((a, b) => a + b, 0);

    const subtitle = document.getElementById("chartFrequencySubtitle");
    if (subtitle) {
        if (totalCount > 0) {
            subtitle.textContent = `${totalCount} verified question appearances mapped across AKTU & GATE exams (2021–2025).`;
        } else {
            subtitle.textContent = "Frequency of query appearances in past exams (2021–2025).";
        }
    }
    
    // Destruct existing chart instance cleanly if it exists
    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }
    
    // Resolve theme colors
    const gridColor = '#f1f5f9';
    const textColor = '#64748b';
    
    // Create line chart
    chartInstance = new Chart(canvas, {
        type: 'line',
        data: {
            labels: years.map(String),
            datasets: [{
                label: 'Exam Appearances',
                data: dataPoints,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: '#10b981'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: { size: 9 },
                        color: textColor
                    },
                    grid: { color: gridColor }
                },
                x: {
                    ticks: { font: { size: 9 }, color: textColor },
                    grid: { display: false }
                }
            }
        }
    });
}

// --- Bookmark Handling ---
async function fetchBookmarks() {
    try {
        const response = await fetch("/api/bookmarks");
        if (response.ok) {
            bookmarks = await response.json();
            updateBookmarksList();
        }
    } catch (e) {
        console.error("Failed to load bookmarks:", e);
    }
}

function updateBookmarksList() {
    const list = document.getElementById("bookmarksList");
    document.getElementById("bookmarkCount").textContent = bookmarks.length;
    
    list.innerHTML = "";
    if (bookmarks.length === 0) {
        list.innerHTML = `<p class="text-sm text-slate-400 italic">No bookmarks saved yet.</p>`;
        return;
    }
    
    bookmarks.forEach(bk => {
        const el = document.createElement("div");
        el.className = "bg-slate-50 border border-slate-100 rounded-lg p-3 flex justify-between items-center hover:border-indigo-100 transition";
        
        let icon = "fa-solid fa-file-lines text-indigo-500";
        if (bk.item_type === "topic") icon = "fa-solid fa-graduation-cap text-purple-500";
        
        el.innerHTML = `
            <div class="flex items-center space-x-3 cursor-pointer min-w-0" onclick="handleBookmarkClick('${bk.item_type}', ${bk.item_id}, '${bk.title}')">
                <i class="${icon} text-lg"></i>
                <div class="min-w-0">
                    <h4 class="font-bold text-xs text-slate-800 line-clamp-1">${bk.title}</h4>
                    <span class="text-[9px] text-slate-400 uppercase tracking-wider font-semibold">${bk.item_type}</span>
                </div>
            </div>
            <button onclick="removeBookmark(${bk.id}, event)" class="glass-btn-icon text-slate-400 hover:text-red-500 transition" title="Remove Bookmark">
                <i class="fa-solid fa-trash-can text-xs"></i>
            </button>
        `;
        list.appendChild(el);
    });
}

async function handleBookmarkClick(type, id, title) {
    if (type === "topic") {
        document.getElementById("navSearchInput").value = title;
        toggleBookmarksSidebar();
        handleSearch();
    } else {
        // Fetch note detail by id and open modal
        try {
            const response = await fetch("/api/notes");
            if (response.ok) {
                const notes = await response.json();
                const noteObj = notes.find(n => n.id === id);
                if (noteObj) {
                    toggleBookmarksSidebar();
                    openNoteModal(noteObj);
                } else {
                    alert("Note no longer exists.");
                }
            }
        } catch (e) {
            console.error(e);
        }
    }
}

async function toggleTopicBookmark() {
    if (!currentSearchData) return;
    
    // Check if already bookmarked
    const existing = bookmarks.find(b => b.item_type === "topic" && b.title.toLowerCase() === currentSearchData.query.toLowerCase());
    
    if (existing) {
        // Delete it
        await removeBookmark(existing.id);
    } else {
        // Create it
        try {
            const response = await fetch("/api/bookmarks", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    item_type: "topic",
                    item_id: 0, // Topics don't have explicit single IDs, using 0
                    title: currentSearchData.query
                })
            });
            if (response.ok) {
                await fetchBookmarks();
                updateTopicBookmarkButton();
            }
        } catch (e) {
            console.error(e);
        }
    }
}

function updateTopicBookmarkButton() {
    const btn = document.getElementById("bookmarkTopicBtn");
    if (!btn || !currentSearchData) return;
    
    const isBookmarked = bookmarks.some(b => b.item_type === "topic" && b.title.toLowerCase() === currentSearchData.query.toLowerCase());
    
    if (isBookmarked) {
        btn.innerHTML = `<i class="fa-solid fa-bookmark text-2xl text-yellow-500"></i>`;
    } else {
        btn.innerHTML = `<i class="fa-regular fa-bookmark text-2xl"></i>`;
    }
}

async function removeBookmark(bookmarkId, event) {
    if (event) event.stopPropagation();
    try {
        const response = await fetch(`/api/bookmarks/${bookmarkId}`, {
            method: "DELETE"
        });
        if (response.ok) {
            await fetchBookmarks();
            updateTopicBookmarkButton();
            if (currentNote) updateNoteModalBookmarkButton();
        }
    } catch (e) {
        console.error(e);
    }
}

function toggleBookmarksSidebar() {
    const bar = document.getElementById("bookmarksSidebar");
    if (bar.classList.contains("translate-x-full")) {
        bar.classList.remove("translate-x-full");
    } else {
        bar.classList.add("translate-x-full");
    }
}

// --- Note Details Modal Operations, TOC Extraction & Markdown Rendering ---

function stripMarkdownSymbols(text) {
    if (!text) return "";
    return text
        .replace(/^[=\-]{3,}.*$/gm, '') // Remove === and --- lines
        .replace(/^#+\s+/gm, '')        // Remove header hashes
        .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold
        .replace(/\*(.*?)\*/g, '$1')     // Remove italics
        .replace(/`([^`]+)`/g, '$1')     // Remove inline code ticks
        .replace(/```[\s\S]*?```/g, '')  // Remove code blocks
        .replace(/\\([a-zA-Z]+)/g, '$1') // Clean LaTeX backslash commands
        .replace(/\\/g, '')              // Clean lone backslashes
        .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1') // Clean links
        .replace(/^>\s*/gm, '')          // Remove blockquote marks
        .replace(/\s+/g, ' ')
        .trim();
}

function formatInlineMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-slate-900">$1</strong>')
        .replace(/\*(.*?)\*/g, '<em class="italic text-slate-700">$1</em>')
        .replace(/`([^`]+)`/g, '<code class="bg-slate-100 text-indigo-700 px-1.5 py-0.5 rounded text-[11px] font-mono border border-slate-200">$1</code>');
}

function renderMarkdownToHtml(rawText) {
    if (!rawText) return "<p class='text-slate-400 italic p-4'>No study notes content available.</p>";
    
    // Pre-process text to remove ASCII divider noise and convert LaTeX notation into readable math
    let cleanText = rawText
        .replace(/^[=\-]{4,}.*$/gm, '') // Remove ASCII banners
        .replace(/\n{3,}/g, '\n\n')
        .replace(/\\mathcal\{([A-Za-z]+)\}/g, '$1')
        .replace(/\\mathbf\{([A-Za-z0-9]+)\}/g, '$1')
        .replace(/\\sum_\{([^\}]+)\}\^\{([^\}]+)\}/g, '∑($1 to $2)')
        .replace(/\\int_\{([^\}]+)\}\^\{([^\}]+)\}/g, '∫($1 to $2)')
        .replace(/\\cdot/g, '·')
        .replace(/\\omega/g, 'ω')
        .replace(/\\psi/g, 'ψ')
        .replace(/\\epsilon/g, 'ε')
        .replace(/\\alpha/g, 'α')
        .replace(/\\beta/g, 'β')
        .replace(/\\theta/g, 'θ')
        .replace(/\\mu/g, 'μ')
        .replace(/\\le/g, '≤')
        .replace(/\\ge/g, '≥')
        .replace(/\\ne/g, '≠')
        .replace(/\\in/g, '∈')
        .replace(/\\subset/g, '⊂')
        .replace(/\\left\(/g, '(')
        .replace(/\\right\)/g, ')')
        .replace(/\\([,;!])/g, '$1');

    // Use marked.js if available
    if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        try {
            marked.setOptions({
                gfm: true,
                breaks: true
            });
            let parsed = marked.parse(cleanText);
            
            // Post-process HTML with modern technical document styling classes
            parsed = parsed
                .replace(/<pre><code>/g, '<pre class="code-block"><code>')
                .replace(/<table/g, '<div class="overflow-x-auto my-4"><table class="min-w-full text-xs border border-slate-200 rounded-xl overflow-hidden shadow-sm"')
                .replace(/<\/table>/g, '</table></div>')
                .replace(/<th>/g, '<th class="bg-slate-50 border border-slate-200 px-3.5 py-2.5 text-left font-bold text-slate-800">')
                .replace(/<td>/g, '<td class="border border-slate-200 px-3.5 py-2 text-slate-600">')
                .replace(/<h1>/g, '<h1 class="text-xl sm:text-2xl font-extrabold text-slate-900 mt-6 mb-3 pb-2 border-b border-slate-200">')
                .replace(/<h2>/g, '<h2 class="text-base sm:text-lg font-bold text-slate-900 mt-6 mb-3 pb-1.5 border-b border-slate-100 flex items-center">')
                .replace(/<h3>/g, '<h3 class="text-sm sm:text-base font-bold text-indigo-900 mt-4 mb-2 flex items-center">')
                .replace(/<h4>/g, '<h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider mt-3 mb-1.5">')
                .replace(/<ul>/g, '<ul class="list-disc pl-5 space-y-1.5 my-3 text-xs sm:text-sm text-slate-600">')
                .replace(/<ol>/g, '<ol class="list-decimal pl-5 space-y-1.5 my-3 text-xs sm:text-sm text-slate-600">')
                .replace(/<code>([^<]+)<\/code>/g, '<code class="bg-slate-100 text-indigo-700 px-1.5 py-0.5 rounded text-[11px] font-mono border border-slate-200">$1</code>')
                .replace(/<blockquote>/g, '<blockquote class="border-l-4 border-indigo-500 bg-indigo-50/50 p-3.5 rounded-r-xl my-3 text-slate-700 text-xs sm:text-sm">');
                
            return parsed;
        } catch (e) {
            console.warn("marked.parse encountered error, using internal parser:", e);
        }
    }
    
    // Built-in resilient Markdown parser
    let lines = cleanText.split("\n");
    let htmlLines = [];
    let inCodeBlock = false;
    let codeBuffer = [];
    let inList = false;
    let listType = "ul";
    let inTable = false;
    
    for (let line of lines) {
        let trimmed = line.trim();
        
        // Code Block
        if (trimmed.startsWith("```")) {
            if (inCodeBlock) {
                htmlLines.push(`<pre class="code-block"><code>${codeBuffer.join("\n")}</code></pre>`);
                codeBuffer = [];
                inCodeBlock = false;
            } else {
                if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
                if (inTable) { htmlLines.push("</tbody></table></div>"); inTable = false; }
                inCodeBlock = true;
            }
            continue;
        }
        
        if (inCodeBlock) {
            codeBuffer.push(line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'));
            continue;
        }
        
        if (!trimmed) {
            if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
            if (inTable) { htmlLines.push("</tbody></table></div>"); inTable = false; }
            continue;
        }
        
        // Table Rows
        if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
            if (!inTable) {
                if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
                htmlLines.push('<div class="overflow-x-auto my-3"><table class="min-w-full text-xs border border-slate-200 rounded-lg"><tbody>');
                inTable = true;
            }
            if (trimmed.includes("---")) {
                continue;
            }
            let cells = trimmed.split("|").slice(1, -1);
            let rowHtml = "<tr>" + cells.map(c => `<td class="border border-slate-200 px-3 py-1.5 text-slate-600">${formatInlineMarkdown(c.trim())}</td>`).join("") + "</tr>";
            htmlLines.push(rowHtml);
            continue;
        } else if (inTable) {
            htmlLines.push("</tbody></table></div>");
            inTable = false;
        }
        
        // Headers
        if (trimmed.startsWith("#### ")) {
            if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
            htmlLines.push(`<h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider mt-3 mb-1.5">${formatInlineMarkdown(trimmed.substring(5))}</h4>`);
        } else if (trimmed.startsWith("### ")) {
            if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
            htmlLines.push(`<h3 class="text-sm font-bold text-indigo-900 mt-4 mb-2 flex items-center"><i class="fa-solid fa-angle-right mr-1.5 text-xs text-indigo-500"></i>${formatInlineMarkdown(trimmed.substring(4))}</h3>`);
        } else if (trimmed.startsWith("## ")) {
            if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
            htmlLines.push(`<h2 class="text-base font-bold text-slate-900 mt-5 mb-2 pb-1 border-b border-slate-100 flex items-center">${formatInlineMarkdown(trimmed.substring(3))}</h2>`);
        } else if (trimmed.startsWith("# ")) {
            if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
            htmlLines.push(`<h1 class="text-xl font-extrabold text-slate-900 mt-5 mb-3 pb-2 border-b border-slate-200">${formatInlineMarkdown(trimmed.substring(2))}</h1>`);
        } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
            if (!inList || listType !== "ul") {
                if (inList) htmlLines.push(`</${listType}>`);
                htmlLines.push('<ul class="list-disc pl-5 space-y-1.5 my-2 text-xs sm:text-sm text-slate-600">');
                inList = true;
                listType = "ul";
            }
            htmlLines.push(`<li>${formatInlineMarkdown(trimmed.substring(2))}</li>`);
        } else if (/^\d+\.\s+/.test(trimmed)) {
            let content = trimmed.replace(/^\d+\.\s+/, '');
            if (!inList || listType !== "ol") {
                if (inList) htmlLines.push(`</${listType}>`);
                htmlLines.push('<ol class="list-decimal pl-5 space-y-1.5 my-2 text-xs sm:text-sm text-slate-600">');
                inList = true;
                listType = "ol";
            }
            htmlLines.push(`<li>${formatInlineMarkdown(content)}</li>`);
        } else if (trimmed.startsWith("> ")) {
            if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
            htmlLines.push(`<blockquote class="border-l-4 border-indigo-500 bg-indigo-50/50 p-3 rounded-r-lg my-2 text-slate-700 text-xs sm:text-sm">${formatInlineMarkdown(trimmed.substring(2))}</blockquote>`);
        } else if (trimmed === "---" || trimmed === "***" || trimmed.startsWith("===")) {
            if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
            htmlLines.push('<hr class="my-4 border-slate-200">');
        } else {
            if (inList) { htmlLines.push(`</${listType}>`); inList = false; }
            htmlLines.push(`<p class="text-xs sm:text-sm text-slate-600 leading-relaxed my-2">${formatInlineMarkdown(trimmed)}</p>`);
        }
    }
    
    if (inCodeBlock) {
        htmlLines.push(`<pre class="code-block"><code>${codeBuffer.join("\n")}</code></pre>`);
    }
    if (inList) htmlLines.push(`</${listType}>`);
    if (inTable) htmlLines.push("</tbody></table></div>");
    
    return htmlLines.join("\n");
}

// --- Modern Technical Document Reader & TOC Controller ---

function showNoteModalLoadingSpinner(topic) {
    const markdownContentEl = document.getElementById("modal-markdown-content") || document.getElementById("noteMainDocument");
    const tocContainer = document.getElementById("noteModalTOC");
    const wordEl = document.getElementById("noteWordCount");
    const timeEl = document.getElementById("noteReadingTime");
    
    if (wordEl) wordEl.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1 text-indigo-400"></i> Synthesizing...`;
    if (timeEl) timeEl.innerHTML = `<i class="fa-regular fa-clock mr-1 text-indigo-400"></i> Generating...`;

    if (tocContainer) {
        tocContainer.innerHTML = `
            <div class="animate-pulse space-y-2.5 p-2">
                <div class="h-3.5 bg-slate-800 rounded w-3/4"></div>
                <div class="h-3.5 bg-slate-800/60 rounded w-5/6 ml-2"></div>
                <div class="h-3.5 bg-slate-800/60 rounded w-2/3 ml-4"></div>
                <div class="h-3.5 bg-slate-800 rounded w-4/5"></div>
                <div class="h-3.5 bg-slate-800/60 rounded w-3/5 ml-2"></div>
            </div>
        `;
    }

    if (markdownContentEl) {
        markdownContentEl.innerHTML = `
            <div class="flex flex-col items-center justify-center py-20 px-4 text-center rounded-2xl border border-slate-700/60 my-6 bg-slate-800/40">
                <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent mb-4"></div>
                <h4 class="text-slate-100 text-base font-bold">Synthesizing Comprehensive Study Notes</h4>
                <p class="text-slate-400 text-xs mt-1.5 max-w-md leading-relaxed">
                    AI Academic Engine is generating verified syllabus notes, code implementations, complexity breakdown, and exam tips for <span class="text-indigo-400 font-semibold">"${topic}"</span>.
                </p>
            </div>
        `;
    }
}

function showNoteModalLoadingSkeleton(topic) {
    showNoteModalLoadingSpinner(topic);
}

function generateAcademicFallbackNotes(topic, subject) {
    const cleanTopic = (topic || "Academic Topic").trim();
    const cleanSubject = (subject || "Engineering & Computer Science").trim();
    const tLower = cleanTopic.toLowerCase();
    const sLower = cleanSubject.toLowerCase();
    const combined = `${tLower} ${sLower}`;

    const isEE = /circuit|kcl|kvl|thevenin|norton|kirchhoff|transistor|diode|bjt|mosfet|op-amp|rlc|transformer|induction motor/.test(combined);
    const isME = /thermodynamic|carnot|entropy|enthalpy|fluid|bernoulli|reynolds|stress|strain|otto|diesel/.test(combined);
    const isMath = /calculus|integral|derivative|differential equation|eigenvalue|eigenvector|matrix algebra|taylor series|fourier/.test(combined);

    if (isEE) {
        return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Electrical & Electronics Engineering | **Level:** B.Tech Undergraduate

**${cleanTopic}** is a fundamental theoretical and operational subject within Electrical Network Theory and Circuit Analysis. It establishes the governing laws for charge conservation, voltage loops, and electromagnetic energy distribution.

## Core Concepts & Mathematical / Architectural Linchpins
Electrical networks are governed by conservation laws derived directly from Maxwell's equations:

1. **Kirchhoff's Current Law (KCL - Charge Conservation)**:
$$\\sum_{k=1}^{N} I_k = 0$$
At any junction node in an electrical circuit, the algebraic sum of currents entering equals the sum of currents leaving.

2. **Kirchhoff's Voltage Law (KVL - Energy Conservation)**:
$$\\sum_{k=1}^{M} V_k = 0$$
The directed sum of electrical potential differences (voltages) around any closed loop equals zero.

3. **Thevenin's Equivalent & Maximum Power Transfer**:
$$I_L = \\frac{V_{\\text{th}}}{R_{\\text{th}} + R_L}, \\qquad P_{\\max} = \\frac{V_{\\text{th}}^2}{4 R_{\\text{th}}}$$

## Production-Grade Implementation & Boundary Validation
\`\`\`python
# Python Analysis: Thevenin Equivalent Calculator
def solve_thevenin(v_oc: float, r_th: float, r_load: float) -> dict:
    \"\"\"Computes circuit branch current, load voltage, and delivered power.\"\"\"
    if (r_th + r_load) <= 0:
        raise ValueError("Total circuit resistance must be strictly positive.")
    i_load = v_oc / (r_th + r_load)
    v_load = i_load * r_load
    p_load = (i_load ** 2) * r_load
    p_max = (v_oc ** 2) / (4 * r_th) if r_th > 0 else 0
    return {"I_load_A": i_load, "V_load_V": v_load, "P_load_W": p_load, "P_max_W": p_max}
\`\`\`

## Step-by-Step Solved Numericals & Circuit Traces
### Problem 1: Thevenin Equivalent Calculation
**Problem**: A DC network has $V_S = 24\\text{ V}$, series resistance $R_1 = 6\\,\\Omega$, and parallel resistor $R_2 = 12\\,\\Omega$ across load terminals $A-B$. Compute $V_{\\text{th}}$, $R_{\\text{th}}$, and load current $I_L$ for $R_L = 4\\,\\Omega$.
1. **Open-Circuit Voltage**: $V_{\\text{th}} = 24 \\times \\frac{12}{6 + 12} = 16\\text{ V}$.
2. **Thevenin Resistance**: $R_{\\text{th}} = R_1 \\parallel R_2 = \\frac{6 \\times 12}{6 + 12} = 4\\,\\Omega$.
3. **Load Current**: $I_L = \\frac{16\\text{ V}}{4\\,\\Omega + 4\\,\\Omega} = 2\\text{ A}$.

## Complexity Analysis & Asymptotic Matrix
| Component / Parameter | Governing Invariant | State Equation |
| :--- | :--- | :--- |
| **Resistive Network** | Ohm's Law | $V = I \\cdot R$ |
| **Inductive Storage** | Faraday's Law | $v(t) = L \\frac{di}{dt}$ |
| **Capacitive Storage** | Displacement Current | $i(t) = C \\frac{dv}{dt}$ |

## Real-World Pitfalls, Common Bugs & Exam Traps
1. Deactivating independent current sources as short circuits instead of open circuits.
2. Sign convention errors when traversing mesh loops against opposing current directions.
3. Forgetting source internal resistance in maximum power transfer computations.

## University Examination Practice Problems with Model Answers
1. **Q1: State Thevenin's Theorem.**
   - *Answer*: Any linear two-terminal DC circuit can be replaced by an equivalent voltage source $V_{\\text{th}}$ in series with resistance $R_{\\text{th}}$.
2. **Q2: Under what condition is maximum power transferred to a load in a DC circuit?**
   - *Answer*: When the load resistance equals the internal Thevenin resistance ($R_L = R_{\\text{th}}$).
3. **Q3: State Kirchhoff's Current Law and its physical basis.**
   - *Answer*: $\\sum I = 0$ at any circuit junction; physically based on conservation of electric charge.`;
    }

    if (isME) {
        return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Mechanical Engineering | **Level:** B.Tech Undergraduate

**${cleanTopic}** is a core operational discipline within thermal systems, fluid mechanics, and mechanical engineering. It governs macroscopic work extraction, heat transfer, and mechanical equilibrium.

## Core Concepts & Mathematical / Architectural Linchpins
1. **First Law of Thermodynamics (Conservation of Energy)**:
$$dQ = dU + dW \\implies \\Delta U = Q - W$$
For an ideal gas, work done during quasi-static expansion is $W = \\int P \\, dV$.

2. **Second Law & Carnot Maximum Thermal Efficiency**:
$$\\eta_{\\text{Carnot}} = 1 - \\frac{T_L}{T_H} = \\frac{T_H - T_L}{T_H}$$
where $T_H$ and $T_L$ represent source and sink temperatures in absolute Kelvin ($\\text{K}$).

3. **Bernoulli's Equation (Incompressible Fluid Flow)**:
$$P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{Constant}$$

## Step-by-Step Solved Numericals & Thermodynamic Traces
### Problem 1: Carnot Cycle Thermal Efficiency Calculation
**Problem**: A heat engine operates between $T_H = 600^\\circ\\text{C}$ and $T_L = 30^\\circ\\text{C}$, absorbing $1200\\text{ kJ}$ heat per cycle. Compute thermal efficiency $\\eta$ and net work output $W_{\\text{net}}$.
1. **Convert to Kelvin**: $T_H = 600 + 273.15 = 873.15\\text{ K}$, $T_L = 30 + 273.15 = 303.15\\text{ K}$.
2. **Carnot Efficiency**: $\\eta = 1 - \\frac{303.15}{873.15} = 0.6528 \\implies 65.28\\%$.
3. **Net Work Output**: $W_{\\text{net}} = 0.6528 \\times 1200\\text{ kJ} = 783.36\\text{ kJ}$.

## Real-World Pitfalls, Common Bugs & Exam Traps
1. Forgetting to convert Celsius to Kelvin ($\\text{K} = ^\\circ\\text{C} + 273.15$).
2. Confusing gauge pressure with absolute pressure ($P_{\\text{abs}} = P_{\\text{gauge}} + P_{\\text{atm}}$).
3. Violating thermodynamic sign conventions for heat supplied vs heat rejected.

## University Examination Practice Problems with Model Answers
1. **Q1: State the Kelvin-Planck statement of the Second Law of Thermodynamics.**
   - *Answer*: It is impossible for any device operating on a cycle to receive heat from a single thermal reservoir and produce a net amount of work.
2. **Q2: State Bernoulli's equation assumptions.**
   - *Answer*: Inviscid, steady, incompressible, and irrotational flow along a streamline.
3. **Q3: What is the efficiency of a reversible engine operating with equal source and sink temperatures?**
   - *Answer*: $\\eta = 0$, since $T_H = T_L$.`;
    }

    if (isMath) {
        return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Engineering Mathematics | **Level:** B.Tech Undergraduate

**${cleanTopic}** provides the analytical foundations required to model multi-dimensional dynamical, structural, and computational engineering systems.

## Core Concepts & Mathematical / Architectural Linchpins
1. **Characteristic Equation & Matrix Eigenvalues**:
$$\\det(A - \\lambda I) = 0$$
For an $n \\times n$ matrix $A$, the roots of this polynomial yield eigenvalues $\\lambda_1, \\dots, \\lambda_n$.

2. **Cayley-Hamilton Theorem**:
Every square matrix satisfies its own characteristic equation:
$$p(A) = A^n + c_{n-1}A^{n-1} + \\dots + c_0 I = 0$$

3. **Exact Differential Equation Criterion**:
$$M(x, y)\\,dx + N(x, y)\\,dy = 0 \\iff \\frac{\\partial M}{\\partial y} = \\frac{\\partial N}{\\partial x}$$

## Step-by-Step Solved Numericals & Analytical Derivations
### Problem 1: Eigenvalues and Eigenvectors of a $2 \\times 2$ Matrix
**Problem**: Find eigenvalues of $A = \\begin{bmatrix} 4 & 1 \\\\ 2 & 3 \\end{bmatrix}$.
1. **Characteristic Equation**: $\\det(A - \\lambda I) = (4 - \\lambda)(3 - \\lambda) - 2 = \\lambda^2 - 7\\lambda + 10 = 0$.
2. **Factoring**: $(\\lambda - 5)(\\lambda - 2) = 0 \\implies \\lambda_1 = 5, \\lambda_2 = 2$.
3. **Eigenvector for $\\lambda = 5$**: $(A - 5I)\\mathbf{v} = \\begin{bmatrix} -1 & 1 \\\\ 2 & -2 \\end{bmatrix} \\begin{bmatrix} x_1 \\\\ x_2 \\end{bmatrix} = 0 \\implies \\mathbf{v}_1 = \\begin{bmatrix} 1 \\\\ 1 \\end{bmatrix}$.

## Real-World Pitfalls, Common Bugs & Exam Traps
1. Failing to test for exactness before integrating differential forms.
2. Determinant sign errors during expansion of $3 \\times 3$ matrices.
3. Confusing linear independence with orthogonality.

## University Examination Practice Problems with Model Answers
1. **Q1: State the Cayley-Hamilton Theorem.**
   - *Answer*: Every square matrix satisfies its own characteristic polynomial equation.
2. **Q2: State the relation between trace and eigenvalues.**
   - *Answer*: $\\text{Trace}(A) = \\sum_{i=1}^n \\lambda_i$.
3. **Q3: What is the condition for exactness in $M dx + N dy = 0$?**
   - *Answer*: $\\frac{\\partial M}{\\partial y} = \\frac{\\partial N}{\\partial x}$.`;
    }

    // Default Computer Science / Data Structures / Algorithms realistic template
    const isArray = /array|matrix|vector/.test(tLower);
    const isList = /list|linked|pointer/.test(tLower);
    const isTree = /tree|bst|avl|heap/.test(tLower);
    const isHash = /hash/.test(tLower);

    let mathSection = "";
    let codeSection = "";
    let workedProblem = "";

    if (isArray) {
        mathSection = `### 1. Memory Representation & Address Arithmetic
In computer memory, an array stores elements at contiguous physical memory addresses. The memory address of any element is calculated algebraically in constant $\\mathcal{O}(1)$ time:

- **1D Array Address Formula**:
$$\\text{Address}(A[i]) = \\text{BaseAddress} + (i - \\text{LowerBound}) \\times w$$
where $w$ is the element width in bytes (e.g., $w = 4$ for 32-bit integers).

- **2D Row-Major Order (RMO - C/Python)**:
$$\\text{Address}(A[i][j]) = \\text{BaseAddress} + \\Big[ (i - \\text{LB}_r) \\times N_c + (j - \\text{LB}_c) \\Big] \\times w$$

- **2D Column-Major Order (CMO - Fortran/MATLAB)**:
$$\\text{Address}(A[i][j]) = \\text{BaseAddress} + \\Big[ (j - \\text{LB}_c) \\times N_r + (i - \\text{LB}_r) \\Big] \\times w$$`;

        codeSection = `\`\`\`python
# Production Python: Dynamic Vector Array with Binary Search
class DynamicArray:
    def __init__(self, capacity: int = 8):
        self.capacity = capacity
        self.data = [0] * capacity
        self.size = 0

    def append(self, value: int) -> None:
        if self.size >= self.capacity:
            self.capacity *= 2
            resized = [0] * self.capacity
            for i in range(self.size):
                resized[i] = self.data[i]
            self.data = resized
        self.data[self.size] = value
        self.size += 1

    def binary_search(self, target: int) -> int:
        low, high = 0, self.size - 1
        while low <= high:
            mid = low + (high - low) // 2
            if self.data[mid] == target:
                return mid
            elif self.data[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        return -1
\`\`\``;

        workedProblem = `### Problem 1: 2D Array Address Derivation
**Problem**: An array $A[-5 \\dots 15, 10 \\dots 30]$ has Base Address $1020$ and element size $w = 4$ bytes. Compute $\\text{Address}(A[5][20])$ in Row-Major Order.
1. **Dimensions**: $N_r = 15 - (-5) + 1 = 21$, $N_c = 30 - 10 + 1 = 21$.
2. **Offset Calculation**: $(5 - (-5)) \\times 21 + (20 - 10) = 10 \\times 21 + 10 = 220$.
3. **Final Address**: $1020 + (220 \\times 4) = 1020 + 880 = 1900$.`;
    } else if (isList) {
        mathSection = `### 1. Pointer Invariants & Cycle Detection
A Linked List is a collection of dynamic heap-allocated nodes connected via pointer addresses:

- **Node Structure**:
$$\\text{Node} = \\langle \\text{Data}, \\quad \\text{NextPointer} \\in \\text{AddressSpace} \\cup \\{\\text{NULL}\\} \\rangle$$

- **Floyd's Tortoise & Hare Cycle Invariant**:
$$\\text{Time Complexity} = \\mathcal{O}(n), \\qquad \\text{Auxiliary Space} = \\mathcal{O}(1)$$`;

        codeSection = `\`\`\`python
# Production Python: Singly Linked List Reversal
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_linked_list(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev
\`\`\``;

        workedProblem = `### Problem 1: Linked List In-Place Reversal Trace
Given list $10 \\to 20 \\to 30 \\to \\text{NULL}$:
- Iteration 1: $10\\to\\text{NULL}$, \`prev=10\`, \`curr=20\`
- Iteration 2: $20\\to 10\\to\\text{NULL}$, \`prev=20\`, \`curr=30\`
- Iteration 3: $30\\to 20\\to 10\\to\\text{NULL}$, \`prev=30\`, \`curr=NULL\`
Final reversed list head: $30$ in $\\mathcal{O}(n)$ time and $\\mathcal{O}(1)$ space.`;
    } else {
        mathSection = `### 1. Algorithmic Invariants & Recurrence Relations
The operational behavior of **${cleanTopic}** is defined by asymptotic complexity and state invariants:

- **Master Theorem Recurrence Form**:
$$T(n) = a \\, T\\left(\\frac{n}{b}\\right) + f(n)$$
- **Algorithmic Bounds**:
$$\\mathcal{O}(1) \\le \\text{Optimal State} \\le \\mathcal{O}(n \\log n)$$`;

        codeSection = `\`\`\`python
# Production Python: Core Implementation for ${cleanTopic}
class ${cleanTopic.replace(/[^a-zA-Z0-9]/g, '') || "Engine"}:
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.items = []

    def insert(self, item) -> bool:
        if item is None or len(self.items) >= self.capacity:
            return False
        self.items.append(item)
        return True

    def find(self, target) -> int:
        for idx, val in enumerate(self.items):
            if val == target:
                return idx
        return -1
\`\`\``;

        workedProblem = `### Problem 1: Asymptotic Recurrence Solution
**Problem**: Solve $T(n) = 2T(n/2) + \\Theta(n)$.
1. $a = 2, b = 2, f(n) = \\Theta(n^1)$.
2. $\\log_b a = \\log_2 2 = 1 \\implies n^{\\log_b a} = n^1 = f(n)$.
3. Case 2 of Master Theorem applies $\\implies T(n) = \\Theta(n \\log n)$.`;
    }

    return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Computer Science & Engineering | **Level:** B.Tech Undergraduate

**${cleanTopic}** constitutes a core conceptual and algorithmic foundation in modern Computer Science and Engineering. Mastering this topic provides the structural basis for high-throughput software architecture, memory optimization, and university end-semester examinations.

## Core Concepts & Mathematical / Architectural Linchpins
${mathSection}

## Physical Memory Layout & Structural Representation
1. **Memory Allocation**: Managed in contiguous physical memory buffers or heap-allocated pointer chains to guarantee deterministic execution invariants.
2. **Cache Locality**: Exploits CPU L1/L2 cache line spatial locality to maximize memory bus throughput.
3. **Pointer Arithmetic**: Guarantees boundary safety and eliminates memory corruption.

## Production-Grade Implementation & Boundary Validation
${codeSection}

## Step-by-Step Solved Numericals & Algorithmic Traces
${workedProblem}

## Complexity Analysis & Asymptotic Matrix
| Operation / Stage | Best Case | Average Case | Worst Case | Auxiliary Space |
| :--- | :--- | :--- | :--- | :--- |
| **Lookup / Random Access** | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |
| **Insertion at Boundary** | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ amortized | $\\mathcal{O}(n)$ shifting | $\\mathcal{O}(1)$ |
| **Arbitrary Search** | $\\mathcal{O}(1)$ | $\\mathcal{O}(\\log n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |
| **Full Traversal** | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |

## Real-World Pitfalls, Common Bugs & Exam Traps
1. **Off-by-One Index Errors**: Loop boundary inaccuracies producing segmentation faults or buffer overflows.
2. **Unchecked Null/Dangling Pointers**: Dereferencing deallocated or uninitialized memory addresses.
3. **Capacity Overflow**: Failing to verify memory allocation bounds before inserting elements.

## University Examination Practice Problems with Model Answers
1. **Q1: Define ${cleanTopic} in Computer Science.**
   - *Answer*: A foundational structure or computational methodology that models data and operational workflows under deterministic time and space bounds.
2. **Q2: Why is random access in an array performed in $\\mathcal{O}(1)$ time?**
   - *Answer*: Because physical memory addresses are calculated directly via index arithmetic without sequential element traversal.
3. **Q3: State the worst-case time complexity of Binary Search.**
   - *Answer*: $\\mathcal{O}(\\log n)$ by repeatedly halving the active search interval.`;
}


function parseMarkdownHeaders(rawContent) {
    if (!rawContent) return [];
    const headers = [];
    const lines = rawContent.split("\n");
    let inCodeBlock = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith("```")) {
            inCodeBlock = !inCodeBlock;
            continue;
        }
        if (inCodeBlock) continue;
        
        const match = line.match(/^(#{1,4})\s+(.+)$/);
        if (match) {
            const level = match[1].length;
            const rawTitle = match[2].trim();
            const cleanTitle = stripMarkdownSymbols(rawTitle).trim();
            if (cleanTitle) {
                headers.push({ level, title: cleanTitle });
            }
        }
    }
    return headers;
}

function renderDefaultTableOfContents(tocContainer, container) {
    const defaultSections = [
        { title: "Executive Overview", icon: "fa-solid fa-book-open", keywords: ["overview", "introduction", "definition", "about"] },
        { title: "Key Concepts & Theory", icon: "fa-solid fa-layer-group", keywords: ["concept", "theory", "theoretical", "foundations", "principles"] },
        { title: "Syntax & Implementation", icon: "fa-solid fa-code", keywords: ["syntax", "implementation", "code", "example", "program"] },
        { title: "Complexity Breakdown", icon: "fa-solid fa-gauge-high", keywords: ["complexity", "time", "space", "big-o", "matrix"] },
        { title: "Common Pitfalls & Edge Cases", icon: "fa-solid fa-triangle-exclamation", keywords: ["pitfall", "common", "edge", "cases", "error", "mistake"] },
        { title: "University Exam Tips", icon: "fa-solid fa-graduation-cap", keywords: ["exam", "interview", "questions", "tips", "derivation", "syllabus"] }
    ];

    const children = container ? Array.from(container.children) : [];
    
    let tocHtml = '<nav class="space-y-1">';
    defaultSections.forEach((sec, idx) => {
        const id = `note-default-sec-${idx}`;
        let matchedEl = null;

        // Match paragraph or section containing keywords
        if (children.length > 0) {
            for (let child of children) {
                const text = child.textContent.toLowerCase();
                if (sec.keywords.some(k => text.includes(k))) {
                    matchedEl = child;
                    break;
                }
            }
            if (!matchedEl) {
                const childIdx = Math.min(children.length - 1, Math.floor((idx / defaultSections.length) * children.length));
                matchedEl = children[childIdx];
            }
        }

        if (matchedEl && !matchedEl.id) {
            matchedEl.id = id;
        } else if (container && !document.getElementById(id)) {
            const anchor = document.createElement("div");
            anchor.id = id;
            anchor.className = "h-0 w-0 overflow-hidden";
            container.appendChild(anchor);
        }

        tocHtml += `
            <a href="#${id}" onclick="scrollToNoteSection(event, '${id}')" class="toc-nav-item pl-2 text-xs font-semibold">
                <i class="${sec.icon} text-[10px] mr-2 text-indigo-500"></i>
                <span class="truncate">${sec.title}</span>
            </a>
        `;
    });
    tocHtml += '</nav>';
    tocContainer.innerHTML = tocHtml;
}

function buildTableOfContents(container, rawContent = "") {
    const tocContainer = document.getElementById("noteModalTOC");
    if (!tocContainer) return;

    // Clear any previous loading or stale content
    tocContainer.innerHTML = "";

    // 1. Check DOM headings inside the container
    let headings = container ? Array.from(container.querySelectorAll("h1, h2, h3, h4")) : [];

    // 2. If no DOM headings found, try parsing from rawContent
    if (headings.length === 0 && rawContent) {
        const parsedHeaders = parseMarkdownHeaders(rawContent);
        if (parsedHeaders.length > 0 && container) {
            headings = Array.from(container.querySelectorAll("h1, h2, h3, h4"));
        }
    }

    // 3. If still no headings found, fall back to default structured academic sections
    if (headings.length === 0) {
        renderDefaultTableOfContents(tocContainer, container);
        setupTOCScrollSpy();
        return;
    }

    // 4. Render headings into TOC nav
    let tocHtml = '<nav class="space-y-1">';
    headings.forEach((heading, idx) => {
        const id = `note-sec-${idx}`;
        heading.id = id;

        const tag = heading.tagName.toLowerCase();
        let indentClass = 'pl-2 text-xs font-semibold';
        let icon = '<i class="fa-solid fa-bookmark text-[10px] mr-1.5 text-indigo-400"></i>';

        if (tag === 'h1') {
            indentClass = 'pl-1 text-xs font-bold text-slate-100';
            icon = '<i class="fa-solid fa-bookmark text-[10px] mr-1.5 text-indigo-400"></i>';
        } else if (tag === 'h2') {
            indentClass = 'pl-2.5 text-xs font-semibold text-slate-200';
            icon = '<i class="fa-solid fa-layer-group text-[10px] mr-1.5 text-indigo-400"></i>';
        } else if (tag === 'h3') {
            indentClass = 'pl-5 text-[11px] text-slate-300';
            icon = '<i class="fa-solid fa-angle-right text-[9px] mr-1.5 text-indigo-400"></i>';
        } else if (tag === 'h4') {
            indentClass = 'pl-7 text-[10px] text-slate-400';
            icon = '<i class="fa-solid fa-circle text-[6px] mr-1.5 text-indigo-300"></i>';
        }

        const rawText = heading.textContent || "";
        const cleanTitle = stripMarkdownSymbols(rawText).replace(/^[\d\.\s]+/, '').trim() || rawText.trim();

        tocHtml += `
            <a href="#${id}" onclick="scrollToNoteSection(event, '${id}')" class="toc-nav-item ${indentClass}">
                ${icon}
                <span class="truncate">${cleanTitle}</span>
            </a>
        `;
    });
    tocHtml += '</nav>';
    tocContainer.innerHTML = tocHtml;
    setupTOCScrollSpy();
}

let isTOCScrolling = false;
function setupTOCScrollSpy() {
    const scrollContainer = document.getElementById("noteMainDocumentScroll");
    if (!scrollContainer || scrollContainer._hasScrollSpy) return;
    scrollContainer._hasScrollSpy = true;

    scrollContainer.addEventListener("scroll", () => {
        if (isTOCScrolling) return;
        const targets = document.querySelectorAll("#modal-markdown-content h1, #modal-markdown-content h2, #modal-markdown-content h3, #modal-markdown-content [id^='note-default-sec-']");
        const containerRect = scrollContainer.getBoundingClientRect();
        
        let currentActiveId = null;
        targets.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.top - containerRect.top <= 120) {
                currentActiveId = el.id;
            }
        });

        if (currentActiveId) {
            document.querySelectorAll("#noteModalTOC a").forEach(a => {
                if (a.getAttribute("href") === `#${currentActiveId}`) {
                    a.classList.add("active");
                } else {
                    a.classList.remove("active");
                }
            });
        }
    }, { passive: true });
}

function scrollToNoteSection(event, sectionId) {
    if (event) event.preventDefault();
    const targetEl = document.getElementById(sectionId);
    const scrollContainer = document.getElementById("noteMainDocumentScroll");
    if (targetEl && scrollContainer) {
        isTOCScrolling = true;
        const targetRect = targetEl.getBoundingClientRect();
        const containerRect = scrollContainer.getBoundingClientRect();
        const targetScrollTop = scrollContainer.scrollTop + (targetRect.top - containerRect.top) - 16;
        scrollContainer.scrollTo({ top: Math.max(0, targetScrollTop), behavior: "smooth" });

        document.querySelectorAll("#noteModalTOC a").forEach(a => a.classList.remove("active"));
        if (event && event.currentTarget) {
            event.currentTarget.classList.add("active");
        }
        setTimeout(() => { isTOCScrolling = false; }, 800);
    }
}

// Sanitizes unwanted ASCII artifacts, decorative borders, and redundant plaintext headers
function sanitizeStudyNotesContent(raw) {
    if (!raw) return "";
    let text = String(raw);

    // 1. Strip raw ASCII decorative borders (===, ---, ___, ~~~, etc.)
    text = text.replace(/^[=\-~_#*]{4,}\s*$/gm, '');
    text = text.replace(/[=\-]{10,}/g, '');

    // 2. Remove redundant plaintext header blocks from modal body:
    // e.g. "STUDY NOTES: PYTHON", "LECTURE NOTE: ...", "Subject: ...", "Date Synthesized: ...", "Author: ..."
    text = text.replace(/^(#+\s*)?(STUDY NOTES|HANDWRITTEN[A-Z\s]*NOTES|LECTURE\s+NOTES?)[:\s].*$/gmi, '');
    text = text.replace(/^>*\s*\*{0,2}(Academic\s+)?Subject\*{0,2}[:\s].*$/gmi, '');
    text = text.replace(/^>*\s*\*{0,2}(Date\s+)?Synthesized\*{0,2}[:\s].*$/gmi, '');
    text = text.replace(/^>*\s*\*{0,2}Author\*{0,2}[:\s].*$/gmi, '');
    text = text.replace(/^>*\s*\*{0,2}Source\*{0,2}[:\s].*$/gmi, '');
    text = text.replace(/^>*\s*\*{0,2}Topic\*{0,2}[:\s].*$/gmi, '');

    // 3. Ensure content starts cleanly with # Executive Overview
    text = text.trim();
    const execMatch = text.match(/(#+\s*Executive Overview[\s\S]*)/i);
    if (execMatch) {
        text = execMatch[1].replace(/^#+\s*Executive Overview/i, '# Executive Overview');
    } else {
        if (!text.startsWith("#")) {
            text = `# Executive Overview\n\n${text}`;
        }
    }

    // 4. Clean up multiple empty lines
    text = text.replace(/\n{3,}/g, '\n\n').trim();
    return text;
}
window.sanitizeStudyNotesContent = sanitizeStudyNotesContent;

function applyKaTeXToElement(container) {
    if (!container) return;
    if (typeof renderMathInElement === "function") {
        try {
            renderMathInElement(container, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false },
                    { left: '\\(', right: '\\)', display: false },
                    { left: '\\[', right: '\\]', display: true }
                ],
                throwOnError: false,
                ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
            });
        } catch (err) {
            console.warn("KaTeX rendering warning:", err);
        }
    } else {
        const checkKaTeXInterval = setInterval(() => {
            if (typeof renderMathInElement === "function") {
                clearInterval(checkKaTeXInterval);
                applyKaTeXToElement(container);
            }
        }, 100);
        setTimeout(() => clearInterval(checkKaTeXInterval), 3000);
    }
}
window.applyKaTeXToElement = applyKaTeXToElement;

// Re-typeset raw LaTeX math strings into formatted mathematical equations using KaTeX and MathJax 3
function renderMathFormulas(elements) {
    const targets = elements ? (Array.isArray(elements) ? elements : [elements]) : [document.body];
    
    // 1. Instant rendering with KaTeX
    targets.forEach(el => {
        if (el) applyKaTeXToElement(el);
    });

    // 2. Typeset with MathJax 3 for full TeX coverage
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        const mathJaxTargets = elements ? (Array.isArray(elements) ? elements : [elements]) : undefined;
        window.MathJax.typesetPromise(mathJaxTargets).catch((err) => console.warn("MathJax error:", err));
    } else if (window.MathJax && typeof window.MathJax.typeset === 'function') {
        try {
            if (elements) {
                window.MathJax.typeset(Array.isArray(elements) ? elements : [elements]);
            } else {
                window.MathJax.typeset();
            }
        } catch (err) {
            console.warn("MathJax typeset error:", err);
        }
    }
}
window.renderMathFormulas = renderMathFormulas;

function renderNoteDocumentContent(content) {
    const cleanContent = sanitizeStudyNotesContent(content);
    const markdownContentEl = document.getElementById("modal-markdown-content") || document.getElementById("noteMainDocument");
    if (markdownContentEl) {
        let html = "";
        if (typeof marked !== 'undefined') {
            if (typeof marked.parse === 'function') {
                try {
                    marked.setOptions({ gfm: true, breaks: true });
                    html = marked.parse(cleanContent);
                } catch (e) {
                    html = renderMarkdownToHtml(cleanContent);
                }
            } else if (typeof marked === 'function') {
                html = marked(cleanContent);
            }
        }
        if (!html) {
            html = renderMarkdownToHtml(cleanContent);
        }
        markdownContentEl.innerHTML = html;
        applyKaTeXToElement(markdownContentEl);
        renderMathFormulas(markdownContentEl);
        buildTableOfContents(markdownContentEl, cleanContent);
    }

    // Reading statistics
    const wordList = cleanContent.trim().split(/\s+/).filter(Boolean);
    const wordCount = wordList.length;
    const readTime = Math.max(1, Math.ceil(wordCount / 185));

    const wordEl = document.getElementById("noteWordCount");
    if (wordEl) wordEl.innerHTML = `<i class="fa-solid fa-file-lines mr-1 text-indigo-400"></i> ${wordCount} words`;

    const timeEl = document.getElementById("noteReadingTime");
    if (timeEl) timeEl.innerHTML = `<i class="fa-regular fa-clock mr-1 text-indigo-400"></i> ~${readTime} min read`;
}

function openStudyNotesModal(note) {
    if (!note) {
        if (currentSearchData && currentSearchData.notes && currentSearchData.notes.length > 0) {
            note = currentSearchData.notes[0];
        } else {
            const topicTitle = (currentSearchData && (currentSearchData.title || currentSearchData.query)) || currentQuery || "Academic Topic";
            note = {
                title: `Study Notes: ${topicTitle}`,
                subject: (currentSearchData && (currentSearchData.category || currentSearchData.domain)) || "Academic Curriculum",
                uploaded_by: "OmniLearn AI Academic Engine",
                file_path: "",
                ocr_text: studyNotes || ""
            };
        }
    }
    return openNoteModal(note);
}
window.openStudyNotesModal = openStudyNotesModal;

async function openNoteModal(note) {
    const activeData = currentSearchData || {};
    const activeTopic = activeData.title || activeData.query || (note && note.title ? note.title.replace(/^Study Notes:\s*/i, '') : currentQuery) || "Academic Topic";

    if (!note) {
        note = {
            title: `Study Notes: ${activeTopic}`,
            subject: activeData.category || activeData.domain || "Academic Curriculum",
            uploaded_by: "OmniLearn AI Academic Engine",
            file_path: ""
        };
    }
    currentNote = note;

    // 1. Dynamic Header Title & Badges
    const titleEl = document.getElementById("noteModalTitle");
    if (titleEl) {
        titleEl.textContent = note.title ? (note.title.startsWith("Study Notes:") ? note.title : `Study Notes: ${note.title}`) : `Study Notes: ${activeTopic}`;
    }

    const badgeEl = document.getElementById("noteModalSubjectBadge");
    if (badgeEl) {
        badgeEl.textContent = note.subject || activeData.domain || activeData.category || "Academic Curriculum";
    }

    const metaEl = document.getElementById("noteModalMeta");
    if (metaEl) {
        metaEl.innerHTML = `<i class="fa-regular fa-user mr-1 text-slate-400"></i>${note.uploaded_by || 'OmniLearn AI Academic Engine'} | Comprehensive University Syllabus Revision`;
    }

    // Configure "View File" action button in modal header
    const viewFileBtn = document.getElementById("viewOriginalFileBtn");
    if (viewFileBtn) {
        if (note.file_path) {
            viewFileBtn.href = `/api/notes/file/${encodeURIComponent(note.file_path)}`;
            viewFileBtn.classList.remove("hidden");
        } else {
            viewFileBtn.classList.add("hidden");
        }
    }

    // Reset search input & bookmark status
    const searchInput = document.getElementById("modalTextSearchInput");
    if (searchInput) searchInput.value = "";
    updateNoteModalBookmarkButton();

    // 2. Show Modal Immediately
    const modalEl = document.getElementById("noteDetailModal");
    if (modalEl) modalEl.classList.remove("hidden");

    // 3. If API data is currently loading and no specific note content exists, show spinner and auto-resolve
    if (isSearching && !note.ocr_text && !note.file_path) {
        showNoteModalLoadingSpinner(activeTopic);
        const checkInterval = setInterval(() => {
            if (!isSearching || (currentSearchData && (currentSearchData.study_notes || currentSearchData.notes))) {
                clearInterval(checkInterval);
                openNoteModal(note);
            }
        }, 300);
        setTimeout(() => {
            clearInterval(checkInterval);
            const contentEl = document.getElementById("modal-markdown-content");
            if (contentEl && contentEl.innerHTML.includes("Synthesizing")) {
                const fb = generateAcademicFallbackNotes(activeTopic, note.subject);
                renderNoteDocumentContent(fb);
                renderMathFormulas();
            }
        }, 3500);
        return;
    }

    // 4. Resolve notes content: prioritize specific note content if card was clicked
    let notesContent = "";
    if (note.ocr_text && note.ocr_text.trim()) {
        notesContent = note.ocr_text;
    } else if (note.file_path) {
        try {
            showNoteModalLoadingSpinner(note.title || activeTopic);
            const resp = await fetch(`/api/notes/file/${encodeURIComponent(note.file_path)}`);
            if (resp.ok) {
                notesContent = await resp.text();
                note.ocr_text = notesContent;
            }
        } catch (err) {
            console.error("Failed to load note file content:", err);
        }
    }

    if (!notesContent || !notesContent.trim()) {
        notesContent = activeData.notesContent || activeData.studyNotes || activeData.study_notes || activeData.notes_content || studyNotes || "";
    }

    if (!notesContent || !notesContent.trim()) {
        try {
            const stored = sessionStorage.getItem("omni_study_notes");
            if (stored && stored.trim()) notesContent = stored.trim();
        } catch (e) {}
    }

    if (!notesContent || !notesContent.trim()) {
        notesContent = generateAcademicFallbackNotes(activeTopic, note.subject);
        studyNotes = notesContent;
        try { sessionStorage.setItem("omni_study_notes", notesContent); } catch(e) {}
    }

    // 5. Directly inject dynamic Markdown HTML into #modal-markdown-content
    renderNoteDocumentContent(notesContent);
    renderMathFormulas();
}

function closeNoteModal() {
    document.getElementById("noteDetailModal").classList.add("hidden");
    currentNote = null;
}

function updateNoteModalBookmarkButton() {
    const btn = document.getElementById("bookmarkNoteBtn");
    if (!btn || !currentNote) return;
    
    const isBookmarked = bookmarks.some(b => b.item_type === "note" && b.item_id === currentNote.id);
    
    if (isBookmarked) {
        btn.innerHTML = `<i class="fa-solid fa-bookmark text-base text-yellow-500"></i>`;
    } else {
        btn.innerHTML = `<i class="fa-regular fa-bookmark text-base text-slate-400"></i>`;
    }
}

async function toggleNoteBookmarkFromModal() {
    if (!currentNote) return;
    
    const existing = bookmarks.find(b => b.item_type === "note" && b.item_id === currentNote.id);
    
    if (existing) {
        await removeBookmark(existing.id);
    } else {
        try {
            const response = await fetch("/api/bookmarks", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    item_type: "note",
                    item_id: currentNote.id,
                    title: currentNote.title
                })
            });
            if (response.ok) {
                await fetchBookmarks();
                updateNoteModalBookmarkButton();
            }
        } catch (e) {
            console.error(e);
        }
    }
}

// Complete note export supporting untruncated TXT and PDF
function downloadCurrentNote(format = 'txt') {
    if (!currentNote) return;
    
    const activeData = currentSearchData || {};
    const activeTopic = activeData.title || activeData.query || (currentNote.title ? currentNote.title.replace(/^Study Notes:\s*/i, '') : "study_notes");
    let notesContent = (currentNote && currentNote.ocr_text) || activeData.notesContent || activeData.studyNotes || activeData.study_notes || activeData.notes_content || studyNotes || "";
    if (!notesContent || !notesContent.trim()) {
        notesContent = generateAcademicFallbackNotes(activeTopic, currentNote.subject);
    }
    const cleanTitle = (currentNote.title || `Study_Notes_${activeTopic}`).replace(/[^a-zA-Z0-9_\-]/g, '_');

    if (format === 'txt') {
        // Direct download of complete untruncated markdown notes
        const blob = new Blob([notesContent], { type: "text/markdown;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${cleanTitle}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    } else if (format === 'pdf') {
        // Open clean styled printable window for complete PDF export
        const printWindow = window.open('', '_blank', 'width=850,height=900');
        if (!printWindow) {
            alert("Please allow popups in your browser to export notes as PDF.");
            return;
        }
        let renderedHtml = "";
        if (typeof marked !== 'undefined') {
            if (typeof marked.parse === 'function') {
                try {
                    renderedHtml = marked.parse(notesContent);
                } catch(e) {
                    renderedHtml = renderMarkdownToHtml(notesContent);
                }
            } else if (typeof marked === 'function') {
                renderedHtml = marked(notesContent);
            }
        }
        if (!renderedHtml) renderedHtml = renderMarkdownToHtml(notesContent);

        printWindow.document.write(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>${currentNote.title || `Study Notes: ${activeTopic}`}</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
                <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
                <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
                <style>
                    @media print {
                        body { padding: 15px; }
                        .no-print { display: none !important; }
                    }
                    body { font-family: system-ui, -apple-system, sans-serif; color: #0f172a; padding: 40px; max-width: 850px; margin: 0 auto; line-height: 1.8; font-size: 16px; }
                    table { border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; }
                    th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }
                    th { background-color: #f1f5f9; font-weight: 700; }
                    pre { background-color: #0f172a; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; font-family: monospace; font-size: 13px; line-height: 1.5; }
                    code { font-family: monospace; font-size: 13px; }
                    .katex-display { margin: 1rem 0; overflow-x: auto; overflow-y: hidden; }
                </style>
            </head>
            <body>
                <div class="mb-6 pb-4 border-b border-slate-200">
                    <h1 class="text-2xl font-bold text-slate-900">${currentNote.title || `Study Notes: ${activeTopic}`}</h1>
                    <p class="text-xs text-slate-500 mt-1">Subject: ${currentNote.subject || 'Academic'} | Author: ${currentNote.uploaded_by || 'OmniLearn'} | OmniLearn Academic Study Resource</p>
                </div>
                <div class="prose max-w-none text-base space-y-4" id="printDocContent">
                    ${renderedHtml}
                </div>
                <script>
                    window.onload = function() {
                        if (typeof renderMathInElement === "function") {
                            renderMathInElement(document.getElementById("printDocContent"), {
                                delimiters: [
                                    { left: '$$', right: '$$', display: true },
                                    { left: '$', right: '$', display: false },
                                    { left: '\\\\(', right: '\\\\)', display: false },
                                    { left: '\\\\[', right: '\\\\]', display: true }
                                ],
                                throwOnError: false
                            });
                        }
                        setTimeout(() => {
                            window.print();
                        }, 500);
                    };
                </script>
            </body>
            </html>
        `);
        printWindow.document.close();
    }
}

// Highlights search occurrences on modal text blocks preserving markdown formatting
function highlightModalText() {
    const searchVal = document.getElementById("modalTextSearchInput").value.trim();
    const markdownContentEl = document.getElementById("modal-markdown-content") || document.getElementById("noteMainDocument");
    if (!currentNote || !markdownContentEl) return;
    
    const activeData = currentSearchData || {};
    const activeTopic = activeData.title || activeData.query || (currentNote.title ? currentNote.title.replace(/^Study Notes:\s*/i, '') : "Topic");
    let notesContent = activeData.notesContent || activeData.studyNotes || activeData.study_notes || activeData.notes_content || studyNotes || (currentNote && currentNote.ocr_text) || "";
    if (!notesContent || !notesContent.trim()) {
        notesContent = generateAcademicFallbackNotes(activeTopic, currentNote.subject);
    }
    
    if (!searchVal) {
        renderNoteDocumentContent(notesContent);
        return;
    }
    
    // Safely inject highlight markers before markdown compilation
    const escapedVal = searchVal.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    const regex = new RegExp(`(${escapedVal})`, 'gi');
    
    const markedText = notesContent.replace(regex, '==OMNI_HL==$1==OMNI_ENDHL==');
    let renderedHtml = "";
    if (typeof marked !== 'undefined') {
        if (typeof marked.parse === 'function') {
            try {
                marked.setOptions({ gfm: true, breaks: true });
                renderedHtml = marked.parse(markedText);
            } catch(e) {
                renderedHtml = renderMarkdownToHtml(markedText);
            }
        } else if (typeof marked === 'function') {
            renderedHtml = marked(markedText);
        }
    }
    if (!renderedHtml) {
        renderedHtml = renderMarkdownToHtml(markedText);
    }
    renderedHtml = renderedHtml
        .replace(/==OMNI_HL==/g, '<mark class="bg-amber-400/30 text-amber-200 px-1 py-0.5 rounded font-semibold border border-amber-400/40">')
        .replace(/==OMNI_ENDHL==/g, '</mark>');
        
    markdownContentEl.innerHTML = renderedHtml;
    applyKaTeXToElement(markdownContentEl);
    renderMathFormulas(markdownContentEl);
    buildTableOfContents(markdownContentEl, notesContent);
}

// --- Upload Note Operations ---
function openUploadModal() {
    document.getElementById("uploadModal").classList.remove("hidden");
}

function closeUploadModal() {
    document.getElementById("uploadModal").classList.add("hidden");
    document.getElementById("uploadForm").reset();
    
    document.getElementById("uploadBtnText").textContent = "Upload & OCR Index";
    document.getElementById("uploadSpinner").classList.add("hidden");
}

async function handleUploadSubmit(event) {
    event.preventDefault();
    
    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);
    
    // UI Loading state
    document.getElementById("uploadBtnText").textContent = "Processing OCR...";
    document.getElementById("uploadSpinner").classList.remove("hidden");
    
    try {
        const response = await fetch("/api/notes/upload", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Upload note failed");
        }
        
        const note = await response.json();
        
        // Success
        alert(`Successfully uploaded "${note.title}". OCR completed!`);
        closeUploadModal();
        
        // Refresh dashboard notes list if search query matches the subject
        if (currentSearchData) {
            // Append the new note to local notes list and refresh display
            currentSearchData.notes.unshift(note);
            renderNotesList(currentSearchData.notes);
        } else {
            // Fetch default list or do nothing
            fillAndSearch(note.subject);
        }
    } catch (e) {
        console.error(e);
        alert(`Error during note upload: ${e.message}`);
        
        document.getElementById("uploadBtnText").textContent = "Upload & OCR Index";
        document.getElementById("uploadSpinner").classList.add("hidden");
    }
}

// --- Render Careers (roadmap.sh) ---
function renderCareers(careers, careerRelevanceText) {
    const card = document.getElementById("careersContainerCard");
    const container = document.getElementById("careersContainer");
    
    if (!card || !container) return;
    container.innerHTML = "";
    
    const hasCareersList = Array.isArray(careers) && careers.length > 0;
    const hasRelevanceText = careerRelevanceText && typeof careerRelevanceText === "string" && careerRelevanceText.trim().length > 0;
    
    if (!hasCareersList && !hasRelevanceText) {
        card.classList.add("hidden");
        return;
    }
    
    card.classList.remove("hidden");

    if (hasRelevanceText) {
        const descEl = document.createElement("div");
        descEl.className = "mb-3 p-3 bg-indigo-50/70 border border-indigo-100 rounded-lg text-xs text-slate-700 leading-relaxed";
        descEl.innerHTML = `<span class="font-bold text-indigo-800 flex items-center mb-1"><i class="fa-solid fa-crosshairs mr-1.5 text-indigo-600"></i>Industry & Career Pathway:</span>${careerRelevanceText}`;
        container.appendChild(descEl);
    }
    
    if (hasCareersList) {
        careers.forEach(item => {
            const itemEl = document.createElement("div");
            itemEl.className = "bg-slate-50 border border-slate-100 rounded-lg p-3 hover:bg-slate-100 transition flex items-start justify-between gap-3";
            
            itemEl.innerHTML = `
                <div class="min-w-0 flex-1">
                    <h4 class="font-bold text-xs text-slate-800 flex items-center">
                        <i class="fa-solid fa-briefcase text-indigo-500 mr-2 text-[11px]"></i>${item.role}
                    </h4>
                    <p class="text-[10px] text-slate-600 mt-1 leading-relaxed">${item.importance}</p>
                </div>
                <div class="flex-shrink-0 self-center">
                    <a href="${item.roadmap_url}" target="_blank" class="glass-btn glass-btn-primary inline-flex items-center space-x-1.5 font-semibold px-2.5 py-1.5 rounded-md text-[10px] transition duration-200">
                        <span>View Roadmap</span>
                        <i class="fa-solid fa-arrow-up-right-from-square text-[8px]"></i>
                    </a>
                </div>
            `;
            container.appendChild(itemEl);
        });
    }
}

// --- Year-wise Notes Library Helpers ---
const YEAR_SUBJECTS = {
    1: {
        title: "First Year Engineering Subjects (Common for AKTU)",
        subjects: [
            {
                name: "Engineering Physics",
                units: [
                    { number: 1, name: "Relativistic Mechanics", file: "newtons_laws_notes.txt", chapters: "Frame of reference, Michelson- Morley experiment, Special theory of relativity, Lorentz transformation." },
                    { number: 2, name: "Electromagnetic Field Theory", file: "temp_engineering_physics_1788020499.txt", chapters: "Continuity equation, Maxwell's equations, Poynting vector, wave propagation in dielectrics." },
                    { number: 3, name: "Quantum Mechanics", file: "temp_engineering_physics_1788020499.txt", chapters: "Wave-particle duality, de Broglie waves, Heisenberg uncertainty relation, Schrodinger wave equation." },
                    { number: 4, name: "Wave Optics", file: "temp_engineering_physics_1788020499.txt", chapters: "Interference of light, double slit, Newton's rings, Fresnel and Fraunhofer diffraction, diffraction grating." },
                    { number: 5, name: "Lasers and Fiber Optics", file: "temp_engineering_physics_1788020499.txt", chapters: "Einstein's coefficients, Ruby laser, He-Ne laser, optical fiber types, numerical aperture, attenuation." }
                ]
            },
            {
                name: "Engineering Chemistry",
                units: [
                    { number: 1, name: "Atomic & Molecular Structure", file: "temp_engineering_physics_1788020499.txt", chapters: "Molecular orbital theory, LCAO method, metallic bonding, liquid crystals, green chemistry principles." },
                    { number: 2, name: "Spectroscopic Techniques", file: "temp_engineering_physics_1788020499.txt", chapters: "Elementary ideas and applications of UV-visible, IR, Raman, and NMR spectroscopy." },
                    { number: 3, name: "Electrochemistry & Corrosion", file: "temp_engineering_physics_1788020499.txt", chapters: "Nernst equation, galvanic cells, batteries, dry/wet corrosion, passivation, prevention methods." },
                    { number: 4, name: "Water Technology", file: "temp_engineering_physics_1788020499.txt", chapters: "Hardness of water, estimation by EDTA, boiler troubles, lime-soda softening, reverse osmosis." },
                    { number: 5, name: "Polymers & Organometallics", file: "temp_engineering_physics_1788020499.txt", chapters: "Classification, preparation and properties of thermoplastics and thermosets, Grignard reagent." }
                ]
            },
            {
                name: "Engineering Mathematics-I",
                units: [
                    { number: 1, name: "Differential Calculus-I", file: "calculus_integration_notes.txt", chapters: "Successive differentiation, Leibniz's theorem, curve tracing, asymptotes, curvature." },
                    { number: 2, name: "Differential Calculus-II", file: "calculus_integration_notes.txt", chapters: "Partial derivatives, Euler's theorem, total derivative, Jacobians, Taylor series for two variables." },
                    { number: 3, name: "Matrices", file: "calculus_integration_notes.txt", chapters: "Rank of matrix, inverse, linear system solutions, eigen values, Cayley-Hamilton theorem." },
                    { number: 4, name: "Multivariable Calculus-I", file: "calculus_integration_notes.txt", chapters: "Multiple integrals, double and triple integration, change of order, area and volume." },
                    { number: 5, name: "Vector Calculus", file: "calculus_integration_notes.txt", chapters: "Gradient, divergence, curl, line, surface and volume integrals, Green's and Stokes' theorems." }
                ]
            },
            {
                name: "Engineering Mathematics-II",
                units: [
                    { number: 1, name: "Ordinary Differential Equations", file: "calculus_integration_notes.txt", chapters: "Linear differential equations of higher order with constant coefficients, Euler-Cauchy equations." },
                    { number: 2, name: "Multivariable Calculus-II", file: "calculus_integration_notes.txt", chapters: "Beta and Gamma functions, Dirichlet's integral, application to center of gravity." },
                    { number: 3, name: "Sequences & Series", file: "calculus_integration_notes.txt", chapters: "Sequences, infinite series, convergence, ratio test, comparison test, Cauchy root test." },
                    { number: 4, name: "Complex Variable-Differentiation", file: "calculus_integration_notes.txt", chapters: "Analytic functions, Cauchy-Riemann equations, harmonic functions, conformal mapping." },
                    { number: 5, name: "Complex Variable-Integration", file: "calculus_integration_notes.txt", chapters: "Cauchy's integral theorem, Taylor's and Laurent's series, residues, evaluation of real integrals." }
                ]
            },
            {
                name: "Basic Electrical Engineering",
                units: [
                    { number: 1, name: "DC Circuits", file: "newtons_laws_notes.txt", chapters: "Mesh and nodal analysis, Superposition, Thevenin's, Norton's, and Maximum Power Transfer theorems." },
                    { number: 2, name: "AC Circuits", file: "newtons_laws_notes.txt", chapters: "Representation of sinusoidal waveforms, active, reactive and apparent power, RLC series-parallel, resonance." },
                    { number: 3, name: "Transformers", file: "newtons_laws_notes.txt", chapters: "EMF equation of transformer, equivalent circuit, losses, efficiency, voltage regulation." },
                    { number: 4, name: "Electrical Machines", file: "newtons_laws_notes.txt", chapters: "Construction and working principle of DC machines, single phase induction motor, synchronous generator." },
                    { number: 5, name: "Electrical Installations", file: "newtons_laws_notes.txt", chapters: "Switch fuse unit, MCB, ELCB, wire types, earthing systems, battery characteristics." }
                ]
            },
            {
                name: "Programming for Problem Solving",
                units: [
                    { number: 1, name: "Introduction to Computer & C", file: "linked_list_reversal_notes.txt", chapters: "Computer systems, compilers, assemblers, algorithms, flowcharts, C syntax, data types." },
                    { number: 2, name: "Expressions & Decision Making", file: "linked_list_reversal_notes.txt", chapters: "Arithmetic expressions, operator precedence, conditional branching, if-else, switch-case." },
                    { number: 3, name: "Loops and Functions", file: "linked_list_reversal_notes.txt", chapters: "For loop, while loop, do-while loop, user-defined functions, recursion, call by value/reference." },
                    { number: 4, name: "Arrays and Pointers", file: "linked_list_reversal_notes.txt", chapters: "1D arrays, 2D arrays, string operations, pointers, address operators, arrays with pointers." },
                    { number: 5, name: "Structures and File I/O", file: "linked_list_reversal_notes.txt", chapters: "Structures, unions, file opening modes, writing and reading data files, library functions." }
                ]
            },
            {
                name: "Fundamentals of Electronics",
                units: [
                    { number: 1, name: "Semiconductor Diode", file: "temp_engineering_physics_1788020499.txt", chapters: "P-N junction diode, V-I characteristics, rectifiers (half, full and bridge type), Zener diode." },
                    { number: 2, name: "Bipolar Junction Transistor", file: "temp_engineering_physics_1788020499.txt", chapters: "BJT construction, input-output CE, CB and CC configuration characteristics, DC load line." },
                    { number: 3, name: "Field Effect Transistors", file: "temp_engineering_physics_1788020499.txt", chapters: "JFET working principles, JFET transfer characteristics, MOSFET structures and types." },
                    { number: 4, name: "Operational Amplifiers", file: "temp_engineering_physics_1788020499.txt", chapters: "Op-Amp characteristics, inverting/non-inverting configuration, adder, subtractor, integrator." },
                    { number: 5, name: "Instruments & CRO", file: "temp_engineering_physics_1788020499.txt", chapters: "Digital multi-meters, CRO block diagram, measurement of phase, voltage and frequency." }
                ]
            },
            {
                name: "Fundamentals of Mechanical",
                units: [
                    { number: 1, name: "Mechanics & Materials", file: "newtons_laws_notes.txt", chapters: "Hooke's law, stress-strain diagram, force systems, Lami's theorem, truss analysis." },
                    { number: 2, name: "Thermal Engineering", file: "newtons_laws_notes.txt", chapters: "Zero, First and Second laws of thermodynamics, Carnot engine, steam generators." },
                    { number: 3, name: "Fluid Mechanics", file: "newtons_laws_notes.txt", chapters: "Fluid properties, viscosity, Pascal's law, Bernoulli's equation, discharge measurement." },
                    { number: 4, name: "Power Transmission", file: "newtons_laws_notes.txt", chapters: "Belts, ropes, gear trains, couplings, clutch operations, journal/roller bearings." },
                    { number: 5, name: "Manufacturing Processes", file: "newtons_laws_notes.txt", chapters: "Casting patterns, electric arc welding, gas welding, lathe operations, milling." }
                ]
            },
            {
                name: "Environment and Ecology",
                units: [
                    { number: 1, name: "Ecosystems", file: "newtons_laws_notes.txt", chapters: "Structure and function, food chain, food web, ecological succession, biogeochemical cycles." },
                    { number: 2, name: "Natural Resources", file: "newtons_laws_notes.txt", chapters: "Forests, water, mineral resources, dams, solar/wind energy systems." },
                    { number: 3, name: "Environmental Pollution", file: "newtons_laws_notes.txt", chapters: "Air, water and soil pollution indicators, waste disposal and control." },
                    { number: 4, name: "Social Environmental Issues", file: "newtons_laws_notes.txt", chapters: "Climate change, global warming, acid rain, ozone layer depletion, sustainable development." },
                    { number: 5, name: "Human Population & Health", file: "newtons_laws_notes.txt", chapters: "Population explosion, environmental health hazards, women and child welfare." }
                ]
            },
            {
                name: "Soft Skills & Soft Communication",
                units: [
                    { number: 1, name: "Technical Communication Fundamentals", file: "newtons_laws_notes.txt", chapters: "Nature and scope of communication, barriers to communication, channels." },
                    { number: 2, name: "Technical Writing", file: "newtons_laws_notes.txt", chapters: "Report writing formats, research proposals, abstracting, technical reports." },
                    { number: 3, name: "Business Correspondence", file: "newtons_laws_notes.txt", chapters: "Professional letters, resume preparation, job applications, memorandum formats." },
                    { number: 4, name: "Presentation & Seminar Techniques", file: "newtons_laws_notes.txt", chapters: "Audience analysis, delivery styles, slide preparations, voice modulation." },
                    { number: 5, name: "Functional English Grammar", file: "newtons_laws_notes.txt", chapters: "Sentence construction, active/passive voice, common errors, vocabulary enhancement." }
                ]
            }
        ]
    },
    2: {
        title: "Second Year B.Tech CSE Subjects (AKTU)",
        subjects: [
            {
                name: "Data Structures & Algorithms",
                units: [
                    { number: 1, name: "Asymptotic Notation & Arrays", file: "linked_list_reversal_notes.txt", chapters: "Big-O, Omega, Theta notations, multi-dimensional arrays, address calculations, sparse matrix." },
                    { number: 2, name: "Linked Lists & Inversion", file: "linked_list_reversal_notes.txt", chapters: "Singly linked lists, circular list, doubly linked list operations, linked list inversion." },
                    { number: 3, name: "Stacks & Queues", file: "linked_list_reversal_notes.txt", chapters: "Stack implementation, recursion, infix to postfix conversions, queues, circular queues, deques." },
                    { number: 4, name: "Trees and Binary Search Trees", file: "linked_list_reversal_notes.txt", chapters: "Binary tree properties, traversals, binary search tree (BST) operations, AVL trees." },
                    { number: 5, name: "Sorting & Searching", file: "linked_list_reversal_notes.txt", chapters: "Bubble, insertion, quick, merge and heap sorting, linear and binary search, hashing." }
                ]
            },
            {
                name: "Computer Organization & Architecture",
                units: [
                    { number: 1, name: "Register Transfer & Microoperations", file: "linked_list_reversal_notes.txt", chapters: "Bus transfer, memory transfer, arithmetic micro-operations, logic micro-operations." },
                    { number: 2, name: "Basic Computer Organization", file: "linked_list_reversal_notes.txt", chapters: "Instruction codes, computer registers, timing and control, instruction cycles." },
                    { number: 3, name: "Central Processing Unit", file: "linked_list_reversal_notes.txt", chapters: "General register organization, stack organization, instruction formats, addressing modes." },
                    { number: 4, name: "Computer Arithmetic", file: "linked_list_reversal_notes.txt", chapters: "Addition, subtraction, multiplication algorithms (Booth's), division algorithms." },
                    { number: 5, name: "Memory Organization", file: "linked_list_reversal_notes.txt", chapters: "Memory hierarchy, main memory, auxiliary memory, associative, cache memory mappings." }
                ]
            },
            {
                name: "Discrete Mathematics",
                units: [
                    { number: 1, name: "Sets, Relations & Functions", file: "calculus_integration_notes.txt", chapters: "Set operations, equivalence relations, partial ordering, lattices, functions." },
                    { number: 2, name: "Algebraic Structures", file: "calculus_integration_notes.txt", chapters: "Groups, subgroups, cyclic groups, rings, integral domains, fields." },
                    { number: 3, name: "Propositional Logic", file: "calculus_integration_notes.txt", chapters: "Tautologies, contradictions, logical equivalences, quantifiers, rules of inference." },
                    { number: 4, name: "Combinatorics & Recurrence", file: "calculus_integration_notes.txt", chapters: "Pigeonhole principle, permutations, combinations, recurrence relations." },
                    { number: 5, name: "Graph Theory", file: "calculus_integration_notes.txt", chapters: "Graphs, subgraphs, paths, cycles, Eulerian and Hamiltonian paths, trees." }
                ]
            },
            {
                name: "Object Oriented Programming",
                units: [
                    { number: 1, name: "OOP Paradigm & C++ Basics", file: "linked_list_reversal_notes.txt", chapters: "Encapsulation, inheritance, polymorphism, classes, objects, access specifiers." },
                    { number: 2, name: "Constructors & Operator Overloading", file: "linked_list_reversal_notes.txt", chapters: "Default, parameterized and copy constructors, operator overloading, friend functions." },
                    { number: 3, name: "Inheritance and Virtual Functions", file: "linked_list_reversal_notes.txt", chapters: "Single, multiple, multi-level inheritance, virtual base classes, runtime polymorphism." },
                    { number: 4, name: "Templates and Exception Handling", file: "linked_list_reversal_notes.txt", chapters: "Function templates, class templates, try-throw-catch exception models." },
                    { number: 5, name: "Streams and Files", file: "linked_list_reversal_notes.txt", chapters: "File stream operations, binary I/O, file pointers, sequential and random access." }
                ]
            },
            {
                name: "Operating Systems",
                units: [
                    { number: 1, name: "Introduction & Process Scheduling", file: "linked_list_reversal_notes.txt", chapters: "OS services, system calls, process state transitions, PCB, CPU scheduling." },
                    { number: 2, name: "Process Synchronization & Deadlocks", file: "linked_list_reversal_notes.txt", chapters: "Critical section, semaphores, monitors, deadlock prevention and Banker's algorithm." },
                    { number: 3, name: "Memory Management", file: "linked_list_reversal_notes.txt", chapters: "Logical/physical address space, paging, segmentation, virtual memory, page replacement." },
                    { number: 4, name: "File System & Disk Scheduling", file: "linked_list_reversal_notes.txt", chapters: "File concepts, directory systems, allocation methods, disk scheduling (FCFS, SSTF, SCAN)." },
                    { number: 5, name: "Case Study: Linux & Windows", file: "linked_list_reversal_notes.txt", chapters: "Linux kernel modules, process management in Linux, security features." }
                ]
            },
            {
                name: "Database Management Systems",
                units: [
                    { number: 1, name: "Database Systems & ER Modeling", file: "linked_list_reversal_notes.txt", chapters: "Data independence, database languages, ER diagram mapping, weak entities." },
                    { number: 2, name: "Relational Data Model & SQL", file: "linked_list_reversal_notes.txt", chapters: "Relational algebra, SQL DDL/DML queries, integrity constraints, joins." },
                    { number: 3, name: "Relational Database Design", file: "linked_list_reversal_notes.txt", chapters: "Functional dependencies, normalization (1NF, 2NF, 3NF, BCNF), dependency preservation." },
                    { number: 4, name: "Transaction Processing & Concurrency", file: "linked_list_reversal_notes.txt", chapters: "ACID properties, serializability, lock-based protocols, two-phase locking (2PL)." },
                    { number: 5, name: "Concurrency & Recovery Systems", file: "linked_list_reversal_notes.txt", chapters: "Deadlock handling, log-based recovery, shadow paging, check-points." }
                ]
            },
            {
                name: "Theory of Automata & Languages",
                units: [
                    { number: 1, name: "Finite Automata", file: "linked_list_reversal_notes.txt", chapters: "DFA, NFA definitions, equivalence of DFA & NFA, minimization of finite automata." },
                    { number: 2, name: "Regular Expressions & Languages", file: "linked_list_reversal_notes.txt", chapters: "Regular grammar, pumping lemma for regular sets, closure properties of regular sets." },
                    { number: 3, name: "Context Free Grammars & Pushdown Automata", file: "linked_list_reversal_notes.txt", chapters: "CFG derivations, ambiguity in grammar, PDA design, equivalence of CFG and PDA." },
                    { number: 4, name: "Turing Machines", file: "linked_list_reversal_notes.txt", chapters: "Turing machine models, design of TM, recursive and recursively enumerable languages." },
                    { number: 5, name: "Undecidability", file: "linked_list_reversal_notes.txt", chapters: "Church-Turing thesis, halting problem, Post's correspondence problem (PCP)." }
                ]
            },
            {
                name: "Cyber Security",
                units: [
                    { number: 1, name: "Cyber Security Overview", file: "linked_list_reversal_notes.txt", chapters: "Information security, threat assessment, cyber crimes, computer forensics." },
                    { number: 2, name: "Application & Network Security", file: "linked_list_reversal_notes.txt", chapters: "Email security, firewall configurations, intrusion detection systems, VPN." },
                    { number: 3, name: "Security Protocols", file: "linked_list_reversal_notes.txt", chapters: "SSL, TLS, IPsec, secure electronic transactions (SET), secure shell." },
                    { number: 4, name: "Cryptography", file: "linked_list_reversal_notes.txt", chapters: "Symmetric and asymmetric encryption, DES, AES, RSA algorithms, digital signatures." },
                    { number: 5, name: "Cyber Laws & Policies", file: "linked_list_reversal_notes.txt", chapters: "IT Act 2000, intellectual property rights, copyright issues, privacy policy." }
                ]
            },
            {
                name: "Universal Human Values",
                units: [
                    { number: 1, name: "Value Education", file: "newtons_laws_notes.txt", chapters: "Understanding value education, self-exploration, basic human aspirations." },
                    { number: 2, name: "Harmony in Human Being", file: "newtons_laws_notes.txt", chapters: "Harmony of Self (I) with Body (Sanyam and Swasthya), correct needs." },
                    { number: 3, name: "Harmony in Family & Society", file: "newtons_laws_notes.txt", chapters: "Trust (Vishwas) and Respect (Samman), relationship values, societal harmony." },
                    { number: 4, name: "Harmony in Nature", file: "newtons_laws_notes.txt", chapters: "Four orders in nature, interconnectedness, mutual fulfillment." },
                    { number: 5, name: "Professional Ethics", file: "newtons_laws_notes.txt", chapters: "Ethical human conduct, professional ethics competence, vision of harmony." }
                ]
            },
            {
                name: "Technical Communication",
                units: [
                    { number: 1, name: "Technical Communication Basics", file: "newtons_laws_notes.txt", chapters: "Channels of communication, active listening, non-verbal signals." },
                    { number: 2, name: "Technical Writing Mechanics", file: "newtons_laws_notes.txt", chapters: "Defining user manuals, writing abstracts, editing engineering drafts." },
                    { number: 3, name: "Business & Corporate Correspondence", file: "newtons_laws_notes.txt", chapters: "Minutes of meetings, circulars, letters of inquiry, complaints." },
                    { number: 4, name: "Advanced Presentation Skills", file: "newtons_laws_notes.txt", chapters: "Handling Q&A sessions, structural outlines, dynamic visual aids." },
                    { number: 5, name: "Communication Ethics", file: "newtons_laws_notes.txt", chapters: "Ethical reporting, copying restrictions, professional integrity in writing." }
                ]
            }
        ]
    },
    3: {
        title: "Third Year B.Tech CSE Subjects (AKTU)",
        subjects: [
            {
                name: "Design & Analysis of Algorithms",
                units: [
                    { number: 1, name: "Divide and Conquer", file: "linked_list_reversal_notes.txt", chapters: "Recurrences solving, Master theorem, Merge sort, Quick sort, Heap sort." },
                    { number: 2, name: "Greedy Algorithms", file: "linked_list_reversal_notes.txt", chapters: "Fractional Knapsack, Huffman coding, Kruskal's & Prim's minimum spanning tree." },
                    { number: 3, name: "Dynamic Programming", file: "linked_list_reversal_notes.txt", chapters: "Matrix chain multiplication, Longest common subsequence, 0/1 Knapsack problem." },
                    { number: 4, name: "Backtracking & Branch and Bound", file: "linked_list_reversal_notes.txt", chapters: "N-Queens problem, TSP, graph coloring, Hamiltonian cycles." },
                    { number: 5, name: "Complexity Classes", file: "linked_list_reversal_notes.txt", chapters: "P, NP, NP-Hard, NP-Complete, vertex cover, clique problem." }
                ]
            },
            {
                name: "Computer Networks",
                units: [
                    { number: 1, name: "Physical & Data Link Layer", file: "linked_list_reversal_notes.txt", chapters: "OSI/TCP-IP reference models, sliding window protocols, error detection/correction." },
                    { number: 2, name: "Medium Access Control", file: "linked_list_reversal_notes.txt", chapters: "CSMA/CD, CSMA/CA, Ethernet, Token Ring, wireless LANs." },
                    { number: 3, name: "Network Layer", file: "linked_list_reversal_notes.txt", chapters: "IPv4/IPv6 addressing, routing algorithms (Distance Vector, Link State), congestion control." },
                    { number: 4, name: "Transport Layer", file: "linked_list_reversal_notes.txt", chapters: "UDP, TCP, flow and error control, connection management." },
                    { number: 5, name: "Application Layer", file: "linked_list_reversal_notes.txt", chapters: "DNS, SMTP, FTP, HTTP, network security cryptography principles." }
                ]
            },
            {
                name: "Compiler Design",
                units: [
                    { number: 1, name: "Lexical Analysis", file: "linked_list_reversal_notes.txt", chapters: "Role of lexical analyzer, tokens, regular expressions, transition diagrams, lex tool." },
                    { number: 2, name: "Syntax Analysis", file: "linked_list_reversal_notes.txt", chapters: "CFGs, Parsing types, LL(1) parsing, LR parsing (SLR, LALR, CLR), parser generators." },
                    { number: 3, name: "Syntax Directed Translation", file: "linked_list_reversal_notes.txt", chapters: "Syntax-directed definitions, dependency graphs, S-attributed and L-attributed definitions." },
                    { number: 4, name: "Intermediate Code Generation", file: "linked_list_reversal_notes.txt", chapters: "Three-address code, quadruples, triples, indirect triples, boolean expressions, declarations." },
                    { number: 5, name: "Code Optimization & Generation", file: "linked_list_reversal_notes.txt", chapters: "Principal sources of optimization, loop optimization, DAG representation of basic blocks." }
                ]
            },
            {
                name: "Software Engineering",
                units: [
                    { number: 1, name: "Software Process Models", file: "linked_list_reversal_notes.txt", chapters: "SDLC phases, Waterfall model, Spiral model, RAD model, Agile development models." },
                    { number: 2, name: "Requirements Engineering", file: "linked_list_reversal_notes.txt", chapters: "Feasibility studies, SRS document, validation, behavioral models." },
                    { number: 3, name: "Software Design", file: "linked_list_reversal_notes.txt", chapters: "Cohesion & coupling, object-oriented design, UML class/use-case diagrams." },
                    { number: 4, name: "Software Testing", file: "linked_list_reversal_notes.txt", chapters: "White-box testing, black-box testing, unit testing, integration and system testing." },
                    { number: 5, name: "Software Project Management", file: "linked_list_reversal_notes.txt", chapters: "COCOMO estimation model, risk management, version control systems (Git)." }
                ]
            },
            {
                name: "Web Technologies",
                units: [
                    { number: 1, name: "HTML5 & CSS3", file: "linked_list_reversal_notes.txt", chapters: "Structural elements, CSS selectors, box model, responsive layouts, media queries." },
                    { number: 2, name: "Client-side Scripting", file: "linked_list_reversal_notes.txt", chapters: "JavaScript syntax, DOM manipulation, events, asynchronous programming (AJAX)." },
                    { number: 3, name: "Server-side Programming", file: "linked_list_reversal_notes.txt", chapters: "Introduction to PHP/Node.js, form handling, session management, database connectivity." },
                    { number: 4, name: "XML and Web Services", file: "linked_list_reversal_notes.txt", chapters: "XML schema, DTD, SOAP, RESTful APIs, JSON data parsing." },
                    { number: 5, name: "Web Frameworks", file: "linked_list_reversal_notes.txt", chapters: "Bootstrap grid system, React component structures, web deployment guidelines." }
                ]
            },
            {
                name: "Microprocessors & Microcontrollers",
                units: [
                    { number: 1, name: "8085 Architecture", file: "temp_engineering_physics_1788020499.txt", chapters: "Pin configurations, register structure, timing diagram, instruction cycles." },
                    { number: 2, name: "8086 Architecture", file: "temp_engineering_physics_1788020499.txt", chapters: "Memory segmentation, segment registers, index registers, addressing modes." },
                    { number: 3, name: "Assembly Language Programming", file: "temp_engineering_physics_1788020499.txt", chapters: "8086 instructions, data transfer, arithmetic, logical and control flow instructions." },
                    { number: 4, name: "Interfacing Devices", file: "temp_engineering_physics_1788020499.txt", chapters: "8255 PPI, 8254 timer, A/D & D/A converters interfacing." },
                    { number: 5, name: "8051 Microcontroller", file: "temp_engineering_physics_1788020499.txt", chapters: "Architecture, pin diagram, I/O ports, internal RAM structure, instruction set." }
                ]
            },
            {
                name: "Data Science & Machine Learning Basics",
                units: [
                    { number: 1, name: "Python for Data Science", file: "linked_list_reversal_notes.txt", chapters: "NumPy arrays, Pandas DataFrames, Matplotlib plotting, data cleaning." },
                    { number: 2, name: "Linear Regression", file: "linked_list_reversal_notes.txt", chapters: "Least squares method, gradient descent, coefficient of determination (R2)." },
                    { number: 3, name: "Logistic Regression", file: "linked_list_reversal_notes.txt", chapters: "Sigmoid function, cost functions, binary classification metrics." },
                    { number: 4, name: "Clustering Algorithms", file: "linked_list_reversal_notes.txt", chapters: "K-means algorithm, silhouette analysis, hierarchical clustering methods." },
                    { number: 5, name: "Feature Selection & Reduction", file: "linked_list_reversal_notes.txt", chapters: "Feature engineering, principal component analysis (PCA) basics." }
                ]
            },
            {
                name: "Theory of Computation",
                units: [
                    { number: 1, name: "Formal Grammars", file: "linked_list_reversal_notes.txt", chapters: "Chomsky hierarchy of languages, terminal/non-terminal symbols, derivation trees." },
                    { number: 2, name: "Context-Free Languages", file: "linked_list_reversal_notes.txt", chapters: "Pumping lemma for CFLs, closure properties, parsing tree reductions." },
                    { number: 3, name: "Linear Bounded Automata", file: "linked_list_reversal_notes.txt", chapters: "Context sensitive grammars, LBA transitions, Turing machines comparison." },
                    { number: 4, name: "Halting & Decidability", file: "linked_list_reversal_notes.txt", chapters: "Universal Turing machines, halting problem proof, recursive languages." },
                    { number: 5, name: "Intractable Problems", file: "linked_list_reversal_notes.txt", chapters: "Polynomial-time reductions, Cook-Levin theorem, SAT problem verification." }
                ]
            },
            {
                name: "Digital Electronics",
                units: [
                    { number: 1, name: "Number Systems", file: "temp_engineering_physics_1788020499.txt", chapters: "Binary, octal, hexadecimal representations, binary arithmetic, BCD, excess-3." },
                    { number: 2, name: "Boolean Algebra", file: "temp_engineering_physics_1788020499.txt", chapters: "Karnaugh maps (up to 4 variables), SOP/POS simplification, logic gates." },
                    { number: 3, name: "Combinational Circuits", file: "temp_engineering_physics_1788020499.txt", chapters: "Half/full adders, multiplexers, demultiplexers, encoders, decoders." },
                    { number: 4, name: "Sequential Circuits", file: "temp_engineering_physics_1788020499.txt", chapters: "Flip-flops (SR, JK, D, T), latch operations, master-slave configurations." },
                    { number: 5, name: "Registers and Counters", file: "temp_engineering_physics_1788020499.txt", chapters: "Shift registers, ripple counters, synchronous counters, ring counters." }
                ]
            },
            {
                name: "Constitution of India",
                units: [
                    { number: 1, name: "Historical Background", file: "newtons_laws_notes.txt", chapters: "Constituent Assembly, preamble, basic features of the Constitution." },
                    { number: 2, name: "Fundamental Rights & Duties", file: "newtons_laws_notes.txt", chapters: "Right to equality, freedom of religion, directive principles of state policy." },
                    { number: 3, name: "The Union Legislature", file: "newtons_laws_notes.txt", chapters: "Presidential powers, Lok Sabha and Rajya Sabha structures, legislative procedure." },
                    { number: 4, name: "The Judiciary", file: "newtons_laws_notes.txt", chapters: "Supreme Court, High Courts, judicial review, public interest litigation." },
                    { number: 5, name: "Emergency Provisions", file: "newtons_laws_notes.txt", chapters: "National, state, and financial emergency, constitutional amendments." }
                ]
            }
        ]
    },
    4: {
        title: "Fourth Year B.Tech CSE Subjects (AKTU)",
        subjects: [
            {
                name: "Artificial Intelligence",
                units: [
                    { number: 1, name: "Searching Strategies", file: "linked_list_reversal_notes.txt", chapters: "Uninformed (BFS, DFS), informed (A*, AO*), constraint satisfaction." },
                    { number: 2, name: "Knowledge Representation", file: "linked_list_reversal_notes.txt", chapters: "Propositional logic, predicate logic, resolution, semantic networks, frames." },
                    { number: 3, name: "Natural Language Processing", file: "linked_list_reversal_notes.txt", chapters: "Syntactic analysis, semantic analysis, parsing techniques, speech recognition." },
                    { number: 4, name: "Game Playing", file: "linked_list_reversal_notes.txt", chapters: "Minimax search, alpha-beta pruning, utility evaluation." },
                    { number: 5, name: "Expert Systems", file: "linked_list_reversal_notes.txt", chapters: "Rule-based shells, inference engines, MYCIN structure." }
                ]
            },
            {
                name: "Cloud Computing & DevOps",
                units: [
                    { number: 1, name: "Cloud Models & Virtualization", file: "linked_list_reversal_notes.txt", chapters: "Hypervisors, SaaS, PaaS, IaaS, private and public cloud configurations." },
                    { number: 2, name: "Containers & Orchestration", file: "linked_list_reversal_notes.txt", chapters: "Docker container builds, Kubernetes pod structures, services, controllers." },
                    { number: 3, name: "DevOps & CI/CD", file: "linked_list_reversal_notes.txt", chapters: "Jenkins automation, GitHub Actions, unit testing pipelines, automated deployments." },
                    { number: 4, name: "Infrastructure as Code", file: "linked_list_reversal_notes.txt", chapters: "Terraform configurations, resource blocks, state file management." },
                    { number: 5, name: "Cloud Monitoring", file: "linked_list_reversal_notes.txt", chapters: "Prometheus alerts, Grafana dashboards, ELK log analysis." }
                ]
            },
            {
                name: "Machine Learning",
                units: [
                    { number: 1, name: "Decision Trees & SVMs", file: "linked_list_reversal_notes.txt", chapters: "Information gain, Gini index, support vector machine maximum margins." },
                    { number: 2, name: "Neural Networks & Backpropagation", file: "linked_list_reversal_notes.txt", chapters: "Multi-layer perceptrons, activation functions, gradient descent backpropagation." },
                    { number: 3, name: "Deep Learning Architectures", file: "linked_list_reversal_notes.txt", chapters: "Convolutional Neural Networks (CNN), Recurrent Neural Networks (RNN)." },
                    { number: 4, name: "Model Tuning & Regularization", file: "linked_list_reversal_notes.txt", chapters: "L1/L2 regularization, dropouts, early stopping, cross-validation metrics." },
                    { number: 5, name: "Reinforcement Learning", file: "linked_list_reversal_notes.txt", chapters: "Q-learning, Bellman equation, policy iteration, value iteration." }
                ]
            },
            {
                name: "Distributed Systems",
                units: [
                    { number: 1, name: "Distributed Architectures", file: "linked_list_reversal_notes.txt", chapters: "System models, communication protocols, RPC, RMI." },
                    { number: 2, name: "Clock Synchronization", file: "linked_list_reversal_notes.txt", chapters: "Logical clocks, Lamport timestamps, vector clocks, mutual exclusion." },
                    { number: 3, name: "Consensus & Agreement", file: "linked_list_reversal_notes.txt", chapters: "Byzantine agreement, Paxos consensus, Raft algorithm." },
                    { number: 4, name: "Distributed File Systems", file: "linked_list_reversal_notes.txt", chapters: "NFS, HDFS architectures, replica management, consistency." },
                    { number: 5, name: "Fault Tolerance", file: "linked_list_reversal_notes.txt", chapters: "Process resilience, reliable multicasting, check-pointing and recovery." }
                ]
            },
            {
                name: "Cryptography & Network Security",
                units: [
                    { number: 1, name: "Security Attacks & Services", file: "linked_list_reversal_notes.txt", chapters: "Active vs passive attacks, classical cipher techniques (substitution, transposition)." },
                    { number: 2, name: "Block Ciphers", file: "linked_list_reversal_notes.txt", chapters: "Feistel cipher structure, DES, double/triple DES, AES cipher operations." },
                    { number: 3, name: "Asymmetric Cryptography", file: "linked_list_reversal_notes.txt", chapters: "RSA algorithm, Diffie-Hellman key exchange, elliptic curve cryptography." },
                    { number: 4, name: "Hash Functions & Signatures", file: "linked_list_reversal_notes.txt", chapters: "SHA-512, MD5, Message Authentication Codes (MAC), digital signature standards." },
                    { number: 5, name: "System Security", file: "linked_list_reversal_notes.txt", chapters: "Intruders, malicious software, viruses, firewalls, secure electronic transactions." }
                ]
            },
            {
                name: "Big Data Analytics",
                units: [
                    { number: 1, name: "Introduction to Big Data", file: "linked_list_reversal_notes.txt", chapters: "Characteristics (V's of Big Data), analytics lifecycle, storage systems." },
                    { number: 2, name: "MapReduce Framework", file: "linked_list_reversal_notes.txt", chapters: "Map phase, reduce phase, execution pipeline, job scheduling." },
                    { number: 3, name: "NoSQL Databases", file: "linked_list_reversal_notes.txt", chapters: "HBase, Cassandra, MongoDB collections, document store indexing." },
                    { number: 4, name: "Spark Streaming & In-Memory Processing", file: "linked_list_reversal_notes.txt", chapters: "Resilient Distributed Datasets (RDD), Spark SQL operations, MLlib." },
                    { number: 5, name: "Graph Analytics", file: "linked_list_reversal_notes.txt", chapters: "Graph databases (Neo4j), PageRank algorithm implementations." }
                ]
            },
            {
                name: "Internet of Things",
                units: [
                    { number: 1, name: "IoT Architectures", file: "linked_list_reversal_notes.txt", chapters: "Sensors, actuators, gateways, IoT protocol stacks, communication models." },
                    { number: 2, name: "IoT Protocols", file: "linked_list_reversal_notes.txt", chapters: "MQTT, CoAP, HTTP, AMQP, ZigBee, 6LoWPAN network configurations." },
                    { number: 3, name: "IoT Hardware Platforms", file: "linked_list_reversal_notes.txt", chapters: "Arduino IDE, Raspberry Pi pin assignments, GPIO interfaces." },
                    { number: 4, name: "Cloud Analytics & IoT", file: "linked_list_reversal_notes.txt", chapters: "AWS IoT core, stream analytics, device shadows, rule actions." },
                    { number: 5, name: "IoT Security Threats", file: "linked_list_reversal_notes.txt", chapters: "Device authentication, physical attacks, firmware security patches." }
                ]
            },
            {
                name: "Digital Image Processing",
                units: [
                    { number: 1, name: "Image Fundamentals", file: "linked_list_reversal_notes.txt", chapters: "Visual perception, digitization, pixel connectivity, image transforms (DFT, DCT)." },
                    { number: 2, name: "Image Enhancement", file: "linked_list_reversal_notes.txt", chapters: "Histogram equalization, spatial filtering, smoothing, sharpening filters." },
                    { number: 3, name: "Image Restoration", file: "linked_list_reversal_notes.txt", chapters: "Noise models, inverse filtering, Wiener filter restorations." },
                    { number: 4, name: "Image Segmentation", file: "linked_list_reversal_notes.txt", chapters: "Point, line, edge detection, Hough transform, thresholding, region growing." },
                    { number: 5, name: "Compression & Representation", file: "linked_list_reversal_notes.txt", chapters: "Lossless vs lossy compression, Huffman coding, run-length coding, JPEG standard." }
                ]
            },
            {
                name: "Mobile Computing",
                units: [
                    { number: 1, name: "Wireless Transmission", file: "linked_list_reversal_notes.txt", chapters: "Signals, multiplexing (SDM, FDM, TDM, CDM), spread spectrum." },
                    { number: 2, name: "Telecommunication Systems", file: "linked_list_reversal_notes.txt", chapters: "GSM architecture, handovers, GPRS configurations, UMTS." },
                    { number: 3, name: "Mobile Network Layer", file: "linked_list_reversal_notes.txt", chapters: "Mobile IP, DHCP, routing in ad-hoc networks (AODV, DSR)." },
                    { number: 4, name: "Mobile Transport Layer", file: "linked_list_reversal_notes.txt", chapters: "Indirect TCP, snooping TCP, mobile TCP, WAP architecture." },
                    { number: 5, name: "Mobile Platforms & Security", file: "linked_list_reversal_notes.txt", chapters: "Android/iOS architectures, mobile application security guidelines." }
                ]
            },
            {
                name: "Software Testing & Quality",
                units: [
                    { number: 1, name: "Testing Principles", file: "linked_list_reversal_notes.txt", chapters: "Software errors, defects, test cases design, verification vs validation." },
                    { number: 2, name: "Black-Box Testing Techniques", file: "linked_list_reversal_notes.txt", chapters: "Boundary value analysis, equivalence partitioning, decision tables." },
                    { number: 3, name: "White-Box Testing Techniques", file: "linked_list_reversal_notes.txt", chapters: "Control flow testing, path coverage, data flow testing, mutation testing." },
                    { number: 4, name: "Quality Assurance Models", file: "linked_list_reversal_notes.txt", chapters: "ISO 9000 standard, CMMI maturity levels, Six Sigma quality controls." },
                    { number: 5, name: "Test Automation", file: "linked_list_reversal_notes.txt", chapters: "Static analysis tools, dynamic analysis tools, unit test tools (JUnit)." }
                ]
            }
        ]
    }
};

function selectYearNotes(year) {
    const data = YEAR_SUBJECTS[year];
    if (!data) return;
    
    const panel = document.getElementById("yearSubjectsPanel");
    const title = document.getElementById("selectedYearTitle");
    const list = document.getElementById("yearSubjectsList");
    
    if (!panel || !title || !list) return;
    
    title.textContent = data.title;
    list.innerHTML = "";
    list.className = "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3";
    
    data.subjects.forEach((subject, idx) => {
        const btn = document.createElement("button");
        btn.className = "flex items-center justify-between text-left bg-slate-50 hover:bg-indigo-50 border border-slate-100 hover:border-indigo-200 p-3 rounded-lg text-xs font-semibold text-slate-700 hover:text-indigo-700 transition duration-150 group";
        btn.onclick = () => viewSubjectUnits(year, idx);
        btn.innerHTML = `
            <span>${subject.name}</span>
            <i class="fa-solid fa-chevron-right text-[10px] opacity-40 group-hover:opacity-100 transition-transform group-hover:translate-x-0.5 font-sans"></i>
        `;
        list.appendChild(btn);
    });
    
    panel.classList.remove("hidden");
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function viewSubjectUnits(year, subjectIndex) {
    const yearData = YEAR_SUBJECTS[year];
    if (!yearData) return;
    const subject = yearData.subjects[subjectIndex];
    if (!subject) return;

    const panel = document.getElementById("yearSubjectsPanel");
    const title = document.getElementById("selectedYearTitle");
    const list = document.getElementById("yearSubjectsList");
    
    if (!panel || !title || !list) return;

    title.textContent = `${subject.name} - Units & Chapters`;
    list.innerHTML = "";
    list.className = "grid grid-cols-1 gap-4 w-full";

    const backBtnContainer = document.createElement("div");
    backBtnContainer.className = "col-span-full mb-2";
    backBtnContainer.innerHTML = `
        <button onclick="selectYearNotes(${year})" class="glass-btn glass-btn-secondary inline-flex items-center space-x-2 font-semibold px-3 py-1.5 rounded-lg text-xs transition">
            <i class="fa-solid fa-arrow-left"></i>
            <span>Back to Subjects</span>
        </button>
    `;
    list.appendChild(backBtnContainer);

    subject.units.forEach(unit => {
        const cleanSubjectName = subject.name.toLowerCase().replace(/[^a-z0-9]/g, "_").replace(/_+/g, "_");
        const filename = `aktu_${cleanSubjectName}_unit_${unit.number}.html`;
        
        const unitCard = document.createElement("div");
        unitCard.className = "bg-slate-50/50 border border-slate-200/80 rounded-xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 transition hover:bg-white hover:shadow-xs";
        
        unitCard.innerHTML = `
            <div class="flex-1">
                <div class="flex items-center space-x-2">
                    <span class="glass-badge glass-badge-indigo px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide">Unit ${unit.number}</span>
                    <h5 class="font-bold text-sm text-slate-800">${unit.name}</h5>
                </div>
                <p class="text-xs text-slate-600 mt-1.5 leading-relaxed font-sans"><strong class="text-slate-755">Topics:</strong> ${unit.chapters}</p>
            </div>
            <div class="flex-shrink-0 self-stretch md:self-center flex items-center">
            </div>
        `;
        list.appendChild(unitCard);
    });
}

function closeYearSubjects() {
    const panel = document.getElementById("yearSubjectsPanel");
    if (panel) {
        panel.classList.add("hidden");
    }
}

async function toggleSettingsModal() {
    const modal = document.getElementById("settingsModal");
    if (!modal) return;
    
    if (modal.classList.contains("hidden")) {
        try {
            const res = await fetch("/api/config/get-status");
            const data = await res.json();
            const statusText = document.getElementById("apiKeyStatusText");
            const keyInput = document.getElementById("geminiApiKeyInput");
            if (data.has_key) {
                statusText.textContent = `✓ Gemini Key active (${data.masked_key})`;
                statusText.className = "text-xs text-emerald-400 block mt-1 font-semibold";
                if (keyInput) keyInput.value = "";
            } else {
                statusText.textContent = "✗ No Gemini Key configured (running in fallback mode)";
                statusText.className = "text-xs text-rose-400 block mt-1 font-semibold";
            }
        } catch (e) {
            console.error("Failed to fetch key status:", e);
        }
        modal.classList.remove("hidden");
    } else {
        modal.classList.add("hidden");
    }
}
window.toggleSettingsModal = toggleSettingsModal;

async function saveApiKey(event) {
    event.preventDefault();
    const keyInput = document.getElementById("geminiApiKeyInput");
    if (!keyInput) return;
    
    const keyVal = keyInput.value.trim();
    if (!keyVal) {
        alert("Please enter a valid API key.");
        return;
    }
    
    try {
        const res = await fetch("/api/config/save-key", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ gemini_api_key: keyVal })
        });
        const data = await res.json();
        if (data.status === "success") {
            alert("Success! Your Gemini API key has been saved and connected.");
            toggleSettingsModal();
        } else {
            alert("Error: " + (data.detail || "Failed to save key"));
        }
    } catch (e) {
        console.error("Failed to save key:", e);
        alert("Failed to connect to backend server. Make sure it is running.");
    }
}
window.saveApiKey = saveApiKey;

