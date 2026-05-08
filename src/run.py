import argparse

from importlib import import_module

from _base_utils import get_input_files

methods = (
    'Piscis', 
    'Big-FISH', 
    'Spotiflow', 
    'U-FISH'
)

channels = (
    'mNeon',
    'Cy3',
    'ACT1',
    'MDN1'
)

spotiflow_models = (
    'smfish_3d',
    'synth_3d',
    '2025-01-26_10-57-34_finetune_from_synth_3d'
)

ap = argparse.ArgumentParser(
    prog='SpotMAX benchmark',
    formatter_class=argparse.RawTextHelpFormatter
)

ap.add_argument(
    '-m', '--method_name',
    required=True,
    type=str,
    metavar='METHOD_NAME',
    choices=methods,
    help=(
        'Name of the method to run'
    )
)

ap.add_argument(
    '-c', '--channel_name',
    required=True,
    type=str,
    metavar='CHANNEL_NAME',
    choices=channels,
    help=(
        'Channel name to analyse'
    )
)

ap.add_argument(
    '-s', '--spotiflow_model_name',
    default='',
    type=str,
    metavar='SPOTIFLOW_MODEL_NAME',
    choices=spotiflow_models,
    help=(
        'Name of the Spotiflow name to run. '
        'Do not use if you are not running Spotiflow'
    )
)

ap.add_argument(
    '-f', '--force_recompute',
    action='store_true',
    help=(
        'Force overwriting existing files for the selected method'
    )
)

ap.add_argument(
    '-i', '--inspect',
    action='store_true',
    help=(
        'Visualize results on every image'
    )
)

args = ap.parse_args()

method_name = args.method_name

channel = args.channel_name
channels = (channel,)
force_recompute = args.force_recompute
inspect = args.inspect
spotiflow_model_name = args.spotiflow_model_name

print(f'Importing {method_name}...')

method_utils_module = method_name.replace('-', '').lower()
method_utils_module = f'{method_utils_module}_utils'

method_utils = import_module(method_utils_module)

if method_name == 'Spotiflow':
    method_utils.download_models()

try:
    get_input_files_func = method_utils.get_input_files
except Exception as err:
    get_input_files_func = get_input_files

input_files = get_input_files_func(
    channels, 
    foce_recompute=force_recompute
)

print(f'Running {method_name}...')

method_utils.run(
    input_files, 
    inspect=inspect,
    save_to_images_path=True, 
    return_final_df=False,
    model_weights_filename=spotiflow_model_name
)

print(f'Running {method_name} done.')