================
Boto3 test utils
================

:Author:   Elvio Toccalino
:Date:     |date|
:Version:  $Revision: 0.1.0 $
:Abstract: Artifacts to test dependencies with AWS using boto3

.. |date| date:: %Y/%m/%d

Testing artifacts to work with the `boto3 <https://pypi.python.org/pypi/boto3>`_ library.

So far, utils cover working with SQS queues and SNS topics.

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

-----
Miscs
-----

reduce_logging_output()
  Quicky reduces the amount of logging output from botocore to simplify debugging of other components.

-----
Tests
-----

The package includes a set of integration tests. These test live objects against the AWS backend, so the network must be up and the boto3 must be correctly configured (`as described here <https://boto3.readthedocs.org/en/latest/guide/quickstart.html#configuration>`_).
