import tensorflow as tf
import math
import numpy as np
from tensorflow.contrib.learn.python.learn.datasets import base
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import random_seed
from sklearn.preprocessing import StandardScaler


def weight_variable(shape):
    initial_ = tf.truncated_normal(shape, stddev=1.0 / math.sqrt(float(shape[0])))
    return tf.Variable(initial_, name='weights')


def bias_variable(shape):
    initial_ = tf.random_uniform(shape, minval=0, maxval=0.001, dtype=tf.float32, seed=None, name=None)
    return tf.Variable(initial_, name='biases')


def conv2d(x, W):
    """
    Computes a 2-D convolution given 4-D input and filter tensors.

    Given an input tensor (x) of shape [batch, in_height, in_width, in_channels] and a filter / kernel (W) tensor of
    shape [filter_height, filter_width, in_channels, out_channels], this op performs the following:

    Flattens the filter to a 2-D matrix with shape [filter_height * filter_width * in_channels, output_channels].
    Extracts image patches from the input tensor to form a virtual tensor of shape [batch, out_height, out_width,
    filter_height * filter_width * in_channels].

    For each patch, right-multiplies the filter matrix and the image patch vector.
    """
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_flat(x):#, num_days):
    c1 = 1
    c2 = 2#num_days
    return tf.nn.max_pool(x, ksize=[1, c1, c2, 1], strides=[1, 1, 1, 1], padding='SAME')


def cnn(disks, num_features, num_days, num_classes, keep_prob_value, verbose=False):
    """
    A convolutional neural net may not make sense here, but here we have a toy model
    The goal is to convolove and maxpool only along one feature at a time though with no mixing between features
    It is possible that single day outlier values of a feature strongly predict future failure
    disks will have shape of [batch_size, num_features, num_days, 1]
    """
    disks = tf.reshape(disks, [-1, num_features, num_days, 1])
    hidden1 = 32
    hidden2 = 64
    dense_layer = 1024
    con_height = 1
    con_width = num_days
    W_conv1 = weight_variable([con_height, con_width, 1, hidden1])
    b_conv1 = bias_variable([hidden1])
    c1 = conv2d(disks, W_conv1)
    h_conv1 = tf.nn.relu(c1 + b_conv1)
    h_pool1 = max_pool_flat(h_conv1)
    if verbose:
        print("Shape of disk data tensor: ", np.shape(disks))
        print("Shape of convolution weight kernel tensor: ", np.shape(W_conv1))
        print("Shape after convolution of disk tensor and weight tensor: ", np.shape(c1))
        print("Shape of pool1 tensor: ", np.shape(h_pool1))

    # add 2nd layer
    W_conv2 = weight_variable([con_height, con_width, hidden1, hidden2])
    b_conv2 = bias_variable([hidden2])
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_flat(h_conv2)
    if verbose:
        print("Shape of W_conv2 tensor: ", np.shape(W_conv2))
        print("Shape of b_conv2 tensor: ", np.shape(b_conv2))
        print("Shape h_conv2 tensor: ", np.shape(h_conv2))
        print("Shape of  h_pool2 tensor: ", np.shape(h_pool2))
    # add dense layer
    s = np.shape(h_pool2)
    rsr = int(s[1])
    rsc = int(s[2])
    W_fc1 = weight_variable([rsr * rsc * hidden2, dense_layer])
    b_fc1 = bias_variable([dense_layer])
    h_pool2_flat = tf.reshape(h_pool2, [-1, rsr*rsc * hidden2])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
    # do dropout
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob_value)
    # do readout
    W_fc2 = weight_variable([dense_layer, num_classes])
    b_fc2 = bias_variable([num_classes])
    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
    return y_conv


def logits_nn(disks, hidden1_units, hidden2_units, disk_arr, num_classes):
    with tf.name_scope('hidden1'):
        weights = weight_variable([disk_arr, hidden1_units])
        biases = bias_variable([hidden1_units])
        hidden1 = tf.nn.relu(tf.matmul(disks, weights) + biases)

    with tf.name_scope('hidden2'):
        weights = weight_variable([hidden1_units, hidden2_units])
        biases = bias_variable([hidden2_units])
        hidden2 = tf.nn.relu(tf.matmul(hidden1, weights) + biases)

    with tf.name_scope('softmax_linear'):
        biases = bias_variable([num_classes])
        weights = weight_variable([hidden2_units, num_classes])
        logits = tf.matmul(hidden2, weights) + biases
    return logits


def softmax(logits):
        prob = tf.nn.softmax(logits=logits, name='prob')
        return prob


def loss_entropy(logits, labels):
        labels = tf.to_int64(labels)
        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels,
                                                                       logits=logits,
                                                                       name='cross_entropy')
        #cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=logits,  name='cross_entropy')
        return tf.reduce_mean(cross_entropy, name='cross_entropy_mean')


def evaluation(logits, labels):
    correct = tf.nn.in_top_k(logits, labels, 1)
    return tf.reduce_sum(tf.cast(correct, tf.int32))


def failure_evaluation(logits):
    vals, indices = tf.nn.top_k(logits, sorted=False)
    return vals, indices


def do_fail_thresh_eval(sess, fail_vals, fail_indices, disks_placeholder, labels_placeholder, data_set, batch_size,
                        run_name, model, keep_prob_pl=None, keep_prob_value=None, test=False):
    """
    Function will evaluate the precision and recall of model using softmax for estimation of probability
    The XX_batch variable holds an array of values from different probability thresholds
    The XX_batch[0] variable will hold the threshold value at thresh of 0, ie. the "default" precision/recall
    TP: number of failures correctly classified
    FN: number of failures marked incorrectly as nominal
    FP: number of nominal marked incorrectly as failure
    TN: number of nominal correctly marked as nominal
    """
    thresholds = np.arange(0.0, 1.0, .01)
    assert thresholds[0] == 0.0
    bins = len(thresholds)
    TP_batch = np.zeros(bins)
    TN_batch = np.zeros(bins)
    FP_batch = np.zeros(bins)
    FN_batch = np.zeros(bins)
    if test:
        ncpn = 0
        nwpn = 0
        ncpf = 0
        nwpf = 0

    steps_per_epoch = data_set.num_examples // batch_size
    for step in range(steps_per_epoch):
        if model == "nn":
            feed_dict = fill_feed_dict(data_set, disks_placeholder, labels_placeholder, batch_size)
        if model == "cnn":
            feed_dict = fill_feed_dict_cnn(data_set, disks_placeholder, labels_placeholder, batch_size,
                                           keep_prob_pl, keep_prob_value)

        f_indices = sess.run(fail_indices, feed_dict=feed_dict)
        f_vals = sess.run(fail_vals, feed_dict=feed_dict)
        f_labels = sess.run(labels_placeholder, feed_dict=feed_dict)
        f_indices = f_indices.reshape(batch_size, )
        TP = []
        FN = []
        TN = []
        FP = []

        if test:
            n_c_pred_nominal = [1 for l, pred in zip(f_labels, f_indices) if pred == 0 and l == 0]
            n_w_pred_nominal = [1 for l, pred in zip(f_labels, f_indices) if pred == 1 and l == 0]
            n_c_pred_fail = [1 for l, pred in zip(f_labels, f_indices) if pred == 1 and l == 1]
            n_w_pred_fail = [1 for l, pred in zip(f_labels, f_indices) if pred == 0 and l == 1]

            ncpn += np.sum(n_c_pred_nominal)
            nwpn += np.sum(n_w_pred_nominal)
            ncpf += np.sum(n_c_pred_fail)
            nwpf += np.sum(n_w_pred_fail)

        for tr in thresholds:
            n_c_pred_nom_thresh = [1 for l, pred, v in zip(f_labels, f_indices, f_vals) if
                                   pred == 0 and l == 0 and v[0] >= tr]
            TN.append(np.sum(n_c_pred_nom_thresh))
            n_w_pred_nom_thresh = [1 for l, pred, v in zip(f_labels, f_indices, f_vals) if
                                   pred == 1 and l == 0 and v[0] >= tr]
            FP.append(np.sum(n_w_pred_nom_thresh))

            n_c_pred_fail_thresh = [1 for l, pred, v in zip(f_labels, f_indices, f_vals) if
                                    pred == 1 and l == 1 and v[1] >= tr]
            TP.append(np.sum(n_c_pred_fail_thresh))
            n_w_pred_fail_thresh = [1 for l, pred, v in zip(f_labels, f_indices, f_vals) if
                                    pred == 0 and l == 1 and v[1] >= tr]
            FN.append(np.sum(n_w_pred_fail_thresh))

        TN_batch = [TN_batch[i] + TN[i] for i in range(bins)]
        TP_batch = [TP_batch[i] + TP[i] for i in range(bins)]
        FP_batch = [FP_batch[i] + FP[i] for i in range(bins)]
        FN_batch = [FN_batch[i] + FN[i] for i in range(bins)]

        if test:
            assert int(TN_batch[0]) == ncpn
            assert int(TP_batch[0]) == ncpf
            assert int(FP_batch[0]) == nwpn
            assert int(FN_batch[0]) == nwpf

    precision_thresholds = [TP_batch[i] / float(TP_batch[i] + FP_batch[i]) for i in range(bins)]
    recall_thresholds = [TP_batch[i] / float(TP_batch[i] + FN_batch[i]) for i in range(bins)]

    precision = TP_batch[0] / float(TP_batch[0] + FP_batch[0])
    recall = TP_batch[0] / float(TP_batch[0] + FN_batch[0])

    f = open(run_name + "/" + 'precision.csv', 'a')
    for i in range(bins):
        if i < bins-2:
            f.write(str(precision_thresholds[i]) + ",")
        else:
            f.write(str(precision_thresholds[i]))
    f.write("\n")
    f.close()

    f = open(run_name + "/" + 'recall.csv', 'a')
    for i in range(bins):
        if i < bins-2:
            f.write(str(recall_thresholds[i]) + ",")
        else:
            f.write(str(recall_thresholds[i]))
    f.write("\n")
    f.close()

    f = open(run_name + "/" + 'precision_recall.csv', 'a')
    f.write(str(precision) + "," + str(recall) + "\n")
    f.close()
    return precision, recall, TP_batch[0], FN_batch[0], TN_batch[0], FP_batch[0]


def clear_output(run_name, file_names=['precision.csv', 'recall.csv', 'precision_recall.csv']):
    for f_name in file_names:
        f = open(run_name + "/" + f_name, 'w')
        f.close()


def do_precision_recall_eval(sess, fail_indices, disks_placeholder, labels_placeholder, data_set, batch_size,  model,
                             keep_prob_pl=None,
                             keep_prob_value=None):
    """
    Calculates the precision and recall for one little batch of data
    """
    if model == "nn":
        feed_dict = fill_feed_dict(data_set, disks_placeholder, labels_placeholder, batch_size)
    if model == "cnn":
        feed_dict = fill_feed_dict_cnn(data_set, disks_placeholder, labels_placeholder, batch_size, keep_prob_pl,
                                       keep_prob_value)
    f_indices = sess.run(fail_indices, feed_dict=feed_dict)
    f_labels = sess.run(labels_placeholder, feed_dict=feed_dict)
    f_indices = f_indices.reshape(batch_size, )
    n_c_pred_nominal = [1 for l, pred in zip(f_labels, f_indices) if pred == 0 and l == 0]
    n_w_pred_nominal = [1 for l, pred in zip(f_labels, f_indices) if pred == 1 and l == 0]
    n_c_pred_fail = [1 for l, pred in zip(f_labels, f_indices) if pred == 1 and l == 1]
    n_w_pred_fail = [1 for l, pred in zip(f_labels, f_indices) if pred == 0 and l == 1]
    return np.sum(n_c_pred_nominal), np.sum(n_w_pred_nominal), np.sum(n_c_pred_fail), np.sum(n_w_pred_fail)


def do_eval(sess, eval_correct, disks_placeholder, labels_placeholder, data_set, batch_size, model, keep_prob_pl=None,
            keep_prob_value=None):
    """
    Counts the number of correct predictions for the total data set
    """
    true_count = 0
    steps_per_epoch = data_set.num_examples // batch_size
    num_examples = steps_per_epoch * batch_size
    for step in range(steps_per_epoch):
        if model == "nn":
            feed_dict = fill_feed_dict(data_set, disks_placeholder, labels_placeholder, batch_size)
        if model == "cnn":
            feed_dict = fill_feed_dict_cnn(data_set, disks_placeholder, labels_placeholder, batch_size, keep_prob_pl,
                                           keep_prob_value)
        true_count += sess.run(eval_correct, feed_dict=feed_dict)
    accuracy = float(true_count) / num_examples
    print('  Num examples: %d  Num correct: %d  Accuracy @ 1: %0.04f' % (num_examples, true_count, accuracy))


def fill_feed_dict(data_set, disk_pl, labels_pl, batch_size):
    """
    Makes feed dict for nn model
    """
    disk_feed, labels_feed = data_set.next_batch(batch_size)
    feed_dict = {
                disk_pl: disk_feed,
                labels_pl: labels_feed,
                }
    return feed_dict


def fill_feed_dict_cnn(data_set, disk_pl, labels_pl, batch_size, keep_prob_pl=None, keep_prob_value=None):
    """
    Makes feed dict for cnn model
    """
    disk_feed, labels_feed = data_set.next_batch(batch_size)
    feed_dict = {
                disk_pl: disk_feed,
                labels_pl: labels_feed,
                keep_prob_pl: keep_prob_value
                }
    return feed_dict


class DataSet(object):
    def __init__(self, disks, labels, dtype=dtypes.float32, reshape=True, scale=True):

        dtype = dtypes.as_dtype(dtype).base_dtype
        if dtype not in (dtypes.uint8, dtypes.float32):
            raise TypeError('Invalid image dtype %r, expected uint8 or float32' %
                            dtype)

        assert disks.shape[0] == labels.shape[0], (
            'disks.shape: %s labels.shape: %s' % (disks.shape, labels.shape))

        self._num_examples = disks.shape[0]

        if reshape:
            assert disks.shape[3] == 1
            disks = disks.reshape(disks.shape[0], disks.shape[1] * disks.shape[2])

        if scale:
            sc = StandardScaler()
            disks = sc.fit_transform(disks)

        self._disks = disks
        self._labels = labels
        self._epochs_completed = 0
        self._index_in_epoch = 0

    @property
    def disks(self):
        return self._disks

    @property
    def labels(self):
        return self._labels

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size, shuffle=True):
        start = self._index_in_epoch
        
        if self._epochs_completed == 0 and start == 0 and shuffle:
            perm0 = np.arange(self._num_examples)
            np.random.shuffle(perm0)
            self._disks = self.disks[perm0]
            self._labels = self.labels[perm0]
        if start + batch_size > self._num_examples:
            self._epochs_completed += 1
            rest_num_examples = self._num_examples - start
            disks_rest_part = self._disks[start:self._num_examples]
            labels_rest_part = self._labels[start:self._num_examples]
            if shuffle:
                perm = np.arange(self._num_examples)
                np.random.shuffle(perm)
                self._disks = self.disks[perm]
                self._labels = self.labels[perm]
            start = 0
            self._index_in_epoch = batch_size - rest_num_examples
            end = self._index_in_epoch
            disks_new_part = self._disks[start:end]
            labels_new_part = self._labels[start:end]
            return np.concatenate((disks_rest_part, disks_new_part), axis=0), np.concatenate(
                (labels_rest_part, labels_new_part), axis=0)
        else:
            self._index_in_epoch += batch_size
            end = self._index_in_epoch
            return self._disks[start:end], self._labels[start:end]


def dense_to_one_hot(labels_dense, num_classes):
    num_labels = labels_dense.shape[0]
    index_offset = np.arange(num_labels) * num_classes
    labels_one_hot = np.zeros((num_labels, num_classes))
    labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
    return labels_one_hot


def load_hd_data(data_dir, train_file, train_label_file, dtype=dtypes.float32, reshape=True,
                 validation_fraction=1.0/7.0,
                 one_hot=False,
                 clip_days=None):
    """
    load the data in the expected format from .npy files
    """
    train_data = np.load(data_dir + train_file)
    if clip_days:
        train_data = np.asarray([c[clip_days[0]:clip_days[1]] for c in train_data])
    s = np.shape(train_data)
    train_data = train_data.reshape(s[0], s[1], s[2], 1)
    train_labels = np.load(data_dir + train_label_file)
    num_classes = len(np.unique(train_labels))

    if one_hot:
        train_labels = dense_to_one_hot(train_labels, num_classes)

    validation_size = int(len(train_data) * validation_fraction)
    validation_disks = train_data[:validation_size]
    validation_labels = train_labels[:validation_size]
    train_data = train_data[validation_size:]
    train_labels = train_labels[validation_size:]
    num_features = np.shape(train_data)[2]
    num_days = np.shape(train_data)[1]

    train = DataSet(train_data, train_labels, dtype=dtype, reshape=reshape, scale=True)
    validation = DataSet(validation_disks, validation_labels, dtype=dtype, reshape=reshape, scale=True)

    return base.Datasets(train=train, validation=validation, test=None),  num_classes, num_features, num_days
