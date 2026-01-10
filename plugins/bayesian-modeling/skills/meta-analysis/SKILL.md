---
name: meta-analysis
description: Bayesian meta-analysis models including fixed effects, random effects, and network meta-analysis with Stan and JAGS implementations.
---

# Meta-Analysis Models

## Fixed Effects Meta-Analysis

### Stan
```stan
data {
  int<lower=0> K;           // Number of studies
  vector[K] y;              // Effect estimates
  vector<lower=0>[K] se;    // Standard errors
}
parameters {
  real theta;               // Common effect
}
model {
  theta ~ normal(0, 10);
  y ~ normal(theta, se);
}
```

### JAGS
```
model {
  for (i in 1:K) {
    y[i] ~ dnorm(theta, prec[i])
    prec[i] <- pow(se[i], -2)
  }
  theta ~ dnorm(0, 0.0001)
}
```

## Random Effects Meta-Analysis

### Stan (Non-centered, recommended)
```stan
data {
  int<lower=0> K;
  vector[K] y;
  vector<lower=0>[K] se;
}
parameters {
  real mu;                  // Overall mean
  real<lower=0> tau;        // Between-study SD
  vector[K] eta;            // Study effects (standardized)
}
transformed parameters {
  vector[K] theta = mu + tau * eta;
}
model {
  // Priors
  mu ~ normal(0, 10);
  tau ~ cauchy(0, 0.5);     // Half-Cauchy
  eta ~ std_normal();

  // Likelihood
  y ~ normal(theta, se);
}
generated quantities {
  real theta_new = normal_rng(mu, tau);  // Predictive
  real I2 = square(tau) / (square(tau) + mean(square(se)));
}
```

### JAGS
```
model {
  for (i in 1:K) {
    y[i] ~ dnorm(theta[i], prec[i])
    prec[i] <- pow(se[i], -2)
    theta[i] ~ dnorm(mu, tau.theta)
  }

  mu ~ dnorm(0, 0.0001)
  tau.theta <- pow(sigma.theta, -2)
  sigma.theta ~ dunif(0, 10)

  # Heterogeneity
  tau2 <- pow(sigma.theta, 2)
}
```

## Binary Outcomes

### Stan (Log-Odds)
```stan
data {
  int<lower=0> K;
  array[K] int<lower=0> r1;   // Events in treatment
  array[K] int<lower=0> n1;   // Total in treatment
  array[K] int<lower=0> r2;   // Events in control
  array[K] int<lower=0> n2;   // Total in control
}
parameters {
  real d;                     // Overall log-OR
  real<lower=0> tau;
  vector[K] delta;            // Study-specific log-OR
  vector[K] mu;               // Baseline log-odds
}
model {
  d ~ normal(0, 10);
  tau ~ cauchy(0, 0.5);
  delta ~ normal(d, tau);
  mu ~ normal(0, 10);

  r2 ~ binomial_logit(n2, mu);
  r1 ~ binomial_logit(n1, mu + delta);
}
generated quantities {
  real OR = exp(d);
}
```

## Network Meta-Analysis (NMA)

### Stan (Consistency Model)
```stan
data {
  int<lower=0> K;             // Number of studies
  int<lower=0> T;             // Number of treatments
  array[K] int<lower=1> t1;   // Treatment 1 index
  array[K] int<lower=1> t2;   // Treatment 2 index
  vector[K] y;                // Effect estimate
  vector<lower=0>[K] se;
}
parameters {
  vector[T-1] d_raw;          // Basic parameters (vs reference)
  real<lower=0> tau;
  vector[K] delta;
}
transformed parameters {
  vector[T] d;
  d[1] = 0;                   // Reference treatment
  d[2:T] = d_raw;
}
model {
  d_raw ~ normal(0, 10);
  tau ~ cauchy(0, 0.5);

  for (k in 1:K) {
    delta[k] ~ normal(d[t2[k]] - d[t1[k]], tau);
    y[k] ~ normal(delta[k], se[k]);
  }
}
generated quantities {
  // Treatment rankings
  array[T] int rank;
  {
    array[T] int order = sort_indices_desc(d);
    for (t in 1:T) rank[order[t]] = t;
  }
}
```

## Publication Bias

### Selection Model (Stan)
```stan
data {
  int<lower=0> K;
  vector[K] y;
  vector<lower=0>[K] se;
  vector<lower=0,upper=1>[K] published;  // Publication indicator
}
parameters {
  real mu;
  real<lower=0> tau;
  vector[K] theta;
  real<lower=0> alpha;        // Selection severity
}
model {
  theta ~ normal(mu, tau);
  y ~ normal(theta, se);

  // Selection model: higher z-scores more likely published
  for (k in 1:K) {
    real z = y[k] / se[k];
    published[k] ~ bernoulli(Phi(alpha * z));
  }
}
```

## Key Statistics

```stan
generated quantities {
  // Heterogeneity
  real tau2 = square(tau);
  real I2 = tau2 / (tau2 + mean(square(se)));

  // Prediction interval
  real pred_lower = mu - 1.96 * tau;
  real pred_upper = mu + 1.96 * tau;

  // Probability effect > 0
  real prob_positive = 1 - normal_cdf(0 | mu, tau);
}
```

## Priors for Heterogeneity

| Context | tau prior |
|---------|-----------|
| Pharmacological | `half_normal(0, 0.5)` |
| Medical devices | `half_normal(0, 1)` |
| Behavioral | `half_cauchy(0, 1)` |
| Default | `half_cauchy(0, 0.5)` |
