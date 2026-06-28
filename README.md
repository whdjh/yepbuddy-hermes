# Hermes

Hermes는 안드로이드 서버의 Termux에서 실행하고, 텔레그램용 핸드폰으로 조종하는 개인 비서입니다.

```text
텔레그램용 핸드폰
  -> Telegram bot으로 명령 전송

안드로이드 서버 Termux
  -> Hermes 프로세스 실행
  -> OpenAI OAuth token 저장
  -> 로컬 JSON/JSONL 저장
  -> Telegram으로 응답

OpenAI API
  -> OAuth로 연결되는 두뇌
```

GitHub에는 코드만 저장합니다. `.env`, `config/topic_routes.json`, `data/*.jsonl`, `data/openai_tokens.json`은 안드로이드 서버 로컬에만 둡니다.

## 현재 범위

- Telegram bot 연결 확인: `/ping`
- 내 Telegram user/topic 확인: `/whoami`, `/topicid`
- OpenAI OAuth 시작: `/auth`
- OpenAI OAuth code 저장: `/authcode <code>`
- OpenAI에게 질문: `/ask <질문>`
- topic route 기반 stub role 기록은 유지

## 1. Telegram bot 만들기

텔레그램용 핸드폰에서 `@BotFather`를 엽니다.

```text
/newbot
```

봇 이름과 username을 만들면 BotFather가 HTTP API token을 줍니다. 이 값은 안드로이드 서버 `.env`의 `TELEGRAM_BOT_TOKEN`에 넣습니다.

그룹 일반 메시지를 받게 하려면 privacy를 끕니다.

```text
/setprivacy
```

방금 만든 봇을 선택하고 `Disable`을 선택합니다.

## 2. 내 Telegram user id 확인

텔레그램용 핸드폰에서 `@userinfobot` 또는 `@RawDataBot`에 `/start`를 보냅니다.

나오는 숫자 ID를 기록합니다.

```text
123456789
```

이 값은 안드로이드 서버 `.env`의 `ALLOWED_USER_IDS`에 넣습니다. 비워 두면 Hermes는 모든 Telegram update를 거부합니다.

## 3. Mac에서 repo 준비

현재 GitHub repo는 `whdjh/yepbuddy-hermes`입니다.

기존 remote 확인:

```bash
git remote -v
```

remote가 다른 경로를 보고 있으면 바꾸기:

```bash
git remote set-url origin git@github.com:whdjh/yepbuddy-hermes.git
```

아직 remote가 없다면:

```bash
git remote add origin git@github.com:whdjh/yepbuddy-hermes.git
```

push:

```bash
git push -u origin main
```

HTTPS clone을 쓸 거면 remote URL은 `https://github.com/whdjh/yepbuddy-hermes.git`로 써도 됩니다.

## 4. 안드로이드 서버 Termux 설치

안드로이드 서버에서 Termux를 엽니다.

```bash
pkg update
pkg install git
git clone https://github.com/whdjh/yepbuddy-hermes.git
cd yepbuddy-hermes
bash scripts/install_termux.sh
```

설치가 끝나면 `.env`를 편집합니다.

```bash
nano .env
```

최소값:

```env
TELEGRAM_BOT_TOKEN=BotFather에서_받은_token
ALLOWED_USER_IDS=텔레그램용_핸드폰_Telegram_user_id

OPENAI_AUTH_URL=https://...
OPENAI_TOKEN_URL=https://...
OPENAI_CLIENT_ID=...
OPENAI_CLIENT_SECRET=...
OPENAI_REDIRECT_URI=urn:ietf:wg:oauth:2.0:oob
OPENAI_SCOPE=

OPENAI_API_BASE_URL=https://...
OPENAI_CHAT_PATH=/v1/chat/completions
OPENAI_MODEL=gpt-4.1-mini

TOPIC_ROUTES_PATH=config/topic_routes.json
DATA_DIR=data
LOG_LEVEL=INFO
REPLY_MAX_CHARS=3500
```

`nano` 저장은 `Ctrl+O`, Enter, 종료는 `Ctrl+X`입니다.

## 5. Hermes 실행

안드로이드 서버 Termux에서:

```bash
cd yepbuddy-hermes
bash scripts/run_termux.sh
```

처음에는 자동 실행보다 이 방식으로 연결부터 확인합니다. Termux가 켜져 있어야 Hermes가 동작합니다.

## 6. Telegram 연결 확인

텔레그램용 핸드폰에서 Hermes 봇 개인 DM에 보냅니다.

```text
/ping
```

정상 응답 예:

```text
Hermes가 안드로이드 서버에서 실행 중입니다.
user_id: 123456789
chat_id: -100...
message_thread_id: 123
```

내 id와 topic id 확인:

```text
/whoami
/topicid
```

개인 DM에서는 `message_thread_id: None`이 정상입니다. group/topic을 쓰지 않으면 `config/topic_routes.json`은 건드리지 않아도 됩니다.

## 7. OpenAI OAuth 연결

Hermes 봇 개인 DM에서:

```text
/auth
```

Hermes가 OpenAI OAuth 로그인 URL을 보냅니다. 텔레그램용 핸드폰 브라우저에서 열고 로그인합니다.

로그인 후 받은 OAuth code를 다시 Telegram으로 보냅니다.

```text
/authcode 받은_code
```

성공하면 token이 안드로이드 서버의 `data/openai_tokens.json`에 저장됩니다. 이 파일은 GitHub에 올라가지 않습니다.

## 8. OpenAI에게 질문

Hermes 봇 개인 DM에서:

```text
/ask 오늘 할 일을 세 줄로 정리해줘
```

OpenAI API 응답이 오면 연결 완료입니다.

`/ask`가 실패하면 먼저 아래를 확인합니다.

- `.env`의 `OPENAI_API_BASE_URL`
- `.env`의 `OPENAI_CHAT_PATH`
- `.env`의 `OPENAI_MODEL`
- `data/openai_tokens.json` 존재 여부
- Termux 로그

## 9. 데이터 확인

안드로이드 서버 Termux에서:

```bash
ls data
cat data/openai_tokens.json
cat data/role_events.jsonl
cat data/denied_updates.jsonl
```

`data/openai_tokens.json`은 secret입니다. 캡처하거나 GitHub에 올리지 마십시오.

## 10. Mac에서 개발한 뒤 안드로이드 서버에 반영

Mac:

```bash
git add .
git commit -m "feat: 변경 설명"
git push
```

안드로이드 서버 Termux:

```bash
cd yepbuddy-hermes
bash scripts/update_termux.sh
bash scripts/run_termux.sh
```

## 현재 명령

- `/start`: Hermes 시작 확인
- `/help`: 명령 목록
- `/ping`: Telegram 연결 확인
- `/whoami`: Telegram user id, chat id, topic id 확인
- `/topicid`: 현재 topic의 `message_thread_id` 확인
- `/auth`: OpenAI OAuth 로그인 URL 생성
- `/authcode <code>`: OpenAI OAuth token 저장
- `/ask <질문>`: OpenAI에게 질문
- `/roles`: topic route와 role 목록 확인
