// ChatGPT-Style FinTech AI User Assistant Client

let currentSessionId = localStorage.getItem("fintech_session_id") || null;

// DOM Elements
const chatContainer = document.getElementById("chatContainer");
const messagesList = document.getElementById("messagesList");
const welcomeCard = document.getElementById("welcomeCard");
const userQueryInput = document.getElementById("userQueryInput");
const sendQueryBtn = document.getElementById("sendQueryBtn");
const newChatBtn = document.getElementById("newChatBtn");
const clearChatTopBtn = document.getElementById("clearChatTopBtn");
const headerCalcBtn = document.getElementById("headerCalcBtn");
const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const sidebarCollapseBtn = document.getElementById("sidebarCollapseBtn");
const chatSidebar = document.getElementById("chatSidebar");
const attachToolBtn = document.getElementById("attachToolBtn");
const promptCardsGrid = document.getElementById("promptCardsGrid");

// Drawer Elements
const calcDrawer = document.getElementById("calcDrawer");
const calcDrawerOverlay = document.getElementById("calcDrawerOverlay");
const closeCalcDrawerBtn = document.getElementById("closeCalcDrawerBtn");
const openEmiCalcBtn = document.getElementById("openEmiCalcBtn");
const openSipCalcBtn = document.getElementById("openSipCalcBtn");
const openCiCalcBtn = document.getElementById("openCiCalcBtn");
const openCagrCalcBtn = document.getElementById("openCagrCalcBtn");
const drawerTabs = document.querySelectorAll(".drawer-tab");
const tabPanes = document.querySelectorAll(".tab-pane");

// Category Prompt Definitions
const CATEGORY_PROMPTS = {
    all: [
        { icon: "fa-calculator", title: "Loan EMI Calculator", desc: "How much is the EMI for a ₹5 Lakh loan at 10% for 5 years?", prompt: "How much is the EMI for a ₹5 Lakh loan at 10% for 5 years?" },
        { icon: "fa-chart-line", title: "SIP Wealth Accumulator", desc: "What will ₹5,000/mo become in 10 years at 12% in a SIP?", prompt: "What will ₹5,000 per month become in 10 years at 12% in a SIP?" },
        { icon: "fa-receipt", title: "Tax Regime Comparison", desc: "Explain Old vs New Tax Regime: Which is better for me?", prompt: "Explain Old vs New Tax Regime: Which is better for me?" },
        { icon: "fa-vault", title: "Bank Deposit Safety", desc: "Is my money safe in bank accounts? (Explain DICGC rule)", prompt: "Is my money safe in bank accounts? (Explain DICGC ₹5 Lakh rule)" }
    ],
    loans: [
        { icon: "fa-calculator", title: "Loan EMI Calculation", desc: "Calculate monthly EMI for ₹10 Lakh loan at 9.5% for 7 years", prompt: "Calculate monthly EMI for ₹10 Lakh loan at 9.5% for 7 years" },
        { icon: "fa-percent", title: "Fixed vs Floating Rates", desc: "What is the difference between Fixed and Floating interest rates?", prompt: "What is the difference between Fixed and Floating interest rates?" },
        { icon: "fa-gauge-high", title: "CIBIL Score Rules", desc: "What is a good CIBIL score and how to improve it?", prompt: "What is a good CIBIL score and how to improve it?" },
        { icon: "fa-hand-holding-dollar", title: "Prepayment Penalties", desc: "Are there any prepayment or foreclosure charges on home loans?", prompt: "Are there any prepayment or foreclosure charges on home loans?" }
    ],
    invest: [
        { icon: "fa-chart-pie", title: "What is a SIP?", desc: "How does SIP investing work and can I start with ₹500?", prompt: "How does SIP investing work and can I start with ₹500?" },
        { icon: "fa-scale-balanced", title: "Direct vs Regular Mutual Funds", desc: "What is the difference between Direct and Regular mutual fund plans?", prompt: "What is the difference between Direct and Regular mutual fund plans?" },
        { icon: "fa-coins", title: "Sovereign Gold Bonds (SGB)", desc: "What are Sovereign Gold Bonds and how does the 2.5% interest work?", prompt: "What are Sovereign Gold Bonds and how does the 2.5% interest work?" },
        { icon: "fa-arrow-trend-up", title: "CAGR Calculation", desc: "Calculate CAGR from ₹1 Lakh to ₹2 Lakh in 5 years", prompt: "Calculate CAGR from ₹1 Lakh to ₹2 Lakh in 5 years" }
    ],
    tax: [
        { icon: "fa-receipt", title: "Old vs New Tax Regime", desc: "Compare tax slabs and deductions under Old vs New Tax Regime", prompt: "Compare tax slabs and deductions under Old vs New Tax Regime" },
        { icon: "fa-piggy-bank", title: "Section 80C Deductions", desc: "What tax investments qualify under Section 80C up to ₹1.5 Lakh?", prompt: "What tax investments qualify under Section 80C up to ₹1.5 Lakh?" },
        { icon: "fa-heart-pulse", title: "Section 80D Health Tax", desc: "How much tax deduction can I claim for health insurance premiums under 80D?", prompt: "How much tax deduction can I claim for health insurance premiums under 80D?" },
        { icon: "fa-file-invoice", title: "Capital Gains Tax (LTCG / STCG)", desc: "What are the latest capital gains tax rates on equity mutual funds?", prompt: "What are the latest capital gains tax rates on equity mutual funds?" }
    ],
    banking: [
        { icon: "fa-vault", title: "DICGC ₹5 Lakh Insurance", desc: "How does DICGC protect my deposits across savings and fixed deposits?", prompt: "How does DICGC protect my deposits across savings and fixed deposits?" },
        { icon: "fa-mobile-screen", title: "UPI Lite & Limits", desc: "How does UPI Lite work and what is the maximum transaction limit?", prompt: "How does UPI Lite work and what is the maximum transaction limit?" },
        { icon: "fa-money-bill-transfer", title: "NEFT vs RTGS vs IMPS", desc: "What are the timing and amount differences between NEFT, RTGS, and IMPS?", prompt: "What are the timing and amount differences between NEFT, RTGS, and IMPS?" },
        { icon: "fa-shield-halved", title: "Unauthorized Transaction Safety", desc: "What are the RBI customer zero-liability rules for banking fraud?", prompt: "What are the RBI customer zero-liability rules for banking fraud?" }
    ]
};

// Initialize on Load
document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
});

function initEventListeners() {
    // Chat Send button & Enter key
    sendQueryBtn.addEventListener("click", () => handleSendMessage());
    userQueryInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Auto-grow textarea & toggle send button active state
    userQueryInput.addEventListener("input", function() {
        this.style.height = "auto";
        this.style.height = Math.min(this.scrollHeight, 180) + "px";
        
        const hasContent = this.value.trim().length > 0;
        sendQueryBtn.disabled = !hasContent;
    });

    // New Chat & Clear Chat
    if (newChatBtn) newChatBtn.addEventListener("click", resetChatSession);
    if (clearChatTopBtn) clearChatTopBtn.addEventListener("click", resetChatSession);
    if (headerCalcBtn) headerCalcBtn.addEventListener("click", () => openDrawer("emi"));

    // Sidebar Toggles
    if (sidebarCollapseBtn) {
        sidebarCollapseBtn.addEventListener("click", () => {
            chatSidebar.classList.toggle("collapsed");
        });
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener("click", () => {
            chatSidebar.classList.toggle("mobile-open");
        });
    }

    // Sidebar Topic Chips
    document.querySelectorAll(".topic-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-query");
            handlePromptClick(query);
            if (window.innerWidth <= 768) {
                chatSidebar.classList.remove("mobile-open");
            }
        });
    });

    // Category Filter Pills
    document.querySelectorAll(".cat-pill").forEach(pill => {
        pill.addEventListener("click", () => {
            document.querySelectorAll(".cat-pill").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            const cat = pill.getAttribute("data-cat");
            renderCategoryPrompts(cat);
        });
    });

    // Tool shortcut button in bottom input
    if (attachToolBtn) {
        attachToolBtn.addEventListener("click", () => openDrawer("emi"));
    }

    // Calculator Drawer triggers
    if (openEmiCalcBtn) openEmiCalcBtn.addEventListener("click", () => openDrawer("emi"));
    if (openSipCalcBtn) openSipCalcBtn.addEventListener("click", () => openDrawer("sip"));
    if (openCiCalcBtn) openCiCalcBtn.addEventListener("click", () => openDrawer("ci"));
    if (openCagrCalcBtn) openCagrCalcBtn.addEventListener("click", () => openDrawer("cagr"));
    
    if (closeCalcDrawerBtn) closeCalcDrawerBtn.addEventListener("click", closeDrawer);
    if (calcDrawerOverlay) calcDrawerOverlay.addEventListener("click", closeDrawer);

    // Calculator tab switches
    drawerTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetTab = tab.getAttribute("data-tab");
            switchTab(targetTab);
        });
    });

    // Calculator Range syncs with dynamic label formatting
    syncSliderWithInput("emiPrincipal", "emiPrincipalRange", "lblEmiPrincipal", v => `₹${formatIndianCurrency(v)}`);
    syncSliderWithInput("emiRate", "emiRateRange", "lblEmiRate", v => `${v}%`);
    syncSliderWithInput("emiTenure", "emiTenureRange", "lblEmiTenure", v => `${v} Years`);

    // Calculation button triggers
    document.getElementById("calcEmiBtn").addEventListener("click", runEmiCalculation);
    document.getElementById("calcSipBtn").addEventListener("click", runSipCalculation);
    document.getElementById("calcCiBtn").addEventListener("click", runCiCalculation);
    document.getElementById("calcCagrBtn").addEventListener("click", runCagrCalculation);
}

function renderCategoryPrompts(categoryKey) {
    const list = CATEGORY_PROMPTS[categoryKey] || CATEGORY_PROMPTS.all;
    if (!promptCardsGrid) return;
    
    promptCardsGrid.innerHTML = list.map(item => `
        <div class="prompt-card" onclick="handlePromptClick('${escapeSingleQuotes(item.prompt)}')">
            <div class="prompt-card-icon"><i class="fa-solid ${item.icon}"></i></div>
            <div class="prompt-card-title">${escapeHtml(item.title)}</div>
            <div class="prompt-card-desc">"${escapeHtml(item.desc)}"</div>
        </div>
    `).join("");
}

function resetChatSession() {
    currentSessionId = null;
    localStorage.removeItem("fintech_session_id");
    messagesList.innerHTML = "";
    welcomeCard.style.display = "flex";
    userQueryInput.value = "";
    userQueryInput.style.height = "auto";
    sendQueryBtn.disabled = true;
}

// ----------------- Chat Handlers -----------------
function handlePromptClick(text) {
    userQueryInput.value = text;
    sendQueryBtn.disabled = false;
    handleSendMessage();
}

async function handleSendMessage() {
    const query = userQueryInput.value.trim();
    if (!query) return;

    // Hide welcome hero
    welcomeCard.style.display = "none";

    // Append User Message
    appendUserMessage(query);
    userQueryInput.value = "";
    userQueryInput.style.height = "auto";
    sendQueryBtn.disabled = true;

    // Append Loading Skeleton (ChatGPT style)
    const loadingRow = appendLoadingIndicator();

    try {
        const response = await fetch("/api/v1/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: query,
                session_id: currentSessionId,
                include_debug: false
            })
        });

        const data = await response.json();
        loadingRow.remove();

        if (response.ok) {
            currentSessionId = data.session_id;
            localStorage.setItem("fintech_session_id", currentSessionId);
            appendAssistantMessage(data);
        } else {
            appendAssistantMessage({
                answer: `⚠️ Error: ${data.detail || "Unable to process request."}`,
                confidence: { label: "unsupported", score: 0.0 },
                sources: []
            });
        }
    } catch (err) {
        loadingRow.remove();
        appendAssistantMessage({
            answer: "⚠️ Network connection error. Please ensure the backend server is running.",
            confidence: { label: "unsupported", score: 0.0 },
            sources: []
        });
    }

    scrollToBottom();
}

function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "message-row user";
    row.innerHTML = `
        <div class="user-bubble-box">
            ${escapeHtml(text)}
        </div>
    `;
    messagesList.appendChild(row);
    scrollToBottom();
}

function appendLoadingIndicator() {
    const row = document.createElement("div");
    row.className = "message-row assistant";
    row.innerHTML = `
        <div class="assistant-avatar">
            <i class="fa-solid fa-shield-halved"></i>
        </div>
        <div class="assistant-content-box" style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px; font-size: 0.9rem;">
            <i class="fa-solid fa-circle-notch fa-spin"></i> Retrieving verified guidelines & calculations...
        </div>
    `;
    messagesList.appendChild(row);
    scrollToBottom();
    return row;
}

function appendAssistantMessage(data) {
    const row = document.createElement("div");
    row.className = "message-row assistant";

    const conf = data.confidence || { label: "high", score: 0.85 };
    const confClass = `conf-${conf.label.toLowerCase()}`;
    const confScorePct = Math.round(conf.score * 100);

    // Citations Accordion
    let citationsHtml = "";
    if (data.sources && data.sources.length > 0) {
        const items = data.sources.map(s => {
            const sourceUrl = s.url || getRegulatoryUrl(s.source_name);
            return `
            <div class="source-item" onclick="window.open('${sourceUrl}', '_blank', 'noopener,noreferrer')" title="Click to view verified regulatory source on official portal">
                <div class="source-item-title">
                    <span>[${s.citation_id}] ${escapeHtml(s.title)}</span>
                    <a href="${sourceUrl}" target="_blank" rel="noopener noreferrer" class="source-org-tag" onclick="event.stopPropagation()">
                        ${escapeHtml(s.source_name)} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 0.65rem; margin-left: 3px;"></i>
                    </a>
                </div>
                <div class="source-item-excerpt">${escapeHtml(s.excerpt)}</div>
            </div>
            `;
        }).join("");

        citationsHtml = `
            <div class="sources-card">
                <div class="sources-header">
                    <i class="fa-solid fa-book-open"></i> Grounded Citations (${data.sources.length}) <span style="font-size: 0.7rem; font-weight: 400; text-transform: none; color: var(--accent-emerald); margin-left: auto;">🔗 Click to view official portal</span>
                </div>
                <div class="sources-grid">
                    ${items}
                </div>
            </div>
        `;
    }

    const formattedAnswer = formatMarkdownToHtml(data.answer);
    const answerId = data.request_id || Math.random().toString(36).substring(7);

    row.innerHTML = `
        <div class="assistant-avatar">
            <i class="fa-solid fa-shield-halved"></i>
        </div>
        <div class="assistant-content-box">
            <div class="answer-meta-row">
                <span class="conf-pill ${confClass}">
                    <i class="fa-solid fa-circle-check"></i> ${conf.label} Grounding (${confScorePct}%)
                </span>
                <span style="font-size: 0.72rem; color: var(--text-tertiary);">
                    ${escapeHtml(data.response_mode || "regulatory_rag")}
                </span>
            </div>
            
            <div class="answer-prose" id="ans-${answerId}">
                ${formattedAnswer}
            </div>

            ${citationsHtml}

            <div class="assistant-actions">
                <button class="action-btn" onclick="copyAnswerText('ans-${answerId}', this)" title="Copy text">
                    <i class="fa-regular fa-copy"></i> Copy
                </button>
                <button class="action-btn" onclick="submitFeedback('${data.request_id || ''}', 5, 'helpful')" title="Helpful">
                    <i class="fa-regular fa-thumbs-up"></i>
                </button>
                <button class="action-btn" onclick="submitFeedback('${data.request_id || ''}', 1, 'incorrect')" title="Report issue">
                    <i class="fa-regular fa-thumbs-down"></i>
                </button>
            </div>
        </div>
    `;

    messagesList.appendChild(row);
    scrollToBottom();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function copyAnswerText(elementId, btn) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-check" style="color: var(--accent-emerald);"></i> Copied!';
        setTimeout(() => {
            btn.innerHTML = originalHtml;
        }, 2000);
    });
}

// ----------------- Calculators -----------------
function openDrawer(tabName) {
    calcDrawer.classList.add("active");
    calcDrawerOverlay.classList.add("active");
    if (tabName) switchTab(tabName);
}

function closeDrawer() {
    calcDrawer.classList.remove("active");
    calcDrawerOverlay.classList.remove("active");
}

function switchTab(tabKey) {
    drawerTabs.forEach(t => t.classList.toggle("active", t.getAttribute("data-tab") === tabKey));
    tabPanes.forEach(p => p.classList.toggle("active", p.id === `tab-${tabKey}`));
}

function syncSliderWithInput(inputId, rangeId, labelId, formatFn) {
    const input = document.getElementById(inputId);
    const range = document.getElementById(rangeId);
    const label = document.getElementById(labelId);
    if (!input || !range) return;

    input.addEventListener("input", () => {
        const val = input.value.replace(/[^0-9.]/g, "");
        range.value = val;
        if (label && formatFn) label.innerText = formatFn(val);
    });
    range.addEventListener("input", () => {
        input.value = range.value;
        if (label && formatFn) label.innerText = formatFn(range.value);
    });
}

async function runEmiCalculation() {
    const principal = document.getElementById("emiPrincipal").value;
    const rate = document.getElementById("emiRate").value;
    const tenureYears = document.getElementById("emiTenure").value;

    try {
        const resp = await fetch("/api/v1/calculate/emi", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                principal: principal,
                annual_interest_rate_pct: rate,
                tenure_years: parseFloat(tenureYears),
                currency: "INR"
            })
        });
        const data = await resp.json();
        if (resp.ok) {
            document.getElementById("resMonthlyEmi").innerText = `₹${data.result.monthly_emi}`;
            document.getElementById("resPrincipal").innerText = `₹${data.inputs.principal}`;
            document.getElementById("resTotalInterest").innerText = `₹${data.result.total_interest}`;
            document.getElementById("resTotalPayment").innerText = `₹${data.result.total_payment}`;
        }
    } catch (err) {
        console.error("EMI calc error:", err);
    }
}

async function runSipCalculation() {
    const amount = document.getElementById("sipAmount").value;
    const rate = document.getElementById("sipRate").value;
    const years = document.getElementById("sipYears").value;

    try {
        const resp = await fetch("/api/v1/calculate/sip", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                monthly_investment: amount,
                annual_return_pct: rate,
                years: parseFloat(years),
                currency: "INR"
            })
        });
        const data = await resp.json();
        if (resp.ok) {
            document.getElementById("resSipFv").innerText = `₹${data.result.estimated_future_value}`;
            document.getElementById("resSipInvested").innerText = `₹${data.result.total_invested}`;
            document.getElementById("resSipGain").innerText = `₹${data.result.estimated_gain}`;
        }
    } catch (err) {
        console.error("SIP calc error:", err);
    }
}

async function runCiCalculation() {
    const principal = document.getElementById("ciPrincipal").value;
    const rate = document.getElementById("ciRate").value;
    const years = document.getElementById("ciYears").value;
    const compounds = parseInt(document.getElementById("ciCompounds").value);

    try {
        const resp = await fetch("/api/v1/calculate/compound-interest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                principal: principal,
                annual_rate_pct: rate,
                years: parseFloat(years),
                compounds_per_year: compounds,
                currency: "INR"
            })
        });
        const data = await resp.json();
        if (resp.ok) {
            document.getElementById("resCiMaturity").innerText = `₹${data.result.maturity_amount}`;
            document.getElementById("resCiInterest").innerText = `₹${data.result.total_interest}`;
        }
    } catch (err) {
        console.error("CI calc error:", err);
    }
}

async function runCagrCalculation() {
    const bv = document.getElementById("cagrBv").value;
    const ev = document.getElementById("cagrEv").value;
    const years = document.getElementById("cagrYears").value;

    try {
        const resp = await fetch("/api/v1/calculate/cagr", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                beginning_value: bv,
                ending_value: ev,
                years: parseFloat(years)
            })
        });
        const data = await resp.json();
        if (resp.ok) {
            document.getElementById("resCagrPct").innerText = data.result.cagr_pct;
            document.getElementById("resCagrAbs").innerText = `₹${data.result.absolute_gain} (${data.result.absolute_gain_pct})`;
        }
    } catch (err) {
        console.error("CAGR calc error:", err);
    }
}

async function submitFeedback(answerId, rating, feedbackType) {
    if (!answerId) return;
    try {
        await fetch("/api/v1/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                answer_id: answerId,
                rating: rating,
                feedback_type: feedbackType
            })
        });
        alert("Thank you for your feedback!");
    } catch (err) {
        console.error(err);
    }
}

// ----------------- Helpers -----------------
function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function escapeSingleQuotes(str) {
    if (!str) return "";
    return str.replace(/'/g, "\\'");
}

function formatIndianCurrency(num) {
    const n = parseFloat(num);
    if (isNaN(n)) return num;
    return n.toLocaleString('en-IN');
}

function getRegulatoryUrl(sourceName) {
    if (!sourceName) return "https://www.rbi.org.in";
    const name = sourceName.toLowerCase();
    if (name.includes("rbi") || name.includes("reserve bank")) return "https://www.rbi.org.in";
    if (name.includes("sebi") || name.includes("securities")) return "https://www.sebi.gov.in";
    if (name.includes("tax") || name.includes("income")) return "https://incometaxindia.gov.in";
    if (name.includes("irdai") || name.includes("insurance")) return "https://irdai.gov.in";
    if (name.includes("npci") || name.includes("payments") || name.includes("upi")) return "https://www.npci.org.in";
    if (name.includes("pfrda") || name.includes("pension")) return "https://www.pfrda.org.in";
    if (name.includes("amfi") || name.includes("mutual fund")) return "https://www.amfiindia.com";
    return "https://www.rbi.org.in";
}

function formatMarkdownToHtml(md) {
    if (!md) return "";
    let html = escapeHtml(md);

    // Markdown Table parsing
    html = html.replace(/\|(.+)\|\n\|[-|\s]+\|\n((?:\|.+\|\n?)+)/g, function(match, headerRow, bodyRows) {
        const headers = headerRow.split('|').filter(h => h.trim()).map(h => `<th>${h.trim()}</th>`).join('');
        const rows = bodyRows.trim().split('\n').map(row => {
            const cells = row.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
            return `<tr>${cells}</tr>`;
        }).join('');
        return `<table><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table>`;
    });

    // Headers
    html = html.replace(/### (.*?)\n/g, '<h4 style="margin: 8px 0; color: var(--accent-emerald); font-weight: 600;">$1</h4>');
    html = html.replace(/## (.*?)\n/g, '<h3 style="margin: 10px 0; color: #ffffff; font-weight: 600;">$1</h3>');

    // Bold & italic
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Code
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');

    // Bullet points
    html = html.replace(/^- (.*?)(?=\n|$)/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Linebreaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');

    return `<p>${html}</p>`;
}
