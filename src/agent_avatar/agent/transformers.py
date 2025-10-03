from typing import AsyncIterator, Tuple, Callable, List
from functools import wraps
from .output_types import Actions, SentenceOutput, DisplayText
from ..utils.tts_preprocessor import tts_filter as filter_text
from ..live2d_model import Live2dModel
from ..config_manager import TTSPreprocessorConfig
from ..utils.sentence_divider import SentenceDivider
from ..utils.sentence_divider import SentenceWithTags, TagState
from loguru import logger

# Emotion extraction now handled per-sentence, no global state needed


def sentence_divider(
    faster_first_response: bool = True,
    segment_method: str = "pysbd",
    valid_tags: List[str] = None,
):
    """
    Decorator that transforms token stream into sentences with tags

    Args:
        faster_first_response: bool - Whether to enable faster first response
        segment_method: str - Method for sentence segmentation
        valid_tags: List[str] - List of valid tags to process
    """

    def decorator(
        func: Callable[..., AsyncIterator[str]],
    ) -> Callable[..., AsyncIterator[SentenceWithTags]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> AsyncIterator[SentenceWithTags]:
            divider = SentenceDivider(
                faster_first_response=faster_first_response,
                segment_method=segment_method,
                valid_tags=valid_tags or [],
            )
            token_stream = func(*args, **kwargs)
            async for sentence in divider.process_stream(token_stream):
                yield sentence
                logger.debug(f"sentence_divider: {sentence}")

        return wrapper

    return decorator


def actions_extractor(live2d_model: Live2dModel):
    """
    Decorator that extracts actions from sentences.
    For Agent-Zero integration, uses globally stored expressions.
    """

    def decorator(
        func: Callable[..., AsyncIterator[SentenceWithTags]],
    ) -> Callable[..., AsyncIterator[Tuple[SentenceWithTags, Actions]]]:
        @wraps(func)
        async def wrapper(
            *args, **kwargs
        ) -> AsyncIterator[Tuple[SentenceWithTags, Actions]]:
            sentence_stream = func(*args, **kwargs)
            last_emotion = [0]  # Track emotion context across sentences

            async for sentence in sentence_stream:
                actions = Actions()

                # Extract emotions from the current sentence text
                # This ensures each sentence gets its own appropriate emotion
                if not any(
                    tag.state in [TagState.START, TagState.END] for tag in sentence.tags
                ):
                    expressions = live2d_model.extract_emotion(sentence.text)
                    if expressions:
                        actions.expressions = expressions
                        last_emotion = expressions  # Remember this emotion for next sentence
                        logger.debug(f"Extracted expressions from sentence '{sentence.text[:50]}...': {expressions}")
                    else:
                        # Check if sentence contains emotion keywords (like "reflecting joy")
                        sentence_lower = sentence.text.lower()
                        if any(emotion_word in sentence_lower for emotion_word in ["joy", "happy", "smile", "laughter", "cheerful"]):
                            actions.expressions = [3]  # Joy expression (fixed mapping)
                            last_emotion = [3]
                            logger.debug(f"Inferred joy emotion from text content: '{sentence.text[:50]}...'")
                        elif any(emotion_word in sentence_lower for emotion_word in ["sad", "sadness", "sorrow", "grief"]):
                            actions.expressions = [1]  # Sadness expression (fixed mapping)
                            last_emotion = [1]
                            logger.debug(f"Inferred sadness emotion from text content: '{sentence.text[:50]}...'")
                        elif any(emotion_word in sentence_lower for emotion_word in ["anger", "angry", "mad", "furious"]):
                            actions.expressions = [2]  # Anger expression
                            last_emotion = [2]
                            logger.debug(f"Inferred anger emotion from text content: '{sentence.text[:50]}...'")
                        else:
                            # Use last emotion context instead of defaulting to neutral
                            actions.expressions = last_emotion
                            logger.debug(f"No emotion tags in sentence, using previous emotion context: {last_emotion}")

                logger.debug(f"EMOTION_DEBUG: Final actions for sentence '{sentence.text[:30]}...': expressions={actions.expressions}")
                yield sentence, actions

        return wrapper

    return decorator


def display_processor():
    """
    Decorator that processes text for display.
    """

    def decorator(
        func: Callable[..., AsyncIterator[Tuple[SentenceWithTags, Actions]]],
    ) -> Callable[..., AsyncIterator[Tuple[SentenceWithTags, DisplayText, Actions]]]:
        @wraps(func)
        async def wrapper(
            *args, **kwargs
        ) -> AsyncIterator[Tuple[SentenceWithTags, DisplayText, Actions]]:
            stream = func(*args, **kwargs)

            async for sentence, actions in stream:
                text = sentence.text

                # Remove emotion tags from display text
                emotion_tags = ['[neutral]', '[joy]', '[sadness]', '[anger]', '[surprise]', '[fear]', '[disgust]', '[smirk]']
                for tag in emotion_tags:
                    text = text.replace(tag, '').replace(tag.upper(), '').replace(tag.lower(), '')
                text = text.strip()

                # Handle think tag states
                for tag in sentence.tags:
                    if tag.name == "think":
                        if tag.state == TagState.START:
                            text = "("
                        elif tag.state == TagState.END:
                            text = ")"

                display = DisplayText(text=text)
                yield sentence, display, actions

        return wrapper

    return decorator


def tts_filter(
    tts_preprocessor_config: TTSPreprocessorConfig = None,
):
    """
    Decorator that filters text for TTS.
    Skips TTS for think tag content.
    """

    def decorator(
        func: Callable[
            ..., AsyncIterator[Tuple[SentenceWithTags, DisplayText, Actions]]
        ],
    ) -> Callable[..., AsyncIterator[SentenceOutput]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> AsyncIterator[SentenceOutput]:
            sentence_stream = func(*args, **kwargs)
            config = tts_preprocessor_config or TTSPreprocessorConfig()

            async for sentence, display, actions in sentence_stream:
                if any(tag.name == "think" for tag in sentence.tags):
                    tts = ""
                else:
                    tts = filter_text(
                        text=display.text,
                        remove_special_char=config.remove_special_char,
                        ignore_brackets=config.ignore_brackets,
                        ignore_parentheses=config.ignore_parentheses,
                        ignore_asterisks=config.ignore_asterisks,
                        ignore_angle_brackets=config.ignore_angle_brackets,
                    )

                logger.debug(f"[{display.name}] display: {display.text}")
                logger.debug(f"[{display.name}] tts: {tts}")

                yield SentenceOutput(
                    display_text=display,
                    tts_text=tts,
                    actions=actions,
                )

        return wrapper

    return decorator
