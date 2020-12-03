from BaseComponent import BaseComponent
import time
from itertools import cycle
import Live

VIEWS = (u'Browser', u'Arranger', u'Session', u'Detail', u'Detail/Clip', u'Detail/DeviceChain')


class QControlComponent(BaseComponent):
    def __init__(self, parent):
        self.__selected_track = -99
        self.__stop_clicked = -99
        self.__control_layer_1_clicked = -99
        self.__control_layer_2_clicked = -99
        self.__control_layer_3_clicked = -99
        self.__select_track_clicked = -99
        self.__shift_clicked = -99
        self.__last_selected = -1
        self.__transpose_val = 36
        self.__transpose_start = 36

        self._shift_pressed = False
        self._shift_fixed = False
        self._control_layer_1 = False
        self._control_layer_2 = False
        self._control_layer_3 = False
        self.__control_layer_permanent = False

        self._sequencer_running = False

        self._detail_cycle = cycle((u'Detail/Clip', u'Detail/DeviceChain'))
        self._view_cycle = cycle((u'Arranger', u'Session'))

        self.selected_track = None
        self.selected_track_index = 0
        self.track_offset = 0
        self.selected_scene = None
        self.selected_scene_index = 0

        self._double_tap_time = 0.5
        self._shift_color_mode = 1   # 0 = none, 1 = top row, 2 = all
        self.npads = 6               # number of pads used to play notes

        self._button_light_status = {i:'black' for i in xrange(16)}

        buttonnames = ['_'+ str(i) for i in xrange(1,17)] + \
                      ['_'+ str(i) + '_encoder' for i in xrange(1,17)] + \
                      ['_shift', '_stop', '_play', '_play_S', '_cntrl', '_chan', '_transpose_encoder']
        super(QControlComponent, self).__init__(parent, buttonnames)

        self.use_tracks = [None for i in range(self.npads)]

        self._parent.song().view.add_selected_track_listener(self.on_selected_track_changed)
        self._parent.song().view.add_selected_scene_listener(self.on_selected_scene_changed)
        self._parent.song().add_tracks_listener(self.on_selected_track_changed)
        self._parent.song().add_scenes_listener(self.on_selected_scene_changed)

        # call this once to initialize "self.use_tracks"
        self.use_slots = [[None, None] for i in range(8)]
        self.use_tracks = self._parent.song().tracks[:self.npads]
        self._select_track(0)
        self.on_selected_track_changed()

        # get list of callback-functions that trigger clip-launch lights
        self._control_3_callbacks = []
        self._control_3_blink_callbacks = []
        for i, slots in enumerate(self.use_slots):
            for j, slot in enumerate(slots):
                buttonid = 1 + i + 8*j
                cb = self._playing_state_callback(i, j, buttonid)
                blinkcb = self._blink_clip_triggered_playing(i, j, buttonid)

                # save a list of the callback-functions so that we can easily
                # remove them later
                self._control_3_callbacks.append(cb)
                self._control_3_blink_callbacks.append(blinkcb)

    def _set_color(self, buttonid, color):
        colordict = dict(black=0, red=1, blue=16, magenta=17)
        self._parent._send_midi(self._parent.QS.set_B_color(buttonid, colordict[color]))

    def _blink(self, condition=lambda: False, buttonid=1, timeout=5,
               colors=['red', 'black']):
        c = cycle(colors)
        def callback():
            if condition():
                self._set_color(buttonid, next(c))
                self._parent.schedule_message(timeout, callback)
            else:
                self._set_color(buttonid, 'black')
        # give the condition some time (1 tick) to fulfil itself
        self._parent.schedule_message(1, callback)

    def _update_lights(self):
        self.update_red_box()
        self._update_button_light_status()
        for key, val in self._button_light_status.items():
            if self._sequencer_running:
                if val in ['magenta']:
                    val = 'black'
                if val in ['blue']:
                    val = 'red'
            self._set_color(key, val)

    def _update_button_light_status(self):

        bdict = dict()

        if self._control_layer_1:
            bdict[16] = 'red'
            bdict[8] = 'black'
            bdict['shift'] = 'black'
            bdict['chan'] = 'black'

            for i, track in enumerate(self.use_tracks):
                button_up = i + 1
                button_down = i + 9

                # if there is no track, turn the lights off
                if track is None:
                    bdict[button_up] = 'black'
                    bdict[button_down] = 'black'
                    continue

                if track.can_be_armed and track.arm:
                    bdict[button_up] = 'red'
                elif track.is_foldable:
                    bdict[button_up] = 'blue'
                else:
                    bdict[button_up] = 'black'


                if track.solo and not track.mute:
                    bdict[button_down] = 'blue'
                elif track.mute and track.solo:
                    bdict[button_down] = 'red'
                elif track.mute:
                    bdict[button_down] = 'black'
                else:
                    bdict[button_down] = 'magenta'

        elif self._control_layer_2:
            bdict[16] = 'black'
            bdict[8] = 'red'
            bdict['shift'] = 'black'
            bdict['chan'] = 'black'

            used_buttons = [1, 2, 3, 6, 8, 9, 10, 11, 13, 14]
            # turn off all other lights
            for i in range(1,17):
                if i in used_buttons:
                    continue
                bdict[i] = 'black'

            bdict[1] = 'magenta'
            bdict[9] = 'magenta'

            bdict[2] = 'blue'
            bdict[10] = 'red'

            bdict[3] = 'blue'
            bdict[11] = 'red'

            if self._shift_color_mode == 0:
                bdict[6] = 'black'
            elif self._shift_color_mode == 1:
                bdict[6] = 'magenta'
            elif self._shift_color_mode == 2:
                bdict[6] = 'red'

            if self._parent.song().metronome:
                bdict[13] = 'red'
            else:
                bdict[13] = 'black'

            if self._parent.song().session_automation_record:
                bdict[14] = 'red'
            else:
                bdict[14] = 'black'

        elif self._control_layer_3:
            # red = 1 which means "on" for the "chan button" light
            # even though it's actually blue
            bdict['shift'] = 'black'
            bdict['chan'] = 'red'

            self._get_used_clipslots()
            for cb in self._control_3_callbacks:
                # call control-layer 3 callbacks to update lights
                cb()

        elif self._shift_pressed or self._shift_fixed:
            # red = 1 which means "on" for the "shift button" light
            # even though it's actually blue
            bdict['shift'] = 'red'
            bdict['chan'] = 'black'

            if self._shift_color_mode == 0:
                # turn off all lights
                for i in range(1, 17):
                    bdict[i] = 'black'
            else:
                # highlite track mute and arm status
                for i, track in enumerate(self.use_tracks):
                    button_up = i + 1
                    button_down = i + 9
                    # if there is no track, turn the lights off
                    if track is None:
                        bdict[button_up] = 'black'
                        continue

                    if track.can_be_armed and track.arm:
                        if (track.mute or track.muted_via_solo):
                            bdict[button_up] = 'magenta'
                        else:
                            bdict[button_up] = 'red'
                    elif track.is_foldable:
                        bdict[button_up] = 'blue'
                    else:
                        bdict[button_up] = 'black'

                if self._shift_color_mode == 1:

                    if self.selected_track_index == None:
                        for i in range(9, 17):
                            bdict[i] = 'black'
                    else:
                        #for i in range(9, 17):
                        for i, track in enumerate(self.use_tracks):
                            button_down = i + 9
                            if i == self.selected_track_index%self.npads:
                                # indicate selected track
                                if self.selected_track.has_audio_input:
                                    bdict[button_down] = 'red'
                                else:
                                    bdict[button_down] = 'blue'
                            else:
                                bdict[button_down] = 'black'

                # indicate control-buttons
                if self._shift_color_mode == 2:
                    bdict[8] = 'red'
                    bdict[9] = 'magenta'
                    bdict[10] = 'red'
                    bdict[11] = 'black'
                    bdict[12] = 'blue'
                    bdict[13] = 'blue'
                    bdict[14] = 'red'
                    bdict[15] = 'black'
                    bdict[16] = 'black'

        else:
            # turn off all lights on shift-release
            for i in range(1, 17):
                bdict[i] = 'black'
            bdict['shift'] = 'black'
            bdict['chan'] = 'black'

        self._button_light_status = bdict

    def on_selected_scene_changed(self):
        song = self._parent.song()

        selected_scene = song.view.selected_scene
        all_scenes = song.scenes
        current_index = list(all_scenes).index(selected_scene)

        self.selected_scene = selected_scene
        self.selected_scene_index = current_index
        self.selected_clip_slot = song.view.highlighted_clip_slot
        # update clip-slot listeners
        if self._control_layer_3:
            self._add_control_3_listeners()
        self._update_lights()

    def on_selected_track_changed(self):
        '''
        update the tracks to focus on the "self.npads" relevant tracks
        '''
        song = self._parent.song()
        #all_tracks = song.tracks
        all_tracks = []
        for track in list(song.tracks):
            if track.is_grouped:
                group = track.group_track
                if group.fold_state is True:
                    continue
                else:
                    all_tracks.append(track)
            else:
                all_tracks.append(track)

        self.all_tracks = all_tracks

        selected_track = song.view.selected_track
        current_index = (list(all_tracks) + list(song.return_tracks) + [song.master_track]).index(selected_track)
        self.track_offset = int(current_index / self.npads) * (self.npads)

        if selected_track in all_tracks:
            self.selected_clip_slot = song.view.highlighted_clip_slot
            self.selected_track = selected_track
            self.selected_track_index = all_tracks.index(selected_track)
        else:
            self.selected_clip_slot = None
            self.selected_track = None
            self.selected_track_index = None


        self.use_tracks = [None for i in range(self.npads)]
        ntrack = 0
        for track in all_tracks[self.track_offset:]:
            self.use_tracks[ntrack] = track
            ntrack += 1

            if ntrack >= self.npads:
                break

        for i, track in enumerate(self.use_tracks):
            if track is not None and track.can_be_armed:
                if not track.arm_has_listener(self._update_lights):
                    track.add_arm_listener(self._update_lights)
                if not track.mute_has_listener(self._update_lights):
                    track.add_mute_listener(self._update_lights)

        # update clip-slot listeners
        if self._control_layer_3:
            self._add_control_3_listeners()
        self._update_lights()

    def _get_used_clipslots(self):
        use_slots = [[None, None] for i in range(8)]
        scene_index = self.selected_scene_index
        for i, track in enumerate(self.use_tracks):
            if track is not None:
                slots = list(track.clip_slots)
                nslots = len(slots)
                if nslots > scene_index:
                    use_slots[i][0] = slots[scene_index]
                if nslots > scene_index + 1:
                    use_slots[i][1] = slots[scene_index + 1]
        self.use_slots = use_slots

    def _play_slot(self, trackid, slotid):
        clip_slot = self.use_slots[trackid][slotid]
        if self._shift_pressed:
            track = self.use_tracks[trackid]
            if track.is_foldable:
                if track.fold_state == True:
                    track.fold_state = False
                else:
                    track.fold_state = True
                self.on_selected_track_changed()
        else:
            if clip_slot is not None and (clip_slot.has_clip or clip_slot.is_group_slot):
                clip_slot.fire()

        # if slotid == 1:
        #     # automatically select the next slot if the lower slot is
        #     # activated
        #     self._select_next_scene(create_new_scenes=False)

        self._update_lights()

    def update_red_box(self):
        width = len(self.use_tracks)
        if self._control_layer_3:
            height = 2
        else:
            height = 1

        include_returns = False
        self._parent._c_instance.set_session_highlight(self.track_offset,
                                                       self.selected_scene_index,
                                                       width,
                                                       height,
                                                       include_returns)

    def _blink_clip_triggered_playing(self, track_id, slot_id, buttonid=1):
        def blinkcb():
            c = cycle(['red', 'black'])
            def callback():
                self._get_used_clipslots()

                clip_slot = self.use_slots[track_id][slot_id]
                if clip_slot is None:
                    return
                if clip_slot.has_clip or clip_slot.is_group_slot:
                    if (not clip_slot.is_playing and clip_slot.is_triggered):
                        self._set_color(buttonid, next(c))
                        self._parent.schedule_message(1, callback)
                    else:
                        self._playing_state_callback(track_id, slot_id, buttonid)
            callback()
        return blinkcb

    def _playing_state_callback(self, track_id, slot_id, buttonid=1):
        def callback():
            self._get_used_clipslots()
            clip_slot = self.use_slots[track_id][slot_id]

            if clip_slot is None:
                self._set_color(buttonid, 'black')
                return
            if clip_slot.is_playing:
                self._set_color(buttonid, 'red')
            elif clip_slot.is_group_slot and clip_slot.controls_other_clips:
                self._set_color(buttonid, 'magenta')
            elif clip_slot.has_clip:
                self._set_color(buttonid, 'blue')
            else:
                self._set_color(buttonid, 'black')
        return callback

    def _add_control_3_listeners(self):
        cbs = iter(self._control_3_callbacks)
        blinkcbs = iter(self._control_3_blink_callbacks)

        # remove old listeners
        self._remove_control_3_listeners()
        # get new clip slots
        self._get_used_clipslots()
        # attach new listeners
        for i, slots in enumerate(self.use_slots):
            for j, slot in enumerate(slots):
                cb = next(cbs)
                blinkcb = next(blinkcbs)

                if slot is None:
                    continue

                track = self.use_tracks[i]
                if track is not None:
                    if not track.fired_slot_index_has_listener(cb):
                        track.add_fired_slot_index_listener(cb)

                if not slot.is_triggered_has_listener(blinkcb):
                    slot.add_is_triggered_listener(blinkcb)
                if not slot.has_clip_has_listener(cb):
                    slot.add_has_clip_listener(cb)
                if not slot.playing_status_has_listener(cb):
                    slot.add_playing_status_listener(cb)

    def _remove_control_3_listeners(self):
        cbs = iter(self._control_3_callbacks)
        blinkcbs = iter(self._control_3_blink_callbacks)
        for i, slots in enumerate(self.use_slots):
            for j, slot in enumerate(slots):
                cb = next(cbs)
                blinkcb = next(blinkcbs)

                if slot is None:
                    continue

                track = self.use_tracks[i]
                if track is not None:
                    if track.fired_slot_index_has_listener(cb):
                        track.remove_fired_slot_index_listener(cb)

                if slot.is_triggered_has_listener(blinkcb):
                    slot.remove_is_triggered_listener(blinkcb)
                if slot.has_clip_has_listener(cb):
                    slot.remove_has_clip_listener(cb)
                if slot.playing_status_has_listener(cb):
                    slot.remove_playing_status_listener(cb)

    def _add_control_2_listeners(self):
        song = self._parent.song()

        if not song.metronome_has_listener(self._update_lights):
            song.add_metronome_listener(self._update_lights)
        if not song.session_automation_record_has_listener(self._update_lights):
            song.add_session_automation_record_listener(self._update_lights)

    def _remove_control_2_listeners(self):
        song = self._parent.song()

        if song.metronome_has_listener(self._update_lights):
            song.remove_metronome_listener(self._update_lights)
        if song.session_automation_record_has_listener(self._update_lights):
            song.remove_session_automation_record_listener(self._update_lights)

    ###################################################

    def _1_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._arm_track(0)
            elif self._control_layer_2:
                self._redo()
            elif self._control_layer_3:
                self._play_slot(0, 0)
            elif self._shift_pressed or self._shift_fixed:
                self._select_track(0)
        else:
            self._update_lights()

    def _2_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._arm_track(1)
            elif self._control_layer_2:
                self._duplicate_track()
            elif self._control_layer_3:
                self._play_slot(1, 0)
            elif self._shift_pressed or self._shift_fixed:
                self._select_track(1)
        else:
            self._update_lights()

    def _3_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._arm_track(2)
            elif self._control_layer_2:
                self._duplicate_scene()
            elif self._control_layer_3:
                self._play_slot(2, 0)
            elif self._shift_pressed or self._shift_fixed:
                self._select_track(2)
        else:
            self._update_lights()

    def _4_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._arm_track(3)
            elif self._control_layer_2:
                self._change_detail_view(next(self._view_cycle))
            elif self._control_layer_3:
                self._play_slot(3, 0)
            elif self._shift_pressed or self._shift_fixed:
                self._select_track(3)
        else:
            self._update_lights()

    def _5_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._arm_track(4)
            elif self._control_layer_2:
                self._change_detail_view(next(self._detail_cycle))
            elif self._control_layer_3:
                self._play_slot(4, 0)
            elif self._shift_pressed or self._shift_fixed:
                self._select_track(4)
        else:
            self._update_lights()


    def _change_detail_view(self, view):
        assert view in VIEWS
        app_view = self._parent.application().view
        if view == u'Detail/DeviceChain' or u'Detail/Clip':
            if not app_view.is_view_visible(u'Detail'):
                app_view.show_view(u'Detail')
        if not app_view.is_view_visible(view):
            app_view.focus_view(view)


    def _6_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._arm_track(5)
            elif self._control_layer_2:
                self._toggle_shift_lights()
            elif self._control_layer_3:
                self._play_slot(5, 0)
            elif self._shift_pressed or self._shift_fixed:
                self._select_track(5)
        else:
            self._update_lights()

    def _7_listener(self, value):
        if value > 0:
            if self.__control_layer_permanent:
                if self._shift_pressed:
                    self._select_next_track()
                else:
                    self._select_prev_scene()
        else:
            self._update_lights()

    def _8_listener(self, value):
        if value == 0:
            if abs(time.clock() - self.__control_layer_1_clicked) <= self._double_tap_time:
                self.__control_layer_permanent = True
                self._shift_fixed = False
                self._control_layer_1 = False
                self._control_layer_2 = True
                self._control_layer_3 = False
                self._add_control_2_listeners()
                self._update_lights()
                return
            else:
                if self.__control_layer_permanent:
                    if self._control_layer_2:
                        self.__control_layer_permanent = False
                        self._unpress_shift()
                    else:
                        self._shift_fixed = False
                        self._control_layer_1 = False
                        self._control_layer_2 = True
                        self._control_layer_3 = False
                        self._add_control_2_listeners()
                else:
                    self._shift_fixed = False
                    self._control_layer_1 = False
                    self._control_layer_2 = True
                    self._control_layer_3 = False
                    self._add_control_2_listeners()

            self._update_lights()
            self.__control_layer_1_clicked = time.clock()

    ###################################################

    def _9_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._mute_solo_track(0)
            elif self._control_layer_2:
                self._undo()
            elif self._control_layer_3:
                self._play_slot(0, 1)
            elif self._shift_pressed or self._shift_fixed:
                self._undo()
        else:
            self._update_lights()

    def _10_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._mute_solo_track(1)
            elif self._control_layer_2:
                self._delete_track()
            elif self._control_layer_3:
                self._play_slot(1, 1)
            elif self._shift_pressed or self._shift_fixed:
                self._delete_clip()
        else:
            self._update_lights()

    def _11_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._mute_solo_track(2)
            elif self._control_layer_2:
                self._delete_scene()
            elif self._control_layer_3:
                self._play_slot(2, 1)
        else:
            self._update_lights()

    def _12_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._mute_solo_track(3)
            elif self._control_layer_2:
                self._tap_tempo()
            elif self._control_layer_3:
                self._play_slot(3, 1)
            elif self._shift_pressed or self._shift_fixed:
                self._duplicate_clip()
        else:
            self._update_lights()

    def _13_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._mute_solo_track(4)
            elif self._control_layer_2:
                self._toggle_metronome()
            elif self._control_layer_3:
                self._play_slot(4, 1)
            elif self._shift_pressed or self._shift_fixed:
                self._duplicate_loop()
        else:
            self._update_lights()

    def _14_listener(self, value):
        if value > 0:
            if self._control_layer_1:
                self._mute_solo_track(5)
            elif self._control_layer_2:
                self._toggle_automation()
            elif self._control_layer_3:
                self._play_slot(5, 1)
            elif self._shift_pressed or self._shift_fixed:
                self._fire_record()
        else:
            self._update_lights()

    def _15_listener(self, value):
        if value > 0:
            if self.__control_layer_permanent:
                if self._shift_pressed:
                    self._select_prev_track()
                else:
                    self._select_next_scene()
        else:
            self._update_lights()

    def _16_listener(self, value):
        if value == 0:
            if abs(time.clock() - self.__control_layer_2_clicked) <= self._double_tap_time:
                self.__control_layer_permanent = True
                self._shift_fixed = False
                self._control_layer_1 = True
                self._control_layer_2 = False
                self._control_layer_3 = False
                self._remove_control_2_listeners()
                self._remove_control_3_listeners()
                self._update_lights()
                return
            else:
                if self.__control_layer_permanent:
                    if self._control_layer_1:
                        self.__control_layer_permanent = False
                        self._unpress_shift()
                    else:
                        self._shift_fixed = False
                        self._control_layer_1 = True
                        self._control_layer_2 = False
                        self._control_layer_3 = False
                        self._remove_control_2_listeners()
                        self._remove_control_3_listeners()
                else:
                    self._shift_fixed = False
                    self._control_layer_1 = True
                    self._control_layer_2 = False
                    self._control_layer_3 = False
                    self._remove_control_2_listeners()
                    self._remove_control_3_listeners()

            self._update_lights()
            self.__control_layer_2_clicked = time.clock()

    ###################################################

    def _fire_record(self):
        clip_slot = self._parent.song().view.highlighted_clip_slot
        if clip_slot is None: return

        if clip_slot.has_clip and (clip_slot.is_playing or clip_slot.is_recording):
            if self._parent.song().session_record == False:
                self._parent.song().session_record = True
        else:
            clip_slot.fire()
            self._blink_fire_record(clip_slot, 15)

    def _blink_fire_record(self, clip_slot, buttonid=1):
        c = cycle(['red', 'black'])
        def callback():
            if clip_slot is None: return
            if clip_slot.is_triggered:
                self._set_color(buttonid, next(c))
                self._parent.schedule_message(1, callback)
            elif clip_slot.is_recording:
                self._set_color(buttonid, 'red')
                self._parent.schedule_message(20, lambda: self._set_color(buttonid, 'black'))
            else:
                self._set_color(buttonid, 'black')

        # give the condition some time (1 tick) to fulfil itself
        self._parent.schedule_message(1, callback)

    def _duplicate_loop(self):
        clip_slot = self._parent.song().view.highlighted_clip_slot
        if clip_slot is None: return
        if clip_slot.has_clip:
            clip_slot.clip.duplicate_loop()

    def _duplicate_track(self):
        song = self._parent.song()
        # find the track-index  explicitly since the duplicate_track function
        # uses a different indexing than QControl!
        selected_track = song.view.selected_track
        if self.selected_track in self.all_tracks:
            if isinstance(selected_track, Live.Track.Track) and selected_track not in list(song.return_tracks):
                selected_track_index = (list(song.tracks) + list(song.return_tracks)).index(selected_track)
                try:
                    song.duplicate_track(selected_track_index)
                except Live.Base.LimitationError:
                    self._parent.show_message('unable to duplicate... track limit reached!')
                except RuntimeError:
                    self._parent.show_message('duplication of track did not work...')

    def _delete_track(self):
        song = self._parent.song()
        # find the track-index  explicitly since the duplicate_track function
        # uses a different indexing than QControl!
        selected_track = song.view.selected_track
        if selected_track is not None:
            selected_track_index = (list(song.tracks) + list(song.return_tracks)).index(selected_track)

            if selected_track_index not in [song.master_track]:
                try:
                    song.delete_track(selected_track_index)
                except RuntimeError:
                    self.show_notification('deletion of track failed')

    def _duplicate_scene(self):
        song = self._parent.song()
        # find the index in here to avoid issues
        selected_scene_index = list(song.scenes).index(song.view.selected_scene)
        if selected_scene_index is not None:
            song.duplicate_scene(selected_scene_index)

    def _delete_scene(self):
        song = self._parent.song()

        # find the index in here to avoid issues
        selected_scene_index = list(song.scenes).index(song.view.selected_scene)

        if selected_scene_index is not None:
            self._parent.song().delete_scene(selected_scene_index)

    def _delete_clip(self):
        clip_slot = self._parent.song().view.highlighted_clip_slot
        if clip_slot is None:
            return
        if clip_slot.has_clip:
            clip_slot.delete_clip()

    def _stop_clip(self):
        # if shift is pressed, stop all clips and stop playing
        if self._shift_pressed:
            self._parent.song().stop_all_clips()
            self._parent.song().stop_playing()
        else:
            # in case the currently selected clip is recording, turn off overdub
            # (to be able to stop overdubbing with the stop-button)
            if self.selected_clip_slot.is_recording:
                if self._parent.song().session_record == True:
                    self._parent.song().session_record = False
            elif self.selected_clip_slot.is_playing:
                self.selected_clip_slot.stop()
            # set the time when stop was last clicked (in seconds)
            self.__stop_clicked = time.clock()

    def _duplicate_clip(self):
        all_scenes = self._parent.song().scenes
        # duplicate the clip slot
        if self.selected_track is None:
            return
        duplicated_id = self.selected_track.duplicate_clip_slot(self.selected_scene_index)
        duplicated_slot = all_scenes[duplicated_id]
        # move to the duplicated clip_slot
        self._parent.song().view.selected_scene = duplicated_slot

        if not self._parent.song().view.highlighted_clip_slot.is_playing:
            # force legato ensures that the playing-position of the duplicated
            # loop is continued from the previous clip
            self._parent.song().view.highlighted_clip_slot.fire(force_legato=True)

    def _select_track(self, trackid):
        track = self.use_tracks[trackid]
        if track is not None:
            self._parent.song().view.selected_track = track

            # on arm the track on double-click
            if abs(time.clock() - self.__select_track_clicked) <= self._double_tap_time and self.__last_selected == trackid:
                self._arm_track(trackid)
            self.__select_track_clicked = time.clock()
            self.__last_selected = trackid

    def _arm_track(self, trackid):
        track = self.use_tracks[trackid]
        if track is not None:
            if track.can_be_armed:
                if track.arm == True:
                    track.arm = False
                else:
                    track.arm = True
            elif track.is_foldable:
                if track.fold_state == True:
                    track.fold_state = False
                else:
                    track.fold_state = True
                self.on_selected_track_changed()

    def _mute_track(self, trackid):
        track = self.use_tracks[trackid]
        if track is not None:
            if track.mute:
                track.mute = False
            else:
                track.mute = True

    def _solo_track(self, trackid):
        track = self.use_tracks[trackid]
        if track is not None:
            if track.solo:
                track.solo = False
            else:
                track.solo = True

    def _mute_solo_track(self, trackid):
        if self._shift_pressed and self._control_layer_1:
            self._solo_track(trackid)
        else:
            self._mute_track(trackid)

    def _toggle_metronome(self):
        if self._parent.song().metronome == True:
            self._parent.song().metronome = False
        else:
            self._parent.song().metronome = True

    def _toggle_automation(self):
        if self._parent.song().session_automation_record == True:
            self._parent.song().session_automation_record = False
        else:
            self._parent.song().session_automation_record = True

    def _tap_tempo(self):
        self._parent.song().tap_tempo()

    def _undo(self):
        self._parent.song().undo()

    def _redo(self):
        self._parent.song().redo()

    def _add_handler(self):
        for i in list(range(1,17)) + ['chan']:
            try:
                getattr(self, '_'+str(i)+'_button').remove_value_listener(getattr(self, '_'+str(i)+'_listener'))
                getattr(self, '_'+str(i)+'_button').add_value_listener(getattr(self, '_'+str(i)+'_listener'))
            except:
                self._parent.log_message('there was something wrong while trying to add button listeners!')
                pass

    def _remove_handler(self):
        for i in list(range(1,17)) + ['chan']:
            try:
                getattr(self, '_'+str(i)+'_button').remove_value_listener(getattr(self, '_'+str(i)+'_listener'))
            except:
                self._parent.log_message('there was something wrong during removal of listeners!')
                pass

    def _chan_listener(self, value):
        if value == 0:
            if abs(time.clock() - self.__control_layer_3_clicked) <= self._double_tap_time:
                self.__control_layer_permanent = True
                self._shift_fixed = False
                self._control_layer_1 = False
                self._control_layer_2 = False
                self._control_layer_3 = True
                self._add_control_3_listeners()
                self._update_lights()
                return
            else:
                if self.__control_layer_permanent:
                    if self._control_layer_3:
                        self.__control_layer_permanent = False
                        self._unpress_shift()
                    else:
                        self._shift_fixed = False
                        self._control_layer_1 = False
                        self._control_layer_2 = False
                        self._control_layer_3 = True
                        self._add_control_3_listeners()
                else:
                    self._shift_fixed = False
                    self._control_layer_1 = False
                    self._control_layer_2 = False
                    self._control_layer_3 = True
                    self._add_control_3_listeners()
            self.__control_layer_3_clicked = time.clock()

        self._update_lights()

    def _play_listener(self, value):
        if value > 0:
            if self._sequencer_running:
                self._sequencer_running = False
            else:
                self._sequencer_running = True
        self._update_lights()

    def _stop_listener(self, value):
        if value > 0:
            self._stop_clip()

        self._sequencer_running = False
        self._update_lights()

    def _unpress_shift(self):
        self._shift_pressed = False
        if not self.__control_layer_permanent:
            self._shift_fixed = False
            self._control_layer_1 = False
            self._control_layer_2 = False
            self._control_layer_3 = False

            if not self._shift_pressed:
                # remove value listeners from buttons in case shift is released
                # (so that we can play instruments if shift is not pressed)
                self._parent._device.set_enabled(True)
                self._remove_handler()
                # transpose notes back to last set transpose-val
                self._set_notes(self.__transpose_val)
                # always update lights on shift release

        # remove control-listeners (e.g. metronome, automation etc.)
        self._remove_control_2_listeners()
        self._remove_control_3_listeners()

    def _shift_listener(self, value):
        if value == 127:
            self._shift_pressed = True
            self._parent._device.set_enabled(False)
            # transpose notes to start-values
            self._set_notes(self.__transpose_start)
            # add value listeners to buttons in case shift is pressed
            self._add_handler()
        else:
            self._shift_pressed = False
            # on release
            if abs(time.clock() - self.__shift_clicked) <= self._double_tap_time * 0.5:
                # if double-tapped
                if self.__control_layer_permanent:
                    if self._shift_fixed:
                        self.__control_layer_permanent = False
                        self._unpress_shift()
                    else:
                        self._shift_fixed = True
                        self._control_layer_1 = False
                        self._control_layer_2 = False
                        self._control_layer_3 = False
                        self._remove_control_2_listeners()
                        self._remove_control_3_listeners()
                else:
                    self.__control_layer_permanent = True
                    self._shift_fixed = True
                    self._control_layer_1 = False
                    self._control_layer_2 = False
                    self._control_layer_3 = False
                    self._remove_control_2_listeners()
                    self._remove_control_3_listeners()
            else:
                if self.__control_layer_permanent:
                    if self._shift_fixed:
                        self.__control_layer_permanent = False
                        self._unpress_shift()
                else:
                    self._unpress_shift()

            self.__shift_clicked = time.clock()

        self._update_lights()

    #########################################################

    def _1_encoder_listener(self, value):
        trackid = 0
        if self._control_layer_1:
            self._track_volume(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 0)

    def _2_encoder_listener(self, value):
        trackid = 1
        if self._control_layer_1:
            self._track_volume(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 0)

    def _3_encoder_listener(self, value):
        trackid = 2
        if self._control_layer_1:
            self._track_volume(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 0)

    def _4_encoder_listener(self, value):
        trackid = 3
        if self._control_layer_1:
            self._track_volume(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 0)

    def _5_encoder_listener(self, value):
        trackid = 4
        if self._control_layer_1:
            self._track_volume(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 0)
        else:
            self._track_send_x(value, -1, 0)

    def _6_encoder_listener(self, value):
        trackid = 5
        if self._control_layer_1:
            self._track_volume(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 0)
        else:
            self._track_send_x(value, -1, 2)

    def _7_encoder_listener(self, value):
        if not self.__control_layer_permanent:
            if self._shift_pressed:
                self._track_volume(value, -2)
            else:
                self._track_volume(value, -1)

    def _8_encoder_listener(self, value):
        self._select_prev_next_track(value)

    #########################################################

    def _9_encoder_listener(self, value):
        trackid = 0
        if self._control_layer_1:
            self._track_pan(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 1)

    def _10_encoder_listener(self, value):
        trackid = 1
        if self._control_layer_1:
            self._track_pan(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 1)

    def _11_encoder_listener(self, value):
        trackid = 2
        if self._control_layer_1:
            self._track_pan(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 1)

    def _12_encoder_listener(self, value):
        trackid = 3
        if self._control_layer_1:
            self._track_pan(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 1)

    def _13_encoder_listener(self, value):
        trackid = 4
        if self._control_layer_1:
            self._track_pan(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 1)
        else:
            self._track_send_x(value, -1, 1)

    def _14_encoder_listener(self, value):
        trackid = 5
        if self._control_layer_1:
            self._track_pan(value, trackid)
        elif self._control_layer_2:
            self._track_send_x(value, trackid, 1)
        else:
            self._track_send_x(value, -1, 3)

    def _15_encoder_listener(self, value):
        if not self.__control_layer_permanent:
            if self._shift_pressed:
                self._track_pan(value, -2)
            else:
                self._track_pan(value, -1)

    def _16_encoder_listener(self, value):
        self._select_prev_next_scene(value)

    #########################################################

    def _track_send_x(self, value, track_id=0, send_id=0):
        accessname = '__last_access_' + str(track_id) + '_' + str(send_id)
        last_access = abs(time.clock() - getattr(self, accessname, 0))

        if track_id == -1:
            track = self._parent.song().view.selected_track
        else:
            track = self.use_tracks[track_id]

        if track is not None:
            sends = track.mixer_device.sends

            if send_id < len(sends):
                prev_value = sends[send_id].value
                if value < 65:
                    if last_access > 0.01:
                        if round(prev_value + .01, 2) <= 1:
                            sends[send_id].value = round(prev_value + .01, 2)
                    else:
                        if round(prev_value + .05, 1) <= 1:
                            sends[send_id].value = round(prev_value + .05, 1)
                elif value > 65 and prev_value > 0:
                    if last_access > 0.01:
                        if round(prev_value - .01, 2) >= 0:
                            sends[send_id].value = round(prev_value - .01, 2)
                    else:
                        if round(prev_value - .05, 1) >= 0:
                            sends[send_id].value = round(prev_value - .05, 1)

            setattr(self, accessname, time.clock())

    def _track_volume(self, value, track_id=0):
        if track_id == -1:
            track = self._parent.song().view.selected_track
        elif track_id == -2:
            track = self._parent.song().master_track
        else:
            track = self.use_tracks[track_id]

        if track is not None:
            prev_value = track.mixer_device.volume.value
            if value < 65:
                if round(prev_value + .01, 2) <= 1:
                    track.mixer_device.volume.value = round(prev_value + .01, 2)
            elif value > 65 :
                if round(prev_value - .01, 2) >= 0:
                    track.mixer_device.volume.value = round(prev_value - .01, 2)

    def _track_pan(self, value, track_id=0):
        if track_id == -1:
            track = self._parent.song().view.selected_track
        elif track_id == -2:
            track = self._parent.song().master_track
        else:
            track = self.use_tracks[track_id]

        if track is not None:
            prev_value = track.mixer_device.panning.value
            if value < 65:
                if round(prev_value + .05, 2) <= 1:
                    track.mixer_device.panning.value = round(prev_value + .05, 2)
            elif value > 65 :
                if round(prev_value - .05, 2) >= -1:
                    track.mixer_device.panning.value = round(prev_value - .05, 2)

    def _toggle_shift_lights(self):
        self._shift_color_mode = (self._shift_color_mode + 1)%3
        self._update_lights()

    def _transpose_encoder_listener(self, value):
        if not self.__control_layer_permanent and not self._shift_pressed:
            self._transpose(value)

    def _transpose(self, value, interval=4):
        tval = self.__transpose_val
        if value < 64:
            if tval <= 126-15:
                tval = (tval + 1)
        else:
            if tval > 0:
                tval = (tval - 1)

        self.__transpose_val = tval

        if tval%interval == 0:
            self._set_notes(tval)
            # ---------------
            # indicate the transposed note via button lights
            buttonid = tval/interval
            usebuttons = [1,2,3,4,5,6,9,10,11,12,13,14]
            b = usebuttons[int(buttonid%len(usebuttons))]
            if buttonid%3 == 0:
                # blink red if lower left button is C0, C1, C2 etc.
                self._set_color(b, 'red')
            else:
                self._set_color(b, 'blue')
            def turnofflight_callback(b, color):
                def callback():
                        self._set_color(b, color)
                return callback
            self._parent.schedule_message(2, turnofflight_callback(b, 'black'))
            # -------------

    def _set_notes(self, start):
        # set midi-notes of buttons to start + (0-15)
        for i in range(16):
            decval = (start + i)%127
            button = i + 1

            if button > 8:
                button = button - 8
            else:
                button = button + 8

            self._parent._send_midi(self._parent.QS.set_B_cc(button, decval))

    def _select_next_scene(self, create_new_scenes=True):
        song = self._parent.song()
        selected_scene = song.view.selected_scene
        all_scenes = song.scenes
        if selected_scene != all_scenes[-1]:
            song.view.selected_scene = all_scenes[self.selected_scene_index + 1]
        else:
            if create_new_scenes is True:
                # create new scenes in case we are at the end
                song.create_scene(-1)
                song.view.selected_scene = all_scenes[self.selected_scene_index + 1]

    def _select_prev_scene(self):
        song = self._parent.song()
        selected_scene = song.view.selected_scene
        all_scenes = song.scenes
        if selected_scene != all_scenes[0]:
            index = list(all_scenes).index(selected_scene)
            song.view.selected_scene = all_scenes[index - 1]

        self.on_selected_scene_changed()

    def _select_prev_next_scene(self, value):
        if value < 65:
            self._select_next_scene(create_new_scenes=False)
        elif value > 65:
            self._select_prev_scene()

    def _select_prev_track(self):
        song = self._parent.song()
        tracks_and_returns = self.all_tracks + list(song.return_tracks) + [song.master_track]
        selected_track = song.view.selected_track
        assert selected_track in tracks_and_returns
        index = list(tracks_and_returns).index(selected_track)
        if selected_track != tracks_and_returns[0]:
            song.view.selected_track = tracks_and_returns[index - 1]

        self.on_selected_track_changed()

    def _select_next_track(self):
        song = self._parent.song()
        tracks_and_returns = self.all_tracks + list(song.return_tracks) + [song.master_track]
        selected_track = song.view.selected_track
        assert selected_track in tracks_and_returns
        index = list(tracks_and_returns).index(selected_track)
        if selected_track != tracks_and_returns[-1]:
            song.view.selected_track = tracks_and_returns[index + 1]

    def _select_prev_next_track(self, value):
        if value < 65:
            self._select_next_track()
        elif value > 65:
            self._select_prev_track()
