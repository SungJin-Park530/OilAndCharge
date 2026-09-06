 # OilAndCharge

 사용자 위치와 등록 차량의 연비를 바탕으로 주변 주유소를 찾고, 주유 가격과 왕복 이동비를 함께 계산하는 웹 서비스입니다.

 현재 MVP는 휘발유 차량과 휘발유(B027) 조회를 대상으로 합니다.

 ## 시연 영상

 [![OilAndCharge 시연 영상](https://img.youtube.com/vi/MbcDpnc_Ljg/maxresdefault.jpg)](https://youtu.be/MbcDpnc_Ljg)

 ## 서비스 화면

 | 메인 화면 | 차량 등록 화면 | 조회 결과 화면 |
 | --- | --- | --- |
 | ![메인 화면](docs/images/main.png) | ![차량 등록 화면](docs/images/car.png) | ![조회 결과 화면](docs/images/result.png) |

 ## 주요 기능

 - 주변 주유소 조회 및 카카오맵 마커 표시
 - 등록 차량의 연비를 반영한 왕복 이동비 계산
 - 주유량, 리터당 가격, 이동비를 합산한 예상 소요 비용 계산
 - 차량 등록 및 등록 차량 목록 조회
 - OPINET 조회 결과의 데이터베이스 캐싱

 ## 기술 스택

 | 구분 | 기술 |
 | --- | --- |
 | Backend | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=Flask&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=Gunicorn&logoColor=white) |
 | Frontend | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=HTML5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=CSS3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=JavaScript&logoColor=black) |
 | Database | ![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=flat-square&logo=MariaDB&logoColor=white) ![PyMySQL](https://img.shields.io/badge/PyMySQL-3776AB?style=flat-square&logo=Python&logoColor=white) |
 | 지도 | ![Kakao Maps](https://img.shields.io/badge/Kakao%20Maps-FFCD00?style=flat-square&logo=Kakao&logoColor=black) |
 | 좌표 변환 | ![pyproj](https://img.shields.io/badge/pyproj-3776AB?style=flat-square&logo=Python&logoColor=white) |
 | HTTP / 환경 설정 | ![requests](https://img.shields.io/badge/requests-3776AB?style=flat-square&logo=Python&logoColor=white) ![python--dotenv](https://img.shields.io/badge/python--dotenv-ECD53F?style=flat-square&logo=Python&logoColor=black) |
 | Deployment | ![Cloudtype](https://img.shields.io/badge/Cloudtype-3B82F6?style=flat-square&logoColor=white) |

 ## 사용 API

 | API | 용도 | 인증 환경 변수 |
 | --- | --- | --- |
 | [OPINET](https://www.opinet.co.kr/) `aroundAll.do` | 반경 내 휘발유 주유소 및 가격 조회 | `OPINET_API_KEY` |
 | [Kakao Mobility](https://developers.kakaomobility.com/) | 경로 탐색 및 이동 거리 계산 | `KAKAO_REST_API_KEY` |
 | [Kakao Maps Web SDK](https://apis.map.kakao.com/) | 지도 렌더링 및 주유소 마커 표시 | `KAKAO_JAVASCRIPT_KEY` |

 > 유가정보 데이터는 한국석유공사 오피넷에서 제공하는 API를 활용해서 제작되었습니다.

 ## 서비스 아키텍처

 ```mermaid
 flowchart LR
       User[사용자] --> Web[Flask 웹 애플리케이션]
       Cloudtype[Cloudtype] --> Web
       Web --> FuelRoutes[Fuel Blueprint]
       Web --> VehicleRoutes[Vehicle Blueprint]
       FuelRoutes --> Search[주유소 검색 서비스]
       FuelRoutes --> Cost[비용 계산 서비스]
       VehicleRoutes --> VehicleService[차량 서비스]
       Search --> Coordinate[좌표 변환 서비스]
       Search --> OPINET[OPINET API]
       Search --> KakaoMobility[Kakao Mobility API]
       Web --> KakaoMaps[Kakao Maps Web SDK]
       Search --> FuelRepository[주유 가격 캐시 Repository]
       VehicleService --> VehicleRepository[차량 Repository]
       FuelRepository --> DB[(MariaDB)]
       VehicleRepository --> DB
 ```

 - `app/fuel/`: 주유소 검색, 좌표 변환, 경로 거리와 비용 계산을 담당합니다.
 - `app/vehicle/`: 차량 등록과 조회를 담당합니다.
 - `app/models/database.py`: MariaDB 연결과 요청 종료 시 연결 해제를 담당합니다.
 - WGS84 위치 좌표를 OPINET 요청용 KATEC/TM128 좌표로 변환하고, 응답 좌표는 다시 WGS84로 변환해 지도에 표시합니다.
 - 애플리케이션은 Cloudtype을 통해 배포합니다.

 ## 시작하기

 ### 사전 요구 사항

 - Python 3
 - MariaDB 접근 정보
 - OPINET API 키
 - Kakao REST API 키 및 JavaScript 키

 ### 설치 및 실행

 ```bash
 python -m venv venv
 .\venv\Scripts\activate
 pip install -r requirements.txt
 ```

 프로젝트 루트에 `.env` 파일을 만들고 다음 값을 설정합니다.

 ```env
 SECRET_KEY=change-me
 OPINET_API_KEY=your-opinet-api-key
 KAKAO_REST_API_KEY=your-kakao-rest-api-key
 KAKAO_JAVASCRIPT_KEY=your-kakao-javascript-api-key
 DB_HOST=your-db-host
 DB_PORT=3306
 DB_USER=your-db-user
 DB_PASSWORD=your-db-password
 DB_NAME=your-db-name
 ```

 ```bash
 python run.py
 ```

 브라우저에서 `http://localhost:5000`에 접속합니다.

> **배포 환경 안내:** Cloudtype 무료 플랜을 사용하므로 서버는 매일 자정에 자동으로 중지됩니다.

 ## API 엔드포인트

 | Method | Endpoint | 설명 |
 | --- | --- | --- |
 | `GET` | `/` | 메인 화면 |
 | `GET` | `/history` | 계산 이력 화면 |
 | `GET` | `/api/stations` | 주변 주유소 검색 및 비용 계산 |
 | `GET` | `/api/vehicles` | 등록 차량 목록 조회 |
 | `POST` | `/api/vehicles` | 차량 등록 |

 ## 프로젝트 구조

 ```text
 app/
    fuel/       # 주유소 검색, 좌표 변환, 비용 계산
    vehicle/    # 차량 등록 및 조회
    models/     # 데이터베이스 연결
    static/     # CSS, JavaScript
    templates/  # HTML 템플릿
 run.py        # 애플리케이션 실행 진입점
 ```

 ## 향후 개선

 - 전기차 충전소와 경유, LPG 등 유종 확대
 - 사용자 위치 직접 지정
 - 차량 수정 및 삭제
 - 정렬, 즐겨찾기, 지도 마커와 목록의 상호작용 개선
