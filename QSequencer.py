class QSequencer(object):
    def __init__(self, parent):
        self._parent = parent
        self._notes = {i: None for i in range(16)}

        for i in range(16):
            setattr(self, "_" + str(i + 1) + "_listener", self.getcb(i))

    def getcb(self, i):
        def callback(value):
            self.get_notes()
            self.mute_note(i)
            self._parent._parent.show_message(str(self._notes))

        return callback

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

    @property
    def notes(self):
        if self.clip is not None:
            self.clip.select_all_notes()
            self._parent._parent.show_message(
                str(self.clip.get_notes_extended(0, 128, 0, 16))
            )
            return self.clip.get_notes_extended(0, 128, 0, 16)

    # -------------------------------------------

    @property
    def note_pitch(self):
        return [i[0] for i in self.notes]

    @property
    def note_start(self):
        return [i[1] for i in self.notes]

    @property
    def note_duration(self):
        return [i[2] for i in self.notes]

    @property
    def note_velocity(self):
        return [i[3] for i in self.notes]

    @property
    def note_mute(self):
        return [i[4] for i in self.notes]

    # -------------------------------------------

    def init_sequence(self):
        # note = (pitch, time, duration, velocity, mute_state)
        if not self.clip_slot.has_clip:
            self.clip_slot.create_clip(16)

        self._notes = {i: (i, i / 2, 1 / 4, 100, False) for i in range(16)}

        self.clip.set_notes(tuple(self._notes.values()))

        self.get_notes()

    def set_notes(self):
        # note = (pitch, time, duration, velocity, mute_state)

        # ((67, 0.5, 0.21704181235431236, 100, False),
        #  (69, 0.25, 0.13585216866466868, 100, False))

        # self.clip.set_notes(tuple([i for i in self._notes.values() if i is not None]))
        # self.clip.select_all_notes()

        self.clip.remove_notes_extended(0, 128, 0, 16)
        self.clip.set_notes(tuple([i for i in self._notes.values() if i is not None]))

    def get_notes(self):
        self._notes = {i: None for i in range(16)}

        notes = self.notes
        n_notes = len(notes)
        for i, note in enumerate(self.notes):
            if i < n_notes:
                self._notes[i] = (
                    note.pitch,
                    note.start_time,
                    note.duration,
                    note.velocity,
                    note.mute,
                )

        # self._notes = list(self.clip.get_notes(0, 0, 16, 128))

    def set_note(self, i, val):
        if len(self._notes) < i:
            self._notes[i][0] = val
        self.set_notes()

    def set_start(self, i, val):
        if len(self._notes) < i:
            self._notes[i][1] = val
        self.set_notes()

    def set_duration(self, i, val):
        if len(self._notes) < i:
            self._notes[i][2] = val
        self.set_notes()

    def set_velocity(self, i, val):
        if len(self._notes) < i:
            self._notes[i][3] = val
        self.set_notes()

    def mute_note(self, i):
        self._notes[i] = None
        # if len(self._notes) < i:
        #    self._notes[i][4] = not self._notes[i][4]
        self.set_notes()

    def _add_handler(self):
        for i in list(range(1, 17)):  # + ['chan', 'recall', 'store']:
            try:
                getattr(self._parent, "_" + str(i) + "_button").remove_value_listener(
                    getattr(self, "_" + str(i) + "_listener")
                )
                getattr(self._parent, "_" + str(i) + "_button").add_value_listener(
                    getattr(self, "_" + str(i) + "_listener")
                )
            except Exception:
                self._parent._parent.log_message(
                    "there was something wrong while trying to add button "
                    + str(i)
                    + " listeners!"
                )
                pass

    def _remove_handler(self):
        for i in list(range(1, 17)):  # + ['chan', 'recall', 'store']:
            try:
                getattr(self._parent, "_" + str(i) + "_button").remove_value_listener(
                    getattr(self, "_" + str(i) + "_listener")
                )
            except Exception:
                self._parent._parent.log_message(
                    "there was something wrong during removal of button "
                    + str(i)
                    + " listeners!"
                )
                pass