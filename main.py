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
    simulator.run_simulation()

if __name__ == "__main__":
    main()
