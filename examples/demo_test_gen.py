"""Demo: Web Test Generation Agent + Jira MCP via Bedrock Agent Gateway.

Shows the full workflow:
1. Fetch test case tickets from Jira
2. Extract test steps from ticket descriptions
3. Post generated script references back to tickets
4. Create test execution ticket
"""

from src.jira_mcp_client import JiraMCPClient
from src.test_gen_jira import TestGenJiraIntegration


def main():
    jira = JiraMCPClient(
        gateway_id="<your-gateway-identifier>",
        region="us-east-1",
        user_oid="<entra-object-id>"
    )
    test_gen = TestGenJiraIntegration(jira, project_key="QA")

    # 1. Fetch test cases ready for automation
    print("=== Fetching test cases from Jira ===")
    test_cases = test_gen.bulk_generate_from_jira(
        sprint="Sprint 24",
        component="Checkout"
    )
    print(f"Found {len(test_cases)} test cases ready for automation")

    for tc in test_cases:
        print(f"\n  {tc['ticket_key']}: {tc['summary']}")
        print(f"  Priority: {tc['priority']}")
        print(f"  Steps:")
        for step in tc["steps"]:
            print(f"    {step['step_number']}. [{step['type']}] {step['text']}")

    # 2. Get test steps from a specific ticket
    print("\n=== Getting test steps from QA-101 ===")
    test_data = test_gen.get_test_steps("QA-101")
    print(f"Ticket: {test_data['summary']}")
    print(f"Steps: {len(test_data['steps'])}")

    # 3. Post generated script reference back to ticket
    print("\n=== Posting generated script references ===")
    generated_scripts = [
        ("QA-101", "Playwright", "tests/specs/checkout-flow.spec.ts"),
        ("QA-101", "k6", "k6/checkout-load-test.js"),
        ("QA-102", "Playwright", "tests/specs/login-flow.spec.ts"),
        ("QA-103", "Playwright", "tests/specs/registration.spec.ts"),
    ]

    for ticket_key, framework, script_path in generated_scripts:
        test_gen.post_generated_script(ticket_key, framework, script_path)
        print(f"  {ticket_key} -> {framework}: {script_path}")

    # 4. Update automation status
    print("\n=== Updating automation status ===")
    automated_tickets = ["QA-101", "QA-102", "QA-103"]
    for ticket_key in automated_tickets:
        test_gen.update_automation_status(ticket_key, status="Automated")
        print(f"  {ticket_key} -> Automated")

    # 5. Create test execution ticket
    print("\n=== Creating test execution ticket ===")
    result = test_gen.create_test_execution_ticket(automated_tickets)
    print(f"Created: {result.get('key')}")


if __name__ == "__main__":
    main()
