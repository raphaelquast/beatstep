import Live
from .QSetup import QSetup

# class QSequencer(ControlSurface):
class QSequencer(object):
    def __init__(self, parent):
        self._parent = parent

        self._encoder_up_counter = {**{i: 0 for i in range(16)}, 'transpose': 0}
        self._encoder_down_counter = {**{i: 0 for i in range(16)}, 'transpose': 0}
        self.QS = QSetup()

        self.up_down = True

        self.change_property = "pitch"
        self.change_interval = 1
        self.change_min = 0
        self.change_max = 128
        self.sensitivity = 8

        self.button_colors = {}

        self.blinkcolor = "red"
        self.mutecolor = "black"
        self.notecolor = "magenta"
        self.loopcolor = "blue"

        self._activeslot = 1
        self.noterange = "all"

        self.sequence_length = 8

        self.adjust_fine = 0.05
        self.adjust_coarse = 0.5


    @property
    def song(self):
        return self._parent._parent.song()

    @property
    def clip_slot(self):
        return self.song.view.highlighted_clip_slot

    @property
    def clip(self):
        if self.clip_slot is not None:
            if self.clip_slot.has_clip:
                return self.clip_slot.clip
            else:
                return None
        else:
            return None

    def dotheblink(self):
        if self.clip is not None and self._parent._sequencer:
            i = 1 + (int(self.clip.playing_position * 16 / self.sequence_length) % 16)
            if self._activeslot == i:
                return
            else:
                self._parent._update_lights()
                # blink only if slot has changed
                self._parent._set_color(i, self.blinkcolor)

            self._activeslot = i

    def _highlite_loop(self):
        self.get_button_colors()
        self._parent._update_lights()
           
    def add_handler(self):
        self.get_button_colors()
        self._parent._update_lights()

        if self.clip is not None:
            # Loop listener
            if not self.clip.loop_start_has_listener(self._highlite_loop):
                self.clip.add_loop_start_listener(self._highlite_loop)
            if not self.clip.loop_end_has_listener(self._highlite_loop):
                self.clip.add_loop_end_listener(self._highlite_loop)
            if not self.clip.position_has_listener(self._highlite_loop):
                self.clip.add_position_listener(self._highlite_loop)
            # Notes listener
            if not self.clip.notes_has_listener(self._highlite_loop):
                self.clip.add_notes_listener(self._parent._update_lights)
            # Playing position listener
            if not self.clip.playing_position_has_listener(self.dotheblink):
                self.clip.add_playing_position_listener(self.dotheblink)


    def remove_handler(self):
        if self.clip is not None:
            if self.clip.playing_position_has_listener(self.dotheblink):
                self.clip.remove_playing_position_listener(self.dotheblink)

            if self.clip.loop_start_has_listener(self._highlite_loop):
                self.clip.remove_loop_start_listener(self._highlite_loop)
            if self.clip.loop_end_has_listener(self._highlite_loop):
                self.clip.remove_loop_end_listener(self._highlite_loop)
            if self.clip.position_has_listener(self._highlite_loop):
                self.clip.remove_position_listener(self._highlite_loop)

    def set_change_properties(self, i, up_down):
        msg = None
        if i == 0:
            self.change_property = "pitch"
            self.change_interval = 1
            self.change_min = 0
            self.change_max = 128
            self.sensitivity = 8
            msg = "Encoders set to:     " + self.change_property
        elif i == 1:
            self.change_property = "velocity"
            self.change_interval = 1
            self.sensitivity = 1
            self.change_min = 0
            self.change_max = 128
            msg = "Encoders set to:     " + self.change_property
        elif i == 2:
            self.change_property = "start_time"
            self.change_interval = 0.01
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 9999
            msg = "Encoders set to:     " + self.change_property
        elif i == 3:
            self.change_property = "duration"
            self.change_interval = 0.01
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 128
            msg = "Encoders set to:     " + self.change_property
        elif i == 4:
            self.change_property = "velocity_deviation"
            self.change_interval = 1
            self.sensitivity = 1
            self.change_min = -128
            self.change_max = 128
            msg = "Encoders set to:     " + self.change_property
        elif i == 5:
            self.change_property = "probability"
            self.change_interval = 0.05
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 1
            msg = "Encoders set to:     " + self.change_property
        elif i == 6:
            self.set_sequence_length(up_down)
        elif i == 7:
            # use QControlComponent functionality
            pass
        elif i == 8:
            self.sensitivity = 4
            self.set_loop_property(
                up_down, "loop_start", self.sequence_length / 16 * 0.5
            )
        elif i == 9:
            self.sensitivity = 4
            self.set_loop_property(
                up_down, "loop_start", self.sequence_length / 16 * self.adjust_fine
            )
        elif i == 10:
            self.sensitivity = 4
            self.set_loop_property(up_down, "position", self.sequence_length / 16 * self.adjust_fine)
        elif i == 11:
            self.sensitivity = 4
            self.set_loop_property(up_down, "loop_end", self.sequence_length / 16 * self.adjust_fine)
        elif i == 12:
            self.sensitivity = 4
            self.set_loop_property(up_down, "loop_end", self.sequence_length / 16 * self.adjust_coarse)
        elif i == 14:
            msg = "transposing loop notes"
            # transpose only notes inside current loop
            self.noterange = "loop"
            self.change_property = "pitch"
            self.change_interval = 1
            self.change_min = 0
            self.change_max = 128
            self.sensitivity = 8
            self.irene_transposers(up_down)
        elif i == 'transpose':
            msg = "transposing all notes"
            # transpose all notes
            self.change_property = "pitch"
            self.change_interval = 1
            self.change_min = 0
            self.change_max = 128
            self.sensitivity = 4
            self.irene_transposers(up_down)

        if msg is not None:
            self._parent._parent.show_message(msg)

    def irene_transposers(self, up_down):
        if self.clip is not None:
            self.clip.select_all_notes()
            for i in range(16):
                self.change_note_property(i, up_down)

    def set_loop_property(self, up_down, prop, interval):
        if up_down:
            setattr(
                self.clip,
                prop,
                getattr(self.clip, prop) + interval,
            )
        else:
            setattr(
                self.clip,
                prop,
                getattr(self.clip, prop) - interval,
            )

    def button_callback(self, i):
        """
        the callback for button i (e.g. 1 - 16)
        """

        if self.clip is not None:
            if self._parent._shift_pressed:
                self.clip.scrub(self.sequence_length / 16 * i)
                self.clip.stop_scrub()
            else:
                self.clip.select_all_notes()
                self.modify_note(
                    i=i,
                    mute=not self.get_note_specs(i, "mute"),
                )
        self.get_button_colors()

    def change_note_property(self, i, up_down):
        if self.clip is not None:
            kwargs = {"i": i}
            curr_val = self.get_note_specs(i, self.change_property)

            if curr_val is not None:
                if up_down:
                    kwargs[self.change_property] = min(
                        curr_val + self.change_interval,
                        self.change_max,
                    )
                else:
                    kwargs[self.change_property] = max(
                        curr_val - self.change_interval,
                        self.change_min,
                    )

                self.modify_note(**kwargs)

    def encoder_callback(self, i, value):
        if i == 15 and self._parent._shift_pressed:
            self._parent._select_prev_next_scene(value)
            return
        elif i == 7 and self._parent._shift_pressed:
            self._parent._select_prev_next_track(value)
            return

        up_down = value < 64
        self.noterange = "all"

        if self._parent._shift_pressed and i in [0, 1, 2, 3, 4, 5]:
            self.set_change_properties(i, up_down)
            return

        # do this to avoid jumping around
        if up_down:
            for key in self._encoder_down_counter.keys():
                self._encoder_down_counter[key] = 0
            self._counter = self._encoder_up_counter
        else:
            for key in self._encoder_up_counter.keys():
                self._encoder_up_counter[key] = 0
            self._counter = self._encoder_down_counter

        # increase the counter
        self._counter[i] = self._counter[i] + 1

        if self._counter[i] > self.sensitivity:
            if i == 'transpose' or self._parent._shift_pressed:
                self.set_change_properties(i, up_down)
            else:
                self.change_note_property(i, up_down)
            # set all counters to zero
            for key in self._encoder_down_counter.keys():
                self._encoder_down_counter[key] = 0
                self._encoder_up_counter[key] = 0

    def get_button_colors(self):
        self.button_colors = dict(
            shift="red",
            chan="red",
            store="red",
            recall="red",
        )
        for i in range(16):
            self.button_colors[i + 1] = "black"

        if self.clip is not None:

            notevector, notes = self.get_notes()

            if notevector is not None:
                for i, note in enumerate(notes):
                    if note.mute:
                        self.button_colors[i + 1] = self.mutecolor
                    else:
                        if (
                            note.start_time >= self.clip.loop_start
                            and note.start_time < self.clip.loop_end
                        ):
                            self.button_colors[i + 1] = self.loopcolor
                        else:
                            self.button_colors[i + 1] = self.notecolor
                if i < 15:
                    self.button_colors[i + 2] = self.notecolor
    # -------------------------------------------

    def add_note(
        self,
        pitch,
        start_time,
        duration,
        velocity,
        velocity_deviation,
        probability,
        mute,
    ):
        """
        add new notes to the currently selected clip
        """
        note = Live.Clip.MidiNoteSpecification(
            pitch=pitch,
            start_time=start_time,
            duration=duration,
            velocity=velocity,
            velocity_deviation=velocity_deviation,
            probability=probability,
            mute=mute,
        )

        if self.clip is not None:
            self.clip.add_new_notes((note,))

    def get_notes(self):
        """
        get all notes of the current clip or the notes inside
        the current loop (depending on self.noterange)
        """

        if self.clip is not None:
            if self.noterange == "loop":
                notevector = self.clip.get_notes_extended(
                    0,
                    128,
                    self.clip.loop_start,
                    self.clip.loop_end - self.clip.loop_start,
                )
            elif self.noterange == "all":
                notevector = self.clip.get_notes_extended(0, 128, 0, 9999)

            if notevector is not None:
                notes = list(notevector)
                notes.sort(key=lambda x: x.start_time)

            return notevector, notes[:16]
        else:
            return None, None

    def modify_note(self, i, **kwargs):
        notevector, notes = self.get_notes()

        if notevector is not None and len(notes) > i:
            note = notes[i]
            for key, val in kwargs.items():
                setattr(note, key, val)

            self.clip.apply_note_modifications(notevector)

    def get_note_specs(self, i, name):

        notevector, notes = self.get_notes()

        if notevector is not None and len(notes) > i:
            return getattr(notes[i], name)
        else:
            return None

    def get_all_note_specs(self, note):
        return dict(
            pitch=note.pitch,
            start_time=note.start_time,
            duration=note.duration,
            velocity=note.velocity,
            velocity_deviation=note.velocity_deviation,
            probability=note.probability,
        )

    # -------------------------------------------

    def set_sequence_length(self, up_down):
        lengths = [1, 2, 4, 8, 16, 32]

        if up_down:
            self.sequence_length = lengths[(lengths.index(self.sequence_length) + 1)%len(lengths)]
            self._parent._parent.show_message(f"sequence length set to {self.sequence_length}")
        else:
            self.sequence_length = lengths[lengths.index(self.sequence_length) - 1]
            self._parent._parent.show_message(f"sequence length set to {self.sequence_length}")

    def init_sequence(self):
        # note = (pitch, time, duration, velocity, mute_state)
        if not self.clip_slot.has_clip:
            self.clip_slot.create_clip(self.sequence_length)
            for i in range(16):
                self.add_note(
                    pitch=self._parent._transpose_val,
                    start_time=self.sequence_length / 16 * i,
                    duration=self.sequence_length / 16 * 0.5,
                    velocity=75,
                    velocity_deviation=0,
                    probability=1,
                    mute=False,
                )

        app = self._parent._parent.application()

        app.view.show_view("Detail/Clip")
        self.add_handler()
            

            
    # TODO
    # self.clip.apply_note_modifications()
    # self.clip.get_notes_extended()
    # self.clip.remove_notes_extended(0, 128, 0, 16)

    # get_notes_extended( (int)from_pitch, (int)pitch_span, (float)from_time, (float)time_span) ->
    # MidiNoteVector : Returns a list of MIDI notes from the given pitch and time range.
    #                 Each note is represented by a Live.Clip.MidiNote object.
    #                 The returned list can be modified freely, but modifications will not be
    #                 reflected in the MIDI clip until apply_note_modifications is called.

    # apply_note_modifications( (MidiNoteVector)arg2) ->
    # None : Expects a list of notes as returned from get_notes_extended.
    #        The content of the list will be used to modify existing notes in the clip,
    #        based on matching note IDs. This function should be used when modifying
    #        existing notes, e.g. changing the velocity or start time.
    #        The function ensures that per-note events attached to the modified notes
    #        are preserved. This is NOT the case when replacing notes via a combination
    #        of remove_notes_extended and add_new_notes. The given list can be a subset of
    #        the notes in the clip, but it must not contain any notes that are not present in the clip.
