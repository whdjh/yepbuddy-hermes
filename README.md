# Termux Telegram 개인 비서 뼈대

Android Termux 단독 환경에서 실행하는 보안 중심 Telegram 그룹 Forum Topic 기반 개인 비서 프레임워크입니다.

봇은 Telegram 메시지를 받고, 보낸 사람이 허용 사용자 목록에 있는지 확인한 뒤, `message_thread_id`를 role 플러그인에 매핑합니다. 이후 role을 실행하고, 로컬 JSONL에 기록한 다음, 같은 topic으로 응답합니다.

## 현재 범위

- Android Termux에서 독립 Python 프로세스로 실행합니다.
- Telegram Group Forum Topic의 `message_thread_id`로 role을 라우팅합니다.
- role은 플러그인 방식으로 확장할 수 있게 분리했습니다.
- 초기 role은 stub입니다: `app_promo`, `health_research`, `ai_research`, `study_summary`, `ops_log`.
- 나중에 실제 AI role을 붙일 수 있도록 OpenAI 비동기 클라이언트 래퍼를 포함했습니다.
- 외부 Threads 게시 기능은 구현하지 않았습니다.
- 실행 기록은 `data/` 아래 JSONL로 저장합니다.
- `ALLOWED_USER_IDS`가 설정되지 않으면 모든 Telegram 업데이트를 거부합니다.

## 파일 구조

```text
.
├── .env.example
├── config/
│   └── topic_routes.example.json
├── data/
│   └── .gitkeep
├── src/termux_telegram_assistant/
│   ├── bot.py
│   ├── config.py
│   ├── openai_client.py
│   ├── router.py
│   ├── security.py
│   ├── storage.py
│   └── plugins/
│       ├── base.py
│       └── stubs.py
└── tests/
```

## Termux 설정

```bash
pkg update
pkg install python
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

로컬 설정 파일을 만듭니다:

```bash
cp .env.example .env
cp config/topic_routes.example.json config/topic_routes.json
```

`.env`는 사용자가 직접 로컬에서 편집합니다. 절대 커밋하지 마십시오.

필수 값:

- `TELEGRAM_BOT_TOKEN`: BotFather에서 받은 봇 토큰입니다.
- `OPENAI_API_KEY`: 나중에 실제 AI role에서 사용할 OpenAI API 키입니다.
- `ALLOWED_USER_IDS`: 봇 사용을 허용할 Telegram 숫자 user ID 목록입니다. 쉼표로 구분합니다.

`config/topic_routes.json`을 편집해 예시 key를 실제 forum topic의 `message_thread_id`로 바꿉니다.

## Topic ID 확인

봇을 Telegram forum group에 추가하고 필요한 권한만 부여한 뒤, 각 topic 안에서 아래 명령을 보냅니다:

```text
/topicid
```

봇이 현재 `message_thread_id`를 응답합니다. 그 값을 `config/topic_routes.json`에 넣으면 됩니다.

## 실행

```bash
. .venv/bin/activate
python -m termux_telegram_assistant
```

사용 가능한 명령:

- `/start`
- `/help`
- `/roles`
- `/topicid`

보낸 사람이 `ALLOWED_USER_IDS`에 없으면 모든 명령과 일반 메시지는 무시됩니다.

## Role 추가

`RolePlugin.handle(request, store)`를 구현하는 플러그인 클래스를 만들고 `default_plugins()`에 등록하면 됩니다. 나중에 필요하면 이 등록 방식을 동적 로더로 교체할 수 있습니다.

secret은 환경 변수로만 관리하십시오. 실행 결과는 `JsonlStore`를 통해 저장해 데이터가 로컬 JSON/JSONL로 남게 합니다.
