import unittest
import time
import json
from awstestutils import (LiveTestBoto3Resource,
                          LiveTestQueue,
                          LiveTestTopicQueue)


class LiveTestBoto3ResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.resource = LiveTestBoto3Resource()

    def test_name(self):
        name = self.resource._generate_test_name()
        num_name = name.split('-')[1]
        self.assertTrue(int(num_name) > 0)

    def test_is_error_on_error(self):
        r = {'ResponseMetadata': {'HTTPStatusCode': 400}}
        self.assertTrue(self.resource._is_error_call(r))

    def test_is_error_no_error(self):
        r = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        self.assertFalse(self.resource._is_error_call(r))

    def test_generate_one_name(self):
        self.resource.exists = lambda name: False
        name = self.resource.generate_name()
        self.assertTrue(len(name) > 0)

    def test_generate_name_repeated(self):
        # Simulate the first name exists.
        def exists():
            exists_one = [True]
            def _exists_once(name):
                if exists_one[0]:
                    exists_one[0] = False
                return exists_one[0]
            return _exists_once

        self.resource.exists = exists()
        name = self.resource.generate_name()
        self.assertTrue(len(name) > 0)


class LiveTestQueueTestCase(unittest.TestCase):

    def _count_sqs_queues(self, sqs):
        """Count the number of queues, accounting for latency.

        Good to count when a queue has just been created.
        Bad to count when all queues have just been deleted.
        """
        count = 1
        left_over_queues = 1
        while count <= 10 and left_over_queues != 0:
            left_over_queues = len(list(sqs.queues.all()))
            if left_over_queues == 0:
                break
            time.sleep(1)
            count += 1
        return left_over_queues

    def test_use_queue(self):
        with LiveTestQueue() as queue:
            queue_url = queue.url
        self.assertTrue('http' in queue_url)

    def test_message_in_queue(self):
        with LiveTestQueue() as queue:
            queue.send_message(MessageBody='test text')
            msgs = queue.receive_messages()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].body, 'test text')

    def test_deleted_queue(self):
        # Create the queue.
        live = LiveTestQueue()
        live.__enter__()

        # Send a message to trigger queue creation.
        live.queue.send_message(MessageBody='dummy message')
        time.sleep(1)
        num_queues = self._count_sqs_queues(live.sqs)
        self.assertEqual(num_queues, 1)
        # FIX: If that last assertion fails, live.queue.delete() is not called!

        # Destroy the queue.
        live.__exit__(None, None, None)
        num_queues = self._count_sqs_queues(live.sqs)
        self.assertEqual(num_queues, 0)


class LiveTestTopicQueueTestCase(unittest.TestCase):

    def test_use_topic(self):
        with LiveTestTopicQueue() as (topic, queue):
            topic_arn = topic.arn
        self.assertTrue('sns' in topic_arn)

    def test_create_topic_and_queue(self):
        live = LiveTestTopicQueue()
        self.assertIsNone(live.topic)
        self.assertIsNone(live.queue)
        self.assertIsNone(live.topic_name)
        self.assertIsNone(live.queue_name)
        try:
            live.create_topic_and_queue()
            time.sleep(1)
            self.assertIsNotNone(live.topic)
            self.assertIsNotNone(live.queue)
            self.assertIsNotNone(live.topic_name)
            self.assertIsNotNone(live.queue_name)
        finally:
            live.destroy_topic_and_queue()
        time.sleep(1)
        self.assertIsNone(live.topic)
        self.assertIsNone(live.queue)
        self.assertIsNone(live.topic_name)
        self.assertIsNone(live.queue_name)

    def test_message_sent(self):
        with LiveTestTopicQueue() as (topic, queue):
            topic.publish(Message='some')
            time.sleep(1)
            msgs = queue.receive_messages()

        self.assertEqual(len(msgs), 1)
        payload = json.loads(msgs[0].body)['Message']
        self.assertEqual(payload, 'some')
