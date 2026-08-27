import asyncio
import httpx
from app.server import app

async def test_end_to_end_flow():
    print("=== Testing FastAPI App & LangGraph Multi-Agent System ===")
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Healthcheck
        res = await client.get("/health")
        print(f"1. Healthcheck: {res.status_code} -> {res.json()}")
        assert res.status_code == 200
        
        # 2. Trigger Multi-Agent Task (Finance + Comms flow)
        goal_payload = {
            "goal": "Generate draft invoice for client Acme Global and prepare email draft",
            "requester_role": "OWNER",
            "context": {}
        }
        res = await client.post("/api/v1/agents/run", json=goal_payload)
        print(f"\n2. Agent Task Run: {res.status_code}")
        task_data = res.json()
        print(f"Task ID: {task_data['task_id']}")
        print(f"Status: {task_data['status']}")
        print(f"Artifacts: {task_data['artifacts'].keys()}")
        print(f"Completed Steps: {len(task_data['steps'])}")
        for step in task_data['steps']:
            print(f"   - [{step['agent']}] -> {step['action']}")
        assert res.status_code == 200
        assert "invoice_draft" in task_data["artifacts"]
        
        # 3. Check Pending Approvals
        res = await client.get("/api/v1/approvals")
        approvals = res.json()
        print(f"\n3. Pending Approvals count: {len(approvals)}")
        assert len(approvals) > 0
        target_approval = approvals[0]
        print(f"Approval ID: {target_approval['id']}")
        print(f"Type: {target_approval['approval_type']}")
        print(f"Title: {target_approval['title']}")
        print(f"Status: {target_approval['status']}")
        
        # 4. Human-In-The-Loop Action: Approve the email/invoice draft
        action_payload = {
            "action": "APPROVE",
            "notes": "Approved by Owner Admin for client release"
        }
        res = await client.post(f"/api/v1/approvals/{target_approval['id']}/action", json=action_payload)
        print(f"\n4. Approval Action Response: {res.status_code} -> Status: {res.json()['status']}")
        assert res.status_code == 200
        assert res.json()["status"] == "APPROVED"
        
        # 5. Check Audit Logs
        res = await client.get("/api/v1/audit/logs")
        logs = res.json()
        print(f"\n5. Audit Trail Entries: {len(logs)}")
        for log in logs[:4]:
            print(f"   - [{log['actor_type']}:{log.get('agent_name') or log['actor_id']}] {log['action']} ({log['status']})")
        assert len(logs) > 0

    print("\n[SUCCESS] All End-to-End Verification Tests Passed Successfully!")

if __name__ == "__main__":
    asyncio.run(test_end_to_end_flow())
