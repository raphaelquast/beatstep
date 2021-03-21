import Live


class QSequencer(object):
    def __init__(self, parent):
        self._parent = parent

        self._encoder_up_counter = {i: 0 for i in range(16)}
        self._encoder_down_counter = {i: 0 for i in range(16)}

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

    def button_callback(self, i):
        """
        the callback for button i (e.g. 1 - 16)
        """

        self.modify_note(
            i=i,
            mute=not self.get_note_specs(i, "mute"),
        )

    def encoder_callback(self, i, value):
        sensitivity = 10
        self._parent._parent.show_message(str(value))

        if value < 64:
            # do this to avoid jumping around
            if self._encoder_down_counter[i] > 0:
                self._encoder_up_counter[i] = 0
                self._encoder_down_counter[i] = 0

            # increase the counter
            self._encoder_up_counter[i] += 1
            if self._encoder_up_counter[i] > sensitivity:
                self.modify_note(
                    i=i,
                    pitch=min(self.get_note_specs(i, "pitch") + 1, 128),
                )
                # reset the counter again
                self._encoder_up_counter[i] = 0

        else:
            # do this to avoid jumping around
            if self._encoder_up_counter[i] > 0:
                self._encoder_up_counter[i] = 0
                self._encoder_down_counter[i] = 0

            # increase the counter
            self._encoder_down_counter[i] += 1
            if self._encoder_down_counter[i] > sensitivity:

                self.modify_note(
                    i=i,
                    pitch=max(self.get_note_specs(i, "pitch") - 1, 0),
                )
                self._encoder_down_counter[i] = 0

    def get_button_colors(self):
        bdict = dict(
            shift="red",
            chan="red",
            store="red",
            recall="red",
        )
        for i in range(16):
            bdict[i + 1] = "black"

        notevector, notes = self.get_notes()

        if notevector is not None:
            for i, note in enumerate(notes):
                if note.mute:
                    bdict[i + 1] = "blue"
                else:
                    bdict[i + 1] = "red"

        return bdict

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
