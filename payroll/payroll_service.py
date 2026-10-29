"""Servicio que calcula la nómina de los empleados."""
from dataclasses import dataclass
from decimal import Decimal

from .employees import Employee, money


@dataclass(frozen=True)
class PayrollConfig:
    """Tasas de deducción como fracción (0.04 = 4%)."""

    social_security_and_pension_rate: Decimal = Decimal("0.04")
    # El enunciado no da el porcentaje de ARL; usamos 0.522% (riesgo I) como supuesto
    arl_rate: Decimal = Decimal("0.00522")

    def __post_init__(self):
        for name, rate in (
            ("seguridad social y pensión", self.social_security_and_pension_rate),
            ("ARL", self.arl_rate),
        ):
            if not Decimal(0) <= rate <= Decimal(1):
                raise ValueError(f"La tasa de {name} debe estar entre 0 y 1.")


@dataclass(frozen=True)
class PayrollResult:
    employee_id: str
    employee_name: str
    gross_salary: Decimal
    social_security_and_pension: Decimal
    arl: Decimal
    savings_contribution: Decimal
    net_pay: Decimal
    employer_food_benefit: Decimal


class PayrollService:
    """Trabaja solo con Employee, sin importar qué tipo de empleado sea."""

    def __init__(self, config: PayrollConfig):
        self._config = config

    def calculate(self, employee: Employee) -> PayrollResult:
        gross = money(employee.gross_salary())
        social = money(gross * self._config.social_security_and_pension_rate)
        arl = money(gross * self._config.arl_rate)
        savings = money(employee.savings_contribution)
        net = money(gross - social - arl - savings)

        if net < 0:
            raise ValueError("El salario neto no puede ser negativo.")

        return PayrollResult(
            employee_id=employee.employee_id,
            employee_name=employee.name,
            gross_salary=gross,
            social_security_and_pension=social,
            arl=arl,
            savings_contribution=savings,
            net_pay=net,
            employer_food_benefit=money(employee.food_benefit),
        )

    def calculate_all(self, employees: list[Employee]) -> list[PayrollResult]:
        """Liquida a todos los empleados de la lista."""
        return [self.calculate(employee) for employee in employees]
