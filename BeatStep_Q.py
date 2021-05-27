# Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/BeatStep/BeatStep_Q.py
from __future__ import absolute_import, print_function, unicode_literals
import Live

# from _Arturia.ArturiaControlSurface import ArturiaControlSurface
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

from functools import partial

ENCODER_MSG_IDS = (10, 74, 71, 76, 77, 93, 73, 75, 114, 18, 19, 16, 17, 91, 79, 72)
PAD_MSG_IDS = list(range(44, 52)) + list(range(36, 44))

# the midi-channel to use for buttons and encoders
CHANNEL = 9
# the used memory-slot to store the configurations
MEMORY_SLOT = 8

SETUP_HARDWARE_DELAY = 2.2
INDIVIDUAL_MESSAGE_DELAY = 0#0.001

def split_list(l, size):
    for i in range(0, len(l), size):
        yield l[i:i + size]



class BeatStep_Q(ControlSurface):
    def __init__(self, *a, **k):
        super(BeatStep_Q, self).__init__(*a, **k)
        self._messages_to_send = []

        self.QS = QSetup()
        self.control_layer_active = False

        with self.component_guard():
            self._init_color_sequence()

            # self._setup_hardware_task = self._tasks.add(
            #     Task.sequence(
            #         Task.wait(SETUP_HARDWARE_DELAY),
            #         Task.run(self._init_color_sequence),
            #         Task.run(partial(self._get_task_sequence, delay=0, maintain_order=True))
            #         )
            #     )
            # self._start_hardware_setup()


            # self._setup_hardware_task = self._tasks.add(
            #     Task.sequence(
            #         Task.run(self._init_color_sequence),
            #         Task.wait(SETUP_HARDWARE_DELAY),
            #         Task.run(partial(self._setup_hardware, 0.1)),
            #     )
            # )
            # self._setup_hardware_task.kill()
            # self._start_hardware_setup()

            # self._create_controls()
            # self._create_Q_control()

            # self._create_device()

    def receive_midi(self, midi_bytes):
        # self.show_message(str(midi_bytes))
        super(BeatStep_Q, self).receive_midi(midi_bytes)

    def handle_sysex(self, midi_bytes):
        # self.show_message(str(midi_bytes))
        super(BeatStep_Q, self).handle_sysex(midi_bytes)

    def port_settings_changed(self):
        super(BeatStep_Q, self).port_settings_changed()

        self._init_color_sequence()

    def _start_hardware_setup(self):
        if self._setup_hardware_task.is_running:
            # kill already running setup tasks
            self._setup_hardware_task.kill()

        self._setup_hardware_task.restart()

    def _B_color_callback(self, b, c):
        # do this to ensure callback-name closure
        def f():
            self._send_midi(self.QS.set_B_color(b, c))

        return f


    def _init_color_sequence(self):
        msg_delay = 0.05

        init_task = self._tasks

        offmsgs = [self.QS.set_B_color(i, 0) for i in range(1, 17)]
        rmsgs = [self.QS.set_B_color(i, 1) for i in range(1, 17)]
        bmsgs = [self.QS.set_B_color(i, 16) for i in range(1, 17)]
        mmsgs = [self.QS.set_B_color(i, 17) for i in range(1, 17)]

        msgs = []

        for i, [o, r, b, m, rr, br, mr] in enumerate(zip(offmsgs, rmsgs, bmsgs, mmsgs,
                                                         rmsgs[::-1], bmsgs[::-1], mmsgs[::-1])):
            msgs.append([
                 Task.wait(SETUP_HARDWARE_DELAY),
                 Task.run(partial(self._send_midi, o)),
                 Task.wait(msg_delay * (i + 1)),
                 Task.run(partial(self._send_midi, r)),
                 Task.wait(msg_delay * (16)),
                 Task.run(partial(self._send_midi, b)),
                 Task.wait(msg_delay * (16)),
                 Task.run(partial(self._send_midi, m)),
                 Task.wait(msg_delay * (16)),
                 Task.run(partial(self._send_midi, rr)),
                 Task.wait(msg_delay * (16)),
                 Task.run(partial(self._send_midi, br)),
                 Task.wait(msg_delay * (16)),
                 Task.run(partial(self._send_midi, mr)),
                 Task.wait(msg_delay * (16)),
                 Task.run(partial(self._send_midi, o)),
                 ])

        for i in msgs:
            init_task.add(Task.sequence(*i))



    def _get_task_sequence(self, delay=0, maintain_order=False):

        sequence_to_run = []
        for msg in self._messages_to_send:
            sequence_to_run.append(Task.run(partial(self._send_midi, msg)))
            sequence_to_run.append(Task.wait(INDIVIDUAL_MESSAGE_DELAY))

        # bin the tasks into groups of 40 messages
        for subsequence in split_list(sequence_to_run, 40):
            self._tasks.add(Task.sequence(*subsequence))

        self._messages_to_send = []



    # def _setup_hardware(self, delay=None):
    #     if delay is None:
    #         delay = INDIVIDUAL_MESSAGE_DELAY

    #     sequence_to_run = []
    #     for msg in self._messages_to_send:
    #         sequence_to_run.append(Task.run(partial(self._send_midi, msg)))
    #         sequence_to_run.append(Task.wait(delay))

    #     for subsequence in split_list(sequence_to_run, 40):
    #         self._tasks.add(Task.sequence(*subsequence))

    #     self._messages_to_send = []


    # def _setup_hardware(self):
    #     self._init_color_sequence()
    #     self._setup_control_buttons_and_encoders()
    #     self._setup_buttons_and_encoders()

    #     # set pad velocity to 0 (e.g. linear) on startup
    #     self._send_midi(self.QS.set_B_velocity(0))
    #     # set encoder acceleration to "slow" on startup
    #     self._send_midi(self.QS.set_E_acceleration(0))

    def _setup_control_buttons_and_encoders(self):
        """
        this function is only called once when the BeatStep is plugged in to
        ensure correct assignments of function-buttons and transpose encoder
        """
        # set shift button to note-mode
        self._send_midi(self.QS.set_B_mode("shift", 8))
        self._send_midi(self.QS.set_B_channel("shift", CHANNEL))
        self._send_midi(self.QS.set_B_behaviour("shift", 1))

        # set stop button to note-mode
        self._send_midi(self.QS.set_B_mode("stop", 8))
        self._send_midi(self.QS.set_B_channel("stop", CHANNEL))
        self._send_midi(self.QS.set_B_behaviour("stop", 1))

        # set play button to note-mode
        self._send_midi(self.QS.set_B_mode("play", 8))
        self._send_midi(self.QS.set_B_channel("play", CHANNEL))
        self._send_midi(self.QS.set_B_behaviour("play", 1))

        # set cntrl/seq button to note-mode
        self._send_midi(self.QS.set_B_mode("cntrl", 8))
        self._send_midi(self.QS.set_B_channel("cntrl", CHANNEL))
        # set button behaviour to toggle
        self._send_midi(self.QS.set_B_behaviour("cntrl", 0))

        # set chan button to note mode
        self._send_midi(self.QS.set_B_mode("chan", 8))
        self._send_midi(self.QS.set_B_channel("chan", CHANNEL))
        self._send_midi(self.QS.set_B_behaviour("chan", 1))

        # set store button to note mode
        self._send_midi(self.QS.set_B_mode("store", 8))
        self._send_midi(self.QS.set_B_channel("store", CHANNEL))
        self._send_midi(self.QS.set_B_behaviour("store", 1))

        # set store button to note mode
        self._send_midi(self.QS.set_B_mode("recall", 8))
        self._send_midi(self.QS.set_B_channel("recall", CHANNEL))
        self._send_midi(self.QS.set_B_behaviour("recall", 1))

        # set transpose encoder channel
        self._send_midi(self.QS.set_E_channel("transpose", CHANNEL))
        self._send_midi(self.QS.set_E_behaviour("transpose", 2))
        # set encoder cc to something else than the shift-encoder cc
        # (4 is unused since it would represent the ext/sync button)
        self._send_midi(self.QS.set_E_cc("transpose", 4))

    def _setup_buttons_and_encoders(self):
        # for all buttons and encoders
        for i in range(1, 17):
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
            # set all encoders to midi cc mode
            self._send_midi(self.QS.set_E_mode(i, 1))
            # set midi cc id's for all encoders
            self._send_midi(self.QS.set_E_cc(i, ENCODER_MSG_IDS[i - 1]))

    def _do_activate_control_mode(self):
        # for all buttons
        for i in range(1, 17):
            # set pad to cc-mode
            self._send_midi(self.QS.set_B_mode(i, 8))
            # set pad channel
            self._send_midi(self.QS.set_B_channel(i, CHANNEL))
            # set pad behaviour to toggle
            self._send_midi(self.QS.set_B_behaviour(i, 1))

            # set encoder channel
            self._send_midi(self.QS.set_E_channel(i, CHANNEL))
            # set all encoders to relative-mode 2
            self._send_midi(self.QS.set_E_behaviour(i, 2))

        # set transpose encoder channel to follow global channel
        self._send_midi(self.QS.set_E_channel("transpose", CHANNEL))
        # set transpose encoder to relative mode 2
        self._send_midi(self.QS.set_E_behaviour("transpose", 2))

    def _deactivate_control_mode(self):
        self._send_midi(self.QS.recall_preset(MEMORY_SLOT))
        # make sure that buttons relevant for control-features
        # are correctly set
        # self._setup_control_buttons_and_encoders()

        # set pad velocity
        self._send_midi(self.QS.set_B_velocity(self._control_component._pad_velocity))

        self.control_layer_active = False

    def _activate_control_mode(self):
        # only save the current configuration if no control-layer is active
        if not self.control_layer_active:
            self._send_midi(self.QS.store_preset(MEMORY_SLOT))

        self._do_activate_control_mode()
        self.control_layer_active = True

    def _create_controls(self):
        self._play_button = ButtonElement(
            True, MIDI_CC_TYPE, CHANNEL, 2, name="Play_Button"
        )
        self._play_S_button = ButtonElement(
            True, MIDI_NOTE_TYPE, 0, 60, name="Play_Button"
        )

        self._stop_button = ButtonElement(
            True, MIDI_CC_TYPE, CHANNEL, 1, name="Stop_Button"
        )
        self._cntrl_button = ButtonElement(
            True, MIDI_CC_TYPE, CHANNEL, 3, name="cntrl_Button"
        )
        self._recall_button = ButtonElement(
            True, MIDI_CC_TYPE, CHANNEL, 5, name="recall_Button"
        )
        self._store_button = ButtonElement(
            True, MIDI_CC_TYPE, CHANNEL, 6, name="store_Button"
        )
        self._shift_button = ButtonElement(
            True, MIDI_CC_TYPE, CHANNEL, 7, name="Shift_Button"
        )
        self._chan_button = ButtonElement(
            True, MIDI_CC_TYPE, CHANNEL, 8, name="chan_Button"
        )

        for i in range(1, 17):
            bmsgid = PAD_MSG_IDS[i - 1]
            setattr(
                self,
                "_" + str(i) + "_button",
                ButtonElement(
                    True, MIDI_CC_TYPE, CHANNEL, bmsgid, name="_" + str(i) + "_button"
                ),
            )

            emsgid = ENCODER_MSG_IDS[i - 1]
            setattr(
                self,
                "_" + str(i) + "_encoder",
                EncoderElement(
                    MIDI_CC_TYPE,
                    CHANNEL,
                    emsgid,
                    Live.MidiMap.MapMode.relative_smooth_two_compliment,
                    name="_" + str(i) + "_encoder",
                ),
            )

        self._transpose_encoder = EncoderElement(
            MIDI_CC_TYPE,
            CHANNEL,
            4,
            Live.MidiMap.MapMode.relative_smooth_two_compliment,
            name="_transpose_encoder",
        )

        self._device_encoders = ButtonMatrixElement(
            rows=[
                [
                    EncoderElement(
                        MIDI_CC_TYPE,
                        CHANNEL,
                        identifier,
                        Live.MidiMap.MapMode.relative_smooth_two_compliment,
                        name="Encoder_%d_%d" % (column_index, row_index),
                    )
                    for column_index, identifier in enumerate(row)
                ]
                for row_index, row in enumerate(
                    (ENCODER_MSG_IDS[:4], ENCODER_MSG_IDS[8:12])
                )
            ]
        )

    def _create_Q_control(self):

        self._control_component = QControlComponent(self)
        self._control_component.set_shift_button(self._shift_button)
        self._control_component.set_stop_button(self._stop_button)
        self._control_component.set_play_button(self._play_button)
        self._control_component.set_play_S_button(self._play_S_button)
        self._control_component.set_cntrl_button(self._cntrl_button)
        self._control_component.set_chan_button(self._chan_button)
        self._control_component.set_store_button(self._store_button)
        self._control_component.set_recall_button(self._recall_button)

        self._control_component.set_transpose_encoder_button(self._transpose_encoder)

        for i in range(1, 17):
            getattr(self._control_component, "set_" + str(i) + "_button")(
                getattr(self, "_" + str(i) + "_button")
            )

        for i in range(1, 17):
            getattr(self._control_component, "set_" + str(i) + "_encoder_button")(
                getattr(self, "_" + str(i) + "_encoder")
            )

    def _create_device(self):
        self._device = DeviceComponent(
            name="Device",
            is_enabled=False,
            layer=Layer(parameter_controls=self._device_encoders),
            device_selection_follows_track_selection=True,
        )
        self._device.set_enabled(True)
        self.set_device_component(self._device)
