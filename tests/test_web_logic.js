"use strict";
// Pruebas de regresión de la lógica real de app.js, sin dependencias externas.
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const source = fs.readFileSync(
  new URL("../app.js", `file://${__filename}`),
  "utf8",
);

function extract(startMarker, endMarker) {
  const start = source.indexOf(startMarker);
  const end = source.indexOf(endMarker, start);
  assert.ok(
    start >= 0 && end > start,
    `No se encontró el bloque ${startMarker}`,
  );
  return source.slice(start, end);
}

// Comprueba que los ejemplos solo se carguen en una primera visita real.
const initialization = extract(
  "try {\n    const saved = localStorage.getItem(key);",
  "\n  const money =",
);
let stored = null;
const initContext = {
  employees: [],
  demoEmployees: [{ id: "demo" }],
  key: "test",
  localStorage: {
    getItem: () => stored,
    setItem: (_key, value) => {
      stored = value;
    },
  },
};
vm.runInNewContext(initialization, initContext);
assert.equal(
  initContext.employees.length,
  1,
  "La primera visita carga los ejemplos",
);
stored = "[]";
initContext.employees = [];
vm.runInNewContext(initialization, initContext);
assert.equal(
  initContext.employees.length,
  0,
  "Una lista vacía guardada no debe repoblarse",
);
console.log("OK: los ejemplos no reaparecen tras eliminarse");

// Ejecuta las funciones de cálculo extraídas directamente del app.js real.
const calculations = extract("function gross(e)", "\n  function totals()");
const calculationContext = {};
vm.runInNewContext(calculations, calculationContext);
const overtime = calculationContext.calc({
  kind: "hourly",
  rate: 10000,
  hours: 41,
  years: 0,
  savings: false,
});
assert.equal(overtime.gross, 415000, "Una hora extra se paga a 1.5x");
console.log("OK: cálculo de hora extra a 1.5x");

assert.throws(
  () => calculationContext.calc({ kind: "salaried", salary: -1000, years: 0 }),
  /salario neto negativo|valores inválidos/i,
  "La nómina debe rechazar datos que generan un neto inválido",
);
assert.throws(
  () =>
    calculationContext.calc({ kind: "salaried", salary: Number.NaN, years: 0 }),
  /salario neto negativo|valores inválidos/i,
  "La nómina debe rechazar datos no finitos",
);
console.log("OK: rechazo de salario neto inválido y datos no finitos");
console.log("Resultado: 4 aserciones web aprobadas.");
