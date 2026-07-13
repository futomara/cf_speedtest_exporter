import unittest

from exporter import flatten_metrics


class ExporterTests(unittest.TestCase):
    def test_flatten_metrics_recurses_and_normalizes_keys(self):
        payload = {
            "download_mbps": 100.5,
            "latency_ms": 20,
            "server": {"name": "nyc", "distance_km": 12},
            "results": [{"jitter_ms": 2.5}],
        }

        metrics = flatten_metrics(payload)

        self.assertEqual(metrics["cf_speedtest_download_mbps"], 100.5)
        self.assertEqual(metrics["cf_speedtest_latency_ms"], 20)
        self.assertEqual(metrics["cf_speedtest_server_distance_km"], 12)
        self.assertEqual(metrics["cf_speedtest_results_0_jitter_ms"], 2.5)


if __name__ == "__main__":
    unittest.main()
