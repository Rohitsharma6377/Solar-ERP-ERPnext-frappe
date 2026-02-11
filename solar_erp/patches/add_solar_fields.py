import frappe

def execute():
    """Create custom fields on Opportunity for Solar ERP"""
    custom_fields = [
        {"dt": "Opportunity", "fieldname": "roof_type", "label": "Roof Type", "fieldtype": "Select", "options": "Flat\nSloped\nTile\nMetal\nOther"},
        {"dt": "Opportunity", "fieldname": "system_size_kw", "label": "System Size (kW)", "fieldtype": "Float"},
        {"dt": "Opportunity", "fieldname": "utility_provider", "label": "Utility Provider", "fieldtype": "Data"},
        {"dt": "Opportunity", "fieldname": "estimated_monthly_bill", "label": "Estimated Monthly Bill", "fieldtype": "Currency"},
        {"dt": "Opportunity", "fieldname": "lead_source_solar", "label": "Lead Source (Solar)", "fieldtype": "Data"},
        {"dt": "Opportunity", "fieldname": "setter_notes", "label": "Setter Notes", "fieldtype": "Text"},
        {"dt": "Opportunity", "fieldname": "solar_proposal_status", "label": "Solar Proposal Status", "fieldtype": "Select", "options": "Draft\nGenerated\nSigned\nRejected"},
        {"dt": "Opportunity", "fieldname": "design_approved", "label": "Design Approved", "fieldtype": "Check"},
        {"dt": "Opportunity", "fieldname": "solargraf_project_id", "label": "SolarGraf Project ID", "fieldtype": "Data"},
        {"dt": "Opportunity", "fieldname": "signed_proposal_attachment", "label": "Signed Proposal Attachment", "fieldtype": "Attach"},
        {"dt": "Opportunity", "fieldname": "closer_notes", "label": "Closer Notes", "fieldtype": "Text"},
        {"dt": "Opportunity", "fieldname": "handoff_notes", "label": "Handoff Notes", "fieldtype": "Text"},
        {"dt": "Opportunity", "fieldname": "assigned_setter", "label": "Assigned Setter", "fieldtype": "Link", "options": "User"},
        {"dt": "Opportunity", "fieldname": "assigned_closer", "label": "Assigned Closer", "fieldtype": "Link", "options": "User"}
    ]

    for f in custom_fields:
        try:
            if not frappe.db.exists('Custom Field', {'dt': f['dt'], 'fieldname': f['fieldname']}):
                doc = frappe.get_doc({
                    'doctype': 'Custom Field',
                    'dt': f['dt'],
                    'fieldname': f['fieldname'],
                    'label': f['label'],
                    'fieldtype': f['fieldtype']
                })
                # optional extras
                if 'options' in f:
                    doc.options = f['options']
                doc.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), 'Creating custom field failed')
