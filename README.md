# Yepbuddy Android Server Telegram OpenAI Harness

안드로이드 서버의 Termux에서 실행하는 Telegram + OpenAI 연결 확인용 하네스입니다.

처음 목표는 기능 많은 비서가 아닙니다. 먼저 아래 세 가지가 되는지 확인합니다.

- 텔레그램용 핸드폰에서 보낸 메시지를 안드로이드 서버의 Termux 봇 프로세스가 받는다.
- 봇이 같은 Telegram topic으로 응답한다.
- `/ai` 명령으로 안드로이드 서버 안의 `OPENAI_API_KEY`를 써서 OpenAI 응답을 받는다.

## 역할 분리

```text
Mac
  코드 개발, git commit, GitHub push

GitHub
  코드 설치 링크 역할
  secret과 runtime data는 저장하지 않음

Android server Termux
  실제 봇 실행 서버
  .env, config/topic_routes.json, data/*.jsonl 저장
  Telegram polling과 OpenAI API 호출

Telegram phone
  BotFather 설정
  Telegram group/topic 생성
  /ping, /whoami, /topicid, /ai 테스트
```

## 1. 텔레그램용 핸드폰에서 Telegram 봇 만들기

텔레그램용 핸드폰에서 `@BotFather`를 엽니다.

```text
/newbot
```

이름과 username을 정하면 BotFather가 token을 줍니다. 이 값은 나중에 안드로이드 서버 `.env`의 `TELEGRAM_BOT_TOKEN`에 넣습니다.

그룹에서 일반 메시지를 받게 하려면 BotFather에서 privacy를 끕니다.

```text
/setprivacy
```

방금 만든 봇을 선택한 뒤 `Disable`을 선택합니다.

## 2. 텔레그램용 핸드폰에서 내 Telegram user id 확인

텔레그램용 핸드폰에서 `@userinfobot` 또는 `@RawDataBot`에 `/start`를 보냅니다.

나오는 숫자 ID를 기록합니다.

예:

```text
123456789
```

이 값은 안드로이드 서버 `.env`의 `ALLOWED_USER_IDS`에 넣습니다. 이 값이 비어 있으면 봇은 모든 메시지를 거부합니다.

## 3. Mac에서 GitHub에 코드 올리기

Mac에서 이 저장소를 GitHub에 올립니다.

```bash
git remote add origin https://github.com/<github-id>/yepbuddy-harness.git
git branch -M main
git push -u origin main
```

처음에는 public repo가 가장 단순합니다. private repo도 가능하지만 안드로이드 서버 Termux에서 GitHub 인증 설정이 추가로 필요합니다.

GitHub에는 코드만 올라갑니다. `.env`, `config/topic_routes.json`, `data/*.jsonl`은 `.gitignore`로 제외됩니다.

## 4. 안드로이드 서버 Termux 설치

안드로이드 서버에서 Termux를 엽니다.

```bash
pkg update
pkg install git
git clone https://github.com/<github-id>/yepbuddy-harness.git
cd yepbuddy-harness
bash scripts/install_termux.sh
```

설치가 끝나면 `.env`를 편집합니다.

```bash
nano .env
```

최소로 채울 값:

```env
TELEGRAM_BOT_TOKEN=BotFather에서_받은_토큰
OPENAI_API_KEY=OpenAI_API_키
ALLOWED_USER_IDS=텔레그램용_핸드폰_Telegram_user_id
OPENAI_MODEL=gpt-4.1-mini
TOPIC_ROUTES_PATH=config/topic_routes.json
DATA_DIR=data
LOG_LEVEL=INFO
REPLY_MAX_CHARS=3500
```

`nano` 저장은 `Ctrl+O`, Enter, 종료는 `Ctrl+X`입니다.

## 5. 텔레그램용 핸드폰에서 Telegram 그룹과 topic 만들기

텔레그램용 핸드폰에서 새 group을 만들고 봇을 초대합니다.

그룹 설정에서 Topics 또는 Forum 기능을 켭니다. 그 다음 테스트용 topic을 하나 만듭니다.

예:

```text
ai-harness
```

## 6. 안드로이드 서버에서 봇 실행

안드로이드 서버 Termux에서:

```bash
cd yepbuddy-harness
bash scripts/run_termux.sh
```

터미널이 계속 켜져 있어야 봇이 동작합니다. 처음에는 자동 실행보다 이 방식으로 연결부터 확인합니다.

## 7. 텔레그램용 핸드폰에서 하네스 연결 확인

Telegram group topic 안에서 아래 명령을 보냅니다.

```text
/ping
```

정상 응답 예:

```text
안드로이드 서버 Telegram OpenAI 하네스가 연결되어 있습니다.
user_id: 123456789
chat_id: -100...
message_thread_id: 123
```

내 user id와 topic id를 확인하려면:

```text
/whoami
/topicid
```

`/topicid` 응답의 `message_thread_id`를 안드로이드 서버의 route 파일에 넣습니다.

```bash
nano config/topic_routes.json
```

예:

```json
{
  "description": "안드로이드 서버 Termux 로컬 파일입니다. GitHub에 올리지 않습니다.",
  "default_role": "ops_log",
  "routes": {
    "123": "ai_research"
  }
}
```

수정 후 안드로이드 서버에서 봇을 껐다가 다시 켭니다.

```bash
bash scripts/run_termux.sh
```

## 8. OpenAI 연결 확인

텔레그램용 핸드폰의 Telegram topic에서:

```text
/ai 안녕. 한 문장으로 연결 확인해줘.
```

OpenAI 응답이 오면 Telegram + 안드로이드 서버 Termux + OpenAI 하네스 연결이 된 것입니다.

`OPENAI_API_KEY`가 비어 있으면 봇은 키를 확인하라는 메시지를 보냅니다.

## 9. 데이터 확인

안드로이드 서버 Termux에서:

```bash
ls data
cat data/role_events.jsonl
cat data/denied_updates.jsonl
```

`data/*.jsonl` 파일은 안드로이드 서버 안에만 저장됩니다. GitHub에 올라가지 않습니다.

## 10. Mac에서 개발한 뒤 안드로이드 서버에 반영

Mac에서 기능을 개발하고 push합니다.

```bash
git add .
git commit -m "feat: 새 기능 설명"
git push
```

안드로이드 서버 Termux에서는 최신 코드만 받습니다.

```bash
cd yepbuddy-harness
bash scripts/update_termux.sh
```

그 다음 다시 실행합니다.

```bash
bash scripts/run_termux.sh
```

## 현재 명령

- `/start`: 봇 시작 확인
- `/help`: 명령 목록
- `/ping`: 안드로이드 서버 Telegram OpenAI 하네스 연결 확인
- `/whoami`: Telegram user id, chat id, topic id 확인
- `/topicid`: 현재 topic의 `message_thread_id` 확인
- `/roles`: topic route와 role 목록 확인
- `/ai 텍스트`: OpenAI API 연결 확인

## 다음 단계

이 하네스가 붙으면 다음 작업은 실제 프롬프팅 계층과 장기 thread 저장 계층입니다.

순서는 다음이 안전합니다.

1. Telegram + OpenAI 하네스 연결 확인
2. role별 prompt 설계
3. 안드로이드 서버 로컬 thread/session 저장 설계
4. OpenAI Threads 또는 Responses 기반 대화 유지 연결
5. Termux 장기 실행 안정화
