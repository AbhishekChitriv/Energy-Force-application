import pickle
import numpy as np

def inspect_scaler(filename):
    with open(filename, 'rb') as f:
        obj = pickle.load(f)
        print(f"Feature Names: {obj.feature_names_in_}")
        print(f"Means: {obj.mean_}")
        print(f"Variances: {obj.var_}")

inspect_scaler('scaler.pkl')
