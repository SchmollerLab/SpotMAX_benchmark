import os

import cellacdc.myutils as acdc_myutils

src_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(src_path)
data_path = os.path.join(project_path, 'data')
spotmax_gt_dataset_path = os.path.join(data_path, 'SpotMAX_gt_dataset')
spotiflow_trained_models = os.path.join(
    project_path, 'spotiflow_trained_models'
)

def get_basename(images_path):
    valid_files = acdc_myutils.listdir(images_path)
    return os.path.commonprefix(valid_files)

def get_input_files(channels, foce_recompute=True, df_coords_endname=''):
    if foce_recompute:
        for root, dir, files in os.walk(spotmax_gt_dataset_path):    
            if not root.endswith('Images'):
                continue
            
            if foce_recompute:
                for file in files:
                    if file.endswith(f'_piscis_coords{df_coords_endname}.csv'):
                        os.remove(os.path.join(root, file))

    input_files = []
    for root, dir, files in os.walk(spotmax_gt_dataset_path):    
        if not root.endswith('Images'):
            continue
        
        basename = get_basename(root)
        
        img_filepaths = []
        lab_filepath = None
        for file in files:
            for channel in channels:
                if file.endswith(f'{channel}.tif'):
                    img_filepaths.append(os.path.join(root, file))
            
            if file == f'{basename}segm.npz':
                lab_filepath = os.path.join(root, file)
        
        if not img_filepaths or lab_filepath is None:
            continue
        
        for img_filepath in img_filepaths:
            input_files.append((img_filepath, lab_filepath))

    
    return input_files