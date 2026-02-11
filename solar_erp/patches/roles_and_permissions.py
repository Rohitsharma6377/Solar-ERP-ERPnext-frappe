import frappe

ROLE_LIST = [
    'Setter',
    'Designer',
    'Closer',
    'Project Manager',
    'Accountant'
]

PERMISSIONS_MATRIX = {
    'Opportunity': [
        {'role': 'Administrator', 'read':1, 'write':1, 'create':1},
        {'role': 'Setter', 'read':1, 'write':1},
        {'role': 'Designer', 'read':1},
        {'role': 'Closer', 'read':1, 'write':1},
        {'role': 'Project Manager', 'read':1},
        {'role': 'Accountant', 'read':1}
    ],
    'Commission Record': [
        {'role': 'Administrator', 'read':1, 'write':1, 'create':1},
        {'role': 'Closer', 'read':1, 'write':1},
        {'role': 'Accountant', 'read':1, 'write':1}
    ],
    'Commission Rule': [
        {'role': 'Administrator', 'read':1, 'write':1, 'create':1},
        {'role': 'Accountant', 'read':1}
    ],
    'Project': [
        {'role': 'Administrator', 'read':1, 'write':1, 'create':1},
        {'role': 'Setter', 'read':1},
        {'role': 'Closer', 'read':1},
        {'role': 'Project Manager', 'read':1, 'write':1},
        {'role': 'Accountant', 'read':1}
    ],
    'Task': [
        {'role': 'Administrator', 'read':1, 'write':1, 'create':1},
        {'role': 'Setter', 'read':1, 'write':1},
        {'role': 'Designer', 'read':1, 'write':1},
        {'role': 'Closer', 'read':1, 'write':1},
        {'role': 'Project Manager', 'read':1, 'write':1},
        {'role': 'Accountant', 'read':1, 'write':1}
    ]
}

def create_roles():
    for r in ROLE_LIST:
        if not frappe.db.exists('Role', r):
            frappe.get_doc({'doctype': 'Role', 'role_name': r}).insert(ignore_permissions=True)

def apply_permissions():
    for doctype, perms in PERMISSIONS_MATRIX.items():
        try:
            dt = frappe.get_doc('DocType', doctype)
            # build permissions list
            dt.permissions = []
            for p in perms:
                entry = {
                    'doctype': 'DocType Permission',
                    'role': p['role'],
                    'permlevel': 0,
                    'read': int(p.get('read', 0)),
                    'write': int(p.get('write', 0)),
                    'create': int(p.get('create', 0)),
                    'submit': int(p.get('submit', 0)),
                    'cancel': int(p.get('cancel', 0)),
                    'amend': int(p.get('amend', 0))
                }
                dt.append('permissions', entry)
            dt.save(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f'Applying permissions for {doctype} failed')

def execute():
    create_roles()
    apply_permissions()
