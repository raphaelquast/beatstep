#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/BeatStep/BeatStep.py
from __future__ import absolute_import, print_function, unicode_literals
from itertools import izip, chain
import Live
from _Arturia.ArturiaControlSurface import ArturiaControlSurface
from _Arturia.SessionComponent import SessionComponent
from _Arturia.MixerComponent import MixerComponent
from _Framework.Layer import Layer
from _Framework.Skin import Skin
from _Framework.DeviceComponent import DeviceComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonElement import ButtonElement, Color
from _Framework.EncoderElement import EncoderElement
HARDWARE_ENCODER_IDS = xrange(32, 48)
HARDWARE_STOP_BUTTON_ID = 89
HARDWARE_PLAY_BUTTON_ID = 88
HARDWARE_PAD_IDS = xrange(112, 128)
ENCODER_MSG_IDS = (10, 74, 71, 76, 77, 93, 73, 75, 114, 18, 19, 16, 17, 91, 79, 72)
PAD_MSG_IDS = (xrange(44, 52),
               xrange(36, 44))


PAD_MSG_IDS_LIST = list(xrange(44, 52)) + list(xrange(36, 44))


PAD_CHANNEL = 9


from BeatStep_custom.ControlComponent import ControlComponent


class Colors:

    class Session:
        ClipStarted = Color(1)
        ClipStopped = Color(1)
        ClipRecording = Color(1)
        ClipTriggeredPlay = Color(1)
        ClipTriggeredRecord = Color(1)
        RecordButton = Color(0)
        ClipEmpty = Color(0)


class BeatStep_custom(ArturiaControlSurface):

    def __init__(self, c_instance):
        self.__c_instance = c_instance

        super(BeatStep_custom, self).__init__(c_instance)

        self._skin = Skin(Colors)
        with self.component_guard():
            self._create_controls()
            self._create_mixer()
            self._create_session()

            self._create_control()

    def _create_controls(self):
        self._horizontal_scroll_encoder = EncoderElement(MIDI_CC_TYPE, 0, 75, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Horizontal_Scroll_Encoder')
        self._vertical_scroll_encoder = EncoderElement(MIDI_CC_TYPE, 0, 72, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Vertical_Scroll_Encoder')
        self._volume_encoder = EncoderElement(MIDI_CC_TYPE, 0, 91, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Volume_Encoder')
        self._pan_encoder = EncoderElement(MIDI_CC_TYPE, 0, 17, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Pan_Encoder')
        self._send_a_encoder = EncoderElement(MIDI_CC_TYPE, 0, 77, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Send_A_Encoder')
        self._send_b_encoder = EncoderElement(MIDI_CC_TYPE, 0, 93, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Send_B_Encoder')
        self._send_encoders = ButtonMatrixElement(rows=[[self._send_a_encoder, self._send_b_encoder]])
        self._return_a_encoder = EncoderElement(MIDI_CC_TYPE, 0, 73, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Return_A_Encoder')
        self._return_b_encoder = EncoderElement(MIDI_CC_TYPE, 0, 79, Live.MidiMap.MapMode.relative_smooth_two_compliment, name=u'Return_B_Encoder')
        self._return_encoders = ButtonMatrixElement(rows=[[self._return_a_encoder, self._return_b_encoder]])

        self._play_button = ButtonElement(True, MIDI_CC_TYPE, 0, 2, name=u'Play_Button')

        self._shift_button = ButtonElement(True, MIDI_CC_TYPE, 0, 1, name=u'Shift_Button')

        for i in xrange(1,17):
            msgid = PAD_MSG_IDS_LIST[i-1]
            setattr(self, '_' + str(i) + '_button',
                     ButtonElement(True, MIDI_NOTE_TYPE, PAD_CHANNEL, msgid))

        for i in xrange(1,17):
            msgid = ENCODER_MSG_IDS[i-1]
            setattr(self, '_' + str(i) + '_encoder',
                    EncoderElement(MIDI_CC_TYPE, 0, msgid, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='_' + str(i) + '_encoder'))


    def _create_session(self):
        self._session = SessionComponent(name=u'Session',
                                         is_enabled=False,
                                         num_tracks=7,
                                         num_scenes=2,
                                         enable_skinning=True,
                                         layer=Layer(#clip_launch_buttons=self._pads,
                                                     scene_select_control=self._vertical_scroll_encoder
                                                     ))

        # do this to enable the "red-box"
        self.set_highlighting_session_component(self._session)
        self._session.set_enabled(True)


    def _create_mixer(self):
        self._mixer = MixerComponent(name=u'Mixer',
                                     is_enabled=False,
                                     num_returns=2,
                                     layer=Layer(track_select_encoder=self._horizontal_scroll_encoder,
                                                 ))
        self._mixer.set_enabled(True)



    def _collect_setup_messages(self):
        for identifier, hardware_id in izip(ENCODER_MSG_IDS, HARDWARE_ENCODER_IDS):
            self._setup_hardware_encoder(hardware_id, identifier)

        self._setup_hardware_button(HARDWARE_STOP_BUTTON_ID, 1, msg_type=u'cc')
        self._setup_hardware_button(HARDWARE_PLAY_BUTTON_ID, 2, msg_type=u'cc')
        for hardware_id, identifier in izip(HARDWARE_PAD_IDS, chain(*PAD_MSG_IDS)):
            self._setup_hardware_button(hardware_id, identifier, PAD_CHANNEL, msg_type=u'note')



    def _create_control(self):

        self._control_component = ControlComponent(self)
        self._control_component.set_shift_button(self._shift_button)


        #self._control_component.set_8_button(self._8_button)
        #self._control_component.set_16_button(self._16_button)

        for i in xrange(1,17):
            getattr(self._control_component, 'set_' + str(i) + '_button'
                    )(getattr(self, '_' + str(i) + '_button'))

        for i in xrange(1,17):
            getattr(self._control_component, 'set_' + str(i) + '_encoder_button'
                    )(getattr(self, '_' + str(i) + '_encoder'))


    # def send_midi(self, midi_event_bytes):
    #     u"""Script -> Live
    #     Use this function to send MIDI events through Live to the _real_ MIDI devices
    #     that this script is assigned to.
    #     """
    #     super(BeatStep_custom, self).send_midi(midi_event_bytes)

    #     #self.__c_instance.send_midi(midi_event_bytes)
    #     self.log_message(str(midi_event_bytes))

    # def build_midi_map(self, midi_map_handle):
    #     u"""Live -> Script
    #     Build DeviceParameter Mappings, that are processed in Audio time, or
    #     forward MIDI messages explicitly to our receive_midi_functions.
    #     Which means that when you are not forwarding MIDI, nor mapping parameters, you will
    #     never get any MIDI messages at all.
    #     """
    #     super(BeatStep_custom, self).build_midi_map(midi_map_handle)

    #     # script_handle = self.__c_instance.handle()
    #     # Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, 1, 51)
    #     # for channel in range(16):
    #     #     for i in range(127):
    #     #         Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, channel, i)
    #     # for channel in range(16):
    #     #     for cc_no in range(127):
    #     #         Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, cc_no)



    # def receive_midi(self, midi_bytes):
    #     u"""Live -> Script
    #     MIDI messages are only received through this function, when explicitly
    #     forwarded in 'build_midi_map'.
    #     """
    #     super(BeatStep_custom, self).receive_midi(midi_bytes)

    #     # # this part is from _Framework.ControlSurface
    #     # with self.component_guard():
    #     #     self._do_receive_midi(midi_bytes)
    #     # # ----------


    # #     # (_, note, val) = midi_bytes
    # #     # if note == 51 and val > 0:
    # #     #     self._control_component._arm_track(7)
