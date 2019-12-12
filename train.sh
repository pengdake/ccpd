#! /bin/bash

cd $CODE_PATH/ccpd/train_model;python train_cnn.py train -ti $DATA_SET/train_data -tl $DATA_SET/train_data/train_data_label.txt -vi $DATA_SET/validate_train_data -vl $DATA_SET/validate_train_data/validate_train_data.txt -b $BATCH_SIZE -img-size 200 40 -n $EPOCH -c checkpoints/'weights.{epoch:02d}-{val_loss:.2f}.h5' -log log -output-dir $MODEL_PATH

