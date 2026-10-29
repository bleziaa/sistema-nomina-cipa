"""Empleados del sistema de nómina y su forma de calcular el salario bruto."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

# Reglas del enunciado
SENIORITY_BONUS_MIN_YEARS = 5
SENIORITY_BONUS_RATE = Decimal("0.10")
REGULAR_HOURS_LIMIT = Decimal("40")
OVERTIME_MULTIPLIER = Decimal("1.5")
SALES_BONUS_THRESHOLD = Decimal("20000000")
SALES_BONUS_RATE = Decimal("0.03")
FOOD_BENEFIT_AMOUNT = Decimal("1000000")
SAVINGS_FUND_MIN_YEARS = 1
SAVINGS_FUND_RATE = Decimal("0.02")


def money(value) -> Decimal:
    """Pasa el valor a Decimal con 2 decimales (no usamos float para el dinero)."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class Employee(ABC):
    employee_id: str
    name: str

    def __post_init__(self):
        if not self.employee_id.strip():
            raise ValueError("El identificador del empleado es obligatorio.")
        if not self.name.strip():
            raise ValueError("El nombre del empleado es obligatorio.")

    @abstractmethod
    def gross_salary(self) -> Decimal:
        """Salario bruto del mes; cada tipo de empleado lo calcula distinto."""

    @property
    def food_benefit(self) -> Decimal:
        # Por defecto no recibe bono de alimentación
        return money(0)

    @property
    def savings_contribution(self) -> Decimal:
        # Por defecto no aporta al fondo de ahorro
        return money(0)


@dataclass
class PermanentEmployee(Employee, ABC):
    """Base de los empleados permanentes, que reciben el bono de alimentación."""

    @property
    def food_benefit(self) -> Decimal:
        return money(FOOD_BENEFIT_AMOUNT)


@dataclass
class SalariedEmployee(PermanentEmployee):
    monthly_salary: Decimal
    years_of_service: int

    def __post_init__(self):
        super().__post_init__()
        self.monthly_salary = money(self.monthly_salary)
        if self.monthly_salary < 0:
            raise ValueError("El salario mensual no puede ser negativo.")
        if self.years_of_service < 0:
            raise ValueError("La antigüedad no puede ser negativa.")

    def gross_salary(self) -> Decimal:
        bonus = Decimal(0)
        # El bono es solo si lleva MÁS de 5 años
        if self.years_of_service > SENIORITY_BONUS_MIN_YEARS:
            bonus = self.monthly_salary * SENIORITY_BONUS_RATE
        return money(self.monthly_salary + bonus)


@dataclass
class HourlyEmployee(Employee):
    hourly_rate: Decimal
    hours_worked: Decimal
    years_of_service: int
    accepts_savings_fund: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.hourly_rate = money(self.hourly_rate)
        self.hours_worked = Decimal(str(self.hours_worked))
        if self.hourly_rate < 0:
            raise ValueError("La tarifa por hora no puede ser negativa.")
        if self.hours_worked < 0:
            raise ValueError("Las horas trabajadas no pueden ser negativas.")
        if self.years_of_service < 0:
            raise ValueError("La antigüedad no puede ser negativa.")

    def gross_salary(self) -> Decimal:
        regular_hours = min(self.hours_worked, REGULAR_HOURS_LIMIT)
        overtime_hours = max(self.hours_worked - REGULAR_HOURS_LIMIT, Decimal(0))
        regular_pay = regular_hours * self.hourly_rate
        overtime_pay = overtime_hours * self.hourly_rate * OVERTIME_MULTIPLIER
        return money(regular_pay + overtime_pay)

    @property
    def savings_contribution(self) -> Decimal:
        # Necesita más de 1 año y que el empleado acepte el fondo
        if self.years_of_service > SAVINGS_FUND_MIN_YEARS and self.accepts_savings_fund:
            return money(self.gross_salary() * SAVINGS_FUND_RATE)
        return money(0)


@dataclass
class CommissionEmployee(PermanentEmployee):
    base_salary: Decimal
    commission_rate: Decimal
    sales: Decimal

    def __post_init__(self):
        super().__post_init__()
        self.base_salary = money(self.base_salary)
        self.commission_rate = Decimal(str(self.commission_rate))
        self.sales = money(self.sales)
        if self.base_salary < 0:
            raise ValueError("El salario base no puede ser negativo.")
        if not Decimal(0) <= self.commission_rate <= Decimal(1):
            raise ValueError("La comisión debe estar entre 0 y 1 (0%-100%).")
        if self.sales < 0:
            raise ValueError("Las ventas no pueden ser negativas.")

    def gross_salary(self) -> Decimal:
        commission = self.sales * self.commission_rate
        sales_bonus = Decimal(0)
        # "Superan" los 20 millones: con exactamente 20 millones no hay bono
        if self.sales > SALES_BONUS_THRESHOLD:
            sales_bonus = self.sales * SALES_BONUS_RATE
        return money(self.base_salary + commission + sales_bonus)


@dataclass
class TemporaryEmployee(Employee):
    monthly_salary: Decimal
    contract_months: int

    def __post_init__(self):
        super().__post_init__()
        self.monthly_salary = money(self.monthly_salary)
        if self.monthly_salary < 0:
            raise ValueError("El salario mensual no puede ser negativo.")
        if self.contract_months <= 0:
            raise ValueError("La duración del contrato debe ser mayor que cero.")

    def gross_salary(self) -> Decimal:
        # Sin bonos ni beneficios adicionales
        return money(self.monthly_salary)
