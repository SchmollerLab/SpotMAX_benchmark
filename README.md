# SpotMAX benchmark methods

A unified Python interface to run all the methods we benchmarked in the SpotMAX manuscript on the SpotMAX 3D ground-truth dataset.

Instructions:

1. Clone this repository with the command `git clone https://github.com/SchmollerLab/SpotMAX_benchmark.git`
2. Download the dataset from [here](https://hmgubox2.helmholtz-muenchen.de/index.php/s/BFpbnnNGNFQCTk3)
3. Extract the dataset to the folder `SpotMAX_benchmark\data\SpotMAX_gt_dataset`
4. Install Cell-ACDC in a dedicated conda environment by following [these instructions](https://cell-acdc.readthedocs.io/en/latest/installation.html#install-latest-version)

To run the analysis, open the terminal, activate the conda environment, navigate to the `SpotMAX_benchmark` folder you cloned before, and run the following command:

```
python src\run.py -m <method_name> -c <channel_name>
```

where you need to replace `<method_name>` and `<channel_name>` with one of the following options:

- Methods: `Piscis`, `Big-FISH`, `Spotiflow`, `U-FISH`
- Channels: `mNeon`, `Cy3`, `MDN1`.

The `mNeon` channel is the mitochondrial DNA dataset, while `Cy3` and `MDN1` are the channels of the single-molecule FISH dataset.

The other available flags for the command are the following:

- `-s`: name of the Spotiflow name to run. Available models are `smfish_3d`, `synth_3d`, and `2025-01-26_10-57-34_finetune_from_synth_3d`
- `-f`: force overwriting existing files for the selected method
- `-i`: inspect results on each image

Once the analysis is completed, each `Images` folder in the dataset will have the CSV file of the selected method containing the coordinates of the detected spots.

For example, for Piscis, you will have the following file: 
```
"SpotMAX_benchmark\data\SpotMAX_gt_dataset\Yeast_smFISH\MDN1_gene\Position_1\Images\MMY116_2c_ACT1_MDN1_7_s10_MDN1_piscis_coords.csv"
```
