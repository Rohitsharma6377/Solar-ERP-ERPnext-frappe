import frappe

def execute(filters=None):
    filters = filters or {}
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    conditions = ""
    args = {}
    if from_date:
        conditions += " AND cr.creation >= %(from_date)s"
        args['from_date'] = from_date
    if to_date:
        conditions += " AND cr.creation <= %(to_date)s"
        args['to_date'] = to_date

    data = frappe.db.sql(f"""
        select cr.user, cr.status, sum(cr.commission_amount) as total
        from `tabCommission Record` cr
        where 1=1 {conditions}
        group by cr.user, cr.status
    """, args, as_dict=1)

    # pivot into per-user rows
    result = {}
    for row in data:
        u = row['user']
        result.setdefault(u, {'user': u, 'pending': 0.0, 'approved': 0.0, 'payable': 0.0, 'paid': 0.0})
        status = row['status'].lower()
        result[u].setdefault(status, 0.0)
        result[u][status] += row['total']

    return list(result.values())
