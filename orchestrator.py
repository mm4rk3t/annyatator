import yaml
import json
from runners.ultralytics import run_ultralytics
from runners.yolonas import run_yolonas
from runners.darknet import run_darknet
from pathlib import Path

def load_config(path="configs/sweep.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()
    dataset = cfg["dataset"]
    results = {}

    print("[*] Running Ultralytics...")
    results["ultralytics"] = run_ultralytics(cfg["ultralytics"], dataset)

    print("[*] Running YoloNAS...")
    results["yolonas"] = run_yolonas(cfg["yolonas"], dataset)

    print("[*] Running Darknet...")
    results["darknet"] = run_darknet(cfg["darknet"], dataset)

    Path("results").mkdir(exist_ok=True)
    with open("results/summary.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[✓] Sweep complete. Results saved to results/summary.json")

if __name__ == "__main__":
    main()