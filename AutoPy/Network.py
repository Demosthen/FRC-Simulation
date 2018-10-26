from Global import *
import tensorflow as tf
import numpy as np

"""neural network to find best policy"""
# neural net params
DISCOUNT = 0.99
SAVE_PATH = "/checkpoints/model.ckpt"
def model_fn(features,mode):
    
    # put in multirnncells and figure out how to train them
    # randomly sample from experience buffer as input
    #input_layer = tf.reshape(features, [BATCH_SIZE,SEQ_LEN,50])
    #bn = tf.layers.batch_normalization(input_layer)
    input_layer = features #tf.split(features, [SEQ_LEN],1)
    lstm = tf.nn.rnn_cell.LSTMCell(100,activation = tf.nn.leaky_relu,reuse = tf.AUTO_REUSE)
    #cell = tf.contrib.rnn.MultiRNNCell([lstm, ])
    #init_State = cell.zero_state(BATCH_SIZE, tf.float32)
    #lstmOut, state = tf.nn.static_rnn(lstm,input_layer,dtype = tf.float32,sequence_length = tf.placeholder(tf.int32,[None]))
    #lstmOut, state = tf.nn.dynamic_rnn(lstm,input_layer, dtype = tf.float32)
    #dense2 = tf.layers.dense(inputs = lstmOut[:, -1], units = 200, activation = tf.nn.leaky_relu)
    dense2 = tf.layers.dense(inputs = input_layer[:,-1], units = 100, activation = tf.nn.leaky_relu)
    dropOut = tf.layers.dropout(inputs = dense2, rate = 0.25, training = mode == tf.estimator.ModeKeys.TRAIN)
    dense3 = tf.layers.dense(inputs = dropOut, units = 100, activation = tf.nn.leaky_relu)
    output = tf.layers.dense(inputs = dense3, units = OUTPUT_SIZE, activation = tf.identity)
    tf.summary.histogram("output", output)
    return output
def normalize(data):
    mean, std = tf.nn.moments(data,[-1])
    std = tf.sqrt(std)
    data = tf.divide( tf.subtract(data,mean),std)
    return data
#tensorflow op definitions


sess = tf.Session()

inputHolder = tf.placeholder(tf.float32, [None, SEQ_LEN, INPUT_SIZE])
actionHolder = tf.placeholder(tf.int32, [None])
rewardHolder = tf.placeholder(tf.float32)
nextInputHolder = tf.placeholder(tf.float32, [None, SEQ_LEN, INPUT_SIZE])
input = tf.convert_to_tensor(inputHolder)
action = tf.convert_to_tensor(actionHolder, dtype = tf.int32)
#action = tf.expand_dims(action,0)
reward = tf.convert_to_tensor(rewardHolder)
reward = tf.expand_dims(reward, -1)

dataSet = tf.data.Dataset.from_tensor_slices({"input" : input,
                                                    "action" : action, 
                                                    "reward" : reward,})
dataSet = dataSet.shuffle(2500000, reshuffle_each_iteration = True)
dataSet = dataSet.batch(BATCH_SIZE)
iterator = tf.data.Iterator.from_structure(dataSet.output_types,dataSet.output_shapes)
next_element = iterator.get_next()
training_init_op = iterator.make_initializer(dataSet)
avg = tf.reduce_mean(next_element["reward"])
#Logits = model_fn(next_element["input"],mode = tf.estimator.ModeKeys.TRAIN)
Logits = model_fn(next_element["input"], mode = tf.estimator.ModeKeys.TRAIN)
probs = tf.nn.softmax(Logits)

labels = tf.one_hot(next_element["action"],OUTPUT_SIZE)
labels = tf.reshape(labels,shape = [-1, OUTPUT_SIZE])
#loss = tf.losses.softmax_cross_entropy(labels ,Logits) 
loss = tf.reduce_sum(probs * labels)
loss = -tf.log(loss + CORRECTION)
#grad = tf.gradients(next_element["reward"] * tf.log(Logits), labels)
totalLoss = loss * (next_element["reward"])#tf.multiply(tf.reduce_sum(loss),tf.maximum( next_element["reward"],tf.multiply(next_element["reward"],0.1)))
tf.summary.histogram("loss", totalLoss)
#with tf.variable_scope('rms', reuse = tf.AUTO_REUSE):
optimizer = tf.train.AdamOptimizer().minimize(totalLoss)#tf.train.RMSPropOptimizer(0.0001,).minimize(totalLoss) 
init_op = tf.global_variables_initializer()
saver = tf.train.Saver()
writer = tf.summary.FileWriter("/logs/1/train", sess.graph)
if RESTORE_MODEL:
    saver.restore(sess, SAVE_PATH)
else:
    sess.run(init_op)
        
        


