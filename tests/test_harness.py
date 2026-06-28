import unittest

from termux_telegram_assistant.harness import HarnessContext, ai_text, ping_text, whoami_text


class HarnessTest(unittest.TestCase):
    def test_ping_text_names_android_harness(self):
        context = HarnessContext(user_id=123, chat_id=-100, message_thread_id=456)

        self.assertIn("안드로이드 서버 Telegram OpenAI 하네스", ping_text(context))

    def test_whoami_text_includes_ids(self):
        context = HarnessContext(user_id=123, chat_id=-100, message_thread_id=456)

        text = whoami_text(context)

        self.assertIn("user_id: 123", text)
        self.assertIn("chat_id: -100", text)
        self.assertIn("message_thread_id: 456", text)


class FakeOpenAIClient:
    async def respond(self, instructions: str, user_input: str) -> str:
        self.instructions = instructions
        self.user_input = user_input
        return "openai-ok"


class AsyncHarnessTest(unittest.IsolatedAsyncioTestCase):
    async def test_ai_text_requires_prompt(self):
        response = await ai_text(None, "   ")

        self.assertIn("/ai 뒤에", response)

    async def test_ai_text_requires_client(self):
        response = await ai_text(None, "hello")

        self.assertIn("OPENAI_API_KEY", response)

    async def test_ai_text_calls_client(self):
        client = FakeOpenAIClient()

        response = await ai_text(client, "hello")

        self.assertEqual(response, "openai-ok")
        self.assertEqual(client.user_input, "hello")
        self.assertIn("연결 확인", client.instructions)


if __name__ == "__main__":
    unittest.main()
