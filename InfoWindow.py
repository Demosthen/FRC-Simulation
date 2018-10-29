from tkinter import *
from Global import *
def run(Pipe):
    #shows what each bot is doing
    root = Tk()
    root.title("Info Window")
    botText = Text(root)
    botText.pack()
    pipe = Pipe
    for i in range(NUM_BOTS):
        botText.insert(END,"Bot: "+ str(i) + " Action: \n")
    while True:
    #def getInfo(event):
        actions = pipe.recv()
        botText.delete('1.0', END)
        for i in range(NUM_BOTS):
            botText.insert(str(i)+'.0', "Bot: "+ str(i) + " Action: " + actions[i]+"\n")
        root.update()
    #root.bind("<<Update>>", getInfo)
    