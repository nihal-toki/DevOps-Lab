import contextlib
import io
import unittest
from unittest.mock import patch
from prometheus_client import REGISTRY
from delivery_monitoring import delivery_metrics as metrics
from run_metrics import ScenarioRandom

class DeliveryMetricsTest(unittest.TestCase):
    def sample(self, name):
        return REGISTRY.get_sample_value(name)

    def simulate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            metrics.simulate_delivery()

    def test_counts_and_summary(self):
        before = self.sample('average_delivery_time_count')
        before_sum = self.sample('average_delivery_time_sum')
        with patch.object(metrics.random, 'randint', side_effect=[12, 8, 40]), patch.object(metrics.random, 'uniform', return_value=25):
            self.simulate()
        self.assertEqual(self.sample('total_deliveries'), 60)
        self.assertEqual(self.sample('pending_deliveries'), 12)
        self.assertEqual(self.sample('on_the_way_deliveries'), 8)
        self.assertEqual(self.sample('average_delivery_time_count'), before + 1)
        self.assertEqual(self.sample('average_delivery_time_sum'), before_sum + 25)

    def test_normal_ranges(self):
        with patch.object(metrics, 'random', ScenarioRandom('normal')):
            for _ in range(20):
                self.simulate()
                self.assertTrue(10 <= self.sample('pending_deliveries') <= 20)
                self.assertTrue(5 <= self.sample('on_the_way_deliveries') <= 20)
                delivered = self.sample('total_deliveries') - self.sample('pending_deliveries') - self.sample('on_the_way_deliveries')
                self.assertTrue(30 <= delivered <= 70)

    def test_high_pending(self):
        generator = ScenarioRandom('high_pending')
        for _ in range(30):
            self.assertTrue(50 <= generator.randint(10, 20) <= 100)
            self.assertTrue(5 <= generator.randint(5, 20) <= 20)
            self.assertTrue(15 <= generator.uniform(15, 45) <= 45)

    def test_controlled_slow(self):
        generator = ScenarioRandom('high_pending_slow')
        for _ in range(30):
            self.assertTrue(50 <= generator.randint(10, 20) <= 100)
            self.assertTrue(35 <= generator.uniform(15, 45) <= 45)
        with self.assertRaises(ValueError):
            ScenarioRandom('unknown')

if __name__ == '__main__':
    unittest.main(verbosity=2)
