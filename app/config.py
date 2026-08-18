import os

from dotenv import load_dotenv


# 프로젝트 루트의 .env 파일을 읽어
# 환경변수로 사용할 수 있도록 설정함.
load_dotenv()


class Config:
    """
    Flask 애플리케이션에서 사용할 환경설정을 관리함.

    API 인증키와 DB 접속정보처럼 환경마다 달라질 수 있는 값은
    코드에 직접 작성하지 않고 환경변수에서 읽어옴.
    """

    # Flask 애플리케이션 설정
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key"
    )

    # OPINET API 인증키
    OPINET_API_KEY = os.getenv(
        "OPINET_API_KEY",
        ""
    )

    # MariaDB 접속정보
    #
    # 로컬에서는 .env에 Cloudtype DB의 외부 접속정보를 입력하고,
    # 추후 Cloudtype 배포 시에는 배포환경의 환경변수/Secret으로
    # 동일한 이름의 값을 전달할 예정.
    DB_HOST = os.getenv("DB_HOST", "")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "")

    
    # Kakao Mobility 길찾기 API에서 사용할 REST API 키
    #
    # 카카오디벨로퍼스에서 발급한 REST API 키 값을 사용함.
    # Client Secret과는 다른 값이므로 혼동하지 않도록 주의.
    KAKAO_REST_API_KEY = os.getenv(
        "KAKAO_REST_API_KEY",
        ""
    )


    # Kakao Maps Web SDK에서 사용할 JavaScript 키
    #
    # 지도 표시와 마커 렌더링 등 브라우저 측 지도 기능에 사용함.
    # 백엔드 길찾기 API 호출에는 사용하지 않음.
    KAKAO_JAVASCRIPT_KEY = os.getenv(
        "KAKAO_JAVASCRIPT_KEY",
        ""
    )