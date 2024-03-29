# Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/BeatStep_Q/__init__.py
from __future__ import absolute_import, print_function, unicode_literals
import _Framework.Capabilities as caps
from .BeatStep_Q import BeatStep_Q


def get_capabilities():
    return {
        caps.CONTROLLER_ID_KEY: caps.controller_id(
            vendor_id=7285, product_ids=[518], model_name=["Arturia BeatStep"]
        ),
        caps.PORTS_KEY: [
            caps.inport(props=[caps.NOTES_CC, caps.SCRIPT, caps.REMOTE]),
            caps.outport(props=[caps.SCRIPT]),
        ],
    }


def create_instance(c_instance):
    return BeatStep_Q(c_instance)
