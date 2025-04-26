### Experiment 0

Experiment 0 involves evaluation on a fairly fixed environment (still some randomization in maneuvers)

#### Goals

1. train Q-Table Agent on this environment

2. Evaluate the following agents

- trained Q-Table

- do nothing agent 

- random agent

- basic revisit agent 

3. compare agent evaluation metrics


#### Metrics [per simulation]

1. final reward

2. unpropagated mean catalog state covariance 

3. propagated mean catalog state covariance 

4. percent of maneuvers detected

5. percent of satellites tracked 

5. total tasks issued

6. tasks dropped (different categories)

7. lost objects? 


### Training Script

python -m scripts.experiment0.qt-training


### Evaluation Scripts