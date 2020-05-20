from discord.ext.commands import Context

from markovbot import markovbot, markov

@markovbot.command(pass_context=True)
async def say(ctx: Context):
    sentence = markov.make_sentence(ctx.guild)
    await ctx.channel.send(sentence)