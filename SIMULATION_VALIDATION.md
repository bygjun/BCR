# BCR 실험계획 가상 시뮬레이션 검증

본 문서는 `/Users/juno/github/BCR/EXPERIMENT_PLAN.md`를 대상으로 한 **가상(Monte Carlo) 검증 결과**다.
실제 데이터셋 성능이 아니라, 계획의 통계/프로토콜 타당성을 점검하기 위한 모의 실험이다.

## 실행 방법
```bash
python3 /Users/juno/github/BCR/simulate_plan_validation.py
```

## 시뮬레이션 설정
- 반복 횟수: 1,200 trials/scenario
- 데이터셋: HotpotQA, 2WikiMultiHopQA, MuSiQue, MultiHop-RAG
- Seed 반복: 5
- 평가 기준:
- H1: `Primary endpoint(ΔF1@B2, cost-matched)` 유의성(p<0.05 & CI lower > 0)
- H3: Error Localization F1 개선 유의성
- H2: BCR vs Full-Rerun의 Cost-per-Gain 우세 확률
- 비용 동등 필터: `0.95 <= C_method/C_ref <= 1.05`

## 결과
| Scenario | Valid Trials | Cost-Matched Kept | Mean Macro ΔF1 | H1 Sig Rate | H1 Target Pass | H3 Sig Rate | H2 CPG Win Rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| A. Expected Effect / Stable Cost(sd=0.02) | 100.0% | 98.7% | 0.0157 | 100.0% | 25.9% | 100.0% | 74.4% |
| B. Expected Effect / Volatile Cost(sd=0.04) | 100.0% | 79.0% | 0.0156 | 100.0% | 22.8% | 100.0% | 74.6% |
| C. Null Effect / Stable Cost(sd=0.02) | 100.0% | 98.8% | 0.0000 | 2.4% | 0.0% | 2.5% | N/A |

## 해석
- 계획의 주가설(H1) 검정 구조는 모의환경에서 높은 검출력을 보였다.
- Null 시나리오의 H1/H3 유의율이 약 2~3% 수준으로, 과도한 오탐은 관찰되지 않았다.
- 비용 변동성이 커질수록(0.02 -> 0.04) cost-matched 통과율은 감소(98.7% -> 79.0%)하지만, 주효과 검출 자체는 유지됐다.
- H2는 기대효과 시나리오에서 약 74% 수준으로 BCR의 비용 효율 우세 가능성을 시사한다.
- `H1 Target Pass`(데이터셋별 최소개선 동시충족률)가 22~26%로 낮아, 데이터셋별 최소치 기준은 보수적으로 재조정할 여지가 있다.

## 검증 결론
- 현재 계획은 **주가설 검정 구조와 비용동등 비교 프레임** 측면에서 타당성이 높다.
- 다만 데이터셋별 최소개선 기준은 지나치게 엄격할 수 있으므로, 보조 성공기준으로 유지하거나 완화값을 추가하는 것이 안전하다.

## 주의
- 본 결과는 가정 기반 시뮬레이션이며, 실제 데이터 분포/모델 편향/도구 장애 패턴을 완전히 반영하지 않는다.
- 실제 실험 전, dev split에서 분산 추정치를 갱신해 재시뮬레이션하는 것을 권장한다.
