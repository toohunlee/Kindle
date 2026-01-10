# Kindle News Delivery

매일 아침 Wall Street Journal과 New York Times의 뉴스를 킨들로 자동 배달하는 시스템입니다.

## 기능

- WSJ와 NYT에서 오늘의 주요 뉴스 자동 스크래핑
- 킨들 친화적인 HTML 포맷으로 변환
- 킨들 이메일로 자동 전송
- 매일 정해진 시간에 자동 실행

## 설치 방법

### 1. 사전 요구사항

**필수:**
- Python 3.8 이상
- Google Chrome 브라우저 (Selenium WebDriver용)

**Chrome 브라우저 설치:**
- macOS: [Chrome 다운로드](https://www.google.com/chrome/)
- 이미 설치되어 있으면 skip

### 2. Python 환경 설정

```bash
cd kindle-news-delivery
pip install -r requirements.txt
```

첫 실행 시 ChromeDriver가 자동으로 다운로드됩니다.

### 3. 설정 파일 생성

```bash
cp config.example.yaml config.yaml
```

`config.yaml` 파일을 열어서 다음 정보를 입력하세요:

#### Kindle 이메일 주소
- Amazon 계정에서 확인: [Manage Your Content and Devices](https://www.amazon.com/mycd)
- "Preferences" > "Personal Document Settings"에서 킨들 이메일 확인
- 예: `seolee@kindle.com`

#### 이메일 설정 (Gmail 사용 권장)

Gmail을 사용하는 경우:
1. [Google App Passwords](https://myaccount.google.com/apppasswords)에서 앱 비밀번호 생성
2. "Mail"과 사용 중인 기기를 선택
3. 생성된 16자리 비밀번호를 `sender_password`에 입력

**중요**: 일반 Gmail 비밀번호가 아닌 앱 비밀번호를 사용해야 합니다!

#### 승인된 이메일 추가

Amazon에서 이메일을 받으려면 발신자 이메일을 승인해야 합니다:
1. [Manage Your Content and Devices](https://www.amazon.com/mycd)
2. "Preferences" > "Personal Document Settings"
3. "Approved Personal Document E-mail List"에 발신 이메일 주소 추가

#### WSJ/NYT 구독 계정
- 유료 구독 계정의 이메일과 비밀번호 입력
- **중요**: 2단계 인증(2FA)이 활성화되어 있으면 로그인이 실패할 수 있습니다

### 4. 테스트 실행

#### WebDriver 테스트 (선택사항)
```bash
cd utils
python webdriver_manager.py
```

Chrome 브라우저가 자동으로 열리고 Google에 접속하면 성공입니다.

#### 연결 테스트
```bash
cd utils
python kindle_sender.py
```

이메일 연결이 제대로 되는지 확인하고, 테스트 이메일을 킨들로 보낼 수 있습니다.

#### 전체 시스템 테스트
```bash
python main.py
```

뉴스를 스크래핑하고 킨들로 전송합니다. 첫 실행 시 5-10분 정도 걸릴 수 있습니다.

## 사용 방법

### 한 번만 실행

```bash
python main.py
```

### 매일 자동 실행 (스케줄러)

```bash
python scheduler.py
```

스케줄러는 `config.yaml`의 `delivery_time`에 설정된 시간에 매일 자동으로 실행됩니다.

#### macOS/Linux에서 백그라운드 실행

```bash
# nohup으로 백그라운드 실행
nohup python scheduler.py > scheduler_output.log 2>&1 &

# 프로세스 확인
ps aux | grep scheduler.py

# 중지하려면
kill <프로세스_ID>
```

#### launchd를 사용한 자동 시작 (macOS)

`~/Library/LaunchAgents/com.kindle.newsdelivery.plist` 파일 생성:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kindle.newsdelivery</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/seo/kindle-news-delivery/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/seo/kindle-news-delivery/logs/output.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/seo/kindle-news-delivery/logs/error.log</string>
</dict>
</plist>
```

로드:
```bash
launchctl load ~/Library/LaunchAgents/com.kindle.newsdelivery.plist
```

## 문제 해결

### Selenium/WebDriver 관련

**Chrome 브라우저가 없다는 에러:**
- Chrome 브라우저를 설치하세요: https://www.google.com/chrome/

**ChromeDriver 다운로드 실패:**
- 인터넷 연결을 확인하세요
- `webdriver-manager` 패키지가 첫 실행 시 자동으로 다운로드합니다

**headless 모드에서 문제 발생:**
- 디버깅을 위해 `headless=False`로 설정하여 브라우저를 볼 수 있습니다
- 스크래퍼 파일을 직접 실행하면 브라우저가 보입니다:
  ```bash
  cd scrapers
  python wsj_scraper_selenium.py
  ```

### 로그인 실패

**Selenium 사용 시 로그인이 더 안정적이지만**, 여전히 실패할 수 있습니다:

1. 웹 브라우저에서 해당 사이트에 정상 로그인되는지 확인
2. **2단계 인증(2FA)을 꺼야 합니다** - Selenium은 2FA를 처리할 수 없습니다
3. 캡차가 나타나면 로그인이 실패할 수 있습니다
4. 로그인 실패 시 스크린샷이 저장됩니다: `wsj_login_failed.png`, `nyt_login_failed.png`
5. `headless=False`로 설정하여 실제로 무슨 일이 일어나는지 확인하세요

### 이메일 전송 실패

1. Gmail 앱 비밀번호가 올바른지 확인
2. Amazon에서 발신자 이메일이 승인되었는지 확인
3. `python utils/kindle_sender.py`로 연결 테스트

### 킨들에 문서가 도착하지 않음

1. 킨들이 Wi-Fi에 연결되어 있는지 확인
2. Amazon 웹사이트의 [Manage Your Content](https://www.amazon.com/mycd)에서 문서가 업로드되었는지 확인
3. 스팸 폴더 확인

### 스크래핑 실패

WSJ나 NYT의 웹사이트 구조가 변경되면 스크래핑이 실패할 수 있습니다. 이 경우:

1. 로그 파일 확인: `kindle_news.log`
2. GitHub Issues에 보고
3. 임시로 한 소스만 사용 (`config.yaml`에서 다른 소스 비활성화)

## 프로젝트 구조

```
kindle-news-delivery/
├── main.py                      # 메인 실행 스크립트
├── scheduler.py                 # 스케줄러
├── config.yaml                  # 설정 파일 (직접 생성)
├── config.example.yaml          # 설정 예제
├── requirements.txt             # Python 패키지 목록
├── README.md                    # 이 파일
├── scrapers/                    # 스크래퍼 모듈
│   ├── wsj_scraper.py          # WSJ 스크래퍼 (requests 기반)
│   ├── wsj_scraper_selenium.py # WSJ 스크래퍼 (Selenium 기반) ⭐
│   ├── nyt_scraper.py          # NYT 스크래퍼 (requests 기반)
│   └── nyt_scraper_selenium.py # NYT 스크래퍼 (Selenium 기반) ⭐
├── formatters/                  # 포맷터 모듈
│   └── kindle_formatter.py      # 킨들 포맷 변환
├── utils/                       # 유틸리티
│   ├── kindle_sender.py         # 이메일 전송
│   └── webdriver_manager.py     # Selenium WebDriver 관리 ⭐
└── output/                      # 백업 파일 저장 (자동 생성)
```

⭐ = Selenium 추가로 새로 생성된 파일

## 개선 사항

현재 버전에 포함된 개선사항:

1. ✅ **Selenium 통합**: 더 안정적인 로그인을 위해 Selenium WebDriver 사용 (완료!)
2. **EPUB 변환**: HTML 대신 EPUB 포맷으로 변환하여 더 나은 독서 경험
3. **이미지 포함**: 기사의 이미지도 함께 다운로드
4. **맞춤 설정**: 특정 섹션이나 키워드로 필터링
5. **에러 알림**: 실패 시 이메일 알림

## 라이선스

개인 사용 목적으로 자유롭게 사용하세요. WSJ와 NYT의 이용약관을 준수해야 합니다.

## 주의사항

- 이 도구는 **개인 유료 구독자**를 위한 것입니다
- 웹 스크래핑은 해당 사이트의 이용약관을 준수해야 합니다
- 과도한 요청으로 계정이 차단될 수 있으니 주의하세요
- 상업적 사용이나 재배포는 금지됩니다
