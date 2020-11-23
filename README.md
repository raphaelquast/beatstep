# GENERAL

This is a **MIDI Remote Script** for **Ableton Live 10** and the **Arturia Beatstep** controller.

It is intended to provide **full control** over **Ableton Live** e.g.:

- select tracks and scenes

- start, stop, record, delete, undo clips etc. 

- arm / mute tracks

- play instruments



# Basic usage (already implemented)

## Buttons:

The stop-button serves as `shift-button` to activate the control-features.

- `shift` + `button 1-7`:  select track 1-7 of the currently focussed slots (red box)
  
  - double tap an already activated track to arm/unarm it !

- `shift` + `button 9`: undo

- `shift` + `button 10`: delete selected clip

- `shift` + `button 11`: stop selected clip
  
  - double-tap to stop all clips!

- `shift` + `button 12`: duplicate the currently selected loop

- `shift` + `button 13`: move to the next clip (add an empty clip-slot if you are at the final slot)

- `shift` + `button 14`: duplicate the currently selected clip, and set the focus to the duplicate

- `shift` + `button 15`: start recording          
  
  - if the currently selected slot is empty, start recording a new clip 
  
  - if a clip is already present, overdub

- `shift` + `button 16`: activate arm / mute control   
  
  - tap `button 16` again (without `shift`) to get back to the normal behaviour
  
  - the buttons in the upper row (1-7) indicate / set the **mute** status of the first 7 tracks in the red box
  
  - the buttons in the lower row (9-15) indicate / set the **arm** status of the first 7 tracks in the red box

## Encoder:

- `encoder 6` : currently selected track: **send B**

- `encoder 5` : currently selected track: **send A**

- `encoder 13` :  currently selected track: **pan**

- `encoder 14` : currently selected track: **volume**

- `encoder 8` : track-selection (left-right)

- `encoder 16` : scene selection (up-down)

# Installation

To use this script, simply copy the contents into a folder named "Beatstep_Q" within the MIDI Remote  scripts folder of Ableton Live (located at `..install-dir..\Resources\MIDI Remote Scripts`) and then select the **Beatstep_Q** device as control-surface in the MIDI-tab of the preferences. (make sure to activate both `track`and `remote` for this device!)

# ...work in progress

While the principal stuff is already working properly, this script is still a work-in-progress, so be prepared for some unexpected behaviour!


