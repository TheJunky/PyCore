import twitter
from BotUtilities import *
from SubspaceBot import *
import logging


    

class Bot(BotInterface):
    def __init__(self, bot, md):
        BotInterface.__init__( self, bot,md)
        bot.registerModuleInfo(__name__,"TweetBot","The Junky","updates status on twitter",".01")
        self._api = twitter.Api(username='extreme_games', password=self.param)
        self._tweet_command_id = bot.registerCommand('!tweet',"!tw",0,COMMAND_LIST_ALL,"web","[message]" , 'update status on twitter.com/extreme_games')
        
    def HandleEvents(self,bot,event):
        if event.type == EVENT_COMMAND and event.command.id == self._tweet_command_id:
            if self.oplist.GetAccessLevel(event.player.name) > 0:
                if len(event.arguments) > 0 and len(event.arguments_after[0]) < 140:
                    status = self._api.PostUpdate("%s - %s" % (event.arguments_after[0],event.player.name))
                    bot.sendArenaMessage( "%s just posted: %s on twitter" % (status.user.name, status.text))
                else:
                        bot.sendPrivateMessage(event.player.name,"you must provide a message of 1 to 140 characters");
            else:
                    bot.sendPrivateMessage(event.player.name,"access denied");
    def Cleanup(self):
        pass
