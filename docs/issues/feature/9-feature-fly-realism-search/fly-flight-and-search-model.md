# 초파리 비행 모델과 기준선 탐색

초파리 비행을 실제 자유비행 측정값에 맞추고, 조준기를 바닥 정가운데로 옮기고, 규칙 기반 기준선에 탐색 패턴을 넣은 근거를 정리한 문서다. 결론은 세 가지다.

- 초파리는 직선 구간과 급선회를 번갈아 하며, 속도와 급선회 각도, 시간, 직선 구간 길이의 분포가 문헌값에 가깝다. 평균 속도는 약 0.3 m/s로 예전 모델(0.5 m/s)보다 느리지만, 급선회가 1초에 약 1.5번 일어나고 한 번에 평균 수천 °/s로 돈다.
- 탐색 패턴은 기준선에만 있다. 환경의 관측, 보상, 행동은 바뀌지 않았고, 강화학습 agent는 찾는 법도 스스로 배운다.
- 바닥 가운데 조준기에서 기준선은 40 에피소드를 모두 잡았다. 예전 제자리 회전 탐색은 같은 조건에서 초파리를 한 번도 보지 못했다.

## 범위

바꾼 것은 세 가지다.

- `flytracker/fly.py`: 초파리 비행 규칙과 값
- `flytracker/env.py`: 조준기 기본 자리를 바닥 정가운데(회전축 높이 0.1 m)로 옮김
- `flytracker/baseline.py`: 규칙 기반 기준선(`RuleAimer`)의 탐색

환경이 agent에게 주는 관측(13차원), 보상, 행동(yaw, pitch 각속도)은 그대로다. 기준선의 탐색은 학습 결과를 견줄 비교 대상이고, agent는 기준선 코드를 쓰지 않는다. 기준선은 관측 벡터와 카메라 시야각, 조준 범위만 쓴다. 초파리가 방 어디에 많은지 같은 시뮬레이터 내부 정보는 쓰지 않는다.

## 초파리 비행 값

근거 수준은 세 가지로 나눴다. "원문"은 논문 본문에서 직접 읽은 값이고, "2차 자료"는 그 논문을 인용한 다른 글이나 검색 요약에서 가져온 값이며, "가정"은 문헌값을 찾지 못해 정한 값이다. 값은 `FlyParams`의 기본값과 같다.

| 항목 | 값 | 출처 | 근거 수준 |
|---|---|---|---|
| 직선 구간 길이 분포 | p(l) ∝ l^−1.3, 0.01~2 m | Reynolds & Frye 2007: 10~100 mm에서 기울기 −1.3 | 원문 |
| 구간 속도 | 30 mm보다 짧은 구간 0.285 m/s, 긴 구간 0.356 m/s, 표준편차 0.19 m/s | Reynolds & Frye 2007 | 원문 |
| 급선회 각도 | 93 ± 27°, 20~180° | Muijres et al. 2015 (N = 44) | 원문 |
| 급선회 시간 | 49 ± 18 ms | Muijres et al. 2015 | 원문 |
| 급선회 중 속도 | 25% 떨어졌다가 0.1 s 시간 상수로 회복 | 떨어졌다 오른다는 사실만 원문(Muijres et al. 2015, Reynolds & Frye 2007). 크기는 가정 | 가정 |
| 같은 방향으로 도는 확률 | 0.8 | Reynolds & Frye 2007: 4번 넘게 같은 방향. 확률은 가정 | 가정 |
| 반응 지연 | 60 ms | Muijres et al. 2014를 인용한 연구에서 감각-운동 지연 약 60 ms | 2차 자료 |
| 회피 선회 시간 | 25 ms | Dickinson & Muijres 2016 총설: 회피 기동에서 기울였다 되돌리기까지 약 25 ms(날갯짓 5번) | 원문 |
| 위협 문턱, 회피 가속 | 1 m 안에서 거리 감소율 1/s, 0.35 m, 1.6배 0.3 s | 찾지 못함 | 가정 |
| 고도 변화 | 급선회마다 진행 방향 y 성분에 표준편차 0.2 잡음, 0.4에서 자름 | 찾지 못함 | 가정 |

Muijres 2014와 2015는 *D. hydei*를, Reynolds & Frye 2007은 *D. melanogaster*를 쟀다. 급선회는 실제로는 몸을 기울였다 되돌리며 도는 3차원 동작이지만, 이 모델은 진행 방향만 수평으로 돌린다. 각속도는 가운데에서 가장 빠른 종 모양이라 최댓값이 평균의 두 배다.

## 모델과 문헌 비교

모델이 문헌값을 따르는지는 같은 폴더의 `fly_stats.py`로 쟀다. 기본 방에서 위협 없이 초파리 200마리를 10초씩 날린 값이다. 급선회에는 벽을 피하는 선회도 들어 있다.

| 항목 | 모델 | 문헌 |
|---|---|---|
| 속도 | 평균 0.273 m/s, 표준편차 0.164 | 구간 시작 속도 0.285~0.356 m/s, 표준편차 약 0.19 (Reynolds & Frye 2007) |
| 급선회 빈도 | 1.53회/s | 1.37회/s (Censi et al. 2013, 2 m 경기장, 초파리 88마리, 5 cm/s 넘게 난 4,814초 동안 6,613번) |
| 급선회 각도 | 98 ± 31° | 93 ± 27° (Muijres et al. 2015) |
| 급선회 시간 | 55 ± 18 ms (10 ms 단위로 잼) | 49 ± 18 ms (Muijres et al. 2015) |
| 최대 각속도 | 중앙값 3,670°/s | 1,000°/s 넘음 (Frye & Dickinson 2004 총설, 검색 요약) |
| 급선회 사이 거리 | 10~100 mm 로그 기울기 −1.23 | −1.3 (Reynolds & Frye 2007) |
| 같은 방향 연속 | 평균 3.2번, 4번 이상인 묶음 34% | 4번 넘게 이어짐 (Reynolds & Frye 2007) |

예전 모델은 0.5 m/s 고정 속도에 1초에 한 번 60~120°를 고르게 돌았다. 속도는 문헌보다 빨랐지만 변화가 없었고, 급선회 사이 거리가 지수 분포라서 짧은 구간과 긴 구간이 섞이는 모양이 나오지 않았다.

## 기준선 탐색

기준선은 초파리가 보이면 화면 좌표에 비례해 조준선을 돌린다. 보이지 않을 때는 두 단계로 찾는다.

1. 국소 탐색: 마지막으로 본 방향(datum)으로 돌린 뒤, 그 방향을 가운데 두고 8자를 그린다. 8자는 yaw와 pitch의 주파수 비가 1:2인 Lissajous 곡선이고 한 바퀴는 1.6 s다. 첫 바퀴의 yaw 진폭은 15°이고 한 바퀴마다 15°씩 늘려 45°까지 그린다. datum에서 시작해 점점 넓히는 생각은 IAMSAR의 확장 사각형 탐색과 섹터 탐색에서 가져왔다.
2. 전역 탐색: 한 번도 본 적이 없거나 국소 탐색으로 못 찾으면, yaw를 최대 각속도의 90%로 돌려 360°를 훑고 한 바퀴마다 pitch 띠를 바꾼다. 띠는 바닥(−10°)부터 세로 시야각(40°)에서 겹침 5°를 뺀 간격으로 쌓아 10°, 45°, 80°다. 훑는 폭만큼 띄워 평행하게 덮는 것은 Koopman 탐색 이론의 평행 탐색과 같다.

띠 순서는 처음에 초파리가 많이 있는 높이(바닥 가운데에서 본 높이각 중앙값 51°)부터 훑도록 정했다가 되돌렸다. 그 분포는 시뮬레이터만 아는 정보라서, 기준선이 agent보다 많은 정보를 쓰게 되기 때문이다. 이 순서로 바꾸면 처음 발견까지 평균 1.41초로 빨라지지만 쓰지 않는다.

같은 seed 0~39로 견준 결과는 다음과 같다.

| 기준선 | 포획 | 처음 발견까지 | 포획까지 | 보인 시간 비율 |
|---|---|---|---|---|
| 예전: 수평으로 제자리 회전 | 0/40 | 한 번도 못 봄 | 없음 | 0% |
| 새 탐색 | 40/40 | 평균 3.69 s | 평균 4.37 s | 18% |

예전 탐색은 pitch를 0°로 맞추고 돌아서, 바닥 높이 0.1 m의 카메라로는 세로 ±20° 안만 본다. 초파리는 대부분 그보다 높이 난다. 조준기가 앞쪽 벽 앞에 있던 #7에서는 기준선이 평균 1.92초 만에 잡았으므로, 바닥 가운데로 옮긴 것만으로 과제가 어려워졌다.

## 한계

아직 확인하지 못한 것이 있다.

- 반응 지연 60 ms는 Muijres et al. 2014 원문을 읽지 못해 그 논문을 인용한 글에서 가져왔다. 회피할 때의 가속과 위협 문턱은 문헌값이 없다.
- 고도 변화 통계를 찾지 못했다.

이번 변경 범위 밖에 남은 것도 있다.

- 초파리 위협 규칙: 고정 포대는 다가오지 않아서, 위 40 에피소드에서 비상시는 한 번도 일어나지 않았다. 고정 포대에 맞는 위협 규칙은 아직 정하지 않았다.

## 참고 문헌

- Reynolds, A. M., Frye, M. A. (2007). Free-flight odor tracking in *Drosophila* is consistent with an optimal intermittent scale-free search. *PLoS ONE* 2: e354. https://pmc.ncbi.nlm.nih.gov/articles/PMC1831497/
- Muijres, F. T., Elzinga, M. J., Iwasaki, N. A., Dickinson, M. H. (2015). Body saccades of *Drosophila* consist of stereotyped banked turns. *J. Exp. Biol.* 218: 864–875. https://resolver.caltech.edu/CaltechAUTHORS:20150217-123946070
- Muijres, F. T., Elzinga, M. J., Melis, J. M., Dickinson, M. H. (2014). Flies evade looming targets by executing rapid visually directed banked turns. *Science* 344: 172–177. https://authors.library.caltech.edu/records/fgsdt-n4t54
- Censi, A., Straw, A. D., Sayaman, R. W., Murray, R. M., Dickinson, M. H. (2013). Discriminating external and internal causes for heading changes in freely flying *Drosophila*. *PLoS Comput. Biol.* 9: e1002891. https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002891
- Dickinson, M. H., Muijres, F. T. (2016). The aerodynamics and control of free flight manoeuvres in *Drosophila*. *Phil. Trans. R. Soc. B* 371: 20150388. https://pmc.ncbi.nlm.nih.gov/articles/PMC4992712/
- Maximally efficient prediction in the early fly visual system may support evasive flight maneuvers (2021). *PLoS Comput. Biol.* https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1008965
- Koopman, B. O. (1956). The theory of search. I. Kinematic bases. *Operations Research* 4: 324–346. III. The optimum distribution of searching effort (1957). *Operations Research* 5: 613–626.
- IMO/ICAO. *IAMSAR Manual*, Volume II: Mission co-ordination. 확장 사각형, 섹터, 평행 탐색 패턴.
- Hwang, K., Seo, Y.-H., Ahn, J., Kim, P., Jeong, K.-H. (2017). Frequency selection rule for high definition and high frame rate Lissajous scanning. *Sci. Rep.* 7: 14075. https://pmc.ncbi.nlm.nih.gov/articles/PMC5658369/
