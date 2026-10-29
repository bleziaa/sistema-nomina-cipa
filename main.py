"""Demostración del sistema de nómina."""
from payroll.employees import (
    SalariedEmployee,
    HourlyEmployee,
    CommissionEmployee,
    TemporaryEmployee,
)
from payroll.payroll_service import PayrollConfig, PayrollService


def main():
    service = PayrollService(PayrollConfig())
    employees = [
        SalariedEmployee("E001", "Ana Pérez", 2_500_000, 7),
        HourlyEmployee("E002", "Carlos Díaz", 15_000, 45, 2, True),
        CommissionEmployee("E003", "María Ruiz", 1_500_000, "0.05", 22_000_000),
        TemporaryEmployee("E004", "Juan López", 1_800_000, 4),
    ]

    results = service.calculate_all(employees)
    for result in results:
        print(f"{result.employee_name} ({result.employee_id})")
        print(f"  {'Salario bruto:':<24} {f'${result.gross_salary:,.2f}':>16}")
        print(f"  {'Seguridad y pensión:':<24} {f'${result.social_security_and_pension:,.2f}':>16}")
        print(f"  {'ARL:':<24} {f'${result.arl:,.2f}':>16}")
        print(f"  {'Fondo de ahorro:':<24} {f'${result.savings_contribution:,.2f}':>16}")
        print(f"  {'Salario neto:':<24} {f'${result.net_pay:,.2f}':>16}")
        print(f"  {'Alimentación (empresa):':<24} {f'${result.employer_food_benefit:,.2f}':>16}")
        print()

    total = sum(result.net_pay for result in results)
    print(f"Total neto a pagar: ${total:,.2f}")


if __name__ == "__main__":
    main()
