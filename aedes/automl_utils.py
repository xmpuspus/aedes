import pandas as pd
import matplotlib.pyplot as plt
import joblib
import warnings
import os

from tpot import TPOTClassifier, TPOTRegressor
from sklearn.cluster import KMeans as km

warnings.filterwarnings('ignore')

def perform_classification(X, y, 
                           max_time_mins=10,
                           max_eval_time_mins=0.05,
                           folder_path="",
                           model_name="best_model.pkl",
                           pipeline_name="best_model_pipeline.py",
                           cv=10,
                           scoring='f1',
                           show_feature_importances=True
                          ):
    """
    This module performs limited automl classification 
    as described in this documentation https://epistasislab.github.io/tpot/.
    The output model follows sklearn-like modules like .score, .predict, etc
    
    Input
        X: dataframe of predictors
        y: Series or dataframe to be predicted (Classification)
        max_time_mins: float value in minutes for maximum training time
        max_eval_time_mins: float value in minutes for max time per pipeline
        folder_path: String for path to store files/models into 
        model_name: String to name the best model's pickle file
        pipeline_name: String to name the best model pipeline python script
        cv: integer for number of cross-validations to perform
        scoring: classification scoring metric described here
        show_feature_importances: boolean that dictates showing/non-showing of feature importance plot
        
    Returns:
    best_model_pipeline: ml model generated from the automl formulation
    feature_importances_df: dataframe of features and feature importances
    """

    # define TPOTClassifier
    model = TPOTClassifier(generations=20, 
                           population_size=50, 
                           cv=cv, 
                           scoring=scoring, 
                           verbosity=2, 
                           random_state=42, 
                           n_jobs=-1,
                           max_time_mins=max_time_mins,
                           max_eval_time_mins=max_eval_time_mins
                          )
    
    # Fit X and y into model and find the best model
    model.fit(X, y)
    
    # best model
    best_model_pipeline = model.fitted_pipeline_
    
    # Save best model
    joblib.dump(best_model_pipeline, os.path.join(folder_path, model_name))
    
    # Save best model pipeline
    model.export(os.path.join(folder_path, pipeline_name))
    
    # Get the best model
    extracted_best_model = model.fitted_pipeline_.steps[-1][1]
    
    # Train the `exctracted_best_model` using the whole dataset
    extracted_best_model.fit(X.dropna(), y[X.isna().sum(axis=1)==0]) 

   # Feature importance dataframe
    feat_importances_df = (pd.DataFrame({'Columns':X.columns,
                  'Feature Importances': extracted_best_model.feature_importances_})
                    .set_index('Columns')
                    .sort_values('Feature Importances', ascending=False))
    
    # Show feature importances as dictated by the input flag
    if show_feature_importances:
        feat_importances_df.plot(kind='barh', figsize=(20, 10))
        plt.gca().invert_yaxis()
    else:
        pass
    
    # output prompt to locate the model and pipeline
    if folder_path == "":
        prompt_path = 'the same directory as this code'
    else:
        prompt_path = folder_path
    print(f"Best model pickle file and best model pipeline saved to {prompt_path}.")
    
    return extracted_best_model, feat_importances_df
    
def perform_regression(X, y, 
                           max_time_mins=10,
                           max_eval_time_mins=0.05,
                           folder_path="",
                           model_name="best_model.pkl",
                           pipeline_name="best_model_pipeline.py",
                           cv=10,
                           scoring='neg_mean_squared_error',
                           show_feature_importances=True
                          ):
    """
    This module performs limited automl regression 
    as described in this documentation https://epistasislab.github.io/tpot/.
    The output model follows sklearn-like modules like .score, .predict, etc
    
    Input
        X: dataframe of predictors
        y: Series or dataframe to be predicted (Regression)
        max_time_mins: float value in minutes for maximum training time
        max_eval_time_mins: float value in minutes for max time per pipeline
        folder_path: String for path to store files/models into 
        model_name: String to name the best model's pickle file
        pipeline_name: String to name the best model pipeline python script
        cv: integer for number of cross-validations to perform
        scoring: classification scoring metric described here
        show_feature_importances: boolean that dictates showing/non-showing of feature importance plot
        
    Returns:
    best_model_pipeline: ml model generated from the automl formulation
    feature_importances_df: dataframe of features and feature importances
    """

    # define TPOTClassifier
    model = TPOTClassifier(generations=20, 
                           population_size=50, 
                           cv=cv, 
                           scoring=scoring, 
                           verbosity=2, 
                           random_state=42, 
                           n_jobs=-1,
                           max_time_mins=max_time_mins,
                           max_eval_time_mins=max_eval_time_mins
                          )
    
    # Fit X and y into model and find the best model
    model.fit(X, y)
    
    # best model
    best_model_pipeline = model.fitted_pipeline_
    
    # Save best model
    joblib.dump(best_model_pipeline, os.path.join(folder_path, model_name))
    
    # Save best model pipeline
    model.export(os.path.join(folder_path, pipeline_name))
    
    # Get the best model
    extracted_best_model = model.fitted_pipeline_.steps[-1][1]
    
    # Train the `exctracted_best_model` using the whole dataset
    extracted_best_model.fit(X.dropna(), y[X.isna().sum(axis=1)==0]) 

   # Feature importance dataframe
    feat_importances_df = (pd.DataFrame({'Columns':X.columns,
                  'Feature Importances': extracted_best_model.feature_importances_})
                    .set_index('Columns')
                    .sort_values('Feature Importances', ascending=False))
    
    # Show feature importances as dictated by the input flag
    if show_feature_importances:
        feat_importances_df.plot(kind='barh', figsize=(20, 10))
        plt.gca().invert_yaxis()
    else:
        pass
    
    # output prompt to locate the model and pipeline
    if folder_path == "":
        prompt_path = 'the same directory as this code'
    else:
        prompt_path = folder_path
    print(f"Best model pickle file and best model pipeline saved to {prompt_path}.")
    
    return extracted_best_model, feat_importances_df

def perform_clustering(df, 
                       features=['longitude', 'latitude', 'ndvi', 'ndbi', 'ndwi', 'ndmi', 
                                 'surface_temperature', 'precipitation_rate', 'relative_humidity'],
                       n_clusters=5):
    
    """
    From dataframe and preset list of features to cluster, outputs the final clustering model
    """
    
    X = df[features].dropna(axis=1, how='all')
    
    kmeans = km(n_clusters=n_clusters, 
                random_state=42).fit(X)
    
    return kmeans
