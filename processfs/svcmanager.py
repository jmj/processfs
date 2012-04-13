import time
import multiprocessing
import Queue
import psutil

START = 1
STOP = 2
MKPROC = 3

class Manager(multiprocessing.Process):
    def __init__(self):
        super(Manager, self).__init__()

        m = multiprocessing.Manager()
        self.procs = m.dict()
        self.queue = m.Queue()

        self._stop = multiprocessing.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        while True:
            print "DEBUG %s" % self.procs.keys()
            try:
                # startup/shutdown everything in the queue
                while True:
                    self.handleproc(self.queue.get(block=False))
                    self.queue.task_done()
            except Queue.Empty:
                # An empty queue is fine
                print 'Q Empty'
                #pass

            ## Iterate running procs checking for still running
            ##      Restart as necessary

            if self._stop.is_set():
                for p in self.procs.keys():
                    self._stopproc(p)
                return
            ## Sleep time should be a -o option from mount
            time.sleep(1)

    def handleproc(self, proc):
        print 'handleproc(%s) ' % proc
        if proc[0] == START:
            self._startproc(proc[1])
        elif proc[0] == STOP:
            self._stopproc(proc[1])
        elif proc[0] == MKPROC:
            self._mkproc(proc[1])
        else:
            raise AttributeError('Missing Action')

    def _startproc(self, proc):
        pass

    def _stopproc(self, procid):
        if procid not in self.procs.keys():
            raise ValueError('process with name %s does not exist' % (procid))
        self.procs.pop(procid)

    def _mkproc(self, procid):
        if procid in self.procs.keys():
            raise ValueError('process with name %s already exists' % (procid))
        self.procs[procid] = None

    #def _restart(self, procid):
    #    proc = self.procs[procid]
    #    self._stopproc(procid)
    #    self._startproc(proc)
