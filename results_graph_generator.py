import json
import os
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = "results"

def load_all_results():
    """Load all scenario JSON files from results/"""
    scenario_files = sorted([
        f for f in os.listdir(RESULTS_DIR)
        if f.endswith(".json") and f.startswith("scenario_")
    ])

    all_data = []
    for file in scenario_files:
        path = os.path.join(RESULTS_DIR, file)
        with open(path, "r") as f:
            data = json.load(f)
            data["scenario_id"] = int(file.replace("scenario_", "").replace(".json", ""))
            all_data.append(data)

    return all_data


def generate_graphs():
    results = load_all_results()

    scenario_ids = [d["scenario_id"] for d in results]
    
    # Extract metrics across all scenarios
    rs_eff = [d["rs_metrics"]["bandwidth_efficiency"] for d in results]
    lrc_eff = [d["lrc_metrics"]["bandwidth_efficiency"] for d in results]

    rs_frag = [d["rs_metrics"]["fragments_accessed"] for d in results]
    lrc_frag = [d["lrc_metrics"]["fragments_accessed"] for d in results]

    rs_xor = [d["rs_metrics"]["xor_operations"] for d in results]
    lrc_xor = [d["lrc_metrics"]["xor_operations"] for d in results]

    rs_mul = [d["rs_metrics"]["multiplication_operations"] for d in results]
    lrc_mul = [d["lrc_metrics"]["multiplication_operations"] for d in results]

    rs_time = [d["rs_metrics"]["recovery_time"] for d in results]
    lrc_time = [d["lrc_metrics"]["recovery_time"] for d in results]

    # ---------------------------------------------------------
    # 1. Bandwidth Efficiency
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(scenario_ids, rs_eff, marker='o', label="RS Efficiency")
    plt.plot(scenario_ids, lrc_eff, marker='o', label="LRC Efficiency")
    plt.xlabel("Scenario ID")
    plt.ylabel("Efficiency (%)")
    plt.title("Bandwidth Efficiency Across Scenarios")
    plt.legend()
    plt.grid(True)
    plt.savefig("bandwidth_efficiency_compare.png")
    plt.close()

    # ---------------------------------------------------------
    # 2. Fragments Accessed
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(scenario_ids, rs_frag, marker='o', label="RS Fragments")
    plt.plot(scenario_ids, lrc_frag, marker='o', label="LRC Fragments")
    plt.xlabel("Scenario ID")
    plt.ylabel("Fragments Accessed")
    plt.title("Fragments Accessed Across Scenarios")
    plt.legend()
    plt.grid(True)
    plt.savefig("fragments_accessed_compare.png")
    plt.close()

    # ---------------------------------------------------------
    # 3. XOR Operations
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(scenario_ids, rs_xor, marker='o', label="RS XOR Ops")
    plt.plot(scenario_ids, lrc_xor, marker='o', label="LRC XOR Ops")
    plt.xlabel("Scenario ID")
    plt.ylabel("XOR Operations")
    plt.title("XOR Operations Across Scenarios")
    plt.legend()
    plt.grid(True)
    plt.savefig("xor_operations_compare.png")
    plt.close()

    # ---------------------------------------------------------
    # 4. Multiplication Operations
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(scenario_ids, rs_mul, marker='o', label="RS Multiplications")
    plt.plot(scenario_ids, lrc_mul, marker='o', label="LRC Multiplications")
    plt.xlabel("Scenario ID")
    plt.ylabel("GF(256) Multiplications")
    plt.title("GF(256) Multiplication Ops Across Scenarios")
    plt.legend()
    plt.grid(True)
    plt.savefig("multiplication_operations_compare.png")
    plt.close()

    # ---------------------------------------------------------
    # 5. Recovery Time
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(scenario_ids, rs_time, marker='o', label="RS Recovery Time")
    plt.plot(scenario_ids, lrc_time, marker='o', label="LRC Recovery Time")
    plt.xlabel("Scenario ID")
    plt.ylabel("Time (ms)")
    plt.title("Recovery Time Across Scenarios")
    plt.legend()
    plt.grid(True)
    plt.savefig("recovery_time_compare.png")
    plt.close()

    print("Graphs generated successfully!")


if __name__ == "__main__":
    generate_graphs()
