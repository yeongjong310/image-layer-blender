# merge-image-layer

두 이미지를 알파 블렌딩으로 합성하는 GUI 프로그램입니다.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 주요 기능

- 이미지 2개를 선택하여 알파 블렌딩으로 합성
- **PDF 입력 지원** — PDF 파일의 첫 페이지를 자동으로 이미지 변환 후 합성 (DPI 300)
- Alpha 슬라이더로 투명도 실시간 조절 (0.0 ~ 1.0)
- 합성 결과 실시간 미리보기
- JPG / PNG 출력 포맷 선택
- DPI 300 고품질 저장 (JPG: quality=100, subsampling=0)
- 크기가 다른 이미지는 큰 쪽에 맞춰 LANCZOS 리샘플링

### 지원 입력 포맷

| 포맷 | 확장자 |
|------|--------|
| 이미지 | PNG, JPG, JPEG, BMP, TIFF, WebP |
| 문서 | PDF (첫 페이지 자동 변환) |

## 요구 사항

- Python 3.11 이상
- macOS / Linux / Windows (Tkinter 지원 환경)

## 빠른 시작

```bash
# 설치 후 바로 실행
make run

# 또는 단계별로
make install
merge-image-layer
```

## Make 명령어

```bash
make help           # 사용 가능한 명령어 목록
make install        # 프로젝트 설치 (editable)
make install-dev    # 개발 의존성 포함 설치
make install-all    # 모든 의존성 설치
make run            # GUI 앱 실행
make test           # 테스트 실행
make lint           # 린트 검사
make format         # 코드 포맷팅
make typecheck      # 타입 체크
make build          # 단일 실행파일 빌드
make app            # macOS .app 번들 빌드
make clean          # 빌드 산출물 정리
make clean-all      # 가상환경 포함 전체 정리
```

## 빌드

### 단일 실행파일

```bash
make build
# → dist/merge-image-layer 생성
```

### macOS 앱 번들

```bash
make app
# → dist/이미지합성.app 생성
```

## 프로젝트 구조

```
src/merge_image_layer/
  __init__.py       # 패키지 초기화
  main.py           # Tkinter GUI
  blender.py        # 이미지 블렌딩 로직
tests/
  test_blender.py   # 블렌딩 단위 테스트
  test_main.py      # GUI 테스트
```

## 기술 스택

| 구분 | 기술 |
|------|------|
| GUI | Tkinter (Python 내장) |
| 이미지 처리 | Pillow |
| PDF 변환 | PyMuPDF |
| 빌드 | PyInstaller |
| 테스트 | pytest |
| 린트 | ruff |
