# Jira MCP Agents - Bedrock Agent Gateway Integration

This project demonstrates Jira MCP server integration with 3 performance engineering agents through AWS Bedrock Agent Gateway.

## Architecture

Agents -> Bedrock Agent Gateway (/mcp) -> Jira MCP Server -> Jira On-Premise

## Agents

- estimation-agent-jira.md - PERF estimation with Jira PET ticket read/write
- perf-review-agent-jira.md - Code review with automatic Jira defect creation
- web-test-gen-agent-jira.md - Test generation from Jira test case tickets

## Jira MCP Tools Available

- search_issues - JQL search
- get_issue - Fetch ticket details
- create_issue - Create tickets
- update_issue_status - Update status
- add_comment - Add comments

## Configuration

Gateway config in config/gateway_config.yaml. Replace placeholders:
- gateway_identifier: Your Bedrock Agent Gateway ID
- user_oid: Your Entra Object ID
- region: Your AWS region
