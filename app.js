(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const key = "cipa_payroll_employees_v1";
  const labels = {
    salaried: "Asalariado",
    hourly: "Por horas",
    commission: "Por comisión",
    temporary: "Temporal",
  };
  let employees = [],
    kind = "salaried";
  // Registros ficticios para la primera demostración. Solo se insertan si el navegador no tiene empleados.
  const demoEmployees = [
    {
      id: "ACT-20261030-01",
      name: "Ana Pérez",
      role: "Analista administrativa",
      startDate: "2023-04-10",
      kind: "salaried",
      salary: 2500000,
      years: 7,
    },
    {
      id: "ACT-20261030-02",
      name: "Carlos Díaz",
      role: "Auxiliar de operaciones",
      startDate: "2024-06-03",
      kind: "hourly",
      rate: 15000,
      hours: 45,
      years: 2,
      savings: true,
    },
    {
      id: "ACT-20261031-01",
      name: "María Ruiz",
      role: "Ejecutiva comercial",
      startDate: "2025-01-15",
      kind: "commission",
      base: 1500000,
      percent: 5,
      sales: 22000000,
    },
    {
      id: "ACT-20261101-01",
      name: "Juan López",
      role: "Apoyo temporal de archivo",
      startDate: "2026-03-02",
      kind: "temporary",
      salary: 1800000,
      months: 4,
    },
    {
      id: "ACT-20261030-03",
      name: "Laura Mendoza",
      role: "Coordinadora de talento humano",
      startDate: "2022-02-14",
      kind: "salaried",
      salary: 3200000,
      years: 8,
    },
    {
      id: "ACT-20261030-04",
      name: "Andrés Torres",
      role: "Asistente contable",
      startDate: "2023-08-21",
      kind: "salaried",
      salary: 2300000,
      years: 3,
    },
    {
      id: "ACT-20261030-05",
      name: "Sofía Herrera",
      role: "Supervisora de operaciones",
      startDate: "2021-11-08",
      kind: "salaried",
      salary: 3500000,
      years: 9,
    },
    {
      id: "ACT-20261030-06",
      name: "Diego Castro",
      role: "Auxiliar de inventario",
      startDate: "2025-05-12",
      kind: "salaried",
      salary: 1900000,
      years: 1,
    },
    {
      id: "ACT-20261030-07",
      name: "Valentina Rojas",
      role: "Auxiliar de bodega",
      startDate: "2024-02-05",
      kind: "hourly",
      rate: 14000,
      hours: 42,
      years: 2,
      savings: false,
    },
    {
      id: "ACT-20261030-08",
      name: "Mateo Jiménez",
      role: "Técnico de soporte",
      startDate: "2022-09-19",
      kind: "hourly",
      rate: 18000,
      hours: 38,
      years: 4,
      savings: true,
    },
    {
      id: "ACT-20261030-09",
      name: "Camila Navarro",
      role: "Operaria de producción",
      startDate: "2025-07-01",
      kind: "hourly",
      rate: 12500,
      hours: 44,
      years: 1,
      savings: false,
    },
    {
      id: "ACT-20261030-10",
      name: "Sebastián Molina",
      role: "Mensajero",
      startDate: "2023-03-27",
      kind: "hourly",
      rate: 13000,
      hours: 40,
      years: 3,
      savings: true,
    },
    {
      id: "ACT-20261031-02",
      name: "Daniela Vargas",
      role: "Asesora comercial",
      startDate: "2022-06-13",
      kind: "commission",
      base: 1700000,
      percent: 4,
      sales: 18500000,
    },
    {
      id: "ACT-20261031-03",
      name: "Felipe Salas",
      role: "Ejecutivo de ventas",
      startDate: "2023-10-02",
      kind: "commission",
      base: 1600000,
      percent: 6,
      sales: 26000000,
    },
    {
      id: "ACT-20261031-04",
      name: "Natalia Pineda",
      role: "Asesora de cuentas",
      startDate: "2024-04-16",
      kind: "commission",
      base: 1450000,
      percent: 5,
      sales: 12000000,
    },
    {
      id: "ACT-20261031-05",
      name: "Samuel Ortega",
      role: "Representante comercial",
      startDate: "2025-02-10",
      kind: "commission",
      base: 1550000,
      percent: 3.5,
      sales: 21500000,
    },
    {
      id: "ACT-20261101-02",
      name: "Isabella Fuentes",
      role: "Auxiliar de archivo temporal",
      startDate: "2026-01-12",
      kind: "temporary",
      salary: 1750000,
      months: 3,
    },
    {
      id: "ACT-20261101-03",
      name: "Tomás Cabrera",
      role: "Apoyo logístico temporal",
      startDate: "2025-12-01",
      kind: "temporary",
      salary: 1850000,
      months: 6,
    },
    {
      id: "ACT-20261101-04",
      name: "Gabriela Acosta",
      role: "Digitadora temporal",
      startDate: "2026-04-06",
      kind: "temporary",
      salary: 1650000,
      months: 2,
    },
    {
      id: "ACT-20261101-05",
      name: "Nicolás Peña",
      role: "Asistente de proyecto temporal",
      startDate: "2026-02-16",
      kind: "temporary",
      salary: 1950000,
      months: 5,
    },
  ];
  try {
    const saved = localStorage.getItem(key);
    if (saved === null) {
      // Los datos de ejemplo se cargan una sola vez, en la primera visita.
      employees = demoEmployees.map((e) => ({ ...e }));
      localStorage.setItem(key, JSON.stringify(employees));
    } else {
      // Respetar la lista guardada, incluso si el usuario eliminó ejemplos o dejó la lista vacía.
      const raw = JSON.parse(saved);
      employees = Array.isArray(raw) ? raw : [];
    }
  } catch {
    // Si el almacenamiento está dañado, no reinsertar registros de ejemplo silenciosamente.
    employees = [];
  }
  const money = (n) =>
    new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(Number(n) || 0);
  const esc = (s) =>
    String(s ?? "").replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  function toast(msg) {
    const t = $("toast");
    if (!t) {
      alert(msg);
      return;
    }
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => t.classList.remove("show"), 3000);
  }
  function persist() {
    localStorage.setItem(key, JSON.stringify(employees));
  }
  function gross(e) {
    if (e.kind === "salaried")
      return Number(e.salary) * (Number(e.years) > 5 ? 1.1 : 1);
    if (e.kind === "hourly")
      return (
        Number(e.rate) * Math.min(Number(e.hours), 40) +
        Number(e.rate) * 1.5 * Math.max(0, Number(e.hours) - 40)
      );
    if (e.kind === "commission")
      return (
        Number(e.base) +
        Number(e.sales) * (Number(e.percent) / 100) +
        (Number(e.sales) > 20000000 ? Number(e.sales) * 0.03 : 0)
      );
    return Number(e.salary);
  }
  function calc(e) {
    const g = gross(e),
      ss = g * 0.04,
      arl = g * 0.00522,
      saving =
        e.kind === "hourly" && Number(e.years) > 1 && e.savings ? g * 0.02 : 0,
      net = g - ss - arl - saving;
    if (
      ![g, ss, arl, saving, net].every(Number.isFinite) ||
      g < 0 ||
      ss < 0 ||
      arl < 0 ||
      saving < 0 ||
      net < 0
    )
      throw Error(
        "La nómina contiene valores inválidos o un salario neto negativo. Revisa los datos del empleado.",
      );
    return {
      gross: g,
      deductions: ss + arl + saving,
      net,
      food: ["salaried", "commission"].includes(e.kind) ? 1000000 : 0,
    };
  }
  function totals() {
    return employees.reduce(
      (a, e) => {
        const c = calc(e);
        a.g += c.gross;
        a.d += c.deductions;
        a.n += c.net;
        return a;
      },
      { g: 0, d: 0, n: 0 },
    );
  }
  function renderStats() {
    const t = totals();
    if ($("count")) $("count").textContent = employees.length;
    if ($("grossTotal")) $("grossTotal").textContent = money(t.g);
    if ($("deductionsTotal")) $("deductionsTotal").textContent = money(t.d);
    if ($("netTotal")) $("netTotal").textContent = money(t.n);
  }
  function renderTable() {
    const body = $("employeeRows");
    if (!body) return;
    const q = ($("search")?.value || "").toLowerCase(),
      f = $("filter")?.value || "";
    const rows = employees
      .filter(
        (e) =>
          (!f || e.kind === f) &&
          [e.name, e.id, e.role].some((v) =>
            String(v || "")
              .toLowerCase()
              .includes(q),
          ),
      )
      .sort(
        (a, b) =>
          String(a.startDate || "").localeCompare(String(b.startDate || "")) ||
          String(a.id).localeCompare(String(b.id)),
      );
    body.innerHTML = rows.length
      ? rows
          .map((e) => {
            const c = calc(e);
            return (
              '<tr><td><div class="name-cell">' +
              esc(e.name) +
              '</div><div class="muted-cell">ID: ' +
              esc(e.id) +
              '</div><div class="muted-cell">' +
              esc(e.role) +
              '</div><div class="muted-cell">Ingreso: ' +
              esc(e.startDate || "Sin fecha") +
              '</div></td><td><span class="pill ' +
              esc(e.kind) +
              '">' +
              labels[e.kind] +
              "</span></td><td>" +
              money(c.gross) +
              "</td><td><b>" +
              money(c.net) +
              '</b></td><td><span class="status">Activo</span></td><td><button class="icon-btn" title="Editar" data-edit="' +
              esc(e.id) +
              '">✎</button><button class="icon-btn delete" title="Eliminar" data-delete="' +
              esc(e.id) +
              '">⌫</button></td></tr>'
            );
          })
          .join("")
      : '<tr><td colspan="6"><div class="empty"><strong>' +
        (employees.length ? "No hay resultados" : "Todavía no hay empleados") +
        "</strong><p>" +
        (employees.length
          ? "Prueba otra búsqueda o filtro."
          : "Registra el primer empleado para comenzar.") +
        '</p><p><a href="empleados.html">Ir a registrar empleado</a></p></div></td></tr>';
    if ($("tableCount"))
      $("tableCount").textContent =
        rows.length + " de " + employees.length + " empleado(s)";
    renderStats();
  }
  function fieldsMarkup() {
    const box = $("dynamicFields");
    if (!box) return;
    let h = "";
    if (kind === "salaried")
      h =
        '<div class="form-grid"><div class="field"><label>Salario mensual bruto (COP) <span class="required">*</span></label><input id="salary" type="number" min="0" step="any" required placeholder="2500000"></div><div class="field"><label>Antigüedad (años) <span class="required">*</span></label><input id="years" type="number" min="0" step="1" required placeholder="0"></div></div>';
    if (kind === "hourly")
      h =
        '<div class="form-grid"><div class="field"><label>Tarifa por hora (COP) *</label><input id="rate" type="number" min="0" required step="any"></div><div class="field"><label>Horas trabajadas *</label><input id="hours" type="number" min="0" required step="any"></div><div class="field"><label>Antigüedad (años) *</label><input id="years" type="number" min="0" step="1" required></div><label class="checkline span-2"><input id="savings" type="checkbox"> Acepta aporte al fondo de ahorro (2%)</label></div>';
    if (kind === "commission")
      h =
        '<div class="form-grid"><div class="field"><label>Salario base (COP) *</label><input id="base" type="number" min="0" step="any" required></div><div class="field"><label>Comisión (%) *</label><input id="percent" type="number" min="0" max="100" step="any" required></div><div class="field span-2"><label>Ventas del periodo (COP) *</label><input id="sales" type="number" min="0" step="any" required></div></div>';
    if (kind === "temporary")
      h =
        '<div class="form-grid"><div class="field"><label>Salario mensual bruto (COP) *</label><input id="salary" type="number" min="0" step="any" required></div><div class="field"><label>Duración del contrato (meses) *</label><input id="months" type="number" min="1" step="1" required></div></div>';
    box.innerHTML = h;
  }
  function setKind(k) {
    kind = k;
    document
      .querySelectorAll("[data-kind]")
      .forEach((b) => b.classList.toggle("active", b.dataset.kind === k));
    fieldsMarkup();
  }
  function clearForm() {
    const f = $("employeeForm");
    if (!f) return;
    f.reset();
    $("recordId").value = "";
    $("startDate").value = new Date().toISOString().slice(0, 10);
    $("saveBtn").textContent = "Guardar empleado";
    setKind("salaried");
  }
  function readNum(id) {
    const el = $(id),
      v = Number(el?.value);
    if (!el || el.value.trim() === "" || !Number.isFinite(v) || v < 0)
      throw Error(
        "Completa los campos numéricos obligatorios con valores válidos.",
      );
    return v;
  }
  function readForm() {
    const e = {
      id: $("idNumber").value.trim(),
      name: $("name").value.trim(),
      role: $("role").value.trim(),
      startDate: $("startDate").value,
      kind,
    };
    if (!e.id || !e.name || !e.role || !e.startDate)
      throw Error("Completa nombre, identificación, cargo y fecha de ingreso.");
    const existing = employees.find((x) => x.id === e.id);
    if (existing && $("recordId").value !== e.id)
      throw Error("Ya existe un empleado con esa identificación.");
    if (kind === "salaried") {
      e.salary = readNum("salary");
      e.years = readNum("years");
    }
    if (kind === "hourly") {
      e.rate = readNum("rate");
      e.hours = readNum("hours");
      e.years = readNum("years");
      e.savings = $("savings").checked;
    }
    if (kind === "commission") {
      e.base = readNum("base");
      e.percent = readNum("percent");
      e.sales = readNum("sales");
      if (e.percent > 100)
        throw Error("La comisión debe estar entre 0 y 100%.");
    }
    if (kind === "temporary") {
      e.salary = readNum("salary");
      e.months = readNum("months");
      if (!Number.isInteger(e.months) || e.months < 1)
        throw Error("La duración debe ser un número entero mayor que cero.");
    }
    if (["salaried", "hourly"].includes(kind) && !Number.isInteger(e.years))
      throw Error("La antigüedad debe ser un número entero.");
    return e;
  }
  function editEmployee(id) {
    const e = employees.find((x) => x.id === id);
    if (!e) return;
    location.href = "empleados.html?edit=" + encodeURIComponent(id);
  }
  function deleteEmployee(id) {
    const e = employees.find((x) => x.id === id);
    if (!e) return;
    if (
      confirm("¿Eliminar a " + e.name + "? Esta acción no se puede deshacer.")
    ) {
      employees = employees.filter((x) => x.id !== id);
      persist();
      renderTable();
      renderStats();
      toast("Empleado eliminado.");
    }
  }
  function exportCSV() {
    if (!employees.length) {
      toast("No hay empleados para exportar.");
      return;
    }
    const rows = [
      [
        "Identificación",
        "Nombre",
        "Cargo",
        "Tipo de pago",
        "Fecha ingreso",
        "Bruto estimado",
        "Deducciones estimadas",
        "Neto estimado",
      ],
      ...employees.map((e) => {
        const c = calc(e);
        return [
          e.id,
          e.name,
          e.role,
          labels[e.kind],
          e.startDate,
          c.gross.toFixed(2),
          c.deductions.toFixed(2),
          c.net.toFixed(2),
        ];
      }),
    ];
    const csv =
      "\ufeff" +
      rows
        .map((r) =>
          r.map((v) => '"' + String(v).replace(/"/g, '""') + '"').join(";"),
        )
        .join("\r\n");
    const url = URL.createObjectURL(
      new Blob([csv], { type: "text/csv;charset=utf-8;" }),
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = "nomina_cipa.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
    toast("Archivo CSV generado.");
  }

  function renderCharts() {
    const bar = $("payrollChart"),
      donut = $("typeChart");
    if (!bar || !donut) return;
    if (!employees.length) {
      bar.innerHTML =
        '<div class="chart-empty"><strong>No hay datos para graficar</strong><span>Registra empleados para comparar bruto y neto.</span></div>';
      donut.innerHTML =
        '<div class="chart-empty"><strong>Plantilla vacía</strong><span>La distribución aparecerá al registrar empleados.</span></div>';
      return;
    }
    const list = employees
      .slice()
      .sort((a, b) => gross(b) - gross(a))
      .slice(0, 8);
    const W = 640,
      H = 245,
      L = 66,
      R = 14,
      T = 18,
      B = 42,
      plotW = W - L - R,
      plotH = H - T - B;
    const max = Math.max(1, ...list.map((e) => calc(e).gross)) * 1.12;
    const fmtAxis = (n) =>
      n >= 1000000
        ? (n / 1000000).toLocaleString("es-CO", { maximumFractionDigits: 1 }) +
          " M"
        : n >= 1000
          ? Math.round(n / 1000) + " mil"
          : String(Math.round(n));
    let svg =
      '<svg viewBox="0 0 ' +
      W +
      " " +
      H +
      '" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">';
    for (let i = 0; i <= 4; i++) {
      const y = T + (plotH * i) / 4,
        val = max * (1 - i / 4);
      svg +=
        '<line class="chart-gridline" x1="' +
        L +
        '" y1="' +
        y +
        '" x2="' +
        (W - R) +
        '" y2="' +
        y +
        '"/><text class="chart-axis" x="' +
        (L - 8) +
        '" y="' +
        (y + 3) +
        '" text-anchor="end">' +
        fmtAxis(val) +
        "</text>";
    }
    const groupW = plotW / list.length,
      barW = Math.min(17, groupW * 0.27);
    list.forEach((e, i) => {
      const c = calc(e),
        x = L + groupW * i + groupW / 2,
        h1 = (c.gross / max) * plotH,
        h2 = (c.net / max) * plotH;
      svg +=
        '<rect x="' +
        (x - barW - 2) +
        '" y="' +
        (T + plotH - h1) +
        '" width="' +
        barW +
        '" height="' +
        h1 +
        '" rx="2" fill="#a55338"><title>' +
        esc(e.name) +
        " — bruto " +
        money(c.gross) +
        "</title></rect>";
      svg +=
        '<rect x="' +
        (x + 2) +
        '" y="' +
        (T + plotH - h2) +
        '" width="' +
        barW +
        '" height="' +
        h2 +
        '" rx="2" fill="#829781"><title>' +
        esc(e.name) +
        " — neto " +
        money(c.net) +
        "</title></rect>";
      let label = String(e.name || "Empleado");
      if (label.length > 11) label = label.slice(0, 10) + "…";
      svg +=
        '<text class="chart-axis" x="' +
        x +
        '" y="' +
        (H - 19) +
        '" text-anchor="middle">' +
        esc(label) +
        "</text>";
    });
    svg += "</svg>";
    bar.innerHTML = svg;
    const types = [
      ["salaried", "Asalariado", "#a55338"],
      ["hourly", "Por horas", "#829781"],
      ["commission", "Comisión", "#c4a66a"],
      ["temporary", "Temporal", "#aaa69b"],
    ];
    const counts = types
      .map((t) => ({
        ...{ key: t[0], label: t[1], color: t[2] },
        count: employees.filter((e) => e.kind === t[0]).length,
      }))
      .filter((t) => t.count > 0);
    const total = employees.length,
      cx = 100,
      cy = 100,
      r = 68,
      circ = 2 * Math.PI * r;
    let offset = 0;
    let rings =
      '<svg viewBox="0 0 200 200" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><circle cx="' +
      cx +
      '" cy="' +
      cy +
      '" r="' +
      r +
      '" fill="none" stroke="#eeeae0" stroke-width="18"/>';
    counts.forEach((t) => {
      const len = (circ * t.count) / total;
      rings +=
        '<circle cx="' +
        cx +
        '" cy="' +
        cy +
        '" r="' +
        r +
        '" fill="none" stroke="' +
        t.color +
        '" stroke-width="18" stroke-dasharray="' +
        len +
        " " +
        (circ - len) +
        '" stroke-dashoffset="' +
        -offset +
        '" transform="rotate(-90 100 100)"><title>' +
        t.label +
        ": " +
        t.count +
        "</title></circle>";
      offset += len;
    });
    rings +=
      '<text class="donut-total" x="100" y="97" text-anchor="middle">' +
      total +
      '</text><text class="donut-caption" x="100" y="113" text-anchor="middle">empleados</text></svg>';
    rings +=
      '<div class="donut-key">' +
      types
        .map((t) => {
          const n = employees.filter((e) => e.kind === t[0]).length;
          return (
            '<div class="donut-key-row"><i style="background:' +
            t[2] +
            '"></i><span>' +
            t[1] +
            "</span><b>" +
            n +
            "</b></div>"
          );
        })
        .join("") +
      "</div>";
    donut.innerHTML = rings;
  }
  function renderReport() {
    const body = $("reportRows");
    if (!body) return;
    if (!employees.length) {
      body.innerHTML =
        '<div class="empty"><strong>No hay empleados registrados</strong><p>Primero agrega empleados para calcular la nómina.</p><a href="empleados.html">Registrar empleado</a></div>';
      return;
    }
    body.innerHTML = employees
      .map((e) => {
        const c = calc(e);
        return (
          '<div class="report-row"><span><b>' +
          esc(e.name) +
          "</b><br><small>" +
          labels[e.kind] +
          " · ID " +
          esc(e.id) +
          '</small></span><span style="text-align:right">Bruto: ' +
          money(c.gross) +
          "<br>Deducciones: " +
          money(c.deductions) +
          "<br><b>Neto: " +
          money(c.net) +
          "</b></span></div>"
        );
      })
      .join("");
    const t = totals();
    if ($("reportTotals"))
      $("reportTotals").innerHTML =
        '<div class="report-row"><span>Total bruto</span><b>' +
        money(t.g) +
        '</b></div><div class="report-row"><span>Total deducciones estimadas</span><b>' +
        money(t.d) +
        '</b></div><div class="report-row total"><span>Total neto estimado</span><b>' +
        money(t.n) +
        "</b></div>";
  }
  document
    .querySelectorAll("[data-kind]")
    .forEach((b) => b.addEventListener("click", () => setKind(b.dataset.kind)));
  if ($("employeeForm")) {
    $("startDate").value = new Date().toISOString().slice(0, 10);
    setKind("salaried");
    const params = new URLSearchParams(location.search),
      id = params.get("edit");
    if (id) {
      const e = employees.find((x) => x.id === id);
      if (e) {
        $("recordId").value = e.id;
        setKind(e.kind);
        for (const [field, val] of Object.entries({
          name: e.name,
          idNumber: e.id,
          role: e.role,
          startDate: e.startDate,
        }))
          $(field).value = val || "";
        for (const field of [
          "salary",
          "years",
          "rate",
          "hours",
          "savings",
          "base",
          "percent",
          "sales",
          "months",
        ]) {
          const el = $(field);
          if (el && e[field] !== undefined) {
            if (el.type === "checkbox") el.checked = !!e[field];
            else el.value = e[field];
          }
        }
        $("saveBtn").textContent = "Guardar cambios";
        $("formTitle").textContent = "Editar empleado";
      }
    }
    $("employeeForm").addEventListener("submit", (ev) => {
      ev.preventDefault();
      try {
        const e = readForm(),
          old = $("recordId").value,
          idx = employees.findIndex((x) => x.id === old);
        if (idx >= 0) {
          employees[idx] = e;
          toast("Cambios guardados.");
        } else {
          employees.push(e);
          toast("Empleado registrado correctamente.");
        }
        persist();
        location.href = "empleados.html?guardado=1";
      } catch (err) {
        toast(err.message);
      }
    });
    $("clearForm").addEventListener("click", clearForm);
  }
  $("employeeRows")?.addEventListener("click", (ev) => {
    const a = ev.target.closest("[data-edit]"),
      d = ev.target.closest("[data-delete]");
    if (a) editEmployee(a.dataset.edit);
    if (d) deleteEmployee(d.dataset.delete);
  });
  $("search")?.addEventListener("input", renderTable);
  $("filter")?.addEventListener("change", renderTable);
  $("newEmployee")?.addEventListener(
    "click",
    () => (location.href = "empleados.html"),
  );
  $("export")?.addEventListener("click", exportCSV);
  $("exportReport")?.addEventListener("click", exportCSV);
  $("printReport")?.addEventListener("click", () => window.print());
  $("today") &&
    ($("today").textContent = new Date().toLocaleDateString("es-CO", {
      weekday: "short",
      day: "numeric",
      month: "short",
      year: "numeric",
    }));
  renderStats();
  renderTable();
  renderReport();
  renderCharts();
  if (new URLSearchParams(location.search).has("guardado"))
    toast(
      "Los datos quedaron guardados y están disponibles en las demás páginas.",
    );
  window.addEventListener("error", (ev) =>
    toast("Error de interfaz: " + ev.message),
  );
})();
