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
        "Hello, World! This is a test message for erasure coding simulation. Local Reconstruction Codes (LRC) are a simplified Azure-like variant. Hai Bye Good Night and sleep now. Shreyas Nagabhushan is a good boy."
    )

if __name__ == "__main__":
    main()
