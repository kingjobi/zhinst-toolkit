# Copyright (C) 2020 Zurich Instruments
#
# This software may be modified and distributed under the terms
# of the MIT license. See the LICENSE file for details.

import numpy as np

from zhinst.toolkit.control.drivers.base import (
    BaseInstrument,
    DAQModule as DAQ,
    SweeperModule as Sweeper,
    ZHTKException,
)
from zhinst.toolkit.interface import DeviceTypes


"""
High-level controller for MFLI.

"""


class MFLI(BaseInstrument):
    def __init__(self, name, serial, **kwargs):
        super().__init__(name, "mfli", serial, **kwargs)

    def connect_device(self, nodetree=True):
        super().connect_device(nodetree=nodetree)
        self._get_streamingnodes()
        self._daq_module = DAQModule(self)
        self._daq_module._setup()
        self._sweeper_module = SweeperModule(self)
        self._sweeper_module._setup()

    def _init_settings(self):
        pass

    @property
    def daq(self):
        return self._daq_module

    @property
    def sweeper(self):
        return self._sweeper_module


MAPPINGS = {
    "sweep_parameters": {
        "auxout1offset": "auxouts/0/offset",
        "auxout2offset": "auxouts/1/offset",
        "auxout3offset": "auxouts/2/offset",
        "auxout4offset": "auxouts/3/offset",
        "demdod1phase": "demods/0/phaseshift",
        "demdod2phase": "demods/1/phaseshift",
        "frequency": "oscs/0/freq",
        "output1amp": "sigouts/0/amplitudes/1",
        "output1offset": "sigouts/0/offset",
    },
}


class DAQModule(DAQ):
    def __init__(self, parent):
        super().__init__(parent, clk_rate=1.8e9)
        nodes = self._parent._streaming_nodes
        self._trigger_signals = {}
        for source in ["auxin", "demod", "imp"]:
            self._trigger_signals.update(
                {k: v for k, v in nodes.items() if source in k}
            )
        self._trigger_types = {
            "demod": {
                "demod2phase": ".TrigDemod2Phase",
                "trigin1": ".TrigIn1",
                "trigin2": ".TrigIn2",
                "trigout1": ".TrigOut1",
                "trigout2": ".TrigOut2",
            },
            "imp": {},
        }


class SweeperModule(Sweeper):
    def signals_list(self):
        return list(self._parent._streaming_nodes.keys())

    def sweep_parameter_list(self):
        return list(MAPPINGS["sweep_parameters"].keys())

    def _parse_signals(self, signal_source):
        sources = MAPPINGS["signal_sources"]
        if signal_source.lower() not in sources.keys():
            raise ZHTKException(f"Signal source must be in {list(sources.keys())}")
        signal_node = "/"
        signal_node += self._parent.serial
        signal_node += f"{sources[signal_source]}"
        return signal_node.lower()

    def _parse_sweep_param(self, param):
        mapping = MAPPINGS["sweep_parameters"]
        if param not in mapping.keys():
            raise ZHTKException(
                f"The parameter {param} must be one of {list(mapping.keys())}"
            )
        return mapping[param]
