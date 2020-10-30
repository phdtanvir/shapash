"""
Check Module
"""

import numpy as np
import pandas as pd
from shapash.utils.transform import preprocessing_tolist, check_supported_inverse


def check_preprocessing(preprocessing=None):
    """
    Check that all transformation of the preprocessing are supported.

    Parameters
    ----------
    preprocessing: category_encoders, ColumnTransformer, list, dict, optional (default: None)
        The processing apply to the original data
    """
    if preprocessing is not None:
        list_preprocessing = preprocessing_tolist(preprocessing)
        use_ct, use_ce = check_supported_inverse(list_preprocessing)
        if not use_ct and not use_ce:
            raise ValueError(
                """
                preprocessing isn't supported.  
                """)

def check_model(model):
    """
    Check if model has a predict_proba method is a one column dataframe of integer or float
    and if y_pred index matches x_pred index

    Parameters
    ----------
    model: model object
        model used to check the different values of target estimate predict or predict_proba

    Returns
    -------
    string:
        'regression' or 'classification' according to the attributes of the model
    """
    _classes = None
    if hasattr(model, 'predict'):
        if hasattr(model, 'predict_proba') or \
                any(hasattr(model, attrib) for attrib in ['classes_', '_classes']):
            if hasattr(model, '_classes'): _classes = model._classes
            if hasattr(model, 'classes_'): _classes = model.classes_
            if isinstance(_classes, np.ndarray): _classes = _classes.tolist()
            if hasattr(model, 'predict_proba') and _classes == []: _classes = [0, 1]  # catboost binary
            if hasattr(model, 'predict_proba') and _classes is None:
                raise ValueError(
                    "No attribute _classes, classification model not supported"
                )
        if _classes not in (None, []):
            return 'classification', _classes
        else:
            return 'regression', None
    else:
        raise ValueError(
            "No method predict in the specified model. Please, check model parameter"
        )

def check_label_dict(label_dict, case, classes):
    """
    Check if label_dict and model _classes match

    Parameters
    ----------
    label_dict: dict
        Dictionary mapping integer labels to domain names (classification - target values).
    case: string
        String that informs if the model used is for classification or regression problem.
    classes: list, None
        List of labels if the model used is for classification problem, None otherwise.
    """
    if label_dict is not None and case == 'classification':
        if set(classes) != set(list(label_dict.keys())):
            raise ValueError(
                "label_dict and don't match: \n" +
                f"label_dict keys: {str(list(label_dict.keys()))}\n" +
                f"Classes model values {str(classes)}"
            )

def check_mask_params(mask_params):
    """
    Check if mask_params given respect the expected format.

    Parameters
    ----------
    mask_params: dict (optional)
        Dictionnary allowing the user to define a apply a filter to summarize the local explainability.
    """
    if not isinstance(mask_params, dict):
        raise ValueError(
            """
            mask_params must be a dict  
            """
        )
    else:
        conform_arguments = ["features_to_hide", "threshold", "positive", "max_contrib"]
        mask_arguments_not_conform = [argument for argument in mask_params.keys()
                                      if argument not in conform_arguments]
        if len(mask_arguments_not_conform) != 0:
            raise ValueError(
            """
            mask_params must only have the following key arguments:
            -feature_to_hide
            -threshold
            -positive
            -max_contrib 
            """
            )

def check_ypred(case, x,  ypred=None):
    """
    Check that ypred given has the right shape and expected value.

    Parameters
    ----------
    ypred: pandas.DataFrame (optional)
        User-specified prediction values.
    case: string
        String that informs if the model used is for classification or regression problem.
    x: pandas.DataFrame
        Dataset used by the model to perform the prediction (preprocessed or not).
    """
    if ypred is not None:
        if case != "classification":
            raise ValueError("ypred should not be specified in classification problems.")
        if not isinstance(ypred, (pd.DataFrame, pd.Series)):
            raise ValueError("y_pred must be a one column pd.Dataframe or pd.Series.")
        if not ypred.index.equals(x.index):
            raise ValueError("x_pred and y_pred should have the same index.")
        if isinstance(ypred, pd.DataFrame):
            if ypred.shape[1] > 1:
                raise ValueError("y_pred must be a one column pd.Dataframe or pd.Series.")
            if not (ypred.dtypes[0] in [np.float, np.int]):
                raise ValueError("y_pred must contain int or float only")
        if isinstance(ypred, pd.Series):
            if not (ypred.dtype in [np.float, np.int]):
                raise ValueError("y_pred must contain int or float only")
            ypred = ypred.to_frame()
    return ypred

def validate_contributions(case, classes, contributions):
    """
    Check len of list if _case is "classification"
    Check contributions object type if _case is "regression"
    Check type of contributions and transform into (list of) pd.Dataframe if necessary

    Parameters
    ----------
    case: string
        String that informs if the model used is for classification or regression problem.
    classes: list, None
        List of labels if the model used is for classification problem, None otherwise.
    contributions : pandas.DataFrame, np.ndarray or list
    """
    if case == "regression" and isinstance(contributions, (np.ndarray, pd.DataFrame)) == False:
        raise ValueError(
            """
            Type of contributions parameter specified is not compatible with 
            regression model.
            Please check model and contributions parameters.  
            """
        )
    elif case == "classification":
        if isinstance(contributions, list):
            if len(contributions) != len(classes):
                raise ValueError(
                    """
                    Length of list of contributions parameter is not equal
                    to the number of classes in the target.
                    Please check model and contributions parameters.
                    """
                )
        else:
            raise ValueError(
                """
                Type of contributions parameter specified is not compatible with 
                classification model.
                Please check model and contributions parameters.
                """
            )
