import frappe
import requests
from frappe import _

def create_solargraf_project(opportunity_name):
    opp = frappe.get_doc("Opportunity", opportunity_name)
    settings = frappe.get_single("SolarGraf Settings")
    if not settings or not settings.enabled:
        frappe.log_error("SolarGraf disabled or not configured", "SolarGraf skipped")
        return
    if opp.get("solargraf_project_id"):
        return opp.solargraf_project_id

    payload = {
        "title": opp.subject or opp.name,
        "customer": opp.customer or opp.party_name,
        "system_size_kw": opp.get("system_size_kw"),
        "roof_type": opp.get("roof_type")
    }
    headers = {"Authorization": f"Bearer {settings.api_key}"} if settings.api_key else {}
    try:
        resp = requests.post(f"{settings.base_url.rstrip('/')}/projects", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        solargraf_id = data.get("id") or data.get("project_id")
        if solargraf_id:
            frappe.db.set_value("Opportunity", opp.name, "solargraf_project_id", solargraf_id)
            frappe.enqueue(method="solar_erp.api.solargraf.fetch_and_attach_pdf", opportunity=opp.name, solargraf_id=solargraf_id)
            return solargraf_id
    except Exception:
        frappe.log_error(frappe.get_traceback(), "SolarGraf API Error")
        # create a small failure record via a child table or a simple log (left minimal)
        raise

def fetch_and_attach_pdf(opportunity, solargraf_id):
    settings = frappe.get_single("SolarGraf Settings")
    if not settings or not settings.enabled:
        return
    url = f"{settings.base_url.rstrip('/')}/projects/{solargraf_id}/signed_proposal"
    headers = {"Authorization": f"Bearer {settings.api_key}"} if settings.api_key else {}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        fname = f"Signed_Proposal_{opportunity}.pdf"
        filedoc = frappe.get_doc({
            "doctype": "File",
            "file_name": fname,
            "is_private": 0,
            "attached_to_doctype": "Opportunity",
            "attached_to_name": opportunity
        })
        filedoc.save()
        # write file content
        _path = frappe.get_site_path('public', 'files', fname)
        with open(_path, 'wb') as f:
            f.write(r.content)
        frappe.db.set_value("Opportunity", opportunity, "signed_proposal_attachment", f"/files/{fname}")
        frappe.db.commit()
        opp = frappe.get_doc("Opportunity", opportunity)
        if opp.get("assigned_closer"):
            try:
                frappe.sendmail(recipients=[opp.assigned_closer], subject="Signed Proposal Attached", message=f"Signed proposal available for {opp.name}")
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Email send failed")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Fetch signed proposal failed")
        raise
