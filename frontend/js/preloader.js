/**
 * OmniLearn Scholastic Preloader Controller
 * Runs an educational intro animation on every page load/reload.
 * Smoothly synthesizes progress, cycles status milestones, and performs a cinematic dissolve unveil.
 */

(function () {
    const STATUS_MILESTONES = [
        { at: 0,  text: "Calibrating academic domain matrices..." },
        { at: 28, text: "Synthesizing Quantum, Calculus & Algorithms..." },
        { at: 58, text: "Aggregating university curriculum models..." },
        { at: 84, text: "Igniting universal knowledge gateway..." },
        { at: 100, text: "Welcome to OmniLearn." }
    ];

    let currentProgress = 0;
    let animationDone = false;
    let lastStatusIndex = -1;

    function initPreloader() {
        const preloader = document.getElementById("omniPreloader");
        const fillBar = document.getElementById("preloaderFill");
        const percentText = document.getElementById("preloaderPercent");
        const statusText = document.getElementById("preloaderStatusText");

        if (!preloader) return;

        const startTime = performance.now();
        // Target total duration: ~1800ms
        const TARGET_DURATION_MS = 1850;

        function updateStatus(val) {
            if (!statusText) return;
            for (let i = STATUS_MILESTONES.length - 1; i >= 0; i--) {
                if (val >= STATUS_MILESTONES[i].at) {
                    if (lastStatusIndex !== i) {
                        lastStatusIndex = i;
                        statusText.style.opacity = "0";
                        setTimeout(() => {
                            statusText.textContent = STATUS_MILESTONES[i].text;
                            statusText.style.opacity = "1";
                        }, 120);
                    }
                    break;
                }
            }
        }

        function step(now) {
            const elapsed = now - startTime;
            // Smooth easeOutCubic curve
            const rawT = Math.min(1, elapsed / TARGET_DURATION_MS);
            // Ease out cubic
            const easeProgress = 1 - Math.pow(1 - rawT, 3);
            currentProgress = Math.min(100, Math.floor(easeProgress * 100));

            if (fillBar) fillBar.style.width = `${currentProgress}%`;
            if (percentText) percentText.textContent = `${currentProgress}%`;
            updateStatus(currentProgress);

            if (rawT < 1) {
                requestAnimationFrame(step);
            } else {
                finishPreloader();
            }
        }

        function finishPreloader() {
            if (animationDone) return;
            animationDone = true;

            currentProgress = 100;
            if (fillBar) fillBar.style.width = "100%";
            if (percentText) percentText.textContent = "100%";
            updateStatus(100);

            // Brief pause at 100% before dissolve
            setTimeout(() => {
                preloader.classList.add("preloader-hidden");
                window.dispatchEvent(new CustomEvent("omni:preloader:complete"));

                setTimeout(() => {
                    preloader.style.display = "none";
                }, 700);
            }, 200);
        }

        // Start step loop
        requestAnimationFrame(step);

        // Safety fallback: maximum 2.8s
        setTimeout(() => {
            if (!animationDone) {
                finishPreloader();
            }
        }, 2800);
    }

    // Run as soon as DOM is ready or immediately if already interactive
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initPreloader);
    } else {
        initPreloader();
    }
})();
