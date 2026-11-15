# SAC 설명

SAC(Soft Actor-Critic)는 연속 행동을 다루는 강화학습 알고리즘이다. issue #35는 조준기를 SAC로 학습한다. DQN과 가장 크게 다른 점은 두 가지다. 첫째, 관측을 받아 행동의 확률분포를 내는 신경망(actor)을 따로 둔다. 둘째, 매 step의 보상에 그 분포가 넓을수록 커지는 보너스를 더해 학습한다.

## 학습 대상

조준기는 방 바닥 가운데에 고정된 카메라이고, 학습하는 agent다. 조준기는 좌우 회전(yaw)과 위아래 회전(pitch)만 할 수 있다. 카메라가 바라보는 방향을 조준선이라 한다.

step은 조준기가 행동을 한 번 고르는 단위이고, 0.02초다. 방을 나는 초파리를 조준선 3° 안에 0.2초(10 step) 동안 잡아 두면 포획이다. 에피소드는 포획하거나 10초(500 step)가 지나면 끝난다.

관측은 13차원이다. 초파리가 화면에 보이는지(1), 보이면 화면 좌표(2)와 거리(1), 마지막으로 본 방향(3)과 놓친 뒤 지난 시간(1), 조준선의 방향(3)과 회전 속도(2)가 들어 있다. 초파리가 움직이는 속도는 관측에 없다.

행동은 yaw 목표 각속도와 pitch 목표 각속도 두 개이고, 둘 다 −1~1의 실수다. 조준선의 실제 회전 속도는 각가속도 제한 안에서 목표 각속도를 따라간다.

## actor와 critic

DQN의 Q network는 행동마다 Q값을 내고, 가장 큰 행동을 고른다. DQN에서 Q값은 어떤 관측에서 그 행동을 했을 때 앞으로 받을 보상 합의 예상치다. SAC의 Q값은 여기에 entropy 보너스가 더해진다("critic 손실" 절). 가장 큰 Q값을 고르는 방식은 행동이 몇 개뿐일 때만 쓸 수 있다. 조준기의 행동은 실수 두 개라서 후보가 끝없이 많고, Q값이 가장 큰 행동을 찾을 수 없다.

그래서 SAC는 신경망을 두 종류로 나눈다.

| 신경망 | 입력 | 출력 | 학습 방향 |
|---|---|---|---|
| actor | 관측 | 행동의 분포 | 분포에서 뽑은 행동에 critic이 매긴 Q값이 커지고, 분포가 너무 좁아지지 않도록 |
| critic | 관측과 행동 | Q값 | 받은 보상과 다음 관측의 Q값으로 만든 목표값에 맞도록. DQN의 Q network처럼 목표값과의 차이 제곱을 줄인다 |

actor가 행동을 고르고 critic이 그 행동의 Q값을 매긴다. 행동을 내는 신경망과 평가하는 신경망을 함께 학습하므로 actor-critic이라고 부른다. critic은 두 개를 쓰고, 이유는 "DQN 계열 장치" 절에 있다.

## entropy 보너스

actor는 정규분포의 평균 $\mu_\phi(s)$와 표준편차 $\sigma_\phi(s)$를 낸다. 그 정규분포에서 뽑은 값 $u$를 tanh에 넣어 −1~1 안으로 맞춘 것이 행동이다. 여기서 $s$는 관측이고 $\phi$는 actor의 가중치다. 이렇게 만든 행동의 분포를 actor의 정책 $\pi_\phi$라 하고, $\pi_\phi(a \mid s)$는 관측 $s$에서 행동 $a$가 뽑힐 확률 밀도다.

entropy는 분포가 얼마나 넓게 퍼졌는지를 나타내는 값이다.

$$
\mathcal{H}\big(\pi_\phi(\cdot \mid s)\big) = -\,\mathbb{E}_{a \sim \pi_\phi(\cdot \mid s)}\big[\log \pi_\phi(a \mid s)\big]
$$

| 항 | 뜻 |
|---|---|
| $\pi_\phi(a \mid s)$ | 관측 $s$에서 행동 $a$가 뽑힐 확률 밀도 |
| $\log \pi_\phi(a \mid s)$ | 그 밀도의 로그. 분포가 좁으면 뽑힌 행동의 밀도가 높아서 이 값이 크다 |
| $\mathbb{E}_{a \sim \pi_\phi(\cdot \mid s)}[\,\cdot\,]$ | 분포에서 행동을 뽑았을 때의 기댓값 |
| 맨 앞의 $-$ | 부호를 뒤집어, 분포가 넓을수록 큰 값이 되게 한다 |

분포가 좁을수록 entropy는 작아진다. 연속 분포의 밀도는 1보다 클 수 있어서, 분포가 좁으면 $\log \pi_\phi$가 양수가 되고 entropy는 음수가 된다.

SAC가 키우려는 학습 목표는 매 step의 보상에 entropy 보너스를 더한 값을 할인해서 합한 것이다.

$$
J(\phi) = \mathbb{E}\left[\sum_{t=0}^{T} \gamma^{t}\Big(r_t + \alpha\,\mathcal{H}\big(\pi_\phi(\cdot \mid s_t)\big)\Big)\right]
$$

| 항 | 뜻 |
|---|---|
| $t$, $T$ | step 번호와 에피소드의 마지막 step |
| $r_t$ | step $t$에 받은 보상 |
| $\gamma^{t}$ | 먼 미래의 값을 덜 쳐주는 할인. $\gamma = 0.99$ |
| $\alpha\,\mathcal{H}(\cdot)$ | entropy 보너스. entropy 계수 $\alpha$가 보너스의 크기를 정한다 |
| $\mathbb{E}[\,\cdot\,]$ | 정책대로 에피소드를 여러 번 돌렸을 때의 평균 |

DQN의 목표는 이 식에서 entropy 보너스를 뺀 것이다. 보너스가 있으니 actor는 한 가지 행동으로 일찍 굳지 않고 여러 행동을 계속 시도한다. DQN은 ε-greedy로, 곧 일정 확률로 무작위 행동을 골라 탐색하지만, SAC에서는 이 보너스가 탐색을 맡는다. 이름의 Soft가 이 보너스를 가리킨다.

$\alpha$는 1.0에서 시작해 학습 중에 자동으로 바뀐다. 기준은 목표 entropy $\bar{\mathcal{H}}$다. 분포의 entropy가 목표보다 작으면, 곧 분포가 목표보다 좁으면 $\alpha$가 커져 분포를 다시 넓힌다. 목표보다 넓으면 $\alpha$가 작아진다. 계산은 "α 손실" 절에 있다.

목표 entropy $\bar{\mathcal{H}}$는 행동 차원 수에 −1을 곱한 값이고, 조준기는 −2다. 행동 차원마다 entropy가 −1인 셈이다. tanh를 무시하고 어림하면 차원마다 표준편차가 약 0.09인 정규분포다. 행동 범위 −1~1에 견주면 좁지만 한 점은 아니다. 목표 entropy를 정하는 이 방식은 참고 문헌의 Soft Actor-Critic Algorithms and Applications가 쓴 경험칙이다.

학습이 끝난 뒤 평가할 때는 분포에서 뽑지 않는다. 평균 $\mu_\phi(s)$를 tanh에 넣은 값을 행동으로 쓴다.

## DQN 계열 장치

- off-policy다. 모은 경험을 replay buffer에 쌓아 두고 여러 번 꺼내 학습한다.
- target network를 둔다. target network는 critic의 복사본이고, critic마다 하나씩 있다. 갱신 방식은 DQN과 다르다. DQN은 일정 step마다 통째로 복사하지만, SAC는 step마다 target network의 가중치를 critic 쪽으로 0.5%씩 옮긴다.
- critic을 두 개 학습한다. critic의 목표값을 만들 때 다음 관측의 Q값은 두 target network 중 작은 값을 쓴다. Q값을 실제보다 크게 잡는 문제를 줄이려는 장치다. Double DQN과 방식은 다르지만 목적은 같다.

## 손실 함수

gradient step은 신경망의 가중치를 한 번 고치는 것이다. 조준기가 행동을 고르는 step과는 다른 단위이고, 학습이 시작된 뒤로는 step마다 gradient step을 한 번 한다. SAC는 gradient step 한 번에 손실 함수 세 개를 줄인다. 세 손실 함수는 알고리즘이 정해 둔 것이고, 사람이 고르는 것은 보상이다. gradient step 한 번의 순서는 아래와 같다.

1. replay buffer에서 경험 256개를 무작위로 꺼낸다.
2. critic 손실로 critic 두 개를 고친다.
3. actor 손실로 actor를 고친다.
4. α 손실로 $\alpha$를 고친다.
5. target network를 critic 쪽으로 조금 옮긴다.

학습에 쓰는 라이브러리 Stable-Baselines3는 α 손실을 critic보다 먼저 계산한다. 그래도 이 gradient step의 critic과 actor 손실에는 α를 고치기 전의 값을 쓰므로, 결과는 위 순서와 같다.

아래 식에 쓰는 기호다.

| 기호 | 뜻 |
|---|---|
| $s$, $a$, $r$, $s'$ | 꺼낸 경험 하나의 관측, 그때 한 행동, 받은 보상, 다음 관측 |
| $d$ | 포획으로 에피소드가 끝났으면 1, 아니면 0. 10초가 지나 끊긴 경우도 0이다 |
| $\pi_\phi$ | actor의 정책. $\phi$는 actor의 가중치 |
| $\theta_1$, $\theta_2$ | critic 두 개의 가중치. $Q_{\theta_i}$는 critic $i$가 매기는 Q값 |
| $\bar\theta_1$, $\bar\theta_2$ | target network 두 개의 가중치. $Q_{\bar\theta_i}$는 target network $i$가 매기는 Q값 |
| $\alpha$ | entropy 계수 |
| $\gamma$ | 할인율, 0.99 |
| $B$ | 한 번에 꺼내는 경험 수(batch 크기), 256 |

### critic 손실

critic이 맞춰야 할 목표값 $y$부터 만든다.

$$
y = r + \gamma\,(1 - d)\Big(\min_{i=1,2} Q_{\bar\theta_i}(s', a') - \alpha \log \pi_\phi(a' \mid s')\Big), \qquad a' \sim \pi_\phi(\cdot \mid s')
$$

| 항 | 뜻 |
|---|---|
| $r$ | 이번 step에 받은 보상 |
| $\gamma\,(1 - d)$ | 다음 관측의 값을 할인해서 더한다. 포획으로 끝났으면 $d = 1$이라 더하지 않는다 |
| $a'$ | 다음 관측 $s'$에서 지금 actor가 새로 뽑은 행동. replay buffer에 든 행동이 아니다 |
| $\min_{i} Q_{\bar\theta_i}(s', a')$ | 다음 관측에서 앞으로 받을 값. target network 두 개 중 작은 값을 쓴다 |
| $-\alpha \log \pi_\phi(a' \mid s')$ | 다음 관측에서 받을 entropy 보너스 |

10초가 지나 끊긴 경우는 $d = 0$으로 둔다. 시간 제한으로 끊겼을 뿐 그 뒤에도 보상은 이어질 수 있었으므로, 다음 관측의 값을 그대로 더한다.

DQN의 목표값 $r + \gamma\,(1 - d) \max_{a'} Q(s', a')$와 견주면 차이가 두 가지다. 행동이 연속이라 $\max$를 구할 수 없으므로 actor가 뽑은 $a'$로 대신하고, entropy 보너스를 더한다. 목표값에 entropy 보너스가 들어가므로, SAC의 Q값은 앞으로 받을 보상과 entropy 보너스를 함께 더한 값의 예상치다.

critic 손실은 두 critic이 각각 $y$와 얼마나 다른지를 제곱해 평균 낸 값이다.

$$
L_Q = \frac{1}{2} \sum_{i=1}^{2} \frac{1}{B} \sum_{\text{batch}} \big(Q_{\theta_i}(s, a) - y\big)^2
$$

| 항 | 뜻 |
|---|---|
| $Q_{\theta_i}(s, a)$ | critic $i$가 지금 매기는 Q값 |
| $\big(Q_{\theta_i}(s, a) - y\big)^2$ | 목표값과의 차이를 제곱한 값. DQN의 손실과 같은 모양이다 |
| $\frac{1}{B} \sum_{\text{batch}}$ | 꺼낸 경험 256개의 평균 |
| $\frac{1}{2} \sum_{i=1}^{2}$ | 두 critic의 손실을 더하고 반으로 나눈다 |

$y$는 상수로 둔다. $y$는 critic이 따라갈 답이므로, 답 쪽을 움직여 손실을 줄이면 안 되기 때문이다. 그래서 $y$를 거쳐 target network나 actor로 gradient가 흐르지 않고, critic 손실로는 critic 두 개만 고친다.

### actor 손실

actor는 꺼낸 경험의 관측 $s$마다 행동을 새로 뽑는다. 다음 관측 $s'$에서 뽑은 행동은 $a'$, 지금 관측 $s$에서 뽑은 행동은 $\tilde a$로 구분한다.

$$
\tilde a = \tanh(u), \qquad u = \mu_\phi(s) + \sigma_\phi(s) \odot \xi, \qquad \xi \sim \mathcal{N}(0, I)
$$

$$
L_\pi = \frac{1}{B} \sum_{\text{batch}} \Big(\alpha \log \pi_\phi(\tilde a \mid s) - \min_{i=1,2} Q_{\theta_i}(s, \tilde a)\Big)
$$

| 항 | 뜻 |
|---|---|
| $\mu_\phi(s)$, $\sigma_\phi(s)$ | actor가 낸 평균과 표준편차 |
| $\xi$ | 표준정규분포에서 뽑은 잡음. $\odot$는 원소끼리의 곱이다 |
| $\tilde a$ | 지금 actor가 뽑은 행동. replay buffer에 든 행동 $a$가 아니다 |
| $-\min_{i} Q_{\theta_i}(s, \tilde a)$ | 이 항을 줄이면 critic이 높게 보는 행동 쪽으로 $\mu_\phi(s)$가 옮겨 간다 |
| $\alpha \log \pi_\phi(\tilde a \mid s)$ | 이 항을 줄이면 뽑힌 행동의 밀도가 낮아지는 쪽, 곧 $\sigma_\phi(s)$가 커져 분포가 넓어지는 쪽으로 간다 |

$-\min_i Q$ 항은 좋은 행동 쪽으로 분포의 중심을 옮기고, $\alpha \log \pi_\phi$ 항은 분포가 한 점으로 좁아지는 것을 막는다. 두 항 사이의 무게를 $\alpha$가 정한다.

무작위성을 $\xi$에만 두는 이유는 gradient 때문이다. 그러면 $\tilde a$가 $\mu_\phi$와 $\sigma_\phi$로 미분할 수 있는 함수가 되어, Q값의 gradient가 $\tilde a$를 거쳐 actor의 가중치까지 흐른다. 이 방법을 reparameterization trick이라 한다. actor 손실로는 actor의 가중치 $\phi$만 고치고 critic은 그대로 둔다.

$\log \pi_\phi(\tilde a \mid s)$는 정규분포의 로그 밀도에 tanh가 만든 변화를 반영한 값이다.

$$
\log \pi_\phi(\tilde a \mid s) = \log \mathcal{N}\big(u;\, \mu_\phi(s), \sigma_\phi(s)\big) - \sum_{j=1}^{2} \log\big(1 - \tanh^2(u_j)\big)
$$

| 항 | 뜻 |
|---|---|
| $\log \mathcal{N}\big(u;\, \mu_\phi(s), \sigma_\phi(s)\big)$ | tanh에 넣기 전 값 $u$가 정규분포에서 뽑힐 로그 밀도 |
| $j$ | 행동의 차원. 1은 yaw, 2는 pitch |
| $-\log\big(1 - \tanh^2(u_j)\big)$ | tanh 보정. 늘 0 이상이다 |

tanh는 큰 값을 −1과 1 근처로 모은다. 값이 모인 자리는 밀도가 높아지므로, tanh 보정이 그만큼 $\log \pi_\phi$를 올려 준다.

### α 손실

$$
L_\alpha = \frac{1}{B} \sum_{\text{batch}} -\log\alpha \,\Big(\log \pi_\phi(\tilde a \mid s) + \bar{\mathcal{H}}\Big), \qquad \bar{\mathcal{H}} = -2
$$

| 항 | 뜻 |
|---|---|
| $\log\alpha$ | 실제로 학습하는 값. $\alpha = e^{\log\alpha}$라서 $\alpha$는 늘 양수다 |
| $-\log \pi_\phi(\tilde a \mid s)$ | 지금 분포의 entropy를 뽑은 행동 하나로 잰 값 |
| $\bar{\mathcal{H}}$ | 목표 entropy. 행동 차원 수 2에 −1을 곱한 값 |
| 괄호 안 | 목표 entropy에서 지금 entropy를 뺀 값. 분포가 목표보다 좁으면 양수다 |

괄호 안이 양수면 손실은 $-\log\alpha$에 양수를 곱한 꼴이라서, $\log\alpha$가 커질수록 손실이 작아진다. 그래서 학습은 $\alpha$를 키운다. $\alpha$가 커지면 actor 손실에서 entropy 항의 무게가 커져 분포가 넓어진다. 괄호 안이 음수면 반대로 $\alpha$가 작아진다.

### target network 갱신

$$
\bar\theta_i \leftarrow \tau\,\theta_i + (1 - \tau)\,\bar\theta_i, \qquad \tau = 0.005
$$

target network의 가중치 $\bar\theta_i$를 critic의 가중치 $\theta_i$ 쪽으로 0.5%만 옮긴다. 목표값 $y$가 gradient step마다 크게 흔들리지 않게 하려는 것이다.

### TensorBoard 기록

TensorBoard에는 `train/critic_loss`, `train/actor_loss`, `train/ent_coef`($\alpha$), `train/ent_coef_loss`가 기록된다. 지도학습과 달리 손실이 줄어든다고 정책이 좋아진다는 뜻은 아니다. 정책이 바뀌면 critic이 맞혀야 할 $y$도 바뀌어서 critic 손실은 오르내린다. 정책의 성능은 평가 에피소드의 포획률과 보상 합으로 판단한다.

## 학습 설정

강화학습 라이브러리 Stable-Baselines3 2.9.2의 SAC를 쓴다. frame stack은 최근 관측 몇 개를 이어 붙여 한 번에 넣는 것이다.

| 항목 | 값 | 정한 곳 (기본값은 Stable-Baselines3의 기본값) |
|---|---|---|
| frame stack | 1과 4. 4면 13차원 관측 4개를 이어 붙여 52차원 | issue #35 |
| 학습 길이 | 실행마다 1,000,000 step. 에피소드로 2,000개 이상 | issue #35 |
| 학습 실행 | frame stack 2가지 × 학습 seed 3개(0, 1, 2) = 6번 | issue #35 |
| 신경망 | actor와 critic 모두 은닉층 256, 256 | 기본값 |
| critic 수 | 2 | 기본값 |
| 학습률 | 0.0003 | 기본값 |
| batch 크기 $B$ | 256 | 기본값 |
| replay buffer | 경험 1,000,000개. 학습 길이와 같아서 버리는 경험이 없다 | 기본값 |
| 할인율 $\gamma$ | 0.99 | 기본값 |
| entropy 계수 $\alpha$ | 1.0에서 시작해 자동 조절. 목표 entropy $\bar{\mathcal{H}} = -2$ | 기본값 |
| target network 갱신 $\tau$ | 0.005, 곧 step마다 0.5% | 기본값 |
| 학습 시작 | 처음 100 step은 무작위 행동으로 replay buffer를 채운다. 그 뒤 step마다 gradient step을 한 번 하고, 탐색은 entropy 보너스가 맡는다 | 기본값 |

frame stack 4를 함께 돌리는 이유는 관측에 초파리가 움직이는 속도가 없어서다. 관측 4개를 이어 붙이면 초파리의 화면 좌표가 어떻게 변하는지에서 속도를 읽을 수 있다. 다만 화면 좌표의 변화에는 조준선이 돌아서 생긴 변화도 들어 있다. 이어 붙인 관측 4개에는 시점마다 조준선의 회전 속도도 들어 있어서, 그 변화를 빼고 초파리 자신의 움직임을 읽을 수 있다.

## 참고 문헌

- Haarnoja, T., Zhou, A., Abbeel, P., Levine, S. (2018). Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor. ICML.
- Haarnoja, T. 외 (2018). Soft Actor-Critic Algorithms and Applications. arXiv:1812.05905. α를 자동으로 조절하는 방법과 목표 entropy 규칙이 이 논문에 있다.
