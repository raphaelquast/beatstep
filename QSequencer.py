import Live
from .QSetup import QSetup


# add this to be able to print nice Fractions (without using the "fractions" module)
def gcd(a, b):
    """Calculate the Greatest Common Divisor of a and b.

    Unless b==0, the result will have the same sign as b (so that when
    b is divided by it, the result comes out positive).
    """
    while b:
        a, b = b, a % b
    return a


def simplify_fraction(numer, denom):
    # This is required since abletons python does not provide the "fractions" module
    # adapted from https://codereview.stackexchange.com/a/66474
    if denom == 0:
        return "Division by 0 - result undefined"
    # Remove greatest common divisor:
    common_divisor = gcd(numer, denom)
    (reduced_num, reduced_den) = (numer / common_divisor, denom / common_divisor)
    # Note that reduced_den > 0 as documented in the gcd function.
    if reduced_den == 1:
        return f"{reduced_num:.0f}"
    elif common_divisor == 1:
        return f"{numer:.0f}/{denom:.0f}"
    else:
        return f"{reduced_num:.0f}/{reduced_den:.0f}"


# class QSequencer(ControlSurface):
class QSequencer(object):
    def __init__(self, parent):
        self._parent = parent

        self._encoder_up_counter = {**{i: 0 for i in range(16)}, "transpose": 0}
        self._encoder_down_counter = {**{i: 0 for i in range(16)}, "transpose": 0}
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

        self.n_notes = 16
        self.note_duration = 0.5
        self.note_offset = 0
        self.note_velocity = 0.75

        self.sequence_lengths = [1, 2, 4, 8, 16, 32, 64, 128]
        #                       [2,1,1/2,1/4,1/8,1/16,1/32]

        self.note_offset_duration = [True, True, False, False]

        self.note_velocities = [0.25, 0.5, 0.75, 1]

        self.sequence_names = {
            i: f"{simplify_fraction(i, 16 * 4)}".ljust(4, "_") + "_Q"
            for i in self.sequence_lengths
        }
        self.sequence_names_inverted = dict(
            (v, k) for k, v in self.sequence_names.items()
        )

        self.sequence_up = 0
        self.sequence_n = 4

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
            if not self.clip.notes_has_listener(self._parent._update_lights):
                self.clip.add_notes_listener(self._parent._update_lights)
            # Playing position listener
            if not self.clip.playing_position_has_listener(self.dotheblink):
                self.clip.add_playing_position_listener(self.dotheblink)

        self.get_sequence_length()
        self.get_n_notes()

    def remove_handler(self):
        if self.clip is not None:
            # Loop listener
            if self.clip.loop_start_has_listener(self._highlite_loop):
                self.clip.remove_loop_start_listener(self._highlite_loop)
            if self.clip.loop_end_has_listener(self._highlite_loop):
                self.clip.remove_loop_end_listener(self._highlite_loop)
            if self.clip.position_has_listener(self._highlite_loop):
                self.clip.remove_position_listener(self._highlite_loop)
            # Notes listener
            if self.clip.notes_has_listener(self._parent._update_lights):
                self.clip.remove_notes_listener(self._parent._update_lights)
            # Playing position listener
            if self.clip.playing_position_has_listener(self.dotheblink):
                self.clip.remove_playing_position_listener(self.dotheblink)

    def set_change_properties(self, i, up_down):
        msg = None
        if i == 0:
            self.change_property = "pitch"
            self.change_interval = 1
            self.change_min = 0
            self.change_max = 127
            self.sensitivity = 8
            msg = "Encoders set to:     " + self.change_property
        elif i == 1:
            self.change_property = "velocity"
            self.change_interval = 1
            self.sensitivity = 1
            self.change_min = 1
            self.change_max = 127
            msg = "Encoders set to:     " + self.change_property
        elif i == 2:
            self.change_property = "start_time"
            self.change_interval = self.sequence_length / 16 * self.adjust_fine
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 9999
            msg = "Encoders set to:     " + self.change_property
        elif i == 3:
            self.change_property = "duration"
            self.change_interval = self.sequence_length / 16 * self.adjust_fine
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 127
            msg = "Encoders set to:     " + self.change_property
        elif i == 4:
            self.change_property = "velocity_deviation"
            self.change_interval = 1
            self.sensitivity = 1
            self.change_min = -127
            self.change_max = 127
            msg = "Encoders set to:     " + self.change_property
        elif i == 5:
            self.change_property = "probability"
            self.change_interval = 0.05
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 1
            msg = "Encoders set to:     " + self.change_property
        elif i == 6:
            pass
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
            self.set_loop_property(
                up_down, "position", self.sequence_length / 16 * self.adjust_fine
            )
        elif i == 11:
            self.sensitivity = 4
            self.set_loop_property(
                up_down, "loop_end", self.sequence_length / 16 * self.adjust_fine
            )
        elif i == 12:
            self.sensitivity = 4
            self.set_loop_property(
                up_down, "loop_end", self.sequence_length / 16 * self.adjust_coarse
            )
        elif i == 14:
            msg = "transposing loop notes"
            # transpose only notes inside current loop
            self.noterange = "loop"
            self.change_property = "pitch"
            self.change_interval = 1
            self.change_min = 0
            self.change_max = 127
            self.sensitivity = 8
            self.irene_transposers(up_down)
        elif i == "transpose":
            msg = "transposing all notes"
            # transpose all notes
            self.change_property = "pitch"
            self.change_interval = 1
            self.change_min = 0
            self.change_max = 127
            self.sensitivity = 4
            self.irene_transposers(up_down)

        if msg is not None:
            self._parent._parent.show_message(msg)

    def irene_transposers(self, up_down):
        if self.clip is not None:
            self.clip.select_all_notes()
            for i in range(16):
                self.change_note_property(i, up_down)

    def set_sequence_up(self, up_down):
        if up_down:

            if (
                self._parent._transpose_val
                + 16 / max(self.sequence_n, 2) * (self.sequence_up)
                < 127
            ):
                self.sequence_up = self.sequence_up + 1
        else:
            if (
                self._parent._transpose_val
                + 16 / max(self.sequence_n, 2) * (self.sequence_up)
                > 0
            ):
                self.sequence_up = self.sequence_up - 1

        self.show_sequence_info()

    def set_sequence_n(self, up_down):
        if up_down:
            self.sequence_n = min(self.sequence_n + 1, 8)
        else:
            self.sequence_n = max(self.sequence_n - 1, 0)

        self.show_sequence_info()

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

        if self._parent._shift_pressed:
            if i in range(7):
                self._parent._select_track(i)
            elif i == 7:
                self._parent._select_prev_scene()
            elif i == 8:
                self._parent._undo()
            elif i == 9:
                self._parent._delete_clip()
            elif i == 11:
                self._parent._duplicate_clip()
            elif i == 12:
                self._parent._duplicate_loop()
            elif i == 14:
                self._parent._fire_record()
            elif i == 15:
                self._parent._select_next_scene()
            return

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
        else:
            self.set_sequence_length_button(i)
            self.set_note_duration_button(i)
            self.set_note_velocity_button(i)
            # self.set_n_notes_button(i)

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
        up_down = value < 64
        self.noterange = "all"

        if i == 15 and (self._parent._shift_pressed or self.clip is None):
            self._parent._select_prev_next_scene(value)
            return
        elif i == 7 and (self._parent._shift_pressed or self.clip is None):
            self._parent._select_prev_next_track(value)
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

        if self.clip is None:
            if i == "transpose":
                self._parent._transpose(value, set_values=False)
            elif i in [0, 1, 2, 3, 4, 5]:
                self.set_change_properties(i, up_down)

            elif i == 8:
                if self._counter[i] > self.sensitivity:
                    self.set_sequence_up(up_down)

                    # set all counters to zero
                    for key in self._encoder_down_counter.keys():
                        self._encoder_down_counter[key] = 0
                        self._encoder_up_counter[key] = 0

            elif i == 9:
                if self._counter[i] > self.sensitivity:
                    self.set_sequence_n(up_down)

                    # set all counters to zero
                    for key in self._encoder_down_counter.keys():
                        self._encoder_down_counter[key] = 0
                        self._encoder_up_counter[key] = 0
            return

        if self._parent._shift_pressed and i in [0, 1, 2, 3, 4, 5]:
            self.set_change_properties(i, up_down)
            return

        if self._counter[i] > self.sensitivity:
            if i == "transpose" or self._parent._shift_pressed:
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
        else:
            self.button_colors[
                self.sequence_lengths.index(self.sequence_length) + 1
            ] = "red"

            for i, offset_Q in enumerate(self.note_offset_duration):
                if offset_Q:
                    self.button_colors[i + 8 + 1] = "magenta"

            for i in range(13, self.note_velocities.index(self.note_velocity) + 14):
                self.button_colors[i] = "blue"

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
        if pitch > 127 or velocity > 127 or probability > 1:
            return

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

    def show_sequence_info(self):
        empty_square = "\u2591"
        v_bars = ["\u2582", "\u2584", "\u2586", "\u2588"]

        n_velocity = self.note_velocities.index(self.note_velocity)
        v_symb = v_bars[n_velocity]

        msg = ""
        for i in self.note_offset_duration:
            if i:
                msg += v_symb
            else:
                msg += empty_square

        pitchmsg = f"(pitch {self.sequence_up} every {self.sequence_n} notes)"

        self._parent._parent.show_message(
            " " * 15
            + msg
            + " " * 15
            + f"{simplify_fraction(self.sequence_length, self.n_notes * 4)} BARS "
            + " " * 15
            + pitchmsg
        )

    def set_sequence_length_button(self, i):
        if i < len(self.sequence_lengths):
            self.sequence_length = self.sequence_lengths[i]

            self.show_sequence_info()

    def set_n_notes_button(self, i):
        if i > 7:
            self.n_notes = 2 * (i - 7)

            self.show_sequence_info()

    def set_note_duration_button(self, i):
        if i > 7 and i < 12:
            j = i - 8

            if j - 1 >= 0:
                prev = self.note_offset_duration[j - 1]
            else:
                prev = False

            currval = self.note_offset_duration[j]

            if j + 1 < 4:
                nex = self.note_offset_duration[j + 1]
            else:
                nex = False

            if currval:
                # only turn ON if NOT both neighbouring are ON and at least one is on
                if not (prev and nex) and sum(self.note_offset_duration) > 1:
                    self.note_offset_duration[j] = False
            else:
                # only turn ON if one neighbouring is ON
                if prev or nex:
                    self.note_offset_duration[j] = True

            offset = self.note_offset_duration.index(True)
            self.note_duration = 0
            for i in self.note_offset_duration[offset:]:
                if i:
                    self.note_duration += 0.25

            self.note_offset = offset * 0.25

            self.show_sequence_info()

    def set_note_velocity_button(self, i):
        if i > 11 and i < 16:
            self.note_velocity = self.note_velocities[i - 12]

            self.show_sequence_info()

    def get_n_notes(self):
        if self.clip is not None:
            notes, notevector = self.get_notes()
            self.n_notes = len(notes)

    def get_sequence_length(self):
        if self.clip is not None:
            try:
                # take only first 6 characters (e.b.   "1/64_Q" )
                self.sequence_length = self.sequence_names_inverted[self.clip.name[:6]]
                self._parent._parent.show_message(
                    "sequence tempo set to:     "
                    + f"{simplify_fraction(self.sequence_length, self.n_notes * 4)} BARS "
                )
            except KeyError:
                self._parent._parent.show_message(
                    "sequence tempo could not be parsed from clip-name..."
                )
                pass

    def init_sequence(self):
        # show midi-clip view when sequence is initialized
        self._parent._change_ableton_view("Detail/Clip")

        if not self.clip_slot.has_clip:
            self.clip_slot.create_clip(self.sequence_length)

            sequence = self.set_sequence()

            for i in range(16):
                self.add_note(
                    pitch=sequence[i],
                    start_time=self.sequence_length / 16 * (i + self.note_offset),
                    duration=self.sequence_length / 16 * self.note_duration,
                    velocity=int(127 * self.note_velocity),
                    velocity_deviation=0,
                    probability=1,
                    mute=False,
                )

            self.clip.name = self.sequence_names[self.sequence_length]
        self.add_handler()

    def set_sequence(self):
        notes = [self._parent._transpose_val for i in range(16)]

        if self.sequence_n > 0:
            for i in range(0, 16, self.sequence_n):
                for j in range(self.sequence_n):
                    if i + j < len(notes):
                        notes[i + j] = (
                            notes[i + j] + i // self.sequence_n * self.sequence_up
                        )
        return notes

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
