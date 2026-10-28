

    
        
        
        
        html {background-color: #fff}
        
        pycaret-fl/client.py · auto-fl-fit · GitFront
    
    
        
            
                auto-fl-fit /
                pycaret-fl /
                client.py
            

            
                
                    client.py
                    
                        Raw
                    
                
                
                    import argparse
import warnings

# from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

from pycaret.classification import ClassificationExperiment
from pycaret.regression import RegressionExperiment

import numpy as np

import flwr as fl
import utils

from flwr.common import (
    Code,
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    GetParametersIns,
    GetParametersRes,
    Status,
)

from typing import List


if __name__ == &#34;__main__&#34;:
    parser = argparse.ArgumentParser(description=&#34;Flower&#34;)
    parser.add_argument(
        &#34;--node-id&#34;,
        type=int,
        required=True,
        help=&#34;Specifies the artificial data partition&#34;,
    )
    parser.add_argument(
        &#34;--num-clients&#34;,
        type=int,
        required=True,
        help=&#34;Specifies the number of clients&#34;,
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
        &#34;--data-path&#34;,
        type=str,
        required=True,
        help=&#34;Specifies the path to the data&#34;,
    )
    parser.add_argument(
        &#34;--target&#34;,
        required=False,
        help=&#34;Specifies the target column&#34;,
        default=-1
    )
    args = parser.parse_args()
    partition_id = args.node_id
    problem_type = args.problem_type
    N_CLIENTS = args.num_clients
    target = args.target

# Setup an experiment
    df = utils.load_data(args.data_path, target_column=target)

    # Partition the data based on NUM_CLIENTS and CLIENT_ID
    # df = utils.stratified_partition_with_all_values(
    #     df=df, n_partitions=N_CLIENTS, partition_id=partition_id, target=target)
    target = utils.get_target_column_name(df, target)

    if (problem_type == &#39;classification&#39;):
        exp = ClassificationExperiment()
    else:
        exp = RegressionExperiment()
    exp.setup(data=df, target=target, **utils.setup_params)
    if (problem_type == &#39;classification&#39;):
        exp.add_metric(&#39;logloss&#39;, &#39;Log Loss&#39;, log_loss,
                       greater_is_better=False, target=&#34;pred_proba&#34;)

    X_train = exp.get_config(&#34;X_train&#34;)
    y_train = exp.get_config(&#34;y_train&#34;)
    X_test = exp.get_config(&#34;X_test&#34;)
    y_test = exp.get_config(&#34;y_test&#34;)

    # Define Flower client
    class FlowerClient(fl.client.Client):
        def __init__(self, cid):
            self.model = None
            self.cid = cid

        def get_parameters(self, ins: GetParametersIns) -&gt; GetParametersRes:
            print(f&#34;[Client {self.cid}] get_parameters&#34;)

            # Get parameters as a list of NumPy ndarray&#39;s
            ndarrays: List[np.ndarray] = utils.get_model_parameters(self.model)

            # Serialize ndarray&#39;s into a Parameters object
            parameters = utils.ndarrays_to_custom_parameters(ndarrays)

            # Build and return response
            status = Status(code=Code.OK, message=&#34;Success&#34;)
            return GetParametersRes(
                status=status,
                parameters=parameters,
            )

        def fit(self, ins: FitIns) -&gt; FitRes:
            print(f&#34;[Client {self.cid}] fit, config: {ins.config}&#34;)

            # Deserialize parameters to NumPy ndarray&#39;s
            parameters_original = ins.parameters
            ndarrays_original = utils.custom_parameters_to_ndarrays(
                parameters_original)

            # Update local model, train, get updated parameters
            if (self.model is None):
                print(f&#34;Creating model with {len(X_train)} examples&#34;)
                self.model = exp.create_model(
                    ins.config[&#39;model_name&#39;], cross_validation=False, train_model=False)
            utils.set_model_params(self.model, ndarrays_original)
            # Ignore convergence failure due to low local epochs
            with warnings.catch_warnings():
                print(f&#34;Training model with {len(X_train)} examples&#34;)
                warnings.simplefilter(&#34;ignore&#34;)
                # self.model.fit(X_train, y_train)
                self.model = exp.create_model(
                    self.model, cross_validation=False)
                metrics = exp.pull()
                results = utils.get_metrics(metrics, problem_type=problem_type)

            ndarrays_updated = utils.get_model_parameters(self.model)

            # Serialize ndarray&#39;s into a Parameters object
            parameters_updated = utils.ndarrays_to_custom_parameters(
                ndarrays_updated)

            # Build and return response
            status = Status(code=Code.OK, message=&#34;Success&#34;)
            return FitRes(
                status=status,
                parameters=parameters_updated,
                num_examples=len(X_train),
                metrics=results,
            )

        def evaluate(self, ins: EvaluateIns) -&gt; EvaluateRes:
            print(f&#34;[Client {self.cid}] evaluate, config: {ins.config}&#34;)

            # Deserialize parameters to NumPy ndarray&#39;s
            parameters_original = ins.parameters
            ndarrays_original = utils.custom_parameters_to_ndarrays(
                parameters_original)

            utils.set_model_params(self.model, ndarrays_original)
            exp.predict_model(self.model)
            metrics = exp.pull()
            results = utils.get_metrics(metrics, problem_type=problem_type)

            loss = utils.get_loss(problem_type=problem_type, metrics=metrics)

            # Build and return response
            status = Status(code=Code.OK, message=&#34;Success&#34;)
            return EvaluateRes(
                status=status,
                loss=loss,
                num_examples=len(X_test),
                metrics=results,
            )

    # Start Flower client
    fl.client.start_client(
        server_address=&#34;0.0.0.0:8091&#34;, client=FlowerClient(cid=partition_id)
    )

                
            

            
            
                Powered by GitFront
            
        
    

