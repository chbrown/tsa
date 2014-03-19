import os
import numpy as np

from tsa import logging
logger = logging.getLogger(__name__)

from itertools import cycle, izip
import matplotlib.cm as colormap
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# import matplotlib.dates as mdates
plt.rcParams['interactive'] = True
plt.rcParams['axes.grid'] = True

qmargins = [0, 5, 10, 50, 90, 95, 100]

# plt.rcParams['ps.useafm'] = True
# plt.rcParams['pdf.use14corefonts'] = True
# plt.rcParams['text.usetex'] = True


def fig_path(name, index=0):
    '''
    `name should be a full filename, like issue2.pdf.
    This will never return a filename that exists at the time of calling the function.
    '''
    dirpath = os.path.expanduser('~/Dropbox/ut/qp/qp-2/figures')
    base, ext = os.path.splitext(name)
    filename = base + ('-%02d' % index if index > 0 else '') + ext
    filepath = os.path.join(dirpath, filename)
    if os.path.exists(filepath):
        return fig_path(name, index + 1)
    logger.info('Using filepath: %r', filepath)
    return filepath


def clear():
    plt.cla()
    plt.axes(aspect='auto')
    # plt.axis('tight')
    # plt.tight_layout()
    plt.margins(0.025, tight=True)


markers = {0: 'tickleft', 1: 'tickright', 2: 'tickup', 3: 'tickdown', 4: 'caretleft', 'D': 'diamond', 6: 'caretup', 7: 'caretdown', 's': 'square', '|': 'vline', '': 'nothing', 'None': 'nothing', 'x': 'x', 5: 'caretright', '_': 'hline', '^': 'triangle_up', None: 'nothing', 'd': 'thin_diamond', ' ': 'nothing', 'h': 'hexagon1', '+': 'plus', '*': 'star', ',': 'pixel', 'o': 'circle', '.': 'point', '1': 'tri_down', 'p': 'pentagon', '3': 'tri_left', '2': 'tri_up', '4': 'tri_right', 'H': 'hexagon2', 'v': 'triangle_down', '8': 'octagon', '<': 'triangle_left', '>': 'triangle_right'}

def _styles():
    # I can distinguish about six different colors from rainbow
    colors = colormap.rainbow(np.linspace(1, 0, 6))
    # and a few different linestyles
    linestyles = ['-', ':', '--', '-.']
    # and linewidth
    linewidths = [1, 2, 3]
    # this produces 6*4*3 = 72 styles, way more than you should really put on a single plot.
    for linewidth in linewidths:
        for linestyle in linestyles:
            for color in colors:
                yield dict(linewidth=linewidth, linestyle=linestyle, color=color)

# this will take those 72 style combos from style_gen() and loop indefinitely.
styles = cycle(_styles())


def _distinct_styles():
    # e.g., for the colorblind
    linewidths = [1, 2, 3]
    linestyles = ['-', ':', '--', '-.']
    colors = colormap.rainbow(np.linspace(1, 0, 6))
    # period = 60
    # markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd']

    zipped = izip(cycle(linewidths), cycle(linestyles), cycle(colors))
    for linewidth, linestyle, color in zipped:
        yield dict(linewidth=linewidth, linestyle=linestyle, color=color)

distinct_styles = _distinct_styles()
