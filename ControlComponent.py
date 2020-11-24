from BaseComponent import BaseComponent
from functools import partial
from _Framework.ButtonElement import Color
import Live
import time


class ControlComponent(BaseComponent):
    def __init__(self, parent):

        buttonnames = ['_'+ str(i) for i in xrange(1,17)] + ['_shift', '_stopall']

        super(ControlComponent, self).__init__(parent, buttonnames)

        self._shift_pressed = False
        self._shift_fixed = False
        self._control_layer = False


        self.npads = 7 # how many pads are there?
        self.use_tracks = [None for i in range(self.npads)]

        self._parent.song().view.add_selected_track_listener(self.on_selected_track_changed)
        self._parent.song().add_tracks_listener(self.on_selected_track_changed)

        # call this once to initialize "self.use_tracks"
        self.use_tracks = self._parent.song().tracks[:self.npads]
        #self.on_selected_track_changed()

        self.__selected_track = -99
        self.__stop_clicked = 0

    def _stopall_listener(self, value):
        self._parent.show_message('lets stop all !')


    def _update_lights(self):

        if self._shift_fixed:
            getattr(self, '_' + str(8) + '_button').send_value(0)
            getattr(self, '_' + str(16) + '_button').send_value(127)

            for i, track in enumerate(self.use_tracks):
                button_up = getattr(self, '_' + str(i + 1) + '_button')
                button_down = getattr(self, '_' + str(i + 9) + '_button')

                if button_up is not None and button_down is not None:
                    # if there is no track, turn the lights off
                    if track is None:
                        button_up.send_value(0)
                        button_down.send_value(0)
                        continue

                    if not track.mute:
                        button_up.send_value(127)
                    else:
                        button_up.send_value(0)

                    if track.arm:
                        button_down.send_value(127)
                    else:
                        button_down.send_value(0)

        elif self._control_layer:
            getattr(self, '_' + str(8) + '_button').send_value(127)
            getattr(self, '_' + str(16) + '_button').send_value(0)

            used_buttons = [8, 11, 13]
            # turn off all other lights
            for i in range(1,17):
                if i in used_buttons:
                    continue
                button = getattr(self, '_' + str(i) + '_button')
                button.send_value(0)

            if self._parent.song().metronome:
                self._13_button.send_value(127)
            else:
                self._13_button.send_value(0)

            if self._parent.song().session_automation_record:
                self._11_button.send_value(127)
            else:
                self._11_button.send_value(0)


        elif self._shift_pressed:
            for i, track in enumerate(self.use_tracks):
                button_up = getattr(self, '_' + str(i + 1) + '_button')
                button_down = getattr(self, '_' + str(i + 9) + '_button')

                if button_up is not None and button_down is not None:
                    # if there is no track, turn the lights off
                    if track is None:
                        button_up.send_value(0)
                        button_down.send_value(0)
                        continue

                    if track.arm:
                        button_up.send_value(127)
                    else:
                        button_up.send_value(0)
        else:
            # turn off all lights on shift-release
            for i in range(1, 17):
                button = getattr(self, '_' + str(i) + '_button')
                if button is not None:
                    button.send_value(0)

    def on_selected_track_changed(self):
        '''
        update the tracks to focus on the 8 relevant tracks
        '''
        try:
            all_tracks = self._parent.song().tracks
            selected_track = self._parent.song().view.selected_track
            current_index = list(all_tracks).index(selected_track)
            slotid = int(current_index / self.npads) * (self.npads)
        except:
            # there will be an error in case a return or master-track is selected
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
                self._mute_track(0)
            elif self._control_layer:
                self._redo()
            elif self._shift_pressed:
                self._select_track(0)
        else:
            self._update_lights()

    def _2_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_track(1)
            elif self._shift_pressed:
                self._select_track(1)
        else:
            self._update_lights()

    def _3_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_track(2)
            elif self._shift_pressed:
                self._select_track(2)
        else:
            self._update_lights()

    def _4_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_track(3)
            elif self._control_layer:
                self._delete_track()
            elif self._shift_pressed:
                self._select_track(3)
        else:
            self._update_lights()

    def _5_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_track(4)
            elif self._shift_pressed:
                self._select_track(4)
        else:
            self._update_lights()

    def _6_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_track(5)
            elif self._control_layer:
                self._delete_scene()
            elif self._shift_pressed:
                self._select_track(5)
        else:
            self._update_lights()

    def _7_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._mute_track(6)
            elif self._shift_pressed:
                self._select_track(6)
        else:
            self._update_lights()

    def _8_listener(self, value):
        if value == 0:
            if self._control_layer:
                self._control_layer = False
                self._shift_fixed = False
                self._shift_pressed = False
                self._update_lights()
                self._remove_control_listeners()
                self._remove_handler()
            else:
                self._shift_fixed = False
                self._control_layer = True
                self._add_control_listeners()
                self._update_lights()
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
                self._tap_tempo()
            elif self._shift_pressed:
                self._delete_clip()
        else:
            self._update_lights()

    def _11_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(2)
            elif self._control_layer:
                self._toggle_automation()
            elif self._shift_pressed:
                self._stop_clip()
        else:
            self._update_lights()

    def _12_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(3)
            elif self._control_layer:
                self._duplicate_track()
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
                self._duplicate_scene()
            elif self._shift_pressed:
                self._duplicate_clip()
        else:
            self._update_lights()

    def _15_listener(self, value):
        if value > 0:
            if self._shift_fixed:
                self._arm_track(6)
            if self._control_layer:
                self._duplicate_track()
            elif self._shift_pressed:

                self._fire_record()

        else:
            self._update_lights()

    def _16_listener(self, value):
        if value == 0:
            if self._shift_fixed:
                self._shift_fixed = False
                self._control_layer = False
                self._shift_pressed = False
                self._update_lights()
                self._remove_handler()

            else:
                self._control_layer = False
                self._shift_fixed = True
                self._update_lights()

    ###################################################


    def _fire_record(self):
        clip_slot = self._parent.song().view.highlighted_clip_slot

        if clip_slot.has_clip and (clip_slot.is_playing or clip_slot.is_recording):
            if self._parent.song().session_record == False:
                self._parent.song().session_record = True
        else:
            clip_slot.fire()

    def _duplicate_loop(self):
        clip_slot = self._parent.song().view.highlighted_clip_slot

        try:
            clip_slot.clip.duplicate_loop()
        except:
            pass

    def _duplicate_track(self):

        selected_track = self._parent.song().view.selected_track
        all_tracks = self._parent.song().tracks
        current_index = list(all_tracks).index(selected_track)

        self._parent.song().duplicate_track(current_index)

    def _delete_track(self):

        selected_track = self._parent.song().view.selected_track
        all_tracks = self._parent.song().tracks
        current_index = list(all_tracks).index(selected_track)

        self._parent.song().delete_track(current_index)

    def _duplicate_scene(self):

        selected_scene = self._parent.song().view.selected_scene
        all_scenes = self._parent.song().scenes
        current_index = list(all_scenes).index(selected_scene)

        self._parent.song().duplicate_scene(current_index)

    def _delete_scene(self):

        selected_track = self._parent.song().view.selected_track
        all_tracks = self._parent.song().tracks
        current_index = list(all_tracks).index(selected_track)

        self._parent.song().delete_scene(current_index)


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
            if track.mute == True:
                track.mute = False
            else:
                track.mute = True


    def _fire_clip(self, padid, offset=0):
        selected_track = self._parent.song().view.selected_track
        all_tracks = self._parent.song().tracks
        current_index = list(all_tracks).index(selected_track)
        slotid = int(current_index / self.npads) * (self.npads - 1)

        selectd_scene = self._parent.song().view.selected_scene
        all_scenes = list(self._parent.song().scenes)
        scene_index = all_scenes.index(selectd_scene)

        if len(all_scenes) > scene_index + offset:
            if len(all_tracks) > slotid + padid:
                clip_slot = all_scenes[scene_index + offset].clip_slots[slotid + padid]

                clip_slot.fire()


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


    def _shift_listener(self, value):
        self.__selected_track = -99

        if value == 127:
            # in case the currently selected clip is recording, turn off overdub
            # (to be able to stop overdubbing with the stop-button)
            clip_slot = self._parent.song().view.highlighted_clip_slot
            if clip_slot.is_recording:
                if self._parent.song().session_record == True:
                    self._parent.song().session_record = False


            self._shift_pressed = True

            # add value listeners to buttons in case shift is pressed
            self._add_handler()
        else:
            self._shift_pressed = False
            # remove value listeners from buttons in case shift is released
            # (so that we can play instruments if shift is not pressed)
            if not self._shift_fixed and not self._control_layer:
                self._remove_handler()
        self._update_lights()



