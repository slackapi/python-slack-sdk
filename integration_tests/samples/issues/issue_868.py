import logging

logging.basicConfig(level=logging.DEBUG)


def legacy():
    from slack_sdk.models.blocks import SectionBlock
    from slack_sdk.models.blocks.basic_components import TextObject

    fields = []
    fields.append(TextObject(text="...", type="mrkdwn"))
    block = SectionBlock(text="", fields=fields)
    assert block is not None


from slack_sdk.models.blocks import SectionBlock, TextObject

fields = []
fields.append(TextObject(text="...", type="mrkdwn"))
block = SectionBlock(text="", fields=fields)
assert block is not None

#
# pip install mypy
# mypy integration_tests/samples/issues/issue_868.py | grep integration_tests
#

# integration_tests/samples/issues/issue_868.py:26: error: Argument "fields" to "SectionBlock" has incompatible type "List[TextObject]"; expected "Optional[List[Union[str, Dict[Any, Any], TextObject]]]"
# integration_tests/samples/issues/issue_868.py:26: note: "List" is invariant -- see http://mypy.readthedocs.io/en/latest/common_issues.html#variance
# integration_tests/samples/issues/issue_868.py:26: note: Consider using "Sequence" instead, which is covariant
