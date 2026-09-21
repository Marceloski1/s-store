from dataclasses import dataclass

from shared.domain.validation import require_text

TESTIMONIAL_QUOTE_MAX_LENGTH = 500
TESTIMONIAL_AUTHOR_MAX_LENGTH = 100


@dataclass(frozen=True, slots=True)
class Testimonial:
    quote: str
    author: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "quote", require_text(self.quote, field="testimonial quote", max_length=TESTIMONIAL_QUOTE_MAX_LENGTH)
        )
        object.__setattr__(
            self,
            "author",
            require_text(self.author, field="testimonial author", max_length=TESTIMONIAL_AUTHOR_MAX_LENGTH),
        )
