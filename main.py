#!/usr/bin/env python3
"""
Main entry point for the Erasure Coding Simulator.

This script initializes and runs the complete simulation comparing
Reed-Solomon (RS) vs Local Reconstruction Codes (LRC).
"""

from core.simulator import Simulator

def main():
    """
    Main function that orchestrates the simulation.
    """
    # Create and run the simulator
    simulator = Simulator()
    simulator.run_simulation(
        "We have ceased to be Men,\nA generation of weaklings.\n\nIn the name of equality,\nWe have long lost chivalry,\nBirthing a hateful mentality,"
    )

if __name__ == "__main__":
    main()
