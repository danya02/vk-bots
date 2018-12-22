#!/usr/bin/python3
import vk_api
import hashlib
import time
import schedule
import threading
import traceback
import random
import time

class UserDataDict:
    """
    A class to wrap the users.get method of VK API.
    """
    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)

        return cls.instance
    def __init__(self, session):
        self.append_session(session)
    @classmethod
    def append_session(cls, session):
        try:
            cls.sessions
        except AttributeError:
            cls.sessions = []
        if session not in cls.sessions:
            cls.sessions.append(session)
    @classmethod
    def get_session(cls):
        return random.choice(cls.sessions)
    @classmethod
    def get_user(cls, user):
        return cls.users[user]
    @classmethod
    def set_user(cls, user, value):
        try:
            cls.users
        except AttributeError:
            cls.users = dict()
        cls.users.update({user: value})
    def __getitem__(self, user_id):
        if not isinstance(user_id, int):
            raise ValueError(f'User ID must be an int, not {type(user_id)}.')
        try:
            value=self.get_user(user_id)
            if value['date']+10*60 < time.time():
                raise KeyError
        except KeyError:
            value = {'date':time.time(), 'values':self.get_session().get_api().users.get(user_ids=member_id, fields='photo_id,verified,sex,bdate,city,country,home_town,has_photo,photo_50,photo_100,photo_200_orig,photo_200,photo_400_orig,photo_max,photo_max_orig,online,domain,has_mobile,contacts,site,education,universities,schools,status,last_seen,followers_count,common_count,occupation,nickname,relatives,relation,personal,connections,exports,activities,interests,music,movies,tv,books,games,about,quotes,can_post,can_see_all_posts,can_see_audio,can_write_private_message,can_send_friend_request,is_favorite,is_hidden_from_feed,timezone,screen_name,maiden_name,crop_photo,is_friend,friend_status,career,military,blacklisted,blacklisted_by_me')[0]}
            self.set_user(user_id, value)
        return value['values']


class Session:
    def __init__(self,vk_session, chat_id):
        self.vk_session=vk_session
        self.api=self.vk_session.get_api()
        self.chat_id=chat_id
        self.latest = time.time()
        self.userdata = UserDataDict(self.vk_session)
    def get_new_messages(self):
        '''
        Get new messages on this session.
        This depends on local time being close to server time.
        '''
        messages=[]
        history = self.api.messages.getHistory(peer_id=self.chat_id,count=10)['items']
        for i in history:
            if i['date']>self.latest:
                self.latest=i['date']
                messages.append(i)
        return messages
    def send_message(self,**params):
        '''
        Send a message using this session and update the latest time.
        This depends on local time being close to server time.
        '''
        try:
            params.update({'peer_id':self.chat_id, 'random_id':0})
            return_value = self.api.messages.send(**params)
        except:
            self.api.messages.send(peer_id=self.chat_id, random_id=0, message='Error while sending message: \n'+'\n'.join(traceback.format_exc().strip().split('\n')[-2:]))
        self.latest = max(*[i['date'] for i in self.api.messages.getHistory(peer_id=self.chat_id,count=10)['items']])
    def get_user(self, uid):
        '''
        Get all available information about a user ID.

        This is cached across all sessions.
        This depends on the time not changing on the local system.
        '''

        return self.userdata[uid]

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
        def check_messages():
            for i in session.get_new_messages():
                bot.on_message(i, session)
        check_messages.target_bot=bot
        schedule.every(1).seconds.do(check_messages)
        bot.send_message = send_message
        bot.send_debug_message=send_debug_message
        bot.session = session
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
                bot.session = None
                bot.send_message=send_message
                bot.send_debug_message=send_message
                for j in schedule.jobs:
                    if j.__dict__.get('target_bot')==bot:
                        schedule.jobs.remove(j)
                        break
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
            if 'wrapped' not in i.job_func.__dict__ and 'target_bot' not in i.job_func.__dict__:
                oldfunc=i.job_func
                args=oldfunc.args
                keywords=oldfunc.keywords
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
