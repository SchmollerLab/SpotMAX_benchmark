import argparse

from importlib import import_module

methods = (
    'Piscis', 
    'Big-FISH', 
    'Spotiflow', 
    'U-FISH'
)

ap = argparse.ArgumentParser(
    prog='SpotMAX benchmark',
    formatter_class=argparse.RawTextHelpFormatter
)

ap.add_argument(
    '-m', '--method_name',
    default='',
    type=str,
    metavar='METHOD_NAME',
    choices=methods,
    help=(
        'Name of the method to run'
    )
)

args = ap.parse_args()