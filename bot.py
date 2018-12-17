#!/usr/bin/python3
import schedule

class VKBot:
    def __init__(self,manager):
        self.manager=manager
    def on_message(self,message) -> bool:
        '''
        Do any needed actions on this message.
        Return a boolean: if it is False, it is assumed that this bot doesn't
        care about this message, and it should be sent to the next bot in the
        list; if True, the message will not be shown to lower-priority bots.
        '''
        return False
    def create_jobs(self):
        '''
        Register any repeating actions with the `schedule` module.
        The jobs are instance-identified, so they can be destroyed later.
        To make the job destroyable, set the `origin_bot` field of every method
        to `self`.
        '''
        pass
    def destroy_jobs(self):
        '''
        Delete any jobs created by me in the 'schedule' module.
        Used if the bot needs to be torn down.
        '''
        for i in schedule.jobs:
            if i.job_func.bot_id==self:
                schedule.cancel_job(i)
