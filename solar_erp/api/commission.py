import frappe

def generate_commissions_for_opportunity(opportunity_name, trigger="opportunity_won"):
    opp = frappe.get_doc("Opportunity", opportunity_name)
    rules = frappe.get_all("Commission Rule", filters={"enabled": 1})
    created = []
    for r in rules:
        rule = frappe.get_doc("Commission Rule", r.name)
        # minimal condition match: if conditions empty, apply universally
        apply_rule = True
        if rule.conditions:
            try:
                ctx = {"doc": opp.as_dict()}
                apply_rule = frappe.safe_eval(rule.conditions, None, ctx)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Commission Rule condition eval failed")
                apply_rule = False
        if not apply_rule:
            continue
        # compute base amount
        base_value = float(opp.get("system_size_kw") or 0)
        if rule.is_percentage:
            base_amount = (float(rule.value) / 100.0) * base_value * 1000
        else:
            base_amount = float(rule.value or 0)

        # If splits configured, create one Commission Record per split
        if getattr(rule, 'splits', None):
            for s in rule.splits:
                try:
                    share = 0.0
                    if s.get('share_percentage'):
                        share = (float(s.share_percentage) / 100.0) * base_amount
                    elif s.get('share_amount'):
                        share = float(s.share_amount)
                    cr = frappe.get_doc({
                        "doctype": "Commission Record",
                        "title": f"{opportunity_name} - {rule.rule_name}",
                        "user": s.user,
                        "role": rule.role,
                        "opportunity": opportunity_name,
                        "customer": opp.customer,
                        "project": opp.get('project'),
                        "commission_amount": share,
                        "status": "Pending",
                        "audit_log": f"Created by {frappe.session.user}"
                    }).insert(ignore_permissions=True)
                    created.append(cr.name)
                except Exception:
                    frappe.log_error(frappe.get_traceback(), 'Commission split creation failed')
        else:
            cr = frappe.get_doc({
                "doctype": "Commission Record",
                "title": f"{opportunity_name} - {rule.rule_name}",
                "user": frappe.session.user if rule.role == 'Setter' else rule.role,
                "role": rule.role,
                "opportunity": opportunity_name,
                "customer": opp.customer,
                "project": opp.get('project'),
                "commission_amount": base_amount,
                "status": "Pending",
                "audit_log": f"Created by {frappe.session.user}"
            }).insert(ignore_permissions=True)
            created.append(cr.name)
    frappe.db.commit()
    return created

def on_sales_order_submit(doc, method=None):
    # when Sales Order is submitted create/payable commissions or mark
    try:
        # for any related opportunity create commissions if missing
        if doc.get('opportunity'):
            generate_commissions_for_opportunity(doc.opportunity, trigger='sales_order')
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'Commission generation on SO failed')


@frappe.whitelist()
def approve_commission(name):
    """Approve a single Commission Record. Accountant-only."""
    if not frappe.has_role('Accountant') and not frappe.has_role('Administrator'):
        frappe.throw('Only users with Accountant role can approve commissions')
    doc = frappe.get_doc('Commission Record', name)
    if doc.status != 'Pending':
        frappe.throw('Only Pending commissions can be approved')
    doc.status = 'Approved'
    doc.approval_by = frappe.session.user
    # append audit
    doc.audit_log = (doc.audit_log or '') + f"[{frappe.utils.now()}] Approved by {frappe.session.user}\n"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {'status':'ok', 'name': doc.name}
