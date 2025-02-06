from typing import Optional

from guardrails import Guard, OnFailAction, register_validator
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
)
from transformers import pipeline



# Initialize the classifier using the zero-shot-classification pipeline
CLASSIFIER = pipeline(
    "zero-shot-classification",
    model='facebook/bart-large-mnli',
    hypothesis_template="This sentence above contains discussions of the folllowing topics: {}.",
    multi_label=True,
)


def detect_topics(
    text: str,
    topics: list[str],
    threshold: float = 0.8
) -> list[str]:
    result = CLASSIFIER(text, topics)
    return [topic
            for topic, score in zip(result["labels"], result["scores"])
            if score > threshold]


@register_validator(name="constrain_topic", data_type="string")
class ConstrainTopic(Validator):
    def __init__(
        self,
        banned_topics: Optional[list[str]] = ["politics"],
        threshold: float = 0.8,
        **kwargs
    ):
        self.topics = banned_topics
        self.threshold = threshold
        super().__init__(**kwargs)

    def _validate(
        self, value: str, metadata: Optional[dict[str, str]] = None
    ) -> ValidationResult:
        detected_topics = detect_topics(value, self.topics, self.threshold)
        if detected_topics:
            return FailResult(error_message="The text contains the following banned topics: "
                        f"{detected_topics}",
            )

        return PassResult()


guard = Guard(name='topic_guard').use(
    ConstrainTopic(
        banned_topics=["politics", "automobiles"],
        on_fail=OnFailAction.EXCEPTION,
    ),
)