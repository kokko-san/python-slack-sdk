import os
import unittest
import time

import pytest

from integration_tests.env_variable_names import (
    SLACK_SDK_TEST_INCOMING_WEBHOOK_URL,
    SLACK_SDK_TEST_INCOMING_WEBHOOK_CHANNEL_NAME,
    SLACK_SDK_TEST_BOT_TOKEN,
)
from slack_sdk.web import WebClient
from slack_sdk.webhook import WebhookClient
from slack_sdk.models.attachments import Attachment, AttachmentField
from slack_sdk.models.blocks import SectionBlock, DividerBlock, ActionsBlock
from slack_sdk.models.blocks.block_elements import ButtonElement
from slack_sdk.models.blocks.basic_components import MarkdownTextObject, PlainTextObject


class TestWebhook(unittest.TestCase):
    def setUp(self):
        if not hasattr(self, "channel_id"):
            token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
            channel_name = os.environ[
                SLACK_SDK_TEST_INCOMING_WEBHOOK_CHANNEL_NAME
            ].replace("#", "")
            client = WebClient(token=token)
            self.channel_id = None
            for resp in client.conversations_list(limit=1000):
                for c in resp["channels"]:
                    if c["name"] == channel_name:
                        self.channel_id = c["id"]
                        break
                if self.channel_id is not None:
                    break

    def tearDown(self):
        pass

    def test_webhook(self):
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        webhook = WebhookClient(url)
        response = webhook.send(text="Hello!")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)

        token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        client = WebClient(token=token)
        history = client.conversations_history(channel=self.channel_id, limit=1)
        self.assertIsNotNone(history)
        actual_text = history["messages"][0]["text"]
        self.assertEqual("Hello!", actual_text)

    def test_with_unfurls_off(self):
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        webhook = WebhookClient(url)
        client = WebClient(token=token)
        # send message that does not unfurl
        response = webhook.send(
            text="<https://imgs.xkcd.com/comics/desert_golfing_2x.png|Desert Golfing>",
            unfurl_links=False,
            unfurl_media=False,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)
        # wait to allow Slack API to edit message with attachments
        time.sleep(2)
        history = client.conversations_history(channel=self.channel_id, limit=1)
        self.assertIsNotNone(history)
        self.assertTrue("attachments" not in history["messages"][0])


    # FIXME: This test started failing as of August 5, 2021
    @pytest.mark.skip()
    def test_with_unfurls_on(self):
        # Slack API rate limits unfurls of unique links so test will
        # fail when repeated. For testing, either use a different URL
        # for text option or delete existing attachments in  webhook channel.
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        token = os.environ[SLACK_SDK_TEST_BOT_TOKEN]
        webhook = WebhookClient(url)
        client = WebClient(token=token)
        # send message that does unfurl
        response = webhook.send(
            text="<https://imgs.xkcd.com/comics/red_spiders_small.jpg|Spiders>",
            unfurl_links=True,
            unfurl_media=True,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)
        # wait to allow Slack API to edit message with attachments
        time.sleep(2)
        history = client.conversations_history(channel=self.channel_id, limit=1)
        self.assertIsNotNone(history)
        self.assertTrue("attachments" in history["messages"][0])

    def test_with_blocks(self):
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        webhook = WebhookClient(url)
        response = webhook.send(
            text="fallback",
            blocks=[
                SectionBlock(
                    block_id="sb-id",
                    text=MarkdownTextObject(
                        text="This is a mrkdwn text section block."
                    ),
                    fields=[
                        PlainTextObject(text="*this is plain_text text*", emoji=True),
                        MarkdownTextObject(text="*this is mrkdwn text*"),
                        PlainTextObject(text="*this is plain_text text*", emoji=True),
                    ],
                ),
                DividerBlock(),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="Create New Task", emoji=True),
                            style="primary",
                            value="create_task",
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="Create New Project", emoji=True),
                            value="create_project",
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="Help", emoji=True),
                            value="help",
                        ),
                    ],
                ),
            ],
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)

    def test_with_blocks_dict(self):
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        webhook = WebhookClient(url)
        response = webhook.send(
            text="fallback",
            blocks=[
                {
                    "type": "section",
                    "block_id": "sb-id",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a mrkdwn text section block.",
                    },
                    "fields": [
                        {
                            "type": "plain_text",
                            "text": "*this is plain_text text*",
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*this is mrkdwn text*",
                        },
                        {
                            "type": "plain_text",
                            "text": "*this is plain_text text*",
                        },
                    ],
                },
                {"type": "divider", "block_id": "9SxG"},
                {
                    "type": "actions",
                    "block_id": "avJ",
                    "elements": [
                        {
                            "type": "button",
                            "action_id": "yXqIx",
                            "text": {
                                "type": "plain_text",
                                "text": "Create New Task",
                            },
                            "style": "primary",
                            "value": "create_task",
                        },
                        {
                            "type": "button",
                            "action_id": "KCdDw",
                            "text": {
                                "type": "plain_text",
                                "text": "Create New Project",
                            },
                            "value": "create_project",
                        },
                        {
                            "type": "button",
                            "action_id": "MXjB",
                            "text": {
                                "type": "plain_text",
                                "text": "Help",
                            },
                            "value": "help",
                        },
                    ],
                },
            ],
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)

    def test_with_attachments(self):
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        webhook = WebhookClient(url)
        response = webhook.send(
            text="fallback",
            attachments=[
                Attachment(
                    text="attachment text",
                    title="Attachment",
                    fallback="fallback_text",
                    pretext="some_pretext",
                    title_link="link in title",
                    fields=[
                        AttachmentField(
                            title=f"field_{i}_title", value=f"field_{i}_value"
                        )
                        for i in range(5)
                    ],
                    color="#FFFF00",
                    author_name="John Doe",
                    author_link="http://johndoeisthebest.com",
                    author_icon="http://johndoeisthebest.com/avatar.jpg",
                    thumb_url="thumbnail URL",
                    footer="and a footer",
                    footer_icon="link to footer icon",
                    ts=123456789,
                    markdown_in=["fields"],
                )
            ],
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)

    def test_with_attachments_dict(self):
        url = os.environ[SLACK_SDK_TEST_INCOMING_WEBHOOK_URL]
        webhook = WebhookClient(url)
        response = webhook.send(
            text="fallback",
            attachments=[
                {
                    "author_name": "John Doe",
                    "fallback": "fallback_text",
                    "text": "attachment text",
                    "pretext": "some_pretext",
                    "title": "Attachment",
                    "footer": "and a footer",
                    "id": 1,
                    "author_link": "http://johndoeisthebest.com",
                    "color": "FFFF00",
                    "fields": [
                        {
                            "title": "field_0_title",
                            "value": "field_0_value",
                        },
                        {
                            "title": "field_1_title",
                            "value": "field_1_value",
                        },
                        {
                            "title": "field_2_title",
                            "value": "field_2_value",
                        },
                        {
                            "title": "field_3_title",
                            "value": "field_3_value",
                        },
                        {
                            "title": "field_4_title",
                            "value": "field_4_value",
                        },
                    ],
                    "mrkdwn_in": ["fields"],
                }
            ],
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.body)
