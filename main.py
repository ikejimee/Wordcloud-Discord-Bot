import re
import io
from wordcloud import WordCloud, STOPWORDS
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os 

# MODIFICATIONS: include multiple users, change font, change shape, colour palette 


load_dotenv() 
token = os.getenv('DISCORD_TOKEN')

# modify
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)  # define FIRST

# REGEX detectors
URL_REGEX = re.compile(r"https?://\S+")
MENTION_REGEX = re.compile(r"<@!?\d+>")
CHANNEL_REGEX = re.compile(r"<#\d+>")
ROLE_REGEX = re.compile(r"<@&\d+>")
EMOJI_REGEX = re.compile(r"<a?:\w+:\d+>")
CODEBLOCK_REGEX = re.compile(r"```.*?```", re.DOTALL) # re.DOTALL means the . matches everything including newline characters
INLINE_CODE_REGEX = re.compile(r"`[^`\n]+`")

REGEX_PATTERNS = [CODEBLOCK_REGEX, INLINE_CODE_REGEX, URL_REGEX, MENTION_REGEX, CHANNEL_REGEX, ROLE_REGEX, EMOJI_REGEX]

ADDITIONAL_STOPWORDS = {"https","http","www","com","jpg","png","gif","tenor", "rt","amp","lol","lmao","idk","im","dont","didnt","wa"}

def clean(text: str) -> str:
    """
    Detect unwanted character patterns and remove them

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    for pattern in REGEX_PATTERNS:
        text = pattern.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
    
def tokenize(text: str) -> list[str]:
    """Turns a string of text into a list of lowercase words

    Args:
        text (str): _description_

    Returns:
        List[str]: _description_
    """
    word_tokens = []
    for word in re.findall(r"[A-Za-z][A-Za-z'-]*", text):
        word_tokens.append(word.lower())
    return word_tokens

@bot.command(name="wordcloud", help="Generate a wordcloud of your messages in the server. Usage: !wordcloud [msgs_per_channel = 2000] [min_words=200]")
async def wordcloud_command(ctx, msgs_per_channel: int = 2000, min_words: int = 200):
    """_summary_

    Args:
        ctx (commands.Context): command context
        msgs_per_channel (int, optional): _description_. Defaults to 2000.
        min_words (int, optional): _description_. Defaults to 200.
    """
    msgs_per_channel = max(100, min(msgs_per_channel, 10000))
    min_words = max(50, min(min_words, 20000))
    
    author = ctx.author 
    guild = ctx.guild # guild is a discord server 
    
    if guild is None: # don't allow dms. ADD ERROR HANDLING
        return await ctx.reply("Use this in a server, not DMs.")
    
    
    text_chunks = []
    text_scanned = total_kept = 0 # for user info
    
    # Collect the readable channels for the bot
    readable_channels = []
    for channel in guild.text_channels:
        perms = channel.permissions_for(guild.me) # list of permissions for the bot in that channel
        if perms.view_channel and perms.read_message_history:
            readable_channels.append(channel)
    
    # sort channels by recent activity
    readable_channels.sort(key=lambda c: (c.last_message_id or 0), reverse=True)
    total_words = 0 
    
    async with ctx.typing():  # nice-to-have #1
        for channel in readable_channels:
            try:
                async for msg in channel.history(limit=msgs_per_channel, oldest_first=False):
                    text_scanned += 1
                    if msg.author.id != author.id: # only process messages for this specific author 
                        continue 
                    if not msg.content: # if the message is empty
                        continue 
                    
                    cleaned_msg = clean(msg.content)
                    if cleaned_msg:
                        text_chunks.append(cleaned_msg)
                        total_kept += 1
                        total_words += len(cleaned_msg.split())
                    
                    # Early stop   
                    if total_words >= max(min_words * 5 , 3000): # ensure there are enough tokens for wordcloud 
                        break
                        
                    
                # Early stop (maybe not needed)
                if total_words >= max(min_words * 5 , 3000): # ensure there are enough tokens for wordcloud 
                    break
            except discord.Forbidden: # encounter a channel that cannot be read
                continue 
            except discord.HTTPException:
                continue # other hiccup in the API
            
    
    if not text_chunks:
        return await ctx.reply("I couldn't find any recent messages from you. Socialise more!")
    
    overall_text = " ".join(text_chunks)
    words = tokenize(overall_text)
    if len(words) < min_words:
        return await ctx.reply(f"I only found {len(words)} words ... Try !wordcloud with lower parameters!")
    
    stopwords = STOPWORDS.union(ADDITIONAL_STOPWORDS)
    
    # generate the wordcloud
    wc = WordCloud(
                prefer_horizontal=0.95,
                colormap="cividis",
                background_color="white",
                height=600,
                width=1000,
                max_font_size=90,
                min_font_size=3,
                stopwords=stopwords,
                collocations = False # single words only
            ).generate(" ".join(words))

    # send the image to discord
    img_buffer = io.BytesIO()
    wc.to_image().save(img_buffer, format="PNG")
    img_buffer.seek(0) # reset the pointer to the start
    
    # user report   
    await ctx.reply(
    content=f"This is the wordcloud for {author.mention}. I scanned ~{text_scanned} messages; kept {total_kept}.",
    file=discord.File(fp=img_buffer, filename="wordcloud.png"))
    
if __name__ == "__main__":
    bot.run(token)

        