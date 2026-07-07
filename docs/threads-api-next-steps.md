# Threads API 다음 작업 정리

## 현재 완료된 것

- Meta Developer 앱 `yepbuddy` 생성 완료
- Threads API 액세스 이용 사례 추가 완료
- OAuth 콜백 URL 저장 완료
  - `https://yepbuddy.co.kr/`
- Threads 테스터 초대 및 수락 완료
- OAuth authorization code 발급 완료
- short-lived access token 발급 완료
- long-lived access token 발급 완료
- Threads 텍스트 게시용 컨테이너 생성 성공
- Threads 텍스트 게시 성공

## 중요한 보안 조치

설정 중 앱 시크릿과 access token이 채팅에 노출됐기 때문에, 실제 자동화를 만들기 전에 반드시 재발급해야 한다.

해야 할 일:

1. Meta 앱 시크릿 재설정
2. OAuth 승인 다시 진행
3. short-lived access token 재발급
4. long-lived access token 재발급
5. 기존에 노출된 토큰은 더 이상 사용하지 않기

시크릿과 토큰은 git에 올리면 안 된다. 로컬 `.env`나 안전한 secret 저장소에만 보관한다.

로컬에 보관할 값 예시:

```env
THREADS_APP_ID=...
THREADS_APP_SECRET=...
THREADS_USER_ID=...
THREADS_ACCESS_TOKEN=...
```

## 내일 첫 목표

Threads API로 이미지 게시가 되는지 확인한다.

Threads 이미지 게시에는 로컬 파일이 아니라 외부에서 접근 가능한 public image URL이 필요하다. Yepbuddy는 Netlify에 배포되어 있으므로, 먼저 정적 테스트 이미지를 올려서 확인한다.

## 1단계: Netlify 사이트에 테스트 이미지 추가

Yepbuddy 프론트엔드 프로젝트에 테스트 이미지를 추가한다.

```text
public/thread-test.png
```

그다음 Netlify에 배포한다.

배포 후 브라우저에서 아래 URL이 바로 열리는지 확인한다.

```text
https://yepbuddy.co.kr/thread-test.png
```

이미지가 로그인 없이 바로 보여야 한다. 리다이렉트되거나 접근이 막히면 Threads API에서 사용할 수 없다.

## 2단계: Threads 이미지 컨테이너 생성

보안 조치 후 새로 발급한 long-lived token을 사용한다.

```bash
curl -X POST "https://graph.threads.net/v1.0/$THREADS_USER_ID/threads" \
  -d "media_type=IMAGE" \
  -d "image_url=https://yepbuddy.co.kr/thread-test.png" \
  -d "text=Yepbuddy image post test" \
  -d "access_token=$THREADS_ACCESS_TOKEN"
```

성공하면 이런 응답이 나온다.

```json
{
  "id": "CREATION_ID"
}
```

이 값은 실제 게시물 ID가 아니라 게시 대기 컨테이너 ID다.

로컬에 이렇게 저장한다.

```env
THREADS_CREATION_ID=...
```

## 3단계: 이미지 컨테이너 게시

```bash
curl -X POST "https://graph.threads.net/v1.0/$THREADS_USER_ID/threads_publish" \
  -d "creation_id=$THREADS_CREATION_ID" \
  -d "access_token=$THREADS_ACCESS_TOKEN"
```

성공하면 이런 응답이 나온다.

```json
{
  "id": "POST_ID"
}
```

그다음 Threads 앱에서 이미지 게시물이 실제로 올라갔는지 확인한다.

## 4단계: 카드뉴스 이미지 저장소 결정

Netlify 정적 파일은 테스트에는 충분하지만, 나중에 Hermes가 생성한 카드뉴스 이미지를 매번 올리려면 업로드 가능한 저장소가 필요하다.

후보:

- Netlify Blobs
- Supabase Storage
- Cloudflare R2
- S3 호환 저장소

현재 추천:

```text
먼저 Netlify 정적 이미지로 Threads 이미지 게시 테스트를 끝낸다.
이미지 게시가 성공한 뒤 카드뉴스용 영구 저장소를 결정한다.
```

## 이후 Hermes 흐름

이미지 게시까지 성공하면 Hermes와 Telegram 승인 플로우를 붙인다.

```text
Telegram에 내용 입력
-> Hermes가 카드뉴스 초안 생성
-> Hermes가 Telegram으로 미리보기 전송
-> 사용자가 수정 요청 또는 승인
-> 사용자가 /post 명령
-> Hermes가 Threads API 호출
-> Threads에 게시
```

반드시 지킬 원칙:

```text
Hermes는 사용자 승인 없이 절대 게시하지 않는다.
```

## 최종 MVP 순서

1. 노출된 앱 시크릿과 토큰 재발급
2. 유효한 Threads access token 다시 발급
3. Netlify public image URL 테스트
4. Threads API 이미지 게시 테스트
5. 로컬 게시 스크립트 추가
6. Hermes/Telegram 승인 플로우 연결
7. 카드뉴스 생성 비서 구현
8. AI 정리 비서 구현
9. 리서처, PM, 홍보 비서 순서로 확장
