# COMPRESS XML Parser

Codeware COMPRESS XML 파일을 파싱하여 Excel로 변환하는 Streamlit 웹 애플리케이션입니다.

## 기능

- COMPRESS XML 파일 업로드
- XML 내용 파싱 및 미리보기
- Excel 파일로 변환 및 다운로드
- 섹션별 시트 분리 (generalVesselInfo, heatExchangerGeneralInfo 등)

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포

이 앱은 Streamlit Cloud에 배포되어 있습니다:
- 배포 URL: https://compress-xml-parser.streamlit.app

## 사용법

1. XML 파일을 업로드
2. 파싱된 데이터 미리보기 확인
3. Excel 파일 다운로드