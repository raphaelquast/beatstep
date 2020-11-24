#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/BeatStep/BeatStep.py
from __future__ import absolute_import, print_function, unicode_literals
from itertools import izip
import Live
from _Arturia.ArturiaControlSurface import ArturiaControlSurface
from _Arturia.SessionComponent import SessionComponent
from _Arturia.MixerComponent import MixerComponent
from _Framework.Layer import Layer
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement

HARDWARE_ENCODER_IDS = xrange(32, 48)
HARDWARE_STOP_BUTTON_ID = 89
HARDWARE_PLAY_BUTTON_ID = 88
HARDWARE_PAD_IDS = xrange(112, 128)

ENCODER_MSG_IDS = (10, 74, 71, 76, 77, 93, 73, 75, 114, 18, 19, 16, 17, 91, 79, 72)
PAD_MSG_IDS = list(xrange(44, 52)) + list(xrange(36, 44))

TRANSPOSE_CHANNEL = 8
PAD_CHANNEL = 9

from BeatStep_custom.ControlComponent import ControlComponent


class BeatStep_custom(ArturiaControlSurface):

    def __init__(self, c_instance):
        self.__c_instance = c_instance

        super(BeatStep_custom, self).__init__(c_instance)

        with self.component_guard():
            self._create_controls()
            self._create_mixer()
            self._create_session()

            self._create_control()


    def _create_controls(self):
        self._play_button = ButtonElement(True, MIDI_CC_TYPE, 0, 2, name=u'Play_Button')
        self._play_note_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, 60, name=u'Play_Note_Button')

        self._shift_button = ButtonElement(True, MIDI_CC_TYPE, 0, 1, name=u'Shift_Button')

        for i in xrange(1,17):
            msgid = PAD_MSG_IDS[i-1]
            setattr(self, '_' + str(i) + '_button',
                     ButtonElement(True, MIDI_NOTE_TYPE, PAD_CHANNEL, msgid,
                                   name='_' + str(i) + '_button'))

            self._transpose_encoder = EncoderElement(MIDI_CC_TYPE, TRANSPOSE_CHANNEL, 7,
                                                     Live.MidiMap.MapMode.relative_smooth_two_compliment,
                                                     name='_transpose_encoder')

        for i in xrange(1,17):
            msgid = ENCODER_MSG_IDS[i-1]
            setattr(self, '_' + str(i) + '_encoder',
                    EncoderElement(MIDI_CC_TYPE, 0, msgid,
                                   Live.MidiMap.MapMode.relative_smooth_two_compliment,
                                   name='_' + str(i) + '_encoder'))


    def _create_session(self):
        self._session = SessionComponent(name=u'Session',
                                         is_enabled=False,
                                         num_tracks=7,
                                         num_scenes=2,
                                         enable_skinning=False,
                                         layer=Layer(scene_select_control=self._16_encoder))

        # do this to enable the "red-box"
        self.set_highlighting_session_component(self._session)
        self._session.set_enabled(True)


    def _create_mixer(self):
        self._mixer = MixerComponent(name=u'Mixer',
                                     is_enabled=False,
                                     num_returns=2,
                                     layer=Layer(track_select_encoder=self._8_encoder))
        self._mixer.set_enabled(True)



    def _collect_setup_messages(self):
        for identifier, hardware_id in izip(ENCODER_MSG_IDS, HARDWARE_ENCODER_IDS):
            self._setup_hardware_encoder(hardware_id, identifier)

        self._setup_hardware_button(HARDWARE_STOP_BUTTON_ID, 1, msg_type=u'cc')
        self._setup_hardware_button(HARDWARE_PLAY_BUTTON_ID, 2, msg_type=u'cc')
        for hardware_id, identifier in izip(HARDWARE_PAD_IDS, PAD_MSG_IDS):
            self._setup_hardware_button(hardware_id, identifier, PAD_CHANNEL, msg_type=u'note')


    def _create_control(self):

        self._control_component = ControlComponent(self)
        self._control_component.set_shift_button(self._shift_button)
        self._control_component.set_play_note_button(self._play_note_button)

        self._control_component.set_transpose_encoder_button(self._transpose_encoder)

        for i in xrange(1,17):
            getattr(self._control_component, 'set_' + str(i) + '_button'
                    )(getattr(self, '_' + str(i) + '_button'))

        for i in xrange(1,17):
            getattr(self._control_component, 'set_' + str(i) + '_encoder_button'
                    )(getattr(self, '_' + str(i) + '_encoder'))


    def _hex_to_dec(self, hex):
        from functools import partial
        return tuple(map(partial(int, base=16), hex.split(' ')))
