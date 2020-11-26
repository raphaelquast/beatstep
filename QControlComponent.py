from BaseComponent import BaseComponent
import time
from itertools import cycle


class QControlComponent(BaseComponent):
    def __init__(self, parent):
        self.__selected_track = -99
        self.__stop_clicked = -99
        self.__shift_fixed_clicked = -99
        self.__control_layer_clicked = -99
        self.__transpose_val = 36
        self.__transpose_start = 36

        self._shift_pressed = False
        self._shift_fixed = False
        self._control_layer = False
        self.__control_layer_permanent = False

        self.selected_track = None
        self.selected_track_index = 0
        self.selected_scene = None
        self.selected_scene_index = 0


        buttonnames = ['_'+ str(i) for i in xrange(1,17)] + ['_'+ str(i) + '_encoder' for i in xrange(1,17)] + ['_shift', '_stop', '_transpose_encoder']

        super(QControlComponent, self).__init__(parent, buttonnames)

        self._shift_color_mode = 1   # 0 = none, 1 = top row, 2 = all

        self.npads = 7 # how many pads are there?
        self.use_tracks = [None for i in range(self.npads)]

        self._parent.song().view.add_selected_track_listener(self.on_selected_track_changed)
        self._parent.song().view.add_selected_scene_listener(self.on_selected_scene_changed)

        self._parent.song().add_tracks_listener(self.on_selected_track_changed)

        # call this once to initialize "self.use_tracks"
        self.use_tracks = self._parent.song().tracks[:self.npads]
        self._select_track(0)
        self.on_selected_track_changed()


    def _set_color(self, buttonid, color):
        colordict = dict(black=0, red=1, blue=16, magenta=17)
        # the hex-code of the buttons
        hexbutton = 111 + buttonid
        hexcolor = colordict[color]

        msg = (240, 0, 32, 107, 127, 66, 2, 0, 16, hexbutton, hexcolor, 247)

        self._parent._send_midi(msg)


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
        if self._shift_fixed:
            self._set_color(16, 'magenta')
            self._set_color(8, 'black')

            for i, track in enumerate(self.use_tracks):
                button_up = i + 1
                button_down = i + 9

                # if there is no track, turn the lights off
                if track is None:
                    self._set_color(button_up, 'black')
                    self._set_color(button_down, 'black')
                    continue

                if track.solo and not track.mute:
                    self._set_color(button_up, 'blue')
                elif track.mute and track.solo:
                    self._set_color(button_up, 'red')
                elif track.mute:
                    self._set_color(button_up, 'black')
                else:
                    self._set_color(button_up, 'magenta')

                if track.arm:
                    self._set_color(button_down, 'red')
                else:
                    self._set_color(button_down, 'black')

        elif self._control_layer:
            self._set_color(16, 'black')
            self._set_color(8, 'blue')

            used_buttons = [1, 2, 3, 7, 8, 9, 10, 11, 13, 14]
            # turn off all other lights
            for i in range(1,17):
                if i in used_buttons:
                    continue
                self._set_color(i, 'black')

            self._set_color(1, 'magenta')
            self._set_color(9, 'magenta')

            self._set_color(2, 'blue')
            self._set_color(10, 'magenta')

            self._set_color(3, 'blue')
            self._set_color(11, 'magenta')


            if self._shift_color_mode == 0:
                self._set_color(7, 'black')
            elif self._shift_color_mode == 1:
                self._set_color(7, 'magenta')
            elif self._shift_color_mode == 2:
                self._set_color(7, 'red')


            if self._parent.song().metronome:
                self._set_color(13, 'red')
            else:
                self._set_color(13, 'black')

            if self._parent.song().session_automation_record:
                self._set_color(14, 'red')
            else:
                self._set_color(14, 'black')


        elif self._shift_pressed:
            if self._shift_color_mode == 0:
                # turn off all lights
                for i in range(1, 17):
                    self._set_color(i, 'black')
            else:
                # highlite track mute and arm status
                for i, track in enumerate(self.use_tracks):
                    button_up = i + 1
                    button_down = i + 9
                    # if there is no track, turn the lights off
                    if track is None:
                        self._set_color(button_up, 'black')
                        continue

                    if track.arm:
                        if (track.mute or track.muted_via_solo):
                            self._set_color(button_up, 'magenta')
                        else:
                            self._set_color(button_up, 'red')
                    elif track.solo:
                        self._set_color(button_up, 'blue')
                    else:
                        self._set_color(button_up, 'black')

                if self._shift_color_mode == 1:
                    if self.selected_track_index == None:
                        for i in range(9, 17):
                            self._set_color(i, 'black')
                    else:
                        for i in range(9, 17):
                            if i - self.npads == self.selected_track_index%self.npads + 2:
                                # indicate selected track
                                if self.selected_track.has_audio_input:
                                    self._set_color(i, 'magenta')
                                else:
                                    self._set_color(i, 'blue')
                            else:
                                # turn off all otherlower buttons
                                self._set_color(i, 'black')


                # indicate control-buttons
                if self._shift_color_mode == 2:
                    self._set_color(8, 'magenta')
                    self._set_color(9, 'magenta')
                    self._set_color(10, 'red')
                    self._set_color(11, 'magenta')
                    self._set_color(12, 'blue')
                    self._set_color(13, 'magenta')
                    self._set_color(14, 'blue')
                    self._set_color(15, 'red')
                    self._set_color(16, 'magenta')


        elif not self._shift_fixed and not self._control_layer:
            # turn off all lights on shift-release
            for i in range(1, 17):
                self._set_color(i, 'black')

    def on_selected_scene_changed(self):
        selected_scene = self._parent.song().view.selected_scene
        all_scenes = self._parent.song().scenes
        current_index = list(all_scenes).index(selected_scene)

        self.selected_scene = selected_scene
        self.selected_scene_index = current_index

    def on_selected_track_changed(self):
        '''
        update the tracks to focus on the 7 relevant tracks
        '''
        try:
            all_tracks = self._parent.song().tracks
            selected_track = self._parent.song().view.selected_track
            current_index = list(all_tracks).index(selected_track)
            slotid = int(current_index / self.npads) * (self.npads)

            self.selected_track = selected_track
            self.selected_track_index = current_index
        except:
            # there will be an error in case a return or master-track is selected
            self.selected_track = None
            self.selected_track_index = None
            self._update_lights()
            return


        self.use_tracks = []
        for i in range(slotid, slotid + self.npads):
            if len(all_tracks) > i:
                track = all_tracks[i]
                self.use_tracks.append(track)
            else:
                self.use_tracks.append(None)

        for i, track in enumerate(self.use_tracks):
            if track is not None:
                if not track.arm_has_listener(self._update_lights):
                    track.add_arm_listener(self._update_lights)
                if not track.mute_has_listener(self._update_lights):
                    track.add_mute_listener(self._update_lights)


        self._update_lights()


    def _add_control_listeners(self):
        song = self._parent.song()

        if not song.metronome_has_listener(self._update_lights):
            song.add_metronome_listener(self._update_lights)
        if not song.session_automation_record_has_listener(self._update_lights):
            song.add_session_automation_record_listener(self._update_lights)

    def _remove_control_listeners(self):
        song = self._parent.song()

        if song.metronome_has_listener(self._update_lights):
            song.remove_metronome_listener(self._update_lights)
        if song.session_automation_record_has_listener(self._update_lights):
            song.remove_session_automation_record_listener(self._update_lights)

    ###################################################

    def _1_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_solo_track(0)
            elif self._control_layer:
                self._redo()
            elif self._shift_pressed:
                self._select_track(0)
        else:
            self._update_lights()

    def _2_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_solo_track(1)
            elif self._control_layer:
                self._duplicate_track()
            elif self._shift_pressed:
                self._select_track(1)
        else:
            self._update_lights()

    def _3_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_solo_track(2)
            elif self._control_layer:
                self._duplicate_scene()
            elif self._shift_pressed:
                self._select_track(2)
        else:
            self._update_lights()

    def _4_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_solo_track(3)
            elif self._shift_pressed:
                self._select_track(3)
        else:
            self._update_lights()

    def _5_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_solo_track(4)
            elif self._shift_pressed:
                self._select_track(4)
        else:
            self._update_lights()

    def _6_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_solo_track(5)
            elif self._control_layer:
                self._toggle_detail_clip_view()
            elif self._shift_pressed:
                self._select_track(5)
        else:
            self._update_lights()

    def _7_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_solo_track(6)
            elif self._control_layer:
                self._toggle_shift_lights()
            elif self._shift_pressed:
                self._select_track(6)
        else:
            self._update_lights()

    def _8_listener(self, value):
        if value == 0:
            if abs(time.clock() - self.__control_layer_clicked) <= 0.25:
                self.__control_layer_permanent = True
                self._shift_fixed = False
                self._control_layer = True
                self._update_lights()
                return
            else:
                self.__control_layer_permanent = False

                if self._control_layer:
                    self._control_layer = False
                    self._shift_fixed = False
                    self._shift_pressed = False
                    # transpose notes back to last set transpose-val
                    self._set_notes(self.__transpose_val)
                    self._update_lights()
                    self._remove_control_listeners()
                    self._remove_handler()

                else:
                    self._shift_fixed = False
                    self._control_layer = True
                    self._add_control_listeners()
                    self._update_lights()

            self.__control_layer_clicked = time.clock()
    ###################################################

    def _9_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(0)
            elif self._control_layer:
                self._undo()
            elif self._shift_pressed:
                self._undo()
        else:
            self._update_lights()

    def _10_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(1)
            elif self._control_layer:
                self._delete_track()
            elif self._shift_pressed:
                self._delete_clip()
        else:
            self._update_lights()

    def _11_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(2)
            elif self._control_layer:
                self._delete_scene()
            elif self._shift_pressed:
                self._stop_clip()
        else:
            self._update_lights()

    def _12_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(3)
            elif self._control_layer:
                self._tap_tempo()
            elif self._shift_pressed:
                self._duplicate_loop()
        else:
            self._update_lights()

    def _13_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(4)
            elif self._control_layer:
                self._toggle_metronome()
            elif self._shift_pressed:
                self._next_clip()
        else:
            self._update_lights()

    def _14_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(5)
            if self._control_layer:
                self._toggle_automation()
            elif self._shift_pressed:
                self._duplicate_clip()
        else:
            self._update_lights()

    def _15_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(6)
            elif self._shift_pressed:

                self._fire_record()
        else:
            self._update_lights()

    def _16_listener(self, value):
        if value == 0:

            if abs(time.clock() - self.__shift_fixed_clicked) <= 0.25:
                self.__control_layer_permanent = True
                self._shift_fixed = True
                self._control_layer = False
                self._update_lights()
                return
            else:
                self.__control_layer_permanent = False

                if self._shift_fixed:
                    self._shift_fixed = False
                    self._control_layer = False
                    self._shift_pressed = False
                    # transpose notes back to last set transpose-val
                    self._set_notes(self.__transpose_val)
                    self._update_lights()
                    self._remove_handler()
                else:
                    self._control_layer = False
                    self._shift_fixed = True
                    self._update_lights()

            self.__shift_fixed_clicked = time.clock()

    ###################################################


    def _fire_record(self):
        clip_slot = self._parent.song().view.highlighted_clip_slot

        if clip_slot.has_clip and (clip_slot.is_playing or clip_slot.is_recording):
            if self._parent.song().session_record == False:
                self._parent.song().session_record = True
        else:
            clip_slot.fire()
            self._blink_fire_record(clip_slot, 15)

    def _blink_fire_record(self, clip_slot, buttonid=1):
        c = cycle(['red', 'black'])
        def callback():
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

        try:
            clip_slot.clip.duplicate_loop()
        except:
            pass

    def _duplicate_track(self):
        if self.selected_track_index is not None:
            self._parent.song().duplicate_track(self.selected_track_index)

    def _delete_track(self):
        if self.selected_track_index is not None:
            self._parent.song().delete_track(self.selected_track_index)

    def _duplicate_scene(self):
        if self.selected_scene_index is not None:
            self._parent.song().duplicate_scene(self.selected_scene_index)

    def _delete_scene(self):
        if self.selected_scene_index is not None:
            self._parent.song().delete_scene(self.selected_scene_index)

    def _delete_clip(self):
        clip_slot = self._parent.song().view.highlighted_clip_slot
        try:
            clip_slot.delete_clip()
        except:
            pass

    def _stop_clip(self):
        # in case the button is pressed twice within 250ms, stop all clips
        if abs(time.clock() - self.__stop_clicked) <= 0.25:
            self._parent.song().stop_all_clips()
            self._parent.song().stop_playing()
        else:
            clip_slot = self._parent.song().view.highlighted_clip_slot
            clip_slot.stop()

        # set the time when stop was last clicked (in seconds)
        self.__stop_clicked = time.clock()


    def _next_clip(self):
        # get the currently selected scene ID
        scene = self._parent.song().view.selected_scene
        all_scenes = list(self._parent.song().scenes)
        scene_id = list(self._parent.song().scenes).index(scene)

        if len(all_scenes) > scene_id + 1:
            self._parent.song().view.selected_scene = all_scenes[scene_id + 1]
        else:
            self._parent.song().create_scene(-1)
            all_scenes = list(self._parent.song().scenes)
            self._parent.song().view.selected_scene = all_scenes[-1]


    def _duplicate_clip(self):

        track = self._parent.song().view.selected_track
        # get the currently selected scene ID
        scene = self._parent.song().view.selected_scene
        all_scenes = list(self._parent.song().scenes)
        scene_id = list(self._parent.song().scenes).index(scene)
        # duplicate the clip slot
        duplicated_id = track.duplicate_clip_slot(scene_id)

        duplicated_slot = all_scenes[duplicated_id]
        # move to the duplicated clip_slot
        self._parent.song().view.selected_scene = duplicated_slot

        clip_slot = self._parent.song().view.highlighted_clip_slot

        if not clip_slot.is_playing:
            # force legato ensures that the playing-position of the duplicated
            # loop is continued from the previous clip
            clip_slot.fire(force_legato=True)


    def _select_track(self, trackid):
        track = self.use_tracks[trackid]
        if track is not None:
            self._parent.song().view.selected_track = track

            # on arm the track on double-click
            if self.__selected_track == trackid:
                self._arm_track(trackid)
            self.__selected_track = trackid


    def _arm_track(self, trackid):
        track = self.use_tracks[trackid]
        if track is not None:
            if track.arm == True:
                track.arm = False
            else:
                track.arm = True


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
        if self._shift_pressed and self.__control_layer_permanent:
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
        for i in range(1,17):
            try:
                getattr(self, '_'+str(i)+'_button').remove_value_listener(getattr(self, '_'+str(i)+'_listener'))
                getattr(self, '_'+str(i)+'_button').add_value_listener(getattr(self, '_'+str(i)+'_listener'))
            except:
                pass


    def _remove_handler(self):
        for i in range(1,17):
            try:
                getattr(self, '_'+str(i)+'_button').remove_value_listener(getattr(self, '_'+str(i)+'_listener'))
            except:
                pass


    def _stop_listener(self, value):
        if value > 0:
            # in case the currently selected clip is recording, turn off overdub
            # (to be able to stop overdubbing with the stop-button)
            clip_slot = self._parent.song().view.highlighted_clip_slot
            if clip_slot.is_recording:
                if self._parent.song().session_record == True:
                    self._parent.song().session_record = False
            elif clip_slot.is_playing:
                clip_slot.stop()

        self._update_lights()


    def _shift_listener(self, value):
        self.__selected_track = -99

        if value == 127:
            # transpose notes to start-values
            self._set_notes(self.__transpose_start)
            self._shift_pressed = True
            # add value listeners to buttons in case shift is pressed
            self._add_handler()
        else:
            self._shift_pressed = False
            if not self.__control_layer_permanent:
                self._shift_fixed = False
                self._control_layer = False

            # remove value listeners from buttons in case shift is released
            # (so that we can play instruments if shift is not pressed)
            if not self._shift_fixed and not self._control_layer:
                self._remove_handler()
                # transpose notes back to last set transpose-val
                self._set_notes(self.__transpose_val)
                # always update lights on shift release
        self._update_lights()


    #########################################################

    def _1_encoder_listener(self, value):
        trackid = 0
        if self._shift_fixed:
            self._track_volume(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 0)

    def _2_encoder_listener(self, value):
        trackid = 1
        if self._shift_fixed:
            self._track_volume(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 0)

    def _3_encoder_listener(self, value):
        trackid = 2
        if self._shift_fixed:
            self._track_volume(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 0)

    def _4_encoder_listener(self, value):
        trackid = 3
        if self._shift_fixed:
            self._track_volume(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 0)

    def _5_encoder_listener(self, value):
        trackid = 4
        if self._shift_fixed:
            self._track_volume(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 0)
        else:
            self._track_send_x(value, -1, 0)

    def _6_encoder_listener(self, value):
        trackid = 5
        if self._shift_fixed:
            self._track_volume(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 0)
        else:
            self._track_send_x(value, -1, 1)

    def _7_encoder_listener(self, value):
        trackid = 6
        if self._shift_fixed:
            self._track_volume(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 1)
        elif self._shift_pressed:
            self._track_volume(value, -2)
        else:
            self._track_volume(value, -1)

    # def _8_encoder_listener(self, value):
    #     pass

    #########################################################

    def _9_encoder_listener(self, value):
        trackid = 0
        if self._shift_fixed:
            self._track_volume(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 1)

    def _10_encoder_listener(self, value):
        trackid = 1
        if self._shift_fixed:
            self._track_pan(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 1)

    def _11_encoder_listener(self, value):
        trackid = 2
        if self._shift_fixed:
            self._track_pan(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 1)

    def _12_encoder_listener(self, value):
        trackid = 3
        if self._shift_fixed:
            self._track_pan(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 1)

    def _13_encoder_listener(self, value):
        trackid = 4
        if self._shift_fixed:
            self._track_pan(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 2)
        else:
            self._track_send_x(value, -1, 2)

    def _14_encoder_listener(self, value):
        trackid = 5
        if self._shift_fixed:
            self._track_pan(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 1)
        else:
            self._track_send_x(value, -1, 3)

    def _15_encoder_listener(self, value):
        trackid = 6
        if self._shift_fixed:
            self._track_pan(value, trackid)
        elif self._control_layer:
            self._track_send_x(value, trackid, 1)
        elif self._shift_pressed:
            self._track_pan(value, -2)
        else:
            self._track_pan(value, -1)
    # def _16_encoder_listener(self, value):
    #     pass
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
                    if last_access > 0.01 and prev_value < 1:
                        sends[send_id].value = round(prev_value + .01, 2)
                    else:
                        sends[send_id].value = round(prev_value + .05, 1)
                elif value > 65 and prev_value > 0:
                    if last_access > 0.01:
                        sends[send_id].value = round(prev_value - .01, 2)
                    else:
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
                track.mixer_device.volume.value = round(prev_value + .01, 2)
            elif value > 65 :
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
                track.mixer_device.panning.value = round(prev_value + .05, 2)
            elif value > 65 :
                track.mixer_device.panning.value = round(prev_value - .05, 2)


    def _toggle_shift_lights(self):
        self._shift_color_mode = (self._shift_color_mode + 1)%3
        self._update_lights()


    def _transpose_encoder_listener(self, value):
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


    def _set_notes(self, start):
        #self._parent.show_message('transposing from  ' + str(start))
        # set midi-notes of buttons to start + (0-15)
        for i in xrange(16):
            decval = (start + i)%127

            if i > 7:
                button = 112 + i%8
            else:
                button = 120 + i%8

            msg = (240, 0, 32, 107, 127, 66, 2, 0) + (3, button, decval, 247)
            self._parent._send_midi(msg)

