import threading
import time
from collections import OrderedDict
from Queue import PriorityQueue, Queue, Empty

ttl_dict_priority = PriorityQueue()
ttl_dict_queue = Queue()
most_recent_value_dict = dict()
most_recent_value_lock = threading.Lock()
lock_actual_dict = threading.RLock()
worker_proceed = threading.Event()
shared_thread = None


def worker(self):
    while True:
        next_item = self.get_item()
        with self.most_recent_value_lock:
            outdated = next_item.time != self.most_recent_value_dict[id(next_item.actual_dict)][next_item.key]
        if outdated:
            # this is an outdated TTL for this key, we can move on
            continue

        to_wait = next_item.time - time.time()
        if to_wait < 0:
            with self.lock_actual_dict:
                try:
                    # reentrant lock needed otherwise we would deadlock in __delitem__ where lock is also aquired
                    del next_item.actual_dict[next_item.key]
                except KeyError:
                    # someone manually deleted this key already
                    pass
            continue
        else:
            # we put the item back because it isn't ready
            self.put_item_front(next_item)

        # The last item is not ready to delete yet so we wait until it is ready
        self.worker_proceed.wait(to_wait)
        # Reset event in case of interrupt
        self.worker_proceed.clear()


class TTLDictItem(object):

    def __init__(self, time, key, actual_dict):
        self.time = time
        self.key = key
        self.actual_dict = actual_dict

    def __cmp__(self, other_item):
        return cmp(self.time, other_item.time)

    def get_dict(self):
        return self

class TTLDict(dict):

    def __init__(self, TTL=60, dedicated_thread=False):
        self.TTL = TTL
        if dedicated_thread:
            self._setup_dedicated_thread()
        else:
            self._setup_default_thread()

    def _get_queue(self, dedicated_thread=False):
        return PriorityQueue() if dedicated_thread else ttl_dict_priority

    def _setup_default_thread(self):
        self.most_recent_value_dict = most_recent_value_dict
        self.most_recent_value_dict[id(self)] = dict()
        self.most_recent_value_lock = most_recent_value_lock
        self.lock_actual_dict = lock_actual_dict
        self.worker_proceed = worker_proceed
        self.ttl_dict = self._get_queue(False)
        self._create_background_thread()

    def _setup_dedicated_thread(self):
        self.most_recent_value_dict = dict()
        self.most_recent_value_dict[id(self)] = dict()
        self.most_recent_value_lock = threading.Lock()
        self.lock_actual_dict = threading.RLock() 
        self.worker_proceed = threading.Event()
        self.ttl_dict = self._get_queue(True)
        self._create_dedicated_thread()

    def _create_background_thread(self):
        global shared_thread
        if not shared_thread:
            print "Creating a thread"
            shared_thread = threading.Thread(target=worker, args=(self,))
            shared_thread.setDaemon(True)
            shared_thread.start()

    def _create_dedicated_thread(self):      
        self.dedicated_thread = threading.Thread(target=worker, args=(self,))
        self.dedicated_thread.setDaemon(True)
        self.dedicated_thread.start()

    def __setitem__(self, key, val):
        self.setitem(key, val, self.TTL)

    def setitem(self, key, val, ttl=0):
        if not ttl:
            ttl = self.TTL

        with self.lock_actual_dict:
            dict.__setitem__(self, key, val)

        item_ttl = time.time() + ttl

        with self.most_recent_value_lock:
            # Must keep track of a key's most recent TTL because with no updating of queue, duplicates can exist.
            self.most_recent_value_dict[id(self)][key] = item_ttl

        self.ttl_dict.put(TTLDictItem(time=item_ttl, key=key, actual_dict=self))

        # if item added is next up, we interrupt waiting worker to figure out when
        self.worker_proceed.set()

    def put_item_front(self, item):
        self.ttl_dict.put(item)

    def get_item(self):
        return self.ttl_dict.get()

    def __delitem__(self, key):
        with self.lock_actual_dict:
            dict.__delitem__(self, key)


class TTLDictFixed(TTLDict):

    def _get_queue(self, dedicated_thread=False):
        return Queue() if dedicated_thread else ttl_dict_queue

    def __setitem__(self, key, val):
        super(TTLDictFixed, self).setitem(key, value, self.TTL)

    def put_item_front(self, item):
        self.ttl_dict.queue.appendleft(item)
