# Android Server Telegram OpenAI Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a first-run Android server Termux harness that verifies Telegram bot connectivity and OpenAI API connectivity without storing secrets or runtime data outside the Android server phone.

**Architecture:** Keep Telegram-specific code in `bot.py`, add a small `harness.py` service layer for command responses and OpenAI test calls, and add shell scripts that make Android server setup repeatable. GitHub carries code only; `.env`, topic mappings, and JSONL records stay local on the Android server.

**Tech Stack:** Python 3.11+, python-telegram-bot 22.x, OpenAI Python SDK 2.x, Termux shell scripts, unittest.

---

### Task 1: Harness command service

**Files:**
- Create: `src/termux_telegram_assistant/harness.py`
- Test: `tests/test_harness.py`

- [x] **Step 1: Write failing tests**

```python
import unittest

from termux_telegram_assistant.harness import HarnessContext, ping_text, whoami_text


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
```

- [x] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_harness`
Expected: FAIL because `termux_telegram_assistant.harness` does not exist.

- [x] **Step 3: Write minimal implementation**

Create `HarnessContext`, `ping_text`, and `whoami_text`.

- [x] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python3 -m unittest tests.test_harness`
Expected: PASS.

### Task 2: OpenAI harness command

**Files:**
- Modify: `src/termux_telegram_assistant/harness.py`
- Test: `tests/test_harness.py`

- [x] **Step 1: Write failing tests**

```python
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
```

- [x] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_harness`
Expected: FAIL because `ai_text` does not exist.

- [x] **Step 3: Write minimal implementation**

Add `ai_text(client, prompt)` with missing prompt and missing API key messages.

- [x] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python3 -m unittest tests.test_harness`
Expected: PASS.

### Task 3: Telegram command wiring

**Files:**
- Modify: `src/termux_telegram_assistant/bot.py`

- [x] **Step 1: Add `/ping`, `/whoami`, and `/ai` handlers**

Use existing `_allow`, `_reply`, `actor_id`, and `settings.openai_api_key`.

- [x] **Step 2: Keep topic replies in the same Telegram topic**

Use existing `_reply`, which passes `message_thread_id` back to Telegram.

- [x] **Step 3: Run all unit tests**

Run: `PYTHONPATH=src python3 -m unittest discover -s tests`
Expected: PASS.

### Task 4: Android server scripts and beginner docs

**Files:**
- Create: `scripts/install_termux.sh`
- Create: `scripts/update_termux.sh`
- Create: `scripts/run_termux.sh`
- Modify: `README.md`
- Modify: `.env.example`

- [x] **Step 1: Add scripts**

Scripts should be short and readable: install packages/deps, update code/deps, and run the bot.

- [x] **Step 2: Rewrite README as A-Z Android-server-first guide**

Document Telegram-phone BotFather steps, GitHub code distribution, Android server Termux setup, topic id mapping, OpenAI harness test, data ownership, and update flow.

- [x] **Step 3: Run all unit tests**

Run: `PYTHONPATH=src python3 -m unittest discover -s tests`
Expected: PASS.
