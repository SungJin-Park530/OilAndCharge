# OilAndCharge

Flask 기반으로 오피넷 데이터를 활용해 주유소 및 충전소 정보를 조회할 수 있는 프로젝트의 뼈대입니다.

## 프로젝트 소개
- 주유소/충전소 정보를 조회하는 Flask 애플리케이션 구조를 제공합니다.
- 환경 변수 기반으로 API 키를 안전하게 관리합니다.
- 확장 가능한 Blueprint 패턴으로 기능을 분리해 개발할 수 있습니다.

## 데이터 출처
- 본 프로젝트는 오피넷(Open Petroleum Information Network) 데이터를 활용하는 구조를 가정합니다.
- OPINET API 키는 `.env` 또는 `.env.example`에 설정하여 사용합니다.

## 실행 방법
1. 가상 환경 생성
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
3. 환경 변수 설정
   ```bash
   copy .env.example .env
   ```
   `.env` 파일에서 `OPINET_API_KEY` 값을 실제 키로 수정합니다.
4. 서버 실행
   ```bash
   python run.py
   ```

## 주요 파일
- `app/__init__.py`: Flask 앱 팩토리
- `app/config.py`: 환경 변수 로드
- `app/fuel/`: 주유소/충전소 관련 기능
- `run.py`: 실행 진입점
