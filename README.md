# BCR

Budgeted Causal Repair for Reliable Multi-Hop RAG 문서 저장소입니다.

## 파일
- `main.tex`: 본안 작성용 템플릿
- `draft.tex`: 연구 초안 상세본(v2.0) + 선행/관련 연구 정리

## 실행법
### 1) Docker로 실행(권장)
TeX가 로컬에 없어도 컴파일할 수 있습니다.

```bash
# 본안
docker run --rm -v "$PWD":/work -w /work texlive/texlive:latest \
  latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex

# 초안
docker run --rm -v "$PWD":/work -w /work texlive/texlive:latest \
  latexmk -xelatex -interaction=nonstopmode -halt-on-error draft.tex
```

### 2) 로컬 TeX 배포판(TeX Live/MacTeX)으로 실행
```bash
# 본안
latexmk -xelatex main.tex

# 초안
latexmk -xelatex draft.tex
```

### 3) 결과 보기
컴파일 후 생성된 PDF를 열어 확인합니다.

```bash
open main.pdf
open draft.pdf
```

또는 Overleaf에 원하는 파일(`main.tex` 또는 `draft.tex`)을 업로드해 컴파일할 수 있습니다.
