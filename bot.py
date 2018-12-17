#!/usr/bin/python3
import schedule

class VKBot:
    def __init__(self):
        pass
    def on_message(self,message) -> bool:
        '''
        Do any needed actions on this message.
        Return a boolean: if it is False, it is assumed that this bot doesn't
        care about this message, and it should be sent to the next bot in the
        list; if True, the message will not be shown to lower-priority bots.
        '''
        return False
    def send_message(self,*args,**kwargs):
        '''
        Send a message on my session.

        This should be replaced with the actual function when the manager connects.
        '''
        pass
    def send_debug_message(self, *args, **kwargs):
        '''
        Send a message on my session.
        This message may not be actually sent, if the manager doesn't want to
        send debug messages. Therefore, this should only be used for debug info.

        This should be replaced with the actual function when the manager connects.
        '''
        pass
    def create_jobs(self):
        '''
        Register any repeating actions with the `schedule` module.
        The jobs are instance-identified, so they can be destroyed later.
        To make the job destroyable, set the `origin_bot` field of every method
        to `self`.

        This should be run when the bot is connected to a manager.
        '''
        pass
    def destroy_jobs(self):
        '''
        Delete any jobs created by me in the 'schedule' module.
        Used if the bot needs to be torn down.

        This should be run when the bot is disconnected from a manager.
        '''
        for i in schedule.jobs:
            if i.job_func.bot_id==self:
                schedule.cancel_job(i)
