from Global import *
import tensorflow as tf
import numpy as np
class Network(object):
    """neural network to find best policy"""
    # neural net params
    DISCOUNT = 0.99
    alpha = 0.999
    beta = 0.9
    learnRate = 0.01
    inputLayerSize = 0
    def __init__(self):
        print("initNet")

    #def __del__(self):
        #self.sess.close()

    def model_fn(self, features, mode):
        # put in multirnncells and figure out how to train them
        # randomly sample from experience buffer as input
        #input_layer = tf.reshape(features, [-1,SEQ_LEN,50])
        #bn = tf.layers.batch_normalization(input_layer)
        input_layer = tf.split(features,SEQ_LEN)
        lstm = tf.contrib.rnn.BasicLSTMCell(50,activation = tf.tanh,reuse = tf.AUTO_REUSE)
        #cell = tf.contrib.rnn.MultiRNNCell([lstm, ])
        #init_State = cell.zero_state(BATCH_SIZE, tf.float32)
        lstmOut, state = tf.nn.static_rnn(lstm,input_layer,dtype = tf.float32)
        dense2 = tf.layers.dense(inputs = lstmOut[-1], units = 50, activation = tf.nn.sigmoid)
        #dropout2 = tf.layers.dropout(inputs= dense2, rate = 0.2, training = mode == tf.estimator.ModeKeys.TRAIN )
        #logits = tf.layers.dense(inputs = dropout2 , units = OUTPUT_SIZE)
        return dense2

    def convertData(self,inputs, rewards):
        inputData = tf.data.Dataset.from_tensors(inputs)
        rewardData = tf.data.Dataset.from_tensors(rewards)
        self.data = tf.data.Dataset.zip(inputData, rewardData)

    def initializeVars(self, sess):
        sess.run(tf.global_variables_initializer())

    def loss(self, labels, logits, rewards):
        actions = tf.reshape(tf.one_hot(tf.slice(labels, [0],[1]),MVMT_TYPE_SIZE),[MVMT_TYPE_SIZE])
        actions = tf.concat([actions, tf.reshape(tf.one_hot(tf.slice(labels, [1],[1]),len(RET_NAMES),),[len(RET_NAMES)])],-1)
        actions = tf.concat([actions, tf.reshape(tf.one_hot(tf.slice(labels, [2], [1]),OUTPUT_SIZE - (MVMT_TYPE_SIZE + 1) ),[OUTPUT_SIZE - (MVMT_TYPE_SIZE+1)])],-1)
        
        crossEntropy = tf.nn.softmax_cross_entropy_with_logits_v2(labels = actions, logits = logits)
        return crossEntropy * rewards;
    def getLabels(self, labels):
        actions = tf.reshape(tf.one_hot(tf.slice(labels, [0],[1]),MVMT_TYPE_SIZE),[MVMT_TYPE_SIZE])
        actions = tf.concat([actions, tf.reshape(tf.one_hot(tf.slice(labels, [1],[1]),len(RET_NAMES),),[len(RET_NAMES)])],-1)
        actions = tf.concat([actions, tf.reshape(tf.one_hot(tf.slice(labels, [2], [1]),OUTPUT_SIZE - (MVMT_TYPE_SIZE + 1) ),[OUTPUT_SIZE - (MVMT_TYPE_SIZE+1)])],-1)
    def defineFeedForward(self):
        ff = self.model_fn()

    def feedForward(self,inputs):
        inputData = inputs
        output = self.model_fn(inputData, mode = tf.estimator.ModeKeys.PREDICT)
        return output
        
        
        


