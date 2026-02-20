# BCR

Budgeted Causal Repair for Reliable Multi-Hop RAG 문서 저장소입니다.

## 파일
- `main.tex`: 본안 작성용 템플릿
- `draft.tex`: 연구 초안 상세본(v2.0) + 선행/관련 연구 정리

## 빌드
로컬에 TeX 배포판(TeX Live/MacTeX)이 설치된 환경에서:

```bash
# 본안
latexmk -xelatex main.tex

# 초안
latexmk -xelatex draft.tex
```

또는 Overleaf에 원하는 파일(`main.tex` 또는 `draft.tex`)을 업로드해 컴파일할 수 있습니다.
