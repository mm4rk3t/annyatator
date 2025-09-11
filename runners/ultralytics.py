import subprocess, os, time
from pathlib import Path

def run_ultralytics(cfg, dataset):
    print("run_ultralytics")
    # run_id = f"ultralytics_{int(time.time())}"
    # outdir = Path("results/runs") / run_id
    # outdir.mkdir(parents=True, exist_ok=True)

    # cmd = [
    #    "python", "-m", "ultralytics", "train",
    #    f"model={cfg['model']}",
    #    f"data={dataset}",
    #    f"epochs={cfg['epochs']}",
    #    f"imgsz={cfg['imgsz']}"
    #]

    #log_file = outdir / "train.log"
    #with open(log_file, "w") as f:
    #    subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

    return {"id": run_id, "log": str(log_file), "weights": str(outdir / "weights")}