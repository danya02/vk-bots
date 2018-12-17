#!/usr/bin/python3
import bot
import vk_api
import hashlib
import time
import schedule

class Session:
    def __init__(self,vk_session, chat_id):
        self.vk_session=vk_session
        self.api=self.vk_session.get_api()
        self.chat_id=chat_id
        self.latest_message = {'date':time.time()}
    def get_new_messages(self):
        '''
        Get new messages on this session.
        The messages are new if local time is not in the future relative
        to server time, and both are monotonously increasing.
        '''
        messages=[]
        history = api.messages.getHistory(peer_id=registration.chat_id,count=10)['items']
        for i in history:
            if i['date']>self.latest_message['date']:
                self.latest_message=i
                messages.append(i)
        return messages
    def send_message(self,**params):
        params.update({'peer_id':self.chat_id, 'random_id':0})
        return self.api.messages.send(**params)


@dataclass
class BotRegistration:
    bot: bot.VKBot
    session: Session
    chat_id: int


class VKBotManager:
    def __init__(self):
        self.running = True
        self.bots = []
        self.log_bot_internal=True
    def send_message(self, bot, **params):
        '''
        Send a message on the behalf of a bot.
        '''
        for i in self.bots:
            if i.bot==bot:
                i.session.send_message(**params)
                break
    def attach_bot(self,session, bot, chat_id):
        registration = BotRegistration(bot, session, chat_id)
        bot.create_jobs()
        if self.log_bot_internal:
            session.send_message(message='SYSTEM: '+repr(bot)+' was attached.')
    def detach_bot(self,bot):
        for i in self.bots:
            if bot==i.bot:
                bot.destroy_jobs()
                if self.log_bot_internal:
                    i.session.send_message(message='SYSTEM: '+repr(bot)+' was detached.')
    def work_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)
        for i in self.bots:
            self.detach_bot(i)
