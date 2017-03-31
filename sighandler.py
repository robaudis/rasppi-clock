import signal


class SigHandler:
    '''
    Simple class to listen for and allow the polite handling of OS signals
    '''
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.handler)
        signal.signal(signal.SIGTERM, self.handler)
    
    def handler(self, signum, frame):
        self.kill_now = True
