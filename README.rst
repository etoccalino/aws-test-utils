================
Boto3 test utils
================

:Author:   Elvio Toccalino
:Date:     |date|
:Version:  $Revision: 1.0.0 $

.. |date| date:: %Y/%m/%d

Testing artifacts to work with the `boto3 <https://pypi.python.org/pypi/boto3>`_ library.

The focus is on **python 3** and **boto3**. So far, utils cover working with SQS queues and SNS topics.

---
SQS
---

LiveTestQueue allows to quicky test code that depends on a SQS queue.

>>> with LiveTestQueue() as queue:
>>>   queue.send_message(MessageBody='some')
>>>   msgs = queue.receive_messages()
>>>   print(msgs[0].body)

The context manager takes care of creating and finally deleting the queue, as well as ensuring the queue has a unique name (prefixed, to be identified as a "test" queue).

---
SNS
---

LiveTestTopicQueue allows to test code on topics.

>>> with LiveTestTopicQueue() as topic, queue:
>>>     topic.publish(Message='some')
>>>     msgs = queue.receive_messages()
>>>     print(msgs[0].body)

The context manager creates (and finally deletes) a pair of objects, one topic and one queue, that work together. Messages published to the topic can be red back on the queue. The topic has the appropriate policy to publish to the queue, and the queue is subscribed to the topic to operate as its endpoint.

--------
DynamoDB
--------

LiveTestDynamoDBTable allows to test using live test DynamoDB tables:

>>> key_schema, attribute_definitions, provisioned_throughput = LiveTestDynamoDBTable.create_key_schema(
>>>     partition_key_name='my_partition_key', sorting_key_name='my_sorting_key',
>>>     partition_key_type='S', sorting_key_type='N', read_capacity_units=1, write_capacity_units=1)
>>> with LiveTestDynamoDBTable(key_schema_definition=key_schema,
>>>                            attribute_definitions=attribute_definitions,
>>>                            provisioned_throughput=provisioned_throughput) as table:

Note the helper function to create the key schemas. Upong exiting the context manager, the test table is deleted.

-----
Miscs
-----

reduce_logging_output()
  Quicky reduces the amount of logging output from botocore to simplify debugging of other components.

cleanup()
  Delete test topics and queues that might have been left behind. This function can also be invoked as a script, using ``python -m awstestutils.cleanup``.

-----
Tests
-----

The package includes a set of integration tests. These test live objects against the AWS backend, so the network must be up and the boto3 must be correctly configured (`as described here <https://boto3.readthedocs.org/en/latest/guide/quickstart.html#configuration>`_).

--------
Examples
--------

An example test can be found in ``examples.py``.

Test an object that uses a topic to send data::

  with LiveTestQueue() as queue:
      o = ObjectUnderTest(sqs_queue=queue)
      o.do_something()
      o.send_results_to_backend()

      msgs = queue.receive_messages()
  self.assertEqual(len(msgs), 1)
  expected = json.dumps(expected_output)
  self.assertEqual(msgs[0].body, expected)

Testing an object that publishes to a topic, inspecting the message published::

  with LiveTestTopicQueue() as (topic, queue):
      o = ObjectUnderTest(topic)
      o.do_something()
      o.send_results_to_aws()

      msgs = queue.receive_messages()
  expected = json.dumps(expected_output)
  self.assertEqual(msgs[0].body, expected)

-------------
Collaborators
-------------

- Facundo Martinez (@fnmartinez) did an awesome job adding support for DynamoDB and its associated tests.
- Ezequiel Pochiero (@epochiero) fixed the original blunder managing the region names.

Thank you both!
