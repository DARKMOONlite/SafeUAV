# SafeUAV: Learning to estimate depth and safe landing areas for UAVs from synthetic data

This repository holds the implementation of the paper, presented at the UAVision2018 workshop (ECCV).

# Installation:
> [!INFO]
> use Docker version >= `20.10`.



You can download pre-train model, datasets and Docker image [here][safeuav/data].
### Building the Image
```bash
    docker build --build-arg ARCH=$(uname -m) docker/ -t safeuav
```


### Run on Jetson
```bash
    docker run --privileged --runtime=nvidia --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -v "$(pwd)/data:/SafeUAV/data" -it safeuav:latest
```
### Run on PC
```bash
    docker run --privileged --gpus all -v "$(pwd)/data:/SafeUAV/data" -it safeuav:latest
```
> [!TIP]
> to train on the dataset or a specific video feed, place them into the data folder. 
> The dataset can be downloaded [here](https://www.google.com/url?q=https%3A%2F%2Fctipub-my.sharepoint.com%2F%3Af%3A%2Fg%2Fpersonal%2Fdragos_costea_upb_ro%2FEnDVg5UkHhpHmNXjQ_QnpwEBwi5cXUOiNH476vOObd1GBw%3Fe%3DwWnDXM&sa=D&sntz=1&usg=AOvVaw15C4Wq1Ay14P1YBRZ4XTbc)
> Models can be downloaded from [here](https://sites.google.com/site/aerialimageunderstanding/safeuav-learning-to-estimate-depth-and-safe-landing-areas-for-uavs)




## Standard variables
```bash

export model= "unet_tiny_sum" #unet_tiny_sum/unet_big_concatenate/deeplabv3plus/unet_classic  # pick one
export dir="data" # this folder should not exist
export lr=0.001
export patience=4
export factor=0.1
export num_epochs=100
export batch_size=4
```

# Options
1. **Train:** trains the model
2. **Test:** tests the model to obtain results.
3. **Retrain:** I assume this is for retraining a model that already exists.

# HVO vs Depth
- if wanting to train/test the depth estimation model please choose **regression**
- if wanting to train/test the landing zone detection please choose **classification**

# Training or Testing a model
## Training:
modify any of the environment variables as needed to get your desired outcome.
```sh
python3.7 main.py train {classification/regression} {path to dataset.h5} 
--model=$model \
--dir=$dir \
--label_dims="hvn_gt_p1" \
--batch_size=$batch_size \
--optimizer="Adam" \
--learning_rate=$lr \
--patience=$patience \
--factor=$factor \
--num_epochs=$num_epochs
```
## Testing
```bash
python3.7 main.py test {classification/regression} {path to dataset.h5} \
--weights_file={path to checkpoint.pkl} \
--model=$model \
--test_plot_results=1 \ 
--label_dims="hvn_gt_p1" \
--batch_size=$batch_size
```

## Running on an existing video (outputs another video)

```sh
python3.7 main_inference_video.py {classification/regression} in_video.mp4 out_video.mp4 \
--weights_file= {path to checkpoint file.pkl} \
--model=$model

```
