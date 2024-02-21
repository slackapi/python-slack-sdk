import unittest

import boto3

try:
    from moto import mock_aws
except ImportError:
    from moto import mock_s3 as mock_aws
from slack_sdk.oauth.state_store.amazon_s3 import AmazonS3OAuthStateStore


class TestAmazonS3(unittest.TestCase):
    mock_aws = mock_aws()
    bucket_name = "test-bucket"

    def setUp(self):
        self.mock_aws.start()
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(self.bucket_name)
        bucket.create(CreateBucketConfiguration={"LocationConstraint": "af-south-1"})

    def tearDown(self):
        self.mock_aws.stop()

    def test_instance(self):
        store = AmazonS3OAuthStateStore(
            s3_client=boto3.client("s3"),
            bucket_name=self.bucket_name,
            expiration_seconds=10,
        )
        self.assertIsNotNone(store)

    def test_issue_and_consume(self):
        store = AmazonS3OAuthStateStore(
            s3_client=boto3.client("s3"),
            bucket_name=self.bucket_name,
            expiration_seconds=10,
        )
        state = store.issue()
        result = store.consume(state)
        self.assertTrue(result)
        result = store.consume(state)
        self.assertFalse(result)
