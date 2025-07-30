# UeSaYangBan (의사양반)

마인크래프트 서버와 디스코드 서버를 연결하여 다양한 상호작용을 가능하게 하는 플러그인 및 봇 프로젝트입니다.
안전한 토큰 기반으로 서버를 연결하고, 유연한 설정을 통해 다양한 목적의 채널을 관리할 수 있습니다.

## 주요 기능

- **안전한 서버 연결**: 마인크래프트 서버 내에서 생성된 일회용 토큰을 통해 디스코드 채널과 안전하게 연결합니다.
- **유연한 연결 관리**: YAML 설정 파일을 통해 여러 개의 마인크래프트 서버 연결을 관리하고, 각 채널의 목적(`log`, `rcon` 등)을 지정할 수 있습니다.
- **양방향 통신 기반**: 디스코드에서 마인크래프트로, 마인크래프트에서 디스코드로 이벤트를 주고받을 수 있는 기반 구조를 갖추고 있습니다.
- **음원 재생 기능**: 디스코드 음성 채널에서 유튜브 음원을 재생하고 관리할 수 있는 기능을 제공합니다.

## 프로젝트 구조

- **`UeSaYangBan_jar/`**: Paper 기반의 마인크래프트 서버 플러그인입니다. (Java, Maven)
- **`UeSaYangBan_py/`**: `discord.py` 기반의 디스코드 봇입니다. (Python)

이 프로젝트는 두 하위 프로젝트가 긴밀하게 상호작용하는 모노레포(Monorepo) 구조로 관리됩니다.

---

## 설치 및 설정 방법

### 사전 준비물

- **Java 21** 이상
- **Paper** 마인크래프트 서버 (1.21.x 권장)
- **Python 3.11** 이상
- **디스코드 봇 토큰**
- Youtube 재생 기능 사용 시 **FFmpeg** 설치

### 1. 마인크래프트 플러그인 설정 (`UeSaYangBan_jar`)

0.  여기를 클릭하여 [UeSaYangBan_jar(미구현)](https://github.com/LuPi13/UeSaYangBan) 빌드된 플러그인 파일을 다운로드할 수 있습니다. (현재는 빌드가 필요합니다.)

1.  **플러그인 빌드**:
    ```bash
    # UeSaYangBan_jar 디렉토리로 이동
    cd UeSaYangBan_jar
    # Maven을 사용하여 빌드
    mvn clean package
    ```
2.  **플러그인 설치**:
    - 빌드가 완료되면 `target/` 디렉토리에 `UeSaYangBan_jar-1.0.jar` 파일이 생성됩니다.
    - 이 `.jar` 파일을 마인크래프트 서버의 `plugins/` 폴더로 복사합니다.
3.  **최초 실행**:
    - 마인크래프트 서버를 한 번 실행하여 `plugins/UeSaYangBanJar/` 폴더와 기본 설정 파일(`config.yml`)이 생성되도록 합니다.
    - 필요시 `config.yml` 파일에서 HTTP 서버 포트(`http-port`) 등을 수정할 수 있습니다.

### 2. 디스코드 봇 설정 (`UeSaYangBan_py`)

1.  **가상환경 및 라이브러리 설치**:
    ```bash
    # UeSaYangBan_py 디렉토리로 이동
    cd UeSaYangBan_py
    # 가상환경 생성
    python -m venv .venv
    # 가상환경 활성화
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    # 필요한 라이브러리 설치
    pip install -r requirements.txt
    ```
2.  **설정 파일 생성**:
    - `config.template.json` 파일을 복사하여 `config.json` 파일을 만듭니다.
    - `config.json` 파일을 열어 `"token"` 항목에 자신의 디스코드 봇 토큰을 입력합니다.
3.  **봇 실행**:
    ```bash
    python bot.py
    ```

---

## 사용 방법

### 1단계: 마인크래프트에서 연결 토큰 생성

1.  마인크래프트 서버 파일의 `server.properties` 파일에서, `server-ip` 항목을 반드시 명시해야 합니다.
    ```properties
    server-ip=<your_address>
    server-port=25565
    ```
    
2.  마인크래프트 서버 관리자가 인게임 채팅창 또는 콘솔에서 아래 명령어를 실행합니다.
    ```
    /linkdiscord
    ```
    
3.  채팅창에 Base64로 인코딩된 긴 문자열이 나타납니다. 이 문자열을 클릭하면 클립보드에 복사됩니다.

### 2단계: 디스코드에서 서버 연결

1.  봇을 초대한 디스코드 서버의 채널에서 아래 슬래시 커맨드를 입력합니다.
    ```
    /link add [base64_string] [connection_name] [channel] (purpose)
    ```
    
2.  명령어의 각 인자를 채워넣습니다.
    - `base64_string`: 1단계에서 복사한 Base64 문자열을 붙여넣습니다.
    - `connection_name`: 이 연결을 식별할 고유한 이름입니다. (예: `survival_chat_sync`, `flatworld_log_stream`)
    - `channel`: 연결할 디스코드 채널을 선택합니다. (텍스트, 음성 채널 모두 가능)
    - `purpose`: 이 채널 연결의 목적을 지정합니다. (예: `log`, `rcon`, `chat`) (현재 의미 없음)


요청이 성공하면, 봇이 마인크래프트 플러그인과 통신하여 연결을 인증하고, `UeSaYangBan_py/links.yml` 파일에 연결 정보가 저장됩니다.

---

## 명령어(Discord bot)
##### [대괄호]는 필수 항목, (소괄호=기본값)은 선택 항목입니다.

- > **Youtube 음원 재생 명령어**
  > - `/youtube add [URL] (index=1)`: 유튜브 음원을 재생 목록에 추가합니다.
  > - `/youtube play (index) (channel=발신자 음성채널)`: 재생 목록을 재생합니다.
  > - `/youtube queue`: 현재 재생 중인 음원과 재생 목록을 확인합니다.
  > - `/youtube loop`: 재생 목록을 반복 재생합니다.
  > - `/youtube remove [index]`: 재생 목록에서 음원을 제거합니다.
  > - `/youtube skip`: 현재 재생 중인 음원을 건너뜁니다.
  > - `/youtube pause`: 음원 재생을 일시 정지합니다.
  > - `/youtube resume`: 일시 정지된 음원을 재개합니다.
  > - `/youtube exit`: 음원 재생을 종료하고 음원 채널에서 내보냅니다.
  > - `/youtube clear`: 플레이리스트를 모두 삭제합니다.
