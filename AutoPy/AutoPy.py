from Global import *
import multiprocessing as mp
from collections import defaultdict
import math, sys, random
from Int import Int
import time
from Network import Network as nw
import tensorflow as tf
import numpy as np
from Context import Context
import Sim
def SimFnWrapper(network,pipe):
    SimFn(network,pipe)

if __name__ == "__main__":
    simProcs = []
    simPipes = []
    
    
    network = nw()
    placeholder = tf.placeholder(tf.float32, [None,INPUT_SIZE])
    feedForward = network.feedForward(placeholder)
    
    for i in range(NUM_SIMS):
        simPipes.append(mp.Pipe())
        simProcs.append(mp.Process(target = Sim.SimFn, name = SIM_PROC_NAME, args = [network,simPipes[i][1]], daemon = False))
        simProcs[i].start()
    for j in range(NUM_GAMES):
        data = [],[],[],[] #[inputs, actions, rewards, logits][data]
        for i in range(NUM_SIMS):
            simPipes[i][0].send(True)
        print("done sending")
        for i in range(NUM_SIMS):
            print("starting receipt")
            datum = simPipes[i][0].recv()
            data[0].extend(datum[0])
            data[1].extend(datum[1])
            data[2].extend(datum[2])
            data[3].extend(datum[3])
        print("done simulating games")
        #tensor = tf.convert_to_tensor(arr)
        print(np.shape(data[0]))
        input = tf.convert_to_tensor(data[0])
        action = tf.convert_to_tensor(data[1],dtype = tf.int32)
        reward = tf.convert_to_tensor(data[2])
        gameLogits = tf.convert_to_tensor(data[3])
        reward = tf.expand_dims(reward, -1)

        dataSet = tf.data.Dataset.from_tensor_slices({"input" : input,
                                                         "action" : action, 
                                                         "reward" : reward,
                                                         "logit" : gameLogits})
        dataSet.batch(BATCH_SIZE)
        iterator = tf.data.Iterator.from_structure(dataSet.output_types,dataSet.output_shapes)
        next_element = iterator.get_next()
        training_init_op = iterator.make_initializer(dataSet)
        Logits = network.model_fn(next_element["input"],mode = tf.estimator.ModeKeys.TRAIN)
        #loss = network.loss(next_element["action"], next_element["logit"], next_element["reward"])
        labels = tf.reshape(tf.one_hot(tf.slice(next_element["action"], [0],[1]),MVMT_TYPE_SIZE),[MVMT_TYPE_SIZE])
        labels = tf.concat([labels, tf.reshape(tf.one_hot(tf.slice(next_element["action"], [1],[1]),len(RET_NAMES),),[len(RET_NAMES)])],-1)
        labels = tf.concat([labels, tf.reshape(tf.one_hot(tf.slice(next_element["action"], [2], [1]),OUTPUT_SIZE - (MVMT_TYPE_SIZE + 1) ),[OUTPUT_SIZE - (MVMT_TYPE_SIZE+1)])],-1)
        labels = labels * next_element["reward"]
        #labels = network.getLabels(next_element["action"])
        loss = tf.nn.sigmoid_cross_entropy_with_logits( labels = labels,logits = Logits)
        totalLoss = tf.reduce_sum(loss)
        with tf.variable_scope('rms', reuse = tf.AUTO_REUSE):
            optimizer = tf.train.RMSPropOptimizer(0.001,).minimize(totalLoss) 
        init_op = tf.global_variables_initializer()
        epochs = 101 
        counter = 0
        with tf.Session() as sess:
            sess.run(init_op)
            sess.run(training_init_op)
            for i in range(epochs):
                try:
                    l = sess.run(totalLoss)
                    sess.run(optimizer)
                    counter += 1
                    #if i % 50 == 0:
                    print("Epoch: {}, loss: {:.3f}%".format(i,l))
                except tf.errors.OutOfRangeError as o:
                    sess.run(training_init_op)
                    print(counter)
    # do training here pls
    for i in range(NUM_SIMS):
        simProcs[i].join()


    #NOTES:
    #test
    #better to undestimate visual field bc convnet can mislabel at edges
    #TODO:
    #toss sessions around
    #account for case where pickupindex == -1 and/or dropoffindex == -1