import unittest
import time
import json

import boto3

from awstestutils import (LiveTestBoto3Resource,
                          LiveTestQueue,
                          LiveTestTopicQueue, LiveTestDynamoDBTable)


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
    def setUp(self):
        self.region_name = 'us-west-1'

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
        with LiveTestQueue(region_name=self.region_name) as queue:
            queue_url = queue.url
        self.assertTrue('http' in queue_url)

    def test_message_in_queue(self):
        with LiveTestQueue(region_name=self.region_name) as queue:
            queue.send_message(MessageBody='test text')
            msgs = queue.receive_messages()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].body, 'test text')

    def test_deleted_queue(self):
        # Create the queue.
        live = LiveTestQueue(region_name=self.region_name)
        live.__enter__()

        # Send a message to trigger queue creation.
        live.queue.send_message(MessageBody='dummy message')
        time.sleep(5)
        num_queues = self._count_sqs_queues(live.sqs)
        try:
            self.assertEqual(num_queues, 1)
        except Exception as e:
            # Call live.queue.delete() even if that last assertion fails.
            live.queue.delete()
            raise e

        # Destroy the queue.
        live.__exit__(None, None, None)
        num_queues = self._count_sqs_queues(live.sqs)
        self.assertEqual(num_queues, 0)


class LiveTestTopicQueueTestCase(unittest.TestCase):
    def setUp(self):
        self.region_name = 'us-west-1'

    def test_use_topic(self):
        with LiveTestTopicQueue(region_name=self.region_name) as (topic, queue):
            topic_arn = topic.arn
        self.assertTrue('sns' in topic_arn)

    def test_create_topic_and_queue(self):
        live = LiveTestTopicQueue(region_name=self.region_name)
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
        with LiveTestTopicQueue(region_name=self.region_name) as (topic, queue):
            topic.publish(Message='some')
            time.sleep(1)
            msgs = queue.receive_messages()

        self.assertEqual(len(msgs), 1)
        payload = json.loads(msgs[0].body)['Message']
        self.assertEqual(payload, 'some')


class LiveTestDynamoDBTableTestCase(unittest.TestCase):
    def setUp(self):
        self.region_name = 'us-west-1'

    def test_use_table(self):
        with LiveTestDynamoDBTable(region_name=self.region_name) as table:
            table_arn = table.table_arn
        self.assertTrue('dynamodb' in table_arn)

    def test_table_creation(self):
        key_schema, attribute_definitions, provisioned_throughput = LiveTestDynamoDBTable.create_key_schema(
            partition_key_name='my_partition_key', sorting_key_name='my_sorting_key',
            partition_key_type='S', sorting_key_type='N', read_capacity_units=1, write_capacity_units=1)
        with LiveTestDynamoDBTable(key_schema_definition=key_schema,
                                   attribute_definitions=attribute_definitions,
                                   provisioned_throughput=provisioned_throughput) as table:
            self.assertEqual(key_schema, table.key_schema)
            self.assertEqual(attribute_definitions, table.attribute_definitions)
            # Boto3's DynamoDB Table comes with a number of decreases of the day that prevents the assertion from being
            # true. That property is a dynamic property never specified in the API, so it cannot be controlled by during
            # initialization
            del table.provisioned_throughput['NumberOfDecreasesToday']
            self.assertEqual(provisioned_throughput, table.provisioned_throughput)

    def test_insert_item(self):
        key_schema, attribute_definitions, provisioned_throughput = LiveTestDynamoDBTable.create_key_schema(
            partition_key_name='my_partition_key', sorting_key_name='my_sorting_key',
            partition_key_type='S', sorting_key_type='N', read_capacity_units=1, write_capacity_units=1)
        with LiveTestDynamoDBTable(key_schema_definition=key_schema,
                                   attribute_definitions=attribute_definitions,
                                   provisioned_throughput=provisioned_throughput) as live_table:
            dynamodb = boto3.resource('dynamodb')
            testing_table = dynamodb.Table(live_table.name)
            item = {
                'my_partition_key': 'test',
                'my_sorting_key': 0,
                'my_testing_attribute': 'testing attribute'
            }
            live_table.put_item(Item=item)
            response = testing_table.get_item(Key={
                'my_partition_key': 'test',
                'my_sorting_key': 0
            })
            testing_item = response['Item']
            self.assertEqual(item, testing_item)
            testing_table = None
