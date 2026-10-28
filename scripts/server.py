

    
        
        
        
        html {background-color: #fff}
        
        pycaret-fl/server.py · auto-fl-fit · GitFront
    
    
        
            
                auto-fl-fit /
                pycaret-fl /
                server.py
            

            
                
                    server.py
                    
                        Raw
                    
                
                
                    import flwr as fl
import utils
from sklearn.metrics import log_loss
from typing import Dict

from pycaret.classification import ClassificationExperiment
from pycaret.regression import RegressionExperiment

from logging import WARNING, INFO
from flwr.common.logger import log

import numpy as np
import argparse


def fit_config(server_round: int) -&gt; Dict:
    &#34;&#34;&#34;Send round number to client.&#34;&#34;&#34;
    return {&#34;server_round&#34;: server_round, &#34;model_name&#34;: MODEL_NAME, &#34;num_rounds&#34;: N_ROUNDS}


def get_evaluate_fn(model, X_test, y_test):
    &#34;&#34;&#34;Return an evaluation function for server-side evaluation.&#34;&#34;&#34;

    # The `evaluate` function will be called after every round
    def evaluate(server_round, parameters: fl.common.NDArrays, config):
        # Update model with the latest parameters
        utils.set_model_params(model, parameters)
        exp.predict_model(model)

        # save the model at the last round
        if server_round == N_ROUNDS:
            final = exp.finalize_model(model)
            exp.save_model(
                final, f&#34;{MODEL_PATH}/fl_{MODEL_NAME}&#34;+(&#34;_gen&#34; if &#34;gen_dataset&#34; in data_path else &#34;&#34;))

        metrics = exp.pull()
        results = utils.get_metrics(metrics, problem_type=problem_type)

        loss = utils.get_loss(problem_type=problem_type, metrics=metrics)

        # save results at the last round as csv
        if (server_round == N_ROUNDS):
            import os
            import pandas as pd
            if not os.path.exists(&#39;./results&#39;):
                os.makedirs(&#39;./results&#39;)

            log(INFO, f&#34;Saving round {server_round} evaluation results...&#34;)
            # add loss column
            metrics[&#39;Model&#39;] = f&#34;Federated {model.__class__.__name__}&#34;
            metrics.to_csv(
                f&#34;./results/{exp_id}-results-{MODEL_NAME}.csv&#34;, index=False)

        return loss, results

    return evaluate

# Aggregate metrics and calculate weighted averages


def metrics_aggregate(results) -&gt; Dict:
    if not results:
        return {}

    else:
        total_samples = 0  # Number of samples in the dataset

        # Collecting metrics
        aggregated_metrics = {}

        # Extracting values from the results
        for samples, metrics in results:
            for key, value in metrics.items():
                if key not in aggregated_metrics:
                    aggregated_metrics[key] = value * samples
                else:
                    aggregated_metrics[key] += (value * samples)
            total_samples += samples

        # Compute the weighted average for each metric
        for key in aggregated_metrics.keys():
            aggregated_metrics[key] = round(
                aggregated_metrics[key] / total_samples, 6)

        return aggregated_metrics


# Start Flower server for five rounds of federated learning
if __name__ == &#34;__main__&#34;:
    parser = argparse.ArgumentParser(description=&#34;Flower&#34;)
    parser.add_argument(
        &#34;--num-clients&#34;,
        type=int,
        required=True,
        help=&#34;Specifies the number of clients&#34;,
    )
    parser.add_argument(
        &#34;--num-rounds&#34;,
        type=int,
        required=True,
        help=&#34;Specifies the number of rounds&#34;,
    )
    parser.add_argument(
        &#34;--model-name&#34;,
        type=str,
        required=True,
        # choices=utils.supported_models,
        help=&#34;Specifies the model name&#34;,
    )
    parser.add_argument(
        &#34;--data-path&#34;,
        type=str,
        required=True,
        help=&#34;Specifies the path to the data&#34;,
    )
    parser.add_argument(
        &#34;--problem-type&#34;,
        type=str,
        required=True,
        choices=[&#34;classification&#34;, &#34;regression&#34;],
        help=&#34;Specifies the problem type&#34;,
        default=&#34;classification&#34;
    )
    parser.add_argument(
        &#34;--target&#34;,
        required=False,
        help=&#34;Specifies the target column&#34;,
        default=-1
    )
    parser.add_argument(
        &#34;--exp-id&#34;,
        required=False,
        help=&#34;Specifies the experiment id&#34;,
        default=&#34;FL_Test&#34;
    )
    parser.add_argument(
        &#34;--model-path&#34;,
        required=True,
        help=&#34;Specifies the path to the model&#34;,
    )

    args = parser.parse_args()
    N_CLIENTS = args.num_clients
    N_ROUNDS = args.num_rounds
    MODEL_NAME = args.model_name
    problem_type = args.problem_type
    data_path = args.data_path
    target = args.target
    exp_id = args.exp_id
    MODEL_PATH = args.model_path

    df = utils.load_data(data_path, target_column=target)
    target = utils.get_target_column_name(df, target)

    # train_df = df.groupby(df.columns[-1]).head(2)
    # df = utils.stratified_partition_with_all_values(
    #     df=df,  n_partitions=N_CLIENTS, partition_id=N_CLIENTS - 1, target=target)

    if (problem_type == &#39;classification&#39;):
        exp = ClassificationExperiment()
    elif (problem_type == &#39;regression&#39;):
        exp = RegressionExperiment()

    exp.setup(data=df, target=target, ** utils.setup_params)
    if (problem_type == &#39;classification&#39;):
        exp.add_metric(&#39;logloss&#39;, &#39;Log Loss&#39;, log_loss,
                       greater_is_better=False, target=&#34;pred_proba&#34;)
    # train only on small portion of the data which would contain all possible target values
    # we just need it for the initial values of the model
    model = exp.create_model(
        MODEL_NAME, train_model=True, cross_validation=False)
    # model = exp.compare_models(
    #     include=utils.supported_models, cross_validation=False)
    # utils.set_initial_params(model)
    X = exp.get_config(&#34;X_test&#34;)
    y = exp.get_config(&#34;y_test&#34;)
    params = utils.get_model_parameters(model)
    strategy = utils.get_strategy(
        model_name=MODEL_NAME,
        fraction_fit=1.0,  # Sample 100% of available clients for training
        fraction_evaluate=1.0,  # Sample 100% of available clients for evaluation
        min_available_clients=2,  # Never sample less than all clients for training
        # Never sample less than 5 clients for evaluation
        # min_evaluate_clients=N_CLIENTS,
        evaluate_fn=get_evaluate_fn(model, X, y),
        on_fit_config_fn=fit_config,
        initial_parameters=utils.ndarrays_to_custom_parameters(params),
        evaluate_metrics_aggregation_fn=metrics_aggregate,
        fit_metrics_aggregation_fn=metrics_aggregate,
        num_rounds=N_ROUNDS,
        exp_id=exp_id,
        problem_type=problem_type
    )

    # Generate a text file for saving the server log
    fl.common.logger.configure(identifier=exp_id, filename=&#34;log.txt&#34;)

    fl.server.start_server(
        server_address=&#34;0.0.0.0:8091&#34;,
        strategy=strategy,
        config=fl.server.ServerConfig(num_rounds=N_ROUNDS),
    )

                
            

            
            
                Powered by GitFront
            
        
    

