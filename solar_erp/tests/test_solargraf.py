import frappe
import unittest
from unittest.mock import patch, MagicMock

from solar_erp.api import solargraf


class TestSolarGrafIntegration(unittest.TestCase):
    def setUp(self):
        self.opp = frappe.get_doc({
            'doctype': 'Opportunity',
            'subject': 'UT - SolarGraf Opp',
            'customer': 'SG Customer',
            'system_size_kw': 3.5
        }).insert(ignore_permissions=True)

    def tearDown(self):
        try:
            frappe.delete_doc('Opportunity', self.opp.name, ignore_permissions=True)
        except Exception:
            pass

    @patch('solar_erp.api.solargraf.requests.post')
    def test_create_solargraf_project(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {'id': 'SG-TEST-1'}
        mock_post.return_value = mock_resp

        # ensure settings present
        if not frappe.db.exists('SolarGraf Settings'):
            s = frappe.get_doc({'doctype': 'SolarGraf Settings', 'enabled': 1, 'base_url': 'https://api.example.com'}).insert(ignore_permissions=True)
        solargraf_id = solargraf.create_solargraf_project(self.opp.name)
        self.assertIsNotNone(solargraf_id)
        self.assertTrue(solar graf_id := frappe.db.get_value('Opportunity', self.opp.name, 'solargraf_project_id'))
