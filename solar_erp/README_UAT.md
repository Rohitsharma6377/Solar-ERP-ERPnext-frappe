# Solar ERP — UAT Checklist

This file contains UAT scenarios to validate the Solar ERP flows.

1) Lead → Opportunity flow
- Create a `Lead`, convert to `Opportunity` with solar fields populated (roof type, system size). Verify fields saved.

2) SolarGraf integration
- Configure `SolarGraf Settings` (enable, set API base URL and API key).
- Move `Opportunity` to configured stage. Verify SolarGraf project is created and `solargraf_project_id` is set. Verify signed proposal PDF attaches when available.

3) Opportunity → Project automation
- Move Opportunity to `Approved` or `Won`. Verify `Project` is created, `Project Manager` assigned, and Tasks created from `Task Template` or defaults.

4) Commission generation and approval
- Create `Commission Rule` (percentage and fixed); mark Opportunity as Won or submit Sales Order. Verify `Commission Record` entries created (including splits). Accountant approves a `Commission Record` and marks Payable.

5) Permissions
- Verify roles (`Setter`, `Designer`, `Closer`, `Project Manager`, `Accountant`) can only perform allowed actions. Try unauthorized actions and confirm blocked.

6) Reports
- Run `Commission by User` report for a date range and validate totals.

7) Error handling
- Simulate SolarGraf API failure (wrong base URL) and verify retries and logged errors.

Record results and notes during UAT.
