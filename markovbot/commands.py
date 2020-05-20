from discord.ext.commands import Context

from markovbot import markovbot, markov

@markovbot.command(pass_context=True)
async def say(ctx: Context):
    try:
        sentence = markov.make_sentence(ctx.guild)
        await ctx.channel.send(sentence)
    except markov.MarkovGenerationException:
        await ctx.channel.send('Unable to generate sentence for your server. There are propably not enough messages.')