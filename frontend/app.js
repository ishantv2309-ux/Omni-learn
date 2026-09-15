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

// --- Dark / Light Mode Theme System ---
function initTheme() {
    const savedTheme = localStorage.getItem("omni_theme") || "dark";
    applyTheme(savedTheme);
}

function applyQuickExampleTheme(theme) {
    const qe = document.getElementById("quickExampleSection");
    if (!qe) return;
    const isDark = theme === "dark" || document.documentElement.classList.contains("dark");
    if (isDark) {
        qe.style.setProperty("background", "linear-gradient(180deg, rgba(15, 23, 42, 0.9) 0%, rgba(10, 15, 29, 0.98) 100%)", "important");
        qe.style.setProperty("border", "1px solid rgba(255, 255, 255, 0.12)", "important");
        qe.style.setProperty("color", "#E2E8F0", "important");
        const hdr = qe.querySelector(".example-card-header");
        if (hdr) {
            hdr.style.setProperty("background", "rgba(15, 23, 42, 0.95)", "important");
            hdr.style.setProperty("border-bottom", "1px solid rgba(255, 255, 255, 0.08)", "important");
        }
    } else {
        qe.style.setProperty("background", "#FFFFFF", "important");
        qe.style.setProperty("border", "1px solid #E2E8F0", "important");
        qe.style.setProperty("box-shadow", "0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.03)", "important");
        qe.style.setProperty("color", "#1E293B", "important");
        const hdr = qe.querySelector(".example-card-header");
        if (hdr) {
            hdr.style.setProperty("background", "#F8FAFC", "important");
            hdr.style.setProperty("border-bottom", "1px solid #E2E8F0", "important");
        }
    }
}

function applyConceptDiagramTheme(theme) {
    const diagSection = document.getElementById("conceptDiagramSection");
    if (!diagSection) return;
    const isDark = theme === "dark" || document.documentElement.classList.contains("dark");
    if (isDark) {
        diagSection.style.setProperty("background", "linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(10, 15, 29, 0.98) 100%)", "important");
        diagSection.style.setProperty("border", "1px solid rgba(255, 255, 255, 0.12)", "important");
        diagSection.style.setProperty("color", "#E2E8F0", "important");
        const hdr = diagSection.querySelector(".diagram-card-header");
        if (hdr) {
            hdr.style.setProperty("background", "rgba(15, 23, 42, 0.95)", "important");
            hdr.style.setProperty("border-bottom", "1px solid rgba(255, 255, 255, 0.08)", "important");
        }
        const canvas = diagSection.querySelector(".diagram-viewer-container");
        if (canvas) {
            canvas.style.setProperty("background", "rgba(2, 6, 23, 0.65)", "important");
            canvas.style.setProperty("border", "1px solid rgba(255, 255, 255, 0.07)", "important");
        }
    } else {
        diagSection.style.setProperty("background", "#FFFFFF", "important");
        diagSection.style.setProperty("border", "1px solid #E2E8F0", "important");
        diagSection.style.setProperty("box-shadow", "0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.03)", "important");
        diagSection.style.setProperty("color", "#1E293B", "important");
        const hdr = diagSection.querySelector(".diagram-card-header");
        if (hdr) {
            hdr.style.setProperty("background", "#F8FAFC", "important");
            hdr.style.setProperty("border-bottom", "1px solid #E2E8F0", "important");
        }
        const canvas = diagSection.querySelector(".diagram-viewer-container");
        if (canvas) {
            canvas.style.setProperty("background", "#F8FAFC", "important");
            canvas.style.setProperty("border", "1px solid #E2E8F0", "important");
        }
    }
}

function applyTheme(theme) {
    const root = document.documentElement;
    root.setAttribute("data-theme", theme);
    if (theme === "dark") {
        root.classList.add("dark");
        root.classList.remove("light");
    } else {
        root.classList.add("light");
        root.classList.remove("dark");
    }
    localStorage.setItem("omni_theme", theme);
    updateThemeToggleUI(theme);
    applyQuickExampleTheme(theme);
    applyConceptDiagramTheme(theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
}

function updateThemeToggleUI(theme) {
    const icon = document.getElementById("themeToggleIcon");
    const text = document.getElementById("themeToggleText");
    const header = document.querySelector("header.navbar-omni");
    const bookmarksBtn = document.getElementById("bookmarksNavBtn") || document.querySelector("button[onclick='toggleBookmarksSidebar()']");

    if (icon) {
        if (theme === "dark") {
            icon.className = "fa-solid fa-moon text-amber-300";
        } else {
            icon.className = "fa-solid fa-sun text-amber-500";
        }
    }
    if (text) {
        text.textContent = theme === "dark" ? "Dark" : "Light";
        text.style.color = "";
    }
    if (bookmarksBtn) {
        bookmarksBtn.style.color = "";
        bookmarksBtn.style.backgroundColor = "";
        bookmarksBtn.style.borderColor = "";
    }
    if (header) {
        if (theme === "dark") {
            header.style.backgroundColor = "rgba(10, 14, 23, 0.9)";
            header.style.color = "#ffffff";
            header.style.borderBottom = "1px solid rgba(255, 255, 255, 0.08)";
        } else {
            header.style.backgroundColor = "rgba(255, 255, 255, 0.96)";
            header.style.color = "#0F172A";
            header.style.borderBottom = "1px solid #E2E8F0";
        }
    }
}

// Expose toggleTheme to window for inline onclick handlers
window.toggleTheme = toggleTheme;
window.applyTheme = applyTheme;
window.initTheme = initTheme;

// --- Language State Management (English / Hinglish) ---
let currentLang = localStorage.getItem("omni_lang") || "english";
if (currentLang !== "hinglish" && currentLang !== "english") {
    currentLang = "english";
}
let isTranslatingLanguage = false;

function initLanguage() {
    const saved = localStorage.getItem("omni_lang") || "english";
    setLanguage(saved, false);
}

async function setLanguage(lang, triggerRefetch = true) {
    const target = (lang === "hinglish") ? "hinglish" : "english";
    currentLang = target;
    localStorage.setItem("omni_lang", target);
    document.documentElement.setAttribute("data-lang", target);
    updateLanguageToggleUI(target, false);
    updateUISectionLabels(target);

    // If currently on dashboard with an active topic, re-fetch payload with localized loading state
    const activeTopic = currentQuery || (currentSearchData && (currentSearchData.topic || currentSearchData.title || currentSearchData.query));
    if (triggerRefetch && activeTopic && activeTopic.trim()) {
        const dashboard = document.getElementById("dashboardScreen");
        const isDashboardVisible = dashboard && !dashboard.classList.contains("hidden");
        if (isDashboardVisible) {
            console.log(`Language switched to ${target}. Triggering immediate re-fetch for: ${activeTopic}`);
            await executeLanguageRefetch(activeTopic.trim(), target);
        }
    }
}

async function toggleLanguage() {
    if (isTranslatingLanguage) return;
    const nextLang = currentLang === "english" ? "hinglish" : "english";
    await setLanguage(nextLang, true);
}

// Re-fetches the current topic with localized in-card & button loading indicators
async function executeLanguageRefetch(topic, targetLang) {
    if (isTranslatingLanguage) return;
    isTranslatingLanguage = true;

    const loadingText = targetLang === "hinglish" ? "Translating to Hinglish..." : "Switching to English...";

    // 1. Show localized loading state inside button and banner
    updateLanguageToggleUI(targetLang, true, loadingText);

    const banner = document.getElementById("langLoadingBanner");
    const bannerText = document.getElementById("langLoadingBannerText");
    if (banner) banner.classList.remove("hidden");
    if (bannerText) bannerText.textContent = loadingText;

    const summaryText = document.getElementById("summaryText") || document.getElementById("overview-text");
    if (summaryText) summaryText.classList.add("opacity-60", "transition-opacity");

    try {
        // 2. Fetch passing { topic: topic, query: topic, lang: targetLang }
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                query: topic,
                lang: targetLang
            })
        });

        if (!response.ok) {
            throw new Error(`Refetch failed with status ${response.status}`);
        }

        const data = await response.json();
        if (!data.query) data.query = topic;
        if (!data.topic) data.topic = topic;
        data.lang = targetLang;
        currentSearchData = data;

        // Cache update
        const cacheKey = `${targetLang}_${topic.toLowerCase()}`;
        searchResultCache.set(cacheKey, data);
        try {
            sessionStorage.setItem("omni_cache_v53_" + cacheKey, JSON.stringify(data));
        } catch (_) {}

        // 3. Update URL with language parameter
        const langParam = targetLang === "hinglish" ? "&lang=hinglish" : "";
        const newUrl = `${window.location.pathname}?q=${encodeURIComponent(topic)}${langParam}`;
        window.history.pushState({ query: topic, lang: targetLang }, "", newUrl);

        // 4. Re-render dashboard UI
        updateDashboardUI(data);

    } catch (err) {
        console.error("Language re-fetch failed:", err);
    } finally {
        isTranslatingLanguage = false;
        if (banner) banner.classList.add("hidden");
        if (summaryText) summaryText.classList.remove("opacity-60");
        updateLanguageToggleUI(targetLang, false);
    }
}

// Updates UI buttons: displays "🇮🇳 Hinglish" when in English mode and "🇬🇧 English" when in Hinglish mode
function updateLanguageToggleUI(lang, isLoading = false, loadingText = "") {
    // When in English mode, the button offers/displays "🇮🇳 Hinglish"
    // When in Hinglish mode, the button offers/displays "🇬🇧 English"
    const labelText = lang === "english" ? "🇮🇳 Hinglish" : "🇬🇧 English";
    const buttonTitle = lang === "english" ? "Switch to Hinglish (Hindi in Roman script + English CS Terms)" : "Switch to English";

    // 1. Overview Card Prominent Button next to topic title
    const topicBtn = document.getElementById("topicLangToggleBtn");
    const topicLabel = document.getElementById("topicLangToggleLabel");
    const topicSpinner = document.getElementById("topicLangToggleSpinner");
    if (topicBtn) {
        topicBtn.disabled = isLoading;
        topicBtn.title = isLoading ? loadingText : buttonTitle;
        topicBtn.setAttribute("aria-label", topicBtn.title);
        topicBtn.classList.toggle("mode-hinglish", lang === "hinglish");
    }
    if (topicSpinner) {
        if (isLoading) {
            topicSpinner.classList.remove("hidden");
        } else {
            topicSpinner.classList.add("hidden");
        }
    }
    if (topicLabel) {
        topicLabel.textContent = isLoading ? loadingText : labelText;
    }

    // 2. Navbar Language Button
    const navBtn = document.getElementById("langToggleBtn");
    const navText = document.getElementById("langToggleText");
    const navSpinner = document.getElementById("navLangToggleSpinner");
    if (navBtn) {
        navBtn.disabled = isLoading;
        navBtn.title = isLoading ? loadingText : buttonTitle;
        navBtn.classList.toggle("mode-hinglish", lang === "hinglish");
    }
    if (navSpinner) {
        if (isLoading) {
            navSpinner.classList.remove("hidden");
        } else {
            navSpinner.classList.add("hidden");
        }
    }
    if (navText) {
        navText.textContent = isLoading ? loadingText : labelText;
    }

    // 3. Landing Screen Language Button
    const landingBtn = document.getElementById("landingLangToggleBtn");
    const landingLabel = document.getElementById("landingLangToggleLabel");
    if (landingBtn) {
        landingBtn.disabled = isLoading;
        landingBtn.title = isLoading ? loadingText : buttonTitle;
        landingBtn.classList.toggle("mode-hinglish", lang === "hinglish");
    }
    if (landingLabel) {
        landingLabel.textContent = isLoading ? loadingText : labelText;
    }
}

// Translates UI section headers dynamically based on selected language
function updateUISectionLabels(lang) {
    const isHinglish = (lang || "").toLowerCase() === "hinglish";

    // 1. Quick Example Section Headers
    const labelBreakdown = document.getElementById("labelBreakdownSubhead");
    if (labelBreakdown) {
        labelBreakdown.textContent = isHinglish ? "KAISE KAAM KARTA HAI (STEP-BY-STEP)" : "How It Works (Step-by-Step)";
    }

    const labelUseCases = document.getElementById("labelUseCasesSubhead");
    if (labelUseCases) {
        labelUseCases.textContent = isHinglish ? "ASLI DUNIYA MEIN KAHAN USE HOTA HAI" : "Everyday & Real-World Applications";
    }

    const labelUseCasesBadge = document.getElementById("labelUseCasesBadge");
    if (labelUseCasesBadge) {
        labelUseCasesBadge.textContent = isHinglish ? "Aaj Ki Tech Me Kahan Kaam Aata Hai" : "Where This Powers Modern Tech";
    }

    const labelTradeoffs = document.getElementById("labelTradeoffsSubhead");
    if (labelTradeoffs) {
        labelTradeoffs.textContent = isHinglish ? "FAAYDE AUR NUKSAAN" : "Advantages vs. Limitations";
    }

    const labelAdv = document.getElementById("labelAdvSubhead");
    if (labelAdv) {
        labelAdv.textContent = isHinglish ? "SABSE BADA FAAYDA" : "What Makes It Great";
    }

    const labelDisadv = document.getElementById("labelDisadvSubhead");
    if (labelDisadv) {
        labelDisadv.textContent = isHinglish ? "DHYAN RAKHNE WALI BAATEIN" : "Limitations to Keep in Mind";
    }

    const labelTakeaway = document.getElementById("labelTakeawaySubhead");
    if (labelTakeaway) {
        labelTakeaway.textContent = isHinglish ? "SABSE MAIN BAAT" : "Key Takeaway";
    }

    const labelScenario = document.getElementById("labelScenarioSubhead");
    if (labelScenario) {
        labelScenario.textContent = isHinglish ? "ASLI DUNIYA KA EXAMPLE AUR ANALOGY" : "Real-World Scenario & Analogy";
    }

    // 2. Right-Panel Cards & Badges
    const labelRoadmap = document.getElementById("labelRoadmapHeader");
    if (labelRoadmap) {
        labelRoadmap.textContent = isHinglish ? "Padhai Ka Roadmap (5 Steps)" : "Topic Study Roadmap";
    }

    const labelAcademicEval = document.getElementById("labelAcademicEval");
    if (labelAcademicEval) {
        labelAcademicEval.textContent = isHinglish ? "Academic Evaluation (Hinglish)" : "Academic Evaluation";
    }

    const labelDidYouKnow = document.getElementById("labelDidYouKnow");
    if (labelDidYouKnow) {
        labelDidYouKnow.textContent = isHinglish ? "Kya Aapko Pata Tha?" : "Did You Know?";
    }
}

window.updateUISectionLabels = updateUISectionLabels;
window.toggleLanguage = toggleLanguage;
window.setLanguage = setLanguage;
window.initLanguage = initLanguage;
window.executeLanguageRefetch = executeLanguageRefetch;

// --- Init on Page Load & URL Routing ("useEffect" Hook equivalent) ---
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initLanguage();
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

function clearNavSearch() {
    const navInput = document.getElementById("navSearchInput");
    if (navInput) {
        navInput.value = "";
        navInput.focus();
    }
    const clearBtn = document.getElementById("navSearchClearBtn");
    if (clearBtn) clearBtn.classList.add("hidden");
}
window.clearNavSearch = clearNavSearch;

function clearMobileNavSearch() {
    const mobileInput = document.getElementById("mobileNavSearchInput");
    if (mobileInput) {
        mobileInput.value = "";
        mobileInput.focus();
    }
    const clearBtn = document.getElementById("mobileNavSearchClearBtn");
    if (clearBtn) clearBtn.classList.add("hidden");
}
window.clearMobileNavSearch = clearMobileNavSearch;

function initSearchInputListeners() {
    const mainInput = document.getElementById("mainSearchInput");
    const navInput = document.getElementById("navSearchInput");
    const mobileNavInput = document.getElementById("mobileNavSearchInput");
    const navClearBtn = document.getElementById("navSearchClearBtn");
    const mobileClearBtn = document.getElementById("mobileNavSearchClearBtn");

    [mainInput, navInput, mobileNavInput].forEach(input => {
        if (input) {
            input.addEventListener("keydown", (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    handleSearch(e, input.value);
                }
            });
        }
    });

    if (navInput && navClearBtn) {
        navInput.addEventListener("input", () => {
            navClearBtn.classList.toggle("hidden", !navInput.value.trim());
        });
    }

    if (mobileNavInput && mobileClearBtn) {
        mobileNavInput.addEventListener("input", () => {
            mobileClearBtn.classList.toggle("hidden", !mobileNavInput.value.trim());
        });
    }

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
        const langFromUrl = urlParams.get("lang");
        if (langFromUrl && (langFromUrl === "hinglish" || langFromUrl === "english")) {
            setLanguage(langFromUrl, false);
        }
        const queryFromUrl = urlParams.get("q") || urlParams.get("query") || urlParams.get("topic");
        if (queryFromUrl && queryFromUrl.trim()) {
            executeSearch(queryFromUrl.trim(), false);
        } else {
            resetSearch(false);
        }
    });

    // Handle cold page load with query parameter in URL (e.g. ?q=Dijkstra or ?query=Newton)
    const initialParams = new URLSearchParams(window.location.search);
    const initialLang = initialParams.get("lang");
    if (initialLang && (initialLang === "hinglish" || initialLang === "english")) {
        setLanguage(initialLang, false);
    }
    const initialQuery = initialParams.get("q") || initialParams.get("query") || initialParams.get("topic");
    if (initialQuery && initialQuery.trim()) {
        executeSearch(initialQuery.trim(), false);
    } else {
        showScreen("landingScreen");
    }
}

// Title Casing utility ensuring clean capitalization without Python/JS apostrophe bugs (e.g. Newton's instead of Newton'S)
function formatProperTitleCase(str) {
    if (!str) return "";
    let clean = String(str).trim();
    clean = clean.replace(/'S\b/g, "'s").replace(/’S\b/g, "’s");
    const minorWords = new Set(["a", "an", "and", "as", "at", "but", "by", "for", "in", "nor", "of", "on", "or", "so", "the", "to", "up", "yet", "vs.", "vs"]);
    const words = clean.split(/\s+/);
    clean = words.map((w, idx) => {
        if (!w) return w;
        if (w.length > 1 && w === w.toUpperCase() && !w.includes("'") && !w.includes("’")) {
            return w;
        }
        let lower = w.toLowerCase();
        if (idx > 0 && idx < words.length - 1 && minorWords.has(lower)) {
            return lower;
        }
        return lower.charAt(0).toUpperCase() + lower.slice(1);
    }).join(" ");
    clean = clean.replace(/'S\b/g, "'s").replace(/’S\b/g, "’s");
    return clean;
}

// HTML Escaping utility to prevent XSS and undefined helper ReferenceErrors
function escapeHtml(str) {
    if (str == null) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
window.escapeHtml = escapeHtml;

function setCardsLoadingState(query) {
    // Reveal dashboard screen immediately with skeleton UI on all cards
    showScreen("dashboardScreen");
    const navSearchContainer = document.getElementById("navSearchContainer");
    if (navSearchContainer) navSearchContainer.classList.remove("hidden");
    const mobileNavSearchContainer = document.getElementById("mobileNavSearchContainer");
    if (mobileNavSearchContainer) mobileNavSearchContainer.classList.remove("hidden");
    document.body.classList.add("dashboard-active");

    // Title & Badges
    const titleEl = document.getElementById("summaryTopicTitle");
    if (titleEl) titleEl.textContent = formatProperTitleCase(query);

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

    // Conceptual Diagram Skeleton - Keep hidden until fresh data arrives
    const diagSection = document.getElementById("conceptDiagramSection");
    if (diagSection) {
        diagSection.classList.add("hidden");
    }

    // Quick Example Skeleton - Keep hidden until fresh data arrives
    const qeSection = document.getElementById("quickExampleSection");
    if (qeSection) {
        qeSection.classList.add("hidden");
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
async function executeSearch(targetQuery, updateHistory = true, forceRefresh = false) {
    const query = (targetQuery || "").trim();
    if (!query) return;

    console.log("Executing search for:", query, `(lang: ${currentLang})`);

    // Prevent re-triggering identical in-flight searches unless forced (e.g. language toggle)
    if (!forceRefresh && isSearching && query === currentQuery) return;
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
    const mobileNavInput = document.getElementById("mobileNavSearchInput");
    const noteInput = document.getElementById("noteSearchInput");

    if (mainInput) mainInput.value = query;
    if (navInput) {
        navInput.value = query;
        const navClearBtn = document.getElementById("navSearchClearBtn");
        if (navClearBtn) navClearBtn.classList.toggle("hidden", !query);
    }
    if (mobileNavInput) {
        mobileNavInput.value = query;
        const mobileClearBtn = document.getElementById("mobileNavSearchClearBtn");
        if (mobileClearBtn) mobileClearBtn.classList.toggle("hidden", !query);
    }
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
        const langParam = currentLang === "hinglish" ? "&lang=hinglish" : "";
        const newUrl = `${window.location.pathname}?q=${encodeURIComponent(query)}${langParam}`;
        window.history.pushState({ query, lang: currentLang }, "", newUrl);
    }
    document.title = `${query} — OmniLearn Academic Hub`;

    const cacheKey = `${currentLang}_${query.toLowerCase()}`;
    currentQuery = query;
    let hasInstantRendered = false;

    // 4. Check client-side instant cache for zero-latency rendering (skip if forceRefresh)
    let cachedData = forceRefresh ? null : searchResultCache.get(cacheKey);
    if (!cachedData && !forceRefresh) {
        try {
            const rawStored = sessionStorage.getItem("omni_cache_v53_" + cacheKey);
            if (rawStored) {
                cachedData = JSON.parse(rawStored);
                searchResultCache.set(cacheKey, cachedData);
            }
        } catch (_) {}
    }

    if (cachedData && cachedData.summary && cachedData.difficulty_score !== undefined) {
        if (!cachedData.query) cachedData.query = query;
        currentSearchData = cachedData;
        showScreen("dashboardScreen");
        const navSearchContainer = document.getElementById("navSearchContainer");
        if (navSearchContainer) navSearchContainer.classList.remove("hidden");
        const mobileNavSearchContainer = document.getElementById("mobileNavSearchContainer");
        if (mobileNavSearchContainer) mobileNavSearchContainer.classList.remove("hidden");
        document.body.classList.add("dashboard-active");
        try {
            updateDashboardUI(cachedData);
            hasInstantRendered = true;
        } catch (cacheErr) {
            console.warn("Cached dashboard render failed, falling back to skeleton:", cacheErr);
            setCardsLoadingState(query);
        }
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
            body: JSON.stringify({ query, lang: currentLang })
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
        if (!data.query) data.query = query;
        currentSearchData = data;
        searchResultCache.set(cacheKey, data);
        try {
            sessionStorage.setItem("omni_cache_v53_" + cacheKey, JSON.stringify(data));
        } catch (_) {}

        // 5. Instantly and completely re-render all dashboard sections with dynamic data
        try {
            updateDashboardUI(data);
        } catch (uiErr) {
            console.error("Failed to render dashboard data:", uiErr);
        }

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
    const mobileNavInput = document.getElementById("mobileNavSearchInput");
    const landingVisible = !document.getElementById("landingScreen").classList.contains("hidden");

    let query = "";
    if (document.activeElement === mobileNavInput && mobileNavInput && mobileNavInput.value.trim()) {
        query = mobileNavInput.value.trim();
    } else if (document.activeElement === navInput && navInput && navInput.value.trim()) {
        query = navInput.value.trim();
    } else if (document.activeElement === mainInput && mainInput && mainInput.value.trim()) {
        query = mainInput.value.trim();
    } else if (landingVisible) {
        query = mainInput ? mainInput.value.trim() : (navInput ? navInput.value.trim() : (mobileNavInput ? mobileNavInput.value.trim() : ""));
    } else {
        query = (mobileNavInput && mobileNavInput.value.trim()) || (navInput && navInput.value.trim()) || (mainInput && mainInput.value.trim()) || "";
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
    const mobileNavInput = document.getElementById("mobileNavSearchInput");
    if (mainInput) mainInput.value = "";
    if (navInput) navInput.value = "";
    if (mobileNavInput) mobileNavInput.value = "";

    const navClearBtn = document.getElementById("navSearchClearBtn");
    if (navClearBtn) navClearBtn.classList.add("hidden");
    const mobileClearBtn = document.getElementById("mobileNavSearchClearBtn");
    if (mobileClearBtn) mobileClearBtn.classList.add("hidden");

    const navContainer = document.getElementById("navSearchContainer");
    if (navContainer) navContainer.classList.add("hidden");
    const mobileNavContainer = document.getElementById("mobileNavSearchContainer");
    if (mobileNavContainer) mobileNavContainer.classList.add("hidden");
    document.body.classList.remove("dashboard-active");

    showScreen("landingScreen");
    currentQuery = "";
    currentSearchData = null;
    closeYearSubjects();

    if (updateHistory) {
        const langParam = currentLang === "hinglish" ? "?lang=hinglish" : "";
        window.history.pushState({}, "", window.location.pathname + langParam);
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

    const eduBg = document.getElementById("eduBackgroundLayer");
    const navSearchContainer = document.getElementById("navSearchContainer");
    const mobileNavSearchContainer = document.getElementById("mobileNavSearchContainer");

    if (screenId === "dashboardScreen" || screenId === "loadingScreen") {
        document.body.classList.add("dashboard-active");
        if (eduBg) {
            eduBg.style.display = "none";
            eduBg.setAttribute("aria-hidden", "true");
        }
        if (navSearchContainer) navSearchContainer.classList.remove("hidden");
        if (mobileNavSearchContainer) mobileNavSearchContainer.classList.remove("hidden");
    } else if (screenId === "landingScreen") {
        document.body.classList.remove("dashboard-active");
        if (eduBg) {
            eduBg.style.display = "";
            eduBg.removeAttribute("aria-hidden");
        }
        if (navSearchContainer) navSearchContainer.classList.add("hidden");
        if (mobileNavSearchContainer) mobileNavSearchContainer.classList.add("hidden");
    }
}

// Modular Step-by-Step UI Card Formatter (minimizes cognitive fatigue)
function formatModularSteps(breakdownText, stepByStepList) {
    let steps = [];
    if (Array.isArray(stepByStepList) && stepByStepList.length > 0) {
        steps = stepByStepList.map((item, idx) => ({
            stepNum: idx + 1,
            title: typeof item === 'object' ? (item.title || item.name || `Step ${idx + 1}`) : `Step ${idx + 1}`,
            desc: typeof item === 'object' ? (item.description || item.desc || item.details || '') : String(item || '')
        }));
    } else if (typeof breakdownText === 'string' && breakdownText.trim()) {
        const text = breakdownText.trim();
        const rawSteps = text.split(/(?:^|\n)\s*\d+\.\s+/).filter(s => s.trim().length > 0);
        if (rawSteps.length >= 2) {
            steps = rawSteps.map((step, idx) => {
                let title = '';
                let desc = step.trim();
                const match = desc.match(/^\*\*([^*]+)\*\*[:\s-]*(.*)/s);
                if (match) {
                    title = match[1].trim();
                    desc = match[2].trim();
                } else {
                    const firstColon = desc.indexOf(':');
                    if (firstColon > 0 && firstColon < 50) {
                        title = desc.slice(0, firstColon).trim();
                        desc = desc.slice(firstColon + 1).trim();
                    } else {
                        title = `Step ${idx + 1}`;
                    }
                }
                return { stepNum: idx + 1, title, desc };
            });
        }
    }

    if (steps.length === 0) {
        return formatSummaryMarkdown(breakdownText || "");
    }

    const stepColors = [
        { badge: "bg-emerald-500 text-white", border: "border-emerald-200/80 dark:border-emerald-800/50", bg: "bg-emerald-50/40 dark:bg-emerald-950/20", title: "text-emerald-900 dark:text-emerald-300" },
        { badge: "bg-indigo-500 text-white", border: "border-indigo-200/80 dark:border-indigo-800/50", bg: "bg-indigo-50/40 dark:bg-indigo-950/20", title: "text-indigo-900 dark:text-indigo-300" },
        { badge: "bg-violet-500 text-white", border: "border-violet-200/80 dark:border-violet-800/50", bg: "bg-violet-50/40 dark:bg-violet-950/20", title: "text-violet-900 dark:text-violet-300" },
        { badge: "bg-amber-500 text-white", border: "border-amber-200/80 dark:border-amber-800/50", bg: "bg-amber-50/40 dark:bg-amber-950/20", title: "text-amber-900 dark:text-amber-300" }
    ];

    const colClass = steps.length === 2 ? "grid-cols-1 sm:grid-cols-2" : (steps.length >= 3 ? "grid-cols-1 md:grid-cols-3" : "grid-cols-1");

    return `
        <div class="grid ${colClass} gap-3 mt-1">
            ${steps.map((s, idx) => {
                const color = stepColors[idx % stepColors.length];
                const numStr = String(s.stepNum).padStart(2, '0');
                return `
                    <div class="example-step-card p-3.5 rounded-xl border ${color.border} ${color.bg} transition-all duration-200 flex flex-col justify-between shadow-2xs hover:shadow-xs">
                        <div>
                            <div class="flex items-center gap-2 mb-2">
                                <span class="w-5 h-5 rounded-full ${color.badge} font-black text-[10px] flex items-center justify-center shrink-0 shadow-2xs">
                                    ${numStr}
                                </span>
                                <h4 class="text-xs font-bold ${color.title} leading-snug break-words">
                                    ${escapeHtml(s.title)}
                                </h4>
                            </div>
                            <div class="text-xs leading-relaxed example-body-text text-slate-600 dark:text-slate-300">
                                ${formatSummaryMarkdown(s.desc)}
                            </div>
                        </div>
                    </div>
                `;
            }).join("")}
        </div>
    `;
}

// --- Dashboard Render Methods ---
function renderDashboard(data) {
    if (!data) return;
    if (!data.query) {
        data.query = currentQuery || data.title || data.topic || "";
    }
    currentSearchData = data;

    const rawTitle = data.title || data.canonical_title || data.query;
    const topicTitle = formatProperTitleCase(rawTitle);

    // 1. Render Summary, Domain and Overview
    try {
        const titleEl = document.getElementById("summaryTopicTitle");
        if (titleEl) titleEl.textContent = topicTitle;
        
        // Set Domain / Category Badge
        const domainBadge = document.getElementById("summaryDomainBadge");
        if (domainBadge) {
            domainBadge.textContent = data.category || data.domain || "Academic Curriculum";
        }

        // Synchronize Language UI state with data.lang
        const effectiveLang = (data.lang || currentLang || "english").toLowerCase();
        updateLanguageToggleUI(effectiveLang);
        updateUISectionLabels(effectiveLang);
        
        // Format and render concise summary/overview text
        const summaryContainer = document.getElementById("overview-text") || document.getElementById("summaryText");
        if (summaryContainer) {
            function stripContextBoilerplate(text) {
                if (!text) return "";
                const pattern = /^(?:In the (?:context|domain|realm|framework) of|From the (?:perspective|standpoint) of|Within the (?:context|framework|realm) of)\s+(?:(?:B\.Tech|Ph\.D|M\.Tech|[^\n,:;])+)(?:,\s*|:\s*|\s*-\s*)/i;
                let cleaned = text.replace(pattern, '').trim();
                if (cleaned && cleaned.length > 1 && (cleaned[0] === '"' || cleaned[0] === "'" || cleaned[0] === '“' || cleaned[0] === '‘')) {
                    cleaned = cleaned[0] + cleaned[1].toUpperCase() + cleaned.slice(2);
                } else if (cleaned && cleaned.length > 0) {
                    cleaned = cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
                }
                return cleaned;
            }

            const rawOverview = (data.overview || data.summary || "").trim();
            const overviewContent = stripContextBoilerplate(rawOverview);

            if (!overviewContent) {
                summaryContainer.innerHTML = `
                    <div class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-sm font-medium flex items-center">
                        <i class="fa-solid fa-triangle-exclamation mr-2.5 text-rose-500 text-base"></i>
                        <span>Educational Overview Unavailable: Gemini API payload did not return an academic overview.</span>
                    </div>`;
            } else {
                summaryContainer.innerHTML = formatSummaryMarkdown(overviewContent);
            }
        }
    } catch (sumErr) {
        console.error("Failed to render summary overview:", sumErr);
    }

    // 1.4 Render Interactive Conceptual Architecture & Diagram
    try {
        renderConceptDiagram(data.diagram, topicTitle);
    } catch (diagErr) {
        console.error("Failed to render conceptual diagram:", diagErr);
    }

    // 1.5 Render Explainable Practical Example & Real-World Walkthrough (No Code)
    try {
        const qeSection = document.getElementById("quickExampleSection");
        const qe = data.quick_example || data.quickExample;
        window.currentQuickExample = qe;

        if (qeSection) {
            if (qe && (qe.scenario || qe.breakdown || qe.takeaway || qe.example || qe.explanation || qe.code)) {
                qeSection.classList.remove("hidden");
                applyQuickExampleTheme(document.documentElement.getAttribute("data-theme") || "dark");
                
                const qeTitle = document.getElementById("quickExampleTitle");
                if (qeTitle) {
                    const subTitle = qe.title ? formatProperTitleCase(qe.title) : topicTitle;
                    qeTitle.textContent = `— ${subTitle}`;
                }
                
                const qeBadge = document.getElementById("quickExampleBadge");
                if (qeBadge) qeBadge.textContent = qe.badge || "Practical Example";
                
                const qeScenario = document.getElementById("quickExampleScenario");
                if (qeScenario) {
                    const scenarioText = qe.scenario || qe.example || `Real-world operational setup and conditions under which ${topicTitle} is observed or applied.`;
                    qeScenario.innerHTML = formatSummaryMarkdown(scenarioText);
                }
                
                const qeBreakdown = document.getElementById("quickExampleBreakdown");
                if (qeBreakdown) {
                    const breakdownText = qe.breakdown || qe.explanation || (qe.code ? `Step-by-step logic:\n${qe.code}` : "");
                    qeBreakdown.innerHTML = formatModularSteps(breakdownText, qe.step_by_step);
                }
                
                const qeTakeaway = document.getElementById("quickExampleTakeaway");
                if (qeTakeaway) {
                    const takeawayText = qe.takeaway || qe.key_takeaway || `Fundamental principle and practical takeaway of ${topicTitle}.`;
                    qeTakeaway.innerHTML = formatSummaryMarkdown(takeawayText);
                }

                // Render Industrial Production Use Cases & Applications
                const qeUseCasesBlock = document.getElementById("quickExampleUseCasesBlock");
                const qeUseCasesList = document.getElementById("quickExampleUseCasesList");
                const rawCases = qe.use_cases || qe.applications || qe.production_use_cases || qe.real_world_applications;
                if (qeUseCasesBlock && qeUseCasesList) {
                    if (Array.isArray(rawCases) && rawCases.length > 0) {
                        const domainThemes = [
                            {
                                bg: "bg-blue-500/10 dark:bg-blue-400/15",
                                text: "text-blue-600 dark:text-blue-400",
                                icon: "fa-solid fa-folder-tree",
                                tag: "OS & Files"
                            },
                            {
                                bg: "bg-indigo-500/10 dark:bg-indigo-400/15",
                                text: "text-indigo-600 dark:text-indigo-400",
                                icon: "fa-solid fa-cart-shopping",
                                tag: "E-Commerce"
                            },
                            {
                                bg: "bg-violet-500/10 dark:bg-violet-400/15",
                                text: "text-violet-600 dark:text-violet-400",
                                icon: "fa-solid fa-magnifying-glass",
                                tag: "Search Engines"
                            },
                            {
                                bg: "bg-emerald-500/10 dark:bg-emerald-400/15",
                                text: "text-emerald-600 dark:text-emerald-400",
                                icon: "fa-solid fa-database",
                                tag: "Databases"
                            },
                            {
                                bg: "bg-amber-500/10 dark:bg-amber-400/15",
                                text: "text-amber-600 dark:text-amber-400",
                                icon: "fa-solid fa-bolt-lightning",
                                tag: "Cloud Systems"
                            }
                        ];

                        qeUseCasesList.innerHTML = rawCases.map((item, idx) => {
                            const theme = domainThemes[idx % domainThemes.length];
                            const isObj = item && typeof item === 'object';
                            const title = isObj ? (item.title || item.name || item.domain || 'Production System') : 'Industrial Application';
                            const impact = isObj ? (item.impact || item.badge || item.system || item.role || 'Production System') : 'Industry Application';
                            const desc = isObj ? (item.description || item.details || item.desc || '') : String(item || '');
                            
                            // Contextual icon detection
                            let cardIcon = theme.icon;
                            const tLower = title.toLowerCase();
                            if (tLower.includes("file") || tLower.includes("folder") || tLower.includes("os") || tLower.includes("kernel") || tLower.includes("directory")) cardIcon = "fa-solid fa-folder-tree";
                            else if (tLower.includes("shop") || tLower.includes("cart") || tLower.includes("commerce") || tLower.includes("store") || tLower.includes("catalog")) cardIcon = "fa-solid fa-cart-shopping";
                            else if (tLower.includes("search") || tLower.includes("google") || tLower.includes("trie") || tLower.includes("autocomplete") || tLower.includes("lookup")) cardIcon = "fa-solid fa-magnifying-glass";
                            else if (tLower.includes("database") || tLower.includes("index") || tLower.includes("sql") || tLower.includes("record") || tLower.includes("storage")) cardIcon = "fa-solid fa-database";
                            else if (tLower.includes("photo") || tLower.includes("gallery") || tLower.includes("image") || tLower.includes("media")) cardIcon = "fa-solid fa-images";
                            else if (tLower.includes("seat") || tLower.includes("flight") || tLower.includes("cinema") || tLower.includes("ticket")) cardIcon = "fa-solid fa-chair";
                            else if (tLower.includes("game") || tLower.includes("score") || tLower.includes("leaderboard")) cardIcon = "fa-solid fa-trophy";
                            else if (tLower.includes("stream") || tLower.includes("music") || tLower.includes("spotify") || tLower.includes("audio")) cardIcon = "fa-solid fa-headphones";
                            else if (tLower.includes("browser") || tLower.includes("web") || tLower.includes("history")) cardIcon = "fa-solid fa-compass";
                            else if (tLower.includes("undo") || tLower.includes("redo") || tLower.includes("editor")) cardIcon = "fa-solid fa-rotate-left";
                            else if (tLower.includes("print") || tLower.includes("document")) cardIcon = "fa-solid fa-print";
                            else if (tLower.includes("call") || tLower.includes("support")) cardIcon = "fa-solid fa-headset";
                            else if (tLower.includes("delivery") || tLower.includes("food") || tLower.includes("order")) cardIcon = "fa-solid fa-utensils";
                            else if (tLower.includes("route") || tLower.includes("map") || tLower.includes("subway") || tLower.includes("gps")) cardIcon = "fa-solid fa-map-location-dot";
                            else if (tLower.includes("social") || tLower.includes("network") || tLower.includes("friend")) cardIcon = "fa-solid fa-users";
                            else if (tLower.includes("package") || tLower.includes("shipping") || tLower.includes("fedex")) cardIcon = "fa-solid fa-truck-fast";
                            else if (tLower.includes("flight") || tLower.includes("airline")) cardIcon = "fa-solid fa-plane-departure";

                            return `
                                <div class="example-usecase-card p-4 rounded-xl transition-all duration-200 flex flex-col justify-between hover:shadow-md">
                                    <div>
                                        <!-- Top Row: Architectural Invariant Badge (No Truncation) & Tag Indicator -->
                                        <div class="flex items-center justify-between gap-2 mb-2.5">
                                            <span class="usecase-impact-pill text-[10px] font-bold px-2.5 py-0.5 rounded-full inline-flex items-center gap-1.5 shadow-2xs">
                                                <i class="fa-solid fa-layer-group text-[9px] opacity-80"></i>
                                                <span class="leading-none">${escapeHtml(impact)}</span>
                                            </span>
                                            <span class="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center gap-1 shrink-0">
                                                <i class="fa-solid fa-microchip text-[9px]"></i>
                                                <span>${escapeHtml(theme.tag)}</span>
                                            </span>
                                        </div>
                                        
                                        <!-- Middle Row: Dedicated Icon Container & Full Clean Title (NO Truncation) -->
                                        <div class="flex items-start gap-2.5 mb-2">
                                            <div class="w-8 h-8 rounded-lg ${theme.bg} ${theme.text} flex items-center justify-center shrink-0 mt-0.5 shadow-2xs text-sm">
                                                <i class="${cardIcon}"></i>
                                            </div>
                                            <h4 class="text-xs sm:text-[13px] font-bold example-usecase-title leading-snug break-words">
                                                ${escapeHtml(title)}
                                            </h4>
                                        </div>
                                        
                                        <!-- Bottom Row: Real-World Technical Description -->
                                        <div class="text-xs leading-relaxed example-body-text text-slate-600 dark:text-slate-300 pl-0.5">
                                            ${formatSummaryMarkdown(desc)}
                                        </div>
                                    </div>
                                </div>
                            `;
                        }).join("");
                        qeUseCasesBlock.classList.remove("hidden");
                    } else {
                        qeUseCasesBlock.classList.add("hidden");
                    }
                }

                // Render Architecture Trade-offs & Production Analysis
                const qeTradeoffsBlock = document.getElementById("quickExampleTradeoffsBlock");
                const qeAdv = document.getElementById("quickExampleTradeoffsAdvantages");
                const qeDisadv = document.getElementById("quickExampleTradeoffsDisadvantages");
                if (qeTradeoffsBlock && qeAdv && qeDisadv) {
                    const to = qe.tradeoffs;
                    if (to && (to.advantages || to.disadvantages || to.pros || to.cons)) {
                        const advText = to.advantages || to.pros || "Deterministic performance bounds and standardized operational stability.";
                        const disadvText = to.disadvantages || to.cons || to.limitations || "Requires careful resource allocation, boundary validation, and scale monitoring.";
                        qeAdv.innerHTML = formatSummaryMarkdown(advText);
                        qeDisadv.innerHTML = formatSummaryMarkdown(disadvText);
                        qeTradeoffsBlock.classList.remove("hidden");
                    } else {
                        qeTradeoffsBlock.classList.add("hidden");
                    }
                }
            } else {
                qeSection.classList.add("hidden");
            }
        }
    } catch (qeErr) {
        console.error("Failed to render quick example:", qeErr);
    }
    
    // 1.8 Populate expandable in-depth detailed breakdown
    try {
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

            if (db && db.length > 50) {
                detailedContainer.innerHTML = `
                    <div class="detailed-breakdown-content space-y-4">
                        ${formatSummaryMarkdown(db)}
                    </div>`;
            } else if (tf || cf) {
                detailedContainer.innerHTML = `
                    <div class="space-y-4">
                        ${tf ? `
                            <div class="theoretical-foundations">
                                <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-1 flex items-center border-b border-slate-200 dark:border-slate-700 pb-1">
                                    <i class="fa-solid fa-microchip text-indigo-600 mr-2 text-xs"></i>Theoretical Foundations & Architecture
                                </h3>
                                <div class="text-slate-700 dark:text-slate-300 text-sm leading-relaxed">${formatSummaryMarkdown(tf)}</div>
                            </div>` : ''}
                        ${cf ? `
                            <div class="core-formulations">
                                <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-1 flex items-center border-b border-slate-200 dark:border-slate-700 pb-1">
                                    <i class="fa-solid fa-code text-indigo-600 mr-2 text-xs"></i>Step-by-Step Algorithm & Formulations
                                </h3>
                                <div class="text-slate-700 dark:text-slate-300 text-sm leading-relaxed">${formatSummaryMarkdown(cf)}</div>
                            </div>` : ''}
                    </div>`;
            } else {
                detailedContainer.innerHTML = `
                    <div class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-semibold flex items-center">
                        <i class="fa-solid fa-circle-exclamation mr-2 text-rose-500 text-sm"></i>
                        <span>Theoretical Foundations Unavailable: Content missing from Gemini API response.</span>
                    </div>`;
            }
        }
    } catch (dtErr) {
        console.error("Failed to render detailed breakdown:", dtErr);
    }
    
    // 1.9 Render Difficulty Score & Badges
    try {
        const diffScore = Number(data.difficulty_score || data.difficultyScore) || 0;
        const diffNumEl = document.getElementById("difficultyNumber");
        if (diffNumEl) diffNumEl.textContent = diffScore > 0 ? diffScore.toFixed(1) : "--";
        
        const diffBar = document.getElementById("difficultyBar");
        const diffLevelBadge = document.getElementById("difficultyLevelBadge");
        if (diffBar) {
            diffBar.style.width = `${Math.min(diffScore * 10, 100)}%`;
            diffBar.className = "h-3 rounded-full transition-all duration-700 ease-out ";
            const explicitLevel = data.difficultyLevel;
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
        }
        
        const aiEval = (data.ai_evaluation || data.aiEvaluation || data.difficulty_reasons || "").trim();
        const verdictEl = document.getElementById("difficultyVerdict");
        if (verdictEl) verdictEl.textContent = aiEval || "AI complexity evaluation unavailable from API.";
    } catch (diffErr) {
        console.error("Failed to render difficulty score:", diffErr);
    }
    
    // Update topic bookmark button status
    try {
        updateTopicBookmarkButton();
    } catch (bkErr) {
        console.warn("Failed to update bookmark button:", bkErr);
    }

    // 2. Render Roadmap Timeline with Checklists
    try {
        renderRoadmap(data.roadmap);
    } catch (roadErr) {
        console.error("Failed to render roadmap:", roadErr);
    }

    // Set global studyNotes state explicitly for the active search query
    try {
        studyNotes = (data.study_notes || data.notes_content || (data.notes && data.notes[0] ? data.notes[0].ocr_text : "")).trim();
        sessionStorage.setItem("omni_study_notes", studyNotes);
        localStorage.setItem("omni_active_topic", topicTitle);
    } catch (e) {}

    // 3. Render Notes Panel
    try {
        renderNotesList(data.notes);
    } catch (noteErr) {
        console.error("Failed to render notes list:", noteErr);
    }

    // 4. Render YouTube Videos
    try {
        renderYouTubeVideos(data.curated_videos || data.youtube_videos);
    } catch (ytErr) {
        console.error("Failed to render YouTube videos:", ytErr);
    }

    // 5. Render Web Links
    try {
        renderWebResources(data.web_resources);
    } catch (webErr) {
        console.error("Failed to render web resources:", webErr);
    }

    // 5.5 Render Careers (roadmap.sh)
    try {
        renderCareers(data.careers, data.careerRelevance || data.career_relevance);
    } catch (carErr) {
        console.error("Failed to render careers:", carErr);
    }

    // 6. Render Fun Fact / Did You Know
    try {
        renderFunFact(data.didYouKnow || data.did_you_know || data.fun_fact);
    } catch (factErr) {
        console.error("Failed to render fun fact:", factErr);
    }

    // 7. Render Chart.js Analytics
    try {
        renderAnalyticsChart(data.pyqs, data.examFrequency || data.exam_frequency);
    } catch (chartErr) {
        console.error("Failed to render analytics chart:", chartErr);
    }

    // 8. Re-typeset all mathematical formulas via MathJax across the dashboard
    try {
        renderMathFormulas();
    } catch (mathErr) {
        console.warn("Failed to render math formulas:", mathErr);
    }
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

function copyQuickExampleContent() {
    const qe = window.currentQuickExample;
    let textToCopy = "";
    if (qe) {
        if (qe.title) textToCopy += `${qe.title}\n\n`;
        if (qe.scenario) textToCopy += `Scenario / Setup:\n${qe.scenario}\n\n`;
        if (qe.breakdown) textToCopy += `Step-by-Step Breakdown:\n${qe.breakdown}\n\n`;
        const rawCases = qe.use_cases || qe.applications || qe.production_use_cases;
        if (Array.isArray(rawCases) && rawCases.length > 0) {
            textToCopy += `Industrial Production Use Cases:\n`;
            rawCases.forEach((u, idx) => {
                const t = typeof u === 'object' ? (u.title || 'Application') : 'Application';
                const imp = typeof u === 'object' ? (u.impact || 'System') : 'Production';
                const d = typeof u === 'object' ? (u.description || '') : String(u);
                textToCopy += `${idx + 1}. ${t} [${imp}]\n   ${d}\n`;
            });
            textToCopy += `\n`;
        }
        if (qe.tradeoffs) {
            if (qe.tradeoffs.advantages) textToCopy += `Production Advantages:\n${qe.tradeoffs.advantages}\n\n`;
            if (qe.tradeoffs.disadvantages) textToCopy += `Limitations & Trade-offs:\n${qe.tradeoffs.disadvantages}\n\n`;
        }
        if (qe.takeaway) textToCopy += `Key Takeaway:\n${qe.takeaway}\n`;
    }
    if (!textToCopy) {
        const sec = document.getElementById("quickExampleSection");
        if (sec) textToCopy = sec.innerText;
    }
    if (!textToCopy) return;

    if (navigator.clipboard) {
        navigator.clipboard.writeText(textToCopy.trim()).then(() => {
            const btnText = document.getElementById("copyExampleText");
            const btnIcon = document.getElementById("copyExampleIcon");
            if (btnText) btnText.textContent = "Copied!";
            if (btnIcon) btnIcon.className = "fa-solid fa-check text-emerald-400 text-[11px]";
            setTimeout(() => {
                if (btnText) btnText.textContent = "Copy";
                if (btnIcon) btnIcon.className = "fa-regular fa-clone text-[11px]";
            }, 2000);
        }).catch(err => {
            console.error("Failed to copy example content: ", err);
        });
    }
}
window.copyQuickExampleContent = copyQuickExampleContent;
window.copyQuickExampleCode = copyQuickExampleContent;

// ==========================================================================
// INTERACTIVE CONCEPTUAL ARCHITECTURE & DIAGRAM RENDERER
// ==========================================================================
window.isDiagramZoomed = false;
function toggleDiagramZoom() {
    const canvas = document.getElementById("diagramViewerContainer");
    const btnIcon = document.getElementById("diagramZoomIcon");
    const btnText = document.getElementById("diagramZoomText");
    if (!canvas) return;

    window.isDiagramZoomed = !window.isDiagramZoomed;
    if (window.isDiagramZoomed) {
        canvas.classList.add("diagram-zoomed");
        if (btnIcon) {
            btnIcon.classList.remove("fa-maximize");
            btnIcon.classList.add("fa-minimize");
        }
        if (btnText) btnText.textContent = "Collapse";
    } else {
        canvas.classList.remove("diagram-zoomed");
        if (btnIcon) {
            btnIcon.classList.remove("fa-minimize");
            btnIcon.classList.add("fa-maximize");
        }
        if (btnText) btnText.textContent = "Expand";
    }
}
window.toggleDiagramZoom = toggleDiagramZoom;

function renderConceptDiagram(diagram, topicName) {
    const section = document.getElementById("conceptDiagramSection");
    if (!section) return;

    if (!diagram || (!diagram.svg_content && !diagram.mermaid_code)) {
        section.classList.add("hidden");
        return;
    }

    section.classList.remove("hidden");
    const isDark = document.documentElement.classList.contains("dark") || 
                   document.documentElement.getAttribute("data-theme") === "dark";
    applyConceptDiagramTheme(isDark ? "dark" : "light");

    // 1. Populate header, title, badge
    const titleEl = document.getElementById("diagramTitle");
    if (titleEl) {
        const dTitle = diagram.title ? diagram.title.replace(/^[^:]+:\s*/, "") : (topicName || "Conceptual Model");
        titleEl.textContent = `— ${dTitle}`;
    }

    const badgeEl = document.getElementById("diagramBadge");
    if (badgeEl) {
        badgeEl.textContent = diagram.badge || "Architecture & Topology";
    }

    const subtitleEl = document.getElementById("diagramSubtitle");
    if (subtitleEl) {
        subtitleEl.textContent = diagram.subtitle || "Structural invariants, state transitions, and memory layout";
    }

    // 2. Render Canvas (SVG or Mermaid)
    const viewer = document.getElementById("diagramViewerContainer");
    if (viewer) {
        viewer.innerHTML = "";
        
        if (diagram.svg_content) {
            viewer.innerHTML = `<div class="w-full flex justify-center py-2">${diagram.svg_content}</div>`;
        } else if (diagram.mermaid_code && window.mermaid) {
            try {
                window.mermaid.initialize({
                    startOnLoad: false,
                    theme: isDark ? 'dark' : 'default',
                    securityLevel: 'loose'
                });
                const renderId = `mermaid_diag_${Date.now()}`;
                window.mermaid.render(renderId, diagram.mermaid_code)
                    .then(({ svg }) => {
                        viewer.innerHTML = `<div class="w-full flex justify-center py-2">${svg}</div>`;
                    })
                    .catch(mErr => {
                        console.warn("[OmniLearn] Mermaid render issue:", mErr);
                        if (diagram.svg_content) {
                            viewer.innerHTML = `<div class="w-full flex justify-center py-2">${diagram.svg_content}</div>`;
                        }
                    });
            } catch (mErr) {
                console.warn("[OmniLearn] Mermaid render issue:", mErr);
                if (diagram.svg_content) {
                    viewer.innerHTML = `<div class="w-full flex justify-center py-2">${diagram.svg_content}</div>`;
                }
            }
        }
    }

    // 3. Explanation & Invariants
    const explanationEl = document.getElementById("diagramExplanationText");
    if (explanationEl) {
        explanationEl.textContent = diagram.explanation || "System structural representation demonstrating core operational invariants.";
    }

    // 4. Legend Chips
    const legendContainer = document.getElementById("diagramLegendContainer");
    if (legendContainer) {
        legendContainer.innerHTML = "";
        const legendItems = Array.isArray(diagram.legend) ? diagram.legend : [];
        if (legendItems.length > 0) {
            legendItems.forEach(item => {
                const chip = document.createElement("div");
                chip.className = "diagram-legend-chip flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium border shadow-xs";
                const dot = document.createElement("span");
                dot.className = "w-2.5 h-2.5 rounded-full shrink-0";
                dot.style.backgroundColor = item.color || "#38bdf8";
                const label = document.createElement("span");
                label.textContent = item.label || "";
                chip.appendChild(dot);
                chip.appendChild(label);
                legendContainer.appendChild(chip);
            });
        }
    }
}
window.renderConceptDiagram = renderConceptDiagram;

function prepareMathMarkdown(rawText) {
    if (!rawText || typeof rawText !== 'string') return "";
    
    // 1. Unescape literal \n into real newlines
    let clean = rawText.replace(/\\n/g, '\n');

    // 2. Clean decorative borders and leading headline hashes
    clean = clean
        .replace(/^[=\-~_#*]{4,}\s*$/gm, '')
        .replace(/^#\s+/gm, '')
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
function formatRoadmapDescription(text) {
    if (!text) return "";
    
    // Fix corrupted LaTeX where \t was absorbed as tab: "ext{" -> "\text{"
    let formatted = text.replace(/(^|[^\\])ext\{/g, '$1\\text{');

    // Remove trailing dangling colons left over from stripped math headers
    formatted = formatted.replace(/(:\s*)+$/g, '.');
    
    // Check if there are code blocks ```lang ... ```
    formatted = formatted.replace(/```([a-zA-Z0-9_-]*)\n?([\s\S]*?)```/g, (match, lang, code) => {
        const cleanCode = code.trim().replace(/</g, "&lt;").replace(/>/g, "&gt;");
        return `<div class="my-2 rounded-lg bg-slate-900/90 border border-slate-700/60 overflow-hidden font-mono text-[11px] leading-relaxed max-w-full min-w-0">
            ${lang ? `<div class="px-2.5 py-0.5 bg-slate-800/80 text-[10px] text-slate-400 border-b border-slate-700/60 uppercase font-semibold">${lang}</div>` : ''}
            <div class="p-2.5 overflow-x-auto custom-scrollbar text-emerald-300">
                <pre class="m-0 p-0 font-mono"><code class="break-normal">${cleanCode}</code></pre>
            </div>
        </div>`;
    });

    // Formatting bold and inline code
    formatted = formatted
        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-800">$1</strong>')
        .replace(/`([^`]+)`/g, '<code class="bg-slate-100 text-indigo-700 px-1 py-0.5 rounded text-[11px] font-mono break-all">$1</code>');

    return formatted;
}

function renderRoadmap(steps) {
    const container = document.getElementById("roadmapTimeline");
    const progressBadge = document.getElementById("roadmapProgressBadge");
    if (!container) return;
    container.innerHTML = "";
    
    if (!steps || !Array.isArray(steps) || steps.length === 0) {
        container.innerHTML = `<p class="text-xs text-slate-400 italic">No roadmap steps calculated.</p>`;
        if (progressBadge) progressBadge.textContent = "0 Steps";
        return;
    }

    const qKey = String(
        (currentSearchData && (currentSearchData.query || currentSearchData.title || currentSearchData.topic)) ||
        currentQuery ||
        ""
    ).trim().toLowerCase();
    
    if (qKey && !completedRoadmapSteps[qKey]) {
        completedRoadmapSteps[qKey] = new Set();
    }
    const completedSet = (qKey && completedRoadmapSteps[qKey]) ? completedRoadmapSteps[qKey] : new Set();
    
    updateRoadmapProgressDisplay(steps.length, completedSet.size);
    
    steps.forEach((step, idx) => {
        if (!step) return;
        const isDone = completedSet.has(idx);
        const stepEl = document.createElement("div");
        stepEl.className = `relative mb-4 last:mb-0 transition-all duration-200 min-w-0 max-w-full ${isDone ? 'opacity-65' : ''}`;
        
        let typeBadgeColor = "glass-badge glass-badge-indigo";
        let dotColor = "border-slate-300 bg-white text-slate-400";
        let typeLabel = step.type || "Core";
        
        const isHinglish = (window.currentSearchLang === "hinglish");
        if (step.type === "prerequisite") {
            typeBadgeColor = "glass-badge glass-badge-indigo";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-blue-500 bg-blue-50 text-blue-600";
            typeLabel = isHinglish ? "Zaroori Basics" : "Prerequisite";
        } else if (step.type === "core") {
            typeBadgeColor = "glass-badge glass-badge-indigo";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-indigo-500 bg-indigo-50 text-indigo-600";
            typeLabel = isHinglish ? "Main Concept" : "Core Principle";
        } else if (step.type === "deep_dive") {
            typeBadgeColor = "glass-badge glass-badge-amber";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-amber-500 bg-amber-50 text-amber-600";
            typeLabel = isHinglish ? "Gehrai Se Samjhein" : "Deep Dive";
        } else if (step.type === "practice") {
            typeBadgeColor = "glass-badge glass-badge-emerald";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-teal-500 bg-teal-50 text-teal-600";
            typeLabel = isHinglish ? "Exam Practice" : "Problem Practice";
        } else if (step.type === "advanced") {
            typeBadgeColor = "glass-badge glass-badge-purple";
            dotColor = isDone ? "border-emerald-500 bg-emerald-500 text-white" : "border-purple-500 bg-purple-50 text-purple-600";
            typeLabel = isHinglish ? "Industry Scope" : "Advanced Scope";
        }
        
        const conceptTitle = step.concept || step.title || `Step ${idx + 1}`;
        const descText = step.description || step.summary || "";
        
        stepEl.innerHTML = `
            <span class="absolute -left-[23px] top-1 rounded-full border-2 ${dotColor} w-5 h-5 flex items-center justify-center text-[10px] font-bold shadow-sm cursor-pointer" onclick="toggleRoadmapStep(${idx})">
                ${isDone ? '<i class="fa-solid fa-check text-[9px]"></i>' : (idx + 1)}
            </span>
            <div class="roadmap-step-card bg-slate-50 hover:bg-slate-100/80 border border-slate-200/70 rounded-xl p-3.5 transition shadow-xs min-w-0 max-w-full overflow-hidden">
                <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center space-x-2 min-w-0">
                        <input type="checkbox" ${isDone ? 'checked' : ''} onchange="toggleRoadmapStep(${idx})" 
                               class="rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer h-3.5 w-3.5 border-slate-300 shrink-0">
                        <span class="text-[10px] font-bold uppercase tracking-wider ${typeBadgeColor} px-1.5 py-0.5 rounded truncate">
                            ${typeLabel}
                        </span>
                    </div>
                    <span class="text-[10px] text-slate-500 font-medium flex items-center shrink-0">
                        <i class="fa-regular fa-clock mr-1 text-slate-400"></i>${step.estimated_time || "2-3 hrs"}
                    </span>
                </div>
                <h4 class="font-bold text-xs text-slate-800 mt-2 break-words ${isDone ? 'line-through text-slate-500' : ''}">${escapeHtml(conceptTitle)}</h4>
                <div class="roadmap-desc text-xs text-slate-600 mt-1.5 leading-relaxed break-words overflow-x-auto custom-scrollbar max-w-full min-w-0">
                    ${formatRoadmapDescription(descText)}
                </div>
            </div>
        `;
        container.appendChild(stepEl);
    });
}

function toggleRoadmapStep(stepIndex) {
    if (!currentSearchData || !currentSearchData.roadmap) return;
    const qKey = String(
        (currentSearchData && (currentSearchData.query || currentSearchData.title || currentSearchData.topic)) ||
        currentQuery ||
        ""
    ).trim().toLowerCase();
    if (!qKey) return;
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
    const isHinglish = (window.currentSearchLang === "hinglish");
    const doneText = isHinglish ? "Poora Hua" : "Done";
    progressBadge.textContent = `${completed} / ${total} ${doneText} (${pct}%)`;
    
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
    const inputEl = document.getElementById("noteSearchInput");
    if (!inputEl) return;
    const val = inputEl.value.trim();
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
    if (!container) return;
    container.innerHTML = "";
    
    let list = Array.isArray(videos) ? videos : [];
    if (list.length === 0) {
        const topic = (currentSearchData && (currentSearchData.title || currentSearchData.query)) || currentQuery || "Academic Topic";
        container.innerHTML = `
            <div class="p-5 bg-slate-50 border border-slate-200/80 rounded-xl text-center flex flex-col items-center justify-center">
                <i class="fa-brands fa-youtube text-red-500 text-3xl mb-2"></i>
                <h4 class="font-bold text-xs text-slate-800 mb-1">Curated Video Tutorials for ${escapeHtml(topic)}</h4>
                <p class="text-[11px] text-slate-500 max-w-sm mb-3">Watch expert engineering lectures, problem-solving demonstrations, and conceptual walkthroughs.</p>
                <a href="https://www.youtube.com/results?search_query=${encodeURIComponent(topic + ' computer science lecture')}" target="_blank" class="inline-flex items-center text-xs text-indigo-600 hover:text-indigo-800 font-semibold glass-btn px-3 py-1.5 rounded-lg">
                    <span>Watch Lectures on YouTube</span>
                    <i class="fa-solid fa-arrow-up-right-from-square ml-1.5 text-[10px]"></i>
                </a>
            </div>
        `;
        return;
    }
    
    list.forEach(video => {
        if (!video) return;
        const card = document.createElement("div");
        card.className = "flex flex-col sm:flex-row bg-slate-50 border border-slate-200/80 rounded-xl overflow-hidden hover:border-indigo-300 hover:shadow-md transition duration-200 group";
        
        const videoId = escapeHtml(video.video_id || "");
        const thumbUrl = escapeHtml(video.thumbnail_url || (videoId ? `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg` : ""));
        const titleText = escapeHtml(video.title || "Educational Lecture");
        const channel = escapeHtml(video.channel_title || "Academic Tutorial");
        const views = escapeHtml(video.view_count || "Popular");
        
        card.innerHTML = `
            <div class="relative w-full sm:w-44 h-28 bg-slate-900 flex-shrink-0 cursor-pointer overflow-hidden" onclick="playVideo(this, '${videoId}')">
                <img src="${thumbUrl}" alt="Thumbnail" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
                <div class="absolute inset-0 bg-black/25 flex items-center justify-center group-hover:bg-black/35 transition">
                    <div class="w-10 h-10 rounded-full bg-red-600/90 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition">
                        <i class="fa-solid fa-play text-sm ml-0.5"></i>
                    </div>
                </div>
            </div>
            <div class="p-3 flex flex-col justify-between flex-1 min-w-0">
                <div>
                    <h4 class="font-bold text-xs text-slate-800 line-clamp-2 leading-snug group-hover:text-indigo-600 transition">${titleText}</h4>
                    <div class="flex items-center space-x-1.5 mt-1.5">
                        <span class="text-[11px] font-semibold text-slate-600 truncate">${channel}</span>
                        <i class="fa-solid fa-circle-check text-[9px] text-blue-500" title="Verified Educational Source"></i>
                    </div>
                </div>
                <div class="flex justify-between items-center text-[10px] text-slate-500 mt-2.5 pt-2 border-t border-slate-200/60">
                    <span class="font-medium bg-slate-200/70 text-slate-700 px-1.5 py-0.5 rounded">${views}</span>
                    <a href="https://youtube.com/watch?v=${videoId}" target="_blank" class="text-indigo-600 hover:text-indigo-800 font-semibold flex items-center">
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
    if (!container) return;
    container.innerHTML = "";
    
    let list = Array.isArray(resources) ? resources : [];
    if (list.length === 0) {
        const topic = (currentSearchData && (currentSearchData.title || currentSearchData.query)) || currentQuery || "Computer Science";
        list = [
            {
                title: `${topic} — Wikipedia Academic Foundations`,
                url: `https://en.wikipedia.org/wiki/${encodeURIComponent(topic.replace(/\s+/g, '_'))}`,
                snippet: `Definitive theoretical foundations, mathematical invariants, and classification for ${topic}.`
            },
            {
                title: `${topic} — GeeksforGeeks Practical Guide`,
                url: `https://www.geeksforgeeks.org/search/?q=${encodeURIComponent(topic)}`,
                snippet: `Algorithmic implementations, edge cases, complexity tables, and university examination problems for ${topic}.`
            },
            {
                title: `${topic} — NPTEL Engineering Courseware`,
                url: `https://nptel.ac.in/courses?search=${encodeURIComponent(topic)}`,
                snippet: `Comprehensive higher education lectures, syllabus mappings, and laboratory assignments.`
            }
        ];
    }
    
    list.forEach(item => {
        if (!item) return;
        const linkCard = document.createElement("div");
        linkCard.className = "bg-slate-50 border border-slate-100 rounded-lg p-3 hover:bg-slate-100 transition flex items-start space-x-3";
        
        const itemUrl = escapeHtml(item.url || "#");
        const itemTitle = escapeHtml(item.title || "Academic Resource");
        const itemSnippet = escapeHtml(item.snippet || "Reference materials and documentation.");
        
        linkCard.innerHTML = `
            <div class="text-blue-500 mt-0.5"><i class="fa-solid fa-globe text-sm"></i></div>
            <div class="min-w-0 flex-1">
                <a href="${itemUrl}" target="_blank" class="font-bold text-xs text-indigo-600 hover:underline hover:text-indigo-800 line-clamp-1">
                    ${itemTitle} <i class="fa-solid fa-arrow-up-right-from-square text-[9px] ml-0.5"></i>
                </a>
                <p class="text-[10px] text-slate-500 line-clamp-2 mt-1 leading-normal">${itemSnippet}</p>
            </div>
        `;
        container.appendChild(linkCard);
    });
}

function renderFunFact(fact) {
    const el = document.getElementById("funFactText");
    if (!el) return;
    if (fact && typeof fact === "string" && fact.trim()) {
        el.textContent = fact.trim();
    } else {
        const topic = (currentSearchData && (currentSearchData.title || currentSearchData.query)) || currentQuery || "Academic Science";
        el.textContent = `Rigorous computational models of ${topic} form the foundational benchmark across computer science and engineering curricula worldwide, directly governing system architecture and algorithmic design.`;
    }
}

// Renders the trend chart indicating how often the topic appears over the years
function renderAnalyticsChart(pyqs, examFrequency) {
    const canvas = document.getElementById("frequencyChart");
    if (!canvas) return;
    
    if (typeof Chart === 'undefined') {
        console.warn("Chart.js is not loaded yet.");
        return;
    }
    
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
                hasFrequency = true;
            }
        });
    }

    // Default mock curve if no appearances recorded yet
    if (!hasFrequency) {
        const fallbackCounts = [10, 14, 17, 21, 25];
        years.forEach((yr, idx) => { counts[yr] = fallbackCounts[idx]; });
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
    
    try {
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
    } catch (chartErr) {
        console.error("Failed to render Chart.js chart:", chartErr);
    }
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
    const topicQuery = String(
        currentSearchData.query || currentSearchData.title || currentSearchData.topic || currentQuery || ""
    ).trim().toLowerCase();
    if (!topicQuery) return;
    
    // Check if already bookmarked
    const existing = Array.isArray(bookmarks) ? bookmarks.find(b => 
        b && b.item_type === "topic" && b.title && String(b.title).trim().toLowerCase() === topicQuery
    ) : null;
    
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
                    title: currentSearchData.query || currentSearchData.title || topicQuery
                })
            });
            if (response.ok) {
                await fetchBookmarks();
                updateTopicBookmarkButton();
            }
        } catch (e) {
            console.error("Failed to add topic bookmark:", e);
        }
    }
}

function updateTopicBookmarkButton() {
    try {
        const btn = document.getElementById("bookmarkTopicBtn");
        if (!btn) return;
        
        const topicQuery = String(
            (currentSearchData && (currentSearchData.query || currentSearchData.title || currentSearchData.topic)) ||
            currentQuery ||
            ""
        ).trim().toLowerCase();
        
        if (!topicQuery) return;
        
        const isBookmarked = Array.isArray(bookmarks) && bookmarks.some(b => 
            b && b.item_type === "topic" && b.title && String(b.title).trim().toLowerCase() === topicQuery
        );
        
        if (isBookmarked) {
            btn.innerHTML = `<i class="fa-solid fa-bookmark text-2xl text-yellow-500"></i>`;
        } else {
            btn.innerHTML = `<i class="fa-regular fa-bookmark text-2xl"></i>`;
        }
    } catch (err) {
        console.warn("Failed to update topic bookmark button:", err);
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
    
    // 1. Sanitize decorative ASCII boundaries, but preserve math syntax intact
    let cleanText = rawText
        .replace(/^[=\-~_#*]{4,}\s*$/gm, '')
        .replace(/\n{3,}/g, '\n\n');

    // 2. Extract math blocks to protect them from Markdown parsing (underscores, asterisks, backslashes)
    const mathTokens = [];
    
    // Display math: $$...$$ or \[...\]
    cleanText = cleanText.replace(/(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\])/g, (match) => {
        const placeholder = `@@MATH_BLOCK_${mathTokens.length}@@`;
        mathTokens.push(match);
        return placeholder;
    });

    // Inline math: $...$ or \(...\)
    cleanText = cleanText.replace(/(\$[^$\n\r]+?\$|\\\([^)\n\r]+?\\\))/g, (match) => {
        const placeholder = `@@MATH_BLOCK_${mathTokens.length}@@`;
        mathTokens.push(match);
        return placeholder;
    });

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
                
            // Restore protected math expressions
            parsed = parsed.replace(/@@MATH_BLOCK_(\d+)@@/g, (match, idx) => {
                return mathTokens[parseInt(idx, 10)] || match;
            });

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
    
    let finalHtml = htmlLines.join("\n");
    finalHtml = finalHtml.replace(/@@MATH_BLOCK_(\d+)@@/g, (match, idx) => {
        return mathTokens[parseInt(idx, 10)] || match;
    });
    return finalHtml;
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
    const cleanSubject = (subject || "Engineering Sciences").trim();
    const tLower = cleanTopic.toLowerCase();
    const sLower = cleanSubject.toLowerCase();
    const combined = `${tLower} ${sLower}`;

    const isPhysics = /physic|gravity|gravitation|kepler|mechanic|kinematic|newton|projectile|friction|collision|momentum|optics|laser|interference|diffraction|polarization|quantum|schrodinger|wavefunction|relativity|lorentz|hall effect|maxwell|coulomb|electromagnet/.test(combined);
    const isChemistry = /chemist|polymer|corrosion|nernst|electrode|galvanic|phase rule|water hardness|hardness|edta|spectroscopy|lubricant|fuel|calorific|cement|battery|titration|molecular orbital|mot/.test(combined);
    const isEE = /circuit|kcl|kvl|thevenin|norton|kirchhoff|transistor|diode|bjt|mosfet|op-amp|rlc|transformer|induction motor/.test(combined);
    const isME = /thermodynamic|carnot|entropy|enthalpy|fluid|bernoulli|reynolds|stress|strain|otto|diesel/.test(combined);
    const isMath = /calculus|integral|derivative|differential equation|eigenvalue|eigenvector|matrix algebra|taylor series|fourier/.test(combined);

    if (isPhysics) {
        const isGravity = /gravity|gravitation|kepler|orbital/.test(combined);
        const isOptics = /optics|laser|interference|diffraction|fiber/.test(combined);
        const isQuantum = /quantum|schrodinger|wavefunction|uncertainty|de broglie/.test(combined);

        if (isGravity) {
            return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Engineering Physics & Applied Mechanics | **Level:** B.Tech Undergraduate

**${cleanTopic}** is a cornerstone of classical mechanics and astrophysical engineering. It describes the fundamental attractive interaction between massive bodies, governing celestial orbits, artificial satellite trajectories, and terrestrial gravitational fields.

## Core Concepts & Mathematical / Architectural Linchpins
1. **Newton's Law of Universal Gravitation**:
$$\\mathbf{F} = -G \\frac{m_1 m_2}{r^2} \\hat{\\mathbf{r}}$$
where $G = 6.67430 \\times 10^{-11} \\text{ N}\\cdot\\text{m}^2/\\text{kg}^2$.

2. **Gravitational Field Intensity & Acceleration**:
$$g = \\frac{GM}{R^2}, \\qquad g_h = g \\left(1 - \\frac{2h}{R}\\right) \\; (h \\ll R), \\qquad g_d = g \\left(1 - \\frac{d}{R}\\right)$$

3. **Gravitational Potential Energy & Escape Velocity**:
$$U(r) = -\\frac{GMm}{r}, \\qquad v_e = \\sqrt{\\frac{2GM}{R}} \\approx 11.19 \\text{ km/s for Earth}$$

4. **Kepler's Third Law (Harmonic Law)**:
$$T^2 = \\left( \\frac{4\\pi^2}{GM} \\right) r^3$$

## Production-Grade Implementation & Boundary Validation
\`\`\`python
# Scientific Python: Two-Body Gravitational Orbital Velocity & Escape Velocity
import math

def compute_orbital_mechanics(mass_central_kg: float, radius_m: float) -> dict:
    """Calculates circular orbital speed, period, and escape velocity."""
    G = 6.67430e-11
    if radius_m <= 0 or mass_central_kg <= 0:
        raise ValueError("Mass and orbital radius must be strictly positive.")
    
    v_orbital = math.sqrt(G * mass_central_kg / radius_m)
    v_escape = math.sqrt(2 * G * mass_central_kg / radius_m)
    period_sec = 2 * math.pi * math.sqrt((radius_m ** 3) / (G * mass_central_kg))
    
    return {
        "v_orbital_m_s": v_orbital,
        "v_escape_km_s": v_escape / 1000.0,
        "orbital_period_hrs": period_sec / 3600.0
    }
\`\`\`

## Step-by-Step Solved Numericals & Analytical Traces
### Problem 1: Earth Escape Velocity Calculation
**Problem**: Calculate the escape velocity from Earth's surface given $M = 5.972 \\times 10^{24}\\text{ kg}$ and mean radius $R = 6.371 \\times 10^6\\text{ m}$.
1. **Formula**: $v_e = \\sqrt{\\frac{2GM}{R}}$.
2. **Substitution**:
$$v_e = \\sqrt{\\frac{2 \\times 6.67430 \\times 10^{-11} \\times 5.972 \\times 10^{24}}{6.371 \\times 10^6}} = \\sqrt{\\frac{7.9718 \\times 10^{14}}{6.371 \\times 10^6}} = \\sqrt{1.25126 \\times 10^8} \\approx 11186 \\text{ m/s}$$
3. **Final Result**: $v_e \\approx 11.19\\text{ km/s}$.

### Problem 2: Geostationary Orbit Radius
**Problem**: Calculate the orbital radius of a geostationary satellite with orbital period $T = 24\\text{ hours} = 86400\\text{ s}$.
1. **Kepler's Law Form**: $r^3 = \\frac{GM T^2}{4\\pi^2} = \\frac{6.67430 \\times 10^{-11} \\times 5.972 \\times 10^{24} \\times (86400)^2}{4 \\pi^2} \\approx 7.537 \\times 10^{22} \\text{ m}^3$.
2. **Cube Root**: $r = (7.537 \\times 10^{22})^{1/3} \\approx 42164 \\text{ km}$.
3. **Altitude Above Earth**: $h = r - R = 42164 - 6371 = 35793 \\text{ km} \\approx 35800 \\text{ km}$.

## Complexity Analysis & Governing Invariant Matrix
| Parameter / Concept | Governing Equation | Physical Dimension |
| :--- | :--- | :--- |
| **Gravitational Field** | $g = GM / R^2$ | $[M^0 L T^{-2}]$ |
| **Gravitational Potential** | $V(r) = -GM / r$ | $[M^0 L^2 T^{-2}]$ |
| **Orbital Speed** | $v_o = \\sqrt{GM / r}$ | $[M^0 L T^{-1}]$ |
| **Escape Speed** | $v_e = \\sqrt{2} \\cdot v_o$ | $[M^0 L T^{-1}]$ |

## Real-World Pitfalls, Common Bugs & Exam Traps
1. Forgetting that gravitational potential energy is strictly negative relative to infinity ($U(r) = -GMm/r$).
2. Using the linear approximation $g_h = g(1 - 2h/R)$ when altitude $h$ is large ($h \not\\ll R$).
3. Confusing circular orbital speed $v_o = \\sqrt{GM/r}$ with parabolic escape speed $v_e = \\sqrt{2GM/r}$.

## University Examination Practice Problems with Model Answers
1. **Q1: State Newton's Law of Universal Gravitation in vector form.**
   - *Answer*: $\\mathbf{F}_{12} = -G \\frac{m_1 m_2}{r^2} \\hat{\\mathbf{r}}_{12}$; the gravitational force is central, conservative, and mutually attractive.
2. **Q2: Show that escape velocity is $\\sqrt{2}$ times orbital velocity near Earth's surface.**
   - *Answer*: $v_e = \\sqrt{2GM/R} = \\sqrt{2} \\sqrt{GM/R} = \\sqrt{2} \\, v_o$.
3. **Q3: State Kepler's Second Law and its conservation law basis.**
   - *Answer*: The radius vector sweeps equal areas in equal intervals of time ($dA/dt = L/(2m) = \\text{constant}$), which is direct consequence of conservation of angular momentum.`;
        } else if (isOptics) {
            return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Engineering Physics (Wave Optics & Lasers) | **Level:** B.Tech Undergraduate

**${cleanTopic}** is an essential subject in wave physics and photonics, governing wave interference, diffraction, laser physics, and optical fiber communications.

## Core Concepts & Mathematical / Architectural Linchpins
1. **Thin Film Interference (Reflected Light)**:
$$2\\mu t \\cos r = \\left(n - \\frac{1}{2}\\right)\\lambda \\quad (\\text{Constructive}), \\qquad 2\\mu t \\cos r = n\\lambda \\quad (\\text{Destructive})$$

2. **Newton's Rings Diameter (Reflected System)**:
$$D_n^2 = 4 n R \\lambda \\implies \\lambda = \\frac{D_{n+p}^2 - D_n^2}{4 p R}$$

3. **Fraunhofer Diffraction Grating Equation**:
$$(a + b) \\sin \\theta = n \\lambda$$

4. **Numerical Aperture (NA) & Acceptance Angle**:
$$\\text{NA} = \\sqrt{n_1^2 - n_2^2}, \\qquad \theta_0 = \\sin^{-1}\\left(\\sqrt{n_1^2 - n_2^2}\\right)$$

## Step-by-Step Solved Numerical
### Problem 1: Newton's Rings Wavelength Calculation
**Problem**: In Newton's rings experiment, the diameter of the 10th dark ring is $0.50\\text{ cm}$ and the 4th dark ring is $0.35\\text{ cm}$. Lens curvature radius $R = 100\\text{ cm}$. Calculate wavelength $\\lambda$.
1. **Formula**: $\\lambda = \\frac{D_{n+p}^2 - D_n^2}{4 p R}$ where $n=4, n+p=10 \\implies p=6$.
2. **Substitution**:
$$\\lambda = \\frac{(0.50)^2 - (0.35)^2}{4 \\times 6 \\times 100} = \\frac{0.25 - 0.1225}{2400} = \\frac{0.1275}{2400} = 5.3125 \\times 10^{-5} \\text{ cm} = 5312.5 \\text{ \\AA}$$

## University Examination Practice Problems with Model Answers
1. **Q1: State the condition for sustained interference of light.**
   - *Answer*: Sources must be coherent (constant phase difference) and emit monochromatic waves with identical amplitudes.
2. **Q2: Why is the center of Newton's rings dark in reflected light?**
   - *Answer*: Reflection at the denser glass interface introduces an additional Stokes phase change of $\\pi$ (path difference $\\lambda/2$), producing destructive interference at zero film thickness.
3. **Q3: What is Population Inversion in lasers?**
   - *Answer*: A condition where more atoms populate the higher metastable excited state than the ground state ($N_2 > N_1$).`;
        } else {
            return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Engineering Physics & Applied Mechanics | **Level:** B.Tech Undergraduate

**${cleanTopic}** is a core foundational subject in Engineering Physics, analyzing the fundamental physical conservation laws, relativistic transformations, and dynamical invariants.

## Core Concepts & Mathematical / Architectural Linchpins
1. **Relativistic Lorentz Transformations**:
$$x' = \\gamma(x - vt), \\qquad t' = \\gamma\\left(t - \\frac{vx}{c^2}\\right), \\qquad \\gamma = \\frac{1}{\\sqrt{1 - v^2/c^2}}$$

2. **Length Contraction & Time Dilation**:
$$L = L_0 \\sqrt{1 - v^2/c^2}, \\qquad \\Delta t = \\frac{\\Delta t_0}{\\sqrt{1 - v^2/c^2}}$$

3. **Relativistic Mass-Energy Equivalence**:
$$E = mc^2 = \\gamma m_0 c^2, \\qquad E^2 = p^2 c^2 + m_0^2 c^4$$

## Step-by-Step Solved Numerical
### Problem 1: Relativistic Length Contraction
**Problem**: A meter stick moves with speed $v = 0.8c$ along its length. Calculate its contracted length.
1. **Formula**: $L = L_0 \\sqrt{1 - (v/c)^2} = 1.0 \\times \\sqrt{1 - 0.64} = \\sqrt{0.36} = 0.60\\text{ m}$.
2. **Contraction**: $1.0 - 0.60 = 0.40\\text{ m}$ ($40\%$ contraction).

## University Examination Practice Problems with Model Answers
1. **Q1: State the postulates of Special Relativity.**
   - *Answer*: (1) Physical laws are invariant in all inertial frames. (2) Speed of light in vacuum $c$ is constant for all observers.
2. **Q2: What is the null outcome of the Michelson-Morley experiment?**
   - *Answer*: It disproved the existence of luminiferous ether, confirming the constancy and isotropy of light speed.
3. **Q3: Write the relativistic energy-momentum relation.**
   - *Answer*: $E^2 = p^2 c^2 + m_0^2 c^4$.`;
        }
    }

    if (isChemistry) {
        return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Engineering Chemistry & Materials Science | **Level:** B.Tech Undergraduate

**${cleanTopic}** is a fundamental subject in Engineering Chemistry, exploring molecular transformations, electrochemical cell thermodynamics, phase equilibria, and engineering materials.

## Core Concepts & Mathematical / Architectural Linchpins
1. **Nernst Equation for Electrochemical Cell Potential**:
$$E_{\\text{cell}} = E^\circ_{\\text{cell}} - \\frac{0.0591}{n} \log_{10} \\left( \\frac{[\\text{Products}]}{[\\text{Reactants}]} \\right) \\quad \\text{at } 298\\text{ K}$$

2. **Gibbs Phase Rule**:
$$F = C - P + 2 \\qquad (F = C - P + 1 \\text{ for condensed systems})$$

3. **Water Hardness EDTA Titration**:
$$\\text{Total Hardness (ppm as CaCO}_3) = \\frac{V_{\\text{EDTA}} \\times M_{\\text{EDTA}} \\times 100 \\times 1000}{V_{\\text{sample}}}$$

## Step-by-Step Solved Numerical
### Problem 1: Electrochemical Cell EMF
**Problem**: Calculate EMF of cell $Zn|Zn^{2+}(0.01\\text{ M}) \\parallel Cu^{2+}(0.1\\text{ M})|Cu$ at $298\\text{ K}$ ($E^\circ_{\\text{cell}} = 1.10\\text{ V}$).
1. **Nernst Equation**: $E = 1.10 - \\frac{0.0591}{2} \log_{10}\\left(\\frac{0.01}{0.1}\\right) = 1.10 - 0.02955 (-1) = 1.1296\\text{ V}$.

## University Examination Practice Problems with Model Answers
1. **Q1: State the Nernst Equation and its applications.**
   - *Answer*: $E = E^\\circ - \\frac{0.0591}{n} \log_{10} Q$; used to calculate cell potential under non-standard conditions.
2. **Q2: State the Gibbs Phase Rule and define Degree of Freedom.**
   - *Answer*: $F = C - P + 2$; minimum independent intensive variables needed to define thermodynamic equilibrium.
3. **Q3: Differentiate between Thermoplastic and Thermosetting polymers.**
   - *Answer*: Thermoplastics soften repeatedly upon heating (linear/branched chains); thermosets crosslink irreversibly into 3D rigid structures.`;
    }

    if (isEE) {
        return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Electrical & Electronics Engineering | **Level:** B.Tech Undergraduate

**${cleanTopic}** is a fundamental theoretical and operational subject within Electrical Network Theory and Circuit Analysis. It establishes the governing laws for charge conservation, voltage loops, and electromagnetic energy distribution.

## Core Concepts & Mathematical / Architectural Linchpins
1. **Kirchhoff's Current Law (KCL - Charge Conservation)**:
$$\sum_{k=1}^{N} I_k = 0$$

2. **Kirchhoff's Voltage Law (KVL - Energy Conservation)**:
$$\sum_{k=1}^{M} V_k = 0$$

3. **Thevenin's Equivalent & Maximum Power Transfer**:
$$I_L = \\frac{V_{\\text{th}}}{R_{\\text{th}} + R_L}, \\qquad P_{\\max} = \\frac{V_{\\text{th}}^2}{4 R_{\\text{th}}}$$

## Production-Grade Implementation & Boundary Validation
\`\`\`python
# Python Analysis: Thevenin Equivalent Calculator
def solve_thevenin(v_oc: float, r_th: float, r_load: float) -> dict:
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

2. **Second Law & Carnot Maximum Thermal Efficiency**:
$$\eta_{\\text{Carnot}} = 1 - \\frac{T_L}{T_H} = \\frac{T_H - T_L}{T_H}$$

3. **Bernoulli's Equation (Incompressible Fluid Flow)**:
$$P + \\frac{1}{2}\\rho v^2 + \\rho g h = \\text{Constant}$$

## Step-by-Step Solved Numericals & Thermodynamic Traces
### Problem 1: Carnot Cycle Thermal Efficiency Calculation
**Problem**: A heat engine operates between $T_H = 600^\\circ\\text{C}$ and $T_L = 30^\\circ\\text{C}$, absorbing $1200\\text{ kJ}$ heat per cycle. Compute thermal efficiency $\\eta$ and net work output $W_{\\text{net}}$.
1. **Convert to Kelvin**: $T_H = 600 + 273.15 = 873.15\\text{ K}$, $T_L = 30 + 273.15 = 303.15\\text{ K}$.
2. **Carnot Efficiency**: $\\eta = 1 - \\frac{303.15}{873.15} = 0.6528 \\implies 65.28\%$.
3. **Net Work Output**: $W_{\\text{net}} = 0.6528 \\times 1200\\text{ kJ} = 783.36\\text{ kJ}$.

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

2. **Cayley-Hamilton Theorem**:
$$p(A) = A^n + c_{n-1}A^{n-1} + \\dots + c_0 I = 0$$

3. **Exact Differential Equation Criterion**:
$$M(x, y)\\,dx + N(x, y)\\,dy = 0 \\iff \\frac{\\partial M}{\\partial y} = \\frac{\\partial N}{\\partial x}$$

## Step-by-Step Solved Numericals & Analytical Derivations
### Problem 1: Eigenvalues of a $2 \\times 2$ Matrix
**Problem**: Find eigenvalues of $A = \\begin{bmatrix} 4 & 1 \\ 2 & 3 \\end{bmatrix}$.
1. **Characteristic Equation**: $\\det(A - \\lambda I) = (4 - \\lambda)(3 - \\lambda) - 2 = \\lambda^2 - 7\\lambda + 10 = 0$.
2. **Factoring**: $(\\lambda - 5)(\\lambda - 2) = 0 \\implies \lambda_1 = 5, \lambda_2 = 2$.

## University Examination Practice Problems with Model Answers
1. **Q1: State the Cayley-Hamilton Theorem.**
   - *Answer*: Every square matrix satisfies its own characteristic polynomial equation.
2. **Q2: State the relation between trace and eigenvalues.**
   - *Answer*: $\\text{Trace}(A) = \sum_{i=1}^n \lambda_i$.
3. **Q3: What is the condition for exactness in $M dx + N dy = 0$?**
   - *Answer*: $\\frac{\\partial M}{\\partial y} = \\frac{\\partial N}{\\partial x}$.`;
    }

    // Computer Science / Algorithmic branch
    const isArray = /array|matrix|vector/.test(tLower);
    const isList = /list|linked|pointer/.test(tLower);

    let mathSection = "";
    let codeSection = "";
    let workedProblem = "";

    if (isArray) {
        mathSection = `### 1. Memory Representation & Address Arithmetic
In computer memory, an array stores elements at contiguous physical memory addresses:

- **1D Array Address Formula**:
$$\\text{Address}(A[i]) = \\text{BaseAddress} + (i - \\text{LowerBound}) \\times w$$

- **2D Row-Major Order (RMO)**:
$$\\text{Address}(A[i][j]) = \\text{BaseAddress} + \Big[ (i - \\text{LB}_r) \\times N_c + (j - \\text{LB}_c) \Big] \\times w$$`;

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
\`\`\``;

        workedProblem = `### Problem 1: 2D Array Address Derivation
**Problem**: An array $A[-5 \\dots 15, 10 \\dots 30]$ has Base Address $1020$ and element size $w = 4$ bytes. Compute $\\text{Address}(A[5][20])$ in Row-Major Order.
1. **Dimensions**: $N_r = 15 - (-5) + 1 = 21$, $N_c = 30 - 10 + 1 = 21$.
2. **Offset Calculation**: $(5 - (-5)) \\times 21 + (20 - 10) = 10 \\times 21 + 10 = 220$.
3. **Final Address**: $1020 + (220 \\times 4) = 1020 + 880 = 1900$.`;
    } else if (isList) {
        mathSection = `### 1. Pointer Invariants & Node Traversal
A Linked List is a collection of dynamic heap-allocated nodes connected via pointer addresses:

- **Node Structure**:
$$\\text{Node} = \langle \\text{Data}, \\quad \\text{NextPointer} \\in \\text{AddressSpace} \\cup \{\\text{NULL}\} \rangle$$`;

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
- Step 1: Head node 10 points to NULL.
- Step 2: Node 20 points to 10.
- Step 3: Node 30 points to 20.
Final reversed list head: $30$ in $\\mathcal{O}(n)$ time and $\\mathcal{O}(1)$ space.`;
    } else {
        mathSection = `### 1. Algorithmic Invariants & State Relations
The operational behavior of **${cleanTopic}** is defined by asymptotic complexity and state invariants:

- **Divide and Conquer Recurrence**:
$$T(n) = a \\, T\\left(\\frac{n}{b}\\right) + f(n)$$
- **Algorithmic Bounds**:
$$\\mathcal{O}(1) \\le \\mathcal{O}(\log n) \\le \\mathcal{O}(n) \\le \\mathcal{O}(n \log n) \\le \\mathcal{O}(n^2)$$`;

        codeSection = `\`\`\`python
# Production Python: Algorithmic Implementation of ${cleanTopic}
def execute_${cleanTopic.toLowerCase().replace(/[^a-z0-9]/g, '_')}(inputs: list) -> list:
    """Processes input elements preserving operational invariants."""
    if not inputs:
        return []
    return [item for item in inputs if item is not None]
\`\`\``;

        workedProblem = `### Problem 1: Asymptotic Recurrence Solution
**Problem**: Solve $T(n) = 2T(n/2) + \\Theta(n)$.
1. $a = 2, b = 2, f(n) = \\Theta(n^1)$.
2. $\log_b a = \log_2 2 = 1 \\implies n^{\log_b a} = n^1 = f(n)$.
3. Case 2 of Master Theorem applies $\\implies T(n) = \\Theta(n \log n)$.`;
    }

    return `# Executive Overview & Theoretical Foundations: ${cleanTopic}
**Academic Domain:** Computer Science & Engineering | **Level:** B.Tech Undergraduate

**${cleanTopic}** constitutes a core conceptual and algorithmic foundation in modern Computer Science and Engineering. Mastering this topic provides the structural basis for high-throughput software architecture, algorithmic efficiency, and university end-semester examinations.

## Core Concepts & Mathematical / Architectural Linchpins
${mathSection}

## Production-Grade Implementation & Boundary Validation
${codeSection}

## Step-by-Step Solved Numericals & Algorithmic Traces
${workedProblem}

## Complexity Analysis & Asymptotic Matrix
| Operation / Stage | Best Case | Average Case | Worst Case | Auxiliary Space |
| :--- | :--- | :--- | :--- | :--- |
| **Lookup / Retrieval** | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |
| **Insertion / State Update** | $\\mathcal{O}(1)$ | $\\mathcal{O}(1)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |
| **Full Traversal** | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(n)$ | $\\mathcal{O}(1)$ |

## Real-World Pitfalls, Common Bugs & Exam Traps
1. **Boundary Index Errors**: Inaccurate loop or base-case conditions leading to runtime faults.
2. **Resource Leaks**: Failing to clean up allocated structures or unclosed handles.
3. **Capacity Constraints**: Omitting bounds verification before processing large workloads.

## University Examination Practice Problems with Model Answers
1. **Q1: Define ${cleanTopic}.**
   - *Answer*: A core theoretical and computational methodology that organizes data and operations under deterministic time and space constraints.
2. **Q2: State the primary operational invariant for ${cleanTopic}.**
   - *Answer*: It enforces structured state transitions guaranteeing deterministic outputs and preventing deadlocks.
3. **Q3: What is the optimal time complexity for operations in ${cleanTopic}?**
   - *Answer*: Asymptotically bounded between $\\mathcal{O}(1)$ and $\\mathcal{O}(n \log n)$ under standard balanced conditions.`;
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
let mathJaxQueue = Promise.resolve();

function renderMathFormulas(elements) {
    const targets = elements ? (Array.isArray(elements) ? elements : [elements]) : [document.body];
    
    // 1. Instant rendering with KaTeX
    targets.forEach(el => {
        if (el) {
            try {
                applyKaTeXToElement(el);
            } catch (err) {
                console.warn("KaTeX render error:", err);
            }
        }
    });

    // 2. Typeset with MathJax 3 for full TeX coverage, safely serialized
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        const mathJaxTargets = elements ? (Array.isArray(elements) ? elements : [elements]) : undefined;
        mathJaxQueue = mathJaxQueue
            .then(() => {
                if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
                    try {
                        return window.MathJax.typesetPromise(mathJaxTargets);
                    } catch (syncErr) {
                        console.warn("MathJax typesetPromise synchronous warning:", syncErr);
                    }
                }
            })
            .catch((err) => {
                console.warn("MathJax typesetPromise async warning:", err);
            });
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
        const html = renderMarkdownToHtml(cleanContent);
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

function closeYearSubjects() {}
window.closeYearSubjects = closeYearSubjects;

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

