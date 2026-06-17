"""Demo: Estimation Agent + Jira MCP via Bedrock Agent Gateway.

Shows the full workflow:
1. Search for PET tickets in Jira
2. Fetch a PET ticket and find linked HLD documents
3. Post estimation report back to the ticket
4. Create a new PET estimation ticket
"""

from src.jira_mcp_client import JiraMCPClient
from src.estimation_jira import EstimationJiraIntegration


def main():
    jira = JiraMCPClient(
        gateway_id="<your-gateway-identifier>",
        region="us-east-1",
        user_oid="<entra-object-id>"
    )
    estimation = EstimationJiraIntegration(jira, project_key="PERF")

    # 1. Search for open PET tickets
    print("=== Searching for PET tickets ===")
    tickets = estimation.find_pet_tickets(status="Open")
    print(f"Found {len(tickets.get('issues', []))} PET tickets")

    # 2. Get a specific PET ticket and find linked HLD
    print("\n=== Fetching PET ticket details ===")
    ticket = estimation.get_pet_ticket("PERF-123")
    print(f"Ticket: {ticket.get('key')} - {ticket.get('fields', {}).get('summary')}")

    print("\n=== Finding linked HLD documents ===")
    hld_refs = estimation.find_linked_hld("PERF-123")
    for ref in hld_refs:
        print(f"  HLD: {ref['filename']} (from {ref['ticket']})")

    # 3. Post estimation report back to ticket
    print("\n=== Posting estimation report ===")
    sample_report = """
======================================================================
  PERF ESTIMATION REPORT - E-Commerce Platform
======================================================================

  Project Size     : MEDIUM
  In-Scope Items   : 12
  Use Cases        : 8
  Data Entities    : 5

----------------------------------------------------------------------
  PERF Activity             Complexity   Time(days)   Units    Total(days)
----------------------------------------------------------------------
  Analysis                  medium       1.50         2        3.00
  Assessment                medium       1.50         1        1.50
  Script Design             complex      4.00         6        24.00
  Planning                  medium       3.01         1        3.01
  Reporting                 medium       2.51         2        5.01
----------------------------------------------------------------------

  Total (Before Efficiency): 55.69 PD
  Total (After 19% Efficiency): 45.11 PD
  Cost @ $250/PD = $11,277.50
======================================================================
"""
    estimation.post_estimation_report("PERF-123", sample_report)
    print("Report posted as comment")

    # 4. Create a new PET estimation ticket
    print("\n=== Creating new PET ticket ===")
    estimation_data = {
        "project_size": "MEDIUM",
        "activities": [
            {"name": "Analysis", "complexity": "medium", "time_days": 1.50, "units": 2, "total_days": 3.00},
            {"name": "Script Design", "complexity": "complex", "time_days": 4.00, "units": 6, "total_days": 24.00},
            {"name": "Planning", "complexity": "medium", "time_days": 3.01, "units": 1, "total_days": 3.01},
        ],
        "total_pd_before": 55.69,
        "efficiency_saving": 10.58,
        "total_pd_after": 45.11,
        "total_cost": 11277.50,
    }
    result = estimation.create_pet_ticket("E-Commerce Platform", estimation_data)
    print(f"Created: {result.get('key')}")


if __name__ == "__main__":
    main()
