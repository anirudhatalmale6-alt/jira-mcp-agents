"""Demo: Performance Review Agent + Jira MCP via Bedrock Agent Gateway.

Shows the full workflow:
1. Scan code and collect performance findings
2. Create Jira defect tickets for each finding
3. Link defects to the source story
4. Post scan summary as a comment
"""

from src.jira_mcp_client import JiraMCPClient
from src.perf_review_jira import PerfReviewJiraIntegration


def main():
    jira = JiraMCPClient(
        gateway_id="<your-gateway-identifier>",
        region="us-east-1",
        user_oid="<entra-object-id>"
    )
    perf_review = PerfReviewJiraIntegration(jira, project_key="PERF")

    # Sample findings from the Performance Review Agent
    findings = [
        {
            "title": "N+1 Query in OrderService.getOrdersWithItems()",
            "severity": "CRITICAL",
            "category": "I/O",
            "file": "src/services/OrderService.java",
            "line": "45",
            "issue": "Each order triggers a separate DB query to fetch items. "
                     "With 1000 orders, this generates 1001 queries.",
            "impact": "Response time grows linearly with order count. "
                      "At 500+ orders, endpoint exceeds 5s SLA.",
            "current_code": (
                "for (Order order : orders) {\n"
                "    List<Item> items = itemRepo.findByOrderId(order.getId());\n"
                "    order.setItems(items);\n"
                "}"
            ),
            "recommended_fix": (
                "@Query(\"SELECT o FROM Order o JOIN FETCH o.items\")\n"
                "List<Order> findAllWithItems();"
            ),
            "estimated_impact": "Reduces query count from O(n) to O(1)",
        },
        {
            "title": "Unbounded Cache in ProductCatalog",
            "severity": "HIGH",
            "category": "MEMORY",
            "file": "src/services/ProductCatalog.java",
            "line": "23",
            "issue": "HashMap used as cache with no eviction policy. "
                     "Grows indefinitely under sustained load.",
            "impact": "Memory usage increases over time, eventually causing OOM.",
            "current_code": (
                "private static Map<String, Product> cache = new HashMap<>();"
            ),
            "recommended_fix": (
                "private static Map<String, Product> cache = \n"
                "    new LinkedHashMap<>(1000, 0.75f, true) {\n"
                "        protected boolean removeEldestEntry(Map.Entry e) {\n"
                "            return size() > 1000;\n"
                "        }\n"
                "    };"
            ),
            "estimated_impact": "Caps memory at ~1000 entries, prevents OOM under sustained load",
        },
        {
            "title": "Sequential API Calls in DashboardController",
            "severity": "MEDIUM",
            "category": "NETWORK",
            "file": "src/controllers/DashboardController.ts",
            "line": "18",
            "issue": "Three independent API calls made sequentially with await. "
                     "Total latency = sum of all three.",
            "impact": "Dashboard load time is 3x slower than necessary.",
            "current_code": (
                "const users = await userService.getActive();\n"
                "const orders = await orderService.getRecent();\n"
                "const metrics = await metricsService.getSummary();"
            ),
            "recommended_fix": (
                "const [users, orders, metrics] = await Promise.all([\n"
                "    userService.getActive(),\n"
                "    orderService.getRecent(),\n"
                "    metricsService.getSummary(),\n"
                "]);"
            ),
            "estimated_impact": "Reduces dashboard load from ~3s to ~1s (parallel execution)",
        },
    ]

    # 1. Create defect tickets for each finding
    print("=== Creating performance defect tickets ===")
    source_ticket = "PERF-456"
    created = perf_review.create_defects_from_scan(findings, source_ticket=source_ticket)
    for ticket_key in created:
        print(f"  Created: {ticket_key}")

    # 2. Post scan summary to the source ticket
    print(f"\n=== Posting scan summary to {source_ticket} ===")
    scan_results = {"findings": findings}
    perf_review.add_scan_summary(source_ticket, scan_results)
    print("Summary posted")

    # 3. Search for open perf defects
    print("\n=== Searching open performance defects ===")
    open_defects = perf_review.search_open_perf_defects()
    for issue in open_defects.get("issues", []):
        print(f"  {issue['key']}: {issue['fields']['summary']}")

    # 4. Close a defect after fix verification
    print("\n=== Closing resolved defect ===")
    perf_review.close_defect(
        "PERF-789",
        "Fixed: Replaced HashMap with bounded LRU cache. "
        "Verified memory stays stable under 24h load test."
    )
    print("Defect closed")


if __name__ == "__main__":
    main()
