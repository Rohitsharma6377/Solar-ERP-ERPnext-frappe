import frappe

def create_project_from_opportunity(opportunity_name):
    """Create a Project and standard Tasks from an Opportunity.
    Idempotent: if Opportunity.project exists, return existing.
    """
    opp = frappe.get_doc('Opportunity', opportunity_name)
    if opp.get('project'):
        return opp.project

    # determine project manager
    settings = frappe.get_single('SolarGraf Settings')
    pm = None
    if opp.get('assigned_to'):
        pm = opp.get('assigned_to')
    if not pm and opp.get('assigned_closer'):
        pm = opp.get('assigned_closer')
    if not pm and getattr(settings, 'default_pm', None):
        pm = settings.default_pm

    project = frappe.get_doc({
        'doctype': 'Project',
        'project_name': f"{opp.name} - {opp.customer or 'Project'}",
        'customer': opp.customer,
        'status': 'Open',
        'expected_start_date': frappe.utils.nowdate(),
        'expected_end_date': None,
        'project_manager': pm
    }).insert(ignore_permissions=True)

    # attach project to opportunity
    opp.db_set('project', project.name)

    # create tasks from Task Template if present, else fallback to defaults
    try:
        templates = frappe.get_all('Task Template', filters={}, limit_page_length=1)
        if templates:
            tmpl = frappe.get_doc('Task Template', templates[0].name)
            for item in tmpl.tasks:
                owner = None
                if item.owner_role:
                    # pick a user having that role if exists
                    users = frappe.get_all('Has Role', filters={'role': item.owner_role}, fields=['parent'], limit_page_length=1)
                    if users:
                        owner = users[0].parent
                frappe.get_doc({
                    'doctype': 'Task',
                    'subject': item.subject,
                    'status': 'Open',
                    'project': project.name,
                    'assigned_to': owner
                }).insert(ignore_permissions=True)
        else:
            # fallback default tasks
            defaults = [
                'Site Survey', 'Design', 'Procurement', 'Installation', 'Commissioning', 'Handover & Training'
            ]
            for name in defaults:
                frappe.get_doc({
                    'doctype': 'Task',
                    'subject': name,
                    'status': 'Open',
                    'project': project.name,
                    'assigned_to': pm
                }).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'Creating project task failed')

    frappe.db.commit()
    return project.name
