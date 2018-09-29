# TTL dict
A dictionary with a TTL for each key:value pair.

A `TTLDict` is passed a TTL arg which serves as the default TTL(if a TTL is not specified the default is 60s):  

`ttl_dict = TTLDict(TTL=10)`  

A key:value pair can be added using the standard assignment method and it takes on the default TTL:  

`ttl_dict['foo'] = 'bar'`  

Alternatively a specific TTL can be set using the method `TTLDict.setitem(key, value, TTL)`:  

`ttl_dict.setitem('foo', 'bar', ttl=5)`  

## How it works
A background thread is created when the first `TTLDict` is instantiated within a given process and a `PriorityQueue` is created to keep track of the TTLs.  The background thread keeps track of when the next key:value is set to expire and sleeps until then.  

By default all instantiations of TTLDict within a given process will share the same background thread.  However, if you want a TTLDict to have it's own dedicated thread you can use the `dedicated_thread` parameter and this will set up a separte thread to keep track of and expire items only in that `TTLDict` instance:  

`ttl_dict = TTLDict(TTL=10, dedicated_thread=True)`  


### Examples
All key:value pairs inherit TTL set at dictionary intitialization:  

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

Use a standard Queue instead of Priority Queue with a TTL fixed for all key:vlaue pairs in the dictionary:  
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
