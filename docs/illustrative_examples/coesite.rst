
Coesite
-------
Coesite is a high-pressure (2-3 GPa) and high-temperature (700°C) polymorph of
silicon dioxide :math:`\text{SiO}_2`. Coesite has five distinct
:math:`^{17}\text{O}` sites.  We use the :math:`^{17}\text{O}` tensor
information from
`Grandinetti et. al. <https://pubs.acs.org/doi/abs/10.1021/j100032a045>`_


**Step 1**  Create sites.

.. doctest::

    >>> O17_1 = Site(isotope='17O', isotropic_chemical_shift=29, quadrupolar={'Cq': 6.05e6, 'eta': 0.000})
    >>> O17_2 = Site(isotope='17O', isotropic_chemical_shift=41, quadrupolar={'Cq': 5.43e6, 'eta': 0.166})
    >>> O17_3 = Site(isotope='17O', isotropic_chemical_shift=57, quadrupolar={'Cq': 5.45e6, 'eta': 0.168})
    >>> O17_4 = Site(isotope='17O', isotropic_chemical_shift=53, quadrupolar={'Cq': 5.52e6, 'eta': 0.169})
    >>> O17_5 = Site(isotope='17O', isotropic_chemical_shift=58, quadrupolar={'Cq': 5.16e6, 'eta': 0.292})

**Step 2**  Create isotopomers using the sites.

.. doctest::

    >>> sites = [O17_1, O17_2, O17_3, O17_4, O17_5]
    >>> abundance = [0.83, 1.05, 2.16, 2.05, 1.90] # abundance of each isotopomer
    >>> isotopomers = [Isotopomer(sites=[s], abundance=a) for s, a in zip(sites, abundance)]

**Step 3**  Create a dimension.

.. doctest::

    >>> dimension = Dimension(isotope='17O', number_of_points=2046, spectral_width=50000, rotor_frequency=14000)

The above dimension is set up to record the :math:`^{17}\text{O}` resonances
at the magic angle, spinning at 14 kHz and 9.4 T external magnetic flux
density.
The resonances are recorded over 50 kHz using 2046 points. You may also request
a full description of the dimension object using the
:meth:`~mrsimulator.Dimension.to_dict_with_units` method.

.. doctest::

    >>> pprint(dimension.to_dict_with_units())
    {'isotope': '17O',
     'label': '',
     'magnetic_flux_density': '9.4 T',
     'number_of_points': 2046,
     'reference_offset': '0 Hz',
     'rotor_angle': '0.9553166 rad',
     'rotor_frequency': '14000.0 Hz',
     'spectral_width': '50000.0 Hz'}

**Step 4**  Create the Simulator object and add dimension and isotopomer
objects.

.. doctest::

    >>> sim_coesite = Simulator()
    >>> # add isotopomers
    >>> sim_coesite.isotopomers += isotopomers
    >>> # add dimensions
    >>> sim_coesite.dimensions += [dimension]

**Step 5**  Simulate and plot.

.. doctest::

    >>> x, y = sim_coesite.run(method=one_d_spectrum)
    >>> plot(x,y) # doctest:+SKIP

.. .. testsetup::
..     >>> plot_save(x, y, 'illustrative_example_coesite')

.. figure:: ../_images/illustrative_example_coesite.*
    :figclass: figure-polaroid
