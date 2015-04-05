import awstestutils
import unittest
import json

class ObjectUnderTest:

    def __init__(self, sqs_queue):
        self.queue = sqs_queue
        self.data = {}

    def do_something(self):
        self.data.update({
            'some': 'value',
            'other': 123,
        })

    def send_results_to_backend(self):
        payload = json.dumps(self.data)
        self.queue.send_message(MessageBody=payload)


class TestCase(unittest.TestCase):

    def test_it(self):
        with awstestutils.LiveTestQueue() as queue:
            o = ObjectUnderTest(sqs_queue=queue)
            o.do_something()
            data = o.data
            o.send_results_to_backend()
            msgs = queue.receive_messages()
        self.assertEqual(len(msgs), 1)
        expected = json.dumps(data)
        self.assertEqual(msgs[0].body, expected)


if __name__ == '__main__':
    unittest.main()
