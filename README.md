# TTL dict
A dictionary with a TTL for each key:value pair.

A `TTLDict` is passed a TTL arg which serves as the default TTL(if a TTL is not specified the default is 60s):  

`ttl_dict = TTLDict(TTL=10)`  

A key:value pair can be added using the standard assignment method and it takes on the default TTL:  

`ttl_dict['foo'] = 'bar'`  

Alternatively a specific TTL can be set using the method `TTLDict.setitem(key, value, TTL)`:  

`ttl_dict.setitem('foo', 'bar', ttl=5)`  

## How it works
A background thread is created when the first `TTLDict` is instantiated within a given process and a `PriorityQueue` is created to keep track of the TTLs.  A PriorityQueue is used as it ensures that the items will be ordered based on the TTL so that the next item to expire will always be the next item in the queue.  This leads to a slight time penalty for insertions of log(n) as opposed to a standard Queue where an insert would be O(1).  If all items in a given TTLDict are to have the same TTL then a standard Queue can be used (use `TTLDictFixed` instead of `TTLDict`) as items can simply be appended to the end of the Queue and still maintain their order.

The background thread works through the (Priority)Queue checking one item at a time (the first item in the Queue). If the item is not ready to expire the thread sleeps until it is ready.  If an item is ready then it is deleted from the dictionary and the thread moves on to the next item.

By default all instantiations of TTLDict within a given process will share the same background thread.  However, if you want a TTLDict to have it's own dedicated thread you can use the `dedicated_thread` parameter and this will set up a separte thread to keep track of and expire items only in that `TTLDict` instance:  

`ttl_dict = TTLDict(TTL=10, dedicated_thread=True)`  

Because a TTL for a given key can be updated between the time it is set and the time it expires you can have multiple instances of a given key and an associated TTL in the PriorityQueue. In order to account for this a mapping of each key and its most recent expiration time is maintained so that when an item is popped from the queue we can check to see if it is the correct (i.e. most recent) time of expiration. If it is not then we simply drop that item on the floor and move on. If it is then we delete the key:value from the dictionary.

### Examples
All key:value pairs inherit the TTL set at dictionary intitialization:

```
>>> from ttl_dict import TTLDict
>>> import time
>>> def ttl_dict_basic_example():
>>>     ttl_dict = TTLDict(TTL=1)
>>>     ttl_dict['foo'] = 'bar'
>>>     print("ttl_dict at 0 seconds: {}".format(str(ttl_dict)))
>>>     time.sleep(2)
>>>     print("ttl_dict at 2 seconds: {}".format(str(ttl_dict)))
>>>
>>> ttl_dict_basic_example()
ttl_dict at 0 seconds: {'foo': 'bar'}
ttl_dict at 2 seconds: {}
```  

One can set a specific TTL for any given key:value pair:
```
>>> from ttl_dict import TTLDict
>>> import time
>>> def mixed_ttl_example():
>>>     ttl_dict = TTLDict(TTL=3)
>>>     ttl_dict['key1'] = 'value1'
>>>     ttl_dict.setitem('key2', 'value2', ttl=1)
>>>     print("Dict at 0 seconds: {}".format(str(ttl_dict)))
>>>     time.sleep(2)
>>>     print("Dict at 2 seconds: {}".format(str(ttl_dict)))
>>>     time.sleep(2)
>>>     print("Dict at 4 seconds: {}".format(str(ttl_dict)))
>>>
>>> mixed_ttl_example()
Dict at 0 seconds: {'key2': 'value2', 'key1': 'value1'}
Dict at 2 seconds: {'key1': 'value1'}
Dict at 4 seconds: {}
```  

Use a standard Queue instead of Priority Queue with a TTL fixed for all key:value pairs in the dictionary:  
```
>>> from ttl_dict import TTLDictFixed
>>> import time
>>> def ttl_dict_normal_queue():
>>>     ttl_dict = TTLDictFixed(TTL=1)
>>>     ttl_dict['foo'] = 'bar'
>>>     print("ttl_dict at 0 seconds: {}".format(str(ttl_dict)))
>>>     time.sleep(2)
>>>     print("ttl_dict at 2 seconds: {}".format(str(ttl_dict)))
>>>
>>> ttl_dict_normal_queue()
ttl_dict at 0 seconds: {'foo': 'bar'}
ttl_dict at 2 seconds: {}
```

Dedicated thread per dictionary:  
```
>>>import threading
>>>threading.active_count()
1
>>>ttl_dict = TTLDict(TTL=3)
>>>threading.active_count()
2
>>>ttl_dict2 = TTLDict(TTL=3)
>>>threading.active_count()
2
>>>ttl_dict3 = TTLDict(TTL=3, dedicated_thread=True)
>>>threading.active_count()
3
```

### Installation

```
python setup.py install
```

### Run Tests

```
python setup.py test
```
