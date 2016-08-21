import unittest
import mock
import cloud_lights

class CloudLightsTests(unittest.TestCase):
    def setUp(self):
        self.lights = cloud_lights.CloudLights(10)

        # mock shuffle so it doesn't do anything
        self.time_patcher = mock.patch("time.time")
        self.time_mock = self.time_patcher.start()

    def tearDown(self):
        self.time_patcher.stop()

    def testInterpolateSimple(self):
        self.assertEquals(
            (0, 0, 255),
            self.lights.colorInterpolate((0, 0, 255), (0, 0, 255), 0.5)
        )

        self.assertEquals(
            (0, 0, 255),
            self.lights.colorInterpolate((0, 0, 255), (255, 0, 0), 0)
        )

        self.assertEquals(
            (255, 0, 0),
            self.lights.colorInterpolate((0, 0, 255), (255, 0, 0), 1.0)
        )
