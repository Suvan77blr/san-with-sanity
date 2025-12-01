from config.constants import DEFAULT_CONFIG
from core.simulator_METRICs import Simulator
import copy, json, os

class ScenarioRunner:
    def __init__(self, scenarios):
        self.scenarios = scenarios



    def run(self):
        results = []
        os.makedirs("results", exist_ok = True)

        for i, scenario in enumerate(self.scenarios):
            config = copy.deepcopy(DEFAULT_CONFIG)
            config.update(scenario)

            self.validate_config(config=config)
            
            sim = Simulator(config, i)
            sim.run_simulation()
            results.append(sim.metrics_collector.get_metrics_summary())

            with open(f"results/scenario_{i}.json", "w") as f:
                json.dump(results[-1], f, indent=4)
            print(f"Written results to results/scenario_{i}.json file.")
        return results

    def validate_config(self, config):
        groups = config["LRC_K"] // config["LRC_GROUP_SIZE"]
        total = config["LRC_K"] + (groups * config["LRC_LOCAL_PARITY"]) + config["LRC_GLOBAL_PARITY"]
        if total > config["NUM_NODES"]:
            raise ValueError(
                f"[INVALID SCENARIO] LRC requires {total} fragments but NUM_NODES={config['NUM_NODES']}"
            )
        return