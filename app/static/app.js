// ============================================================
//  HORY A VODA – App JS v4.0
//  Modern redesign – adapted selectors to match new HTML
// ============================================================

// ── STATE ────────────────────────────────────────────────────
const state = {
  token: sessionStorage.getItem("token") || null,
  user: null,
  categories: [],
  equipment: [],
  selectedCategory: null,
  selectedItem: null,
  activeStatusFilter: "AVAILABLE",
};

// ── INIT ─────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupModals();
  setupAuth();
  setupFilters();
  setupReservationForm();
  setupEquipmentManagement();
  setupConditionManagement();
  setupCategoryManagement();

  loadCategories();
  loadEquipment();
  checkCurrentUser();
});

// ── 1. NAVIGATION ─────────────────────────────────────────────
function setupNavigation() {
  const navLinks       = document.querySelectorAll(".nav-link");
  const panels         = document.querySelectorAll(".tab-panel");
  const mobileTrigger  = document.getElementById("mobile-nav-trigger");
  const mobileMenu     = document.getElementById("mobile-nav-menu");
  const mobileItems    = document.querySelectorAll(".mobile-nav-item");
  const mobileText     = document.getElementById("mobile-nav-trigger-text");

  function closeMobileMenu() {
    if (mobileMenu) {
      mobileMenu.classList.remove("open");
    }
    if (mobileTrigger) {
      mobileTrigger.classList.remove("open");
      mobileTrigger.setAttribute("aria-expanded", "false");
    }
  }

  function activateTab(tab) {
    // Desktop tabs
    navLinks.forEach(l => {
      const isActive = l.dataset.tab === tab;
      l.classList.toggle("active", isActive);
      l.setAttribute("aria-selected", isActive ? "true" : "false");
    });

    // Mobile drop-down items
    mobileItems.forEach(item => {
      const isActive = item.dataset.tab === tab;
      item.classList.toggle("active", isActive);
      item.setAttribute("aria-selected", isActive ? "true" : "false");
      if (isActive && mobileText) {
        const titleEl = item.querySelector(".mobile-nav-item-title");
        mobileText.textContent = titleEl ? titleEl.textContent.trim() : item.textContent.trim();
      }
    });

    // Switch panels
    panels.forEach(p => p.classList.remove("active"));
    const target = document.getElementById(`panel-${tab}`);
    if (target) target.classList.add("active");

    // Load tab-specific data
    if (tab === "dashboard") loadEquipment();
    if (tab === "rezervace") renderActiveReservationsTable();
    if (tab === "cenik")     renderCategoriesCards();
  }

  // Desktop tab clicks
  navLinks.forEach(link => {
    link.addEventListener("click", () => {
      activateTab(link.dataset.tab);
    });
  });

  // Mobile trigger toggle
  if (mobileTrigger && mobileMenu) {
    mobileTrigger.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = mobileMenu.classList.contains("open");
      if (isOpen) {
        closeMobileMenu();
      } else {
        mobileMenu.classList.add("open");
        mobileTrigger.classList.add("open");
        mobileTrigger.setAttribute("aria-expanded", "true");
      }
    });

    // Mobile item clicks
    mobileItems.forEach(item => {
      item.addEventListener("click", (e) => {
        e.stopPropagation();
        activateTab(item.dataset.tab);
        closeMobileMenu();
      });
    });

    // Close on click outside
    document.addEventListener("click", (e) => {
      if (!mobileMenu.contains(e.target) && !mobileTrigger.contains(e.target)) {
        closeMobileMenu();
      }
    });

    // Close on Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeMobileMenu();
      }
    });
  }
}

// ── 2. MODALS ─────────────────────────────────────────────────
function setupModals() {
  // Close buttons
  document.querySelectorAll(".modal-close").forEach(btn => {
    btn.addEventListener("click", () => closeAllModals());
  });

  // Click outside to close
  document.querySelectorAll(".modal-overlay").forEach(overlay => {
    overlay.addEventListener("click", e => {
      if (e.target === overlay) closeAllModals();
    });
  });

  // Escape key
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeAllModals();
  });
}

function closeAllModals() {
  document.querySelectorAll(".modal-overlay").forEach(m => m.classList.add("hidden"));
}

function openModal(id) {
  closeAllModals();
  const el = document.getElementById(id);
  if (el) el.classList.remove("hidden");
}

// ── 3. AUTH ──────────────────────────────────────────────────
function setupAuth() {
  const btnOpenLogin = document.getElementById("btn-open-login");
  const formLogin    = document.getElementById("form-login");
  const btnLogout    = document.getElementById("btn-logout");

  btnOpenLogin.addEventListener("click", () => openModal("modal-login"));

  document.getElementById("btn-fill-staff").addEventListener("click", () => {
    document.getElementById("login-username").value = "obsluha";
    document.getElementById("login-password").value = "Heslo123!";
  });

  document.getElementById("btn-fill-admin").addEventListener("click", () => {
    document.getElementById("login-username").value = "admin";
    document.getElementById("login-password").value = "Admin123!";
  });

  formLogin.addEventListener("submit", async e => {
    e.preventDefault();
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    const errorBox = document.getElementById("login-error");
    errorBox.classList.add("hidden");

    try {
      const body = new URLSearchParams({ username, password });
      const resp = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Přihlášení se nezdařilo.");
      }

      const data = await resp.json();
      state.token = data.access_token;
      sessionStorage.setItem("token", state.token);
      closeAllModals();
      showToast(`Přihlášen jako ${username}`, "success");
      await checkCurrentUser();
      loadEquipment();
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.classList.remove("hidden");
    }
  });

  btnLogout.addEventListener("click", () => {
    state.token = null;
    state.user  = null;
    sessionStorage.removeItem("token");
    updateAuthUI();
    showToast("Byl jste odhlášen.", "info");
    loadEquipment();
  });
}

async function checkCurrentUser() {
  if (!state.token) { updateAuthUI(); return; }
  try {
    const resp = await fetch("/api/v1/auth/me", {
      headers: { "Authorization": `Bearer ${state.token}` },
    });
    if (resp.ok) {
      state.user = await resp.json();
    } else {
      state.token = null;
      sessionStorage.removeItem("token");
    }
  } catch {
    state.token = null;
  }
  updateAuthUI();
}

function updateAuthUI() {
  const btnLogin  = document.getElementById("btn-open-login");
  const userInfo  = document.getElementById("user-info");
  const nameEl    = document.getElementById("user-name-display");

  if (state.token && state.user) {
    btnLogin.classList.add("hidden");
    userInfo.classList.remove("hidden");
    nameEl.textContent = `${state.user.username} (${state.user.role})`;
  } else {
    btnLogin.classList.remove("hidden");
    userInfo.classList.add("hidden");
  }

  renderActiveReservationsTable();
  renderEquipmentTable();
}

// ── 4. DATA LOADING ───────────────────────────────────────────
async function loadCategories() {
  try {
    const resp = await fetch("/api/v1/categories/");
    if (!resp.ok) throw new Error();
    state.categories = await resp.json();
    populateCategoryDropdowns();
    renderCategoriesCards();
  } catch {
    showToast("Nepodařilo se načíst kategorie.", "error");
  }
}

async function loadEquipment() {
  const tbody = document.getElementById("equipment-table-body");
  try {
    const headers = {};
    if (state.token) {
      headers["Authorization"] = `Bearer ${state.token}`;
    }
    const resp = await fetch("/api/v1/equipment/", { headers });
    if (!resp.ok) throw new Error();
    state.equipment = await resp.json();
    renderMorningStats();
    renderEquipmentTable();
    renderActiveReservationsTable();
  } catch {
    if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-muted">Chyba při načítání vybavení.</td></tr>`;
  }
}

// ── 5. KPI STATS ──────────────────────────────────────────────
function renderMorningStats() {
  const active = state.equipment.filter(i => !i.is_deleted);
  const available = active.filter(i => i.status === "AVAILABLE").length;
  const inService  = active.filter(i => i.status === "IN_SERVICE").length;
  const rented     = active.filter(i => i.status === "RENTED" || i.status === "RESERVED").length;
  const total      = active.length;

  document.getElementById("stat-count-available").textContent = available;
  document.getElementById("stat-count-service").textContent   = inService;
  document.getElementById("stat-count-rented").textContent    = rented;
  document.getElementById("stat-count-total").textContent     = total;
}

// ── 6. EQUIPMENT TABLE ────────────────────────────────────────
function renderEquipmentTable() {
  const tbody        = document.getElementById("equipment-table-body");
  const searchVal    = (document.getElementById("filter-search")?.value || "").toLowerCase().trim();
  const catId        = document.getElementById("filter-category")?.value || "";

  const filtered = state.equipment.filter(item => {
    if (item.is_deleted) return false;
    if (searchVal && 
        !item.inventory_number.toLowerCase().includes(searchVal) && 
        !item.size.toLowerCase().includes(searchVal) &&
        !(item.reservation_code && item.reservation_code.toLowerCase().includes(searchVal)) &&
        !(item.reservation_customer && item.reservation_customer.toLowerCase().includes(searchVal))
    ) return false;
    if (catId && String(item.category_id) !== catId) return false;

    const f = state.activeStatusFilter;
    if (f === "AVAILABLE"         && item.status !== "AVAILABLE") return false;
    if (f === "IN_SERVICE"        && item.status !== "IN_SERVICE") return false;
    if (f === "RENTED_OR_RESERVED" && item.status !== "RENTED" && item.status !== "RESERVED") return false;
    return true;
  });

  const countBadge = document.getElementById("table-results-count");
  if (countBadge) {
    const total = state.equipment.filter(i => !i.is_deleted).length;
    countBadge.textContent = `${filtered.length} z ${total} kusů`;
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-muted">Žádné vybavení neodpovídá filtrům.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(item => {
    const cat        = state.categories.find(c => c.id === item.category_id) || item.category;
    const catName    = cat ? cat.name : "—";
    const dailyPrice = cat ? `${cat.daily_price} Kč` : "—";
    const wkndPrice  = cat ? `${cat.weekend_price} Kč` : "—";

    const badgeClass = {
      AVAILABLE: "badge-available",
      IN_SERVICE: "badge-service",
      RENTED:     "badge-rented",
      RESERVED:   "badge-reserved",
    }[item.status] || "badge-retired";

    const statusLabel = {
      AVAILABLE: "Volné",
      IN_SERVICE: "V servisu",
      RENTED:     "Půjčeno",
      RESERVED:   "Rezervováno",
      RETIRED:    "Vyřazeno",
    }[item.status] || item.status;

    const isStaffOrAdmin = state.token && state.user && (state.user.role === "STAFF" || state.user.role === "ADMIN");

    let statusCellContent = `<span class="badge ${badgeClass}">${statusLabel}</span>`;
    // GDPR: Osobní údaje zákazníka a kód rezervace vidí výhradně přihlášený personál
    if (isStaffOrAdmin) {
      if (item.status === "RESERVED") {
        const codeHtml = item.reservation_code 
          ? `<div class="res-tag"><span class="res-num" title="Číslo rezervace zákazníka">${escapeHtml(item.reservation_code)}</span></div>` 
          : "";
        const custHtml = item.reservation_customer 
          ? `<div class="res-cust" title="${escapeHtml(item.reservation_customer)}">👤 ${escapeHtml(item.reservation_customer)}</div>` 
          : "";
        const noteHtml = item.reservation_note 
          ? `<div class="res-note text-xs text-muted">${escapeHtml(item.reservation_note)}</div>` 
          : "";
        statusCellContent = `
          <div class="status-cell-wrap">
            <span class="badge ${badgeClass}">${statusLabel}</span>
            ${codeHtml}
            ${custHtml}
            ${noteHtml}
          </div>
        `;
      } else if (item.status === "RENTED" && (item.reservation_customer || item.reservation_code)) {
        statusCellContent = `
          <div class="status-cell-wrap">
            <span class="badge ${badgeClass}">${statusLabel}</span>
            <div class="res-cust text-xs text-muted" title="${escapeHtml(item.reservation_customer || '')}">👤 ${escapeHtml(item.reservation_customer || '')}</div>
          </div>
        `;
      }
    }

    const condHtml = state.token
      ? `<button class="condition-btn btn-open-condition" data-id="${item.id}" title="Upravit stav opotřebení">${escapeHtml(item.condition_state)}<span class="pencil">✎</span></button>`
      : `<span class="text-sm">${escapeHtml(item.condition_state)}</span>`;

    return `
      <tr>
        <td><span class="inv-chip">${escapeHtml(item.inventory_number)}</span></td>
        <td><strong class="fw-bold">${escapeHtml(catName)}</strong></td>
        <td>${escapeHtml(item.size)}</td>
        <td>${item.purchase_year}</td>
        <td>${condHtml}</td>
        <td>
          <div class="price-cell">
            <span class="price-day">${dailyPrice} / den</span>
            <span class="price-wknd">víkend ${wkndPrice}</span>
          </div>
        </td>
        <td>${statusCellContent}</td>
        <td class="text-right">
          <div class="row-actions">${renderRowActions(item)}</div>
        </td>
      </tr>`;
  }).join("");

  attachRowActionListeners();
}

function renderRowActions(item) {
  if (!state.token) {
    return `<span class="text-muted text-xs">Pouze personál</span>`;
  }
  const actions = [];
  actions.push(`<button class="btn btn-xs btn-outline btn-action" data-action="edit-condition" data-id="${item.id}" title="Upravit stav opotřebení kusu">Stav</button>`);

  if (item.status === "AVAILABLE") {
    actions.push(`<button class="btn btn-xs btn-secondary btn-action" data-action="set-service" data-id="${item.id}" title="Odeslat do servisu">Do servisu</button>`);
    actions.push(`<button class="btn btn-xs btn-primary btn-action" data-action="set-rent" data-id="${item.id}" title="Vydat zákazníkovi k půjčení">Půjčit</button>`);
  } else if (item.status === "IN_SERVICE") {
    actions.push(`<button class="btn btn-xs btn-success btn-action" data-action="set-available" data-id="${item.id}" title="Ukončit servis a vrátit k půjčení">Ze servisu</button>`);
  } else if (item.status === "RESERVED") {
    actions.push(`<button class="btn btn-xs btn-primary btn-action" data-action="issue-reserved" data-id="${item.id}" title="Zákazník si přišel vyzvednout rezervaci – označit jako PŮJČENÝ">Vydat (půjčit)</button>`);
    actions.push(`<button class="btn btn-xs btn-outline btn-action" data-action="cancel-reservation" data-id="${item.id}" title="Zrušit rezervaci a uvolnit kus zpět k půjčení">Zrušit rez.</button>`);
  } else if (item.status === "RENTED") {
    actions.push(`<button class="btn btn-xs btn-success btn-action" data-action="set-available" data-id="${item.id}" title="Zákazník vrátil vybavení – vrátit k půjčení">Vráceno</button>`);
  }
  actions.push(`<button class="btn btn-xs btn-ghost btn-action" data-action="delete" data-id="${item.id}" title="Vyřadit kus z aktivního inventáře">Vyřadit</button>`);

  return actions.join("");
}

function attachRowActionListeners() {
  document.querySelectorAll(".btn-open-condition").forEach(btn => {
    btn.addEventListener("click", () => openConditionModal(btn.dataset.id));
  });

  document.querySelectorAll(".btn-action").forEach(btn => {
    btn.addEventListener("click", async () => {
      const { action, id } = btn.dataset;
      if (action === "edit-condition") {
        openConditionModal(id);
      } else if (action === "set-service") {
        await updateEquipmentStatus(id, "IN_SERVICE");
      } else if (action === "set-available") {
        await updateEquipmentStatus(id, "AVAILABLE");
      } else if (action === "set-rent") {
        await updateEquipmentStatus(id, "RENTED");
      } else if (action === "issue-reserved") {
        const item = state.equipment.find(i => i.id == id);
        const codeMsg = item && item.reservation_code ? ` (rezervace ${item.reservation_code})` : "";
        if (confirm(`Označit kus jako PŮJČENÝ pro zákazníka${codeMsg}?`)) {
          await updateEquipmentStatus(id, "RENTED");
        }
      } else if (action === "cancel-reservation") {
        const item = state.equipment.find(i => i.id == id);
        const codeMsg = item && item.reservation_code ? ` ${item.reservation_code}` : "";
        if (confirm(`Opravdu zrušit rezervaci${codeMsg} a uvolnit kus zpět k běžnému půjčení?`)) {
          await updateEquipmentStatus(id, "AVAILABLE");
        }
      } else if (action === "delete") {
        if (confirm("Opravdu vyřadit tento kus z aktivního inventáře?")) {
          await deleteEquipment(id);
        }
      }
    });
  });
}

async function updateEquipmentStatus(itemId, newStatus) {
  if (!state.token) {
    showToast("Pro tuto akci se musíte přihlásit.", "error");
    return;
  }
  try {
    const resp = await fetch(`/api/v1/equipment/${itemId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${state.token}`,
      },
      body: JSON.stringify({ status: newStatus }),
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Chyba při změně stavu");
    }
    showToast(`Status změněn na ${newStatus}`, "success");
    await loadEquipment();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteEquipment(itemId) {
  if (!state.token) return;
  try {
    const resp = await fetch(`/api/v1/equipment/${itemId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${state.token}` },
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Chyba při vyřazení kusu.");
    }
    showToast("Kus byl bezpečně vyřazen.", "info");
    await loadEquipment();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ── 7. FILTERS ────────────────────────────────────────────────
function setupFilters() {
  const searchEl  = document.getElementById("filter-search");
  const catEl     = document.getElementById("filter-category");
  const refreshEl = document.getElementById("btn-refresh");

  // KPI filter buttons
  document.querySelectorAll(".kpi-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      state.activeStatusFilter = btn.dataset.statusFilter;
      document.querySelectorAll(".kpi-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderEquipmentTable();
    });
  });

  if (searchEl)  searchEl.addEventListener("input", renderEquipmentTable);
  if (catEl)     catEl.addEventListener("change", renderEquipmentTable);
  if (refreshEl) refreshEl.addEventListener("click", () => {
    loadEquipment();
    showToast("Data inventáře obnovena.", "info");
  });
}

function populateCategoryDropdowns() {
  const filterCat = document.getElementById("filter-category");
  const resCat    = document.getElementById("res-category");
  const eqCat     = document.getElementById("eq-category-id");

  filterCat.innerHTML = `<option value="">Všechny kategorie</option>` +
    state.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");

  resCat.innerHTML = `<option value="">— Vyberte kategorii —</option>` +
    state.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");

  eqCat.innerHTML = state.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
}

// ── 8. RESERVATION FORM ───────────────────────────────────────
function setupReservationForm() {
  const resCat     = document.getElementById("res-category");
  const resItem    = document.getElementById("res-item");
  const itemDetail = document.getElementById("res-item-details");
  const form       = document.getElementById("reservation-form");

  // Default date: tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  document.getElementById("res-date").value = tomorrow.toISOString().split("T")[0];

  resCat.addEventListener("change", () => {
    const catId = resCat.value;
    state.selectedCategory = state.categories.find(c => c.id == catId) || null;
    itemDetail.classList.add("hidden");

    if (!catId) {
      resItem.innerHTML = `<option value="">— Nejprve zvolte kategorii —</option>`;
      resItem.disabled = true;
      updateReservationPrice();
      return;
    }

    const available = state.equipment.filter(i => i.category_id == catId && i.status === "AVAILABLE" && !i.is_deleted);
    if (available.length === 0) {
      resItem.innerHTML = `<option value="">V této kategorii není volný žádný kus</option>`;
      resItem.disabled = true;
    } else {
      resItem.innerHTML = `<option value="">— Vyberte konkrétní kus —</option>` +
        available.map(i => `<option value="${i.id}">${i.inventory_number} – ${i.size} (${i.condition_state})</option>`).join("");
      resItem.disabled = false;
    }
    updatePriceLabels();
    updateReservationPrice();
  });

  resItem.addEventListener("change", () => {
    state.selectedItem = state.equipment.find(i => i.id == resItem.value) || null;
    if (state.selectedItem) {
      document.getElementById("prev-inv").textContent  = state.selectedItem.inventory_number;
      document.getElementById("prev-size").textContent = `Velikost: ${state.selectedItem.size}`;
      document.getElementById("prev-desc").textContent = `Stav: ${state.selectedItem.condition_state} (${state.selectedItem.purchase_year})`;
      itemDetail.classList.remove("hidden");
    } else {
      itemDetail.classList.add("hidden");
    }
    updateReservationPrice();
  });

  document.querySelectorAll("input[name='rental-block']").forEach(r => {
    r.addEventListener("change", updateReservationPrice);
  });

  form.addEventListener("submit", async e => {
    e.preventDefault();

    if (!state.selectedItem) {
      showToast("Vyberte prosím konkrétní kus vybavení.", "error");
      return;
    }

    const customerName  = document.getElementById("cust-name").value.trim();
    const customerPhone = document.getElementById("cust-phone").value.trim();
    const selectedBlock = document.querySelector("input[name='rental-block']:checked")?.value || "FULLDAY";
    const date          = document.getElementById("res-date").value;
    const finalPrice    = calculatePrice(selectedBlock);
    const note          = document.getElementById("res-note")?.value?.trim() || null;

    const blockLabels = {
      HALFDAY_MORNING:   "Půlden dopoledne (08:00–13:00)",
      HALFDAY_AFTERNOON: "Půlden odpoledne (13:00–18:00)",
      FULLDAY:           "Celý kalendářní den",
      WEEKEND:           "Víkendový balíček (2 dny)",
    };

    try {
      const headers = { "Content-Type": "application/json" };
      if (state.token) {
        headers["Authorization"] = `Bearer ${state.token}`;
      }

      const resp = await fetch(`/api/v1/equipment/${state.selectedItem.id}/reserve`, {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          customer_name: customerName,
          customer_phone: customerPhone,
          start_date: date,
          rental_block: blockLabels[selectedBlock] || selectedBlock,
          note: note
        }),
      });

      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData.detail || `Chyba serveru (${resp.status})`);
      }

      const updated = await resp.json();
      const resCode = updated.reservation_code || "REZ-POTVRZENO";

      showToast(`Rezervace ${resCode} pro ${customerName} potvrzena!`, "success");
      alert(
        `REZERVACE POTVRZENA\n\n` +
        `ČÍSLO REZERVACE PRO ZÁKAZNÍKA: ${resCode}\n` +
        `Zákazník: ${customerName} (${customerPhone})\n` +
        `Vybavení: ${state.selectedItem.inventory_number} (${state.selectedItem.size})\n` +
        `Termín: ${date} – ${blockLabels[selectedBlock]}\n` +
        `Cena: ${finalPrice} Kč + kauce 1 000 Kč (hotovost)\n\n` +
        `Při ranním vyzvednutí zákazník nahlásí číslo rezervace: ${resCode}`
      );

      form.reset();
      itemDetail.classList.add("hidden");
      resItem.disabled = true;
      resItem.innerHTML = `<option value="">— Nejprve zvolte kategorii —</option>`;
      state.selectedCategory = null;
      state.selectedItem = null;
      updateReservationPrice();
      await loadEquipment();
    } catch (err) {
      showToast(err.message || "Chyba při odesílání rezervace.", "error");
    }
  });
}

function updatePriceLabels() {
  if (!state.selectedCategory) return;
  document.getElementById("price-halfday-m").textContent = `${state.selectedCategory.halfday_price} Kč`;
  document.getElementById("price-halfday-a").textContent = `${state.selectedCategory.halfday_price} Kč`;
  document.getElementById("price-fullday").textContent   = `${state.selectedCategory.daily_price} Kč`;
  document.getElementById("price-weekend").textContent   = `${state.selectedCategory.weekend_price} Kč`;
}

function calculatePrice(block) {
  if (!state.selectedCategory) return 0;
  if (block.startsWith("HALFDAY")) return state.selectedCategory.halfday_price;
  if (block === "FULLDAY") return state.selectedCategory.daily_price;
  if (block === "WEEKEND") return state.selectedCategory.weekend_price;
  return 0;
}

function updateReservationPrice() {
  const block = document.querySelector("input[name='rental-block']:checked")?.value || "FULLDAY";
  const price = calculatePrice(block);

  const priceEl  = document.getElementById("summary-price");
  const invEl    = document.getElementById("summary-inv");
  const tariffEl = document.getElementById("summary-tariff-label");

  if (priceEl)  priceEl.textContent = `${price} Kč`;
  if (invEl)    invEl.textContent   = state.selectedItem ? `${state.selectedItem.inventory_number} (${state.selectedItem.size})` : "—";

  const blockLabels = {
    HALFDAY_MORNING:   "Půlden dopol. (08–13h)",
    HALFDAY_AFTERNOON: "Půlden odpol. (13–18h)",
    FULLDAY:           "Celý den",
    WEEKEND:           "Víkend (2 dny)",
  };
  if (tariffEl) tariffEl.textContent = blockLabels[block] || block;
}

// ── 8B. ACTIVE RESERVATIONS TABLE ─────────────────────────────
function renderActiveReservationsTable() {
  const card = document.getElementById("card-active-reservations");
  const tbody = document.getElementById("active-reservations-tbody");
  const countBadge = document.getElementById("active-reservations-count");
  if (!card) return;

  const isStaffOrAdmin = state.token && state.user && (state.user.role === "STAFF" || state.user.role === "ADMIN");
  if (!isStaffOrAdmin) {
    card.classList.add("hidden");
    return;
  }
  card.classList.remove("hidden");
  if (!tbody) return;

  const reserved = state.equipment.filter(i => i.status === "RESERVED" && !i.is_deleted);
  if (countBadge) {
    const n = reserved.length;
    countBadge.textContent = `${n} ${n === 1 ? 'rezervace' : (n >= 2 && n <= 4 ? 'rezervace' : 'rezervací')}`;
  }

  if (reserved.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center py-6 text-muted">Aktuálně neevidujeme žádné čekající rezervace. Všechno rezervované vybavení bylo vyzvednuto nebo uvolněno.</td></tr>`;
    return;
  }

  tbody.innerHTML = reserved.map(item => {
    const cat = state.categories.find(c => c.id === item.category_id) || item.category;
    const catName = cat ? cat.name : "Vybavení";
    const resCode = item.reservation_code || `REZ-${item.id}`;
    const custInfo = item.reservation_customer || "Nespecifikovaný zákazník";
    const note = item.reservation_note || "—";

    const actionsHtml = state.token
      ? `<div class="row-actions">
           <button class="btn btn-xs btn-primary btn-action" data-action="issue-reserved" data-id="${item.id}" title="Zákazník ${escapeHtml(custInfo)} si přišel kus vyzvednout – označit jako PŮJČENÝ">Vydat (půjčit)</button>
           <button class="btn btn-xs btn-ghost btn-action" data-action="cancel-reservation" data-id="${item.id}" title="Zrušit rezervaci a vrátit do volného fondu">Zrušit rez.</button>
         </div>`
      : `<span class="text-muted text-xs">Pouze personál</span>`;

    return `
      <tr>
        <td><span class="res-num">${escapeHtml(resCode)}</span></td>
        <td><strong>${escapeHtml(custInfo)}</strong></td>
        <td><span class="inv-chip">${escapeHtml(item.inventory_number)}</span> <strong>${escapeHtml(catName)}</strong> (${escapeHtml(item.size)})</td>
        <td><span class="text-sm">${escapeHtml(note)}</span></td>
        <td class="text-right">${actionsHtml}</td>
      </tr>
    `;
  }).join("");

  attachRowActionListeners();
}

// ── 9. EQUIPMENT MANAGEMENT ───────────────────────────────────
function setupEquipmentManagement() {
  const btnOpen  = document.getElementById("btn-open-add-equipment");
  const form     = document.getElementById("form-add-equipment");
  const errorBox = document.getElementById("add-equipment-error");

  btnOpen.addEventListener("click", () => {
    if (!state.token) {
      showToast("Pro evidenci nového inventáře se přihlaste.", "error");
      openModal("modal-login");
      return;
    }
    errorBox.classList.add("hidden");
    form.reset();
    openModal("modal-add-equipment");
  });

  form.addEventListener("submit", async e => {
    e.preventDefault();
    errorBox.classList.add("hidden");

    const payload = {
      inventory_number: document.getElementById("eq-inv-number").value.trim(),
      category_id:      parseInt(document.getElementById("eq-category-id").value),
      size:             document.getElementById("eq-size").value.trim(),
      purchase_year:    parseInt(document.getElementById("eq-year").value),
      condition_state:  document.getElementById("eq-condition").value.trim(),
      status:           document.getElementById("eq-status").value,
    };

    try {
      const resp = await fetch("/api/v1/equipment/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${state.token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Chyba při ukládání vybavení");
      }

      closeAllModals();
      showToast(`Kus ${payload.inventory_number} zaevidován!`, "success");
      await loadEquipment();
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.classList.remove("hidden");
    }
  });
}

// ── 10. CATEGORY MANAGEMENT ───────────────────────────────────
function setupCategoryManagement() {
  const btnOpen  = document.getElementById("btn-open-add-category");
  const form     = document.getElementById("form-add-category");
  const errorBox = document.getElementById("add-category-error");

  btnOpen.addEventListener("click", () => {
    if (!state.token) {
      showToast("Pro přidání kategorie se přihlaste.", "error");
      openModal("modal-login");
      return;
    }
    errorBox.classList.add("hidden");
    form.reset();
    openModal("modal-add-category");
  });

  form.addEventListener("submit", async e => {
    e.preventDefault();
    errorBox.classList.add("hidden");

    const payload = {
      name:          document.getElementById("cat-name").value.trim(),
      description:   document.getElementById("cat-desc").value.trim() || null,
      halfday_price: parseFloat(document.getElementById("cat-price-half").value),
      daily_price:   parseFloat(document.getElementById("cat-price-day").value),
      weekend_price: parseFloat(document.getElementById("cat-price-week").value),
    };

    try {
      const resp = await fetch("/api/v1/categories/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${state.token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Chyba při ukládání kategorie");
      }

      closeAllModals();
      showToast(`Kategorie "${payload.name}" přidána!`, "success");
      await loadCategories();
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.classList.remove("hidden");
    }
  });
}

function renderCategoriesCards() {
  const container = document.getElementById("categories-cards-container");
  if (!container) return;

  if (state.categories.length === 0) {
    container.innerHTML = `<p class="text-muted" style="padding:2rem;">Žádné kategorie nejsou evidovány.</p>`;
    return;
  }

  container.innerHTML = state.categories.map(cat => `
    <div class="cat-card">
      <div class="cat-name">${escapeHtml(cat.name)}</div>
      <div class="cat-desc">${escapeHtml(cat.description || "Bez podrobnějšího popisu.")}</div>
      <div class="pricing-row">
        <div class="price-cell">
          <span class="price-cell-label">Půlden</span>
          <span class="price-cell-value">${cat.halfday_price} Kč</span>
        </div>
        <div class="price-cell">
          <span class="price-cell-label">Celý den</span>
          <span class="price-cell-value">${cat.daily_price} Kč</span>
        </div>
        <div class="price-cell">
          <span class="price-cell-label">Víkend</span>
          <span class="price-cell-value" style="color:var(--brand-darker)">${cat.weekend_price} Kč</span>
        </div>
      </div>
    </div>
  `).join("");
}

// ── 11. CONDITION MODAL ───────────────────────────────────────
function openConditionModal(itemId) {
  if (!state.token) {
    showToast("Pro úpravu stavu opotřebení se přihlaste.", "error");
    openModal("modal-login");
    return;
  }

  const item = state.equipment.find(i => i.id == itemId);
  if (!item) return;

  const cat     = state.categories.find(c => c.id === item.category_id) || item.category;
  const catName = cat ? cat.name : "Kategorie";

  document.getElementById("edit-condition-item-id").value = item.id;
  document.getElementById("edit-condition-inv-display").textContent = `${item.inventory_number} · ${catName} (${item.size})`;

  const selectEl   = document.getElementById("edit-condition-select");
  const customGrp  = document.getElementById("edit-condition-custom-group");
  const customInp  = document.getElementById("edit-condition-custom");
  const statusSync = document.getElementById("edit-condition-status-sync");
  const errorBox   = document.getElementById("update-condition-error");

  errorBox.classList.add("hidden");
  statusSync.value = "NO_CHANGE";

  let matched = false;
  for (let i = 0; i < selectEl.options.length; i++) {
    if (selectEl.options[i].value === item.condition_state) {
      selectEl.selectedIndex = i;
      matched = true;
      break;
    }
  }

  if (!matched) {
    selectEl.value = "custom";
    customGrp.classList.remove("hidden");
    customInp.value = item.condition_state || "";
  } else {
    customGrp.classList.add("hidden");
    customInp.value = "";
  }

  openModal("modal-update-condition");
}

function setupConditionManagement() {
  const form      = document.getElementById("form-update-condition");
  const selectEl  = document.getElementById("edit-condition-select");
  const customGrp = document.getElementById("edit-condition-custom-group");
  const customInp = document.getElementById("edit-condition-custom");
  const errorBox  = document.getElementById("update-condition-error");

  selectEl.addEventListener("change", () => {
    if (selectEl.value === "custom") {
      customGrp.classList.remove("hidden");
      customInp.required = true;
      customInp.focus();
    } else {
      customGrp.classList.add("hidden");
      customInp.required = false;
    }
  });

  form.addEventListener("submit", async e => {
    e.preventDefault();
    errorBox.classList.add("hidden");

    const itemId     = document.getElementById("edit-condition-item-id").value;
    const condVal    = selectEl.value === "custom" ? customInp.value.trim() : selectEl.value;
    const statusSync = document.getElementById("edit-condition-status-sync").value;

    if (!condVal) {
      errorBox.textContent = "Zadejte platný stav opotřebení.";
      errorBox.classList.remove("hidden");
      return;
    }

    const payload = { condition_state: condVal };
    if (statusSync && statusSync !== "NO_CHANGE") payload.status = statusSync;

    try {
      const resp = await fetch(`/api/v1/equipment/${itemId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${state.token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Chyba při aktualizaci stavu opotřebení.");
      }

      const updated = await resp.json();
      closeAllModals();
      showToast(`Stav opotřebení pro ${updated.inventory_number} upraven.`, "success");
      await loadEquipment();
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.classList.remove("hidden");
    }
  });
}

// ── 12. TOASTS ────────────────────────────────────────────────
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast     = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const icons = { success: "✓", error: "✗", info: "i" };
  const iconEl = document.createElement("span");
  iconEl.textContent = icons[type] || "i";
  iconEl.style.cssText = "font-weight:800;font-size:.8rem;flex-shrink:0;";

  const msgEl = document.createElement("span");
  msgEl.textContent = message;

  toast.appendChild(iconEl);
  toast.appendChild(msgEl);
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = "opacity .3s, transform .3s";
    toast.style.opacity = "0";
    toast.style.transform = "translateX(16px)";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ── UTILS ─────────────────────────────────────────────────────
function escapeHtml(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
