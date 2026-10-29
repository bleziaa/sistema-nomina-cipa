"""Interfaz gráfica para el Sistema de Nómina CIPA."""
import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from decimal import Decimal, InvalidOperation

from payroll.employees import (
    SalariedEmployee, HourlyEmployee, CommissionEmployee, TemporaryEmployee
)
from payroll.payroll_service import PayrollConfig, PayrollService

DATA_FILE = Path(__file__).resolve().parent / "payroll" / "employees_data.json"
TYPES = ("Asalariado", "Por horas", "Por comisión", "Temporal")
TYPE_MAP = {
    "Asalariado": "salaried",
    "Por horas": "hourly",
    "Por comisión": "commission",
    "Temporal": "temporary",
}
MAP_TYPE = {v: k for k, v in TYPE_MAP.items()}


def number(value, label, integer=False):
    raw = value.strip().replace(" ", "")
    if not raw:
        raise ValueError(f"El campo «{label}» es obligatorio.")
    # Acepta decimal con coma o punto; no interpreta separadores de miles.
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    else:
        raw = raw.replace(",", ".")
    try:
        result = Decimal(raw)
    except InvalidOperation:
        raise ValueError(f"«{label}» debe ser un número válido.")
    if not result.is_finite():
        raise ValueError(f"«{label}» debe ser un número válido.")
    if integer:
        if result != result.to_integral_value():
            raise ValueError(f"«{label}» debe ser un número entero.")
        return int(result)
    return result


def cop(value):
    return "$" + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class PayrollApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Nómina CIPA")
        self.geometry("1120x760")
        self.minsize(900, 620)
        self.configure(bg="#f3f5f9")
        self.records = {}
        self.fields = {}
        self.editing_id = None
        self._style()
        self._build()
        self._load_data()
        self._refresh_table()

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f3f5f9")
        style.configure("TLabel", background="#f3f5f9", foreground="#172033", font=("Sans", 10))
        style.configure("Title.TLabel", font=("Sans", 20, "bold"), foreground="#172033")
        style.configure("Sub.TLabel", foreground="#586174")
        style.configure("TButton", padding=(10, 7), font=("Sans", 10))
        style.configure("Primary.TButton", background="#2457d6", foreground="white")
        style.map("Primary.TButton", background=[("active", "#1945b3")])
        style.configure("Treeview", rowheight=29, font=("Sans", 10))
        style.configure("Treeview.Heading", font=("Sans", 10, "bold"))

    def _build(self):
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Sistema de Nómina CIPA", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Registro y edición de empleados · Cálculo de nómina · Datos guardados localmente",
            style="Sub.TLabel"
        ).pack(anchor="w", pady=(3, 14))

        form = ttk.LabelFrame(outer, text="Datos del empleado", padding=12)
        form.pack(fill="x", pady=(0, 12))
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        self._add_field(form, "Identificación *", "employee_id", 0, 0)
        self._add_field(form, "Nombre completo *", "name", 0, 2)
        ttk.Label(form, text="Tipo de pago *").grid(row=1, column=0, sticky="w", padx=5, pady=6)
        self.type_var = tk.StringVar(value=TYPES[0])
        self.type_combo = ttk.Combobox(form, textvariable=self.type_var, values=TYPES, state="readonly", width=25)
        self.type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=6)
        self.type_combo.bind("<<ComboboxSelected>>", lambda _e: self._render_type_fields())

        self.dynamic = ttk.Frame(form)
        self.dynamic.grid(row=2, column=0, columnspan=4, sticky="ew")
        for col in (1, 3):
            self.dynamic.columnconfigure(col, weight=1)
        self._render_type_fields()

        actions = ttk.Frame(form)
        actions.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        ttk.Button(actions, text="Guardar empleado", style="Primary.TButton", command=self._save).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Limpiar / Nuevo", command=self._clear).pack(side="left", padx=6)
        ttk.Button(actions, text="Editar seleccionado", command=self._edit_selected).pack(side="left", padx=6)
        ttk.Button(actions, text="Eliminar seleccionado", command=self._delete_selected).pack(side="left", padx=6)

        list_frame = ttk.LabelFrame(outer, text="Empleados registrados", padding=10)
        list_frame.pack(fill="both", expand=True)
        columns = ("id", "name", "kind", "gross", "net")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        headers = {"id": "Identificación", "name": "Nombre", "kind": "Tipo de pago",
                   "gross": "Bruto estimado", "net": "Neto estimado"}
        widths = {"id": 125, "name": 260, "kind": 145, "gross": 160, "net": 160}
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor="w" if col in ("id", "name", "kind") else "e")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom = ttk.Frame(outer)
        bottom.pack(fill="x", pady=(12, 0))
        ttk.Button(bottom, text="Calcular nómina completa", style="Primary.TButton", command=self._calculate).pack(side="left")
        ttk.Label(bottom, text="* Campos obligatorios. Los cálculos son académicos, no una liquidación legal.",
                  style="Sub.TLabel").pack(side="left", padx=12)

    def _add_field(self, parent, label, key, row, col, container=None):
        target = container or parent
        ttk.Label(target, text=label).grid(row=row, column=col, sticky="w", padx=5, pady=6)
        entry = ttk.Entry(target, width=28)
        entry.grid(row=row, column=col + 1, sticky="ew", padx=5, pady=6)
        self.fields[key] = entry

    def _render_type_fields(self):
        for child in self.dynamic.winfo_children():
            child.destroy()
        for key in list(self.fields):
            if key not in ("employee_id", "name"):
                del self.fields[key]
        kind = self.type_var.get()
        if kind == "Asalariado":
            specs = [("Salario mensual bruto *", "monthly_salary"), ("Antigüedad en años *", "years_of_service")]
        elif kind == "Por horas":
            specs = [("Tarifa por hora *", "hourly_rate"), ("Horas trabajadas *", "hours_worked"),
                     ("Antigüedad en años *", "years_of_service")]
        elif kind == "Por comisión":
            specs = [("Salario base *", "base_salary"), ("Comisión (%) *", "commission_percent"),
                     ("Ventas del periodo *", "sales")]
        else:
            specs = [("Salario mensual bruto *", "monthly_salary"), ("Duración del contrato (meses) *", "contract_months")]
        for i, (label, key) in enumerate(specs):
            row, col = 0, (0 if i % 2 == 0 else 2)
            self._add_field(self.dynamic, label, key, row, col)
        if kind == "Por horas":
            self.savings_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.dynamic, text="Acepta aporte al fondo de ahorro (si cumple antigüedad)",
                            variable=self.savings_var).grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=4)
        else:
            self.savings_var = tk.BooleanVar(value=False)

    def _load_data(self):
        try:
            if DATA_FILE.exists():
                data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                for record in data:
                    self.records[record["employee_id"]] = record
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            messagebox.showerror("Error al cargar datos", f"No se pudo leer el archivo local de empleados.\n{exc}")

    def _persist(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        temp = DATA_FILE.with_suffix(".tmp")
        temp.write_text(json.dumps(list(self.records.values()), ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(DATA_FILE)

    def _employee_from_record(self, record):
        kind = record["kind"]
        common = (record["employee_id"], record["name"])
        if kind == "salaried":
            return SalariedEmployee(*common, record["monthly_salary"], record["years_of_service"])
        if kind == "hourly":
            return HourlyEmployee(*common, record["hourly_rate"], record["hours_worked"],
                                  record["years_of_service"], record.get("accepts_savings_fund", False))
        if kind == "commission":
            return CommissionEmployee(*common, record["base_salary"], record["commission_rate"], record["sales"])
        return TemporaryEmployee(*common, record["monthly_salary"], record["contract_months"])

    def _make_record(self):
        employee_id = self.fields["employee_id"].get().strip()
        name = self.fields["name"].get().strip()
        if not employee_id or not name:
            raise ValueError("La identificación y el nombre son obligatorios.")
        kind = TYPE_MAP[self.type_var.get()]
        record = {"employee_id": employee_id, "name": name, "kind": kind}
        if kind == "salaried":
            record["monthly_salary"] = str(number(self.fields["monthly_salary"].get(), "Salario mensual"))
            record["years_of_service"] = number(self.fields["years_of_service"].get(), "Antigüedad", True)
        elif kind == "hourly":
            record["hourly_rate"] = str(number(self.fields["hourly_rate"].get(), "Tarifa por hora"))
            record["hours_worked"] = str(number(self.fields["hours_worked"].get(), "Horas trabajadas"))
            record["years_of_service"] = number(self.fields["years_of_service"].get(), "Antigüedad", True)
            record["accepts_savings_fund"] = self.savings_var.get()
        elif kind == "commission":
            record["base_salary"] = str(number(self.fields["base_salary"].get(), "Salario base"))
            percent = number(self.fields["commission_percent"].get(), "Comisión (%)")
            if not Decimal(0) <= percent <= Decimal(100):
                raise ValueError("La comisión debe estar entre 0 y 100%.")
            record["commission_rate"] = str(percent / Decimal(100))
            record["sales"] = str(number(self.fields["sales"].get(), "Ventas"))
        else:
            record["monthly_salary"] = str(number(self.fields["monthly_salary"].get(), "Salario mensual"))
            record["contract_months"] = number(self.fields["contract_months"].get(), "Duración del contrato", True)
        employee = self._employee_from_record(record)
        # Valida también el bruto antes de aceptar el registro.
        employee.gross_salary()
        return record

    def _save(self):
        try:
            record = self._make_record()
            emp_id = record["employee_id"]
            if emp_id in self.records and self.editing_id != emp_id:
                raise ValueError("Ya existe un empleado con esa identificación.")
            if self.editing_id and self.editing_id != emp_id and emp_id in self.records:
                raise ValueError("Ya existe otro empleado con esa identificación.")
            if self.editing_id and self.editing_id != emp_id:
                self.records.pop(self.editing_id, None)
            self.records[emp_id] = record
            self._persist()
            self._refresh_table()
            self._clear()
            messagebox.showinfo("Empleado guardado", "Los datos del empleado se guardaron correctamente.")
        except (ValueError, InvalidOperation, OSError) as exc:
            messagebox.showerror("No se pudo guardar", str(exc))

    def _refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        service = PayrollService(PayrollConfig())
        for emp_id, record in sorted(self.records.items()):
            try:
                result = service.calculate(self._employee_from_record(record))
                self.tree.insert("", "end", iid=emp_id, values=(
                    emp_id, record["name"], MAP_TYPE[record["kind"]],
                    cop(result.gross_salary), cop(result.net_pay)
                ))
            except (ValueError, KeyError, InvalidOperation):
                self.tree.insert("", "end", iid=emp_id, values=(emp_id, record.get("name", ""), "Revisar datos", "—", "—"))

    def _selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona un empleado", "Primero selecciona un empleado de la tabla.")
            return None
        return self.records.get(selected[0])

    def _edit_selected(self):
        record = self._selected_record()
        if not record:
            return
        self.editing_id = record["employee_id"]
        self.type_var.set(MAP_TYPE[record["kind"]])
        self._render_type_fields()
        for key in ("employee_id", "name"):
            self.fields[key].delete(0, "end")
            self.fields[key].insert(0, record[key])
        for key, value in record.items():
            field_key = "commission_percent" if key == "commission_rate" else key
            if field_key in self.fields:
                self.fields[field_key].delete(0, "end")
                if key == "commission_rate":
                    value = str(Decimal(value) * Decimal(100))
                self.fields[field_key].insert(0, str(value))
        if record["kind"] == "hourly":
            self.savings_var.set(record.get("accepts_savings_fund", False))
        self.fields["employee_id"].focus_set()

    def _delete_selected(self):
        record = self._selected_record()
        if not record:
            return
        if messagebox.askyesno("Confirmar eliminación", f"¿Eliminar a {record['name']} ({record['employee_id']})?"):
            self.records.pop(record["employee_id"], None)
            self._persist()
            self._refresh_table()
            self._clear()

    def _clear(self):
        self.editing_id = None
        for entry in self.fields.values():
            entry.delete(0, "end")
        self.type_var.set(TYPES[0])
        self._render_type_fields()
        self.fields["employee_id"].focus_set()

    def _calculate(self):
        if not self.records:
            messagebox.showinfo("Nómina", "Todavía no hay empleados registrados.")
            return
        service = PayrollService(PayrollConfig())
        lines = []
        total = Decimal("0")
        try:
            for emp_id, record in sorted(self.records.items()):
                result = service.calculate(self._employee_from_record(record))
                total += result.net_pay
                lines.append(
                    f"{result.employee_name} ({result.employee_id})\n"
                    f"  Salario bruto: {cop(result.gross_salary)}\n"
                    f"  Seguridad social y pensión: {cop(result.social_security_and_pension)}\n"
                    f"  ARL: {cop(result.arl)}\n"
                    f"  Fondo de ahorro: {cop(result.savings_contribution)}\n"
                    f"  Salario neto: {cop(result.net_pay)}\n"
                    f"  Bono de alimentación (empresa): {cop(result.employer_food_benefit)}\n"
                )
        except (ValueError, KeyError, InvalidOperation) as exc:
            messagebox.showerror("Error de cálculo", str(exc))
            return
        win = tk.Toplevel(self)
        win.title("Resultado de nómina")
        win.geometry("700x600")
        text = tk.Text(win, wrap="word", font=("Monospace", 10), padx=12, pady=12)
        text.pack(fill="both", expand=True)
        text.insert("1.0", "\n".join(lines) + f"\nTOTAL NETO A PAGAR: {cop(total)}\n")
        text.configure(state="disabled")
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=8)


if __name__ == "__main__":
    app = PayrollApp()
    app.mainloop()
