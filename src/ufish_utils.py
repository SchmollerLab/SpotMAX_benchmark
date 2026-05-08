import os

import numpy as np
import pandas as pd

import skimage.io

from tqdm import tqdm

import torch

from ufish.api import UFish

from cellacdc.plot import imshow

def run(
        input_files, 
        inspect=False, 
        save_to_images_path=True, 
        return_final_df=False,
        df_coords_endname='',
        threshold=0.5,
        **kwargs
    ):
    # Load the U-FISH model.
    if torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'
        
    # Load the U-FISH model.
    model = UFish(device=device)
    model.load_weights()

    pbar = tqdm(total=len(input_files), ncols=100)
    for img_filepath, lab_filepath in input_files:
        images_path = os.path.dirname(img_filepath)
        basename = get_basename(images_path)
        filename_no_ext = os.path.splitext(os.path.basename(img_filepath))[0]
        channel = filename_no_ext[len(basename):]

        ufish_filename = f'{basename}{channel}_ufish_coords.csv'
        ufish_filepath = os.path.join(images_path, ufish_filename)
        if os.path.exists(ufish_filepath):
            pbar.update()
            continue
            
        img = skimage.io.imread(img_filepath)
        
        lab = np.load(lab_filepath)['arr_0']
        
        df_points, enhanced_img = model.predict(img, axes='zyx')
        
        coords = df_points.values.astype(int)
        
        IDs = lab[coords[:, 1], coords[:, 2]]
        df_ufish = pd.DataFrame(data=coords, columns=['z', 'y', 'x'], index=IDs)
        df_ufish.index.name = 'Cell_ID'
        
        if INSPECT:
            from cellacdc.plot import imshow
            SizeZ = img.shape[0]
            lab_3d = np.array([lab]*SizeZ)
            imshow(lab_3d, img, enhanced_img, points_coords_df=df_ufish)
            import pdb; pdb.set_trace()
        
        df_ufish.to_csv(ufish_filepath)
        
        pbar.update()
    pbar.close()