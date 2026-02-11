import frappe

def make_workflow(name, document, states, transitions, is_active=1):
    if frappe.db.exists('Workflow', {'workflow_name': name}):
        return
    wf = frappe.get_doc({
        'doctype': 'Workflow',
        'workflow_name': name,
        'document_type': document,
        'is_active': is_active,
        'states': states,
        'transitions': transitions
    })
    wf.insert(ignore_permissions=True)

def execute():
    # Opportunity workflow
    states = [
        {'state': 'New', 'idx': 1},
        {'state': 'Qualified', 'idx': 2},
        {'state': 'Design', 'idx': 3},
        {'state': 'Proposal', 'idx': 4},
        {'state': 'Approved', 'idx': 5},
        {'state': 'Won', 'idx': 6},
        {'state': 'Lost', 'idx': 7}
    ]
    transitions = [
        {'state': 'New', 'next_state': 'Qualified', 'allowed': []},
        {'state': 'Qualified', 'next_state': 'Design', 'allowed': []},
        {'state': 'Design', 'next_state': 'Proposal', 'allowed': []},
        {'state': 'Proposal', 'next_state': 'Approved', 'allowed': []},
        {'state': 'Approved', 'next_state': 'Won', 'allowed': []},
        {'state': 'Proposal', 'next_state': 'Lost', 'allowed': []}
    ]
    try:
        make_workflow('Opportunity Solar Workflow', 'Opportunity', states, transitions)
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'Creating Opportunity workflow failed')

    # Commission Record workflow
    states = [
        {'state': 'Pending', 'idx': 1},
        {'state': 'Approved', 'idx': 2},
        {'state': 'Payable', 'idx': 3},
        {'state': 'Paid', 'idx': 4}
    ]
    transitions = [
        {'state': 'Pending', 'next_state': 'Approved', 'allowed': ['Accountant']},
        {'state': 'Approved', 'next_state': 'Payable', 'allowed': ['Accountant']},
        {'state': 'Payable', 'next_state': 'Paid', 'allowed': []}
    ]
    try:
        make_workflow('Commission Record Workflow', 'Commission Record', states, transitions)
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'Creating Commission Record workflow failed')
