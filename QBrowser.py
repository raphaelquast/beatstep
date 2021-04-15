import Live
from .QSetup import QSetup
from itertools import islice

NavDirection = Live.Application.Application.View.NavDirection

# fmt: off


def makebold(text, surround='select'):
    target = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'",]
    transl = ['𝗮', '𝗯', '𝗰', '𝗱', '𝗲', '𝗳', '𝗴', '𝗵', '𝗶', '𝗷', '𝗸', '𝗹', '𝗺', '𝗻', '𝗼', '𝗽', '𝗾', '𝗿', '𝘀', '𝘁', '𝘂', '𝘃', '𝘄', '𝘅', '𝘆', '𝘇', '𝗔', '𝗕', '𝗖', '𝗗', '𝗘', '𝗙', '𝗚', '𝗛', '𝗜', '𝗝', '𝗞', '𝗟', '𝗠', '𝗡', '𝗢', '𝗣', '𝗤', '𝗥', '𝗦', '𝗧', '𝗨', '𝗩', '𝗪', '𝗫', '𝗬', '𝗭', '𝟬', '𝟭', '𝟮', '𝟯', '𝟰', '𝟱', '𝟲', '𝟳', '𝟴', '𝟵', '❗', '❓', '.', ',', '"', "'",]
    transl = ['ａ', 'ｂ', 'ｃ', 'ｄ', 'ｅ', 'ｆ', 'ｇ', 'ｈ', 'ｉ', 'ｊ', 'ｋ', 'ｌ', 'ｍ', 'ｎ', 'ｏ', 'ｐ', 'ｑ', 'ｒ', 'ｓ', 'ｔ', 'ｕ', 'ｖ', 'ｗ', 'ｘ', 'ｙ', 'ｚ', 'Ａ', 'Ｂ', 'Ｃ', 'Ｄ', 'Ｅ', 'Ｆ', 'Ｇ', 'Ｈ', 'Ｉ', 'Ｊ', 'Ｋ', 'Ｌ', 'Ｍ', 'Ｎ', 'Ｏ', 'Ｐ', 'Ｑ', 'Ｒ', 'Ｓ', 'Ｔ', 'Ｕ', 'Ｖ', 'Ｗ', 'Ｘ', 'Ｙ', 'Ｚ', '０', '１', '２', '３', '４', '５', '６', '７', '８', '９', '！', '？', '．', '，', '"', '＇',]

    if surround=='select':
        before = u"\U0001F537 " + u'\U0001f534  '
        after = u'\U0001f534 ' + u"  \U0001F537"
    elif surround=='list':
        before = u"\U0001F537 "
        after = ""

    translated = ''
    for i in text:
        try:
            translated += transl[target.index(i)]
        except Exception:
            translated += i
    return before + translated +  after


# fmt: on


# class QSequencer(ControlSurface):
class QBrowser(object):
    def __init__(self, parent):
        self._parent = parent

        self._encoder_up_counter = {**{i: 0 for i in range(16)}, "transpose": 0}
        self._encoder_down_counter = {**{i: 0 for i in range(16)}, "transpose": 0}
        self.QS = QSetup()

        self.up_down = True

        self.button_colors = {}

        self.pointer = 0

        self.parent_item = []
        self.browser_item = self.app.browser.instruments

        # encoder turn sensitivity
        self.sensitivity = 6

    @property
    def app(self):
        return self._parent._parent.application()

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
        ]

    def get_itemlist(self):
        if len(self.parent_item) == 0:
            itemlist = self._itemlist

        else:
            itemlist = list(self.parent_item[-1].children)

        return itemlist

    def _scroll_browser(self, up_down):
        app = self.app

        if not app.view.is_view_visible("Browser"):
            app.view.show_view("Browser")
            app.view.focus_view("Browser")

        if up_down:
            app.view.scroll_view(NavDirection.up, "Browser", False)
        else:
            app.view.scroll_view(NavDirection.down, "Browser", False)

    def next_level(self):
        itemlist = list(self.browser_item.children)
        if len(itemlist) > 0:
            self._print_info(empty=True)
            self.parent_item.append(self.browser_item)
            self.pointer = 0
            self.browser_item = itemlist[self.pointer]

        else:
            self._parent._parent.show_message("NO FURTHER LEVEL AVAILABLE")

    def prev_level(self):
        if len(self.parent_item) > 0:
            self.browser_item = self.parent_item.pop(-1)

            self._print_info(empty=True)
            self.pointer = 0

        else:
            self._parent._parent.show_message(
                " ".join(
                    [
                        makebold(i, surround="list")
                        for i in [
                            "sounds",
                            "drums",
                            "instruments",
                            "audio-effects",
                            "midi-effects",
                            "samples",
                        ]
                    ]
                )
            )

    def scroll_up(self):
        itemlist = self.get_itemlist()
        nitems = len(itemlist)
        if self.pointer < nitems - 1:
            self.pointer += 1

        self.browser_item = itemlist[self.pointer]
        self._print_info()

    def scroll_down(self):
        itemlist = self.get_itemlist()
        if self.pointer > 0:
            self.pointer -= 1
        self.browser_item = itemlist[self.pointer]
        self._print_info()


    def scroll_item(self, value):

        itemlist = self.get_itemlist()
        nitems = len(itemlist)
        if value < 65:
            if self.pointer < nitems - 1:
                self.pointer += 1
        else:
            if self.pointer > 0:
                self.pointer -= 1

        self.browser_item = itemlist[self.pointer]

        self._print_info()

    def _print_info(self, empty=False):

        names = []
        for i in self.get_itemlist():
            n = i.name
            if n.endswith(".adg") or n.endswith(".adv"):
                n = n[:-4]

            names.append(n)

        before = "  |  ".join(names[: self.pointer])
        selected = names[self.pointer]
        after = "  |  ".join(names[self.pointer + 1 :])

        if empty:
            before = " " * len(before)
            after = " "
        nchar = (250 - len(selected) - 40) // 2

        outstr = (
            before[-nchar:].rjust(nchar)
            + " " * 15
            + makebold(selected.upper())
            + " " * 15
            + after[:nchar].ljust(nchar)
        )

        self._parent._parent.show_message(outstr)

    def _load_item(self):

        try:
            self._print_info(empty=True)
            self.app.browser.load_item(self.browser_item)

        except Exception:
            self._parent._parent.show_message(
                "the item " + str(self.item.browser_item) + " could not be loaded"
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
                self._parent._toggle_or_delete_device()
            elif i == 3:
                pass
            elif i == 4:
                pass
            elif i == 5:
                self._change_quantization()
            elif i == 6:
                self._change_ableton_view(next(self._detail_cycle))
            elif i == 7:
                self._parent._select_prev_scene()
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
                self._parent._fire_record()
            elif i == 15:
                self._parent._select_next_scene()
            return
        else:
            itemlist = self._itemlist
            if i in range(0, len(itemlist)):
                self.parent_item = [itemlist[i]]

                self.browser_item = itemlist[i].children[0]
                self._print_info()

                self.pointer = 0
            elif i == 7:
                self._parent._select_next_track()
            # ---
            elif i == 8:
                self.prev_level()
            elif i == 9:
                self.next_level()
            elif i == 10:
                pass
            elif i == 11:
                self.scroll_down()
            elif i == 12:
                self.scroll_up()
            elif i == 13:
                pass
            elif i == 14:
                self._load_item()
            elif i == 15:
                self._parent._select_prev_track()
            self.get_button_colors()
            self.button_colors[i] = "red"

    def encoder_callback(self, i, value):
        up_down = value < 64

        if i == 15:
            self._parent._select_prev_next_scene(value)
            return
        elif i == 7:
            self._parent._select_prev_next_track(value)
            return

        # do this to avoid jumping around
        if up_down:
            for key in self._encoder_down_counter.keys():
                self._encoder_down_counter[key] = 0
            self._counter = self._encoder_up_counter
        else:
            for key in self._encoder_up_counter.keys():
                self._encoder_up_counter[key] = 0
            self._counter = self._encoder_down_counter

        if i == "transpose":
            self.scroll_item(value)

        # increase the counter
        self._counter[i] = self._counter[i] + 1
        if self._counter[i] > self.sensitivity:
            if i == 0:
                self.scroll_item(value)

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

        self.button_colors[1] = "magenta"
        self.button_colors[2] = "blue"
        self.button_colors[3] = "blue"
        self.button_colors[4] = "magenta"
        self.button_colors[5] = "magenta"
        self.button_colors[6] = "blue"

        self.button_colors[9] = "magenta"
        self.button_colors[10] = "blue"

        self.button_colors[12] = "blue"
        self.button_colors[13] = "magenta"

        self.button_colors[15] = "red"
