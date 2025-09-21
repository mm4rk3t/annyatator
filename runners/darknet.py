import subprocess, os, time
from pathlib import Path

def run_darknet(cfg, dataset):
    """
    run_id = f"darknet_{int(time.time())}"
    outdir = Path("results/runs") / run_id
    outdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "./darknet", "detector", "train",
        cfg["data"], cfg["cfg"], cfg["weights"]
    ]

    env = dict(**os.environ)
    env["CUDA_VISIBLE_DEVICES"] = str(cfg.get("gpu", 0))

    log_file = outdir / "train.log"
    with open(log_file, "w") as f:
        subprocess.run(cmd, cwd=cfg["bin_dir"], env=env,
                       stdout=f, stderr=subprocess.STDOUT, text=True)

    return {"id": run_id, "log": str(log_file), "weights": str(outdir / "weights")}
    """