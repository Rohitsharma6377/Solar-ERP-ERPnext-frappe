import frappe
from frappe import _

def validate_opportunity(doc, method=None):
    # basic validations for solar fields
    if doc.get('system_size_kw') and doc.system_size_kw < 0:
        frappe.throw(_('System size must be positive'))

def on_update_opportunity(doc, method=None):
    # when Opportunity reaches stage configured to create SolarGraf project
    try:
        settings = frappe.get_single('SolarGraf Settings')
        if settings and settings.enabled and settings.create_on_stage:
            if doc.get('status') == settings.create_on_stage and not doc.get('solargraf_project_id'):
                frappe.enqueue('solar_erp.api.solargraf.create_solargraf_project', opportunity_name=doc.name)
        # Create Project when Opportunity is Approved/Won
        if doc.get('status') in ('Approved', 'Won') and not doc.get('project'):
            frappe.enqueue('solar_erp.api.project.create_project_from_opportunity', opportunity_name=doc.name)
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'Opportunity update handler failed')
