from guardrails import Guard, OnFailAction
from guardrails.hub import RestrictToTopic


guard = Guard(name="on_topic").use(
    RestrictToTopic,
    valid_topics=["pizza", "food", "restaurant"],
    invalid_topics=["politics", "religion", "school homework"],
    on_fail=OnFailAction.EXCEPTION
)