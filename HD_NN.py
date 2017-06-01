import time
import tensorflow as tf
import os
import HD_TF_Model


def main():
    if tf.gfile.Exists(LOG_DIR) and CLEAR_LOGS:
        tf.gfile.DeleteRecursively(LOG_DIR)

    if tf.gfile.Exists(RUN_NAME):
        HD_TF_Model.clear_output(RUN_NAME)
    else:
        os.mkdir(RUN_NAME)
    log_dir = LOG_DIR + "/" + RUN_NAME
    tf.gfile.MakeDirs(log_dir)

    data_set, num_classes, num_features, num_days = HD_TF_Model.load_hd_data(DATA_DIR,
                                                                             TRAIN_FILE,
                                                                             TRAIN_LABEL_FILE,
                                                                             one_hot=False,
                                                                             clip_days=CLIP_DAYS)
    disk_arr = num_features * num_days

    with tf.Graph().as_default():
        data_placeholder = tf.placeholder(tf.float32, shape=(BATCH_SIZE, disk_arr))
        labels_placeholder = tf.placeholder(tf.int32, shape=BATCH_SIZE)

        if MODEL == "nn":
            logits = HD_TF_Model.logits_nn(data_placeholder, HIDDEN1, HIDDEN2, disk_arr, num_classes)
            loss = HD_TF_Model.loss_entropy(logits, labels_placeholder)
            kwargs = {'keep_prob_pl': None, 'keep_prob_value': None}

        if MODEL == "cnn":
            keep_prob_placeholder = tf.placeholder(tf.float32)
            logits = HD_TF_Model.cnn(data_placeholder, num_features, num_days, num_classes, keep_prob_placeholder)
            loss = HD_TF_Model.loss_entropy(logits, labels_placeholder)
            kwargs = {'keep_prob_pl': keep_prob_placeholder, 'keep_prob_value': KEEP_PROB}

        tf.summary.scalar('loss', loss)
        softmax = HD_TF_Model.softmax(logits)

        #optimizer = tf.train.GradientDescentOptimizer(INIT_LEARNING_RATE)
        optimizer = tf.train.AdamOptimizer(INIT_LEARNING_RATE)
        global_step = tf.Variable(0, name='global_step', trainable=False)
        train_op = optimizer.minimize(loss, global_step=global_step)

        eval_correct = HD_TF_Model.evaluation(logits, labels_placeholder)
        tf.summary.scalar("precision", eval_correct/BATCH_SIZE)

        vals, indices = HD_TF_Model.failure_evaluation(logits)
        summary = tf.summary.merge_all()
        init = tf.global_variables_initializer()
        saver = tf.train.Saver()
        sess = tf.Session()
        summary_writer = tf.summary.FileWriter(log_dir, sess.graph)
        sess.run(init)

        total_time = time.time()
        for step in range(MAX_STEPS):
            start_time = time.time()
            if MODEL == "nn":
                feed_dict = HD_TF_Model.fill_feed_dict(data_set.train, data_placeholder, labels_placeholder, BATCH_SIZE)
            if MODEL == "cnn":
                feed_dict = HD_TF_Model.fill_feed_dict_cnn(data_set.train,
                                                           data_placeholder,
                                                           labels_placeholder,
                                                           BATCH_SIZE,
                                                           **kwargs)

            _, loss_value = sess.run([train_op, loss], feed_dict=feed_dict)

            if step % 50 == 0:
                duration = time.time() - start_time
                total_duration = time.time() - total_time
                print('Step %d: loss = %.2f (n step time: %.3f sec, total time: %.1f sec)' %
                      (step, loss_value, duration, total_duration))
                TN, FP, TP, FN = HD_TF_Model.do_precision_recall_eval(sess,
                                                                      indices,
                                                                      data_placeholder,
                                                                      labels_placeholder,
                                                                      data_set.validation,
                                                                      BATCH_SIZE,
                                                                      MODEL,
                                                                      **kwargs)
                print("TP: ", TP, "\tFN: ", FN, "\tTN: ", TN, "\tFP: ",  FP)
                print("Precision: ", TP/float(TP+FP), "Recall: ", TP/float(TP+FN))
                summary_str = sess.run(summary, feed_dict=feed_dict)
                summary_writer.add_summary(summary_str, step)
                summary_writer.flush()

            if step % 100 == 0 or step == MAX_STEPS:
                checkpoint_file = os.path.join(log_dir, 'model.ckpt')
                saver.save(sess, checkpoint_file, global_step=step)
                print('Validation Data Evaluation:')
                HD_TF_Model.do_eval(sess, eval_correct, data_placeholder, labels_placeholder,
                                    data_set.validation, BATCH_SIZE, MODEL, **kwargs)
                precision, recall, TP, FN, TN, FP = HD_TF_Model.do_fail_thresh_eval(sess,
                                                                                    softmax,
                                                                                    indices,
                                                                                    data_placeholder,
                                                                                    labels_placeholder,
                                                                                    data_set.validation,
                                                                                    BATCH_SIZE,
                                                                                    RUN_NAME,
                                                                                    MODEL,
                                                                                    **kwargs)

                print("\tPrecision: ", precision, "\n",
                      "\tRecall: ", recall)
                print("\tTrue Positive: ", TP, "\n",
                      "\tFalse Negative: ", FN, "\n",
                      "\tTrue Negative: ", TN, "\n",
                      "\tFalse Positive: ", FP)

if __name__ == '__main__':
    """
    VERBOSE True prints out lots of details
    LOG_DIR is the tensorboard and checkpoint logging directory
    RUN_NAME is the name of the run in tensorboard and the name of the local data dir to be created
    DATA_DIR is where the data is located
    TRAIN_FILE is the input data file
    CLIP_DAYS is the days to grab from the input TRAIN_FILE, note that the day of failure is number of days
    MODEL is the model type, it can be "cnn" or "nn"
    CLEAR_LOGS True deletes the LOG_DIR to start a clean tensorboard logging
    KEEP_PROB is the dropout probability that is only used with cnn
    """
    VERBOSE = True
    LOG_DIR = '/tmp/tensorflow/logs/hd_failure'
    RUN_NAME = 'r_d30_d0_660_256'
    DATA_DIR = '/home/alex/data_projects/disk_analysis/data/'
    TRAIN_FILE = 'train_d60.npy'
    TRAIN_LABEL_FILE = 'label_d60.npy'
    INIT_LEARNING_RATE = .01
    CLIP_DAYS = [50, 55]
    HIDDEN1 = 48
    HIDDEN2 = 48
    BATCH_SIZE = 128
    MAX_STEPS = 1000000
    CLEAR_LOGS = True
    MODEL = "cnn"
    KEEP_PROB = 0.75
    main()
