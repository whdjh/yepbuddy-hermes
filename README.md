# 안드로이드 기기 기반 Hermes Agent

남는 안드로이드 기기에서 Hermes Agent를 실행하고 GPT Codex를 연결해, Telegram을 통해 개인 AI Agent로 사용하고 있습니다.

![전체 구조](./assets/architecture.png)

## 만든 이유

Threads에 개발 카드뉴스와 기술 글을 직접 제작해 올리며 **지인 유입 없이 약 한 달 만에 팔로워 300명**을 만들었습니다.

직접 운영하면서 카드뉴스 형식에 대한 반응을 확인했지만, 내용을 정리하고 카드뉴스와 글을 각각 만들고 게시하는 과정이 반복됐습니다.

이 과정을 줄이기 위해 남는 안드로이드 기기를 활용해 개인 AI Agent 환경을 구성하고, 콘텐츠 제작부터 게시까지 자동화하고 있습니다.

## 직접 운영 결과

실제로 제작해 게시한 카드뉴스입니다.

![Threads 카드뉴스](./assets/threads-cardnews.png)

게시 후 받은 실제 반응입니다.

![Threads 반응](./assets/threads-feedback.png)

카드뉴스를 직접 운영하며 콘텐츠 형식의 가능성을 확인했고, 반복되는 제작 과정을 자동화할 가치가 있다고 판단했습니다.

## 현재 구성

- [x] 안드로이드 기기에서 Termux와 Hermes Agent 실행
- [x] Hermes Agent와 GPT Codex 연결
- [x] Telegram을 통해 Agent 사용
- [x] Threads API 인증 및 텍스트 게시 검증
- [ ] 이미지 게시 및 사용자 승인 후 게시 흐름

## 자동화 방향

직접 정리한 내용을 Telegram으로 전달하면 Hermes가 카드뉴스와 Threads 글을 생성하고, 결과를 확인·수정한 뒤 **사용자가 승인한 콘텐츠만 게시**하는 흐름을 구성하고 있습니다.

이후에는 Threads의 헬스·운동 관련 게시글을 주기적으로 수집하고 정리해 YepBuddy의 기능 아이디어와 콘텐츠·광고 소재를 제안하는 방향으로 확장할 예정입니다.