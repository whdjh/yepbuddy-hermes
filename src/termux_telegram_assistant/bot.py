from __future__ import annotations

import logging

from telegram import Message, Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from termux_telegram_assistant.config import Settings, load_settings
from termux_telegram_assistant.harness import HarnessContext, ai_text, ping_text, whoami_text
from termux_telegram_assistant.openai_client import OpenAITextClient
from termux_telegram_assistant.plugins import RoleRequest, default_plugins
from termux_telegram_assistant.router import TopicRouter
from termux_telegram_assistant.security import actor_id, is_authorized
from termux_telegram_assistant.storage import JsonlStore


LOGGER = logging.getLogger(__name__)


class TelegramAssistant:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = JsonlStore(settings.data_dir)
        self.plugins = default_plugins()
        self.router = TopicRouter.from_file(settings.topic_routes_path, self.plugins)
        self.openai_client = (
            OpenAITextClient(api_key=settings.openai_api_key, model=settings.openai_model)
            if settings.openai_api_key
            else None
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._allow(update):
            return
        await self._reply(
            update.effective_message,
            "Termux Telegram 개인 비서가 실행 중입니다. 설정된 role은 /roles로 확인하십시오.",
            context,
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._allow(update):
            return
        await self._reply(
            update.effective_message,
            (
                "명령: /start, /help, /ping, /whoami, /topicid, /roles, /ai.\n"
                "일반 텍스트 메시지는 message_thread_id 기준으로 라우팅합니다."
            ),
            context,
        )

    async def ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._allow(update):
            return
        await self._reply(update.effective_message, ping_text(self._harness_context(update)), context)

    async def whoami(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._allow(update):
            return
        await self._reply(update.effective_message, whoami_text(self._harness_context(update)), context)

    async def ai(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._allow(update):
            return

        prompt = " ".join(context.args) if context.args else ""
        response = await ai_text(self.openai_client, prompt)
        await self._reply(update.effective_message, response, context)

    async def roles(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._allow(update):
            return

        route_lines = self.router.route_lines()
        routes = "\n".join(route_lines) if route_lines else "불러온 topic route가 없습니다."
        roles = ", ".join(self.router.roles())
        await self._reply(
            update.effective_message,
            f"사용 가능한 role: {roles}\n\nTopic route:\n{routes}",
            context,
        )

    async def topic_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._allow(update):
            return

        message = update.effective_message
        thread_id = message.message_thread_id if message else None
        await self._reply(message, f"message_thread_id: {thread_id}", context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._allow(update):
            return

        message = update.effective_message
        user_id = actor_id(update)
        if message is None or user_id is None or not message.text:
            return

        thread_id = message.message_thread_id
        route = self.router.resolve(thread_id)
        if route is None:
            self.store.append(
                "unrouted_messages",
                {
                    "chat_id": message.chat_id,
                    "message_thread_id": thread_id,
                    "user_id": user_id,
                    "message_id": message.message_id,
                    "text": message.text,
                },
            )
            await self._reply(
                message,
                (
                    "이 topic에 연결된 role이 없습니다. "
                    "config/topic_routes.json에 message_thread_id와 role을 매핑하세요."
                ),
                context,
            )
            return

        request = RoleRequest(
            role=route.role,
            chat_id=message.chat_id,
            message_thread_id=thread_id,
            user_id=user_id,
            text=message.text,
            message_id=message.message_id,
        )

        try:
            response = await route.plugin.handle(request, self.store)
        except Exception:
            LOGGER.exception("Role 플러그인 처리 실패: %s", route.role)
            self.store.append(
                "errors",
                {
                    "role": route.role,
                    "chat_id": message.chat_id,
                    "message_thread_id": thread_id,
                    "user_id": user_id,
                    "message_id": message.message_id,
                },
            )
            await self._reply(message, "role 처리 중 오류가 발생했습니다. 로컬 로그를 확인하세요.", context)
            return

        await self._reply(message, self._truncate(response.text), context)

    def _allow(self, update: Update) -> bool:
        if not is_authorized(update, self.settings.allowed_user_ids):
            self.store.append(
                "denied_updates",
                {
                    "user_id": actor_id(update),
                    "has_allowed_users": self.settings.has_allowed_users,
                },
            )
            return False
        return True

    def _truncate(self, text: str) -> str:
        if len(text) <= self.settings.reply_max_chars:
            return text
        return text[: self.settings.reply_max_chars - 20] + "\n...[잘림]"

    def _harness_context(self, update: Update) -> HarnessContext:
        message = update.effective_message
        return HarnessContext(
            user_id=actor_id(update),
            chat_id=message.chat_id if message else None,
            message_thread_id=message.message_thread_id if message else None,
        )

    async def _reply(self, message: Message | None, text: str, context: ContextTypes.DEFAULT_TYPE) -> None:
        if message is None:
            return

        kwargs = {
            "chat_id": message.chat_id,
            "text": self._truncate(text),
        }
        if message.message_thread_id is not None:
            kwargs["message_thread_id"] = message.message_thread_id
        await context.bot.send_message(**kwargs)


def build_application(settings: Settings | None = None) -> Application:
    settings = settings or load_settings()
    assistant = TelegramAssistant(settings)

    application = ApplicationBuilder().token(settings.telegram_bot_token).concurrent_updates(True).build()
    application.add_handler(CommandHandler("start", assistant.start))
    application.add_handler(CommandHandler("help", assistant.help))
    application.add_handler(CommandHandler("ping", assistant.ping))
    application.add_handler(CommandHandler("whoami", assistant.whoami))
    application.add_handler(CommandHandler("ai", assistant.ai))
    application.add_handler(CommandHandler("roles", assistant.roles))
    application.add_handler(CommandHandler("topicid", assistant.topic_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, assistant.handle_message))
    return application


def run() -> None:
    settings = load_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    if not settings.has_allowed_users:
        LOGGER.warning("ALLOWED_USER_IDS가 비어 있습니다. 모든 Telegram 업데이트를 거부합니다.")
    if not settings.topic_routes_path.exists():
        LOGGER.warning("Topic route 파일을 찾을 수 없습니다: %s", settings.topic_routes_path)

    build_application(settings).run_polling(allowed_updates=Update.ALL_TYPES)
