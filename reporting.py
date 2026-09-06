"""Shared reporting conventions, copied locally so this repository is standalone."""
import argparse
import csv
import json
from pathlib import Path
import platform
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg', force=True)


def arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--seed', type=int, default=2023, help='Random seed (not a creation date)')
    parser.add_argument('--output', type=Path, default=Path('results'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    return args, args.output


def csv_write(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def style():
    matplotlib.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.titleweight': 'bold',
        'axes.grid': True, 'grid.alpha': .15, 'figure.facecolor': 'white',
        'axes.labelcolor': '#24344a', 'text.color': '#24344a', 'savefig.facecolor': 'white'})


def finish(out, summary):
    summary['environment'] = {'python': platform.python_version(), 'numpy': np.__version__,
                              'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__}
    (out/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print(json.dumps(summary, indent=2, allow_nan=False))
