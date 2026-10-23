import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from discord.ext.commands import BadArgument, TooManyArguments
from discord.ext.commands.view import StringView

from markovbot import markov
from markovbot.commands import learn, say, seeder


def get_context(guild_id=123):
    return SimpleNamespace(
        guild=SimpleNamespace(id=guild_id),
        channel=SimpleNamespace(send=AsyncMock()),
    )


class SayTest(unittest.IsolatedAsyncioTestCase):
    async def parse(self, argument):
        ctx = get_context()
        ctx.message = SimpleNamespace(attachments=[])
        ctx.view = StringView(argument)
        await say._parse_arguments(ctx)
        return ctx

    async def test_omitted_target_uses_server_chain(self):
        ctx = await self.parse('')
        with patch('markovbot.commands.markov.make_sentence', return_value='Server sentence') as generate:
            await say.callback(*ctx.args, **ctx.kwargs)

        generate.assert_called_once_with(ctx.guild, None)
        ctx.channel.send.assert_awaited_once_with('Server sentence')

    async def test_mention_or_id_selects_user_without_member_lookup(self):
        user_id = 123456789012345678
        for target in (str(user_id), f'<@{user_id}>', f'<@!{user_id}>'):
            with self.subTest(target=target):
                ctx = await self.parse(target)
                with patch('markovbot.commands.markov.make_sentence', return_value='User sentence') as generate:
                    await say.callback(*ctx.args, **ctx.kwargs)

                generate.assert_called_once_with(ctx.guild, user_id)
                ctx.channel.send.assert_awaited_once_with('User sentence')

    async def test_invalid_targets_are_usage_errors_without_server_fallback(self):
        for target in ('Alice', '<@&123456789012345678>', '<#123456789012345678>',
                       '123', '-123456789012345678', '99999999999999999999'):
            with self.subTest(target=target):
                ctx = get_context()
                ctx.message = SimpleNamespace(attachments=[])
                ctx.view = StringView(target)
                with patch('markovbot.commands.markov.make_sentence') as generate:
                    with self.assertRaises(BadArgument) as error:
                        await say._parse_arguments(ctx)
                    await say.on_error(ctx, error.exception)

                generate.assert_not_called()
                self.assertIn('!markov say USER_ID', ctx.channel.send.call_args.args[0])

    async def test_extra_arguments_are_rejected(self):
        with self.assertRaises(TooManyArguments):
            await self.parse('123456789012345678 another-user')

    async def test_unavailable_user_model_returns_targeted_error_without_fallback(self):
        ctx = get_context()
        with patch('markovbot.commands.markov.make_sentence', side_effect=markov.MarkovGenerationException) as generate:
            await say.callback(ctx, 123456789012345678)

        generate.assert_called_once_with(ctx.guild, 123456789012345678)
        ctx.channel.send.assert_awaited_once()
        self.assertIn('that user in this server', ctx.channel.send.call_args.args[0])

    async def test_unavailable_server_model_preserves_existing_error_message(self):
        ctx = get_context()
        with patch('markovbot.commands.markov.make_sentence', side_effect=markov.MarkovGenerationException):
            await say.callback(ctx)

        ctx.channel.send.assert_awaited_once_with(
            'Unable to generate sentence for your server. There are propably not enough messages.'
        )


class LearnTest(unittest.IsolatedAsyncioTestCase):
    async def test_duplicate_is_ignored_during_reseed_and_can_retry_after_completion(self):
        started = asyncio.Event()
        release = asyncio.Event()

        async def reseed(guild):
            started.set()
            await release.wait()

        first = get_context()
        duplicate = get_context()
        with patch.object(seeder, 'reseed', side_effect=reseed) as reseed_mock:
            task = asyncio.create_task(learn.callback(first))
            try:
                await asyncio.wait_for(started.wait(), timeout=1)
                await learn.callback(duplicate)
                duplicate.channel.send.assert_not_awaited()
                reseed_mock.assert_awaited_once_with(first.guild)
            finally:
                release.set()
                await task

            self.assertEqual(first.channel.send.await_count, 2)
            await learn.callback(duplicate)
            self.assertEqual(reseed_mock.await_count, 2)
            self.assertEqual(duplicate.channel.send.await_count, 2)

    async def test_duplicate_is_ignored_before_initial_message_finishes(self):
        started = asyncio.Event()
        release = asyncio.Event()

        async def send(message):
            started.set()
            await release.wait()

        first = get_context()
        first.channel.send.side_effect = send
        duplicate = get_context()
        with patch.object(seeder, 'reseed', new_callable=AsyncMock) as reseed_mock:
            task = asyncio.create_task(learn.callback(first))
            try:
                await asyncio.wait_for(started.wait(), timeout=1)
                await learn.callback(duplicate)
                duplicate.channel.send.assert_not_awaited()
                reseed_mock.assert_not_awaited()
            finally:
                release.set()
                await task

    async def test_other_guild_can_learn_while_first_guild_is_learning(self):
        started = asyncio.Event()
        release = asyncio.Event()

        async def reseed(guild):
            if guild.id == 123:
                started.set()
                await release.wait()

        with patch.object(seeder, 'reseed', side_effect=reseed) as reseed_mock:
            task = asyncio.create_task(learn.callback(get_context()))
            try:
                await asyncio.wait_for(started.wait(), timeout=1)
                other = get_context(456)
                await learn.callback(other)
                self.assertEqual(other.channel.send.await_count, 2)
                self.assertEqual(reseed_mock.await_count, 2)
                self.assertFalse(task.done())
            finally:
                release.set()
                await task

    async def test_can_retry_after_send_or_reseed_failure(self):
        for failure_stage in ('initial_message', 'reseed', 'completion_message'):
            with self.subTest(failure_stage=failure_stage):
                ctx = get_context()
                with patch.object(seeder, 'reseed', new_callable=AsyncMock) as reseed_mock:
                    error = RuntimeError('Learning failed')
                    if failure_stage == 'reseed':
                        reseed_mock.side_effect = error
                    elif failure_stage == 'initial_message':
                        ctx.channel.send.side_effect = error
                    else:
                        ctx.channel.send.side_effect = [None, error]

                    with self.assertRaises(RuntimeError):
                        await learn.callback(ctx)

                    reseed_mock.side_effect = None
                    reseed_mock.reset_mock()
                    retry = get_context()
                    await learn.callback(retry)
                    reseed_mock.assert_awaited_once_with(retry.guild)
                    self.assertEqual(retry.channel.send.await_count, 2)

    async def test_can_retry_after_cancellation(self):
        started = asyncio.Event()

        async def reseed(guild):
            started.set()
            await asyncio.Event().wait()

        with patch.object(seeder, 'reseed', side_effect=reseed) as reseed_mock:
            task = asyncio.create_task(learn.callback(get_context()))
            try:
                await asyncio.wait_for(started.wait(), timeout=1)
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task

            reseed_mock.side_effect = None
            reseed_mock.reset_mock()
            retry = get_context()
            await learn.callback(retry)
            reseed_mock.assert_awaited_once_with(retry.guild)
            self.assertEqual(retry.channel.send.await_count, 2)
