hyperlpr-train_e2e
======
A simple code for creating licence plate images and train e2e network based on [HyperLPR](https://github.com/zeusees/HyperLPR)   

****
	
|Author|LCorleone|
|---|---
|E-mail|lcorleone@foxmail.com


****
## Requirements
* tensorflow 1.5
* keras 2.2.0
* some common packages like numpy and so on.

# 0.Start
```bash
git clone https://github.com/caisan/A-Simple-Chinese-License-Plate-Generator-and-Recognition-Framework
cd A-Simple-Chinese-License-Plate-Generator-and-Recognition-Framework
```

## 1.Prepare dir
```bash
mkdir -p ./data/train_data
```
```bash
mkdir -p ./data/validate_train_data
```

## 2.Prepare train data
```bash
python create_train_data.py ./data/train_data ./data/train_data/train_data_label.txt 6000
```
Images for trainning will be generated in the dir ``` ./data/train_data```, and the image-label file will be generated in the dir ```./data/train_data/train_data_label.txt```
batch size is 6000.

## 3.Prepare validate data
```bash
python create_train_data.py ./data/validate_train_data ./data/validate_train_data/validate_train_data.txt 300
```
This process aims to generate images for validate when training.

## 4.Train
```bash
python main.py train -ti ./data/train_data -tl ./data/train_data/train_data_label.txt -vi ./data/validate_train_data -vl ./data/validate_train_data/validate_train_data.txt -b 16 -img-size 200 40 -n 100 -c checkpoints/'weights.{epoch:02d}-{val_loss:.2f}.h5' -log log
```
After training, the model is in dir ```checkpoints```. It will be loaded for predicting.

## 5. Test your model and predict plate
Use test_model.py for testing!
```bash
python test_model.py <Your Plate image path>
```
~~NOTE: it is better using ./data/train_data/xxx.jpg as testing image.~~
test_model.py is inspired by https://github.com/zeusees/HyperLPR

For example you can test the plate image: https://github.com/zeusees/HyperLPR/blob/master/images_rec/1.jpg

## Other:Detect chinese plate region
Use detect_plate.py for detecting chinese plate demo !
```bash
python detect_plate.py <Your plate image path>
```
After execute detect_plate.py, you will get a image named ./cc_plate.jpg with plate region only.
**NOTE**: this is not predict, it is detect only

# Docker file
docker file for building docker image:
```bash
cd docker
docker build -f ./Dockerfile -t ccpd-keras-test:v1 .
```

## Attention
* The image size created automatically is 200 * 40, fix the input size when you use the e2e network. You can create and train your own e2e network if you want.  
* Generate at least 50000 images for training, less may degrade the performance.
* Also, when tested in real scene, the e2e network performs not very well due to that the images' quality created automatically are still poor. If you have real image dataset and labels, it may be perfect.  

