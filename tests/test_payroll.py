"""Pruebas unitarias del sistema de nómina."""
import unittest
from decimal import Decimal

from payroll.employees import (
    Employee,
    SalariedEmployee,
    HourlyEmployee,
    CommissionEmployee,
    TemporaryEmployee,
)
from payroll.payroll_service import PayrollConfig, PayrollService


class SalariedEmployeeTests(unittest.TestCase):
    def test_bonus_only_after_more_than_five_years(self):
        five_years = SalariedEmployee("1", "Ana", 2_000_000, 5)
        six_years = SalariedEmployee("2", "Luis", 2_000_000, 6)
        self.assertEqual(five_years.gross_salary(), Decimal("2000000.00"))
        self.assertEqual(six_years.gross_salary(), Decimal("2200000.00"))

    def test_has_food_benefit(self):
        employee = SalariedEmployee("3", "Sol", 1_000_000, 0)
        self.assertEqual(employee.food_benefit, Decimal("1000000.00"))

    def test_negative_salary_is_rejected(self):
        with self.assertRaises(ValueError):
            SalariedEmployee("4", "Vic", -100, 0)

    def test_negative_years_are_rejected(self):
        with self.assertRaises(ValueError):
            SalariedEmployee("5", "Vic", 100, -1)


class HourlyEmployeeTests(unittest.TestCase):
    def test_exactly_40_hours_has_no_overtime(self):
        employee = HourlyEmployee("6", "Marta", 10_000, 40, 0)
        self.assertEqual(employee.gross_salary(), Decimal("400000.00"))

    def test_overtime_is_paid_at_one_and_half(self):
        employee = HourlyEmployee("7", "Marta", 10_000, 45, 0)
        # 40 x 10.000 + 5 x 15.000 = 475.000
        self.assertEqual(employee.gross_salary(), Decimal("475000.00"))

    def test_one_overtime_hour(self):
        employee = HourlyEmployee("8", "Marta", 10_000, 41, 0)
        self.assertEqual(employee.gross_salary(), Decimal("415000.00"))

    def test_has_no_food_benefit(self):
        employee = HourlyEmployee("9", "Marta", 10_000, 40, 0)
        self.assertEqual(employee.food_benefit, Decimal("0.00"))

    def test_savings_fund_requires_consent_and_more_than_one_year(self):
        eligible = HourlyEmployee("10", "Eva", 10_000, 40, 2, True)
        exactly_one_year = HourlyEmployee("11", "Noé", 10_000, 40, 1, True)
        no_consent = HourlyEmployee("12", "Leo", 10_000, 40, 3, False)
        self.assertEqual(eligible.savings_contribution, Decimal("8000.00"))
        self.assertEqual(exactly_one_year.savings_contribution, Decimal("0.00"))
        self.assertEqual(no_consent.savings_contribution, Decimal("0.00"))

    def test_negative_hours_are_rejected(self):
        with self.assertRaises(ValueError):
            HourlyEmployee("13", "Tom", 10_000, -1, 0)


class CommissionEmployeeTests(unittest.TestCase):
    def test_commission_and_sales_bonus_above_threshold(self):
        employee = CommissionEmployee("14", "Sara", 1_000_000, "0.05", 21_000_000)
        # 1.000.000 + 1.050.000 (5%) + 630.000 (3%)
        self.assertEqual(employee.gross_salary(), Decimal("2680000.00"))

    def test_no_bonus_when_sales_equal_threshold(self):
        employee = CommissionEmployee("15", "Sara", 1_000_000, "0.05", 20_000_000)
        # con exactamente 20M no hay bono del 3%
        self.assertEqual(employee.gross_salary(), Decimal("2000000.00"))

    def test_has_food_benefit(self):
        employee = CommissionEmployee("16", "Sara", 1_000_000, "0.05", 0)
        self.assertEqual(employee.food_benefit, Decimal("1000000.00"))

    def test_negative_sales_are_rejected(self):
        with self.assertRaises(ValueError):
            CommissionEmployee("17", "Uma", 1_000_000, "0.05", -1)

    def test_invalid_commission_rate_is_rejected(self):
        with self.assertRaises(ValueError):
            CommissionEmployee("18", "Uma", 1_000_000, "1.5", 100)


class TemporaryEmployeeTests(unittest.TestCase):
    def test_has_no_extra_benefits(self):
        employee = TemporaryEmployee("19", "Joel", 1_500_000, 6)
        self.assertEqual(employee.gross_salary(), Decimal("1500000.00"))
        self.assertEqual(employee.food_benefit, Decimal("0.00"))
        self.assertEqual(employee.savings_contribution, Decimal("0.00"))

    def test_contract_duration_must_be_positive(self):
        with self.assertRaises(ValueError):
            TemporaryEmployee("20", "Joel", 1_500_000, 0)


class EmployeeBaseTests(unittest.TestCase):
    def test_empty_id_is_rejected(self):
        with self.assertRaises(ValueError):
            SalariedEmployee("  ", "Ana", 1_000_000, 0)

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            SalariedEmployee("21", "", 1_000_000, 0)

    def test_employee_is_abstract(self):
        with self.assertRaises(TypeError):
            Employee("22", "Nadie")


class PayrollServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = PayrollService(PayrollConfig(arl_rate=Decimal("0.01")))

    def test_deductions_are_based_on_gross_salary(self):
        result = self.service.calculate(SalariedEmployee("23", "Paz", 1_000_000, 0))
        self.assertEqual(result.social_security_and_pension, Decimal("40000.00"))
        self.assertEqual(result.arl, Decimal("10000.00"))
        self.assertEqual(result.net_pay, Decimal("950000.00"))

    def test_food_benefit_is_employer_paid_not_added_to_net(self):
        result = self.service.calculate(SalariedEmployee("24", "Sol", 1_000_000, 0))
        self.assertEqual(result.employer_food_benefit, Decimal("1000000.00"))
        self.assertEqual(result.net_pay, Decimal("950000.00"))

    def test_savings_fund_is_deducted_from_hourly_net(self):
        employee = HourlyEmployee("25", "Eva", 10_000, 40, 2, True)
        result = self.service.calculate(employee)
        # 400.000 - 16.000 - 4.000 - 8.000
        self.assertEqual(result.savings_contribution, Decimal("8000.00"))
        self.assertEqual(result.net_pay, Decimal("372000.00"))

    def test_net_pay_cannot_be_negative(self):
        # con ARL al 99% más el 4% las deducciones superan el bruto
        service = PayrollService(PayrollConfig(arl_rate=Decimal("0.99")))
        with self.assertRaises(ValueError):
            service.calculate(SalariedEmployee("26", "Max", 1_000_000, 0))

    def test_default_config_uses_four_percent_pension(self):
        config = PayrollConfig()
        self.assertEqual(config.social_security_and_pension_rate, Decimal("0.04"))
        self.assertGreater(config.arl_rate, Decimal("0"))

    def test_invalid_rates_are_rejected(self):
        with self.assertRaises(ValueError):
            PayrollConfig(arl_rate=Decimal("1.2"))
        with self.assertRaises(ValueError):
            PayrollConfig(social_security_and_pension_rate=Decimal("-0.1"))

    def test_new_employee_type_works_without_changing_the_service(self):
        # Open/Closed: un tipo nuevo funciona sin modificar PayrollService
        class InternEmployee(Employee):
            def gross_salary(self):
                return Decimal("1000000.00")

        result = self.service.calculate(InternEmployee("27", "Pasante"))
        self.assertEqual(result.gross_salary, Decimal("1000000.00"))
        self.assertEqual(result.net_pay, Decimal("950000.00"))

    def test_calculate_all_returns_one_result_per_employee(self):
        employees = [
            SalariedEmployee("28", "Ana", 1_000_000, 0),
            TemporaryEmployee("29", "Joel", 1_500_000, 6),
        ]
        results = self.service.calculate_all(employees)
        self.assertEqual([r.employee_id for r in results], ["28", "29"])
        self.assertEqual(results[1].net_pay, Decimal("1425000.00"))


if __name__ == "__main__":
    unittest.main()
