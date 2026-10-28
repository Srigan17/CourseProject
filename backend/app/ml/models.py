import numpy as np
import copy
from typing import Tuple, Dict, Any, Optional, List
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, ExtraTreesRegressor, RandomForestRegressor

def softmax(z: np.ndarray) -> np.ndarray:
    exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
    return exp_z / np.sum(exp_z, axis=1, keepdims=True)


class FedProxMLPClassifierImpl(MLPClassifier):
    """
    Internal scikit-learn MLPClassifier extension that injects the exact FedProx
    proximal regularization term (mu / 2) * ||w - w_global||^2 directly into
    backpropagation and loss computation for each local mini-batch step.
    """
    def __init__(
        self,
        hidden_layer_sizes: Tuple[int, ...] = (128, 64),
        activation: str = 'relu',
        solver: str = 'adam',
        alpha: float = 0.005,
        batch_size: int = 32,
        learning_rate_init: float = 0.01,
        max_iter: int = 1,
        random_state: int = 42
    ):
        super().__init__(
            hidden_layer_sizes=hidden_layer_sizes,
            activation=activation,
            solver=solver,
            alpha=alpha,
            batch_size=batch_size,
            learning_rate_init=learning_rate_init,
            max_iter=max_iter,
            random_state=random_state
        )
        self.mu_prox = 0.0
        self.ref_coefs: Optional[List[np.ndarray]] = None
        self.ref_intercepts: Optional[List[np.ndarray]] = None

    def set_reference_weights(self, coefs: List[np.ndarray], intercepts: List[np.ndarray], mu: float = 0.005):
        self.mu_prox = float(mu)
        self.ref_coefs = [c.copy() for c in coefs]
        self.ref_intercepts = [b.copy() for b in intercepts]

    def _backprop(self, X, y, sample_weight, activations, deltas, coef_grads, intercept_grads):
        loss, coef_grads, intercept_grads = super()._backprop(
            X, y, sample_weight, activations, deltas, coef_grads, intercept_grads
        )
        if self.mu_prox > 0 and self.ref_coefs is not None and self.ref_intercepts is not None:
            prox_loss = 0.0
            for i in range(len(self.coefs_)):
                diff_c = self.coefs_[i] - self.ref_coefs[i]
                diff_b = self.intercepts_[i] - self.ref_intercepts[i]
                coef_grads[i] += self.mu_prox * diff_c
                intercept_grads[i] += self.mu_prox * diff_b
                prox_loss += 0.5 * self.mu_prox * (np.sum(diff_c ** 2) + np.sum(diff_b ** 2))
            loss += prox_loss
        return loss, coef_grads, intercept_grads


class FederatedMLPClassifier:
    """
    Multi-Layer Perceptron Classifier with exact continuous parameter extraction,
    true FedProx proximal regularization in local backpropagation, and full compatibility
    with Differential Privacy (gradient/delta clipping + noise) and Paillier Additive
    Homomorphic Encryption.
    """
    def __init__(
        self,
        input_dim: int,
        num_classes: int,
        hidden_layer_sizes: Tuple[int, ...] = (128, 64),
        learning_rate: float = 0.01,
        alpha: float = 0.005,
        random_state: int = 42
    ):
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.hidden_layer_sizes = hidden_layer_sizes
        self.learning_rate = learning_rate
        self.alpha = alpha
        self.random_state = random_state
        self.mlp = FedProxMLPClassifierImpl(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver='adam',
            alpha=alpha,
            learning_rate_init=learning_rate,
            random_state=random_state
        )
        # Initialize internal architecture with dummy pass
        dummy_X = np.zeros((num_classes, input_dim))
        dummy_y = np.arange(num_classes)
        self.mlp.partial_fit(dummy_X, dummy_y, classes=dummy_y)

    def get_weights(self) -> np.ndarray:
        return np.concatenate([c.flatten() for c in self.mlp.coefs_] + [b.flatten() for b in self.mlp.intercepts_])

    def set_weights(self, flat_w: np.ndarray):
        idx = 0
        nc = []
        for c in self.mlp.coefs_:
            s = c.size
            nc.append(flat_w[idx:idx+s].reshape(c.shape))
            idx += s
        nb = []
        for b in self.mlp.intercepts_:
            s = b.size
            nb.append(flat_w[idx:idx+s].reshape(b.shape))
            idx += s
        self.mlp.coefs_ = nc
        self.mlp.intercepts_ = nb
        if hasattr(self.mlp, "_optimizer"):
            delattr(self.mlp, "_optimizer")

    def fit_local(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 12,
        lr: float = 0.01,
        batch_size: int = 32,
        mu_prox: float = 0.005,
        ref_weights: Optional[np.ndarray] = None,
        epoch_callback: Optional[Any] = None
    ) -> float:
        if len(X) == 0:
            return 0.0

        # Set reference weights for FedProx proximal regularization
        if ref_weights is not None and mu_prox > 0:
            idx = 0
            rc = []
            for c in self.mlp.coefs_:
                s = c.size
                rc.append(ref_weights[idx:idx+s].reshape(c.shape))
                idx += s
            rb = []
            for b in self.mlp.intercepts_:
                s = b.size
                rb.append(ref_weights[idx:idx+s].reshape(b.shape))
                idx += s
            self.mlp.set_reference_weights(rc, rb, mu=mu_prox)
        else:
            self.mlp.mu_prox = 0.0
            self.mlp.ref_coefs = None
            self.mlp.ref_intercepts = None

        self.mlp.batch_size = batch_size
        self.mlp.learning_rate_init = lr

        for ep in range(1, epochs + 1):
            perm = np.random.permutation(len(X))
            self.mlp.partial_fit(X[perm], y[perm])
            current_loss = float(self.mlp.loss_) if hasattr(self.mlp, "loss_") and self.mlp.loss_ is not None else 0.0
            if epoch_callback:
                epoch_callback(ep, epochs, current_loss)

        return float(self.mlp.loss_) if hasattr(self.mlp, "loss_") and self.mlp.loss_ is not None else 0.0

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.mlp.predict_proba(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.mlp.predict(X)


class FedProxMLPRegressorImpl(MLPRegressor):
    """
    Internal scikit-learn MLPRegressor extension with FedProx proximal regularization.
    """
    def __init__(
        self,
        hidden_layer_sizes: Tuple[int, ...] = (64, 32),
        activation: str = 'relu',
        solver: str = 'adam',
        alpha: float = 0.005,
        batch_size: int = 32,
        learning_rate_init: float = 0.01,
        max_iter: int = 1,
        random_state: int = 42
    ):
        super().__init__(
            hidden_layer_sizes=hidden_layer_sizes,
            activation=activation,
            solver=solver,
            alpha=alpha,
            batch_size=batch_size,
            learning_rate_init=learning_rate_init,
            max_iter=max_iter,
            random_state=random_state
        )
        self.mu_prox = 0.0
        self.ref_coefs: Optional[List[np.ndarray]] = None
        self.ref_intercepts: Optional[List[np.ndarray]] = None

    def set_reference_weights(self, coefs: List[np.ndarray], intercepts: List[np.ndarray], mu: float = 0.005):
        self.mu_prox = float(mu)
        self.ref_coefs = [c.copy() for c in coefs]
        self.ref_intercepts = [b.copy() for b in intercepts]

    def _backprop(self, X, y, sample_weight, activations, deltas, coef_grads, intercept_grads):
        loss, coef_grads, intercept_grads = super()._backprop(
            X, y, sample_weight, activations, deltas, coef_grads, intercept_grads
        )
        if self.mu_prox > 0 and self.ref_coefs is not None and self.ref_intercepts is not None:
            prox_loss = 0.0
            for i in range(len(self.coefs_)):
                diff_c = self.coefs_[i] - self.ref_coefs[i]
                diff_b = self.intercepts_[i] - self.ref_intercepts[i]
                coef_grads[i] += self.mu_prox * diff_c
                intercept_grads[i] += self.mu_prox * diff_b
                prox_loss += 0.5 * self.mu_prox * (np.sum(diff_c ** 2) + np.sum(diff_b ** 2))
            loss += prox_loss
        return loss, coef_grads, intercept_grads


class FederatedMLPRegressor:
    """
    Multi-Layer Perceptron Regressor for calorie expenditure prediction.
    Continuous parameter vector for Paillier Secure Aggregation and FedProx.
    """
    def __init__(
        self,
        input_dim: int,
        hidden_layer_sizes: Tuple[int, ...] = (64, 32),
        learning_rate: float = 0.01,
        alpha: float = 0.005,
        random_state: int = 42
    ):
        self.input_dim = input_dim
        self.hidden_layer_sizes = hidden_layer_sizes
        self.learning_rate = learning_rate
        self.alpha = alpha
        self.mlp = FedProxMLPRegressorImpl(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver='adam',
            alpha=alpha,
            learning_rate_init=learning_rate,
            random_state=random_state
        )
        dummy_X = np.zeros((2, input_dim))
        dummy_y = np.zeros(2)
        self.mlp.partial_fit(dummy_X, dummy_y)

    def get_weights(self) -> np.ndarray:
        return np.concatenate([c.flatten() for c in self.mlp.coefs_] + [b.flatten() for b in self.mlp.intercepts_])

    def set_weights(self, flat_w: np.ndarray):
        idx = 0
        nc = []
        for c in self.mlp.coefs_:
            s = c.size
            nc.append(flat_w[idx:idx+s].reshape(c.shape))
            idx += s
        nb = []
        for b in self.mlp.intercepts_:
            s = b.size
            nb.append(flat_w[idx:idx+s].reshape(b.shape))
            idx += s
        self.mlp.coefs_ = nc
        self.mlp.intercepts_ = nb
        if hasattr(self.mlp, "_optimizer"):
            delattr(self.mlp, "_optimizer")

    def fit_local(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 12,
        lr: float = 0.01,
        batch_size: int = 32,
        mu_prox: float = 0.005,
        ref_weights: Optional[np.ndarray] = None,
        epoch_callback: Optional[Any] = None
    ) -> float:
        if len(X) == 0:
            return 0.0

        if ref_weights is not None and mu_prox > 0:
            idx = 0
            rc = []
            for c in self.mlp.coefs_:
                s = c.size
                rc.append(ref_weights[idx:idx+s].reshape(c.shape))
                idx += s
            rb = []
            for b in self.mlp.intercepts_:
                s = b.size
                rb.append(ref_weights[idx:idx+s].reshape(b.shape))
                idx += s
            self.mlp.set_reference_weights(rc, rb, mu=mu_prox)
        else:
            self.mlp.mu_prox = 0.0
            self.mlp.ref_coefs = None
            self.mlp.ref_intercepts = None

        self.mlp.batch_size = batch_size
        self.mlp.learning_rate_init = lr

        for ep in range(1, epochs + 1):
            perm = np.random.permutation(len(X))
            self.mlp.partial_fit(X[perm], y[perm])
            current_loss = float(self.mlp.loss_) if hasattr(self.mlp, "loss_") and self.mlp.loss_ is not None else 0.0
            if epoch_callback:
                epoch_callback(ep, epochs, current_loss)

        return float(self.mlp.loss_) if hasattr(self.mlp, "loss_") and self.mlp.loss_ is not None else 0.0

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.mlp.predict(X)


class FederatedTreeEnsembleClassifier:
    """
    Federated Extra Trees / Random Forest Ensemble matching Akhmetov et al. (2025).
    Simulated hospitals train decision trees locally. The coordinator aggregates
    the decision trees into a unified global ensemble (FedEnsemble).
    """
    def __init__(self, model_type: str = "extra_trees", n_estimators_per_client: int = 35, random_state: int = 42):
        self.model_type = model_type
        self.n_estimators_per_client = n_estimators_per_client
        self.random_state = random_state
        self.global_ensemble = None

    def aggregate_client_models(self, client_models: List[Any]):
        if not client_models:
            return
        self.global_ensemble = copy.deepcopy(client_models[0])
        all_estimators = []
        for m in client_models:
            all_estimators.extend(m.estimators_)
        self.global_ensemble.estimators_ = all_estimators
        self.global_ensemble.n_estimators = len(all_estimators)

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.global_ensemble is None:
            raise RuntimeError("Ensemble not aggregated yet.")
        return self.global_ensemble.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.global_ensemble is None:
            raise RuntimeError("Ensemble not aggregated yet.")
        return self.global_ensemble.predict_proba(X)


class FederatedLogisticClassifier:
    """
    Multi-class Softmax Regression with exact flattened parameter vectors
    and true FedProx proximal regularization.
    """
    def __init__(self, input_dim: int, num_classes: int, random_state: int = 42):
        self.input_dim = input_dim
        self.num_classes = num_classes
        np.random.seed(random_state)
        self.W = np.random.randn(input_dim, num_classes) * 0.01
        self.b = np.zeros(num_classes)

    def get_weights(self) -> np.ndarray:
        return np.concatenate([self.W.flatten(), self.b])

    def set_weights(self, flat_weights: np.ndarray):
        w_size = self.input_dim * self.num_classes
        self.W = flat_weights[:w_size].reshape(self.input_dim, self.num_classes)
        self.b = flat_weights[w_size:]

    def fit_local(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 12,
        lr: float = 0.05,
        batch_size: int = 32,
        mu_prox: float = 0.0,
        ref_weights: Optional[np.ndarray] = None,
        epoch_callback: Optional[Any] = None
    ) -> float:
        num_samples = len(X)
        if num_samples == 0:
            return 0.0

        Y_onehot = np.zeros((num_samples, self.num_classes))
        Y_onehot[np.arange(num_samples), y.astype(int)] = 1.0

        ref_W = None
        ref_b = None
        if ref_weights is not None and mu_prox > 0:
            w_size = self.input_dim * self.num_classes
            ref_W = ref_weights[:w_size].reshape(self.input_dim, self.num_classes)
            ref_b = ref_weights[w_size:]

        last_loss = 0.0
        for ep in range(1, epochs + 1):
            indices = np.random.permutation(num_samples)
            X_shuffled = X[indices]
            Y_shuffled = Y_onehot[indices]

            for i in range(0, num_samples, batch_size):
                X_batch = X_shuffled[i:i + batch_size]
                Y_batch = Y_shuffled[i:i + batch_size]
                m = len(X_batch)

                logits = np.dot(X_batch, self.W) + self.b
                probs = softmax(logits)

                loss = -np.mean(np.sum(Y_batch * np.log(probs + 1e-12), axis=1))
                if mu_prox > 0 and ref_W is not None and ref_b is not None:
                    loss += 0.5 * mu_prox * (np.sum((self.W - ref_W)**2) + np.sum((self.b - ref_b)**2))
                last_loss = float(loss)

                grad_logits = (probs - Y_batch) / m
                grad_W = np.dot(X_batch.T, grad_logits)
                grad_b = np.sum(grad_logits, axis=0)

                # FedProx proximal gradient
                if mu_prox > 0 and ref_W is not None and ref_b is not None:
                    grad_W += mu_prox * (self.W - ref_W)
                    grad_b += mu_prox * (self.b - ref_b)

                self.W -= lr * (grad_W + 1e-4 * self.W)
                self.b -= lr * grad_b

            if epoch_callback:
                epoch_callback(ep, epochs, last_loss)

        return last_loss

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        logits = np.dot(X, self.W) + self.b
        return softmax(logits)

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)


class FederatedLinearRegressor:
    """
    Linear Regression with exact parameter vector extraction for FL, SecAgg, and FedProx.
    """
    def __init__(self, input_dim: int, random_state: int = 42):
        self.input_dim = input_dim
        np.random.seed(random_state)
        self.W = np.random.randn(input_dim) * 0.01
        self.b = 0.0

    def get_weights(self) -> np.ndarray:
        return np.append(self.W, self.b)

    def set_weights(self, flat_weights: np.ndarray):
        self.W = flat_weights[:-1]
        self.b = float(flat_weights[-1])

    def fit_local(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 12,
        lr: float = 0.01,
        batch_size: int = 32,
        mu_prox: float = 0.0,
        ref_weights: Optional[np.ndarray] = None
    ) -> float:
        num_samples = len(X)
        if num_samples == 0:
            return 0.0

        ref_W = None
        ref_b = None
        if ref_weights is not None and mu_prox > 0:
            ref_W = ref_weights[:-1]
            ref_b = float(ref_weights[-1])

        last_loss = 0.0
        for _ in range(epochs):
            indices = np.random.permutation(num_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]

            for i in range(0, num_samples, batch_size):
                X_batch = X_shuffled[i:i + batch_size]
                y_batch = y_shuffled[i:i + batch_size]
                m = len(X_batch)

                preds = np.dot(X_batch, self.W) + self.b
                error = preds - y_batch
                mse = float(np.mean(error ** 2))
                last_loss = mse

                grad_W = (2.0 / m) * np.dot(X_batch.T, error)
                grad_b = (2.0 / m) * np.sum(error)

                if mu_prox > 0 and ref_W is not None:
                    grad_W += mu_prox * (self.W - ref_W)
                    grad_b += mu_prox * (self.b - ref_b)

                self.W -= lr * (grad_W + 1e-4 * self.W)
                self.b -= lr * grad_b

        return last_loss

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.dot(X, self.W) + self.b
