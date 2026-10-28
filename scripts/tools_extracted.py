

    
        
        
        
        html {background-color: #fff}
        
        tools.py · auto-fl-fit · GitFront
    
    
        
            
                auto-fl-fit /
                tools.py
            

            
                
                    tools.py
                    
                        Raw
                    
                
                
                    import sys
import hashlib
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import json
import os
import numpy as np
from directory_tree import display_tree

from pycaret.regression import RegressionExperiment
from pycaret.classification import ClassificationExperiment

PATH_TO_FL = &#34;./pycaret-fl&#34;
CONST_PATH_TO_DATA = &#34;./data&#34;
CONST_PATH_TO_MODELS = &#34;./models&#34;


def init_paths(scope, exp_id=None):
    if exp_id:
        PATH_TO_DATA = os.path.join(CONST_PATH_TO_DATA, exp_id)
        PATH_TO_MODELS = os.path.join(CONST_PATH_TO_MODELS, exp_id)
    else:
        PATH_TO_DATA = CONST_PATH_TO_DATA
        PATH_TO_MODELS = CONST_PATH_TO_MODELS

    if not os.path.exists(PATH_TO_DATA):
        os.makedirs(PATH_TO_DATA)
    if not os.path.exists(PATH_TO_MODELS):
        os.makedirs(PATH_TO_MODELS)

    scope[&#39;PATH_TO_DATA&#39;] = PATH_TO_DATA
    scope[&#39;PATH_TO_MODELS&#39;] = PATH_TO_MODELS

    scope[&#39;PATH_TO_DATASET&#39;] = f&#34;{PATH_TO_DATA}/dataset.csv&#34;
    scope[&#39;PATH_TO_TRAIN_DATASET&#39;] = f&#34;{PATH_TO_DATA}/train_dataset.csv&#34;
    scope[&#39;PATH_TO_EVAL_DATASET&#39;] = f&#34;{PATH_TO_DATA}/eval_dataset.csv&#34;
    scope[&#39;PATH_TO_GEN_DATASET&#39;] = f&#34;{PATH_TO_DATA}/gen_dataset.csv&#34;


def init_session():
    if &#39;use_synth_data&#39; not in st.session_state:
        st.session_state[&#39;use_synth_data&#39;] = False

    if &#39;exp_id&#39; not in st.session_state:
        # load from config.json
        if os.path.exists(&#39;config.json&#39;):
            with open(&#39;config.json&#39;, &#39;r&#39;) as f:
                config = json.load(f)
                st.session_state[&#39;exp_id&#39;] = config.get(&#39;exp_id&#39;)
        else:
            st.session_state[&#39;exp_id&#39;] = None


def update_exp_id(exp_id_ph: DeltaGenerator, exp_id: str):
    if exp_id:
        exp_id_ph.caption(f&#34;Experiment ID: *{exp_id}*&#34;)
    else:
        exp_id_ph.info(&#34;Experiment not initialized, please upload a dataset&#34;)


def update_file_tree(ph, scope):
    if (ptd := scope.get(&#39;PATH_TO_DATA&#39;)) and (ptm := scope.get(&#39;PATH_TO_MODELS&#39;)):
        import seedir as sd

        fd = sd.FakeDir(&#34;Structure&#34;)
        fdd = fd.create_folder(&#39;data&#39;)
        fdm = fd.create_folder(&#39;models&#39;)

        fptd = sd.fakedir(ptd)
        fdd._children = fptd._children
        fptm = sd.fakedir(ptm)
        fdm._children = fptm._children

        filetree = fd.seedir(style=&#39;emoji&#39;, printout=False)
        container = ph.container(height=310, border=True)
        container.text(filetree)


def sidebar(scope):
    st.set_page_config(layout=&#34;wide&#34;)

    init_session()

    # Custom CSS for changing the sidebar navigation
    custom_css = &#34;&#34;&#34;
    &lt;style&gt;
        [data-testid=stSidebarContent] {
            overflow: overlay !important;
        }
        [data-testid=stSidebarNavItems] {
            max-height: 75vh !important;
        }
        [data-testid=stSidebarUserContent] {
            padding-bottom: 1rem !important;
        }
    &lt;/style&gt;
    &#34;&#34;&#34;
    # Apply custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)

    with st.sidebar:
        st.checkbox(&#34;Use synthetic data&#34;, key=&#34;use_synth_data&#34;,
                    value=st.session_state[&#39;use_synth_data&#39;], on_change=reset_run_btn)

        exp_id = st.session_state[&#39;exp_id&#39;]
        init_paths(scope, exp_id)

        file_tree_ph = st.empty()
        update_file_tree(file_tree_ph, scope)

        exp_id_ph = st.empty()
        update_exp_id(exp_id_ph, exp_id)

        return exp_id_ph, file_tree_ph


def show_df(df):
	st.dataframe(df, use_container_width=True)


def identify_problem_type(df, threshold=10):
	# Check if the unique values in the column are less than a certain threshold
	chosen_target = st.session_state.get(&#39;preserve_chosen_target&#39;)
	unique_values = np.unique(df[chosen_target])
	if len(unique_values) &lt; threshold:
		return &#34;classification&#34;
	return &#34;regression&#34;


def get_plot_types(problem_type):
    regression_plots = [&#34;residuals&#34;, &#34;error&#34;, &#34;cooks&#34;,
                        &#34;rfe&#34;, &#34;learning&#34;, &#34;vc&#34;, &#34;manifold&#34;, &#34;feature&#34;, &#34;feature_all&#34;, &#34;parameter&#34;]

    regression_plots = {
        # &#39;Schematic drawing of the preprocessing pipeline&#39;: &#39;pipeline&#39;,
        &#39;Interactive Residual plots&#39;: &#39;residuals_interactive&#39;,
        &#39;Residuals Plot&#39;: &#39;residuals&#39;,
        &#39;Prediction Error Plot&#39;: &#39;error&#39;,
        &#39;Cooks Distance Plot&#39;: &#39;cooks&#39;,
        &#39;Recursive Feat. Selection&#39;: &#39;rfe&#39;,
        &#39;Learning Curve&#39;: &#39;learning&#39;,
        &#39;Validation Curve&#39;: &#39;vc&#39;,
        &#39;Manifold Learning&#39;: &#39;manifold&#39;,
        &#39;Feature Importance&#39;: &#39;feature&#39;,
        &#39;Feature Importance (All)&#39;: &#39;feature_all&#39;,
        &#39;Model Hyperparameter&#39;: &#39;parameter&#39;,
        &#39;Decision Tree&#39;: &#39;tree&#39;,
    }

    classification_plots = {
        # &#39;Schematic drawing of the preprocessing pipeline&#39;: &#39;pipeline&#39;,
        &#39;Area Under the Curve&#39;: &#39;auc&#39;,
        &#39;Discrimination Threshold&#39;: &#39;threshold&#39;,
        &#39;Precision Recall Curve&#39;: &#39;pr&#39;,
        &#39;Confusion Matrix&#39;: &#39;confusion_matrix&#39;,
        &#39;Class Prediction Error&#39;: &#39;error&#39;,
        &#39;Classification Report&#39;: &#39;class_report&#39;,
        &#39;Decision Boundary&#39;: &#39;boundary&#39;,
        &#39;Recursive Feature Selection&#39;: &#39;rfe&#39;,
        &#39;Learning Curve&#39;: &#39;learning&#39;,
        &#39;Manifold Learning&#39;: &#39;manifold&#39;,
        &#39;Calibration Curve&#39;: &#39;calibration&#39;,
        &#39;Validation Curve&#39;: &#39;vc&#39;,
        &#39;Dimension Learning&#39;: &#39;dimension&#39;,
        &#39;Feature Importance&#39;: &#39;feature&#39;,
        &#39;Feature Importance (All)&#39;: &#39;feature_all&#39;,
        &#39;Model Hyperparameter&#39;: &#39;parameter&#39;,
        &#39;Lift Curve&#39;: &#39;lift&#39;,
        &#39;Gain Chart&#39;: &#39;gain&#39;,
        &#39;Decision Tree&#39;: &#39;tree&#39;,
        &#39;KS Statistic Plot&#39;: &#39;ks&#39;,
    }

    if problem_type == &#39;classification&#39;:
        return classification_plots
    elif problem_type == &#39;regression&#39;:
        return regression_plots


def reset_run_btn():
    st.session_state[&#39;run_mod_btn&#39;] = False


@st.cache_resource()
def create_experiment(chosen_problem, df, target, ignore_features, exp_id):
	if chosen_problem == &#39;classification&#39;:
		exp = ClassificationExperiment()
	elif chosen_problem == &#39;regression&#39;:
		exp = RegressionExperiment()

	exp.setup(df, target=target, verbose=False,
           ignore_features=ignore_features, experiment_name=exp_id)
	return exp

                
            

            
            
                Powered by GitFront
            
        
    

