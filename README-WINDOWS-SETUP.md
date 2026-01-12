# Windows PC 자동 실행 설정 가이드

이 가이드는 **Windows 10/11**에서 매일 오전 5시에 자동으로 NYT Business 뉴스를 Kindle로 전송하는 방법을 설명합니다.

## 📋 사전 요구사항

1. **Windows PC 켜두기**: 매일 오전 5시에 PC가 켜져 있어야 합니다
2. **Python 설치**: Python 3.8 이상 설치 필요
3. **Chrome 브라우저**: 웹 스크래핑에 필요
4. **의존성 설치 완료**: `pip install -r requirements.txt`
5. **config.yaml 설정 완료**: NYT 로그인 정보 입력

## 🚀 설정 방법

### 1. PowerShell을 관리자 권한으로 실행

1. **시작 메뉴** → **PowerShell** 검색
2. **우클릭** → **관리자 권한으로 실행**
3. 프로젝트 폴더로 이동:

```powershell
cd C:\path\to\kindle-news-delivery
```

### 2. 실행 정책 변경 (최초 1회만)

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**질문이 나오면 `Y` 입력**

### 3. 스케줄러 설치

```powershell
.\setup_scheduler_windows.ps1
```

**다른 시간에 실행하고 싶다면:**
```powershell
.\setup_scheduler_windows.ps1 -Time "06:00"  # 오전 6시
```

### 4. 설치 확인

```powershell
Get-ScheduledTask -TaskName "KindleNewsDelivery"
```

또는 **작업 스케줄러** GUI 사용:
1. **시작 메뉴** → **작업 스케줄러** 검색
2. **작업 스케줄러 라이브러리**에서 "KindleNewsDelivery" 확인

### 5. 수동 테스트 (선택사항)

PowerShell에서:
```powershell
.\run_daily.bat
```

또는

```powershell
python main.py
```

또는 작업 스케줄러에서:
```powershell
Start-ScheduledTask -TaskName "KindleNewsDelivery"
```

## 📅 실행 스케줄

- **요일**: 월요일 ~ 금요일
- **시간**: 오전 5:00 AM (변경 가능)
- **제외**: 토요일, 일요일

## 📊 로그 확인

실행 로그는 자동으로 저장됩니다:

```powershell
# 일반 로그
Get-Content logs\daily_run.log -Tail 50

# 실시간 로그 확인
Get-Content logs\daily_run.log -Wait

# 앱 로그
Get-Content kindle_news.log -Tail 50
```

또는 메모장으로:
```
notepad logs\daily_run.log
```

## 🛠️ 문제 해결

### 스케줄러가 실행되지 않을 때

#### 1. 작업 상태 확인
```powershell
Get-ScheduledTask -TaskName "KindleNewsDelivery" | Select-Object State,LastRunTime,LastTaskResult
```

#### 2. 수동 실행 테스트
```powershell
Start-ScheduledTask -TaskName "KindleNewsDelivery"
```

#### 3. 로그 확인
```powershell
notepad logs\daily_run.log
```

#### 4. 작업 이벤트 로그 확인
**이벤트 뷰어** → **응용 프로그램 및 서비스 로그** → **Microsoft** → **Windows** → **TaskScheduler**

### PC가 절전 모드일 때

Windows는 절전 모드에서 예약된 작업을 **실행하지 않습니다**. 다음 설정이 필요합니다:

#### 옵션 1: 절전 모드 비활성화 (권장)

**설정** → **시스템** → **전원 및 배터리** → **화면 및 절전**:
- **화면**: 10분 후 끄기 (또는 원하는 시간)
- **절전**: 사용 안 함

#### 옵션 2: 작업을 위해 PC 깨우기

작업 스케줄러에서 설정 변경:
1. **작업 스케줄러** 열기
2. **KindleNewsDelivery** 작업 우클릭 → **속성**
3. **조건** 탭:
   - ✅ **작업을 실행하기 위해 컴퓨터를 절전 모드에서 해제**
   - ✅ **AC 전원에서만 시작**
4. **설정** 탭:
   - ✅ **예약된 시작 시간이 지난 경우 가능한 한 빨리 작업 실행**

### Python을 찾을 수 없다는 오류

`run_daily.bat`를 편집하여 Python 전체 경로 지정:

```batch
REM 이 줄을 찾아서
python main.py

REM 이렇게 변경 (본인의 Python 경로로)
"C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe" main.py
```

Python 경로 찾기:
```powershell
(Get-Command python).Source
```

### 실행 시간 변경

PowerShell 관리자 권한으로:
```powershell
.\uninstall_scheduler_windows.ps1
.\setup_scheduler_windows.ps1 -Time "06:00"
```

## 🗑️ 제거 방법

PowerShell 관리자 권한으로:

```powershell
.\uninstall_scheduler_windows.ps1
```

이후에도 수동 실행은 가능합니다:
```powershell
python main.py
```

## ⚙️ 고급 설정

### GUI로 작업 수정

1. **작업 스케줄러** 실행
2. **KindleNewsDelivery** 우클릭 → **속성**
3. 원하는 설정 변경:
   - **트리거**: 실행 시간 변경
   - **조건**: 네트워크, 전원 조건
   - **설정**: 재시도, 타임아웃 설정

### 매일 실행 (주말 포함)

PowerShell에서 직접 수정:

```powershell
$Trigger = New-ScheduledTaskTrigger -Daily -At "05:00"
Set-ScheduledTask -TaskName "KindleNewsDelivery" -Trigger $Trigger
```

### 하루에 여러 번 실행

PowerShell 스크립트를 편집하거나, 작업 스케줄러 GUI에서:
1. **트리거** 탭 → **새로 만들기**
2. 원하는 시간 추가 (예: 오후 6시)

### 특정 Wi-Fi에서만 실행

작업 스케줄러에서:
1. **조건** 탭
2. ✅ **다음 네트워크 연결에서만 시작**
3. 네트워크 선택

## 🔋 전원 관리 팁

배터리/전력 절약:

1. **모니터만 끄기**:
   - 설정 → 전원 및 배터리 → 화면: 10분
   - 절전: 사용 안 함

2. **저전력 모드**:
   - 대부분의 작업은 저전력 모드에서도 작동

3. **야간에만 실행**:
   - 이미 오전 5시 설정이므로 전력 낭비 최소화

## 📝 체크리스트

설정 완료 확인:

- [ ] Python 3.8+ 설치 확인: `python --version`
- [ ] Chrome 브라우저 설치
- [ ] `pip install -r requirements.txt` 실행 완료
- [ ] `config.yaml`에 NYT 로그인 정보 입력
- [ ] `config.yaml`에 Gmail 정보 입력
- [ ] `config.yaml`에 Kindle 이메일 입력
- [ ] Amazon Kindle 설정에서 Gmail 승인
- [ ] PowerShell 실행 정책 설정: `Set-ExecutionPolicy RemoteSigned`
- [ ] `.\setup_scheduler_windows.ps1` 실행 완료
- [ ] `Get-ScheduledTask -TaskName "KindleNewsDelivery"` 확인
- [ ] 수동 테스트 성공: `.\run_daily.bat`
- [ ] Windows 절전 설정 확인

모든 항목 완료 시 매일 오전 5시에 자동으로 뉴스를 받을 수 있습니다!

## 🆚 작업 스케줄러 vs GitHub Actions

| 항목 | Windows 로컬 | GitHub Actions |
|------|-------------|----------------|
| PC 켜두기 | 필요 | 불필요 |
| 전기 비용 | 있음 (절전 모드 가능) | 없음 |
| 설정 복잡도 | 보통 | 약간 복잡 |
| 안정성 | PC 상태 의존 | 매우 안정적 |
| 브라우저 확인 | 가능 | 불가능 |
| 디버깅 | 쉬움 | 어려움 |
| 전문 기사 | ✅ | ❌ (CAPTCHA 문제) |

**권장**: 회사 PC는 보통 평일에 켜져 있으므로 로컬 실행이 이상적!

## 💡 회사 PC에서 사용 시 주의사항

1. **회사 방화벽**: NYT 접속이 차단될 수 있음
2. **보안 정책**: 관리자 권한이 필요할 수 있음
3. **네트워크**: VPN 사용 시 연결 확인
4. **퇴근 시**: PC를 꺼도 아침에 자동으로 켜지지 않으므로, **절전 모드만 사용** 권장

## 🎯 최적 설정 (회사 PC용)

```powershell
# 1. 스케줄러 설치 (오전 8시 - 출근 후)
.\setup_scheduler_windows.ps1 -Time "08:00"

# 2. Windows 전원 설정
# 설정 → 전원 및 배터리:
#   - 화면: 10분
#   - 절전: 사용 안 함 (또는 4시간)

# 3. 작업 스케줄러 조건 설정
# 조건 탭:
#   ✅ 네트워크 연결 시에만 시작
#   ✅ AC 전원에서만 시작
```

이렇게 하면 **회사 PC**에서 평일 아침마다 자동으로 뉴스를 받을 수 있습니다!
