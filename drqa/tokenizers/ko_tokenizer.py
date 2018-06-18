#!/usr/bin/env python3
"""Simple regex based tokenizer."""

import regex
import logging
from drqa.tokenizers.tokenizer import Tokens, Tokenizer

logger = logging.getLogger(__name__)


class KoreanTokenizer(Tokenizer):
    # Matches numbers like "10", "1:00", "1,000", "100.00"
    DIGIT = r'\p{Nd}+([:\.\,]\p{Nd}+)*'

    # Matches double or single quotation marks that start new lines or
    # are preceded by space or opening brackets/parentheses. They also must be
    # followed by non-space.
    START_DQUOTE = r'(?<=[\p{Z}\(\[{<]|^)(``|["\u0093\u201C\u00AB])(?!\p{Z})'
    START_SQUOTE = r'(?<=[\p{Z}\(\[{<]|^)[\'\u0091\u2018\u201B\u2039](?!\p{Z})'

    # Matches double or single quotation marks that are preceded by non-space.
    END_DQUOTE = r'(?<!\p{Z})(\'\'|["\u0094\u201D\u00BB])'
    END_SQUOTE = r'(?<!\p{Z})[\'\u0092\u2019\u203A]'

    # Matches three dots in a row (ellipses)
    ELLIPSES = r'\.\.\.|\u2026'

    # Matches all unicode punctuation characters
    PUNCT = r'\p{P}'

    # Matches all unicode symbol characters
    SYM = r'\p{S}'

    # Anything else but space, punctuation, or control characters.
    NON_WS = r'[^\p{Z}\p{C}\p{P}]++'

    def __init__(self, **kwargs):
        """
        Args:
            annotators: None or empty set (only tokenizes).
            substitutions: if true, normalizes some token types (e.g. quotes).
        """

        # This regex will try to match (in order and and then pause) digits,
        # start/end quotes, ellipses, punctuation (single), non-space (multiple)
        self._regexp = regex.compile(
            '(?P<digit>%s)|(?P<sdquote>%s)|(?P<edquote>%s)|(?P<ssquote>%s)|'
            '(?P<esquote>%s)|(?<ellipses>%s)|(?P<punct>%s)|(?P<sym>%s)|'
            '(?P<nonws>%s)' %
            (self.DIGIT, self.START_DQUOTE, self.END_DQUOTE, self.START_SQUOTE,
             self.END_SQUOTE, self.ELLIPSES, self.PUNCT, self.SYM, self.NON_WS),
            flags=regex.IGNORECASE + regex.UNICODE + regex.MULTILINE
        )
        if len(kwargs.get('annotators', {})) > 0:
            logger.warning('%s only tokenizes! Skipping annotators: %s' %
                           (type(self).__name__, kwargs.get('annotators')))
        self.annotators = set()
        self.substitutions = kwargs.get('substitutions', True)

    def tokenize(self, text):
        data = []
        matches = [m for m in self._regexp.finditer(text)]
        for i in range(len(matches)):
            # Get text
            token = matches[i].group()

            # Make normalizations for special token types
            if self.substitutions:
                groups = matches[i].groupdict()
                if groups['sdquote']:
                    token = "``"
                elif groups['edquote']:
                    token = "''"
                elif groups['ssquote']:
                    token = "`"
                elif groups['esquote']:
                    token = "'"
                elif groups['ellipses']:
                    token = '...'

            # Get whitespace
            span = matches[i].span()
            start_ws = span[0]
            if i + 1 < len(matches):
                end_ws = matches[i + 1].span()[0]
            else:
                end_ws = span[1]

            # Format data
            data.append((
                token,
                text[start_ws: end_ws],
                span,
            ))
        return Tokens(data, self.annotators)


if __name__ == "__main__":
    # Testing
    tok = KoreanTokenizer()

    # Numbers that should be one unit
    txt = "1234 1.234 12:34 1,234"
    expected = ["1234", "1.234", "12:34", "1,234"]
    assert(tok.tokenize(txt).words() == expected)

    # Numbers that should not be one unit
    txt = "123, 123. 123: .123 $1.00"
    expected = ["123", ",", "123", ".", "123", ":", ".", "123", "$", "1.00"]
    assert(tok.tokenize(txt).words() == expected)

    # Start/end double quotes
    txt = "I said, \"Hello World\"."
    expected = ["I", "said", ",", "``", "Hello", "World", "''", "."]
    assert(tok.tokenize(txt).words() == expected)

    # Start/end single quotes
    txt = "I said, \'Hello World\'."
    expected = ["I", "said", ",", "`", "Hello", "World", "'", "."]
    assert(tok.tokenize(txt).words() == expected)

    # Punctuation
    txt = "!#$%&()*+,-./:;<=>?@[\\]^_{|}~"
    expected = list(txt)
    assert(tok.tokenize(txt).words() == expected)

    # Random stuff
    txt = "abc abc123 ... 생산에는"
    expected = ["abc", "abc123", "...", "생산에는"]
    assert(tok.tokenize(txt).words() == expected)

    # Make sure we get back what we put in
    assert(tok.tokenize(txt).untokenize() == txt)

    print('Tests passed.')
