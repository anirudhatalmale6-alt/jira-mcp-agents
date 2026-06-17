"""Estimation Agent + Jira MCP Integration.

Demonstrates:
- Reading PET tickets from Jira via MCP
- Fetching HLD attachment references from linked tickets
- Posting estimation reports as Jira comments
- Creating new PET estimation tickets
"""

from .jira_mcp_client import JiraMCPClient


class EstimationJiraIntegration:
    """Connects the PERF Estimation Agent with Jira PET tickets via MCP."""

    def __init__(self, jira: JiraMCPClient, project_key="PERF"):
        self.jira = jira
        self.project_key = project_key

    def find_pet_tickets(self, status=None, max_results=10):
        """Search for PET estimation tickets."""
        jql = f'project = {self.project_key} AND issuetype = "Estimate"'
        if status:
            jql += f' AND status = "{status}"'
        return self.jira.search_issues(jql, max_results)

    def get_pet_ticket(self, ticket_key):
        """Fetch a specific PET ticket with all fields."""
        return self.jira.get_issue(ticket_key)

    def find_linked_hld(self, ticket_key):
        """Find HLD document reference from a linked ticket.

        Looks for linked requirements or story tickets that may
        contain HLD attachments.
        """
        issue = self.jira.get_issue(ticket_key)
        linked_keys = []

        links = issue.get("fields", {}).get("issuelinks", [])
        for link in links:
            if "outwardIssue" in link:
                linked_keys.append(link["outwardIssue"]["key"])
            if "inwardIssue" in link:
                linked_keys.append(link["inwardIssue"]["key"])

        hld_references = []
        for key in linked_keys:
            linked_issue = self.jira.get_issue(key)
            attachments = linked_issue.get("fields", {}).get("attachment", [])
            for att in attachments:
                filename = att.get("filename", "").lower()
                if "hld" in filename or filename.endswith(".docx"):
                    hld_references.append({
                        "ticket": key,
                        "filename": att.get("filename"),
                        "url": att.get("content"),
                        "size": att.get("size")
                    })

        return hld_references

    def post_estimation_report(self, ticket_key, report):
        """Post the estimation report as a comment on the PET ticket."""
        comment = f"PERF Estimation Report (AI-Generated)\n\n{report}"
        return self.jira.add_comment(ticket_key, comment)

    def create_pet_ticket(self, project_name, estimation_data):
        """Create a new PET estimation ticket in Jira."""
        summary = f"PET Estimation - {project_name}"

        description_lines = [
            f"Project: {project_name}",
            f"Project Size: {estimation_data.get('project_size', 'N/A')}",
            f"Estimation Phase: +/- 10%",
            "",
            "PERF Activity Breakdown:",
            "-" * 60,
        ]

        for activity in estimation_data.get("activities", []):
            description_lines.append(
                f"  {activity['name']:<28} {activity['complexity']:<12} "
                f"{activity['time_days']:<10} x{activity['units']:<6} = {activity['total_days']:.2f} PD"
            )

        description_lines.extend([
            "-" * 60,
            f"Total (Before Efficiency): {estimation_data.get('total_pd_before', 0):.2f} PD",
            f"Efficiency Saving (19%): {estimation_data.get('efficiency_saving', 0):.2f} PD",
            f"Total (After Efficiency): {estimation_data.get('total_pd_after', 0):.2f} PD",
            f"Cost @ $250/PD: ${estimation_data.get('total_cost', 0):,.2f}",
        ])

        description = "\n".join(description_lines)

        return self.jira.create_issue(
            project_key=self.project_key,
            issue_type="Estimate",
            summary=summary,
            description=description
        )

    def update_pet_status(self, ticket_key, status):
        """Update PET ticket status (e.g., Draft -> Reviewed -> Approved)."""
        return self.jira.update_issue_status(ticket_key, status)
