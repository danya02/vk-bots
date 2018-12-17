#!/usr/bin/python3
import vk_api
import hashlib
import time
import schedule
import threading
import traceback

class Session:
    def __init__(self,vk_session, chat_id):
        self.vk_session=vk_session
        self.api=self.vk_session.get_api()
        self.chat_id=chat_id
        self.latest = time.time()
    def get_new_messages(self):
        '''
        Get new messages on this session.
        This depends on local time being close to server time.
        '''
        messages=[]
        history = api.messages.getHistory(peer_id=registration.chat_id,count=10)['items']
        for i in history:
            if i['date']>self.latest:
                self.latest_message=i
                messages.append(i)
        return messages
    def send_message(self,**params):
        '''
        Send a message using this session and update the latest time.
        This depends on local time being close to server time.
        '''
        self.latest = time.time()
        params.update({'peer_id':self.chat_id, 'random_id':0})
        return self.api.messages.send(**params)


class BotRegistration:
    def __init__(self,bot,session):
        self.bot=bot
        self.session=session


class VKBotManager:
    def __init__(self,to_attach=[]):
        self.log_bot_internal=True
        self.running = True
        self.bots = []
        for i in to_attach:
            self.attach_bot(*i)
        self.work_thread = threading.Thread(target=self.work_loop)
        self.work_thread.start()
    def attach_bot(self,session, bot):
        '''Attach a bot to this manager, and assign a session for it.'''
        registration = BotRegistration(bot, session)
        def send_message(**kwargs):
            session.send_message(**kwargs)
        def send_debug_message(**kwargs):
            if self.log_bot_internal:
                session.send_message(**kwargs)
        bot.send_message = send_message
        bot.send_debug_message=send_debug_message
        bot.create_jobs()
        self.upgrade_bot_jobs()
        self.bots.append(registration)
        if self.log_bot_internal:
            session.send_message(message='SYSTEM: '+repr(bot)+' was attached.')
    def detach_bot(self,bot):
        '''Detach a bot from the manager.'''
        for i in self.bots:
            if bot==i.bot:
                def send_message(**kwargs):pass
                bot.send_debug_message(message='SYSTEM: '+repr(bot)+' was detached.')
                bot.send_message=send_message
                bot.send_debug_message=send_message
                bot.destroy_jobs()
                self.bots.remove(i)
    def broadcast(self,**kwargs):
        '''Send a message on all chats on sessions assigned to attached bots.'''
        sessions=[]
        for i in self.bots:
            if i.session not in sessions:
                if i.session.chat_id not in [q.session_id for q in sessions]:
                    sessions.append(i.session)
        for i in sessions:
            i.send_message(**kwargs)
    def upgrade_bot_jobs(self):
        '''Wrap each job that was created by a bot with error-reporting code.'''
        for i in schedule.jobs:
            if 'wrapped' not in i.job_func.__dict__:
                oldfunc=i.job_func
                args=oldfunc.args
                keywords=oldfunc.args
                if keywords==():
                    keywords=dict()
                def func():
                    try:
                        return oldfunc()
                    except:
                        origin_bot = oldfunc.origin_bot
                        origin_bot.send_debug_message(message='Exception while running job "'+repr(i)+
                                    '" created by '+repr(origin_bot)+':\n'+traceback.format_exc())
                func.__dict__.update(oldfunc.__dict__)
                func.__dict__.update({'wrapped':True,'args':args,'keywords':keywords})
                i.job_func=func

    def work_loop(self):
        '''
        Run the scheduler, and do all cleanup actions when the manager is to shut down.
        '''
        if self.log_bot_internal:
            self.broadcast(message='SYSTEM: Manager is starting!')
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.running=False
                break
        self.broadcast(message='SYSTEM: Manager is shutting down!')
        for i in self.bots:
            self.detach_bot(i)
        time.sleep(5)
