# Jira MCP Agents

Performance engineering agents integrated with Jira through AWS Bedrock Agent Gateway MCP endpoint.

## Architecture

```
Claude Code Agent
    |
    v
Bedrock Agent Gateway (/mcp endpoint)
    |
    v
Jira MCP Server
    |
    v
Jira On-Premise
```

Authentication flows through Entra Object ID passed in sessionAttributes, allowing per-user access control.

## 3 Agents with Jira Integration

### 1. PERF Estimation Agent (Jira MCP)
- Reads PET tickets from Jira
- Finds linked HLD documents from related tickets
- Calculates effort across 11 PERF activities
- Posts estimation reports as Jira comments
- Creates new PET estimation tickets

### 2. Performance Review Agent (Jira MCP)
- Scans code for performance bottlenecks (6 categories)
- Creates Jira Bug tickets for each finding with severity mapping
- Links defects to source story/epic
- Posts scan summary as Jira comment

### 3. Web Test Generation Agent (Jira MCP)
- Reads test case descriptions from Jira tickets
- Extracts numbered test steps from ticket descriptions
- Generates Playwright/k6/Selenium/LoadRunner scripts
- Posts generated script paths back as Jira comments
- Updates ticket status to "Automated"

## Jira MCP Tools

| Tool | Description |
|------|-------------|
| search_issues | Search Jira issues using JQL queries |
| get_issue | Get a specific issue by key (e.g., PERF-123) |
| create_issue | Create a new issue (Bug, Estimate, Test Case, etc.) |
| update_issue_status | Transition issue status (Open -> Done, etc.) |
| add_comment | Add a comment to an issue |

## Setup

### 1. Configure Gateway

Edit `config/gateway_config.yaml` with your values:

```yaml
bedrock_gateway:
  gateway_identifier: "<your-gateway-id>"
  region: "us-east-1"

authentication:
  user_oid: "<your-entra-object-id>"
```

### 2. Set Environment Variables

```bash
export BEDROCK_GATEWAY_ID="<your-gateway-identifier>"
export AWS_REGION="us-east-1"
export ENTRA_USER_OID="<your-entra-object-id>"
```

### 3. Install Dependencies

```bash
pip install boto3
```

### 4. Use as Claude Code Agents

Copy the `.github/agents/` folder into your project:

```bash
mkdir -p .github/agents
cp .github/agents/*-jira.md your-project/.github/agents/
```

Open in VS Code with Claude Code extension, select the agent from the picker at the bottom.

### 5. Use Programmatically (Python)

```python
from src.jira_mcp_client import JiraMCPClient
from src.estimation_jira import EstimationJiraIntegration

jira = JiraMCPClient()
estimation = EstimationJiraIntegration(jira, project_key="PERF")

# Search PET tickets
tickets = estimation.find_pet_tickets(status="Open")

# Post estimation report
estimation.post_estimation_report("PERF-123", report_text)
```

## Project Structure

```
jira-mcp-agents/
  .github/agents/
    estimation-agent-jira.md      # Estimation agent with Jira MCP
    perf-review-agent-jira.md     # Perf review agent with Jira MCP
    web-test-gen-agent-jira.md    # Test gen agent with Jira MCP
  src/
    jira_mcp_client.py            # Bedrock Gateway MCP client
    estimation_jira.py            # Estimation + Jira integration
    perf_review_jira.py           # Perf review + Jira integration
    test_gen_jira.py              # Test gen + Jira integration
  config/
    gateway_config.yaml           # Gateway configuration
  examples/
    demo_estimation.py            # Estimation workflow demo
    demo_perf_review.py           # Perf review workflow demo
    demo_test_gen.py              # Test gen workflow demo
```

## Examples

### Estimation Agent - Read PET ticket and post report

```bash
python examples/demo_estimation.py
```

### Perf Review Agent - Create defect tickets from findings

```bash
python examples/demo_perf_review.py
```

### Web Test Gen Agent - Read test cases and generate scripts

```bash
python examples/demo_test_gen.py
```

## How the Gateway Call Works

```python
import boto3

bedrock = boto3.client("bedrock-agentcore-runtime", region_name="us-east-1")

response = bedrock.invoke_gateway(
    gatewayIdentifier="<your-gateway-id>",
    payload={
        "method": "tools/call",
        "params": {
            "name": "search_issues",
            "arguments": {
                "jql": "project = PERF AND status != Done",
                "max_results": 10
            }
        }
    },
    sessionAttributes={
        "user_oid": "<entra-object-id>"
    }
)
```

The gateway routes the MCP tool call to the Jira MCP server, which executes the operation against Jira on-premise and returns the result.
