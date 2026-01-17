import unittest

from slack_sdk.models.blocks.block_elements import UrlSourceElement
from slack_sdk.models.messages.chunk import MarkdownTextChunk, TaskUpdateChunk


class MarkdownTextChunkTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            MarkdownTextChunk(text="greetings!").to_dict(),
            {
                "type": "markdown_text",
                "text": "greetings!",
            },
        )


class PlanUpdateChunkTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            PlanUpdateChunk(title="Crunching numbers...").to_dict(),
            {
                "type": "plan_update",
                "title": "Crunching numbers...",
            },
        )


class TaskUpdateChunkTests(unittest.TestCase):
    def test_json(self):
        self.assertDictEqual(
            TaskUpdateChunk(id="001", title="Waiting...", status="pending").to_dict(),
            {
                "type": "task_update",
                "id": "001",
                "title": "Waiting...",
                "status": "pending",
            },
        )
        self.assertDictEqual(
            TaskUpdateChunk(
                id="002",
                title="Wondering...",
                status="in_progress",
                details="- Gathering information...",
            ).to_dict(),
            {
                "type": "task_update",
                "id": "002",
                "title": "Wondering...",
                "status": "in_progress",
                "details": "- Gathering information...",
            },
        )
        self.assertDictEqual(
            TaskUpdateChunk(
                id="003",
                title="Answering...",
                status="complete",
                output="Found a solution",
                sources=[
                    UrlSourceElement(
                        text="Discussion of Life's Questions",
                        url="https://www.answers.com",
                    ),
                    UrlSourceElement(
                        text="The Free Encyclopedia",
                        url="https://wikipedia.org",
                        icon_url="https://example.com/globe.png",
                    ),
                ],
            ).to_dict(),
            {
                "type": "task_update",
                "id": "003",
                "title": "Answering...",
                "status": "complete",
                "output": "Found a solution",
                "sources": [
                    {
                        "type": "url",
                        "text": "Discussion of Life's Questions",
                        "url": "https://www.answers.com",
                    },
                    {
                        "type": "url",
                        "text": "The Free Encyclopedia",
                        "url": "https://wikipedia.org",
                        "icon_url": "https://example.com/globe.png",
                    },
                ],
            },
        )
