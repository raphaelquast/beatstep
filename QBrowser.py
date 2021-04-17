import Live
from .QSetup import QSetup

NavDirection = Live.Application.Application.View.NavDirection
FilterType = Live.Browser.FilterType
DeviceType = Live.Device.DeviceType
Relation = Live.Browser.Relation


symb_folder = u"\U0001f4c1"
symb_folder_open = u"\U0001f4c2"
symb_red_circle = u"\U0001f534"
symb_orange_circle = u"\U0001f7e0"
symb_red_box = u"\U0001f7e5"
symb_circle_arrow = u"\U0001f504"

symb_blue_diamond_large = u"\U0001F537"
symb_blue_diamond_small = u"\U0001f539"
symb_fire = u"\U0001f525"
symb_black_circle = u"\u25cf"
symb_stop = u"\U0001f6ab"

symb_left_arraow = u"\u25c4"
symb_right_arrow = u"\u25ba"


# fmt: off
def makebold(text, surround="select", translate=False):

    if surround == "select":
        before = "||  " + "    "
        after = "    " + "  ||"
    elif surround == "hotswap":
        before = "||  " + symb_fire + "   "
        after = "   " + symb_fire + "  ||"
    elif surround == "last_level":
        before = " " + symb_stop
        after = " " + symb_stop
    elif surround == "list":
        before = symb_blue_diamond_small + " "
        after = ""
    elif surround == "no":
        before = ""
        after = ""
    if translate:
        target = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.',
                  ',', '"', "'", "|"]

        transl = [u'\uff41', u'\uff42', u'\uff43', u'\uff44', u'\uff45',
                  u'\uff46', u'\uff47', u'\uff48', u'\uff49', u'\uff4a',
                  u'\uff4b', u'\uff4c', u'\uff4d', u'\uff4e', u'\uff4f',
                  u'\uff50', u'\uff51', u'\uff52', u'\uff53', u'\uff54',
                  u'\uff55', u'\uff56', u'\uff57', u'\uff58', u'\uff59',
                  u'\uff5a', u'\uff21', u'\uff22', u'\uff23', u'\uff24',
                  u'\uff25', u'\uff26', u'\uff27', u'\uff28', u'\uff29',
                  u'\uff2a', u'\uff2b', u'\uff2c', u'\uff2d', u'\uff2e',
                  u'\uff2f', u'\uff30', u'\uff31', u'\uff32', u'\uff33',
                  u'\uff34', u'\uff35', u'\uff36', u'\uff37', u'\uff38',
                  u'\uff39', u'\uff3a', u'\uff10', u'\uff11', u'\uff12',
                  u'\uff13', u'\uff14', u'\uff15', u'\uff16', u'\uff17',
                  u'\uff18', u'\uff19', u'\uff01', u'\uff1f', u'\uff0e',
                  u'\uff0c', u'"', u'\uff07', u'\uff5c']
        translated = ""
        for i in text:
            try:
                translated += transl[target.index(i)]
            except Exception:
                translated += i
    else:
        translated = text

    return before + translated + after
# fmt: on


class dummy_item(object):
    def __init__(self, name, children):
        self.name = name
        self.children = list(children)
        self.is_loadable = False
        self.is_folder = True
        self.is_device = False
        self.source = "QBrowser"
        self.uri = "QBrowser#top-level"


# class QSequencer(ControlSurface):
class QBrowser(object):
    def __init__(self, parent):
        self._parent = parent

        self.up_down = True

        self.button_colors = {}

        self.pointer = 0
        self.parent_pointer = []

        self.browser_item = self.app.browser.instruments
        self.parent_item = []

        # encoder turn sensitivity
        self.sensitivity = 6

        self.itemlist = self._get_itemlist()
        self.names = self._get_names()

        self.preview_items = False
        self.hotswap = False

        self._ableton_version = self.app.get_major_version()

    # --------------------------

    @property
    def song(self):
        return self._parent._parent.song()

    @property
    def app(self):
        return self._parent._parent.application()

    # --------------------------

    @property
    def sounds(self):
        return self.app.browser.sounds

    @property
    def drums(self):
        return self.app.browser.drums

    @property
    def instruments(self):
        return self.app.browser.instruments

    @property
    def audio_effects(self):
        return self.app.browser.audio_effects

    @property
    def midi_effects(self):
        return self.app.browser.midi_effects

    @property
    def samples(self):
        return self.app.browser.samples

    @property
    def colors(self):
        return dummy_item("Collections", self.app.browser.colors)

    # --------------------------

    @property
    def hotswap_target(self):
        return self.app.browser.hotswap_target

    # TODO implement grooves via Live.GroovePool
    @property
    def _itemlist(self):
        return [
            self.sounds,
            self.drums,
            self.instruments,
            self.audio_effects,
            self.midi_effects,
            self.samples,
            self.colors,
        ]

    @property
    def _itemlist_names(self):
        return dict(
            clips=[self.samples.name],
            instruments=[self.sounds.name, self.instruments.name, self.drums.name],
            audio_effects=[self.audio_effects.name],
            midi_effects=[self.midi_effects.name],
            special=[self._itemlist[6].name],
        )

    def _get_itemlist(self):
        if len(self.parent_item) == 0:
            itemlist = self._itemlist

        else:
            itemlist = list(self.parent_item[-1].children)

        return itemlist

    def _scroll_browser(self, up_down, direction="up_down"):
        app = self.app

        if not app.view.is_view_visible("Browser"):
            app.view.show_view("Browser")
            app.view.focus_view("Browser")

        if up_down:
            if direction == "up_down":
                app.view.scroll_view(NavDirection.up, "Browser", False)
            elif direction == "left_right":
                app.view.scroll_view(NavDirection.left, "Browser", False)
        else:
            if direction == "up_down":
                app.view.scroll_view(NavDirection.down, "Browser", False)
            elif direction == "left_right":
                app.view.scroll_view(NavDirection.right, "Browser", False)

    def next_level(self, empty=False):
        itemlist = list(self.browser_item.children)
        if len(itemlist) > 0:
            # if self.hotswap:
            #     self._scroll_browser(False, direction="left_right")
            #     self._scroll_browser(False, direction="up_down")

            self.parent_item.append(self.browser_item)
            self.parent_pointer.append(self.pointer)

            if empty:
                self._print_info(empty=empty)

            self.pointer = 0

            self.browser_item = itemlist[self.pointer]

            self.itemlist = self._get_itemlist()
            self.names = self._get_names()

            if not empty:
                self._print_info(empty=empty)

        else:
            self._print_info(empty=True, surround_selected="last_level")

    def prev_level(self):

        if len(self.parent_item) > 0:

            # if self.hotswap:
            #     # do this twice to close the open folder
            #     self._scroll_browser(True, direction="left_right")
            #     self._scroll_browser(True, direction="left_right")

            self.browser_item = self.parent_item.pop(-1)

            self.pointer = self.parent_pointer.pop(-1)

            self.itemlist = self._get_itemlist()
            self.names = self._get_names()

        self._print_info(empty=False)

    def scroll_up(self):

        # clear any remaining send-messages
        self._parent._parent._task_group.clear()

        nitems = len(self.itemlist)
        if self.pointer < nitems - 1:
            self.pointer += 1

            # if self.hotswap:
            #     self._scroll_browser(False, direction="up_down")

        self.browser_item = self.itemlist[self.pointer]
        self._print_info()

        if self.preview_items:
            self.app.browser.stop_preview()
            self._preview_item()

    def scroll_down(self):

        # clear any remaining send-messages
        self._parent._parent._task_group.clear()

        if self.pointer > 0:
            self.pointer -= 1

            # if self.hotswap:
            #     self._scroll_browser(True, direction="up_down")

        self.browser_item = self.itemlist[self.pointer]
        self._print_info()

        if self.preview_items:
            self.app.browser.stop_preview()
            self._preview_item()

    def scroll_item(self, value):

        # clear any remaining send-messages
        self._parent._parent._task_group.clear()

        nitems = len(self.itemlist)
        if value < 65:
            if self.pointer < nitems - 1:
                self.pointer += 1
                # if self.hotswap:
                #     self._scroll_browser(False, direction="up_down")

        else:
            if self.pointer > 0:
                self.pointer -= 1
                # if self.hotswap:
                #     self._scroll_browser(True, direction="up_down")

        self.browser_item = self.itemlist[self.pointer]

        self._print_info()

        if self.preview_items:
            self.app.browser.stop_preview()
            self._preview_item()

    def _get_names(self):
        names = []
        for item in self.itemlist:
            n = item.name

            if item.is_folder:
                n = symb_folder + " " + n
            elif item.is_device:
                n = symb_blue_diamond_small + " " + n
            else:
                n = symb_black_circle + " " + n

            names.append(n)

        return names

    def _print_info(
        self,
        empty=False,
        surround_selected="select",
        surround_all=None,
        sel_nchar=0,
        l_r_nchar=80,
        sep="     ",
        space=" ",
    ):
        """

        Parameters
        ----------
        empty : bool, optional
            print whitespaces instead of text. The default is False.
        surround_selected : str, optional
            makebold() applied to the selected item
            The default is "select".
        surround_all : str, optional
            makebold() applied to all names
            The default is None.
        sel_nchar : int, optional
            min. number of characters for the selected string.
            The default is 40.
        l_r_nchar : int, optional
            additional characters printed left-and right.
            (filled with available item names)
            The default is 50.
        sep : str, optional
            separator for additional elements
        space: str, optional
            space-character
        """

        # don't print the info if browser is no longer active
        if not self._parent._browser:
            return

        if surround_all is not None:
            names = [makebold(i, surround=surround_all) for i in self.names]
        else:
            names = self.names

        before = sep.join(names[: self.pointer]) + sep
        after = sep + sep.join(names[self.pointer + 1 :])

        if self.hotswap:
            surround_selected = "hotswap"

        selected = names[self.pointer]
        if self.browser_item.is_loadable:
            if self.hotswap:
                selected = symb_circle_arrow + selected[selected.index(" ") :]
            else:
                selected = symb_red_circle + selected[selected.index(" ") :]
        else:
            selected = symb_orange_circle + selected[selected.index(" ") :]

        if empty:
            before = space * len(before)
            after = ""

        # number of additional text on left- and right side
        nchar = l_r_nchar - len(selected) // 2

        outstr = (
            before[-nchar:].rjust(nchar, space)
            + makebold(
                selected.upper(), surround=surround_selected, translate=True
            ).center(sel_nchar, space)
            + after[:nchar].ljust(nchar, space)
        )

        folder = (
            symb_folder
            + sep
            + (sep + "|" + sep + symb_folder_open).join(
                [i.name for i in self.parent_item]
            )
            + ":"
            + sep * 5
        )

        self._parent._parent.show_message(folder + makebold(outstr, surround="no"))

        # continue updating the info-bar unil the browser is closed
        if self._parent._browser:
            self._parent._parent.schedule_message(16, self._print_info)

    def _load_item(self):
        try:
            self._print_info(empty=True)
            self.app.browser.load_item(self.browser_item)
        except Exception:
            self._parent._parent.show_message(
                "     "
                + symb_stop
                + " the item  "
                + str(self.browser_item.name)
                + "  could not be loaded"
            )

        if self.hotswap:
            self._hide_browser()
            self._print_info()

            try:

                def cb():
                    try:
                        track = self.song.view.selected_track
                        device = track.view.selected_device
                        self.app.browser.hotswap_target = device
                    except Exception:
                        self._parent._parent.log_message("couldn't set hotswap target")

                self._parent._parent.schedule_message(4, cb)
            except Exception:
                self._parent._parent.schedule_message(2, cb)

    def _toggle_preview_item(self):

        self.preview_items = not self.preview_items

        if not self.preview_items:
            self.app.browser.stop_preview()
        else:
            self._preview_item()

    def _preview_item(self):
        try:
            self.app.browser.preview_item(self.browser_item)
        except Exception:
            self._parent._parent.show_message(
                "     "
                + symb_stop
                + "the item  "
                + str(self.browser_item.name)
                + "  could not be previewed"
            )

    def button_callback(self, i):
        """
        the callback for button i (e.g. 1 - 16)
        """

        if self._parent._shift_pressed:
            # use fuctionality of CONTROL layer
            if i == 0:
                self._parent._redo()
            elif i == 1:
                self._parent._collapse_device()
            elif i == 2:
                self._parent._toggle_device_on_off()
            elif i == 3:
                pass
            elif i == 4:
                pass
            elif i == 5:
                self._parent._change_quantization()
            elif i == 6:
                self._parent._change_ableton_view(next(self._parent._detail_cycle))
            elif i == 7:
                self._parent._scroll_device_chain(0, sensitivity=1)
            # ----------
            elif i == 8:
                self._parent._undo()
            elif i == 9:
                self._parent._duplicate_track()
            elif i == 10:
                self._parent._duplicate_scene()
            elif i == 11:
                self._parent._tap_tempo()
            elif i == 12:
                self._parent._toggle_metronome()
            elif i == 13:
                self._parent._toggle_automation()
            elif i == 14:
                self._load_on_new_track()
            elif i == 15:
                self._parent._scroll_device_chain(127, sensitivity=1)
            return
        else:
            if i in range(7):

                self.pointer = i
                self.parent_pointer = []

                self.browser_item = self._itemlist[i]
                self.parent_item = []

                self.itemlist = self._get_itemlist()
                self.names = self._get_names()

                self.next_level(empty=True)

                # clear remaining scheduled messages
                self._parent._parent._task_group.clear()
                # after a delay of 10 ticks, show the folder content
                self._parent._parent.schedule_message(8, self._print_info)

            elif i == 6:
                pass
            elif i == 7:
                self._parent._select_next_track()
            # ---
            elif i == 8:
                self.scroll_down()
            elif i == 9:
                self.prev_level()
            elif i == 10:
                self.next_level()
            elif i == 11:
                self.scroll_up()
            elif i == 12:
                self._toggle_hotswap()
            elif i == 13:
                self._toggle_preview_item()
            elif i == 14:
                self._load_item()
            elif i == 15:
                self._parent._select_prev_track()
            self.get_button_colors()
            self.button_colors[i] = "red"

            self._parent._update_lights()

    def encoder_callback(self, i, value):

        if i == 4:
            self._parent._track_send_x(value, -1, 0)
        elif i == 5:
            self._parent._track_send_x(value, -1, 2)
        elif i == 6:
            self._parent._track_volume_master_or_current(value)
        elif i == 7:
            if self._parent._shift_pressed:
                self._parent._scroll_drum_pad_row(value)
            else:
                self._parent._select_prev_next_track(value)
        elif i == 12:
            self._parent._track_send_x(value, -1, 1)
        elif i == 13:
            self._parent._track_send_x(value, -1, 4)
        elif i == 14:
            self._parent._track_pan_master_or_current(value)
        elif i == 15:
            if self._parent._shift_pressed:
                self._parent._scroll_drum_pad_col(value)
            else:
                self._parent._select_prev_next_scene(value)

        elif i == "transpose":
            self.scroll_item(value)

    def get_button_colors(self):
        self.button_colors = dict(
            shift="red",
            chan="red",
            store="red",
            recall="red",
        )
        for i in range(16):
            self.button_colors[i + 1] = "black"

        self.button_colors[1] = "magenta"
        self.button_colors[2] = "magenta"
        self.button_colors[3] = "magenta"
        self.button_colors[4] = "magenta"
        self.button_colors[5] = "magenta"
        self.button_colors[6] = "magenta"
        self.button_colors[7] = "magenta"

        self.button_colors[9] = "magenta"
        self.button_colors[10] = "blue"
        self.button_colors[11] = "red"
        self.button_colors[12] = "magenta"

        if self.hotswap:
            self.button_colors[13] = "red"
        else:
            self.button_colors[13] = "black"

        if self.preview_items:
            self.button_colors[14] = "blue"
        else:
            self.button_colors[14] = "black"

        self.button_colors[15] = "red"

    def _hide_browser(self):
        self._parent._parent.schedule_message(
            2, lambda: self.app.view.hide_view("Browser")
        )
        self._parent._parent.schedule_message(
            4, lambda: self.app.view.hide_view("Browser")
        )
        self._parent._parent.schedule_message(
            8, lambda: self.app.view.hide_view("Browser")
        )

    def _toggle_hotswap(self):
        self.hotswap = not self.hotswap

        if self.hotswap:
            device = self._parent.selected_track.view.selected_device

            if device is None:
                self._parent._parent.show_message(
                    "cannot activate hotswap without a target"
                )
                self.hotswap = False
                return

            self.app.browser.hotswap_target = device
            self.app.view.show_view("Detail/DeviceChain")

            self.find_device(device)
        else:
            self.app.browser.hotswap_target = None

        self._hide_browser()
        self._print_info()

    def _select_item(self, pointer, parent_pointer, parent_item):
        try:
            self.pointer = pointer
            self.parent_pointer = parent_pointer
            self.parent_item = parent_item

            self.itemlist = self._get_itemlist()
            self.names = self._get_names()
            self.browser_item = self.itemlist[self.pointer]

            self._print_info()
        except Exception:
            self._parent._parent.show_message("the item could not be selected")

    def find_device(self, device, select=True):
        folders = self._itemlist[:-1]
        # returns indexes of the sub-level structure
        parent_pointer = []
        parent_item = []

        def get_nested_elements(folders, device):
            device_found = [
                i
                for i, dev in enumerate(folders)
                if self.app.browser.relation_to_hotswap_target(dev) == Relation.equal
            ]

            if len(device_found) > 0:
                yield device_found[0]
            else:
                for i, node in enumerate(folders):
                    if hasattr(node, "children") and len(node.children) > 0:
                        parent_pointer.append(i)
                        parent_item.append(node)

                        for e in get_nested_elements(node.children, device):
                            yield e
                if len(parent_pointer) > 0:
                    parent_pointer.pop(-1)
                    parent_item.pop(-1)

        try:
            pointer = next(get_nested_elements(folders, device))

            if select is True:
                self._select_item(pointer, parent_pointer, parent_item)
            else:
                return pointer, parent_pointer, parent_item

        except Exception:
            self._parent._parent.show_message(
                "     " + symb_stop + " could not find the device " + str(device.name)
            )

    def _find_item(self, item, select=True):
        folders = self._itemlist[:-1]
        # returns indexes of the sub-level structure
        parent_pointer = []
        parent_item = []

        def get_nested_elements(folders, item):
            device_found = [i for i, dev in enumerate(folders) if dev.name == item.name]

            if len(device_found) > 0:
                yield device_found[0]
            else:
                for i, node in enumerate(folders):
                    if hasattr(node, "children") and len(node.children) > 0:
                        parent_pointer.append(i)
                        parent_item.append(node)

                        for e in get_nested_elements(node.children, item):
                            yield e
                if len(parent_pointer) > 0:
                    parent_pointer.pop(-1)
                    parent_item.pop(-1)

        try:
            pointer = next(get_nested_elements(folders, item))

            if select is True:
                self._select_item(pointer, parent_pointer, parent_item)
            else:
                return pointer, parent_pointer, parent_item

        except AssertionError:
            self._parent._parent.show_message(
                "could not find the device " + str(item.name)
            )

    def identify_item(self):

        if len(self.parent_item) > 0:
            parent = self.parent_item[0].name

            for key, val in self._itemlist_names.items():
                if parent in val:
                    ID = key
            if ID == "special":

                try:
                    _, _, parent_item = self._find_item(self.browser_item, select=False)
                    if len(parent_item) > 0:
                        ID = parent_item[0].name
                    else:
                        ID = "UNKNOWN"
                except Exception:
                    self._parent._parent.show_message(
                        "item not found... please create track manually"
                    )
                    ID = "UNKNOWN"

        return ID

    def _load_on_new_track(self):
        ID = self.identify_item()
        if ID == "audio_effects" or "midi_effects":
            self.song.create_return_track()
            self._load_item()
        elif ID == "instruments":
            self.song.create_midi_track()
            self._load_item()
        elif ID == "clips":
            self.song.create_audio_track()
            self._load_item()
        else:
            self._parent._parent.show_message(
                "could not establish the type of "
                + str(self.browser_item.name)
                + " ... please create the appropriate"
                + "track manually"
            )
