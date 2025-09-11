import subprocess, os, time
from pathlib import Path

def run_yolonas(cfg, dataset):
    run_id = f"yolonas_{int(time.time())}"
    outdir = Path("results/runs") / run_id
    outdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", "train.py",  # adjust to your YoloNAS entrypoint
        "--model", cfg["model"],
        "--data", dataset,
        "--epochs", str(cfg["epochs"]),
        "--img-size", str(cfg["imgsz"])
    ]

    log_file = outdir / "train.log"
    with open(log_file, "w") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

    return {"id": run_id, "log": str(log_file), "weights": str(outdir / "weights")}