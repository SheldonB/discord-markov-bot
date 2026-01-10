import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

if "discord" not in sys.modules:
    discord_stub = types.ModuleType("discord")
    discord_stub.Message = type("Message", (), {})
    discord_stub.Guild = type("Guild", (), {})
    sys.modules["discord"] = discord_stub

if "markovbot" not in sys.modules:
    markovbot_pkg = types.ModuleType("markovbot")
    markovbot_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "markovbot")]
    sys.modules["markovbot"] = markovbot_pkg

from markovbot.markov import CustomMarkovText, MarkovGenerationException, generate_chain, make_sentence
from .utils import get_guild


class MarkovTest(unittest.TestCase):

    def test_prepare_text_trims_whitespace_and_appends_punctuation(self):
        text = "  Hello world  "

        result = CustomMarkovText(["seed"])._prepare_text(text)

        self.assertEqual(result, "Hello world.")

    def test_prepare_text_keeps_trailing_punctuation(self):
        text = "Hello world!"

        result = CustomMarkovText(["seed"])._prepare_text(text)

        self.assertEqual(result, "Hello world!")

    def test_sentence_split_calls_prepare_text_and_returns_sentences(self):
        markov_text = CustomMarkovText(["seed"])

        with mock.patch.object(markov_text, "_prepare_text", return_value="Hi there.") as prepare_mock:
            with mock.patch("markovbot.markov.markovify.split_into_sentences", return_value=["Hi there."]):
                result = markov_text.sentence_split("  Hi there  ")

        prepare_mock.assert_called_once_with("  Hi there  ")
        self.assertEqual(result, ["Hi there."])

    def test_generate_chain_returns_custom_markov_text(self):
        messages = [SimpleNamespace(content="Hello there")]

        result = generate_chain(messages)

        self.assertIsInstance(result, CustomMarkovText)

    def test_make_sentence_success(self):
        guild = get_guild()
        chain_dict = {"state": "data"}
        chain_mock = mock.Mock()
        chain_mock.make_short_sentence.return_value = "Generated sentence"

        with mock.patch("markovbot.markov.persistence.get_chain", return_value=chain_dict):
            with mock.patch.object(CustomMarkovText, "from_dict", return_value=chain_mock) as from_dict_mock:
                result = make_sentence(guild)

        from_dict_mock.assert_called_once_with(chain_dict)
        chain_mock.make_short_sentence.assert_called_once_with(500, min_chars=125, tries=300)
        self.assertEqual(result, "Generated sentence")

    def test_make_sentence_failure_raises_exception(self):
        guild = get_guild()
        chain_dict = {"state": "data"}
        chain_mock = mock.Mock()
        chain_mock.make_short_sentence.return_value = None

        with mock.patch("markovbot.markov.persistence.get_chain", return_value=chain_dict):
            with mock.patch.object(CustomMarkovText, "from_dict", return_value=chain_mock):
                with self.assertRaises(MarkovGenerationException):
                    make_sentence(guild)

        chain_mock.make_short_sentence.assert_called_once_with(500, min_chars=125, tries=300)


if __name__ == '__main__':
    unittest.main()
