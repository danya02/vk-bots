import bot
import main
import vk_api
import traceback
import getpass
import schedule

class KeyboardBot(bot.VKBot):
    def on_message(self,message):
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


if __name__ == '__main__':
    k=KeyboardBot()
    s=vk_api.VkApi(login=input('Login: '), password=getpass.getpass())
    s.auth()
    supers=main.Session(s, 2000000001)
    m=main.VKBotManager([(supers,k)])
    try:
        k.work()
    except:
        m.running=False
