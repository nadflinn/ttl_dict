import unittest
import time
import threading

from ttl_dict.ttl_dict import TTLDict

class TTLDictTest(unittest.TestCase):

	def test_value_expires(self):
		ttl_value = 3
		ttl_dict = TTLDict()
		ttl_dict.setitem('key1', 'value1', ttl_value)
		self.assertEqual(ttl_dict.get('key1'), 'value1')
		time.sleep(ttl_value + 1)
		self.assertEqual(ttl_dict.get('key1'), None)

	def test_multiple_values_expire(self):
		ttl_value = 3
		ttl_dict = TTLDict()
		ttl_dict.setitem('key1', 'value1', ttl=ttl_value)
		time.sleep(2)
		ttl_dict.setitem('key2', 'value2', ttl=ttl_value)
		self.assertEqual(ttl_dict.get('key1'), 'value1')
		self.assertEqual(ttl_dict.get('key2'), 'value2')
		time.sleep(2)
		self.assertEqual(ttl_dict.get('key1'), None)
		self.assertEqual(ttl_dict.get('key2'), 'value2')
		time.sleep(3)
		self.assertEqual(ttl_dict.get('key2'), None)

	def test_reset_value(self):
		ttl_value = 3
		ttl_dict = TTLDict()
		ttl_dict.setitem('key1', 'value1', ttl=ttl_value)
		time.sleep(2)
		ttl_dict.setitem('key1', 'value1', ttl=ttl_value)
		time.sleep(2)
		self.assertEqual(ttl_dict.get('key1'), 'value1')
		time.sleep(2)
		self.assertEqual(ttl_dict.get('key1'), None)

	def test_multiple_dict_same_key_expire(self):
		"""
		Ensure that TTL times are managed separately.
		"""
		ttl_dict1 =  TTLDict()
		ttl_dict2 =  TTLDict()

		ttl_dict1.setitem('key1', 'value1', ttl=3)
		time.sleep(2)
		ttl_dict2.setitem('key1', 'value1', ttl=3)
		
		self.assertEqual(ttl_dict1.get('key1'), 'value1')
		self.assertEqual(ttl_dict2.get('key1'), 'value1')
		
		time.sleep(2)
		self.assertEqual(ttl_dict1.get('key1'), None)
		self.assertEqual(ttl_dict2.get('key1'), 'value1')

		time.sleep(2)
		self.assertEqual(ttl_dict2.get('key1'), None)

	def test_standard_key_val_assignment(self):
		ttl_dict = TTLDict(TTL=3)
		
		ttl_dict['key1'] = 'value1'
		
		time.sleep(2)
		
		ttl_dict['key2'] = 'value2'

		self.assertEqual(ttl_dict.get('key1'), 'value1')
		self.assertEqual(ttl_dict.get('key2'), 'value2')

		time.sleep(2)

		self.assertEqual(ttl_dict.get('key1'), None)
		self.assertEqual(ttl_dict.get('key2'), 'value2')

		time.sleep(2)

		self.assertEqual(ttl_dict.get('key2'), None)

	def test_delete_key(self):
		ttl_dict = TTLDict(TTL=2)
		ttl_dict['key1'] = 'value1'
		time.sleep(1)
		del ttl_dict['key1']

		self.assertIsNone(ttl_dict.get('key1'))

		# internal ttl_dict still has key
		self.assertEqual(ttl_dict.ttl_dict.empty(), False)

		time.sleep(2)

		# key is wiped from internal_dict, after it is checked at the original anticipated expiration
		self.assertEqual(ttl_dict.ttl_dict.empty(), True)	

	def test_thread_count_dedicated_thread(self):
		# current_thread_count = threading.active_count()
		ttl_dict_original_thread = TTLDict()
		current_thread_count = threading.active_count()
		ttl_dict_same_thread = TTLDict()
		
		self.assertTrue(current_thread_count == threading.active_count())

		ttl_dict_dedicated_thread = TTLDict(dedicated_thread=True)
		self.assertTrue((current_thread_count + 1) == threading.active_count())

