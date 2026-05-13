import os
import json
from datetime import datetime


async def export_job(job_data: dict, audit_logs: list[dict], output_dir: str = "./data/exports") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = job_data.get("id", "unknown")
    base = os.path.join(output_dir, f"job_{job_id}_{timestamp}")
    os.makedirs(base, exist_ok=True)

    report = {
        "job": job_data,
        "audit_logs": audit_logs,
        "exported_at": datetime.now().isoformat(),
    }
    report_path = os.path.join(base, "legal_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return {
        "export_path": base,
        "report_path": report_path,
        "formats": ["json"],
    }
