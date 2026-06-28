# Yepbuddy Hermes

안드로이드 서버에서 공식 NousResearch Hermes Agent를 설치하고 실행하기 위한 bootstrap repo입니다.

이 repo는 Hermes 본체가 아닙니다. 직접 만든 Telegram bot/OAuth 코드는 제거했습니다. 실제 설치 대상은 공식 Hermes Agent입니다.

공식 문서:
- Termux 설치: https://hermes-agent.nousresearch.com/docs/getting-started/termux
- Hermes Agent docs: https://hermes-agent.nousresearch.com/docs

## 구조

```text
텔레그램용 핸드폰
  Hermes/Telegram gateway 조종용

안드로이드 서버 Termux
  공식 Hermes Agent 실행
  Nous Portal OAuth 로그인
  로컬 데이터와 설정 저장

Nous Portal / Hermes Agent
  OAuth, 모델 설정, 도구 gateway
```

OAuth는 로그인 방식입니다. OAuth 자체가 과금 상품은 아닙니다. 실제 모델 사용 비용이나 무료 제공 범위는 연결한 모델/provider 정책을 따릅니다.

## 1. 설치

안드로이드 서버 Termux에서:

```bash
git clone https://github.com/whdjh/yepbuddy-hermes.git
cd yepbuddy-hermes
bash scripts/install_android.sh
```

이 스크립트는 Termux 패키지를 설치한 뒤 공식 installer를 실행합니다.

공식 installer 명령:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

## 2. 상태 확인

```bash
bash scripts/doctor.sh
```

또는 직접:

```bash
hermes version
hermes doctor
```

## 3. OAuth / Portal 설정

```bash
bash scripts/setup_portal.sh
```

또는 직접:

```bash
hermes setup --portal
```

로그인 URL이 나오면 텔레그램용 핸드폰 브라우저에서 열어 로그인합니다. 안드로이드 서버는 Termux 실행과 token 저장을 담당합니다.

## 4. 실행

```bash
bash scripts/run_hermes.sh
```

또는 직접:

```bash
hermes
```

## 5. 업데이트

```bash
cd ~/yepbuddy-hermes
git pull
bash scripts/update_android.sh
```

## 안드로이드에서 다시 설치할 때

기존 bootstrap repo만 지우려면:

```bash
cd ~
rm -rf yepbuddy-hermes
```

Hermes Agent 자체 설정/캐시는 공식 Hermes Agent가 쓰는 위치에 남을 수 있습니다. 완전 삭제는 공식 uninstall 문서나 `hermes`가 제공하는 uninstall 명령을 확인한 뒤 진행하십시오.

## 지금 이 repo가 하지 않는 것

- 자체 Telegram bot 구현
- 자체 OAuth 서버 구현
- OpenAI API key 저장
- 직접 모델 API wrapping

이제 Hermes Agent 본체가 제공하는 기능을 그대로 사용합니다.
