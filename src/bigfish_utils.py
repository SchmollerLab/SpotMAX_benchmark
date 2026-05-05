
import os

from configparser import ConfigParser
import re

import numpy as np
import pandas as pd

import skimage.io

from tqdm import tqdm

import bigfish.detection as detection

from cellacdc.plot import imshow

from _base_utils import get_basename, spotmax_gt_dataset_path

def get_input_files(channels, foce_recompute=True, df_coords_endname=''):
    if foce_recompute:
        for root, dir, files in os.walk(spotmax_gt_dataset_path):    
            if not root.endswith('Images'):
                continue
            
            if foce_recompute:
                for file in files:
                    if file.endswith(f'_bigfish_coords{df_coords_endname}.csv'):
                        os.remove(os.path.join(root, file))

    input_files = []
    for root, dir, files in os.walk(spotmax_gt_dataset_path):    
        if not root.endswith('Images'):
            continue
        
        files = [file for file in files if not file.startswith('.')]
        basename = os.path.commonprefix(files)
        
        img_filepaths = []
        lab_filepath = None
        metadata_csv_filepath = None
        smax_ini_filepath = None
        for file in files:
            for channel in channels:
                if file.endswith(f'{channel}.tif'):
                    img_filepaths.append(os.path.join(root, file))
            
            if file == f'{basename}segm.npz':
                lab_filepath = os.path.join(root, file)
            elif file == f'{basename}metadata.csv':
                metadata_csv_filepath = os.path.join(root, file)
                
        pos_path = os.path.dirname(root)
        smax_path = os.path.join(pos_path, 'spotMAX_output')
        if not os.path.exists(smax_path):
            continue
        
        for smax_file in os.listdir(smax_path):
            if (
                    smax_file.startswith('1_analysis_parameters') 
                    and smax_file.endswith('.ini')
                ):
                smax_ini_filepath = os.path.join(smax_path, smax_file)
                break
        
        if smax_ini_filepath is None:
            for smax_file in os.listdir(smax_path):
                if (
                        smax_file.startswith('2_analysis_parameters') 
                        and smax_file.endswith('.ini')
                    ):
                    smax_ini_filepath = os.path.join(smax_path, smax_file)
                    break
        
        if not img_filepaths:
            continue
        
        if lab_filepath is None:
            continue
        
        if metadata_csv_filepath is None:
            continue
        
        if smax_ini_filepath is None:
            continue
        
        for img_filepath in img_filepaths:
            input_files.append(
                (img_filepath, lab_filepath, metadata_csv_filepath, smax_ini_filepath)
            )
    return input_files

def run(
        input_files, 
        inspect=False, 
        save_to_images_path=True, 
        return_final_df=False,
        df_coords_endname='',
        threshold_percentage=None
    ):
    pbar = tqdm(total=len(input_files), ncols=100)
    for files in input_files:
        img_filepath, lab_filepath, metadata_csv_filepath, smax_ini_filepath = files
        images_path = os.path.dirname(img_filepath)
        basename = get_basename(images_path)
        filename_no_ext = os.path.splitext(os.path.basename(img_filepath))[0]
        channel = filename_no_ext[len(basename):]
        
        bigfish_filename = (
            f'{basename}{channel}_bigfish_coords{df_coords_endname}.csv'
        )
        bigfish_filepath = os.path.join(images_path, bigfish_filename)
        if os.path.exists(bigfish_filepath):
            pbar.update()
            continue
            
        img = skimage.io.imread(img_filepath)
        lab = np.load(lab_filepath)['arr_0']
        
        df_metadata = pd.read_csv(metadata_csv_filepath, index_col='Description')
        voxel_size_z_nm = float(
            df_metadata.at['PhysicalSizeZ', 'values']) * 1000
        pixel_size_y_nm = float(
            df_metadata.at['PhysicalSizeY', 'values']) * 1000
        pixel_size_x_nm = float(
            df_metadata.at['PhysicalSizeX', 'values']) * 1000
        voxel_size = (voxel_size_z_nm, pixel_size_y_nm, pixel_size_x_nm)
        
        cp = ConfigParser()
        cp.read(smax_ini_filepath)        
        spot_size_text = (
            cp['METADATA']['Spot (z, y, x) minimum dimensions (radius)']
        )
        spot_size_text = re.findall(
            r'(\d+\.\d+), (\d+\.\d+), (\d+\.\d+)\) micrometer', spot_size_text
        )[0]
        spot_radius = tuple(float(x)*1000/2 for x in spot_size_text)
        
        points, threshold = detection.detect_spots(
            images=img, 
            return_threshold=True, 
            voxel_size=voxel_size,  # in nanometer (one value per dimension zyx)
            spot_radius=spot_radius,
            threshold_percentage=threshold_percentage
        )
        
        coords = np.round(points).astype(int)
        
        IDs = lab[coords[:, 1], coords[:, 2]]
        df_bigfish = pd.DataFrame(data=points, columns=['z', 'y', 'x'], index=IDs)
        df_bigfish.index.name = 'Cell_ID'
        
        if inspect:
            from cellacdc.plot import imshow
            SizeZ = img.shape[0]
            lab_3d = np.array([lab]*SizeZ)
            imshow(lab_3d, img, points_coords_df=df_bigfish)
            import pdb; pdb.set_trace()
        
        if save_to_images_path:
            df_bigfish.to_csv(bigfish_filepath)
        
        pbar.update()
    pbar.close()