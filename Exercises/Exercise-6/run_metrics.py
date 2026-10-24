"""Run the preserved simulator with explicit, repeatable lab scenarios."""
import os
import random
import time
from delivery_monitoring import delivery_metrics as metrics

class ScenarioRandom(random.Random):
    def __init__(self, scenario):
        super().__init__()
        if scenario not in ('normal', 'high_pending', 'high_pending_slow'):
            raise ValueError('Unknown scenario: ' + scenario)
        self.scenario = scenario

    def randint(self, low, high):
        if (low, high) == (10, 20) and self.scenario != 'normal':
            low, high = 50, 100
        return super().randint(low, high)

    def uniform(self, low, high):
        if (low, high) == (15, 45) and self.scenario == 'high_pending_slow':
            low, high = 35, 45
        return super().uniform(low, high)

if __name__ == '__main__':
    scenario = os.environ.get('DELIVERY_SCENARIO', 'normal')
    metrics.random = ScenarioRandom(scenario)
    print('Delivery scenario:', scenario, flush=True)
    metrics.start_http_server(8000, addr='0.0.0.0')
    while True:
        metrics.simulate_delivery()
        time.sleep(1)
