# -*- coding: utf-8 -*-
"""The Event class."""
from copy import deepcopy
from itertools import permutations
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional

import csdmpy as cp
import numpy as np
from mrsimulator import Parseable
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from .isotope import Isotope
from .transition import Transition


class TransitionQuery(BaseModel):
    """Base TransitionQuery class.

    Args:
        P: A list of p symmetry transition, where p = Δm and Δm is the difference
                between spin quantum numbers of the final and initial states.
    """

    P: Optional[Dict] = {"channel-1": [[-1.0]]}
    D: Optional[Dict] = Field(default=None)
    f: Optional[Dict] = Field(default=None)
    transitions: List[Transition] = None

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

    def to_dict_with_units(self):
        return {k: v for k, v in self.dict().items() if v is not None}


class Event(Parseable):
    r"""Base Event class defines the spin environment and the transitions along a
    segment of the transition pathway.

    Args:
        fraction: A `required` float containing the weight of the frequency
                contribution from the event.
        magnetic_flux_density: An `optional` float containing the macroscopic magnetic
                flux density, :math:`H_0`, of the applied external magnetic field
                during the event in units of T. The default value is ``9.4``.
        rotor_frequency: An `optional` float containing the sample spinning frequency
                :math:`\nu_r`, during the event in units of Hz.
                The default value is ``0``.
        rotor_angle: An `optional` float containing the angle between the
                sample rotation axis and the applied external magnetic field,
                :math:`\theta`, during the event in units of rad.
                The default value is ``0.9553166``, i.e. the magic angle.
        transition_query" An `optional` TransitionQuery object or an equivalent dict
                object listing the queries used in selecting the active transitions
                during the event. Only the active transitions from this query
                contribute to the frequency.
    """

    fraction: float = 1
    magnetic_flux_density: Optional[float] = Field(default=9.4, ge=0)
    rotor_frequency: Optional[float] = Field(default=0, ge=0)
    # 54.735 degrees = 0.9553166 radians
    rotor_angle: Optional[float] = Field(default=0.9553166, ge=0, le=1.5707963268)
    transition_query: Optional[TransitionQuery] = TransitionQuery()

    property_unit_types: ClassVar = {
        "magnetic_flux_density": "magnetic flux density",
        "rotor_frequency": "frequency",
        "rotor_angle": "angle",
    }

    property_default_units: ClassVar = {
        "magnetic_flux_density": "T",
        "rotor_frequency": "Hz",
        "rotor_angle": "rad",
    }

    property_units: Dict = {
        "magnetic_flux_density": "T",
        "rotor_frequency": "Hz",
        "rotor_angle": "rad",
    }

    class Config:
        validate_assignment = True

    @classmethod
    def parse_dict_with_units(cls, py_dict):
        """
        Parse the physical quantities of a Event object from as a python dictionary.

        Args:
            py_dict: Dict object
        """
        return super().parse_dict_with_units(py_dict)


class SpectralDimension(Parseable):
    r"""Base SpectralDimension class defines the dimensions of the method.

    Args:
        count: An optional integer with the number of points, :math:`N`,
                along the dimension. The default value is ``1024``.
        spectral_width: A `required` float with the spectral width,
                :math:`\Delta x`, along the dimension in units of Hz.
        reference_offset: An `optional` float with the reference offset, :math:`x_0`
                along the dimension in units of Hz. The default value is ``0``.
        label: An `optional` string label. The default is an empty string.
        events: A `required` list of Event object or an equivalent list of dict objects
                describing the series of events along the spectroscopic dimension.
    """

    count: int = Field(1024, gt=0)
    spectral_width: float = Field(..., gt=0)
    reference_offset: Optional[float] = Field(default=0)
    label: Optional[str] = ""
    events: List[Event]

    property_unit_types: ClassVar = {
        "spectral_width": ["frequency", "dimensionless"],
        "reference_offset": ["frequency", "dimensionless"],
    }

    property_default_units: ClassVar = {
        "spectral_width": ["Hz", "ppm"],
        "reference_offset": ["Hz", "ppm"],
    }

    property_units: Dict = {"spectral_width": "Hz", "reference_offset": "Hz"}

    class Config:
        validate_assignment = True

    @property
    def coordinates_Hz(self):
        r"""
        The grid coordinates along the dimension in units of Hz, evaluated as

        .. math::
            x_\text{Hz} = \left([0, 1, ... N-1] - T\right) \frac{\Delta x}{N} + x_0

        where :math:`T=N/2` and :math:`T=(N-1)/2` for even and odd values of
        :math:`N`, respectively.

        Example:
            >>> dim.coordinates_Hz[:5]
            array([-25000.      , -24951.171875, -24902.34375 , -24853.515625,
                   -24804.6875  ])
        """
        n = self.count
        Tk = int(n / 2)
        increment = self.spectral_width / self.count
        return (np.arange(n) - Tk) * increment + self.reference_offset

    # @property
    # def coordinates_ppm(self):
    #     r"""
    #     The grid coordinates along the dimension as dimension frequency ratio
    #     in units of ppm. The coordinates are evaluated as

    #     .. math::
    #         x_\text{ppm} = \frac{x_\text{Hz}} {x_0 + \omega_0}

    #     where :math:`\omega_0` is the Larmor frequency.

    #     Example:
    #         >>> dim.coordinates_ppm[:5]
    #         array([-239.53462217, -239.06678111, -238.59894005, -238.13109899,
    #                -237.66325794])
    #     """
    #     if self.isotope is None:
    #         warnings.warn(
    #             (
    #                 "The coordinates along the dimension without an assigned "
    #                 "isotope cannot be converted to dimensionless frequency ratio."
    #             )
    #         )
    #     else:

    #         denominator = (self.coordinates_offset + self.larmor_frequency) / 1e6
    #         return self.coordinates_Hz / abs(denominator)

    @classmethod
    def parse_dict_with_units(cls, py_dict):
        """
        Parse the physical quantities of a Dimension object from as a python dictionary.

        Args:
            py_dict: Dict object
        """
        py_dict_copy = deepcopy(py_dict)
        if "events" in py_dict_copy:
            py_dict_copy["events"] = [
                Event.parse_dict_with_units(e) for e in py_dict_copy["events"]
            ]

        return super().parse_dict_with_units(py_dict_copy)

    def to_csdm_dimension(self):
        increment = self.spectral_width / self.count
        dim = cp.Dimension(
            type="linear",
            count=self.count,
            increment=f"{increment} Hz",
            coordinates_offset=f"{self.reference_offset} Hz",
            # origin_offset=f"{np.abs(self.larmor_frequency)} Hz",
            complex_fft=True,
            reciprocal={"coordinates_offset": f"{-1/(2*increment)} s"},
        )
        return dim


class Method(Parseable):
    name: Optional[str] = ""
    description: Optional[str] = ""
    channels: List[str]
    spectral_dimensions: List[SpectralDimension]
    simulation: Optional[cp.CSDM]
    experiment: Optional[cp.CSDM]

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

    @validator("channels", always=True)
    def get_channels(cls, v, *, values, **kwargs):
        return [Isotope(symbol=_) for _ in v]

    @classmethod
    def parse_dict_with_units(cls, py_dict):
        """
        Parse the physical quantities of a Event object from as a python dictionary.

        Args:
            py_dict: Dict object
        """
        py_dict_copy = deepcopy(py_dict)
        if "spectral_dimensions" in py_dict_copy:
            py_dict_copy["spectral_dimensions"] = [
                SpectralDimension.parse_dict_with_units(s)
                for s in py_dict_copy["spectral_dimensions"]
            ]
        if "simulation" in py_dict_copy:
            py_dict_copy["simulation"] = cp.parse_dict(py_dict_copy["simulation"])
        if "experiment" in py_dict_copy:
            py_dict_copy["experiment"] = cp.parse_dict(py_dict_copy["experiment"])
        return super().parse_dict_with_units(py_dict_copy)

    def to_dict_with_units(self):
        temp_dict = self.dict(
            exclude={"spectral_dimensions", "channels", "simulation", "experiment"}
        )
        temp_dict["spectral_dimensions"] = [
            item.to_dict_with_units() for item in self.spectral_dimensions
        ]
        temp_dict["channels"] = [item.to_dict_with_units() for item in self.channels]
        if self.simulation is not None:
            temp_dict["simulation"] = self.simulation.to_dict(update_timestamp=True)
        if self.experiment is not None:
            temp_dict["experiment"] = self.experiment.to_dict()
        return temp_dict

    def dict(self, **kwargs):
        temp_dict = super().dict(**kwargs)
        if self.simulation is not None:
            temp_dict["simulation"] = self.simulation.to_dict(update_timestamp=True)
        if self.experiment is not None:
            temp_dict["experiment"] = self.experiment.to_dict()
        return temp_dict

    def get_transition_pathways(self, isotopomer):
        transitions = isotopomer.all_transitions
        segments = []
        for seq in self.spectral_dimensions:
            for ent in seq.events:
                list_of_P = query_permutations(
                    ent.transition_query.to_dict_with_units(),
                    isotope=isotopomer.get_isotopes(),
                    channel=[self.channel.symbol],
                )
                for symmetry in list_of_P:
                    segments.append(np.asarray(transitions.filter(P=symmetry)))

        return cartesian_product(*segments)


def cartesian_product(*arrays):
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[..., i] = a
    return arr.reshape(-1, la)


def get_iso_dict(channel, isotope):
    """
        Parse the isotopomer sites to determine indecies of each isotope that
        is part of the method channel.

        Args:
            channel: List object
            isotope: List object

    """
    iso_dict = {}

    # determine channels for P
    for i, item in enumerate(isotope):
        if item in channel and item not in iso_dict:
            iso_dict[item] = [i]
        elif item in iso_dict:
            iso_dict[item].append(i)

    return iso_dict


def query_permutations(query, isotope, channel):
    """
        Determines the transition symmetries that are involved in a given
        transition query.

        Args:
            query: Dict bject
            channel: List object
            isotope: List object

    """

    P_permutated = []
    iso_dict = get_iso_dict(channel=channel, isotope=isotope)
    query_short = query["P"]
    for i, items in enumerate(query_short):
        # Check if method isotope is in the isotopomer
        if channel[i] not in iso_dict:
            print(
                f"Method/channel isotope mismatch. Channel asks for {channel[i]} but is not in {isotope}"
            )
            return []

        temp_P = []
        for k in range(len(query_short[items])):
            # Check transition query doesnt require more isotopes than present
            if len(query_short[items][k]) > len(iso_dict[channel[i]]):
                print("Failed: Transition query larger than channel")
                return []
            elif len(query_short[items][k]) <= len(iso_dict[channel[i]]):
                query_short[items][k] += (
                    len(iso_dict[channel[i]]) - len(query_short[items][k])
                ) * [k]
            temp_P += list(permutations(query_short[items][k]))
        P_permutated += [temp_P]
        # P_permutated += [list(permutations(query_short[items][k]))]

    transition_symmetry_from_query = []  # rename to transition symmetry from query
    for i, iso_trans_symmetry in enumerate(P_permutated):
        print(iso_trans_symmetry)
        temp_transitions = []
        for transition in iso_trans_symmetry:
            P_expanded = len(isotope) * [0]
            for j, item in enumerate(transition):
                P_expanded[iso_dict[channel[i]][j]] = item
            if transition_symmetry_from_query == []:
                temp_transitions.append(P_expanded)
            else:
                for k, intermediate in enumerate(transition_symmetry_from_query[-1]):
                    temp_transitions.append(
                        [sum(x) for x in zip(intermediate, P_expanded)]
                    )
        # transition_symmetry_from_query += temp_transitions

        transition_symmetry_from_query.append(temp_transitions)
        print("trans from query: ", transition_symmetry_from_query[-1])

    return transition_symmetry_from_query[-1]


#     ['17O', '1H', '29Si', '1H', '17O']
# [[(1, 0), (0, 1)], [(2, 0), (0, 2)]]
# Pass 0:  [[[1, 0, 0, 0, 0], [0, 0, 0, 0, 1]]]
# Pass 1:  [[[1, 0, 0, 0, 0], [0, 0, 0, 0, 1]], [[1, 2, 0, 0, 0], [0, 2, 0, 0, 1], [1, 0, 0, 2, 0], [0, 0, 0, 2, 1]]]
# [[1, 2, 0, 0, 0], [0, 2, 0, 0, 1], [1, 0, 0, 2, 0], [0, 0, 0, 2, 1]]