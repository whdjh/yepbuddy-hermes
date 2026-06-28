import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from hermes.hermes import (
    HermesContext,
    BrainTokens,
    TokenStore,
    ask_text,
    auth_url_text,
    build_authorization_url,
    ping_text,
    whoami_text,
)


class HermesTextTest(unittest.TestCase):
    def test_ping_text_names_hermes(self):
        context = HermesContext(user_id=123, chat_id=-100, message_thread_id=456)

        self.assertIn("Hermes", ping_text(context))
        self.assertIn("안드로이드 서버", ping_text(context))

    def test_whoami_text_includes_ids(self):
        context = HermesContext(user_id=123, chat_id=-100, message_thread_id=456)

        text = whoami_text(context)

        self.assertIn("user_id: 123", text)
        self.assertIn("chat_id: -100", text)
        self.assertIn("message_thread_id: 456", text)

    def test_build_authorization_url_contains_oauth_fields(self):
        url = build_authorization_url(
            auth_url="https://hermes.example/oauth/authorize",
            client_id="client-123",
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            scope="chat profile",
            state="state-123",
        )

        self.assertIn("response_type=code", url)
        self.assertIn("client_id=client-123", url)
        self.assertIn("redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob", url)
        self.assertIn("scope=chat+profile", url)
        self.assertIn("state=state-123", url)

    def test_auth_url_text_requires_config(self):
        text = auth_url_text(auth_url="", client_id="", redirect_uri="", scope="")

        self.assertIn("OPENAI_AUTH_URL", text)

    def test_auth_url_text_returns_url(self):
        text = auth_url_text(
            auth_url="https://hermes.example/oauth/authorize",
            client_id="client-123",
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            scope="chat",
        )

        self.assertIn("https://hermes.example/oauth/authorize", text)
        self.assertIn("브라우저", text)


class TokenStoreTest(unittest.TestCase):
    def test_token_store_round_trips_tokens(self):
        with TemporaryDirectory() as tmp:
            store = TokenStore(Path(tmp) / "tokens.json")
            tokens = BrainTokens(access_token="access", refresh_token="refresh", expires_in=3600)

            store.write(tokens)

            self.assertEqual(store.read(), tokens)


class FakeOpenAIBrain:
    async def ask(self, prompt: str) -> str:
        self.prompt = prompt
        return "hermes-ok"


class AsyncHermesTest(unittest.IsolatedAsyncioTestCase):
    async def test_ask_text_requires_prompt(self):
        response = await ask_text(None, "   ")

        self.assertIn("/ask 뒤에", response)

    async def test_ask_text_requires_brain(self):
        response = await ask_text(None, "hello")

        self.assertIn("/auth", response)

    async def test_ask_text_calls_brain(self):
        brain = FakeOpenAIBrain()

        response = await ask_text(brain, "hello")

        self.assertEqual(response, "hermes-ok")
        self.assertEqual(brain.prompt, "hello")


if __name__ == "__main__":
    unittest.main()
