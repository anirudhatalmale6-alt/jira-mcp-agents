import json
import os
import boto3


class JiraMCPClient:
    """Jira MCP client that communicates through Bedrock Agent Gateway."""

    def __init__(self, gateway_id=None, region=None, user_oid=None):
        self.gateway_id = gateway_id or os.getenv("BEDROCK_GATEWAY_ID", "<your-gateway-identifier>")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.user_oid = user_oid or os.getenv("ENTRA_USER_OID", "<entra-object-id>")
        self.client = boto3.client("bedrock-agentcore-runtime", region_name=self.region)

    def _invoke(self, tool_name, arguments):
        response = self.client.invoke_gateway(
            gatewayIdentifier=self.gateway_id,
            payload={
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            },
            sessionAttributes={
                "user_oid": self.user_oid
            }
        )
        return json.loads(response["body"].read()) if hasattr(response.get("body", ""), "read") else response

    def search_issues(self, jql, max_results=10):
        return self._invoke("search_issues", {
            "jql": jql,
            "max_results": max_results
        })

    def get_issue(self, issue_key):
        return self._invoke("get_issue", {
            "issue_key": issue_key
        })

    def create_issue(self, project_key, issue_type, summary, description, **fields):
        args = {
            "project_key": project_key,
            "issue_type": issue_type,
            "summary": summary,
            "description": description
        }
        args.update(fields)
        return self._invoke("create_issue", args)

    def update_issue_status(self, issue_key, status):
        return self._invoke("update_issue_status", {
            "issue_key": issue_key,
            "status": status
        })

    def add_comment(self, issue_key, comment):
        return self._invoke("add_comment", {
            "issue_key": issue_key,
            "comment": comment
        })
