from Global import *
import tensorflow as tf
import numpy as np

"""neural network to find best policy"""
# neural net params
DISCOUNT = 0.999
SAVE_PATH = "/checkpoints/model.ckpt"
def model_fn(features,mode):
   
    input_layer = features #tf.split(features, [SEQ_LEN],1)
    lstm = tf.nn.rnn_cell.LSTMCell(100,activation = tf.nn.leaky_relu,reuse = tf.AUTO_REUSE)
    dense2 = tf.layers.dense(inputs = input_layer[:,-1], units = 100, activation = tf.nn.leaky_relu, kernel_initializer = tf.initializers.glorot_normal())
    dropOut = tf.layers.dropout(inputs = dense2, rate = 0.25, training = mode == tf.estimator.ModeKeys.TRAIN)
    dense3 = tf.layers.dense(inputs = dropOut, units = 100, activation = tf.nn.leaky_relu, kernel_initializer = tf.initializers.glorot_normal())
    output = tf.layers.dense(inputs = dense3, units = OUTPUT_SIZE, activation = tf.identity, kernel_regularizer = tf.contrib.layers.l2_regularizer(0.01), kernel_initializer = tf.initializers.glorot_normal())
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
dataSet = dataSet.shuffle(2500000)
dataSet = dataSet.batch(BATCH_SIZE)
iterator = tf.data.Iterator.from_structure(dataSet.output_types,dataSet.output_shapes)
next_element = iterator.get_next()
training_init_op = iterator.make_initializer(dataSet)
avg = tf.reduce_mean(next_element["reward"])
Logits = model_fn(next_element["input"], mode = tf.estimator.ModeKeys.TRAIN)
probs = Logits

labels = tf.one_hot(next_element["action"],OUTPUT_SIZE)
labels = tf.reshape(labels,shape = [-1, OUTPUT_SIZE])
loss = tf.losses.mean_squared_error((next_element["reward"]-avg) * labels + Logits, Logits)
totalLoss = loss 
tf.summary.histogram("loss", totalLoss)
optimizer = tf.train.RMSPropOptimizer(0.0001,).minimize(totalLoss) 
init_op = tf.global_variables_initializer()
saver = tf.train.Saver()
writer = tf.summary.FileWriter("/logs/1/train", sess.graph)
merge = tf.summary.merge_all()
if RESTORE_MODEL:
    saver.restore(sess, SAVE_PATH)
else:
    sess.run(init_op)
        
        


