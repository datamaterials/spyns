# -*- coding: utf-8 -*-

import numpy as np

from spyns.data import SimulationData, SimulationParameters
from spyns.lattice import BinaryLattice
import spyns


def simulation(parameters: SimulationParameters) -> SimulationData:
    """Run the Ising model simulation.

    :param parameters: Parameters to use for setting up and running the simulation.
    :return: Output of the Ising model simulation.
    """
    np.random.seed(parameters.seed)

    lattice: BinaryLattice = BinaryLattice(
        parameters.dimensions,
        parameters.neighborhood,
        parameters.interaction_coefficients,
    )
    data: SimulationData = spyns.data.setup_containers(
        parameters=parameters,
        state=lattice.sample_random_state(),
    )

    pre_simulation(
        lattice=lattice,
        data=data,
    )
    main_simulation(
        lattice=lattice,
        data=data,
    )
    post_simulation(
        lattice=lattice,
        data=data,
    )

    return data


def pre_simulation(
    lattice: BinaryLattice,
    data: SimulationData,
) -> None:
    """Run equilibration sweeps.

    :param lattice: Structural information and neighbor tables.
    :param data: Data container for the simulation.
    """
    for sweep_index in range(data.parameters.equilibration_sweeps):
        spyns.sampling.sweep_grid(
            lattice=lattice,
            data=data,
            sweep_index=sweep_index,
            equilibration_run=True,
        )


def main_simulation(
    lattice: BinaryLattice,
    data: SimulationData,
) -> None:
    """Run the production sweeps for the Ising model simulation.

    :param lattice: Structural information and neighbor tables.
    :param data: Data container for the simulation.
    """
    spyns.model.ising_save_full_state(lattice=lattice, data=data)
    for sweep_index in range(data.parameters.sweeps):
        spyns.sampling.sweep_grid(
            lattice=lattice,
            data=data,
            sweep_index=sweep_index,
            equilibration_run=False,
        )


def post_simulation(
    lattice: BinaryLattice,
    data: SimulationData,
) -> None:
    """Write the simulation history to disk and print estimators.

    :param lattice: Structural information and neighbor tables.
    :param data: Data container for the simulation.
    """
    spyns.data.write_trace_to_disk(data=data)

    average_energy: float = \
        data.estimators.energy_1st_moment / lattice.number_sites
    fm_order_parameter: float = \
        data.estimators.magnetization_1st_moment / lattice.number_sites
    afm_order_parameter: float = (
        data.estimators.magnetization_even_sites_1st_moment -
        data.estimators.magnetization_odd_sites_1st_moment
    ) / lattice.number_sites
    print(f"Average energy = {average_energy}")
    print(f"FM order parameter = {fm_order_parameter}")
    print(f"AFM order parameter = {afm_order_parameter}")