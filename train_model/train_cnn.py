import os
import argparse

import cv2
import numpy as np
from keras import backend as K
from keras.layers import Input, Activation, Conv2D, BatchNormalization, Lambda, MaxPooling2D, Dropout
from keras.models import Model
from keras.optimizers import SGD
from keras.callbacks import ModelCheckpoint, TensorBoard

CHARS = ['京', '沪', '津', '渝', '冀', '晋', '蒙', '辽', '吉', '黑',
         '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤',
         '桂', '琼', '川', '贵', '云', '藏', '陕', '甘', '青', '宁',
         '新',
         '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
         'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K',
         'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
         'W', 'X', 'Y', 'Z',
         '港', '学', '使', '警', '澳', '挂', '军', '北', '南', '广',
         '沈', '兰', '成', '济', '海', '民', '航', '空',
         ]

CHARS_DICT = {char:i for i, char in enumerate(CHARS)}

NUM_CHARS = len(CHARS)

# The actual loss calc occurs here despite it not being
# an internal Keras loss function
def ctc_lambda_func(args):
    y_pred, labels, input_length, label_length = args
    y_pred = y_pred[:, :, 0, :]
    return K.ctc_batch_cost(labels, y_pred, input_length, label_length)

def build_model(width, num_channels):
    input_tensor = Input(name='the_input', shape=(width, 40, num_channels), dtype='float32')
    x = input_tensor
    base_conv = 32

    for i in range(3):
        x = Conv2D(base_conv * (2 ** (i)), (3, 3), padding="same")(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Conv2D(256, (5, 5))(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv2D(1024, (1, 1))(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv2D(NUM_CHARS+1, (1, 1))(x)
    x = Activation('softmax')(x)

    y_pred = x
    return input_tensor, y_pred

def encode_label(s):
    label = np.zeros([len(s)])
    for i, c in enumerate(s):
        label[i] = CHARS_DICT[c]
    return label

def parse_line(line):
    parts = line.split(':')
    filename = parts[0]
    label = encode_label(parts[1].strip().upper())
    return filename, label

class TextImageGenerator:
    def __init__(self, img_dir, label_file, batch_size, img_size, input_length, num_channels=3, label_len=5):
        self._img_dir = img_dir
        self._label_file = label_file
        self._batch_size = batch_size
        self._num_channels = num_channels
        self._label_len = label_len
        self._input_len = input_length
        self._img_w, self._img_h = img_size

        self._num_examples = 0
        self._next_index = 0
        self._num_epoches = 0
        self.filenames = []
        self.labels = None

        self.init()

    def init(self):
        self.labels = []
        with open(self._label_file) as f:
            for line in f:
                filename, label = parse_line(line)
                self.filenames.append(filename)
                self.labels.append(label)
                self._num_examples += 1
        self.labels = np.float32(self.labels)

    def next_batch(self):
        # Shuffle the data
        if self._next_index == 0:
            perm = np.arange(self._num_examples)
            np.random.shuffle(perm)
            self._filenames = [self.filenames[i] for i in perm]
            self._labels = self.labels[perm]

        batch_size = self._batch_size
        start = self._next_index
        end = self._next_index + batch_size
        if end >= self._num_examples:
            self._next_index = 0
            self._num_epoches += 1
            end = self._num_examples
            batch_size = self._num_examples - start
        else:
            self._next_index = end
        images = np.zeros([batch_size, self._img_h, self._img_w, self._num_channels])
        # labels = np.zeros([batch_size, self._label_len])
        for j, i in enumerate(range(start, end)):
            fname = self._filenames[i]
            img = cv2.imread(os.path.join(self._img_dir, fname))
            images[j, ...] = img
        images = np.transpose(images, axes=[0, 2, 1, 3])
        labels = self._labels[start:end, ...]
        input_length = np.zeros([batch_size, 1])
        label_length = np.zeros([batch_size, 1])
        input_length[:] = self._input_len
        label_length[:] = self._label_len
        outputs = {'ctc': np.zeros([batch_size])}
        inputs = {'the_input': images,
                  'the_labels': labels,
                  'input_length': input_length,
                  'label_length': label_length,
                  }
        return inputs, outputs

    def get_data(self):
        while True:
            yield self.next_batch()

def train(args):
    """Train the OCR model
    """
    ckpt_dir = os.path.dirname(args.c)
    if not os.path.isdir(ckpt_dir):
        os.makedirs(ckpt_dir)

    if args.log != '' and not os.path.isdir(args.log):
        os.makedirs(args.log)
    label_len = args.label_len

    input_tensor, y_pred = build_model(args.img_size[0], args.num_channels)

    labels = Input(name='the_labels', shape=[label_len], dtype='float32')
    input_length = Input(name='input_length', shape=[1], dtype='int32')
    label_length = Input(name='label_length', shape=[1], dtype='int32')

    pred_length = int(y_pred.shape[1])
    # Keras doesn't currently support loss funcs with extra parameters
    # so CTC loss is implemented in a lambda layer
    loss_out = Lambda(ctc_lambda_func, output_shape=(1,), name='ctc')([y_pred, labels, input_length, label_length])

    # clipnorm seems to speeds up convergence
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.0, nesterov=True, clipnorm=5)

    model = Model(inputs=[input_tensor, labels, input_length, label_length], outputs=loss_out)

    # the loss calc occurs elsewhere, so use a dummy lambda func for the loss
    model.compile(loss={'ctc': lambda y_true, y_pred: y_pred}, optimizer=sgd)

    if args.pre != '':
        model.load_weights(args.pre)

    train_gen = TextImageGenerator(img_dir=args.ti,
                                 label_file=args.tl,
                                 batch_size=args.b,
                                 img_size=args.img_size,
                                 input_length=pred_length,
                                 num_channels=args.num_channels,
                                 label_len=label_len)

    val_gen = TextImageGenerator(img_dir=args.vi,
                                 label_file=args.vl,
                                 batch_size=args.b,
                                 img_size=args.img_size,
                                 input_length=pred_length,
                                 num_channels=args.num_channels,
                                 label_len=label_len)

    #checkpoints_cb = ModelCheckpoint(args.c, period=1)
    model_path = "%s/ocr_wrnn_ccpd_model.h5" % args.output_dir
    checkpoints_cb = ModelCheckpoint(model_path, period=1, save_best_only=True)
    cbs = [checkpoints_cb]

    if args.log != '':
        tfboard_cb = TensorBoard(log_dir=args.log, write_images=True)
        cbs.append(tfboard_cb)

    model.fit_generator(generator=train_gen.get_data(),
                        steps_per_epoch=(train_gen._num_examples+train_gen._batch_size-1) // train_gen._batch_size,
                        epochs=args.n,
                        validation_data=val_gen.get_data(),
                        validation_steps=(val_gen._num_examples+val_gen._batch_size-1) // val_gen._batch_size,
                        callbacks=cbs,
                        initial_epoch=args.start_epoch)
    #model.save("test_save_model.h5")

def export(args):
    """Export the model to an hdf5 file
    """
    input_tensor, y_pred = build_model(None, args.num_channels)
    model = Model(inputs=input_tensor, outputs=y_pred)
    model.save(args.m)
    print('model saved to {}'.format(args.m))

def main ():
    ps = argparse.ArgumentParser()
    ps.add_argument('-num_channels', type=int, help='number of channels of the image', default=3)
    subparsers = ps.add_subparsers()

    # Parser for arguments to train the model
    parser_train = subparsers.add_parser('train', help='train the model')
    parser_train.add_argument('-ti','--train_img', dest='ti', help='train img dir', required=True)
    parser_train.add_argument('-tl','--train_label', dest='tl', help='train label file', required=True)
    parser_train.add_argument('-vi','--validate_img', dest='vi', help='validate img dir', required=True)
    parser_train.add_argument('-vl','--validate_label', dest='vl', help='validate label file', required=True)
    parser_train.add_argument('-b','--batch_size', dest='b', type=int, help='batch size', required=True)
    parser_train.add_argument('-img-size', type=int, nargs=2, help='width and length of tran img', required=True)
    parser_train.add_argument('-pre','--pre_trained_weight', dest='pre', help='pre trained weight file', default='')
    parser_train.add_argument('-start-epoch', type=int, default=0)
    parser_train.add_argument('-n','--epochs',dest='n', type=int, help='number of epochs', required=True)
    parser_train.add_argument('-label-len', type=int, help='label length', default=7)
    parser_train.add_argument('-c','--checkpoint_format',dest='c', help='checkpoints format string', required=True)
    parser_train.add_argument('-log', help='tensorboard log dir', default='')
    parser_train.add_argument('-output-dir', help='model save path', default='')
    parser_train.set_defaults(func=train)

    # Argument parser of arguments to export the model
    parser_export = subparsers.add_parser('export', help='export model to hdf5')
    parser_export.add_argument('-m','--model_name',dest='m', help='export model name(.h5)', required=True)
    parser_export.set_defaults(func=export)

    args = ps.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
