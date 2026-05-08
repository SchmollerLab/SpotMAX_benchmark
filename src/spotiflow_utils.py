import os
import tempfile
import shutil

import numpy as np
import pandas as pd

import skimage.io

from tqdm import tqdm

from spotiflow.model import Spotiflow

try:
    from cellacdc.plot import imshow
except Exception as err:
    pass

from _base_utils import spotiflow_trained_models, project_path

def download_models():
    if os.path.exists(spotiflow_trained_models):
        return
    
    print('Downloading Spotiflow fine-tuned models...')
    from cellacdc.myutils import download_url, extract_zip
    
    url = (
        'https://hmgubox5.helmholtz-munich.de/public.php/dav/files/LmM7ZTaaZgFycCY/?accept=zip'
    )
    file_size = 550296065
    
    temp_folder_path = tempfile.mkdtemp()
    temp_zip_path = os.path.join(
        temp_folder_path, 'spotiflow_trained_models.zip'
    )
    
    download_url(url, temp_zip_path, file_size=file_size, desc='Spotiflow')
    extract_zip(temp_zip_path, temp_folder_path, verbose=False)
    
    for root, dirs, files in os.walk(temp_folder_path):
        for file in files:
            if file.endswith('.zip'):
                continue
            
            src_filepath = os.path.join(root, file)
            src_relpath = os.path.relpath(src_filepath, temp_folder_path)
            dst_filepath = f'{project_path}{os.sep}{src_relpath}'
            
            os.makedirs(os.path.dirname(dst_filepath), exist_ok=True)
            
            shutil.move(src_filepath, dst_filepath)
    
    shutil.rmtree(temp_folder_path)

def run(
        input_files, 
        inspect=False, 
        save_to_images_path=True, 
        return_final_df=False,
        df_coords_endname='',
        threshold=0.5,
        model_weights_filename='smfish_3d',
        **kwargs
    ):
    trained_model_path = os.path.join(
        spotiflow_trained_models, model_weights_filename
    )
    
    if os.path.exists(trained_model_path):
        model = Spotiflow.from_folder(trained_model_path)
    else:
        model = Spotiflow.from_pretrained(pretrained_model_name)
    
    pbar = tqdm(total=len(input_files), ncols=100)
    for img_filepath, lab_filepath in input_files:
        images_path = os.path.dirname(img_filepath)
        basename = get_basename(images_path)
        
        spotiflow_filename = f'{basename}spotiflow_{pretrained_model_name}_coords.csv'
        spotiflow_filepath = os.path.join(images_path, spotiflow_filename)
            
        img = skimage.io.imread(img_filepath)
        
        lab = np.load(lab_filepath)['arr_0']
        points, details = model.predict(img, verbose=False)
        
        coords = np.round(points).astype(int)
        
        if INSPECT:
            lab3d = np.array([lab]*len(img))
            imshow(img, lab3d, points_coords=coords, annotate_labels_idxs=[1])

        IDs = lab[coords[:, 1], coords[:, 2]]
        df_spotiflow = pd.DataFrame(data=points, columns=['z', 'y', 'x'], index=IDs)
        df_spotiflow.index.name = 'Cell_ID'
        
        df_spotiflow.to_csv(spotiflow_filepath)
        
        pbar.update()
    pbar.close()
    