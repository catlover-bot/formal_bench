from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("canonize_pred_with_style.py")), run_name="__main__")
