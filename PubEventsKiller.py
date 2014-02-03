from SubspaceBot import *
from BotUtilities import *
import TimerManager

class Bot(BotInterface):
    def __init__(self,ssbot,md):
        ssbot.registerModuleInfo(__name__,"pubeventskiller","The Junky","pubeventsk",".01")
        self.botname2kill = "Bot-EG-Pubvents"
        self.answered = True
        self.tm = TimerManager.TimerManager()
        self.tm.set(10,1)
        self.bots_to_check= {
                             "Bot-EG-Pubvents":True,
                             
                             }
                             
                             
        pass
    def HandleEvents(self,ssbot,event):
        if event.type == EVENT_TICK:
            timer_expired = self.tm.getExpired()
            if timer_expired:
                if timer_expired.data == 1: #timer_expired is now the data we passed to timer
                            for bname, answered in self.killable_bots.iteritems():
                                p = ssbot.findPlayerByName(bname)
                                if p:
                                    if answered == True:
                                        ssbot.sendPrivateMessage(p,"!wtf")
                                        self.bots_to_check[event.pname] = False
                                    else:
                                        ssbot.sendPrivateMessage(p,"*kill")
                                        ssbot.sendPublicMessage("?alert "+bname+" is not responding and has been killed")
                                        self.bots_to_check[event.pname] = True
                            self.tm.set(60,1)
        elif event.type in  [EVENT_COMMAND, EVENT_MESSAGE]:
            if event.pname in self.bots_to_check:
                self.bots_to_check[event.pname] = True
    def Cleanup(self):
        pass

if __name__ == '__main__': 
    botMain(Bot,False,False,"99")