# thanks to https://www.untergeek.de/de/2014/11/taming-arturias-beatstep-sysex-codes-for-programming-via-ipad/#Sysex_for_the_Pads
# for unravelling sysx messages for BeatStep

class QSetup(object):
    def __init__(self):

        # a dict with the button IDS
        self._B = dict(play=88,   # white
                       stop=89,   # no light
                       cntrl=90,    # red or blue
                       ext=91,      # blue
                       recall=92,  # blue
                       store=93,  # red
                       shift=94,  # blue
                       chan=95,   # blue
                       )
        # a dict with the encoder IDS
        self._E = dict(transpose=48)

        for i in range(16):
            self._B[i] = 112 + i
            self._E[i] = 32 + i


        self._funcdict = dict(mode=1, channel=2, cc=3, off=4, on=5, behaviour=6, color=16)

        self._B_START_MSG =   (240, 0, 32, 107, 127, 66, 2, 0)   # F0 00 20 6B 7F 42 02 00
        self._B_REQUEST_MSG = (240, 0, 32, 107, 127, 66, 1, 0)   # F0 00 20 6B 7F 42 01 00 pp cc F7


        for key, c in self._funcdict.items():

            funcs = self._get_callbacks(c)
            setattr(self, 'set_B_' + key, funcs[0])
            setattr(self, 'get_B_' + key, funcs[1])
            setattr(self, 'set_E_' + key, funcs[2])
            setattr(self, 'get_E_' + key, funcs[3])


    def _send_change(self, c, ID, val):
        return self._B_START_MSG + (c, ID, val, 247)

    def _send_request(self, c, ID):
        return self._B_REQUEST_MSG + (c, ID, 247)

    def _get_callbacks(self, c):
        # do this to ensure function-name closure!
        def changeB(ID, val):
            return self._send_change(c, self._B[ID], val)

        def requestB(ID):
            return self._send_request(c, self._B[ID])

        def changeE(ID, val):
            return self._send_change(c, self._E[ID], val)

        def requestE(ID):
            return self._send_request(c, self._E[ID])

        return changeB, requestB, changeE, requestE
