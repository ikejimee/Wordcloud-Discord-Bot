import re
import io
from wordcloud import WordCloud, STOPWORDS
from PIL import image 

# REGEX detectors
URL_REGEX = re.compile(r"https?://\S+")
MENTION_REGEX = re.compile(r"<@!?\d+>")
CHANNEL_REGEX = re.compile(r"<#\d+>")
ROLE_REGEX = re.compile(r"<@&\d+>")
EMOJI_REGEX = re.compile(r"<a?:\w+\d+>")
CODEBLOCK_REGEX = re.compile(r"```.*?```", re.DOTALL) # re.DOTALL means the . matches everything including newline characters
INLINE_CODE_REGEX = re.compile(r"`[^`]+`")

REGEX_NAMES = [CODEBLOCK_REGEX, INLINE_CODE_REGEX, URL_REGEX, MENTION_REGEX, CHANNEL_REGEX, ROLE_REGEX, EMOJI_REGEX]

ADDITIONAL_STOPWORDS = {"https","http","www","com","jpg","png","gif","tenor", "rt","amp","lol","lmao","idk","im","dont","didnt","wa"}

def clean(text: str) -> str:
    """
    Detect unwanted character patterns and remove them

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    for func in REGEX_NAMES:
        text = func.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
    
def tokenize(text: str) -> str:
    """Turns a string of text into a list of lowercase words

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    word_tokens = []
    for word in re.findall(r"[A-Za-z][A-Zz-a'-]*", text):
        word_tokens.append(word.lower())
    return word_tokens





        