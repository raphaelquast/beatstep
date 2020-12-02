This is a **MIDI Remote Script** for **Ableton Live 10** and the **Arturia BeatStep** controller.  

It turns the BeatStep controller into a fully-fledged control-surface for Ableton Live, e.g.:

- arm / mute / solo / start / stop / record / delete / duplicate / overdub / undo / redo / ... 

- get indications on the status of tracks and scenes via button-lights

- ... and of course, at the same time ...  
  use the controller to play midi instruments with access to the **full range** of midi-notes!

Any comments / suggestions for improvements etc. are highly welcome!    

> Just drop an [Issue](https://github.com/raphaelquast/beatstep/issues) and I'll see what I can do!

# Summary of Assignments

![](/assignment_01.png)

# Installation

To use this script, simply copy the contents into a folder named **"Beatstep_custom"** within the MIDI Remote scripts folder of Ableton Live (located at `..install-dir..\Resources\MIDI Remote Scripts`) and then select the **Beatstep_custom** device as control-surface in the MIDI-tab of the preferences. 
(make sure to activate both `track`and `remote` for this device!)

---

# More detailed explanations on the assignments:

The script will set all encoders and buttons to send messages on the Midi-channel 10.  
To indicate a successful setup, the top-row will light up red and blue (about 2 seconds after plugin).

## Buttons:

The `shift-button` is used to activate the control-features.  
`shift` + `button 8` and `shift` + `button 16` is used to activate different control-layers.   
(**double-tap**  to make the control-layers remain activated until the activation button is pressed again!)  

## Encoder:

The `transpose-slider` transposes the note-assignments of the buttons.
(a red button-colour indicates that the lower-left button is at the note C-2, C-1, C0, C1, etc. )

- `encoder 8` : track-selection (left-right)

- `encoder 16` : scene selection (up-down)

- `encoder 5, 6, 13, 14` : send A, B, C, D of selected track

- `encoder 7` : volume of selected track

- `encoder 15` : pan of selected track

--- 

### If **shift** is pressed:

The lights in the first row indicate the track-arm status: 

- `red` if the track is **armed** and **not muted**
  
  - `magenta` if the track is armed but muted

- `blue` if the track represents a **track-group**

- `off` if the track is muted and **not** armed

The lights in the second indicate the currently activated clip.  (red for midi, blue for audio)  
(you can change this behaviour or turn the lights off! >> check `"scene control" + button 7`)



The assignments are as follows:

- `button 1-6`:  select track 1-6 of the currently focussed slots (red box)
  
  - double tap an already selected track to arm/unarm it
    - if the selected track is a track-group, instead fold/unfold the group

- `button 7`: select previous scene (e.g. go 1 scene up) 

- `button 8`: activate **song control** (see below)

- `button 9`: undo

- `button 10`: delete selected clip

- `button 12`: duplicate the currently selected loop

- `button 13`: duplicate the currently selected clip, and set the focus to the duplicate

- `button 14`: start recording
  
  - if the currently selected slot is empty, start recording a new clip 
  
  - if a clip is already present, overdub

- `button 15` : select next scene (if at the end, add a new scene)

- `button 16` : activate **track control** (see below)

- `encoder 8` : track-selection (left-right)

- `encoder 16` : scene selection (up-down)

- `encoder 7` : volume of master-track

- `encoder 15` : pan of master-track

---

### If "song control" is active

Most lights are simply there to help remembering the button-assignments.
The lights of `button 13` and `button 14` indicate the status of their corresponding parameter in Live 

- `red` for ON 

- `off` for off

The light of `button 7` indicates the visibility of the shift-button lights:

- `off` for no lights if `shift` is pressed

- `magenta` for only the top-row if `shift` is pressed

- `red` for all lights if `shift` is pressed



The assignments are as follows:

- `button 1` : redo last step

- `button 2` : duplicate currently selected track

- `button 3` : duplicate currently selected scene

- `button 4` : toggle between Ableton's session-view and arrangement-view

- `button 5` : toggle between showing the selected clip-details or the device-chain of the selected track

- `button 6` : change what lights will turn on if shift is pressed
  
  - see the description of the lights above for details

- `button 7` : select previous scene (e.g. go 1 scene up)

- `button 8` : get back to the normal behaviour (e.g. deactivate song control)

- `button 9` : undo last step

- `button 10` : delete currently selected track

- `button 11` : delete currently selected scene

- `button 12` : tap tempo

- `button 13` : toggle metronome

- `button 14` : toggle session automation record

- `button 16`: switch to **track control** (see below)

- the top-row of the encoders (`1-6`) control "send A"

- the bottom-row of the encoders (`9-14`) control "send B"

- `encoder 8` : track-selection (left-right)

- `encoder 16` : scene selection (up-down)

---

### If "track control" is active

The lights in the top-row indicate the arm status of the corresponding track.

- `red` if the track is armed

- `blue` if the track represents a track-group

- `off` if the track is unarmed (and no track-group)

The lights in the bottom-row indicate the mute / solo status of the corresponding track.

- `blue` for a track that is set to solo

- `magenta` for a unmuted track

- `red` if the track is both solo and muted

- `off` if the track is muted and not solo



The assignments are as follows:

- the buttons in the top row (1-6) set the **arm** (or track-group) status of the first 6 tracks in the red box

- the buttons in the bottom row (9-14) set the **mute** status of the first 6 tracks in the red box

- - holding `shift` while pressing the button will **solo** the corresponding track if **track control** is activated permanently (e.g. if the activation-button has been double-tapped)

- `button 8` : switch to **song control** (see above)  

- `button 16` : get back to the normal behaviour (e.g. deactivate track control)

- the top-row of the encoders (`1-7`) control the "track volume"

- the bottom-row of the encoders (`9-15`) control the "track pan"

- `encoder 8` : track-selection (left-right)

- `encoder 16` : scene selection (up-down)

---

# Thanks to

- [untergeek](https://www.untergeek.de/2014/11/taming-arturias-beatstep-sysex-codes-for-programming-via-ipad/) for unravelling BeatStep sysex messages

- Julien Bayle for the awesome [PythonLiveAPI_documentation](https://julienbayle.studio/PythonLiveAPI_documentation/) and some more info's ( [here](https://julienbayle.studio/ableton-live-midi-remote-scripts/) )

- Hanz Petrov for his [Introduction to the Framework-classes](https://livecontrol.q3f.org/ableton-liveapi/articles/introduction-to-the-framework-classes/) and the corresponding [remotescripts-blog](http://remotescripts.blogspot.com)

---
