from matplotlib import pyplot as pl
from os.path import join
from math import floor
import pandas as pd
import numpy as np
import functions
import parsers

pl.rcParams["figure.figsize"] = [8, 6]  # Define plot size


def analysis(path, incar, poscar, outcar, fraction, save_plots=False):
    '''
    The analysis for a run.

    inputs:
        path = Path to run.
        incar = The INCAR file.
        poscar = The POSCAR file.
        outcar = The OUTCAR file.
        fraction = The amount of data to average.
        save_plots = Whether to save analysis plots.

    outputs:
        comp = The composition.
        vol = The average system volume.
        press = The average system pressure.
        temp = The average system temperature.
        start_temp = The starting temperature defined in INCAR.
        end_temp = The ending temperature defined in INCAR.
    '''

    # INCAR parameters
    params = parsers.incar(join(path, incar))
    start_temp = params['TEBEG']  # Starting temperature
    end_temp = params['TEEND']  # Ending temperature

    # POSCAR paramters
    lattice, coords = parsers.poscar(join(path, poscar))

    # OUTCAR paramters
    comp, vol, press, temp, etots = parsers.outcar(join(path, outcar))

    # Find minium data length because of runs stopping abruptly
    cut = min(map(len, [vol, press, temp]))
    vol = vol[:cut]
    press = press[:cut]
    temp = temp[:cut]
    etots = etots[:cut]

    # Average the last percent amount of holds data
    start = floor(fraction*len(press))
    volume = np.mean(vol[start:])
    pressure = np.mean(press[start:])
    temperature = np.mean(temp[start:])
    etot = np.mean(etots[start:])

    if save_plots:
        n = 4  # Number of plots
        fig, ax = pl.subplots(n)

        x = np.array(range(len(vol)))*float(params['POTIM'])  # Time

        ax[0].plot(x, vol, color='b', label=r'Data')
        ax[1].plot(x, press, color='b', label=r'Data')
        ax[2].plot(x, temp, color='b', label=r'Data')
        ax[3].plot(x, etots, color='b', label=r'Data')

        xmin = x[start]/(max(x)-min(x))  # Fraction not exact due to rounding
        ax[0].axhline(
                      volume,
                      xmin=xmin,
                      color='g',
                      label=r'Mean Data'
                      )
        ax[1].axhline(
                      pressure,
                      xmin=xmin,
                      color='g',
                      label=r'Mean Data'
                      )
        ax[2].axhline(
                      temperature,
                      xmin=xmin,
                      color='g',
                      label=r'Mean Data'
                      )
        ax[3].axhline(
                      etot,
                      xmin=xmin,
                      color='g',
                      label=r'Mean Data'
                      )

        ax[0].set_ylabel(r'Volume $[\AA^{3}]$')
        ax[1].set_ylabel(r'Pressure $[\AA^{3}]$')
        ax[2].set_ylabel(r'Temperature $[\AA^{3}]$')
        ax[3].set_ylabel(r'Total Energy $[eV]$')

        for i in range(n):
            ax[i].axvline(
                          start*float(params['POTIM']),
                          linestyle=':',
                          color='r',
                          label='Averaging start'
                          )
            ax[i].legend(loc='upper left')

        ax[-1].set_xlabel(r'Time $[fs]$')
        fig.tight_layout()

        name = path.strip('../')
        name = name.split('/')
        name = '_'.join(name)
        name += '_thermodynamic.png'

        # Create directory and save figure
        fig.savefig(join(save_plots, name))

        pl.close('all')

    return comp, volume, pressure, temperature, etot, start_temp, end_temp


def iterate(paths, *args, **kwargs):
    '''
    Analyze every run.

    inputs:
        paths = Paths to all runs.

    outputs:
        df = Data frame containing all pertinent information.
    '''

    runs = []
    compositions = []
    volumes = []
    pressures = []
    temperatures = []
    etots = []
    temp_is = []
    temp_fs = []

    counts = str(len(paths))
    count = 1
    for i in paths:

        # Status
        print('Run '+'('+str(count)+'/'+counts+')'+': '+i)

        # Run data
        j, k, l, m, e, n, o = analysis(i, *args)

        runs.append(i)
        compositions.append(j)
        volumes.append(k)
        pressures.append(l)
        temperatures.append(m)
        etots.append(e)
        temp_is.append(n)
        temp_fs.append(o)

        count += 1

    df = {
          'run': runs,
          'composition': compositions,
          'volume': volumes,
          'pressure': pressures,
          'temperature': temperatures,
          'total_energy': etots,
          'start_temperature': temp_is,
          'end_temperature': temp_fs,
          }

    df = pd.DataFrame(df)

    return df
