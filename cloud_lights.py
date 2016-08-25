import random
import time
import math
import colorsys

RANDOM_TIME_FACTOR = 0.3
STORM_PROBABILITY = 0.5
LIGHTNING_PROBABILITY_PER_SEC = 0.2
RESTRIKE_PROBABILITES = [0.7, 0.4, 0.1]
LIGHTNING_STRIKE_MIN_SEC = 1
LIGHTNING_STRIKE_MAX_SEC = 3

STATE_TIMES = {
    "sunrise": 60 * 5,
    "day": 60 * 15,
    "sunset": 60 * 5,
    "night": 60 * 10,
    "storm": 60 * 10
    #"sunrise": 30,
    #"day": 30,
    #"sunset": 30,
    #"night": 30,
    #"storm": 30
}

STATE_COLORS = {
    "sunrise": [
        [(224, 173, 190), (120, 144, 180), (242, 224, 138), (228, 160, 157), (157, 181, 219)],

        # sunrise in south korea
        [(224, 123, 129), (243, 231, 109), (236, 202, 128), (232, 181, 124), (191, 129, 106)],

        # stephen bowler
        [(170, 125, 145), (90, 99, 132), (229, 154, 131), (208, 140, 137), (242, 232, 196), (29, 55, 80)],

        # Paul Aloe
        [(244, 233, 125), (244, 233, 125), (228, 157, 75), (226, 130, 80), (102, 81, 78)]
    ],
    "day": [
        [(203, 229, 239), (22, 79, 173), (132, 173, 229), (103, 200, 251)]
    ],
    "sunset": [
        # set to the sunrise palette
    ],
    "night": [
        [(40, 15, 54), (99, 43, 108), (200, 107, 152), (240, 159, 156), (255, 193, 160), (254, 156, 127)],
        [(19, 24, 98), (46, 68, 130), (84, 107, 171), (135, 136, 156), (190, 169, 222)],
    ],
    "storm": [
        #[(68, 91, 123), (170, 202, 240), (39, 56, 76)]
        # [(203, 229, 239), (22, 79, 173), (132, 173, 229), (103, 200, 251)]
        [(0, 0, 255)]
    ]
}
STATE_COLORS["sunset"] = STATE_COLORS["sunrise"]

random.seed(time.time())

LED_GAMMA_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255
]

class CloudLights(object):
    def __init__(self, numClouds):
        self.numClouds = numClouds
        self.state = "initial"

        self.state_time_start = 0
        self.state_time_end = 0

        self.color_array_last_state = []
        self.color_array_next_state = []

        self.lightningState = ["Initial"]

        # transition to sunrise, then to day to get the linear effects that we want
        self._stateTransition(force_choice="storm")
        self._stateTransition(force_choice="storm") # TODO: permastorm for testing

        self.lastTimeCalled = 0

    def _stateTransition(self, force_choice=None):
        if self.state == "initial":
            self.state = "sunrise"
        elif self.state == "sunrise":
            self.state = "storm" if random.random() < STORM_PROBABILITY else "day"
        elif self.state == "day":
            self.state = "storm" if random.random() < STORM_PROBABILITY else "sunset"
        elif self.state == "sunset":
            self.state = "night"
        elif self.state == "night":
            self.state = "sunrise"
        elif self.state == "storm":
            #self.state = "night"
            self.state = "storm" # TODO: permastorm for testing

        if force_choice:
            self.state = force_choice

        if self.state == "storm":
            self.lightningState = [0 for _ in xrange(0, self.numClouds)]
            print "Set lightning state to %s" % self.lightningState

        print "Transitioning to %s" % self.state

        self.state_time_start = time.time()
        self.state_time_end = time.time() + STATE_TIMES[self.state] * (
            (random.random() * 2 * RANDOM_TIME_FACTOR) + (1 - RANDOM_TIME_FACTOR)
        )

        # transition to next set of colors
        self.color_array_last_state = self.color_array_next_state

        next_state_palette = random.choice(STATE_COLORS[self.state])
        self.color_array_next_state = [
            random.choice(next_state_palette) for _ in xrange(0, self.numClouds)
        ]

        if not self.color_array_last_state:
            self.color_array_last_state = self.color_array_next_state

    def runStorm(self, colorArray):
        currTime = time.time()
        timeSinceLastCall = currTime - self.lastTimeCalled
        self.lastTimeCalled = currTime

        # scale the lightning probability based on the time between calls
        lightningProb = min(LIGHTNING_PROBABILITY_PER_SEC * timeSinceLastCall, 0.5)

        for i in xrange(0, self.numClouds):
            cloudLightningState = self.lightningState[i]

            if cloudLightningState == 0 and random.random() < lightningProb:
                # make this a new lightning cloud
                print "Lightning @ %s" % i
                self.lightningState[i] = [currTime, currTime + random.random() *
                    (LIGHTNING_STRIKE_MAX_SEC - LIGHTNING_STRIKE_MIN_SEC) + LIGHTNING_STRIKE_MIN_SEC
                ]
                cloudLightningState = self.lightningState[i]

            if cloudLightningState != 0:
                alpha = float(currTime - cloudLightningState[0]) / (cloudLightningState[1] - cloudLightningState[0])

                # set current color to 255 value
                colorHSV = colorsys.rgb_to_hsv(*map(lambda x: float(x) / 255.0, colorArray[i]))

                # this is a lightning cloud -- animate it
                if alpha > 1.0:
                    # stop lightning
                    self.lightningState[i] = 0
                    print "Lightning done @ %s" % i
                else:
                    # go back to original color from white
                    colorArray[i] = self.colorInterpolate([255, 255, 255], colorArray[i], alpha * alpha * alpha * alpha)

    def colorInterpolate(self, c1, c2, alpha):
        assert alpha >= 0 and alpha <= 1.0

        (c1_hsv, c2_hsv) = map(lambda c: colorsys.rgb_to_hsv(*map(lambda z: float(z) / 255.0, c)), (c1, c2))

        # hue interpolation is special
        (h1, h2) = (c1_hsv[0], c2_hsv[0])
        h_delta = h2 - h1
        if h1 > h2:
            # swap hue values if c1's hue > c2's hue
            temp = h1
            h1 = h2
            h2 = temp
            h_delta *= -1
            alpha = 1.0 - alpha

        if h_delta > 0.5:
            h1 += 1
            h = (h1 + alpha * (h2 - h1)) % 1.0  # apparently this works?
        else:
            h = h1 + (alpha * h2)

        interp_hsv = [(y - x) * alpha + x for (x, y) in zip(c1_hsv, c2_hsv)]
        interp_hsv[0] = h

        retVal = tuple(map(lambda z: int(z * 255), colorsys.hsv_to_rgb(*interp_hsv)))
        if any((x > 255 for x in retVal)):
            print "%s, %s, %s, %s" % (c1, c2, alpha, retVal)
        return retVal

    def _getColorArray(self):
        alpha = float(time.time() - self.state_time_start) / (self.state_time_end - self.state_time_start)
        if alpha >= 1.0:
            self._stateTransition()
            return self._getColorArray()

        nonlinearAlpha = alpha * alpha

        # for each cloud, interpolate linearly from current color to next color
        cloudColors = [
            self.colorInterpolate(old_color, new_color, nonlinearAlpha)
            for old_color, new_color in zip(self.color_array_last_state, self.color_array_next_state)
        ]

        # if we're in the storm mode, add extra lightning colors
        if self.state == "storm":
            self.runStorm(cloudColors)

        return cloudColors

    def getCloudLightSerialString(self):
        colorArray = self._getColorArray()
        gammaCorrectedColor = [map(lambda c: LED_GAMMA_TABLE[c], color) for color in colorArray]
        return "@%s,$" % (",".join(map(lambda c: str(c[0] << 16 | c[1] << 8 | c[2]), gammaCorrectedColor)))
