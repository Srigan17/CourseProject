

    
        
        
        
        html {background-color: #fff}
        
        pycaret-fl/utils.py · auto-fl-fit · GitFront
    
    
        
            
                auto-fl-fit /
                pycaret-fl /
                utils.py
            

            
                
                    utils.py
                    
                        Raw
                    
                
                
                    import numpy as np

from flwr.common import (
    NDArray, NDArrays, Parameters, FitRes, MetricsAggregationFn, NDArrays, Scalar)
from flwr.common.typing import NDArray, NDArrays, Parameters

from io import BytesIO
from typing import Callable, Dict, List, Optional, Tuple, Union

import pickle
import pandas as pd

from strategy.customfedavg import CustomFedAvg
from strategy.fedensemble import FedEnsemble

from imblearn.over_sampling import SMOTE

def get_model_type(model) -&gt; str:
    return model.__class__.__name__


def string_to_integers(string):
    return [ord(char) for char in string]


def integers_to_string(integers):
    return &#39;&#39;.join([chr(int(integer)) for integer in integers])


supported_models = [&#34;lr&#34;, &#34;rf&#34;, &#34;xgboost&#34;, &#34;dt&#34;]
setup_params = {
    &#34;verbose&#34;: True,
    &#34;session_id&#34;: 42,
    &#34;transformation&#34;: False,
    &#34;html&#34;: False,
    &#34;ignore_features&#34;: [&#34;date&#34;, &#34;Unnamed: 0&#34;],
    # &#34;fix_imbalance&#34;: True,
    # &#34;fix_imbalance_method&#34;: &#34;smote&#34;,
}
create_model_params = {
    &#34;cross_validation&#34;: False,
    &#34;verbose&#34;: False,
}

def get_model_parameters(model) -&gt; NDArrays:
    &#34;&#34;&#34;Returns the parameters of a sklearn model.&#34;&#34;&#34;
    tp = get_model_type(model)
    attrs = []
    blacklist = [&#34;feature_names_in_&#34;]
    # if tp == &#34;LogisticRegression&#34; or tp == &#39;RidgeClassifier&#39; or &#34;LinearRegression&#34;:
    #     attrs = [&#34;coef_&#34;, &#34;intercept_&#34;, &#34;classes_&#34;]
    # if tp == &#34;RandomForestClassifier&#34;:
    #     attrs = [&#34;n_estimators&#34;, &#34;max_depth&#34;,
    #              &#34;min_samples_split&#34;, &#34;min_samples_leaf&#34;]
    # if tp == &#34;XGBClassifier&#34;:
    #     attrs = [&#34;n_estimators&#34;, &#34;max_depth&#34;,
    #              &#34;learning_rate&#34;, &#34;subsample&#34;, &#34;colsample_bytree&#34;, &#34;subsample&#34;, &#34;gamma&#34;]
    # if attrs == []:
    #     raise Exception(&#34;Model type not supported&#34;)

    attrs = [v for v in vars(model)
             if v.endswith(&#34;_&#34;) or v.startswith(&#34;_&#34;)]
    attrs = [i for i in attrs if i not in blacklist]

    params = []
    for attr in attrs:
        if hasattr(model, attr):
            k = string_to_integers(attr)
            v = getattr(model, attr)
            if v is None:
                continue
            params.append(k)
            params.append(v)

    # print(&#34;Params: &#34;, params)
    return params


def set_model_params(model, params: NDArrays):
    &#34;&#34;&#34;Sets the parameters of a sklearn model.&#34;&#34;&#34;
    for i in range(0, len(params), 2):
        k, v = params[i], params[i+1]
        k = integers_to_string(k)
        setattr(model, k, v)
    return model


def set_initial_params(model):
    &#34;&#34;&#34;Sets initial parameters as zeros Required since model params are uninitialized
    until model.fit is called.

    But server asks for initial parameters from clients at launch. Refer to
    sklearn.linear_model.LogisticRegression documentation for more information.
    &#34;&#34;&#34;
    n_classes = 2  # MNIST has 10 classes
    n_features = 8  # Number of features in dataset
    model.classes_ = np.array([i for i in range(n_classes)])
    model.coef_ = np.zeros((n_classes, n_features))
    if model.fit_intercept:
        model.intercept_ = np.zeros((n_classes,))
    return model
    model.n_estimators = 100
    model.max_depth = 40,
    model.min_samples_split = 2,
    model.min_samples_leaf = 1,
    return model


def get_metrics(df, problem_type=&#34;classification&#34;) -&gt; Dict:
    # take from the first row
    results = df.iloc[0].to_dict()
    results.pop(&#39;Model&#39;, None)
    return results


def ndarrays_to_custom_parameters(ndarrays: NDArrays) -&gt; Parameters:
    &#34;&#34;&#34;Convert NumPy ndarrays to parameters object.&#34;&#34;&#34;
    tensors = [ndarray_to_bytes(ndarray) for ndarray in ndarrays]
    return Parameters(tensors=tensors, tensor_type=&#34;numpy.ndarray&#34;)


def custom_parameters_to_ndarrays(parameters: Parameters) -&gt; NDArrays:
    &#34;&#34;&#34;Convert parameters object to NumPy ndarrays.&#34;&#34;&#34;
    return [bytes_to_ndarray(tensor) for tensor in parameters.tensors]


def ndarray_to_bytes(ndarray: NDArray) -&gt; bytes:
    &#34;&#34;&#34;Serialize NumPy ndarray to bytes.&#34;&#34;&#34;
    # bytes_io = BytesIO()
    # WARNING: NEVER set allow_pickle to true.
    # Reason: loading pickled data can execute arbitrary code
    # Source: https://numpy.org/doc/stable/reference/generated/numpy.save.html
    # np.save(bytes_io, ndarray, allow_pickle=True)
    # return bytes_io.getvalue()
    return pickle.dumps(ndarray)


def bytes_to_ndarray(tensor: bytes) -&gt; NDArray:
    &#34;&#34;&#34;Deserialize NumPy ndarray from bytes.&#34;&#34;&#34;
    # bytes_io = BytesIO(tensor)
    # WARNING: NEVER set allow_pickle to true.
    # Reason: loading pickled data can execute arbitrary code
    # Source: https://numpy.org/doc/stable/reference/generated/numpy.load.html
    # ndarray_deserialized = np.load(bytes_io, allow_pickle=True)
    # return cast(NDArray, ndarray_deserialized)
    return pickle.loads(tensor)


def data_partitioning(df, N_CLIENTS, partition_id):
    # group the data by the last column and return df
    split_size = len(df) // N_CLIENTS
    df = [df.iloc[i:i+split_size].reset_index(drop=True)
          for i in range(0, len(df), split_size)][partition_id]
    return df


def get_target_column_name(df, target=-1):
    if target.lstrip(&#39;-+&#39;).isnumeric():
        return df.columns[int(target)]
    else:
        return target


def get_smote_data(_real_data, _target_column):
    sm = SMOTE(random_state=42)

    X = _real_data.drop(_target_column, axis=1)
    y = _real_data[_target_column]

    X_res, y_res = sm.fit_resample(X, y)

    synthetic_data = pd.concat([X_res, y_res], axis=1)

    return synthetic_data

def stratified_partition_with_all_values(df, n_partitions, partition_id, target=-1):
    # Group the data by the column of interest
    target = get_target_column_name(df, target)
    grouped = df.groupby(target)

    # Initialize empty list to store partitions
    partitions = [[] for _ in range(n_partitions)]

    # Iterate over groups
    for name, group in grouped:
        # Randomly shuffle the data within the group
        # group = group.sample(frac=1).reset_index(drop=True)

        # Calculate the number of samples in each partition for this group
        samples_per_partition = len(group) // n_partitions

        # Distribute the data evenly among partitions, ensuring each partition has all values
        for i in range(n_partitions):
            start_idx = i * samples_per_partition
            end_idx = (i + 1) * samples_per_partition
            if i == n_partitions - 1:
                end_idx = None  # Include remaining samples in the last partition
            partition_data = group.iloc[start_idx:end_idx]
            partitions[i].append(partition_data)

    # Concatenate data frames in each partition
    partitions = [pd.concat(partition) for partition in partitions]

    # reset index
    df = partitions[partition_id].reset_index(drop=True)

    # get smote
    smote_data = get_smote_data(df, target)

    return smote_data


def load_data(path: str, encode_target=True, target_column=-1):
    # Load data
    # from pycaret.datasets import get_data
    # return get_data(&#39;diabetes&#39;)
    import pandas as pd
    # df = pd.read_csv(&#39;../../data/aw_fb/aw_fb_data.csv&#39;)
    # df = df.drop([&#39;Unnamed: 0&#39;, &#39;X1&#39;], axis=1)
    # df_aw = df[df[&#39;device&#39;] == &#39;apple watch&#39;]
    # df_fb = df[df[&#39;device&#39;] == &#39;fitbit&#39;]
    # df_aw = df_aw.drop(&#39;device&#39;, axis=1)
    # df_fb = df_fb.drop(&#39;device&#39;, axis=1)
    # df = df_aw
    df = pd.read_csv(path)
    if encode_target:
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        # encode target column
        target = get_target_column_name(df, target_column)
        df[target] = le.fit_transform(df[target])
    return df


def get_strategy(model_name: str, num_rounds: int, exp_id: str, problem_type: str, fraction_fit: float = 1.0, fraction_evaluate: float = 1.0, min_fit_clients: int = 2,
                 min_evaluate_clients: int = 2,
                 min_available_clients: int = 2, evaluate_fn: Optional[
                     Callable[
                         [int, NDArrays, Dict[str, Scalar]],
                         Optional[Tuple[float, Dict[str, Scalar]]],
                     ]
                 ] = None,  on_fit_config_fn: Optional[Callable[[int], Dict[str, Scalar]]] = None,
                 on_evaluate_config_fn: Optional[Callable[[
                     int], Dict[str, Scalar]]] = None,
                 accept_failures: bool = True,
                 initial_parameters: Optional[Parameters] = None,
                 fit_metrics_aggregation_fn: Optional[MetricsAggregationFn] = None,
                 evaluate_metrics_aggregation_fn: Optional[MetricsAggregationFn] = None,):

    coef_models = [&#39;lr&#39;]

    if model_name in coef_models:
        return CustomFedAvg(
            num_rounds=num_rounds,
            exp_id=exp_id,
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
    else:
        return FedEnsemble(
            num_rounds=num_rounds,
            exp_id=exp_id,
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
            problem_type=problem_type
        )


def get_loss(problem_type: str, metrics):
    if (problem_type == &#39;classification&#39;):
        loss = float(metrics[&#39;Log Loss&#39;])
    elif (problem_type == &#39;regression&#39;):
        loss = float(metrics[&#39;MAE&#39;])
    return loss

                
            

            
            
                Powered by GitFront
            
        
    

