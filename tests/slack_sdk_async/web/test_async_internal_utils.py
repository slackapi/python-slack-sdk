import os
import tempfile
import unittest

from slack_sdk.web.async_internal_utils import _files_to_data


class TestAsyncInternalUtils(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.existing_path = os.path.join(self.tmp_dir.name, "existing.txt")
        with open(self.existing_path, "w") as f:
            f.write("hello")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_files_to_data_closes_opened_files_when_a_later_file_fails_to_open(self):
        missing_path = os.path.join(self.tmp_dir.name, "missing.txt")
        req_args = {"files": {"first": self.existing_path, "second": missing_path}, "data": {}}

        with self.assertRaises(FileNotFoundError):
            _files_to_data(req_args)

        self.assertTrue(req_args["data"]["first"].closed)

    def test_files_to_data_keeps_files_open_until_the_returned_stack_exits(self):
        req_args = {"files": {"first": self.existing_path}, "data": {}}

        with _files_to_data(req_args):
            self.assertFalse(req_args["data"]["first"].closed)

        self.assertTrue(req_args["data"]["first"].closed)
