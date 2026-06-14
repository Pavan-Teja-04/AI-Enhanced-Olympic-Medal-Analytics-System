const API_BASE = "http://127.0.0.1:5000/api";

const chartColors = ["#2563eb", "#c99700", "#8a95a3", "#a35f2b", "#067647"];

function setTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
}

function initTheme() {
    setTheme(localStorage.getItem("theme") || "light");
    const toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) {
        toggle.addEventListener("click", () => {
            const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            setTheme(next);
        });
    }
}

function setActiveNav() {
    const page = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav a").forEach((link) => {
        if (link.getAttribute("href") === page) {
            link.classList.add("active");
        }
    });
}

function getCurrentUser() {
    const rawUser = localStorage.getItem("olympicUser");
    if (!rawUser) return null;
    try {
        return JSON.parse(rawUser);
    } catch (error) {
        localStorage.removeItem("olympicUser");
        return null;
    }
}

function requireLogin() {
    const publicPages = ["index.html", "login.html"];
    const page = location.pathname.split("/").pop() || "index.html";
    if (!publicPages.includes(page) && !getCurrentUser()) {
        location.href = "login.html";
    }
}

function updateAuthNav() {
    const user = getCurrentUser();
    const nav = document.querySelector(".nav");
    const loginLink = document.querySelector('.nav a[href="login.html"]');
    if (!nav) return;

    if (!user) {
        if (loginLink) loginLink.textContent = "Login";
        return;
    }

    const chip = document.createElement("span");
    chip.className = "user-chip";
    chip.textContent = user.name;

    const logout = document.createElement("button");
    logout.className = "btn";
    logout.type = "button";
    logout.dataset.logout = "";
    logout.textContent = "Logout";

    if (loginLink) {
        loginLink.replaceWith(chip, logout);
    } else if (!document.querySelector("[data-logout]")) {
        nav.append(chip, logout);
    }

    const logoutButton = document.querySelector("[data-logout]");
    if (logoutButton) {
        logoutButton.addEventListener("click", () => {
            localStorage.removeItem("olympicUser");
            location.href = "login.html";
        });
    }
}

async function api(path, options = {}) {
    let response;
    try {
        response = await fetch(`${API_BASE}${path}`, {
            headers: { "Content-Type": "application/json" },
            ...options,
        });
    } catch (error) {
        throw new Error("Backend API is not running. Open run_backend.bat, keep that terminal open, then refresh this page.");
    }

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
}

function formatNumber(value) {
    return Number(value || 0).toLocaleString();
}

function createMedalBadge(medal) {
    const badge = document.createElement("span");
    badge.className = `badge ${String(medal || "").toLowerCase()}`;
    badge.textContent = medal || "Unknown";
    return badge;
}

function showMessage(target, text, type = "success") {
    const node = document.querySelector(target);
    if (!node) return;
    node.className = `message ${type}`;
    node.textContent = text;
    node.classList.remove("hidden");
}

async function loadOverview() {
    const overview = await api("/analytics/overview");
    const statMap = {
        total_medals: "totalMedals",
        total_countries: "totalCountries",
        total_sports: "totalSports",
        first_year: "firstYear",
        latest_year: "latestYear",
    };
    Object.entries(statMap).forEach(([key, id]) => {
        const node = document.getElementById(id);
        if (node) node.textContent = formatNumber(overview[key]);
    });
}

async function loadDashboardCharts() {
    const countries = await api("/analytics/top-countries?limit=10");
    const sports = await api("/analytics/sport-distribution?limit=10");
    const trends = await api("/analytics/medal-trends");

    const countryCanvas = document.getElementById("countryChart");
    if (countryCanvas) {
        new Chart(countryCanvas, {
            type: "bar",
            data: {
                labels: countries.map((item) => item.country),
                datasets: [{ label: "Medals", data: countries.map((item) => item.medals), backgroundColor: chartColors[0] }],
            },
        });
    }

    const sportCanvas = document.getElementById("sportChart");
    if (sportCanvas) {
        new Chart(sportCanvas, {
            type: "doughnut",
            data: {
                labels: sports.map((item) => item.sport),
                datasets: [{ data: sports.map((item) => item.medals), backgroundColor: chartColors }],
            },
        });
    }

    const trendCanvas = document.getElementById("trendChart");
    if (trendCanvas) {
        new Chart(trendCanvas, {
            type: "line",
            data: {
                labels: trends.map((item) => item.year),
                datasets: [{ label: "Medals", data: trends.map((item) => item.medals), borderColor: chartColors[0], tension: 0.25 }],
            },
        });
    }
}

async function loadStandings() {
    const rows = await api("/medals?limit=250");
    renderMedalRows(rows);

    const form = document.getElementById("filterForm");
    if (form) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const params = new URLSearchParams(new FormData(form));
            const filtered = await api(`/medals?${params.toString()}&limit=250`);
            renderMedalRows(filtered);
        });
    }
}

function renderMedalRows(rows) {
    const body = document.getElementById("medalsBody");
    if (!body) return;
    body.replaceChildren();

    const uniqueRows = [];
    const seen = new Set();

    rows.forEach((row) => {
        const key = [
            row.year,
            row.country,
            row.sport,
            row.event_name,
            row.medal,
        ].map((value) => String(value || "").toLowerCase().trim()).join("|");

        if (!seen.has(key)) {
            seen.add(key);
            uniqueRows.push(row);
        }
    });

    uniqueRows.forEach((row) => {
        const tr = document.createElement("tr");
        ["year", "country", "sport", "event_name"].forEach((key) => {
            const td = document.createElement("td");
            td.textContent = row[key] || "";
            tr.appendChild(td);
        });

        const medalCell = document.createElement("td");
        medalCell.appendChild(createMedalBadge(row.medal));
        tr.appendChild(medalCell);
        body.appendChild(tr);
    });
}

async function loadAnalytics() {
    await loadOverview();
    await loadDashboardCharts();

    const form = document.getElementById("trendForm");
    if (form) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const params = new URLSearchParams(new FormData(form));
            const report = await api(`/ai/trend-report?${params.toString()}`);
            document.getElementById("trendReport").textContent = report.insight;
        });
    }
}

function initAuth() {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const loginTab = document.getElementById("loginTab");
    const registerTab = document.getElementById("registerTab");

    if (loginTab && registerTab) {
        loginTab.addEventListener("click", () => {
            loginForm.classList.remove("hidden");
            registerForm.classList.add("hidden");
        });
        registerTab.addEventListener("click", () => {
            registerForm.classList.remove("hidden");
            loginForm.classList.add("hidden");
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const payload = Object.fromEntries(new FormData(loginForm));
                const result = await api("/auth/login", { method: "POST", body: JSON.stringify(payload) });
                localStorage.setItem("olympicUser", JSON.stringify(result.user));
                showMessage("#authMessage", "Login successful. Redirecting to dashboard.");
                location.href = "index.html";
            } catch (error) {
                showMessage("#authMessage", error.message, "error");
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const payload = Object.fromEntries(new FormData(registerForm));
                const result = await api("/auth/register", { method: "POST", body: JSON.stringify(payload) });
                localStorage.setItem("olympicUser", JSON.stringify(result.user));
                showMessage("#authMessage", "Registration successful. Redirecting to dashboard.");
                location.href = "index.html";
            } catch (error) {
                showMessage("#authMessage", error.message, "error");
            }
        });
    }
}

function initPrediction() {
    const form = document.getElementById("predictionForm");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = Object.fromEntries(new FormData(form));
        try {
            const result = await api("/analytics/predict", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            const predictionResult = document.getElementById("predictionResult");
            predictionResult.replaceChildren();

            const title = document.createElement("h3");
            title.textContent = `${result.country} - ${result.sport} - ${result.year}`;

            const medalLine = document.createElement("p");
            medalLine.append("Predicted medal: ", createMedalBadge(result.predicted_medal));

            const confidence = document.createElement("p");
            confidence.textContent = `Confidence: ${result.probability_percent}%`;

            const note = document.createElement("p");
            note.className = "muted";
            note.textContent = result.model_note;

            predictionResult.append(title, medalLine, confidence, note);

            const probabilityList = document.getElementById("probabilityList");
            probabilityList.replaceChildren();
            Object.entries(result.probabilities).forEach(([medal, value]) => {
                const item = document.createElement("li");
                item.textContent = `${medal}: ${value}%`;
                probabilityList.appendChild(item);
            });
        } catch (error) {
            showMessage("#predictionMessage", error.message, "error");
        }
    });
}

function initAiInsights() {
    const form = document.getElementById("aiForm");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const params = new URLSearchParams(new FormData(form));
        try {
            const result = await api(`/ai/country-summary?${params.toString()}`);
            document.getElementById("aiInsight").textContent = result.insight;
        } catch (error) {
            showMessage("#aiMessage", error.message, "error");
        }
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    initTheme();
    requireLogin();
    setActiveNav();
    updateAuthNav();
    initAuth();
    initPrediction();
    initAiInsights();

    try {
        if (document.body.dataset.page === "dashboard") {
            await loadOverview();
            await loadDashboardCharts();
        }
        if (document.body.dataset.page === "standings") {
            await loadStandings();
        }
        if (document.body.dataset.page === "analytics") {
            await loadAnalytics();
        }
    } catch (error) {
        const status = document.getElementById("pageStatus");
        if (status) {
            status.textContent = error.message;
            status.className = "message error";
        }
    }
});
