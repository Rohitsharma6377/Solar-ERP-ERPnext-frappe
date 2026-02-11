import frappe

def execute():
    try:
        # Create example Commission Rule with splits
        if not frappe.db.exists('Commission Rule', {'rule_name': 'Default Setter Commission'}):
            cr = frappe.get_doc({
                'doctype': 'Commission Rule',
                'rule_name': 'Default Setter Commission',
                'role': 'Setter',
                'is_percentage': 1,
                'value': 5.0,
                'enabled': 1
            }).insert(ignore_permissions=True)
        # Create an example split rule
        if not frappe.db.exists('Commission Rule', {'rule_name': 'Closer + Setter Split'}):
            cr2 = frappe.get_doc({
                'doctype': 'Commission Rule',
                'rule_name': 'Closer + Setter Split',
                'role': 'Closer',
                'is_percentage': 1,
                'value': 6.0,
                'enabled': 1
            }).insert(ignore_permissions=True)
            # add splits child table
            cr2.append('splits', {'user': frappe.session.user, 'share_percentage': 60})
            cr2.append('splits', {'user': frappe.session.user, 'share_percentage': 40})
            cr2.save(ignore_permissions=True)

        # Create Default Task Template
        if not frappe.db.exists('Task Template', {'template_name': 'Default'}):
            tmpl = frappe.get_doc({
                'doctype': 'Task Template',
                'template_name': 'Default'
            }).insert(ignore_permissions=True)
            tmpl.append('tasks', {'subject': 'Site Survey', 'owner_role': 'Setter', 'sequence': 1})
            tmpl.append('tasks', {'subject': 'Design', 'owner_role': 'Designer', 'sequence': 2})
            tmpl.append('tasks', {'subject': 'Installation', 'owner_role': 'Project Manager', 'sequence': 3})
            tmpl.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'Seeding example data failed')
