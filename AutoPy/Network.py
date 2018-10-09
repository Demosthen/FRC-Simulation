from Global import *
import tensorflow as tf
import numpy as np

"""neural network to find best policy"""
# neural net params
DISCOUNT = 0.99
SAVE_PATH = "/checkpoints/model.ckpt"
def model_fn(features, mode):
    # put in multirnncells and figure out how to train them
    # randomly sample from experience buffer as input
    #input_layer = tf.reshape(features, [-1,SEQ_LEN,50])
    #bn = tf.layers.batch_normalization(input_layer)
    input_layer = tf.split(features,SEQ_LEN)
    lstm = tf.nn.rnn_cell.LSTMCell(100,activation = tf.nn.leaky_relu,reuse = tf.AUTO_REUSE)
    #cell = tf.contrib.rnn.MultiRNNCell([lstm, ])
    #init_State = cell.zero_state(BATCH_SIZE, tf.float32)
    lstmOut, state = tf.nn.static_rnn(lstm,input_layer,dtype = tf.float32)
    dense2 = tf.layers.dense(inputs = lstmOut[-1], units = 200, activation = tf.nn.leaky_relu)
    dropOut = tf.layers.dropout(inputs = dense2, rate = 0.6, training = mode == tf.estimator.ModeKeys.TRAIN)
    output = tf.layers.dense(inputs = dense2, units = 50, activation = tf.nn.sigmoid)
    #dropout2 = tf.layers.dropout(inputs= dense2, rate = 0.2, training = mode == tf.estimator.ModeKeys.TRAIN )
    #logits = tf.layers.dense(inputs = dropout2 , units = OUTPUT_SIZE)
    return output

#tensorflow op definitions
feedHolder = tf.placeholder(tf.float32, [None,INPUT_SIZE])
feedForward = model_fn(feedHolder,mode = tf.estimator.ModeKeys.PREDICT)

sess = tf.Session()

inputHolder = tf.placeholder(tf.float32, [None, None, INPUT_SIZE])
actionHolder = tf.placeholder(tf.int32, [None, MVMT_TYPE_SIZE+2])
rewardHolder = tf.placeholder(tf.float32)

input = tf.convert_to_tensor(inputHolder)
action = tf.convert_to_tensor(actionHolder, dtype = tf.int32)
reward = tf.convert_to_tensor(rewardHolder)
reward = tf.expand_dims(reward, -1)

dataSet = tf.data.Dataset.from_tensor_slices({"input" : input,
                                                    "action" : action, 
                                                    "reward" : reward,})
dataSet.batch(BATCH_SIZE)
dataSet.shuffle(5000)
iterator = tf.data.Iterator.from_structure(dataSet.output_types,dataSet.output_shapes)
next_element = iterator.get_next()
training_init_op = iterator.make_initializer(dataSet)
Logits = model_fn(next_element["input"],mode = tf.estimator.ModeKeys.TRAIN)
#loss = network.loss(next_element["action"], next_element["logit"], next_element["reward"])
labels = tf.reshape(tf.one_hot(tf.slice(next_element["action"], [0],[1]),MVMT_TYPE_SIZE),[MVMT_TYPE_SIZE])
labels = tf.concat([labels, tf.reshape(tf.one_hot(tf.slice(next_element["action"], [1],[1]),len(RET_NAMES),),[len(RET_NAMES)])],-1)
labels = tf.concat([labels, tf.reshape(tf.one_hot(tf.slice(next_element["action"], [2], [1]),OUTPUT_SIZE - (MVMT_TYPE_SIZE + 1) ),[OUTPUT_SIZE - (MVMT_TYPE_SIZE+1)])],-1)
labels = labels * next_element["reward"]
#labels = network.getLabels(next_element["action"])
loss = tf.losses.mean_squared_error(labels = labels, predictions = Logits)
totalLoss = tf.reduce_sum(loss)
with tf.variable_scope('rms', reuse = tf.AUTO_REUSE):
    optimizer = tf.train.RMSPropOptimizer(0.001,).minimize(totalLoss) 
init_op = tf.global_variables_initializer()
saver = tf.train.Saver()
if RESTORE_MODEL:
    saver.restore(sess, SAVE_PATH)
else:
    sess.run(init_op)
        
        


