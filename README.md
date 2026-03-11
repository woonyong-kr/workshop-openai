# Clean Email

## 2분 발표 스크립트
안녕하세요. 저희 프로젝트 **Clean Email**은 Gmail 받은편지함을 더 빠르고 안전하게 확인할 수 있도록 만든 메일 필터링 웹서비스입니다.  
기획 의도는 사용자가 메일을 직접 하나씩 읽으면서 판단하는 부담을 줄이고, 위험 가능성이 있는 메일은 먼저 분류해서 우선순위를 잡을 수 있게 돕는 데 있습니다.

시연은 크게 세 단계입니다.  
첫 번째로 Google 로그인으로 계정을 연결하면, Gmail API를 통해 실제 메일 목록을 바로 불러옵니다.  
두 번째로 메인 메일함에서는 전체 메일뿐 아니라 `일반`, `보류`, `격리` 상태별로 메일을 나눠 볼 수 있고, 위험 점수와 분류 근거도 함께 확인할 수 있습니다.  
세 번째로 사용자가 특정 키워드를 숨김 규칙에 등록하면 해당 키워드가 포함된 메일은 기본 목록에서 숨겨지고, 사이드바의 키워드 버튼을 눌렀을 때만 따로 모아서 볼 수 있습니다. 필요하면 여러 메일을 선택해서 Gmail 휴지통으로 이동할 수도 있습니다.

정리하면, 이 서비스는 Gmail을 그대로 쓰면서도 메일 분류, 상세 확인, 숨김 규칙, 휴지통 이동까지 한 화면 흐름으로 정리한 메일 관리 도구입니다.

---

## 프로젝트 소개
Clean Email은 Google OAuth 로그인과 Gmail API를 기반으로 동작하는 Flask 웹앱입니다.  
실제 Gmail 메일함을 읽어와 메일 목록, 상세 보기, 위험 점수, 분류 상태, 키워드 기반 숨김 규칙, 휴지통 이동 기능을 제공합니다.

### 핵심 목표
- Gmail을 실시간으로 읽어오는 메일 워크스페이스 제공
- 위험 메일을 `일반 / 보류 / 격리` 상태로 분류
- 키워드 기반 숨김 규칙으로 메일 목록 노이즈 감소
- 메일 상세 보기와 첨부파일 다운로드를 한 화면에서 제공
- Windows 11 스타일의 밝고 정돈된 UI 적용

## 주요 기능
### 1. Google OAuth 로그인
- Google 계정으로 로그인
- 사용자 식별 정보와 OAuth 토큰을 MongoDB에 저장
- 토큰은 `cryptography.Fernet`으로 암호화하여 보관

### 2. Gmail 메일함 조회
- Gmail API에서 받은편지함 메일을 실시간으로 조회
- 무한 스크롤 방식으로 다음 메일 페이지 로딩
- 메일 상세 보기에서 HTML 본문, 첨부파일, 메타데이터 확인

### 3. 메일 분류
- 메일 본문, 제목, 발신 도메인, 첨부파일 확장자를 기반으로 위험 점수 계산
- 상태 분류:
  - `일반`
  - `보류`
  - `격리`
- 분류 근거와 위험 점수를 메일 목록/상세 화면에 함께 표시

### 4. 숨김 규칙
- 사용자가 키워드를 직접 등록 가능
- 등록한 키워드가 들어간 메일은 기본 목록에서 숨김
- 사이드바의 키워드 버튼을 누르면 해당 키워드에 해당하는 메일만 다시 모아서 확인 가능

### 5. 휴지통 이동
- 메일 목록에서 여러 메일을 선택해 한 번에 휴지통 이동 가능
- 메일 상세 화면에서도 단건 휴지통 이동 가능
- 실제 영구 삭제가 아니라 Gmail의 `trash` 동작을 사용

### 6. 설정 페이지
- 기본 메일 보기 설정
- 한 번에 불러올 메일 수 설정
- `보류` / `격리` 임계값 조정
- 숨김 규칙 적용 여부, 첨부파일 다운로드 허용 여부 등 옵션 저장

## 사용자 흐름
1. 홈 화면에서 Google 계정 연결
2. 메일함 화면에서 메일 목록 확인
3. 상태 필터(`전체`, `일반`, `보류`, `격리`) 적용
4. 필요한 경우 숨김 키워드 추가
5. 상세 보기에서 본문, 첨부파일, 분류 근거 확인
6. 선택 메일 또는 단일 메일을 Gmail 휴지통으로 이동

## 기술 스택
- Backend: Flask 3
- Database: MongoDB
- OAuth / API: Google OAuth 2.0, Gmail API
- Security: `cryptography` 기반 토큰 암호화
- HTML Sanitizing: `bleach`
- Frontend styling: Tailwind CSS + custom Windows 11 style CSS
- Test: pytest

## 프로젝트 구조
```text
workshop-openai/
├─ app/
│  ├─ auth/                # Google OAuth 로그인/콜백/로그아웃
│  ├─ core/                # 홈, 설정, 개인정보, 헬스체크
│  ├─ mailbox/             # 메일 목록, 상세, 숨김 규칙, 휴지통 이동
│  ├─ repositories/        # MongoDB 사용자/설정 저장소
│  ├─ services/            # Gmail API, Google OAuth, 가시성 규칙
│  └─ utils/               # 인증 데코레이터, 암호화 유틸
├─ static/
│  ├─ css/                 # 빌드된 스타일 + Windows 11 스타일 보정
│  └─ js/                  # 무한 스크롤 메일 로딩
├─ templates/              # 홈, 메일함, 상세, 설정, 개인정보 페이지
├─ tests/                  # 주요 플로우 테스트
├─ app.py                  # Flask 실행 진입점
├─ requirements.txt
└─ package.json
```

## 환경 변수
이 프로젝트는 `.env.public`과 `.env.secret`를 함께 읽습니다.

### `.env.public`
기본 앱 이름과 공개 설정을 담습니다.

예시:
```env
APP_NAME=Clean Email
APP_TAGLINE=Google 메일을 더 차분하고 정돈된 흐름으로 읽는 웹앱
APP_BASE_URL=https://mail.woonyong.org
MAILBOX_PAGE_SIZE=20
SESSION_COOKIE_SECURE=true
```

### `.env.secret`
민감한 정보와 실행 환경별 설정을 담습니다.

예시:
```env
PORT=5001
FLASK_SECRET_KEY=change-this-secret

MONGO_URI=mongodb://localhost:27017/cleen_mail
MONGO_DB_NAME=cleen_mail

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5001/auth/google/callback

TOKEN_ENCRYPTION_KEY=your-fernet-key
SESSION_COOKIE_SECURE=false
```

### 필수 환경 변수 설명
- `FLASK_SECRET_KEY`: Flask 세션 암호화 키
- `MONGO_URI`: MongoDB 연결 문자열
- `MONGO_DB_NAME`: 사용할 DB 이름
- `GOOGLE_CLIENT_ID`: Google OAuth 클라이언트 ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth 클라이언트 Secret
- `GOOGLE_REDIRECT_URI`: OAuth 콜백 URL
- `TOKEN_ENCRYPTION_KEY`: Google 토큰 암호화용 Fernet 키

## 로컬 실행 방법
### 1. Python 가상환경 준비
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. MongoDB 실행
로컬에서 MongoDB가 설치되어 있어야 합니다.

### 3. 환경 변수 파일 준비
- `.env.public` 확인
- `.env.secret` 생성 후 필수 값 입력

### 4. Flask 서버 실행
```powershell
python app.py
```

접속 주소:
- `http://localhost:5001`

## CSS 개발
기본 CSS는 이미 저장소에 포함되어 있습니다.  
디자인을 수정할 때만 Tailwind 빌드를 다시 실행하면 됩니다.

```powershell
npm install
npm run build:css
```

watch 모드:
```powershell
npm run watch:css
```

## 테스트
```powershell
pytest
```

현재 테스트에는 다음 흐름이 포함됩니다.
- 홈 화면 렌더링
- 로그인 없이 메일함 접근 시 리다이렉트
- Google OAuth 콜백 처리
- 메일 목록/피드/상세 화면 렌더링

## 주요 화면
- `/` : 랜딩 페이지
- `/auth/google/start` : Google 로그인 시작
- `/auth/google/callback` : Google OAuth 콜백
- `/mailbox` : 메일 목록 화면
- `/mail/<message_id>` : 메일 상세 화면
- `/settings` : 사용자 설정 화면
- `/privacy` : 개인정보 안내
- `/health` : 헬스체크 API

## 보안 및 저장 정책
- 메일 본문은 Gmail API에서 실시간 조회
- OAuth 토큰은 암호화 후 MongoDB 저장
- 세션에는 사용자 ID만 저장
- HTML 본문은 `bleach`로 정제 후 렌더링
- 첨부파일 다운로드는 설정에서 허용 여부 제어 가능

## 시연 포인트
- Google 로그인 후 실제 메일함 연결
- 메일 상태별 필터 확인
- 숨김 규칙 추가 후 기본 목록에서 메일이 사라지는지 확인
- 키워드 버튼으로 숨겨진 메일 묶음만 다시 보기
- 메일 상세에서 위험 점수, 근거, 첨부파일 확인
- 메일 선택 후 Gmail 휴지통 이동

## 한계와 현재 범위
- 실제 수신 거부 메일 발송은 현재 기본 기능에서 제외
- 분류 로직은 규칙 기반이며, ML 모델 기반 분류는 아님
- Gmail API 및 Google OAuth 설정은 실행 환경별로 별도 준비 필요

## 팀 메모
- `.env.secret`는 저장소에 포함하지 않습니다.
- Google OAuth Redirect URI는 로컬/배포 환경에 맞게 Google Cloud Console에 등록해야 합니다.
- 운영 환경에서는 HTTPS와 `SESSION_COOKIE_SECURE=true` 사용을 권장합니다.
