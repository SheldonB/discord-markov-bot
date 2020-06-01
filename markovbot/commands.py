from discord.ext.commands import Context

from markovbot import markovbot, markov, discord_utils
from markovbot.seeder import seeder

@markovbot.command(pass_context=True, help='Generate a sentence based of a Markov Chain')
async def say(ctx: Context, user: str = None):
    if user:
        user_id = discord_utils.extract_id_from_mention(user)
        print('User Id ' + str(user_id))
        mem = ctx.guild.get_member(user_id)
        print(mem)

    try:
        sentence = markov.make_sentence(ctx.guild)
        await ctx.channel.send(sentence)
    except markov.MarkovGenerationException:
        await ctx.channel.send('Unable to generate sentence for your server. There are propably not enough messages.')


@markovbot.command(pass_context=True, help='Regenerate the Markov Chain for this server.')
async def learn(ctx: Context):
    await ctx.channel.send('I am regenerating the Markov Chain. This may take a minute. I will let you know when I am done.')
    await seeder.reseed(ctx.guild)
    await ctx.channel.send('Chain has been regenerated! Use the "say" command to make me speak!')
