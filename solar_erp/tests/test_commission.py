import frappe
import unittest

from solar_erp.api.commission import generate_commissions_for_opportunity


class TestCommissionGeneration(unittest.TestCase):
    def setUp(self):
        # create a test Opportunity
        self.opp = frappe.get_doc({
            'doctype': 'Opportunity',
            'subject': 'UT - Commission Opp',
            'customer': 'Test Customer',
            'system_size_kw': 5.0
        }).insert(ignore_permissions=True)

        # create a commission rule (10% of kW*1000)
        self.rule = frappe.get_doc({
            'doctype': 'Commission Rule',
            'rule_name': 'UT Rule',
            'role': 'Setter',
            'is_percentage': 1,
            'value': 10,
            'enabled': 1
        }).insert(ignore_permissions=True)

    def tearDown(self):
        # cleanup
        try:
            frappe.delete_doc('Commission Rule', self.rule.name, ignore_permissions=True)
        except Exception:
            pass
        try:
            # delete generated commission records
            crs = frappe.get_all('Commission Record', filters={'opportunity': self.opp.name})
            for c in crs:
                frappe.delete_doc('Commission Record', c.name, ignore_permissions=True)
        except Exception:
            pass
        try:
            frappe.delete_doc('Opportunity', self.opp.name, ignore_permissions=True)
        except Exception:
            pass

    def test_generate_commissions(self):
        created = generate_commissions_for_opportunity(self.opp.name)
        self.assertTrue(len(created) >= 1)
        # verify commission record exists
        cr = frappe.get_all('Commission Record', filters={'opportunity': self.opp.name}, limit_page_length=1)
        self.assertTrue(len(cr) == 1)
