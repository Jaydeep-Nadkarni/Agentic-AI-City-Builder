const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[char]));
}

function setConnection(online, text) {
  const pill = $("#connection-status");
  pill.textContent = text;
  pill.className = `status-pill ${online ? "status-ok" : "status-off"}`;
}

function render(data) {
  const agents = data.agents || [];
  const proposals = data.proposals || [];
  const history = data.history || [];
  const bridge = data.bridge || {};
  const config = data.config || {};
  const city = data.city || {};

  $("#metric-grid").innerHTML = [
    ["AI agents", agents.length, "Registered specialists"],
    ["Open proposals", proposals.length, proposals.length ? "Awaiting review" : "Queue is clear"],
    ["Planning budget", `$${Number(city.budget || 0).toLocaleString()}`, "Configured cycle limit"],
    ["City population", Number(city.population || 0).toLocaleString(), "Live game data unavailable"]
  ].map(([label, value, note]) => `<div class="metric"><div class="metric-label">${label}</div><div class="metric-value">${value}</div><div class="metric-note">${note}</div></div>`).join("");

  $("#agent-count").textContent = agents.length;
  $("#agent-list").innerHTML = agents.map((agent) => `<div class="agent">
    <span class="agent-dot"></span><div><div class="agent-name">${escapeHtml(agent.name)}</div><div class="agent-role">${escapeHtml(agent.role)} · ${escapeHtml(agent.type)}</div></div>
  </div>`).join("");

  $("#proposal-count").textContent = proposals.length;
  $("#proposal-list").className = proposals.length ? "proposal-list" : "proposal-list empty-state";
  $("#proposal-list").innerHTML = proposals.length ? proposals.map((proposal) => `<article class="proposal">
    <div class="proposal-top"><span class="proposal-action">${escapeHtml(proposal.action)}</span><span class="proposal-cost">$${Number(proposal.cost || 0).toLocaleString()}</span></div>
    <p class="proposal-reason">${escapeHtml(proposal.reason)}</p>
    <div class="proposal-meta">${escapeHtml(proposal.agent_role)} · ${proposal.requires_approval ? "Manual approval required" : "Ready for validation"}</div>
  </article>`).join("") : "No proposals yet. Run a planning cycle.";

  const capabilityCount = (data.bridge?.capabilities || []).length;
  $("#integration-list").innerHTML = [
    ["Planning engine", "Deterministic local planner", true],
    ["Groq model", config.model || "Not configured", Boolean(config.model)],
    ["TheoTown bridge", `${capabilityCount} capabilities inventoried`, Boolean(bridge.available)]
  ].map(([label, detail, available]) => `<div class="integration"><div><div class="integration-label">${escapeHtml(label)}</div><div class="integration-detail">${escapeHtml(detail)}</div></div><span class="integration-state ${available ? "available" : "unavailable"}">${available ? "READY" : "OFFLINE"}</span></div>`).join("");

  $("#activity-list").className = history.length ? "activity-list" : "activity-list empty-state";
  $("#activity-list").innerHTML = history.length ? [...history].reverse().map((event) => `<div class="activity">
    <span>${escapeHtml(event.created_at || "Recent")}</span><strong>${escapeHtml(event.city_id || "Planning cycle")}</strong><span>${Number(event.proposals || 0)} proposal(s)</span>
  </div>`).join("") : "No activity recorded yet.";
  $("#last-updated").textContent = `Updated ${new Date().toLocaleTimeString()}`;
}

async function loadDashboard() {
  try {
    const response = await fetch("/api/overview", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    render(await response.json());
    setConnection(true, "System online");
  } catch (error) {
    setConnection(false, "Disconnected");
    showToast(`Dashboard unavailable: ${error.message}`);
  }
}

async function runCycle() {
  const button = $("#cycle-button");
  button.disabled = true;
  button.textContent = "Planning…";
  try {
    const response = await fetch("/api/cycles", { method: "POST" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    await loadDashboard();
    showToast("Planning cycle completed.");
  } catch (error) {
    showToast(`Planning cycle failed: ${error.message}`);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Run planning cycle <span>→</span>';
  }
}

let toastTimer;
function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3500);
}

$("#refresh-button").addEventListener("click", loadDashboard);
$("#cycle-button").addEventListener("click", runCycle);
loadDashboard();
setInterval(loadDashboard, 15000);
