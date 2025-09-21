import time
from pathlib import Path
from ultralytics import YOLO

def run_ultralytics(cfg, dataset):
    print("run_ultralytics")
    run_id = f"ultralytics_{int(time.time())}"
    outdir = Path("results/runs") / run_id
    outdir.mkdir(parents=True, exist_ok=True)

    # Load model
    model = YOLO(cfg["model"])

    # Start training
    results = model.train(
        data=dataset,
        epochs=cfg["epochs"],
        imgsz=cfg["imgsz"],
        project=str(outdir.parent),  # parent folder (results/runs)
        name=outdir.name,            # subfolder (results/runs/ultralytics_TIMESTAMP)
        exist_ok=True                # allow overwriting
    )

    # Return summary info
    return {
        "id": run_id,
        "results_dir": str(outdir),
        "best_model": str(outdir / "weights" / "best.pt")
    }
