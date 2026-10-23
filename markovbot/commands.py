import re

from discord.ext.commands import BadArgument, Context, Converter, UserInputError, guild_only

from markovbot import markovbot, markov
from markovbot.seeder import seeder

_learning_guilds = set()


class UserIDConverter(Converter):
    """Resolve a user mention or ID without requiring a current guild member."""

    async def convert(self, ctx: Context, argument: str) -> int:
        match = re.fullmatch(r'(?:<@!?([0-9]{15,20})>|([0-9]{15,20}))', argument)
        if match is None:
            raise BadArgument('Expected a user mention or numeric user ID.')
        user_id = int(match.group(1) or match.group(2))
        if not 0 < user_id < 2 ** 64:
            raise BadArgument('Invalid user ID.')
        return user_id


@markovbot.command(
    help='Generate a sentence for this server, or select an author with a user mention or ID.',
    ignore_extra=False,
)
@guild_only()
async def say(ctx: Context, user_id: UserIDConverter = None):
    try:
        sentence = markov.make_sentence(ctx.guild, user_id)
        await ctx.channel.send(sentence)
    except markov.MarkovGenerationException:
        if user_id is None:
            await ctx.channel.send('Unable to generate sentence for your server. There are propably not enough messages.')
        else:
            await ctx.channel.send(
                'Unable to generate a sentence for that user in this server. '
                'Their chain may be missing or have too few messages. '
                'Use "!markov learn" to rebuild the chains.'
            )


@say.error
async def say_error(ctx: Context, error):
    if isinstance(error, UserInputError):
        await ctx.channel.send(
            'Use "!markov say" for this server, '
            'or "!markov say @user" / "!markov say USER_ID" for a user.'
        )
    else:
        raise error


@markovbot.command(help='Regenerate the Markov Chain for this server.')
@guild_only()
async def learn(ctx: Context):
    guild_id = ctx.guild.id
    if guild_id in _learning_guilds:
        return

    # Claim this guild before the first await so concurrent commands are ignored.
    _learning_guilds.add(guild_id)
    try:
        await ctx.channel.send('I am regenerating the Markov Chain. This may take a minute. I will let you know when I am done.')
        await seeder.reseed(ctx.guild)
        await ctx.channel.send('Chain has been regenerated! Use the "say" command to make me speak!')
    finally:
        _learning_guilds.remove(guild_id)
