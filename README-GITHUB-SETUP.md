# GitHub Actions 자동 실행 설정 가이드

이 가이드는 GitHub Actions를 사용하여 매일 자동으로 NYT Business 뉴스를 Kindle로 전송하는 방법을 설명합니다.

## 📅 실행 스케줄

- **실행 시간**: 월요일 ~ 금요일 오전 5시 (한국시간)
- **휴일**: 주말(토요일, 일요일)에는 실행되지 않음

## 🚀 설정 방법

### 1. GitHub 저장소 생성

1. GitHub에서 새로운 private repository 생성
2. 로컬 프로젝트를 GitHub에 push

```bash
cd /Users/seo/kindle-news-delivery

# Git 초기화 (처음인 경우)
git init

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: NYT Business to Kindle delivery"

# GitHub repository 연결 (본인의 repository URL로 변경)
git remote add origin https://github.com/YOUR_USERNAME/kindle-news-delivery.git

# Push
git branch -M main
git push -u origin main
```

### 2. GitHub Secrets 설정

GitHub repository 설정에서 다음 secrets를 추가해야 합니다:

1. GitHub repository 페이지로 이동
2. **Settings** → **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 버튼 클릭
4. 다음 secrets를 하나씩 추가:

#### 필수 Secrets:

| Secret 이름 | 값 | 설명 |
|------------|-----|------|
| `KINDLE_EMAIL` | `seolee@kindle.com` | Kindle 이메일 주소 |
| `GMAIL_EMAIL` | `seolee@gmail.com` | Gmail 주소 |
| `GMAIL_APP_PASSWORD` | `djwv chjz ygmp ydoo` | Gmail 앱 비밀번호 |
| `NYT_EMAIL` | `email@example.com` | NYT 계정 이메일 |
| `NYT_PASSWORD` | `qwerty0070!` | NYT 계정 비밀번호 |

**중요**:
- 각 secret을 개별적으로 추가해야 합니다
- Secret 이름은 대소문자를 정확히 지켜야 합니다
- 값에는 따옴표를 넣지 마세요 (그냥 값만 입력)

### 3. Workflow 활성화

1. GitHub repository에서 **Actions** 탭 클릭
2. "I understand my workflows, go ahead and enable them" 클릭
3. "Daily News Delivery" workflow가 보이면 설정 완료

### 4. 수동 실행 테스트 (선택사항)

자동 실행 전에 테스트하려면:

1. **Actions** 탭 → **Daily News Delivery** workflow 선택
2. **Run workflow** 버튼 클릭
3. **Run workflow** 다시 클릭하여 확인
4. 실행 상태를 확인하고 로그를 통해 정상 작동 여부 확인

## 🔍 실행 확인 방법

### GitHub에서 확인
1. **Actions** 탭에서 실행 기록 확인
2. 각 실행을 클릭하여 상세 로그 확인
3. 성공 시 녹색 체크 표시, 실패 시 빨간 X 표시

### Kindle에서 확인
1. 실행 후 5-10분 내에 Kindle에서 확인
2. 제목: `01-09-26` (날짜 형식)
3. 저자: `NYT Business`
4. 10개의 NYT Business 기사 포함

## ⚙️ 스케줄 변경

실행 시간을 변경하려면 `.github/workflows/daily-news-delivery.yml` 파일 수정:

```yaml
schedule:
  # 예: 오전 6시로 변경 (UTC 21:00 전날)
  - cron: '0 21 * * 0-4'

  # 예: 매일 실행 (주말 포함)
  - cron: '0 20 * * *'
```

**Cron 시간 계산:**
- 한국시간(KST) = UTC + 9시간
- 한국시간 05:00 = UTC 20:00 (전날)
- 한국시간 06:00 = UTC 21:00 (전날)

**Cron 요일:**
- `0-4` = 일요일-목요일 (UTC) = 월요일-금요일 (KST)
- `*` = 매일

## 🐛 문제 해결

### Workflow가 실행되지 않을 때

1. **Actions 탭이 비활성화된 경우:**
   - Settings → Actions → General
   - "Allow all actions and reusable workflows" 선택

2. **Secrets가 잘못된 경우:**
   - Settings → Secrets and variables → Actions
   - 각 secret 값 재확인 및 수정

3. **실행 실패 시:**
   - Actions 탭에서 실패한 workflow 클릭
   - 로그를 확인하여 에러 메시지 확인
   - 대부분 credential 문제이므로 Secrets 재확인

### 자주 발생하는 에러

**"SMTP Authentication failed"**
- `GMAIL_APP_PASSWORD` secret 확인
- Gmail 앱 비밀번호가 올바른지 확인

**"Login failed to NYT"**
- `NYT_EMAIL`, `NYT_PASSWORD` secret 확인
- NYT 계정이 활성화되어 있는지 확인

**"No articles were scraped"**
- NYT 웹사이트 구조 변경 가능성
- 로그를 확인하여 구체적인 에러 확인

## 💰 비용

GitHub Actions 무료 사용량:
- Private repository: 월 2,000분 무료
- Public repository: 무제한 무료

예상 사용량:
- 1회 실행: 약 3-5분
- 월 실행 횟수: 약 20회 (월-금)
- 월간 총 사용: 약 60-100분

**결론**: 무료 한도 내에서 충분히 사용 가능

## 🔒 보안

1. **Private repository 사용 권장**
   - config.yaml은 .gitignore에 포함되어 있음
   - Secrets는 암호화되어 저장됨

2. **절대 하지 말아야 할 것:**
   - config.yaml을 GitHub에 push
   - Secrets를 코드에 직접 입력
   - Public repository에 민감한 정보 노출

## 📧 Amazon Kindle 설정 확인

GitHub Actions가 작동하려면 Amazon에서 Gmail을 승인해야 합니다:

1. [Amazon - Manage Your Content and Devices](https://www.amazon.com/mycd)
2. Preferences → Personal Document Settings
3. Approved Personal Document E-mail List에 `seolee@gmail.com` 추가

## 🎯 완료 체크리스트

- [ ] GitHub repository 생성 및 코드 push
- [ ] 5개의 GitHub Secrets 설정 완료
- [ ] Actions 활성화
- [ ] 수동 실행 테스트 성공
- [ ] Amazon Kindle에서 Gmail 승인
- [ ] Kindle에서 첫 번째 뉴스 수신 확인

모든 항목을 완료하면 월요일부터 금요일 오전 5시에 자동으로 NYT Business 뉴스를 받을 수 있습니다!

## 🖼️ 커버 이미지 설정

Kindle idle time에 표시될 커버 이미지를 설정하려면:

### 로컬 실행 시

1. 첨부하신 New York Times 이미지를 `assets/` 폴더에 저장
2. 파일명을 `cover.jpg` 또는 `cover.png`로 변경

```bash
# 자동 설정 스크립트 실행
./setup-cover.sh

# 또는 수동으로 복사
cp ~/Downloads/nyt-cover.jpg assets/cover.jpg
```

### GitHub Actions에서

GitHub에 이미지를 포함시키려면:

1. 이미지를 `assets/cover.jpg`로 저장
2. Git에 추가하고 커밋

```bash
cp ~/Downloads/nyt-cover.jpg assets/cover.jpg
git add assets/cover.jpg
git commit -m "Add cover image for Kindle"
git push
```

**주의**: 이미지는 `.gitignore`에서 예외 처리되어 있어 `assets/cover.*` 파일은 자동으로 포함됩니다.

### 권장 사양

- **해상도**: 1600x2560 픽셀 (Kindle Paperwhite)
- **최소**: 800x1280 픽셀
- **형식**: JPG 또는 PNG
- **파일 크기**: 2MB 이하

