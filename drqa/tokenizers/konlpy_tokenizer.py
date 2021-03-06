from konlpy.tag import Twitter
from drqa.tokenizers.tokenizer import Tokens, Tokenizer
import logging

logger = logging.getLogger(__name__)

class KoNLPyTokenizer(Tokenizer):

    def __init__(self, **kwargs):
        self.twitter = Twitter()
        if len(kwargs.get('annotators', {})) > 0:
            logger.warning('%s only tokenizes! Skipping annotators: %s' % (type(self).__name__, kwargs.get('annotators')))
        self.annotators = set()

    def tokenize(self, text):
        """Given raw text, output a list of token data tuples."""
        # ... Tokenize text
        tokenizer = self.twitter
        tokens = [token[0] for token in tokenizer.pos(text)]
        
        # Format each token as a tuple of:
        # (token text, (start offset, end offset))
        # Return list of tuples
        i, past, tuples = 0, 0, []
        for token in tokens:
            if text[0] == " ":
                # Get rid of white space from tokens
                text = text[1:]
                past += 1
            start = text.find(token[0]) + past
            end = text.find(token[len(token) - 1]) + past
            tuples.append((token, token, (start, end + 1)))

            # Cut down processed token from original text but remember
            # length to keep track of indices
            text = text[len(token):]
            past += len(token)
            i += 1
        return Tokens(tuples, self.annotators)

    def untokenize(self, tokens):
        """Given the output list of tokenize, return the original
        text. This should work for slices of the token list as well.
        """
        rawText = ""
        previous_token_end = 0
        for token in tokens:
            if previous_token_end != token[2][0]:
                rawText += " "
            rawText += token[0]
        return rawText
