
/* ================= TOAST ================= */
function showToast(msg) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const t = document.createElement("div");
    t.className = "toast";
    t.innerText = msg;

    container.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

/* ================= CLOCK ================= */
function updateClock() {
    const now = new Date();
    const clock = document.getElementById("clock");
    const date = document.getElementById("date");

    if (clock) {
        clock.innerText = now.toLocaleTimeString("tr-TR");
    }

    if (date) {
        date.innerText = now.toLocaleDateString("tr-TR", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric"
        });
    }
}
setInterval(updateClock, 1000);
updateClock();

/* ================= AI STATE ================= */
const circle = document.querySelector(".circle");

function setState(state) {
    if (!circle) return;

    circle.classList.remove("listening", "thinking", "idle");

    if (state === "listening") circle.classList.add("listening");
    if (state === "idle") circle.classList.add("idle");
}

/* ================= BUTTONS ================= */
const micBtn = document.querySelector(".mic");
const toggleBtn = document.querySelector(".toggle");
const stopBtn = document.querySelector(".stop");

if (micBtn) {
    micBtn.onclick = () => {
        setState("listening");
        showToast("🎤 Listening...");
    };
}

if (toggleBtn) {
    toggleBtn.onclick = () => {
        setState("idle");
        showToast("⏯ Processing...");
    };
}

/* ================= SHUTDOWN ================= */
const shutdownScreen = document.getElementById("shutdown-screen");
const bootScreen = document.getElementById("boot-screen");
const bootBar = document.getElementById("boot-progress");
const bootStatus = document.getElementById("boot-status");
const openBtn = document.getElementById("open-btn");

/* 🔴 CRITICAL FIX: GLOBAL BOOT CONTROL */
let bootInterval = null;

/* ================= SHUTDOWN BUTTON ================= */
if (stopBtn) {
    stopBtn.onclick = () => {
        if (shutdownScreen) shutdownScreen.classList.remove("hidden");
        showToast("⛔ System Offline");
    };
}

/* ================= BOOT SYSTEM (FIXED) ================= */
function startBoot() {

    // 🔴 kill previous instance
    if (bootInterval) {
        clearInterval(bootInterval);
        bootInterval = null;
    }

    let progress = 0;
    let stepIndex = 0;

    const steps = [
        "Initializing...",
        "Loading AI Core...",
        "Starting Systems...",
        "Optimizing Modules...",
        "Finalizing..."
    ];

    if (bootScreen) bootScreen.classList.remove("hidden");

    bootInterval = setInterval(() => {

        progress += 2;

        if (bootBar) bootBar.style.width = progress + "%";

        const calculatedStep = Math.floor(progress / 20);

        if (calculatedStep !== stepIndex && steps[calculatedStep]) {
            stepIndex = calculatedStep;
            if (bootStatus) bootStatus.innerText = steps[stepIndex];
        }

        if (progress >= 100) {

            clearInterval(bootInterval);
            bootInterval = null;

            if (bootBar) bootBar.style.width = "100%";

            setTimeout(() => {
                if (bootScreen) bootScreen.classList.add("hidden");
                showToast("🟢 JARVIS ONLINE");
            }, 400);
        }

    }, 40);
}

/* ================= OPEN BUTTON ================= */
if (openBtn) {
    openBtn.onclick = () => {
        if (shutdownScreen) shutdownScreen.classList.add("hidden");
        startBoot();
    };
}