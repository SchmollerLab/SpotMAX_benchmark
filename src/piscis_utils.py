import os

import numpy as np
import pandas as pd

import skimage.io

from tqdm import tqdm

import torch

from piscis import Piscis

from _base_utils import spotmax_gt_dataset_path, get_basename

def run(
        input_files, 
        inspect=False, 
        save_to_images_path=True, 
        return_final_df=False,
        df_coords_endname='',
        threshold=0.5,
        **kwargs
    ):
    # Load the Piscis model.
    if torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'
    model = Piscis(model_name='20251212', device=device)

    dfs = {}
    
    pbar = tqdm(total=len(input_files), ncols=100)
    for img_filepath, lab_filepath in input_files:
        images_path = os.path.dirname(img_filepath)
        basename = get_basename(images_path)
        filename_no_ext = os.path.splitext(os.path.basename(img_filepath))[0]
        channel = filename_no_ext[len(basename):]

        piscis_filename = (
            f'{basename}{channel}_piscis_coords{df_coords_endname}.csv'
        )
        piscis_filepath = os.path.join(images_path, piscis_filename)
        if os.path.exists(piscis_filepath):
            pbar.update()
            continue
            
        img = skimage.io.imread(img_filepath)
        
        lab = np.load(lab_filepath)['arr_0']
        
        points = model.predict(
            img, 
            threshold=threshold,
            stack=True
        )
        
        coords = np.round(points).astype(int)
        
        IDs = lab[coords[:, 1], coords[:, 2]]
        df_piscis = pd.DataFrame(data=points, columns=['z', 'y', 'x'], index=IDs)
        df_piscis.index.name = 'Cell_ID'
        
        if inspect:
            from cellacdc.plot import imshow
            SizeZ = img.shape[0]
            lab_3d = np.array([lab]*SizeZ)
            imshow(lab_3d, img, points_coords_df=df_piscis)
            import pdb; pdb.set_trace()
        
        if save_to_images_path:
            df_piscis.to_csv(piscis_filepath)
        
        if return_final_df:
            pos_folderpath = os.path.dirname(images_path)
            pos_foldername = os.path.basename(pos_folderpath)
            exp_folderpath = os.path.dirname(pos_folderpath)
            exp_foldername = os.path.basename(exp_folderpath)
            exp_rel_path = os.path.relpath(
                exp_folderpath, spotmax_gt_dataset_path
            ).replace('\\', '/')
            
            key = (
                spotmax_gt_dataset_path.replace('\\', '/'),
                exp_rel_path, 
                pos_foldername,
                channel
            )
            
            dfs[key] = df_piscis
        
        pbar.update()
    pbar.close()
    
    if not return_final_df:
        return
    
    final_df = pd.concat(
        dfs, 
        names=(
            'src_dset_path', 
            'exp_rel_path', 
            'pos_foldername', 
            'channel',
        )
    ) 
    
    return final_df