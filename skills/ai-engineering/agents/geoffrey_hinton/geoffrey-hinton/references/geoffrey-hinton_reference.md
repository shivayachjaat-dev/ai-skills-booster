# Geoffrey Hinton Technical Reference

## Representation Learning, Distillation & AI Safety

Geoffrey Hinton's contributions (Backpropagation, Boltzmann Machines, Deep Belief Networks, Dropout, Knowledge Distillation, and Forward-Forward) form the conceptual backbone of modern neural networks.

### Core Theoretical Pillars

```
+------------------------------------------------------------------------+
|                      Hintonian Learning Paradigms                      |
|                                                                        |
|  [ Distributed Representations ] ---> Concepts as high-d thought vectors|
|                   |                                                    |
|                   v                                                    |
|  [ Knowledge Distillation ]      ---> Soft targets & dark knowledge    |
|                   |                                                    |
|                   v                                                    |
|  [ Biological Plausibility ]     ---> Forward-Forward vs Backprop      |
|                   |                                                    |
|                   v                                                    |
|  [ AI Existential Risk ]         ---> Instrumental convergence & safety|
+------------------------------------------------------------------------+
```

### Knowledge Distillation & Dark Knowledge

In a typical multi-class classifier, softmax probabilities on non-target classes (e.g. predicting 0.001 for "truck" and 0.000001 for "carrot" when target is "car") contain immense structural information about how the network categorizes reality.
$$q_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$$
Scaling temperature $T > 1$ softens the probability distribution, enabling a small student model to absorb the dark knowledge of massive teacher ensembles.

### Forward-Forward Algorithm vs Backpropagation

- **Backpropagation**: Mathematically exact gradient computation via reverse chain rule; requires perfect knowledge of forward activations and symmetric synaptic feedback (biologically implausible, high energy cost).
- **Forward-Forward**: Replaces backpropagation with two forward passes—one with positive (real) data and one with negative (generated/corrupted) data. Evaluates local layer goodness, enabling training on analog neuromorphic hardware without global backward pipelines.
