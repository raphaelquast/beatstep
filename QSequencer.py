import Live
from .QSetup import QSetup
from itertools import cycle

# class QSequencer(ControlSurface):
class QSequencer(object):
    def __init__(self, parent):
        self._parent = parent

        self._encoder_up_counter = {i: 0 for i in range(16)}
        self._encoder_down_counter = {i: 0 for i in range(16)}
        self.QS = QSetup()
        self.change_property = "pitch"
        self.up_down = True
        self.change_interval = 1
        self.sensitivity = 10
        self.change_min = 0
        self.change_max = 128
        self.button_colors = {}

        self.blinkcolor = "blue"
        self.mutecolor = "black"
        self.notecolor = "magenta"

        self._activeslot = 1

    @property
    def song(self):
        return self._parent._parent.song()

    @property
    def clip_slot(self):
        return self.song.view.highlighted_clip_slot

    @property
    def clip(self):
        if self.clip_slot.has_clip:
            return self.clip_slot.clip
        else:
            return None

            # -------------------------------------------

    def _blink_playing(self):
        def blinkcb():
            def callback():
                clip_slot = self.clip_slot
                if clip_slot is None:
                    self._parent._update_lights()
                    return

                i = 1 + (int(self.clip.playing_position) % 16)

                if self._activeslot == i:
                    self._parent._parent.schedule_message(
                        480 / (self.song.tempo * 4), callback
                    )
                    return
                else:
                    if clip_slot.has_clip and clip_slot.is_playing:
                        self._parent._update_lights()

                        self.get_button_colors()
                        c = cycle([self.blinkcolor, self.button_colors[i]])

                        # blink only if slot has changed
                        self._parent._set_color(i, next(c))
                        self._parent._parent.schedule_message(
                            480 / (self.song.tempo * 4), callback
                        )

                    else:
                        # update lights in case the callback is released while the
                        # control-layer has already been changed
                        self._parent._update_lights()

                self._activeslot = i

            callback()

        return blinkcb

    def set_change_properties(self, i):
        if i == 0:
            self._blink_playing()()
            self.change_property = "pitch"
            self.change_interval = 1
            self.change_min = 0
            self.change_max = 128
            self.sensitivity = 8
        elif i == 1:
            self.change_property = "velocity"
            self.change_interval = 1
            self.sensitivity = 1
            self.change_min = 0
            self.change_max = 128
        elif i == 2:
            self.change_property = "start_time"
            self.change_interval = 0.05
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 9999
        elif i == 3:
            self.change_property = "duration"
            self.change_interval = 0.05
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 128
        elif i == 4:
            self.change_property = "velocity_deviation"
            self.change_interval = 1
            self.sensitivity = 1
            self.change_min = -128
            self.change_max = 128
        elif i == 5:
            self.change_property = "probability"
            self.change_interval = 0.05
            self.sensitivity = 5
            self.change_min = 0
            self.change_max = 100

    def button_callback(self, i):
        """
        the callback for button i (e.g. 1 - 16)
        """
        self.set_change_properties(i)

        if self.clip is not None:
            self.clip.select_all_notes()
            self.modify_note(
                i=i,
                mute=not self.get_note_specs(i, "mute"),
            )
        self.get_button_colors()

    def change_note_property(self, i, up_down):
        kwargs = {"i": i}

        if up_down:
            kwargs[self.change_property] = min(
                self.get_note_specs(i, self.change_property) + self.change_interval,
                self.change_max,
            )
        else:
            kwargs[self.change_property] = max(
                self.get_note_specs(i, self.change_property) - self.change_interval,
                self.change_min,
            )

        self.modify_note(**kwargs)

    def encoder_callback(self, i, value):
        up_down = value < 64

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

        notevector, notes = self.get_notes()

        if notevector is not None:
            for i, note in enumerate(notes):
                if note.mute:
                    self.button_colors[i + 1] = self.mutecolor
                else:
                    self.button_colors[i + 1] = self.notecolor

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
        get the notes of the first 16 beats of the current clip
        """
        if self.clip is not None:
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

    def init_sequence(self):
        # note = (pitch, time, duration, velocity, mute_state)
        if not self.clip_slot.has_clip:
            self.clip_slot.create_clip(16)
            for i in range(16):
                self.add_note(
                    pitch=64,
                    start_time=i,
                    duration=1 / 2,
                    velocity=50,
                    velocity_deviation=0,
                    probability=1,
                    mute=False,
                )

        app = self._parent._parent.application()

        app.view.show_view("Detail/Clip")

        self.get_button_colors()
        self._parent._update_lights()

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
