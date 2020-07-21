import re
from typing import List, Optional, Set

from . import EnumValidator, JsonObject, JsonValidator, extract_json
from .actions import Action
from .blocks import Block

SeededColors = {"danger", "good", "warning"}


class AttachmentField(JsonObject):
    attributes = {"short", "title", "value"}

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        value: Optional[str] = None,
        short: bool = True,
    ):
        self.title = title
        self.value = value
        self.short = short


class Attachment(JsonObject):
    attributes = {
        "author_icon",
        "author_link",
        "author_name",
        "color",
        "fallback",
        "fields",
        "footer",
        "footer_icon",
        "image_url",
        "pretext",
        "text",
        "thumb_url",
        "title",
        "title_link",
        "ts",
    }

    fields: List[AttachmentField]
    actions: List[Action]

    MarkdownFields = {"fields", "pretext", "text"}

    footer_max_length = 300

    def __init__(
        self,
        *,
        text: str,
        fallback: Optional[str] = None,
        fields: Optional[List[AttachmentField]] = None,
        color: Optional[str] = None,
        markdown_in: Optional[List[str]] = None,
        title: Optional[str] = None,
        title_link: Optional[str] = None,
        pretext: Optional[str] = None,
        author_name: Optional[str] = None,
        author_link: Optional[str] = None,
        author_icon: Optional[str] = None,
        image_url: Optional[str] = None,
        thumb_url: Optional[str] = None,
        footer: Optional[str] = None,
        footer_icon: Optional[str] = None,
        ts: Optional[int] = None,
    ):
        """
        A supplemental object that will display after the rest of the message.
        Considered legacy - recommended replacement is to use message blocks instead.

        https://api.slack.com/reference/messaging/attachments#fields

        Args:
            text: The main body text of the attachment. It can be formatted as
                plain text, or with markdown by including it in the markdown_in
                parameter. The content will automatically collapse if it contains 700+
                characters or 5+ linebreaks, and will display a "Show more..." link to
                expand the content.
            fallback: A plain text summary of the attachment used in clients that
                don't show formatted text (eg. IRC, mobile notifications).
            fields: An array of AttachmentField objects that get displayed in a
                table-like way. For best results, include no more than 2-3 field
                objects.
            color: Changes the color of the border on the left side of this attachment
                from the default gray. Can either be one of "good" (green), "warning"
                (yellow), "danger" (red), or any hex color code (eg. #439FE0)
            markdown_in: An array of field names that should be formatted by
                markdown syntax - allowed values: "pretext", "text", "fields"
            title: Large title text near the top of the attachment.
            title_link: A valid URL that turns the title text into a hyperlink.
            pretext: Text that appears above the message attachment block. It can
                be formatted as plain text, or with markdown by including it in the
                markdown_in parameter.
            author_name: Small text used to display the author's name.
            author_link: A valid URL that will hyperlink the author_name text.
                Will only work if author_name is present.
            author_icon: A valid URL that displays a small 16px by 16px image to
                the left of the author_name text. Will only work if author_name is
                present.
            image_url: A valid URL to an image file that will be displayed at the
                bottom of the attachment. We support GIF, JPEG, PNG, and BMP formats.
                Large images will be resized to a maximum width of 360px or a maximum
                height of 500px, while still maintaining the original aspect ratio.
                Cannot be used with thumb_url.
            thumb_url: A valid URL to an image file that will be displayed as a
                thumbnail on the right side of a message attachment. We currently
                support the following formats: GIF, JPEG, PNG, and BMP. The thumbnail's
                longest dimension will be scaled down to 75px while maintaining the
                aspect ratio of the image. The filesize of the image must also be less
                than 500 KB. For best results, please use images that are already 75px
                by 75px.
            footer: Some brief text to help contextualize and identify an
                attachment. Limited to 300 characters, and may be truncated further when
                displayed to users in environments with limited screen real estate.
            footer_icon: A valid URL to an image file that will be displayed
                beside the footer text. Will only work if footer is present. We'll
                render what you provide at 16px by 16px. It's best to use an image that
                is similarly sized.
            ts: An integer Unix timestamp that is used to related your attachment
                to a specific time. The attachment will display the additional timestamp
                value as part of the attachment's footer. Your message's timestamp will
                be displayed in varying ways, depending on how far in the past or future
                 it is, relative to the present. Form factors, like mobile versus
                 desktop may also transform its rendered appearance.
        """
        self.text = text
        self.title = title
        self.fallback = fallback
        self.pretext = pretext
        self.title_link = title_link
        self.color = color
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.footer = footer
        self.footer_icon = footer_icon
        self.ts = ts
        self.fields = fields or []
        self.markdown_in = markdown_in or []

    @JsonValidator(f"footer attribute cannot exceed {footer_max_length} characters")
    def footer_length(self):
        return self.footer is None or len(self.footer) <= self.footer_max_length

    @JsonValidator("ts attribute cannot be present if footer attribute is absent")
    def ts_without_footer(self):
        return self.ts is None or self.footer is not None

    @EnumValidator("markdown_in", MarkdownFields)
    def markdown_in_valid(self):
        return not self.markdown_in or all(
            e in self.MarkdownFields for e in self.markdown_in
        )

    @JsonValidator(
        "color attribute must be 'good', 'warning', 'danger', or a hex color code"
    )
    def color_valid(self):
        return (
            self.color is None
            or self.color in SeededColors
            or re.match("^#(?:[0-9A-F]{2}){3}$", self.color, re.IGNORECASE)
        )

    @JsonValidator("image_url attribute cannot be present if thumb_url is populated")
    def image_url_and_thumb_url_populated(self):
        return self.image_url is None or self.thumb_url is None

    @JsonValidator("name must be present if link is present")
    def author_link_without_author_name(self):
        return self.author_link is None or self.author_name is not None

    @JsonValidator("icon must be present if link is present")
    def author_link_without_author_icon(self):
        return self.author_link is None or self.author_icon is not None

    def to_dict(self) -> dict:  # skipcq: PYL-W0221
        json = super().to_dict()
        if self.fields is not None:
            json["fields"] = extract_json(self.fields)
        if self.markdown_in:
            json["mrkdwn_in"] = self.markdown_in
        return json


class BlockAttachment(Attachment):
    attributes = {"color"}
    blocks: List[Block]

    def __init__(self, *, blocks: List[Block], color: Optional[str] = None):
        """
        A bridge between legacy attachments and blockkit formatting - pass a list of
        Block objects directly to this attachment.

        https://api.slack.com/reference/messaging/attachments#fields

        Args:
            blocks: a sequence of Block objects

            color: Changes the color of the border on the left side of this
                attachment from the default gray. Can either be one of "good" (green),
                "warning" (yellow), "danger" (red), or any hex color code (eg. #439FE0)
        """
        super().__init__(text="", color=color)
        self.blocks = list(blocks)

    @JsonValidator("fields attribute cannot be populated on BlockAttachment")
    def fields_attribute_absent(self):
        return not self.fields

    def to_dict(self) -> dict:
        json = super().to_dict()
        json.update({"blocks": extract_json(self.blocks)})
        del json["fields"]  # cannot supply fields and blocks at the same time
        return json


class InteractiveAttachment(Attachment):
    @property
    def attributes(self) -> Set[str]:
        return super().attributes.union({"callback_id"})

    actions_max_length = 5

    def __init__(
        self,
        *,
        actions: List[Action],
        callback_id: str,
        text: str,
        fallback: Optional[str] = None,
        fields: Optional[List[AttachmentField]] = None,
        color: Optional[str] = None,
        markdown_in: Optional[List[str]] = None,
        title: Optional[str] = None,
        title_link: Optional[str] = None,
        pretext: Optional[str] = None,
        author_name: Optional[str] = None,
        author_link: Optional[str] = None,
        author_icon: Optional[str] = None,
        image_url: Optional[str] = None,
        thumb_url: Optional[str] = None,
        footer: Optional[str] = None,
        footer_icon: Optional[str] = None,
        ts: Optional[int] = None,
    ):
        """
        An Attachment, but designed to contain interactive Actions
        Considered legacy - recommended replacement is to use message blocks instead.

        https://api.slack.com/docs/interactive-message-field-guide#attachment_fields

        https://api.slack.com/reference/messaging/attachments#fields

        Args:
            actions: A collection of Action objects to include in the attachment.
                Cannot exceed 5 elements.
            callback_id: The ID used to identify this attachment. Will be part of the
                payload sent back to your application.
            text: The main body text of the attachment. It can be formatted as
                plain text, or with markdown by including it in the markdown_in
                parameter. The content will automatically collapse if it contains 700+
                characters or 5+ linebreaks, and will display a "Show more..." link to
                expand the content.
            fallback: A plain text summary of the attachment used in clients that
                don't show formatted text (eg. IRC, mobile notifications).
            fields: An array of AttachmentField objects that get displayed in a
                table-like way. For best results, include no more than 2-3 field
                objects.
            color: Changes the color of the border on the left side of this attachment
                from the default gray. Can either be one of "good" (green), "warning"
                (yellow), "danger" (red), or any hex color code (eg. #439FE0)
            markdown_in: An array of field names that should be formatted by
                markdown syntax - allowed values: "pretext", "text", "fields"
            title: Large title text near the top of the attachment.
            title_link: A valid URL that turns the title text into a hyperlink.
            pretext: Text that appears above the message attachment block. It can
                be formatted as plain text, or with markdown by including it in the
                markdown_in parameter.
            author_name: Small text used to display the author's name.
            author_link: A valid URL that will hyperlink the author_name text.
                Will only work if author_name is present.
            author_icon: A valid URL that displays a small 16px by 16px image to
                the left of the author_name text. Will only work if author_name is
                present.
            image_url: A valid URL to an image file that will be displayed at the
                bottom of the attachment. We support GIF, JPEG, PNG, and BMP formats.
                Large images will be resized to a maximum width of 360px or a maximum
                height of 500px, while still maintaining the original aspect ratio.
                Cannot be used with thumb_url.
            thumb_url: A valid URL to an image file that will be displayed as a
                thumbnail on the right side of a message attachment. We currently
                support the following formats: GIF, JPEG, PNG, and BMP. The thumbnail's
                longest dimension will be scaled down to 75px while maintaining the
                aspect ratio of the image. The filesize of the image must also be less
                than 500 KB. For best results, please use images that are already 75px
                by 75px.
            footer: Some brief text to help contextualize and identify an
                attachment. Limited to 300 characters, and may be truncated further when
                displayed to users in environments with limited screen real estate.
            footer_icon: A valid URL to an image file that will be displayed
                beside the footer text. Will only work if footer is present. We'll
                render what you provide at 16px by 16px. It's best to use an image that
                is similarly sized.
            ts: An integer Unix timestamp that is used to related your attachment
                to a specific time. The attachment will display the additional timestamp
                value as part of the attachment's footer. Your message's timestamp will
                be displayed in varying ways, depending on how far in the past or future
                 it is, relative to the present. Form factors, like mobile versus
                 desktop may also transform its rendered appearance.
        """
        super().__init__(
            text=text,
            title=title,
            fallback=fallback,
            fields=fields,
            pretext=pretext,
            title_link=title_link,
            color=color,
            author_name=author_name,
            author_link=author_link,
            author_icon=author_icon,
            image_url=image_url,
            thumb_url=thumb_url,
            footer=footer,
            footer_icon=footer_icon,
            ts=ts,
            markdown_in=markdown_in,
        )
        self.callback_id = callback_id
        self.actions = actions or []

    @JsonValidator(f"actions attribute cannot exceed {actions_max_length} elements")
    def actions_length(self):
        return len(self.actions) <= self.actions_max_length

    def to_dict(self) -> dict:
        json = super().to_dict()
        json["actions"] = extract_json(self.actions)
        return json
