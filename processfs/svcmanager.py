import time
import threading
import Queue
import psutil

START = 1
STOP = 2

class Manager(threading.thread):
    def __init__(self, queue):
        super(Manager, self).__init__()
        self.procs = dict()
        self.queue = queue
        self.p_lock = threading.Lock()


    def run(self):
        while True:
            try:
                # startup/shutdown everything in the queue
                while True:
                    self.handleproc(self.queue.get(block=False))
            except Queue.Empty:
                # An empty queue is fine
                pass

            ## Iterate running procs checking for still running
            ##      Restart as necessary

            ## Sleep time should be a -o option from mount
            time.sleep(5)

    def handleproc(self, proc):
        if proc[0] == START:
            self._startproc(proc[1])
        elif proc[0] == STOP:
            self._stopproc(proc[1])
        else:
            raise AttributeError('Missing Action')

    def _startproc(self, proc):
        if proc[0] in self.procs.keys():
            raise ValueError('process with name %s already exists' % (proc))
        self.proc[proc[0]] = proc[1]

    def _stopproc(self, procid):
        if procid not in self.procs.keys():
            raise ValueError('process with name %s does not exist' % (procid))
        self.procs.pop(procid)

    #def _restart(self, procid):
    #    proc = self.procs[procid]
    #    self._stopproc(procid)
    #    self._startproc(proc)
