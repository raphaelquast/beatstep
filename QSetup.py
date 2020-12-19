# thanks to https://www.untergeek.de/de/2014/11/taming-arturias-beatstep-sysex-codes-for-programming-via-ipad/#Sysex_for_the_Pads
# for unravelling sysx messages for BeatStep


class QSetup(object):
    '''
    ##### BUTTON
    set_B_.........  (ID, val)
                     ID: the button number (1-16), or one of ('play', 'stop', 'cntrl', 'sync', 'recall', 'store', 'shift', 'chan')

          mode:      set button mode
                     (0=off, 1=silent, 2=silent cc switch, 7=mmc, 8=cc, 9=note)
          channel:   set midi channel
                     (0-15)    (65 to follow the global channel)
          cc:        set midi CC
                     (0-127)
          off:       set midi off value
                     (0-127)
          on:        set midi on value
                     (0-127)
          behaviour: set button behaviour
                     (0=toggle, 1=gate)
          color:     set button LED color [only works if button is set to note]
                     (0=black, 1=red, 16=blue, 17=magenta)

    set_B_acceleration(value): set button acceleration (global)
                               (0=slow, 1=medium, 2=fast)
    set_B_velocity(value):     set button velocity curve   (global)
                               (0=linear, 1=logarithmic, 2=exponential, 3=full)

    ##### ENCODER
    set_E_.........  (ID, val)
                     ID: the encoder number (1-16)

          mode:      set encoder mode
                     (0=off, 1=Midi cc, 4=RPN/NRPN)
          channel:   set midi channel
                     (0-15)   (65 to follow the global channel)
          cc:        set midi CC
                     (0-127)
          off:       set lowest possible value [only if encoder is set to absolute]
                     (0-127)
          on:        set highest possible value [only if encoder is set to absolute]
                     (0-127)
          behaviour  set encoder behaviour
                     (0=absolute, 1-3=relative mode 1-3)

    ##### SEQUENCER
    set_S_...(val)
          mode:      set the mode
                     (0=forward, 1=reverse, 2=alternating, 3=random)
          channel:   set midi channel
                     (0-15)
          rate:      set rate (e.g. speed)
                     (0-4)
          transpose: base note is C5=60, to transpose down 12 semitones to C4, nn=48 and so on
                     (0-127)
          scale:     set the scale
                     (0=chromatic, 1=major, 2=minor, 3=dorian, 4=mixolydian, 5=harmonic minor, 6=blues, 7=user)
          stepsize:  set the step-size
                     (0=1/4, 1=1/8, 2=1/16, 3=1/32)
          length:    set pattern-length to 1-16 steps
                     (0-15)
          swing:     set swing
                     (50=no swing, 75=maximal swing)
          gate:      set gate   (0-99%)
                     (0-99)
          legato:    set legato
                     (0=off, 1=on, 2=reset)

    set_S_on(ID):        turn on step
                         (0-15)
    set_S_off(ID):       turn off step
                         (0-15)
    set_S_note(ID, val): set note (val) for step (ID)
                         (0-15), (1-127)

    #### GLOBAL
    set_global_channel(c): set the global midi-channel
                           (0-15)
    '''

    def __init__(self):

        # a dict with the button IDS
        self._B = dict(play=88,   # white
                       stop=89,   # no light
                       cntrl=90,  # red or blue
                       sync=91,   # blue
                       recall=92, # blue
                       store=93,  # red
                       shift=94,  # blue
                       chan=95,   # blue
                       )
        # a dict with the encoder IDS
        self._E = dict(transpose=48)

        for i in range(1, 17):
            self._B[i] = 111 + i
            self._E[i] = 31 + i


        self._funcdict = dict(mode=1, channel=2, cc=3, off=4, on=5, behaviour=6, color=16)

        self._S_funcdict = dict(channel=1, transpose=2, scale=3, mode=4, stepsize=5, length=6, swing=7, gate=8, legato=9)

        self._B_START_MSG =   (240, 0, 32, 107, 127, 66, 2, 0)   # F0 00 20 6B 7F 42 02 00 c  ID val F7
        self._B_REQUEST_MSG = (240, 0, 32, 107, 127, 66, 1, 0)   # F0 00 20 6B 7F 42 01 00 c  ID     F7

        # set button and encoder getters and setters
        for key, c in self._funcdict.items():
            funcs = self._get_callbacks(c)
            setattr(self, 'set_B_' + key, funcs[0])
            setattr(self, 'get_B_' + key, funcs[1])
            setattr(self, 'set_E_' + key, funcs[2])
            setattr(self, 'get_E_' + key, funcs[3])

        B_acc_set, B_acc_get = self._get_acceleration_callback()
        setattr(self, 'set_B_acceleration', B_acc_set)
        setattr(self, 'get_B_acceleration', B_acc_get)

        B_velocity_set, B_velocity_get = self._get_velocity_callback()
        setattr(self, 'set_B_velocity', B_velocity_set)
        setattr(self, 'set_B_velocity', B_velocity_get)

        # set sequencer setters
        for key, c in self._S_funcdict.items():
            funcs = self._get_S_callbacks(c)
            setattr(self, 'set_S_' + key, funcs[0])
            setattr(self, 'get_S_' + key, funcs[1])

        S_note_set, S_note_get = self._get_S_note_callback()
        setattr(self, 'set_S_note', S_note_set)
        setattr(self, 'get_S_note', S_note_get)

        setattr(self, 'set_S_on', self._get_S_toggle_callback(127))
        setattr(self, 'set_S_off', self._get_S_toggle_callback(0))
        setattr(self, 'get_S_onoff', self._get_S_toggle_get_callback())

    def recall_preset(self, slot):
        return (240, 0, 32, 107, 127, 66, 5, slot, 247)

    def store_preset(self, slot):
        return (240, 0, 32, 107, 127, 66, 6, slot, 247)

    def set_global_channel(self, val):
        return self._send_change(64, 6, val)

    def get_global_channel(self):
        return self._send_request(64, 6)

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

    def _get_velocity_callback(self):
        def set_callback(val):
            return self._send_change(65, 3, val)
        def get_callback():
            return self._send_request(65, 3)
        return set_callback, get_callback

    def _get_acceleration_callback(self):
        def set_callback(val):
            return self._send_change(65, 4, val)
        def get_callback():
            return self._send_request(65, 4)
        return set_callback, get_callback

    def _get_S_callbacks(self, c):
        def set_callback(val):
            return self._send_change(80, c, val)
        def get_callback():
            return self._send_request(80, c)
        return set_callback, get_callback

    def _get_S_note_callback(self):
        def set_callback(ID, val):
            return self._send_change(82, ID, val)
        def get_callback(ID):
            return self._send_request(82, ID)
        return set_callback, get_callback

    def _get_S_toggle_callback(self, val):
        def set_callback(ID):
            return self._send_change(83, ID, val)
        return set_callback

    def _get_S_toggle_get_callback(self):
        def get_callback(ID):
            return self._send_request(83, ID)
        return get_callback
