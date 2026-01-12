# 로컬 PC 자동 실행 설정 가이드

이 가이드는 **macOS**에서 매일 오전 5시에 자동으로 NYT Business 뉴스를 Kindle로 전송하는 방법을 설명합니다.

## 📋 사전 요구사항

1. **Mac을 켜두기**: 매일 오전 5시에 Mac이 켜져 있어야 합니다
2. **전원 설정**: 시스템 설정 → 배터리 → "디스플레이 끄기" 시간 설정 (sleep은 괜찮음)
3. **의존성 설치 완료**: `pip install -r requirements.txt`
4. **config.yaml 설정 완료**: NYT 로그인 정보 입력

## 🚀 설정 방법

### 1. 스케줄러 설치

프로젝트 폴더에서 다음 명령어를 실행하세요:

```bash
cd /Users/seo/kindle-news-delivery
./setup_scheduler.sh
```

이 스크립트가 자동으로:
- `logs/` 폴더 생성
- macOS launchd에 스케줄 등록
- 월요일~금요일 오전 5시 실행 설정

### 2. 설치 확인

스케줄러가 제대로 설치되었는지 확인:

```bash
launchctl list | grep kindle
```

출력 예시:
```
-    0    com.kindle.news.delivery
```

### 3. 수동 테스트 (선택사항)

스케줄러가 작동하기 전에 수동으로 테스트:

```bash
./run_daily.sh
```

또는

```bash
python3 main.py
```

## 📅 실행 스케줄

- **요일**: 월요일 ~ 금요일
- **시간**: 오전 5:00 AM
- **제외**: 토요일, 일요일

## 📊 로그 확인

실행 로그는 자동으로 저장됩니다:

```bash
# 일반 로그
tail -f logs/daily_run.log

# 에러 로그
tail -f logs/daily_error.log

# 앱 로그
tail -f kindle_news.log
```

## 🛠️ 문제 해결

### 스케줄러가 실행되지 않을 때

1. **스케줄러 상태 확인**
```bash
launchctl list | grep kindle
```

2. **스케줄러 재시작**
```bash
./uninstall_scheduler.sh
./setup_scheduler.sh
```

3. **로그 확인**
```bash
cat logs/daily_error.log
```

### Mac이 sleep 모드일 때

- macOS는 sleep 모드에서도 예약된 작업을 실행할 수 있습니다
- 하지만 **화면은 깨어나지 않습니다** (백그라운드 실행)
- 확실한 실행을 위해서는 "디스플레이 끄기"만 허용하고 sleep은 비활성화 권장

**시스템 설정 → 배터리 → 전원 어댑터:**
- "디스플레이 끄기": 10분 (또는 원하는 시간)
- "컴퓨터 자동 잠자기 방지": 체크 (전원 연결 시)

### 실행 시간 변경

`com.kindle.news.delivery.plist` 파일을 편집하여 시간 변경:

```xml
<key>Hour</key>
<integer>6</integer>  <!-- 5에서 6으로 변경하면 오전 6시 -->
```

변경 후 재설치:
```bash
./uninstall_scheduler.sh
./setup_scheduler.sh
```

## 🗑️ 제거 방법

자동 실행을 중지하려면:

```bash
./uninstall_scheduler.sh
```

이후에도 수동 실행은 가능합니다:
```bash
python3 main.py
```

## ⚙️ 고급 설정

### 매일 실행 (주말 포함)

`com.kindle.news.delivery.plist` 파일에서 `StartCalendarInterval`를 다음과 같이 변경:

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>5</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### 하루에 여러 번 실행

`StartCalendarInterval` array에 시간을 추가:

```xml
<key>StartCalendarInterval</key>
<array>
    <!-- 오전 5시 -->
    <dict>
        <key>Hour</key>
        <integer>5</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <!-- 오후 6시 -->
    <dict>
        <key>Hour</key>
        <integer>18</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</array>
```

## 🔋 전원 관리 팁

배터리 절약을 위해:

1. **clamshell 모드**: MacBook을 닫고 외부 모니터로 사용
2. **저전력 모드**: 시스템 설정 → 배터리 → 저전력 모드 (Selenium은 작동함)
3. **밝기 최소화**: 디스플레이가 꺼지면 상관없지만, 켜질 때를 대비

## 📝 체크리스트

설정 완료 확인:

- [ ] `pip install -r requirements.txt` 실행 완료
- [ ] `config.yaml`에 NYT 로그인 정보 입력
- [ ] `config.yaml`에 Gmail 정보 입력
- [ ] `config.yaml`에 Kindle 이메일 입력
- [ ] Amazon Kindle 설정에서 Gmail 승인
- [ ] `./setup_scheduler.sh` 실행 완료
- [ ] `launchctl list | grep kindle` 확인
- [ ] 수동 테스트 성공 (`./run_daily.sh`)
- [ ] Mac 전원 설정 확인 (자동 잠자기 방지)

모든 항목 완료 시 매일 오전 5시에 자동으로 뉴스를 받을 수 있습니다!

## 🆚 로컬 vs GitHub Actions 비교

| 항목 | 로컬 PC | GitHub Actions |
|------|---------|----------------|
| Mac 켜두기 | 필요 | 불필요 |
| 전기 비용 | 있음 | 없음 |
| 설정 복잡도 | 간단 | 약간 복잡 |
| 안정성 | Mac 상태 의존 | 매우 안정적 |
| 브라우저 확인 | 가능 (headless=False) | 불가능 |
| 디버깅 | 쉬움 | 어려움 |

**권장**: 로컬에서 테스트 후 안정화되면 GitHub Actions로 전환
