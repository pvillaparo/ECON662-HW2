import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
LATEX_OUTPUT = ROOT / "results_table_pv.tex"
LATEX_COMPACT_OUTPUT = ROOT / "results_table_pv_compact.tex"

METHODS = [
    ("Qa_pv.ipynb", "Nested Fixed Point"),
    ("Qb_pv.ipynb", "Hotz and Miller"),
    ("Qc1_pv.ipynb", "Forward Simulation (Eq. 5)"),
    ("Qc2_pv.ipynb", "Forward Simulation (Eq. 6)-(7)"),
    ("Qd_pv.ipynb", "Linear Regression Approach"),
]


def notebook_text(path: Path) -> str:
    with path.open() as f:
        nb = json.load(f)

    chunks = []
    for cell in nb["cells"]:
        chunks.extend(cell.get("source", []))
        for out in cell.get("outputs", []):
            if out.get("output_type") == "stream":
                chunks.extend(out.get("text", []))
    return "".join(chunks)


def extract_last_float(pattern: str, text: str) -> float:
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if not matches:
        raise ValueError(f"Could not find pattern: {pattern}")
    return float(matches[-1])


def extract_runtime(text: str) -> tuple[float, float]:
    matches = re.findall(
        r"Comparable running time\s*=*\s*([0-9.]+)\s*(?:sec|seconds)\s*\(([0-9.]+)\s*ms\)",
        text,
        flags=re.MULTILINE,
    )
    if not matches:
        raise ValueError("Could not find comparable running time in notebook output.")
    sec, ms = matches[-1]
    return float(sec), float(ms)


def extract_common_rho(text: str) -> tuple[float, float, float]:
    rho0 = extract_last_float(r"rho0(?:_hat)?\s*\(?.*?\)?\s*=\s*([0-9.]+)", text)
    rho1 = extract_last_float(r"rho1(?:_hat)?\s*\(?.*?\)?\s*=\s*([0-9.]+)", text)
    sigma = extract_last_float(r"sigma_rho(?:_hat)?\s*\(?.*?\)?\s*=\s*([0-9.]+)", text)
    return rho0, rho1, sigma


def main() -> None:
    records = []
    for filename, method in METHODS:
        text = notebook_text(ROOT / filename)
        theta1 = extract_last_float(r"theta1(?:_hat)?\s*(?:\(.*?\))?\s*=\s*([0-9.]+)", text)
        theta2 = extract_last_float(r"theta2(?:_hat)?\s*(?:\(.*?\))?\s*=\s*([0-9.]+)", text)
        runtime_sec, runtime_ms = extract_runtime(text)
        records.append(
            {
                "Method": method,
                "theta1": theta1,
                "theta2": theta2,
                "Running Time": f"{runtime_sec:.4f} s ({runtime_ms:.2f} ms)",
                "running_time_sec": runtime_sec,
            }
        )

    summary_df = pd.DataFrame(records)

    report_rows = []
    for row in records:
        report_rows.extend(
            [
                {"Method": row["Method"], "Parameter": "theta1", "Paola": f"{row['theta1']:.4f}"},
                {"Method": row["Method"], "Parameter": "theta2", "Paola": f"{row['theta2']:.4f}"},
                {"Method": row["Method"], "Parameter": "Running Time", "Paola": row["Running Time"]},
            ]
        )
    report_df = pd.DataFrame(report_rows)

    rho0, rho1, sigma_rho = extract_common_rho(notebook_text(ROOT / "Qa_pv.ipynb"))
    compact_latex = summary_df[["Method", "theta1", "theta2", "Running Time"]].to_latex(
        index=False,
        escape=False,
        caption="Results obtained for Rust's Bus Problem using five estimation methods",
        label="tab:rust_bus_paola_compact",
    )
    report_latex = report_df.to_latex(
        index=False,
        escape=False,
        caption="Results obtained for Rust's Bus Problem using five estimation methods",
        label="tab:rust_bus_paola",
    )

    LATEX_COMPACT_OUTPUT.write_text(compact_latex)
    LATEX_OUTPUT.write_text(report_latex)

    print("Results obtained for Rust's Bus Problem using five estimation methods")
    print("Paola Gabriela Villa Paro")
    print()
    print("Comparable running time is measured from the start of each method-specific estimation block")
    print("until theta1 and theta2 are obtained, after common setup objects have been built.")
    print()
    print("Compact table")
    print(summary_df[["Method", "theta1", "theta2", "Running Time"]].to_markdown(index=False))
    print()
    print("Report-style table")
    print(report_df.to_markdown(index=False))
    print()
    print(
        "Common first-stage OLS estimates used in the dynamic-MLE notebooks: "
        f"rho0={rho0:.4f}, rho1={rho1:.4f}, sigma_rho={sigma_rho:.4f}"
    )
    print()
    print(f"Wrote compact LaTeX table to: {LATEX_COMPACT_OUTPUT.name}")
    print(f"Wrote report-style LaTeX table to: {LATEX_OUTPUT.name}")
    print()
    print("LaTeX table")
    print(report_latex)


if __name__ == "__main__":
    main()
