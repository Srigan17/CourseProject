

    
        
        
        
        html {background-color: #fff}
        
        pycaret-fl/strategy/fedensemble.py · auto-fl-fit · GitFront
    
    
        
            
                auto-fl-fit /
                pycaret-fl /
                strategy /
                fedensemble.py
            

            
                
                    fedensemble.py
                    
                        Raw
                    
                
                
                    import numpy as np
from flwr.server.strategy import FedAvg

from flwr.server.client_proxy import ClientProxy
from typing import Callable, Dict, List, Optional, Tuple, Union
from flwr.common import (FitRes, MetricsAggregationFn,
                         NDArrays, Parameters, Scalar,
                         MetricsAggregationFn)
from flwr.common.logger import log
from logging import WARNING, INFO

import utils

WARNING_MIN_AVAILABLE_CLIENTS_TOO_LOW = &#34;&#34;&#34;
Setting `min_available_clients` lower than `min_fit_clients` or
`min_evaluate_clients` can cause the server to fail when there are too few clients
connected to the server. `min_available_clients` must be set to a value larger
than or equal to the values of `min_fit_clients` and `min_evaluate_clients`.
&#34;&#34;&#34;

# Flower strategy that picks the best model based on accuracy and loss function


def flower_strategy(models, accuracy_scores, loss_scores):
    # Calculate the average accuracy and loss scores for each model
    avg_accuracy = np.mean(accuracy_scores)
    avg_loss = np.mean(loss_scores)

    # Find the index of the model with the highest accuracy score
    best_accuracy_index = np.argmax(accuracy_scores)

    # Find the index of the model with the lowest loss score
    best_loss_index = np.argmin(loss_scores)

    # Check if the model with the highest accuracy score also has the lowest loss score
    if best_accuracy_index == best_loss_index:
        return models[best_accuracy_index]
    else:
        # Calculate the weighted score for each model based on accuracy and loss
        weighted_scores = (accuracy_scores - avg_accuracy) + \
            (avg_loss - loss_scores)

        # Find the index of the model with the highest weighted score
        best_weighted_index = np.argmax(weighted_scores)

        return models[best_weighted_index]


class FedEnsemble(FedAvg):
    def __init__(
        self,
        *,
        fraction_fit: float = 1.0,
        fraction_evaluate: float = 1.0,
        min_fit_clients: int = 2,
        min_evaluate_clients: int = 2,
        min_available_clients: int = 2,
        evaluate_fn: Optional[
            Callable[
                [int, NDArrays, Dict[str, Scalar]],
                Optional[Tuple[float, Dict[str, Scalar]]],
            ]
        ] = None,
        on_fit_config_fn: Optional[Callable[[int], Dict[str, Scalar]]] = None,
        on_evaluate_config_fn: Optional[Callable[[
            int], Dict[str, Scalar]]] = None,
        accept_failures: bool = True,
        initial_parameters: Optional[Parameters] = None,
        fit_metrics_aggregation_fn: Optional[MetricsAggregationFn] = None,
        evaluate_metrics_aggregation_fn: Optional[MetricsAggregationFn] = None,
        num_rounds: int = 10,
        exp_id: str = &#34;test&#34;,
        problem_type: str
    ) -&gt; None:
        if (
            min_fit_clients &gt; min_available_clients
            or min_evaluate_clients &gt; min_available_clients
        ):
            log(WARNING, WARNING_MIN_AVAILABLE_CLIENTS_TOO_LOW)

        self.num_rounds = num_rounds
        self.exp_id = exp_id
        self.problem_type = problem_type

        super().__init__(
            fraction_fit=fraction_fit,
            fraction_evaluate=fraction_evaluate,
            min_fit_clients=min_fit_clients,
            min_evaluate_clients=min_evaluate_clients,
            min_available_clients=min_available_clients,
            evaluate_fn=evaluate_fn,
            on_fit_config_fn=on_fit_config_fn,
            on_evaluate_config_fn=on_evaluate_config_fn,
            accept_failures=accept_failures,
            initial_parameters=initial_parameters,
            fit_metrics_aggregation_fn=fit_metrics_aggregation_fn,
            evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn,
        )

    def __repr__(self) -&gt; str:
        return &#34;FedEnsemble&#34;

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -&gt; Tuple[Optional[Parameters], Dict[str, Scalar]]:
        &#34;&#34;&#34;Aggregate training results. In this strategy we choose the weights with the best accuracy and loss scores.&#34;&#34;&#34;
        if not results:
            return None, {}
        # Do not aggregate if there are failures and failures are not accepted
        if not self.accept_failures and failures:
            return None, {}

        def get_best(result: FitRes):
            # Get the best model based loss scores
            return utils.get_loss(problem_type=self.problem_type, metrics=result.metrics)

        aggregated_weight_results = utils.custom_parameters_to_ndarrays(
            min([fit_res for _, fit_res in results], key=get_best).parameters)

        # Save aggregated_ndarrays on the last round
        if (server_round == self.num_rounds):
            # create weights folder if not exist
            import os
            if not os.path.exists(&#39;./weights&#39;):
                os.makedirs(&#39;./weights&#39;)

            log(INFO, f&#34;Saving round {server_round} aggregated_ndarrays...&#34;)
            np.savez(f&#34;./weights/{self.exp_id}-weights.npz&#34;,
                     *aggregated_weight_results)

        parameters_aggregated = utils.ndarrays_to_custom_parameters(
            aggregated_weight_results)

        # Aggregate custom metrics if aggregation fn was provided
        metrics_aggregated = {}
        if self.fit_metrics_aggregation_fn:
            fit_metrics = [(res.num_examples, res.metrics)
                           for _, res in results]
            metrics_aggregated = self.fit_metrics_aggregation_fn(fit_metrics)
        elif server_round == 1:  # Only log this warning once
            log(WARNING, &#34;No fit_metrics_aggregation_fn provided&#34;)

        return parameters_aggregated, metrics_aggregated

    def evaluate(
        self, server_round: int, parameters: Parameters
    ) -&gt; Optional[Tuple[float, Dict[str, Scalar]]]:
        &#34;&#34;&#34;Evaluate the current model parameters.
        Evaluate model parameters using an evaluation function.&#34;&#34;&#34;
        if self.evaluate_fn is None:
            # No evaluation function provided
            return None

        # We deserialize using our custom method
        parameters_ndarrays = utils.custom_parameters_to_ndarrays(parameters)

        eval_res = self.evaluate_fn(server_round, parameters_ndarrays, {})
        if eval_res is None:
            return None
        loss, metrics = eval_res

        return loss, metrics

                
            

            
            
                Powered by GitFront
            
        
    

