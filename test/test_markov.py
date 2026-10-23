import unittest
from types import SimpleNamespace
from unittest import mock

from markovbot.markov import CustomMarkovText, MarkovGenerationException, MarkovTrainingException, generate_chain, make_sentence
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

    def test_generate_chain_rejects_empty_or_unusable_corpora(self):
        for messages in ([], [SimpleNamespace(content='(no usable text)')]):
            with self.subTest(messages=messages):
                with self.assertRaises(MarkovTrainingException):
                    generate_chain(messages)

    def test_generate_chain_does_not_hide_unexpected_errors(self):
        with mock.patch.object(CustomMarkovText, 'sentence_split', side_effect=RuntimeError('Unexpected failure')):
            with self.assertRaises(RuntimeError):
                generate_chain([SimpleNamespace(content='Some valid text')])

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

    def test_make_sentence_selects_server_or_user_without_changing_generation_settings(self):
        guild = get_guild()
        for user_id in (None, 456):
            with self.subTest(user_id=user_id):
                model = mock.Mock()
                model.make_short_sentence.return_value = 'A generated sentence'
                with mock.patch('markovbot.markov.persistence.get_chain', return_value={'model': 'data'}) as get_chain:
                    with mock.patch.object(CustomMarkovText, 'from_dict', return_value=model):
                        self.assertEqual(make_sentence(guild, user_id), 'A generated sentence')
                get_chain.assert_called_once_with(guild, user_id)
                model.make_short_sentence.assert_called_once_with(500, min_chars=125, tries=300)

    def test_missing_chain_is_a_controlled_error(self):
        for user_id in (None, 456):
            with self.subTest(user_id=user_id):
                with mock.patch('markovbot.markov.persistence.get_chain', return_value=None) as get_chain:
                    with mock.patch.object(CustomMarkovText, 'from_dict') as from_dict:
                        with self.assertRaises(MarkovGenerationException):
                            make_sentence(get_guild(), user_id)
                get_chain.assert_called_once_with(get_guild(), user_id)
                from_dict.assert_not_called()


if __name__ == '__main__':
    unittest.main()
