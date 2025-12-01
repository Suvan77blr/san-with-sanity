#!/usr/bin/env python3
"""
Main entry point for the Erasure Coding Simulator.

This script initializes and runs the complete simulation comparing
Reed-Solomon (RS) vs Local Reconstruction Codes (LRC).
"""

# from core.simulator import Simulator
# from core.simulator_METRICs_GENERATOR import Simulator as SimulatorMETRICsGENERATOR
from core.scenario_simulator import ScenarioRunner
from config.scenarios import SCENARIOS
import json, os

def run_scenarios():
    runner = ScenarioRunner(SCENARIOS)
    results = runner.run()

    # print("\nAll Scenario Results :-")
    # for idx, res in enumerate(results, 1):
    #     print(f"\n--- Scenario {idx} Summary ---")
    #     print(res)
    print(f"Got results of {len(results)} tests!")
    return results


def main():
    """
    Main function that orchestrates the simulation.
    """
    # Create and run the simulator
    # simulator = Simulator()
    # simulator.run_simulation(
    #     "We have ceased to be Men,\nA generation of weaklings.\n\nIn the name of equality,\nWe have long lost chivalry,\nBirthing a hateful mentality,"
    # )

    # Uncomment to run the metrics generator simulator.
    # simulator_metrics_generator = SimulatorMETRICsGENERATOR()
    # simulator_metrics_generator.run_simulation(
    #     "We have ceased to be Men,\nA generation of weaklings.\n\nIn the name of equality,\nWe have long lost chivalry,\nBirthing a hateful mentality,"
    # )

    # Create and run the scenario simulator
    run_scenarios()


if __name__ == "__main__":
    main()
