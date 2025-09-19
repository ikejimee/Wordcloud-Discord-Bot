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

