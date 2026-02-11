frappe.ui.form.on('Commission Record', {
    refresh: function(frm) {
        // Make key fields read-only for non-accountants when status is Approved/Payable/Paid
        const accountant = frappe.user.has_role('Accountant') || frappe.user.has_role('Administrator');
        const locked_statuses = ['Approved','Payable','Paid'];

        if (!accountant && locked_statuses.includes(frm.doc.status)) {
            ['user','role','opportunity','commission_amount','status'].forEach(function(f){
                frm.set_df_property(f, 'read_only', 1);
            });
        } else {
            ['user','role','opportunity','commission_amount','status'].forEach(function(f){
                frm.set_df_property(f, 'read_only', 0);
            });
        }

        // Add Approve button for Accountants when status is Pending
        if (accountant && frm.doc.status === 'Pending') {
            frm.add_custom_button(__('Approve'), function() {
                frappe.confirm(
                    __('Approve this commission record?'),
                    function() {
                        frappe.call({
                            method: 'solar_erp.api.commission.approve_commission',
                            args: {name: frm.doc.name},
                            freeze: true,
                            callback: function(r) {
                                if(!r.exc) {
                                    frm.reload_doc();
                                    frappe.msgprint(__('Commission approved'));
                                }
                            }
                        });
                    }
                );
            }, __('Actions'));
        }
    }
});
