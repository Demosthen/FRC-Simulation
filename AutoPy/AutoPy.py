
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
    for j in range(NUM_GAMES-START):
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
        
        epochs = 1001
        counter = 0
        # run stuff
        nw.sess.run(nw.training_init_op,feed_dict = {nw.inputHolder : data[0],
                                                     nw.actionHolder : data[1],
                                                     nw.rewardHolder : data[2],
                                                     })
        #i = 0
        for i in range(epochs):
        #while True:
            try:
                l = nw.sess.run(nw.totalLoss)
                nw.sess.run(nw.optimizer)
                counter += 1
                summary = nw.sess.run(nw.merge)
                nw.writer.add_summary(summary,i)
                if i % 25 == 0:
                    print("Epoch: {}, loss: {}".format(i,str(np.average(l))))
            except tf.errors.OutOfRangeError as o:
                #nw.sess.run(nw.training_init_op)
                break
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
    #some training done already, should evaluate w/ DRAW
    #try new conda package version of tensorflow