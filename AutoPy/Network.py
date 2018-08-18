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
        input_layer = features
        #bn = tf.layers.batch_normalization(input_layer)
        lstm = tf.contrib.rnn.BasicLSTMCell(30)
        cell = tf.contrib.rnn.MultiRNNCell([lstm, ])
        init_State = cell.zero_state(tf.shape(input_layer)[0], tf.float32)
        lstmOut, state = tf.nn.dynamic_rnn(cell,input_layer,dtype = tf.float32)
        dense2 = tf.layers.dense(inputs = lstmOut, units = 50, activation = tf.nn.relu)
        dropout2 = tf.layers.dropout(inputs= dense2, rate = 0.2, training = mode == tf.estimator.ModeKeys.TRAIN )
        #print("train")
        #print(tf.estimator.ModeKeys.TRAIN)
        logits = tf.layers.dense(inputs = dropout2 , units = 50)
        return logits

    def convertData(self,inputs, rewards):
        inputData = tf.data.Dataset.from_tensors(inputs)
        rewardData = tf.data.Dataset.from_tensors(rewards)
        self.data = tf.data.Dataset.zip(inputData, rewardData)

    def initializeVars(self, sess):
        sess.run(tf.global_variables_initializer())
    def defineFeedForward(self):
        ff = self.model_fn()
    def feedForward(self,inputs):
        inputData = tf.expand_dims( inputs, axis = 0) 
        
        output = self.model_fn(inputData, mode = tf.estimator.ModeKeys.PREDICT)
        return output
        
        
        


