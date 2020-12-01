#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/BeatStep/BeatStep_Q.py
from __future__ import absolute_import, print_function, unicode_literals
import Live
#from _Arturia.ArturiaControlSurface import ArturiaControlSurface
from _Framework.ControlSurface import ControlSurface
from _Framework.Layer import Layer
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework import Task
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.DeviceComponent import DeviceComponent


from .QControlComponent import QControlComponent
from .QSetup import QSetup


ENCODER_MSG_IDS = (10, 74, 71, 76, 77, 93, 73, 75, 114, 18, 19, 16, 17, 91, 79, 72)
PAD_MSG_IDS = list(xrange(44, 52)) + list(xrange(36, 44))

CHANNEL_SEQUENCER = 8
CHANNEL = 9


SETUP_HARDWARE_DELAY = 2.1

class BeatStep_Q(ControlSurface):

    def __init__(self, *a, **k):
        super(BeatStep_Q, self).__init__(*a, **k)

        self.QS = QSetup()

        with self.component_guard():
            self._setup_hardware_task = self._tasks.add(Task.sequence(Task.wait(SETUP_HARDWARE_DELAY),
                                                                      Task.run(self._setup_hardware)))
            self._setup_hardware_task.kill()
            self._start_hardware_setup()

            self._create_controls()
            self._create_Q_control()

            self._create_device()

    def receive_midi(self, midi_bytes):
        #self.show_message(str(midi_bytes))
        super(BeatStep_Q, self).receive_midi(midi_bytes)

    def handle_sysex(self, midi_bytes):
        #self.show_message(str(midi_bytes))
        super(BeatStep_Q, self).handle_sysex(midi_bytes)

    def port_settings_changed(self):
        super(BeatStep_Q, self).port_settings_changed()
        self._start_hardware_setup()

    def _start_hardware_setup(self):
        # kill already running setup tasks:
        self._setup_hardware_task.kill()
        self._messages_to_send = []
        self._setup_hardware_task.restart()

    def _B_color_callback(self, b, c):
        # do this to ensure callback-name closure
        def f():
            self._send_midi(self.QS.set_B_color(b, c))
        return f

    def _init_color_sequence(self):
        for i in range(8):
            self.schedule_message(i + 1, self._B_color_callback(i, 1))
            self.schedule_message(16 - i, self._B_color_callback(i, 16))
        for i in range(15):
            self.schedule_message(20, self._B_color_callback(i, 0))

    def _setup_hardware(self):

        self._init_color_sequence()
        # set shift button to note-mode
        self._send_midi(self.QS.set_B_mode('shift', 9))
        self._send_midi(self.QS.set_B_channel('shift', CHANNEL))

        # set stop button to note-mode
        self._send_midi(self.QS.set_B_mode('stop', 9))
        self._send_midi(self.QS.set_B_channel('stop', CHANNEL))

        # set play button to note-mode
        self._send_midi(self.QS.set_B_mode('play', 9))
        self._send_midi(self.QS.set_B_channel('play', CHANNEL))

        # set cntrl/seq button to note-mode
        self._send_midi(self.QS.set_B_mode('cntrl', 9))
        self._send_midi(self.QS.set_B_channel('cntrl', CHANNEL))
        # set button behaviour to toggle
        self._send_midi(self.QS.set_B_behaviour('cntrl', 0))

        # set transpose encoder channel
        self._send_midi(self.QS.set_E_channel('transpose', CHANNEL))
        self._send_midi(self.QS.set_E_behaviour('transpose', 2))

        # for all buttons
        for i in range(16):
            # set pad to note-mode
            self._send_midi(self.QS.set_B_mode(i, 9))
            # set pad channel
            self._send_midi(self.QS.set_B_channel(i, CHANNEL))
            # set pad behaviour to toggle
            self._send_midi(self.QS.set_B_behaviour(i, 1))

            # set encoder channel
            self._send_midi(self.QS.set_E_channel(i, CHANNEL))
            # set all encoders to relative-mode 2
            self._send_midi(self.QS.set_E_behaviour(i, 2))

        self._send_midi(self.QS.set_S_channel(CHANNEL_SEQUENCER))

    def _create_controls(self):
        self._play_button = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, 2, name=u'Play_Button')
        self._play_S_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, 60, name=u'Play_Button')

        self._stop_button = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, 1, name=u'Stop_Button')
        self._shift_button = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, 7, name=u'Shift_Button')
        self._cntrl_button = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, 3, name=u'cntrl_Button')

        for i in xrange(1,17):
            msgid = PAD_MSG_IDS[i-1]
            setattr(self, '_' + str(i) + '_button',
                     ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, msgid,
                                   name='_' + str(i) + '_button'))

            self._transpose_encoder = EncoderElement(MIDI_CC_TYPE, CHANNEL, 7,
                                                     Live.MidiMap.MapMode.relative_smooth_two_compliment,
                                                     name='_transpose_encoder')

        for i in xrange(1,17):
            msgid = ENCODER_MSG_IDS[i-1]
            setattr(self, '_' + str(i) + '_encoder',
                    EncoderElement(MIDI_CC_TYPE, CHANNEL, msgid,
                                   Live.MidiMap.MapMode.relative_smooth_two_compliment,
                                   name='_' + str(i) + '_encoder'))

        self._device_encoders = ButtonMatrixElement(rows=[ [ EncoderElement(MIDI_CC_TYPE, CHANNEL, identifier, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Encoder_%d_%d' % (column_index, row_index)) for column_index, identifier in enumerate(row) ] for row_index, row in enumerate((ENCODER_MSG_IDS[:4], ENCODER_MSG_IDS[8:12])) ])

    def _create_Q_control(self):

        self._control_component = QControlComponent(self)
        self._control_component.set_shift_button(self._shift_button)
        self._control_component.set_stop_button(self._stop_button)
        self._control_component.set_play_button(self._play_button)
        self._control_component.set_play_S_button(self._play_S_button)
        self._control_component.set_cntrl_button(self._cntrl_button)

        self._control_component.set_transpose_encoder_button(self._transpose_encoder)

        for i in xrange(1,17):
            getattr(self._control_component, 'set_' + str(i) + '_button'
                    )(getattr(self, '_' + str(i) + '_button'))

        for i in xrange(1,17):
            getattr(self._control_component, 'set_' + str(i) + '_encoder_button'
                    )(getattr(self, '_' + str(i) + '_encoder'))

    def _create_device(self):
        self._device = DeviceComponent(name=u'Device', is_enabled=False,
                                       layer=Layer(parameter_controls=self._device_encoders),
                                       device_selection_follows_track_selection=True)
        self._device.set_enabled(True)
        self.set_device_component(self._device)
