import bot
import main
import vk_api
import traceback
import getpass
import schedule

class KeyboardBot(bot.VKBot):
    def on_message(self,message, session):
        print(message)
    def work(self):
        while 1:
            m = input('> ')
            if m[0]=='!':
                self.send_debug_message(message=m)
            else:
                self.send_message(message=m)
class RepeatJobFailingBot(bot.VKBot):
    def job(self):
        #self.send_message(message='Exception now!')
        raise EnvironmentError('Continue testing.')
    def create_jobs(self):
        self.job.__dict__.update({'origin_bot': self})
        schedule.every(5).seconds.do(self.job)

class EchoBot(bot.VKBot):
    def on_message(self,message,session):
        self.send_message(message='Received message: '+str(message))

class GreeterBot(bot.VKBot):
    def __init__(self,greet_msg='Welcome, {name} ({screen_name})!', goodbye_msg='Goodbye, {name} ({screen_name}).'):
        self.greet_message=greet_msg
        self.goodbye_message=goodbye_msg
    def on_message(self, message, session):
        if 'action' in message:
            if message['action']['type']=='chat_invite_user':
                member_id = str(message['action']['member_id'])
                data=session.vk_session.get_api().users.get(user_ids=member_id, fields='screen_name')[0]
                name=data['first_name']+' '+data['last_name']
                screen_name=data['screen_name']
                self.send_message(message=self.greet_message.format(name=name, screen_name=screen_name))
            elif message['action']['type']=='chat_kick_user':
                member_id = str(message['action']['member_id'])
                data=session.vk_session.get_api().users.get(user_ids=member_id, fields='screen_name')[0]
                name=data['first_name']+' '+data['last_name']
                screen_name=data['screen_name']
                self.send_message(message=self.goodbye_message.format(name=name, screen_name=screen_name))

if __name__ == '__main__':
    k=GreeterBot()
    s=vk_api.VkApi(login=input('Login: '), password=getpass.getpass())
    s.auth()
    supers=main.Session(s, 2000000001)
    m=main.VKBotManager([(supers,k)])
    try:
        input()
    except:
        m.running=False
