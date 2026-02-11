import frappe
from frappe.utils import now


def _append_audit(doc, message):
    entry = f"[{now()}] {message} by {frappe.session.user}\n"
    doc.audit_log = (doc.audit_log or "") + entry


def validate_commission_permissions(doc, method=None):
    """Enforce that only users with Accountant role can approve/payable and prevent edits to approved records.

    This runs before save on `Commission Record`.
    """
    approved_statuses = ("Approved", "Payable", "Paid")

    # If this is an existing doc, fetch current status from DB
    if doc.name and frappe.db.exists('Commission Record', doc.name):
        existing_status = frappe.db.get_value('Commission Record', doc.name, 'status')
    else:
        existing_status = None

    # If attempting to transition to an accountant-only state, require Accountant role
    if doc.status in ("Approved", "Payable") and not frappe.has_role('Accountant'):
        # allow Administrator (system) as well
        if not frappe.has_role('Administrator'):
            frappe.throw('Only users with the Accountant role can set status to Approved or Payable')

    # Prevent edits to approved/payable/paid records by non-accountants
    if existing_status in approved_statuses:
        # if user is not Accountant or Administrator, disallow modifications
        if not (frappe.has_role('Accountant') or frappe.has_role('Administrator')):
            # allow no changes except adding comments to audit_log
            # Compare key editable fields
            immutable_fields = ['user', 'role', 'opportunity', 'commission_amount', 'status']
            for f in immutable_fields:
                db_val = frappe.db.get_value('Commission Record', doc.name, f)
                cur_val = doc.get(f)
                # normalize numeric
                if isinstance(db_val, float) or isinstance(cur_val, float):
                    db_val = float(db_val or 0)
                    cur_val = float(cur_val or 0)
                if str(db_val) != str(cur_val):
                    frappe.throw('Approved commission records cannot be modified. Contact Accountant to change status.')


def on_change_audit(doc, method=None):
    """Append audit entries for status changes and approvals."""
    try:
        if not doc.get('doctype') == 'Commission Record':
            return
        # Determine prior status
        prior_status = None
        if doc.name and frappe.db.exists('Commission Record', doc.name):
            prior_status = frappe.db.get_value('Commission Record', doc.name, 'status')
        # If status changed to Approved, set approval_by and log
        if doc.status == 'Approved' and prior_status != 'Approved':
            doc.approval_by = frappe.session.user
            _append_audit(doc, 'Status changed to Approved')
        elif doc.status == 'Payable' and prior_status != 'Payable':
            _append_audit(doc, 'Status changed to Payable')
        elif doc.status == 'Paid' and prior_status != 'Paid':
            _append_audit(doc, 'Status changed to Paid')
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'Commission Record audit failed')
