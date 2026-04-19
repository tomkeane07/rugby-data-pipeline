import json
import subprocess
from datetime import datetime
from pathlib import Path


def main() -> None:
    dbt_project_dir = Path("dbt/rugby_stats")
    profiles_dir = dbt_project_dir

    if not dbt_project_dir.exists():
        summary = {
            "run_finished": datetime.utcnow().isoformat() + "Z",
            "status": "skipped",
            "reason": "dbt project not initialized at dbt/rugby_stats",
        }
        summary_path = Path("data/raw/run_summaries") / f"run_dbt_summary_{datetime.utcnow().strftime('%Y%m%d')}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        print("[run_dbt] Skipped: dbt project not found at dbt/rugby_stats")
        print(f"[run_dbt] Wrote summary: {summary_path}")
        return

    build_cmd = [
        "dbt",
        "build",
        "--project-dir",
        str(dbt_project_dir),
        "--profiles-dir",
        str(profiles_dir),
    ]
    test_cmd = [
        "dbt",
        "test",
        "--project-dir",
        str(dbt_project_dir),
        "--profiles-dir",
        str(profiles_dir),
    ]

    print(f"[run_dbt] Running: {' '.join(build_cmd)}")
    build_result = subprocess.run(build_cmd, check=False)  # noqa: S603

    if build_result.returncode == 0:
        print(f"[run_dbt] Running: {' '.join(test_cmd)}")
        test_result = subprocess.run(test_cmd, check=False)  # noqa: S603
    else:
        test_result = subprocess.CompletedProcess(args=test_cmd, returncode=1)

    summary = {
        "run_finished": datetime.utcnow().isoformat() + "Z",
        "status": "success" if build_result.returncode == 0 and test_result.returncode == 0 else "failed",
        "build_return_code": build_result.returncode,
        "test_return_code": test_result.returncode,
        "project_dir": str(dbt_project_dir),
        "profiles_dir": str(profiles_dir),
    }

    summary_path = Path("data/raw/run_summaries") / f"run_dbt_summary_{datetime.utcnow().strftime('%Y%m%d')}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[run_dbt] Wrote summary: {summary_path}")

    if build_result.returncode != 0:
        raise SystemExit(build_result.returncode)
    if test_result.returncode != 0:
        raise SystemExit(test_result.returncode)


if __name__ == "__main__":
    main()
