import pickle
import numpy as np
import pandas as pd
import sklearn

def inspect_pkl(filename):
    print(f"--- Inspecting {filename} ---")
    try:
        with open(filename, 'rb') as f:
            obj = pickle.load(f)
            print(f"Type: {type(obj)}")
            
            if hasattr(obj, 'feature_names_in_'):
                print(f"Feature names in: {obj.feature_names_in_}")
            elif hasattr(obj, 'n_features_in_'):
                print(f"Number of features in: {obj.n_features_in_}")
                
            if hasattr(obj, 'categories_'):
                print(f"Categories: {obj.categories_}")
            
            if hasattr(obj, 'classes_'): # LabelEncoder
                print(f"Classes: {obj.classes_}")

            # Try to infer more if it's a pipeline or standard scaler
            if hasattr(obj, 'mean_'):
                print("Has mean_ (likely Scaler)")
            
    except Exception as e:
        print(f"Error inspecting {filename}: {e}")

inspect_pkl('encoder.pkl')
inspect_pkl('scaler.pkl')
inspect_pkl('model.pkl')
