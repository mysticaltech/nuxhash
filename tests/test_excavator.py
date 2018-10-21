import unittest
from time import sleep

import nuxhash.settings
from nuxhash.devices.nvidia import enumerate_devices as nvidia_devices
from nuxhash.download.downloads import make_miners
from nuxhash.miners.excavator import Excavator
from tests import get_test_devices


devices = nvidia_devices()


@unittest.skipIf(len(devices) == 0, 'requires an nvidia graphics card')
class TestExcavator(unittest.TestCase):

    def setUp(self):
        self.configdir = nuxhash.settings.DEFAULT_CONFIGDIR
        self.settings = nuxhash.settings.DEFAULT_SETTINGS
        self.settings['nicehash']['wallet'] = '3Qe7nT9hBSVoXr8rM2TG6pq82AmLVKHy23'
        self.device = devices[0]

        self.excavator = Excavator(self.configdir)
        self.excavator.settings = nuxhash.settings.DEFAULT_SETTINGS
        self.equihash = next(a for a in self.excavator.algorithms
                             if a.algorithms == ['equihash'])
        self.neoscrypt = next(a for a in self.excavator.algorithms
                              if a.algorithms == ['neoscrypt'])

        make_miners(self.configdir)
        self.excavator.load()

    def tearDown(self):
        self.excavator.unload()

    def _get_workers(self):
        response = self.excavator.server.send_command('worker.list', [])
        def algorithms(worker): return [a['name'] for a in worker['algorithms']]
        return [{ 'device_uuid': w['device_uuid'],
                  'algorithms': algorithms(w) } for w in response['workers']]

    def _get_algorithms(self):
        response = self.excavator.server.send_command('algorithm.list', [])
        return [a['name'] for a in response['algorithms']]

    def test_add_worker(self):
        self.equihash.set_devices([self.device])
        self.assertEqual(self._get_workers(), [{ 'device_uuid': self.device.uuid,
                                                 'algorithms': ['equihash'] }])

    def test_add_algorithm(self):
        self.equihash.set_devices([self.device])
        self.assertEqual(self._get_algorithms(), ['equihash'])

    def test_remove_worker(self):
        self.equihash.set_devices([self.device])
        sleep(1)
        self.equihash.set_devices([])
        self.assertEqual(self._get_workers(), [])

    def test_remove_algorithm(self):
        self.equihash.set_devices([self.device])
        sleep(1)
        self.equihash.set_devices([])
        self.assertEqual(self._get_algorithms(), [])

    def test_report_speed(self):
        self.equihash.set_devices([self.device])
        self.assertEqual(len(self.equihash.current_speeds()), 1)

    def test_switch_worker(self):
        self.equihash.set_devices([self.device])
        sleep(1)
        self.equihash.set_devices([])
        self.neoscrypt.set_devices([self.device])
        self.assertEqual(self._get_workers(), [{ 'device_uuid': self.device.uuid,
                                                 'algorithms': ['neoscrypt'] }])

    def test_switch_algorithm(self):
        self.equihash.set_devices([self.device])
        sleep(1)
        self.equihash.set_devices([])
        self.neoscrypt.set_devices([self.device])
        self.assertEqual(self._get_algorithms(), ['neoscrypt'])

    def test_simultaneous_worker(self):
        self.equihash.set_devices([self.device])
        sleep(1)
        self.neoscrypt.set_devices([self.device])
        sleep(1)
        self.equihash.set_devices([])
        self.assertEqual(self._get_workers(), [{ 'device_uuid': self.device.uuid,
                                                 'algorithms': ['neoscrypt'] }])

    def test_simultaneous_algorithm(self):
        self.equihash.set_devices([self.device])
        sleep(1)
        self.neoscrypt.set_devices([self.device])
        sleep(1)
        self.equihash.set_devices([])
        self.assertEqual(self._get_algorithms(), ['neoscrypt'])

    def test_set_twice(self):
        self.equihash.set_devices([self.device])
        sleep(1)
        self.equihash.set_devices([self.device])
        self.assertEqual(self._get_algorithms(), ['equihash'])

    def test_benchmark_mode(self):
        self.equihash.set_devices([self.device])
        sleep(1)
        self.equihash.benchmarking = True
        self.assertEqual(self._get_workers(), [{ 'device_uuid': self.device.uuid,
                                                 'algorithms': ['equihash'] }])

    def test_benchmark_stop(self):
        self.equihash.benchmarking = True
        self.equihash.set_devices([self.device])
        sleep(1)
        self.equihash.set_devices([])
        self.assertEqual(self._get_workers(), [])

    def test_bad_device(self):
        device = get_test_devices()[0]
        self.assertFalse(self.equihash.accepts(device))

    def test_set_bad_device(self):
        devices = get_test_devices()
        self.assertRaises(AssertionError,
                          lambda: self.equihash.set_devices(devices))


if __name__ == '__main__':
    unittest.main()

