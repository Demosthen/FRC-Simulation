
if __name__ == "__main__":
    from Global import *
    import multiprocessing as mp
    from collections import defaultdict
    import math, sys, random
    from Int import Int
    import time
    import Network as nw
    import tensorflow as tf
    import numpy as np
    from Context import Context
    import Sim
    simProcs = []
    simPipes = []
    for i in range(NUM_SIMS):
        simPipes.append(mp.Pipe())
        simProcs.append(mp.Process(target = Sim.SimFn, name = SIM_PROC_NAME, args = [simPipes[i][1]], daemon = False))
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
        
        epochs = 201
        counter = 0
        # run stuff
        nw.sess.run(nw.training_init_op,feed_dict = {nw.inputHolder : data[0],
                                                     nw.actionHolder : data[1],
                                                     nw.rewardHolder : data[2]})

        for i in range(epochs):
            try:
                l = nw.sess.run(nw.totalLoss)
                nw.sess.run(nw.optimizer)
                counter += 1
                if i % 25 == 0:
                    print("Epoch: {}, loss: {:.3f}".format(i,l))
            except tf.errors.OutOfRangeError as o:
                nw.sess.run(nw.training_init_op)
                print(counter)
        save_path = nw.saver.save(nw.sess, nw.SAVE_PATH)
        print("Done saving at "+str(save_path))
    # do training here pls
    for i in range(NUM_SIMS):
        simProcs[i].join()
    nw.sess.close()

    #NOTES:
    #test
    #better to undestimate visual field bc convnet can mislabel at edges
    #TODO:
    #account for case where pickupindex == -1 and/or dropoffindex == -1
    #softmax all 50 outputs
    #vault scoring
    #train (hopefully)