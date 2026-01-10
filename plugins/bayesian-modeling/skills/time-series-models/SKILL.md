---
name: time-series-models
description: Bayesian time series models including AR, MA, ARMA, state-space models, and dynamic linear models in Stan and JAGS.
---

# Time Series Models

## AR(1) Model

### Stan
```stan
data {
  int<lower=0> T;
  vector[T] y;
}
parameters {
  real mu;
  real<lower=-1, upper=1> phi;  // Stationarity
  real<lower=0> sigma;
}
model {
  mu ~ normal(0, 10);
  phi ~ uniform(-1, 1);
  sigma ~ exponential(1);

  // Stationary initial distribution
  y[1] ~ normal(mu, sigma / sqrt(1 - phi^2));

  // AR(1) likelihood
  for (t in 2:T)
    y[t] ~ normal(mu + phi * (y[t-1] - mu), sigma);
}
```

### Vectorized Stan (Efficient)
```stan
model {
  y[1] ~ normal(mu, sigma / sqrt(1 - square(phi)));
  y[2:T] ~ normal(mu + phi * (y[1:(T-1)] - mu), sigma);
}
```

### JAGS
```
model {
  y[1] ~ dnorm(mu, tau / (1 - phi * phi))
  for (t in 2:T) {
    y[t] ~ dnorm(mu + phi * (y[t-1] - mu), tau)
  }
  mu ~ dnorm(0, 0.001)
  phi ~ dunif(-1, 1)
  tau ~ dgamma(0.001, 0.001)
  sigma <- 1/sqrt(tau)
}
```

## AR(p) Model

### Stan
```stan
data {
  int<lower=0> T;
  int<lower=1> P;  // AR order
  vector[T] y;
}
parameters {
  real mu;
  vector[P] phi;
  real<lower=0> sigma;
}
model {
  mu ~ normal(0, 10);
  phi ~ normal(0, 0.5);
  sigma ~ exponential(1);

  for (t in (P+1):T) {
    real pred = mu;
    for (p in 1:P)
      pred += phi[p] * (y[t-p] - mu);
    y[t] ~ normal(pred, sigma);
  }
}
```

## Local Level (Random Walk + Noise)

### Stan
```stan
data {
  int<lower=0> T;
  vector[T] y;
}
parameters {
  vector[T] mu;           // Latent state
  real<lower=0> sigma_y;  // Observation noise
  real<lower=0> sigma_mu; // State noise
}
model {
  sigma_y ~ exponential(1);
  sigma_mu ~ exponential(1);

  // State evolution (random walk)
  mu[1] ~ normal(y[1], sigma_y);
  mu[2:T] ~ normal(mu[1:(T-1)], sigma_mu);

  // Observations
  y ~ normal(mu, sigma_y);
}
```

## Local Linear Trend

### Stan
```stan
parameters {
  vector[T] mu;           // Level
  vector[T] delta;        // Trend
  real<lower=0> sigma_y;
  real<lower=0> sigma_mu;
  real<lower=0> sigma_delta;
}
model {
  // Level evolution
  mu[2:T] ~ normal(mu[1:(T-1)] + delta[1:(T-1)], sigma_mu);

  // Trend evolution
  delta[2:T] ~ normal(delta[1:(T-1)], sigma_delta);

  // Observations
  y ~ normal(mu, sigma_y);
}
```

## Seasonal Model

### Stan (Additive Seasonality)
```stan
data {
  int<lower=0> T;
  int<lower=2> S;  // Season length (e.g., 12 for monthly)
  vector[T] y;
}
parameters {
  vector[T] mu;
  vector[S-1] gamma_init;  // Initial seasonal effects
  real<lower=0> sigma_y;
  real<lower=0> sigma_mu;
  real<lower=0> sigma_gamma;
}
transformed parameters {
  vector[T] gamma;
  // Sum-to-zero constraint
  for (t in 1:(S-1))
    gamma[t] = gamma_init[t];
  gamma[S] = -sum(gamma_init);
  for (t in (S+1):T)
    gamma[t] = -sum(gamma[(t-S+1):(t-1)]) + normal_rng(0, sigma_gamma);
}
model {
  y ~ normal(mu + gamma, sigma_y);
}
```

## GARCH(1,1) (Volatility Clustering)

### Stan
```stan
parameters {
  real mu;
  real<lower=0> alpha0;
  real<lower=0, upper=1> alpha1;
  real<lower=0, upper=1-alpha1> beta1;
}
transformed parameters {
  vector<lower=0>[T] sigma2;
  sigma2[1] = alpha0 / (1 - alpha1 - beta1);
  for (t in 2:T)
    sigma2[t] = alpha0 + alpha1 * square(y[t-1] - mu) + beta1 * sigma2[t-1];
}
model {
  y ~ normal(mu, sqrt(sigma2));
}
```

## Diagnostics

- Check stationarity constraints (|phi| < 1 for AR)
- Examine residual autocorrelation (ACF/PACF)
- One-step-ahead predictions for model comparison
- Use `generated quantities` for forecasting
