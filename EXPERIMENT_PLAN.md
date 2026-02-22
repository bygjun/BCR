# BCR 상세 실험 계획 (기간 제외, v2)

본 문서는 **Budgeted Causal Repair (BCR)**의 재현 가능하고 검증 가능한 실험 프로토콜을 정의한다.
기간/일정 산정은 포함하지 않는다.

## 1. 실험 목표
- 멀티홉 RAG에서 BCR이 **비용이 동등한 조건**에서 정확도와 근거 체인 신뢰성을 동시에 개선하는지 검증한다.
- 개선이 특정 데이터셋/난이도에만 나타나는지, 일반적으로 재현되는지 확인한다.
- 개선 폭뿐 아니라 비용 대비 효율(Cost-per-Gain)과 Pareto 관점 우위를 함께 보고한다.

## 2. 핵심 주장(최종 논문 클레임 2개)
- Claim A(효율): BCR은 동일 비용대에서 정답 성능(F1)을 개선한다.
- Claim B(신뢰성): BCR은 근거 체인 품질(Evidence/Omission/Link)을 개선한다.

## 3. 동등 비용 조건 정의
- 비교는 동일 dataset/method/budget tier/seed 단위로 수행한다.
- 비용 동등성은 아래 조건으로 정의한다.
- `0.95 <= C_method / C_ref <= 1.05`
- `C_ref`는 비교쌍별 기준 모델로 고정한다. 예: `BCR-Full vs Vanilla`는 `C_ref=C_vanilla`, `BCR-Full vs Full-Rerun`은 `C_ref=C_full-rerun`.
- 위 범위를 벗어난 쌍은 "비용 비동등"으로 태깅하고, **주가설 검정에서는 제외**한다.
- 비용 비동등 결과는 별도 부록(민감도 분석)에서만 보고한다.

## 4. 연구 질문과 가설
- RQ1. LCIS 기반 우선순위는 휴리스틱 우선순위보다 복구 효율이 높은가?
- RQ2. 순차검정 조기종료는 성능 손실 없이 반사실적 호출 수를 줄이는가?
- RQ3. 동일 budget tier에서 BCR은 비지배(Pareto non-dominated) 해를 더 자주 형성하는가?

가설:
- H1(주가설): B2(+20%)에서 BCR-Full의 macro F1가 핵심 비교군 대비 유의하게 높다.
- H2: BCR-Full은 Full-Rerun 대비 Cost-per-Gain이 유의하게 우수하다.
- H3: BCR-Full은 Error Localization F1에서 핵심 비교군 대비 유의미한 개선을 보인다.

데이터셋별 최소 기대 개선 기준(참고용, 주가설과 별도):
- HotpotQA: F1 +1.5p 이상
- 2WikiMultiHopQA: F1 +1.5p 이상
- MuSiQue: F1 +1.0p 이상
- MultiHop-RAG benchmark: F1 +1.5p 이상

## 5. 주평가지표/보조지표/탐색지표
- Primary endpoint:
- `B2 tier`에서 `동등 비용 조건(±5%)`을 만족하는 쌍의 **macro F1 차이(ΔF1)**
- Secondary endpoints:
- EM, Evidence Coverage, Omission Rate, Link-Consistency, Error Localization F1
- Cost-per-Gain
- Exploratory endpoints:
- Pareto frontier 우위 비율
- hop 길이/오류 유형별 개선 패턴

## 6. 평가 범위
- 태스크: Multi-hop open-domain QA
- 데이터셋:
- HotpotQA
- 2WikiMultiHopQA
- MuSiQue
- MultiHop-RAG benchmark
- 출력 단위: 질문별 최종 답변 + 근거 체인 + 실행 비용 로그

## 7. 비교군 구성(핵심/확장 분리)
핵심 비교군(확증 실험):
- BCR-Full
- Vanilla RAG
- Full-Rerun-Repair
- Random-Hop-Repair
- BCR-NoLCIS
- BCR-NoSequential

확장 비교군(탐색 실험):
- Adaptive-RAG
- HopRAG
- PropRAG
- HydraRAG
- ERL (재현 가능 시)
- BCR-NoGate
- BCR-NoBudgetAlloc

## 8. 공정성 통제(고정 조건)
- 동일 backbone LLM
- 동일 retriever/index/top-k/context window
- 동일 decoding 파라미터(temperature, top-p, max tokens)
- 동일 프롬프트 템플릿 계열
- 동일 seed 집합(권장 5개)
- 동일 budget tier에서만 직접 비교
- 외부 도구/API 장애 시 동일 재시도 정책 적용

## 9. 튜닝/평가 분리 규칙
- 하이퍼파라미터 튜닝은 **공식 dev split**에서만 수행한다.
- 최종 보고는 **공식 test split**(또는 잠금된 held-out split)에서만 수행한다.
- 튜닝 과정에서 test 통계를 절대 참조하지 않는다.
- 튜닝 결정 로그(선택 이유/후보값/최종값)를 run artifact에 저장한다.

## 10. 비용 예산 정의
질의당 총 비용을 아래 합으로 정의한다.

- `C = c_tok*N_tok + c_ret*N_ret + c_rep*N_rep + c_lat*T_lat`
- `N_tok`: 입력/출력 토큰 사용량
- `N_ret`: retrieval 호출 수
- `N_rep`: repair/재시도 호출 수
- `T_lat`: end-to-end latency

Budget tier:
- B0: 추가 복구 0%
- B1: +10%
- B2: +20%
- B3: +30%

## 11. BCR 기본 설정
- Gate threshold `tau_g`: 위험 상위 30% hop 통과
- Sequential test: `n_min=2`, `n_max=6`
- LCIS 임계: `tau_low=0.02`, `tau_high=0.10`
- LCIS 해석: 값이 클수록 해당 hop의 인과적 영향이 큼(우선 복구 후보)
- 복구 연산 우선순위: 재검색 -> 링크 재연결 -> 부분 재생성 -> 전체 재시도(최후)
- 종료 규칙:
- 예산 소진
- 추가 기대 이득이 최소 개선 기준 미달
- 조기종료 조건 충족

## 12. 인과 타당성 검증(신규)
개입의 의미보존/유효성을 별도로 검증한다.

- Intervention Validity Check:
- 원문 질의 의도 보존 여부
- 문법/형식 오류 여부
- 비정상 변형(무의미 치환) 여부

추가 대조 실험:
- Placebo intervention: 의미적으로 무해한 변형만 적용
- Oracle intervention: 정답 기준 실패 hop만 복구

필수 보고:
- `intervention_valid_rate`
- `intervention_strength_mean`
- `placebo_gain` (BCR 대비)
- `oracle_gap` (oracle 대비 성능 격차)

## 13. 실험 매트릭스
### 13.1 확증(Confirmatory) 실험
- 대상: 핵심 비교군만
- 조합: dataset 4종 x budget(B0/B1/B2/B3) x seed 5회
- 목적: 주가설(H1/H2/H3) 검정

### 13.2 탐색(Exploratory) 실험
- 대상: 확장 비교군 + 추가 아블레이션
- 권장 범위: B0, B2 중심
- 목적: 일반화 경향과 실패 패턴 분석

### 13.3 아블레이션 실험
- BCR-Full vs BCR-NoLCIS
- BCR-Full vs BCR-NoSequential
- BCR-Full vs BCR-NoGate
- BCR-Full vs BCR-NoBudgetAlloc
- BCR-Full vs Random-Hop-Repair
- BCR-Full vs Full-Rerun-Repair

### 13.4 민감도 실험
- `tau_g`: 20%, 30%, 40%
- `n_max`: 4, 6, 8
- `tau_low/high`: (0.01/0.08), (0.02/0.10), (0.03/0.12)
- budget sweep: B0~B3

## 14. 실행 프로토콜(질의 단위)
1. 질문 입력과 gold metadata 로드
2. baseline 추론 경로 생성
3. hop 분해 및 게이트 스코어 계산
4. 후보 hop에 대해 개입 생성(bridge/relation/citation)
5. 개입 유효성 검사(Invalid 개입 제외)
6. LCIS 순차 추정 및 조기종료 판정
7. 예산 제약 하 우선순위 계산 후 복구 실행
8. 최종 답변/근거 체인 산출
9. 정답/근거/비용 지표 계산
10. query-level 로그 저장(JSONL)

## 15. 데이터 전처리/검증 규칙
- 질문-정답 쌍 누락 샘플 제거 규칙 명시
- 텍스트 정규화(lowercase, punctuation) 규칙 고정
- evidence 매핑 실패 케이스 별도 라벨링
- 샘플 제외 발생 시 제외 사유를 로그 필드로 기록
- 데이터셋별 split 고정 및 버전 해시 저장

## 16. 지표 계산 정의
- EM/F1: 데이터셋 표준 스크립트 우선 사용
- Evidence Coverage: 정답 체인에 필요한 핵심 근거 매칭 비율
- Omission Rate: 필요 근거 미포함 비율
- Link-Consistency: 인접 hop 간 엔티티/관계 연결 일관성
- Error Localization F1: 실패 hop 탐지 정밀도/재현율 기반 F1
- Cost-per-Gain:
- 분자: 추가 비용(`C_method - C_baseline`)
- 분모: 성능 개선(`F1_method - F1_baseline` 또는 EM 개선)
- 분모가 0 이하인 경우 `CPG-Invalid`로 태깅하고 CPG 우열 통계에서 제외

## 17. 통계 분석 계획(엄밀화)
주가설 검정:
- 기본 유의수준 `alpha = 0.05`
- Primary endpoint는 paired bootstrap 10,000회 + paired permutation test를 함께 보고
- 신뢰구간은 95% CI
- EM 개선은 secondary endpoint로 분리 보고

순차검정 오류율 통제:
- LCIS 순차검정은 O'Brien-Fleming alpha-spending 규칙 적용
- 각 hop 판정 로그에 단계별 사용 alpha를 기록

다중 비교 보정:
- 확증 실험 family와 탐색 실험 family를 분리
- family 내부는 BH-FDR(q=0.05) 보정

효과크기 및 민감도:
- 절대 개선폭(ΔEM, ΔF1)
- 상대 개선률(%)
- 표준화 효과크기(Cohen's dz)
- MDE(최소검출효과) 기준: F1 1.0p

## 18. Baseline 재현 실패 처리 규칙(신규)
- 재현 성공 기준: 공개 보고 수치 대비 ±1.5p 이내
- 1차 실패 시 동일 설정으로 재실행 후 평균값 기준 재판정
- 2차 실패 시 "재현 실패"로 태깅하고 원인 로그 공개
- 재현 실패 baseline은 확증 실험에서 제외하고 탐색/부록으로만 보고

## 19. 오류 분석 프로토콜
- 샘플링: 데이터셋/난이도 층화 샘플링
- 분석 라벨:
- retrieval miss
- bridge entity break
- relation drift
- citation mismatch
- hallucinated link
- 라벨링 기준 문서화 후 2인 교차 검토
- 불일치 라벨은 adjudication 기록 남김
- 산출물: 오류 유형별 빈도표 + 유형별 개선 기여도

## 20. 로깅/아티팩트 스펙
필수 query-level 필드:
- `qid`, `dataset`, `method`, `budget_tier`, `seed`
- `answer_pred`, `answer_gold`, `em`, `f1`
- `evidence_coverage`, `omission_rate`, `link_consistency`
- `error_localization_f1`
- `n_tok`, `n_ret`, `n_rep`, `latency_ms`, `total_cost`
- `k_candidates`, `n_interventions`, `early_stop_flag`
- `intervention_valid_rate`, `intervention_strength_mean`
- `placebo_gain`, `oracle_gap`
- `repair_ops_applied`, `failure_tag`

실험 run-level 산출물:
- 설정 파일 사본(모든 하이퍼파라미터 포함)
- 튜닝 로그(후보값/선택값/선택 근거)
- 실행 로그(JSONL)
- 집계 결과 CSV
- 표/그림 생성 스크립트 출력물
- 재현용 커밋 해시 및 데이터 버전 메타

## 21. 품질 게이트(실험 수용 기준)
- 로그 누락 필드 0건
- 동일 seed 재실행 시 주요 지표 편차 허용 범위 내
- baseline 재현 성능이 비정상적으로 낮지 않을 것
- 주요 결과 표에 CI/효과크기 누락 없음
- 비용/성능 지표가 동일 집합에서 계산되었음을 검증
- **제3자 1회 재실행 성공(동일 설정) 확인**

## 22. 결과 보고 템플릿
필수 표:
- Table A: 데이터셋별 Primary endpoint(ΔF1@B2, cost-matched)
- Table B: EM/F1 전체(B0~B3)
- Table C: 근거 품질(Evidence/Omission/Link)
- Table D: 비용 지표 및 Cost-per-Gain
- Table E: 아블레이션 결과

필수 그림:
- Figure A: Budget vs 성능 곡선
- Figure B: Budget vs 비용 곡선
- Figure C: Pareto frontier(method별)
- Figure D: 오류 유형별 개선 기여도

본문 결론 검증 문장:
- "비용 동등 조건(±5%)에서 F1 개선"
- "근거 품질 지표 동시 개선"

## 23. 실패 시에도 남는 기여(신규)
성능 개선이 작더라도 아래 결과를 기여로 남긴다.
- 비용-성능 한계선(Pareto) 실증
- 오류 유형 taxonomy 및 빈도 통계
- LCIS/순차검정의 작동 조건과 실패 조건 정리
- dataset별 취약 패턴(길이/관계/출처) 문서화

## 24. 최종 체크리스트
- 확증 실험 결과(주가설) 확보
- 탐색 실험/민감도/아블레이션 결과 확보
- 통계 검정 + CI + 효과크기 + 다중비교 보정 완료
- Cost-matched 분석과 비동등 분석 분리 보고 완료
- 오류 분석(정성+정량) 완료
- 재현 패키지(설정/로그/집계/그림) + 제3자 재실행 증빙 완료
