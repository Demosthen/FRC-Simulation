from Global import *
import tensorflow as tf
import numpy as np

"""neural network to find best policy"""
# neural net params
DISCOUNT = 0.999
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
    dense2 = tf.layers.dense(inputs = input_layer[:,-1], units = 100, activation = tf.nn.leaky_relu, kernel_initializer = tf.initializers.glorot_normal())
    dense3 = tf.layers.dense(inputs = dense2, units = 100, activation = tf.nn.leaky_relu, kernel_initializer = tf.initializers.glorot_normal())
    dense4 = tf.layers.dense(inputs = dense3, units = 100, activation = tf.nn.leaky_relu, kernel_initializer = tf.initializers.glorot_normal())
    dense5 = tf.layers.dense(inputs = dense4, units = 100, activation = tf.nn.leaky_relu, kernel_initializer = tf.initializers.glorot_normal())
    output = tf.layers.dense(inputs = dense5, units = OUTPUT_SIZE, activation = tf.identity, kernel_regularizer = tf.contrib.layers.l2_regularizer(0.01), kernel_initializer = tf.initializers.glorot_normal())
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
#Logits = model_fn(next_element["input"],mode = tf.estimator.ModeKeys.TRAIN)
Logits = model_fn(next_element["input"], mode = tf.estimator.ModeKeys.TRAIN)
probs = Logits
min = tf.reduce_min(Logits)
normalized = tf.div(Logits-min,tf.subtract(tf.reduce_max(Logits),min))
labels = tf.one_hot(next_element["action"],OUTPUT_SIZE)
labels = tf.reshape(labels,shape = [-1, OUTPUT_SIZE])
loss = tf.losses.log_loss(labels, tf.nn.softmax(Logits)) * next_element["reward"]#tf.losses.sigmoid_cross_entropy(labels * next_element["reward"],Logits)#-tf.losses.softmax_cross_entropy(labels,normalized + 0.01) * next_element["reward"]
#loss = -tf.reduce_sum(tf.log(normalized * next_element["reward"]) * labels)#tf.losses.mean_squared_error((next_element["reward"]-avg) * labels + Logits, Logits)
#mask = loss == 0
#loss = -tf.log(tf.where(mask, x = loss, y = CORRECTION))
#grad = tf.gradients(next_element["reward"] * tf.log(Logits), labels)
totalLoss = loss #tf.multiply(tf.reduce_sum(loss),tf.maximum( next_element["reward"],tf.multiply(next_element["reward"],0.1)))
tf.summary.histogram("loss", totalLoss)
#with tf.variable_scope('rms', reuse = tf.AUTO_REUSE):
optimizer = tf.train.RMSPropOptimizer(0.0001,).minimize(totalLoss) 
init_op = tf.global_variables_initializer()
saver = tf.train.Saver()
writer = tf.summary.FileWriter("/logs/1/train", sess.graph)
merge = tf.summary.merge_all()
if RESTORE_MODEL:
    saver.restore(sess, SAVE_PATH)
else:
    sess.run(init_op)
        
        


