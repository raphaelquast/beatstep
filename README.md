This is a **MIDI Remote Script** for **Ableton Live 10 & 11** and the **Arturia BeatStep** controller.
It turns the BeatStep controller into a fully-fledged control-surface for Ableton Live !

- select / arm / mute / solo / start / stop / record / delete / duplicate / overdub / undo / redo / ...

- use pads to start/stop/trigger clips

- get indications on the status of clips and tracks via button-LED's

- play midi instruments with access to the **full range** of midi-notes!

- ... and much more!

### Comments / suggestions / bugs?  
> Just drop an [Issue](https://github.com/raphaelquast/beatstep/issues) or start a [Discussion](https://github.com/raphaelquast/beatstep/discussions) and I'll see what I can do!  
  
... and if you like what I did here, how about buying me a coffee?  

<a href="https://www.buymeacoffee.com/raphaelquast" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;" ></a>

# Installation

To use this script, simply copy the files of the latest [release](https://github.com/raphaelquast/beatstep/releases) into a folder named **"Beatstep_Q"** within the MIDI Remote scripts folder of Ableton Live (located at `..install-dir..\Resources\MIDI Remote Scripts`) and then select the **Beatstep_Q** device as control-surface in the MIDI-tab of the preferences. (make sure to activate both `track` and `remote` for this device!)

WARNING: The script is using BeatStep's **storage bank 9** during runtime. Any configuration stored to this slot will be overwritten!

# Overlay
The overlay-design provides indications for most of the assignments as well as the original sequencer-functions.  
<sup>
(I got mine printed here: [Taktility](https://www.taktility.com/))
</sup>

![overlay-image](/BeatStep_Q_Overlay_with_image.png)

# Summary of Assignments

![assignments-image](/assignment_01.png)
---

# More detailed explanations on the assignments:

The script will set all encoders and buttons to send messages on the Midi-channel 10.  To indicate a successful setup, the top-row will light up red and blue (about 2 seconds after plugin).

- It's best to **connect the controller after Ableton started** to ensure that all settings are properly assigned.

- To ensure that the script is automatically selected (instead of the default script), rename the already existing *"Beatstep"* folder to *"_Beatstep"* (or something that it is alphabetically sorted **after** *"BeatStep_Q"*)

After initialization, you can recall any saved MIDI configuration and the control-layers will still work !


## General (click to expand)

<details><summary>:black_square_button: <strong>BUTTONS</strong></summary>

The buttons `recall`, `store`,`chan` and `shift` are used to activate the control-layers.

- to maintain the initial functionality of the buttons, the layers are activated when the buttons are **released** !

- all layers (except the *"shift-layer"*) remain activated until the corresponding button is pressed again

- the *"shift-layer"* can be activated permanently by **double-tapping** the `shift` button

- holding `shift` while pressing one of the layer-buttons will activate the layer until `shift` is released

- the *"if shift pressed"* features are only relevant if the layers are activated permanently **and** `shift` is pressed

The `stop` button can be used as follows:

- if the selected clip is currently recording: stop recording (but continue playback)

- if the selected clip is playing: trigger stop

- *"if shift pressed"* : stop ALL tracks

</details>


---

<details><summary>:white_circle: <strong>ENCODERS</strong></summary>  

The `transpose-encoder` can be used to transpose the note-assignments of the buttons.
(a red button-color indicates that the lower-left button is at the note C-2, C-1, C0, C1, etc.)

- `encoder 1-4` and `9-12` : control the first 8 parameters of the selected device

- `encoder 5, 6, 13, 14` : send A, B, C, D of selected track

- `encoder 7` : volume of selected track
  
  - *"if shift pressed"*: volume of master-track

- `encoder 15` : pan of selected track
  
  - *"if shift pressed"*: pan of master-track

- `encoder 8` : track-selection (left-right)
  
  - *"if shift pressed"* **and** a *"drum-rack"* is selected:
    
    select drum-pad slot of the viewed 16 slots

- `encoder 16` : scene selection (up-down)
  
  - *"if shift pressed"* **and** a *"drum-rack"* is selected:
    select row of viewed drum-pads

</details>

---

## Layers (click to expand)


<details>
<summary>:trumpet: <strong>SHIFT</strong></summary>  

You can always **double-tap** `shift` to re-activate the shift-layer permanently!

The lights in the first indicate the currently activated clip.
(`red` for midi, `blue` for audio and `magenta` for return tracks)

The lights in the second row indicate the track-arm status:

- `red` if the track is **armed** and **not muted**
  
  - `magenta` if the track is armed but muted

- `blue` if the track represents a **track-group**

- `off` if the track is muted and **not** armed



#### The assignments are as follows:

- `button 1-7`: select track 1-7 of the currently focussed slots (red box)
  
  - double tap an already selected track to arm/unarm it
    - if the selected track is a track-group, instead fold/unfold the group

- `button 8`: select previous scene (e.g. go 1 scene up)
  
  - if the control-layer is activated permanently, holding `shift` will switch to track-selection

- `button 9` : undo last step

- `button 10`: delete selected clip

- `button 12`: duplicate the currently selected clip and set the focus to the duplicate

- `button 13`: duplicate the currently selected loop

- `button 15`: start recording
  
  - if the currently selected slot is empty, start recording a new clip
  
  - if a clip is already present, toggle overdubbing the clip

- `button 16` : select next scene (if at the end, create a new scene)
  
  - if the control-layer is activated permanently, holding `shift` will switch to track-selection

All encoders are assigned as described above except for the `transpose-encoder`, which is now used to **select devices** in the device-chain of the selected track. (turning the `transpose-encoder` will automatically focus the view to the device-chain!)

</details>

---

<details>
<summary>:violin: <strong>CONTROL</strong></summary>  

Most lights are simply there to help remember the button-assignments.
The lights of `button 13` and `button 14` indicate the status of their corresponding parameter in Live.

- `button 13` indicates the status of the metronome (`red` for on)

- `button 14` indicates the status of "automation arm" (`red` for active)
  
  - "if shift pressed" and an automation has been overridden, the button will turn `blue`

- `button 3`, `10` and `11` will turn red if shift is pressed to highlight the alternative functionality

#### The assignments are as follows:

- `button 1` : redo last step

- `button 2` : fold / unfold selected device

- `button 3` : activate / deactivate selected device
  
  - *"if shift pressed"* : delete selected device

- `button 6` : cycle through the *"launch-quantization"* times (e.g. 1 bar, 1/2 bar, 1/8 bar etc.)
  
  - *"if shift pressed"* : turn *"launch-quantization"* off

- `button 7` : toggle between showing the selected *"clip-details"* or the *"device-chain"* of the selected track
  
  - *"if shift pressed"* : toggle between Ableton's session-view and arrangement-view

- `button 8` : select previous scene (e.g. go 1 scene up)

- - *"if shift pressed"* : select previous track

- `button 9` : undo last step

- `button 10` : duplicate selected track
  
  - "if shift pressed" : delete selected track

- `button 11` : duplicate selected scene
  
  - *"if shift pressed"* : delete selected scene

- `button 12` : tap tempo

- `button 13` : toggle metronome

- `button 14` : toggle *"session automation record"*
  
  - *"if shift-pressed"* and an automation has been overridden: *"re-enable automation"*

- `button 15` : change the assigned "pad velocity curve" (e.g. the midi velocity response of the pad)
  
  - `blue` for linear, `magenta` for logarithmic, `red` for exponential and `off` for "always max. velocity"

- `button 16` : select next scene (if at the end, create a new scene)
  
  - *"if shift-pressed"*: select next track

All encoders are assigned similar to the *"shift-layer"*.

</details>

---

<details>
<summary>:guitar: <strong>LAUNCH</strong></summary>  

In this control-layer, both button-rows (e.g. `1-7` and `9-15`) represent clip-slots.  
NOTICE: the `stop` button has a special feature in this layer (see below).

There are 2 possible ways to activate this layer:

- tap `store` to control **2 clip-slots of 7 tracks**
   - only the `store` button LED will be on
- tap `shift + store` to control **14 clip-slots of 1 track**
   - the LED's of `store`, `chan` and `recall` will be on

The button-lights indicate the status of the clip-slots, e.g.:

- `blue` indicates a slot with a clip
  - a `blue blinking` slot indicates a clip that is triggered to **stop**

- `red` indicates a clip that is playing
  - a `red blinking` slot indicates a clip that is triggered to **play**

- `magenta` indicates a group-track (it will turn `red` if a clip of the group is playing) [or indicate a triggered clip in `shift + store` mode]

- the `shift` button indicates if *"re-trigger clips"* or *"stop clips"* mode is active

#### The assignments are as follows:

- the `stop-button` toggles the behavior of the buttons (indicated by the `shift` button LED)
  
  - *"re-trigger clips"* mode (`shift` LED OFF) : tapping on an already playing clip will **re-trigger** the clip
  
  - *"stop clips"* mode (`shift` LED ON) : tapping on an already playing clip will **stop** the clip
  
  (... the *"if shift-pressed"* behavior is still similar to the other layers, e.g. *"stop all clips"*)

- `button 1-7` : launch the clips present in the top-row of the selection.
  
  - *"if shift-pressed"* : select the track to which the clip-slot belongs to
    - if the slot is a "group-slot": fold/unfold the corresponding group

- `button 8` : select previous scene (e.g. go 1 scene up)
 
  - *"if shift-pressed"*: select previous track

- `button 9-15` : same as `1-7` but for the bottom row of the selection.

- `button 16` : select next scene (if at the end, add a new scene)
  
  - *"if shift-pressed"*: select next track

All encoders are assigned similar to the *"shift-layer"*.

</details>

---

<details>
<summary>:headphones: <strong>MIX</strong></summary>  

The lights in the top-row indicate the mute / solo status of the corresponding track.

- `blue` for a track that is set to solo

- `magenta` for an unmuted track

- `red` if the track is both solo and muted

- `off` if the track is muted and not solo

The lights in the bottom-row indicate the arm status of the corresponding track.

- `red` if the track is armed

- `blue` if the track represents a track-group

- `off` if the track is unarmed (and no track-group)

#### The assignments are as follows:

- `button 1-7` : set the **mute** status of the first 6 tracks in the red box
  
  - *"if shift pressed"*: **solo** the corresponding track

- `button 9-15` : set the **arm** status of the first 7 tracks in the red box
  
  - if the track represents a group, fold / unfold the corresponding group

- `button 8` : select previous scene (e.g. go 1 scene up)
  
  - *"if shift pressed"*: select previous track

- `button 16` : select next scene (if at the end, create a new scene)
  
  - "if shift pressed" : select next track

- `encoder 1-7` : *"track volume"* of corresponding track
  
  - *"if shift pressed"* : *"send A"* of corresponding track

- `encoder 9-15` : *"track pan"* of corresponding track
  
  - *"if shift pressed"* : *"send B"* of corresponding track

- `encoder 8` : track-selection (left-right)

- `encoder 16` : scene selection (up-down)

- `transpose encoder` : set volume of master-track

</details>

---

<details>
<summary>:musical_score: <strong>SEQUENCER</strong></summary>  

- ... coming soon

</details>
---  

## Thanks to

- [untergeek](https://www.untergeek.de/2014/11/taming-arturias-beatstep-sysex-codes-for-programming-via-ipad/) for unravelling BeatStep sysex messages

- Julien Bayle for the awesome [PythonLiveAPI_documentation](https://julienbayle.studio/PythonLiveAPI_documentation/) and some more info's ( [here](https://julienbayle.studio/ableton-live-midi-remote-scripts/) )

- Hanz Petrov for his [Introduction to the Framework-classes](https://livecontrol.q3f.org/ableton-liveapi/articles/introduction-to-the-framework-classes/) and the corresponding [remotescripts-blog](http://remotescripts.blogspot.com)

---
 
