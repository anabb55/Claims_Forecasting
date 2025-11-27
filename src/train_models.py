import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.linear_model import PoissonRegressor, TweedieRegressor
from xgboost import XGBRegressor
from data_prep import load_data, basic_clean, add_claim_freq
import numpy as np
from typing import Tuple
import joblib
import os


def prepare_model_data(path: str) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    df = load_data(path)
    df_cleaned = basic_clean(df)
    df_final = add_claim_freq(df_cleaned)

    feature_cols = ["Area", "VehBrand", "VehGas", "Region", "VehPower", "VehAge", "DrivAge", "BonusMalus", "Density"]
    df_model = df_final[feature_cols + ["ClaimFreq", "Exposure"]].copy()

    X = df_model[feature_cols]
    y = df_model["ClaimFreq"]
    sample_weight = df_model["Exposure"]

    return X, y, sample_weight



def build_preprocessor(X: pd.DataFrame):
    numeric_cols = X.select_dtypes(include = ["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    

    preprocessor = ColumnTransformer(transformers=[
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("numerical", StandardScaler(), numeric_cols)
    ])

    return preprocessor



def tune_poisson(X_train, y_train, sample_weight_train, preprocessor):
    model = Pipeline(steps = [
        ("prep", preprocessor),
        ("poisson", PoissonRegressor(max_iter=500))
    ])

    param_grid = {
        "poisson__alpha": [0.0, 0.01, 0.1, 1.0]
    }

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(model, param_grid=param_grid, cv = cv, scoring="neg_mean_squared_error", n_jobs= -1)

    grid.fit(X_train, y_train, poisson__sample_weight = sample_weight_train)
    print("Best Poisson params:", grid.best_params_)
    return grid



def tune_tweedie(X_train, y_train, sample_weight_train, preprocessor):
    model = Pipeline(steps = [
        ("prep", preprocessor),
        ("tweedie", TweedieRegressor(max_iter=500, link = "log"))
    ])

    param_grid = {
        "tweedie__power": [1.2, 1.5, 1.8],
        "tweedie__alpha": [0.0, 0.01, 0.1]
    }
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(model, param_grid=param_grid, cv = cv, scoring="neg_mean_squared_error", n_jobs= -1)

    grid.fit(X_train, y_train, tweedie__sample_weight = sample_weight_train)
    print("Best Tweedie params:", grid.best_params_)
    return grid



def tune_xgboost(X_train, y_train, sample_weight_train, preprocessor):
    model = Pipeline(steps = [
        ("prep", preprocessor),
        ("xgb", XGBRegressor(
            objective = "count:poisson",
            tree_method = "hist",
            random_state = 42,
        ))
    ])

    param_grid = {
        "xgb__max_depth": [3, 5],
        "xgb__learning_rate": [0.05, 0.1],
        "xgb__n_estimators": [200],
        "xgb__subsample": [0.8],
        "xgb__colsample_bytree": [0.8],
    }

    cv = KFold(n_splits=3, shuffle=True, random_state=42)
    grid = GridSearchCV(model, param_grid=param_grid, cv = cv, scoring="neg_mean_squared_error", n_jobs= -1)

    grid.fit(X_train, y_train, xgb__sample_weight = sample_weight_train)
    print("Best XGBoost params:", grid.best_params_)
    return grid



def evaluate_model(name: str, model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series, sample_weight_test: pd.Series):
    y_pred = model.predict(X_test)

    rmse = mean_squared_error(y_test, y_pred, sample_weight=sample_weight_test)
    mae = mean_absolute_error(y_test, y_pred, sample_weight=sample_weight_test)
    print(f"{name}")
    print(f"Weighted MSE: {rmse:.6f}")
    print(f"Weighted MAE: {mae:.6f}")
    print()



def get_feature_importance(pipeline):
    """
    Returns a DataFrame with all sorted feature importances 
    """

    xgb_model = pipeline.named_steps["xgb"]
    pre = pipeline.named_steps["prep"]

    one_hot_encoding = pre.named_transformers_["categorical"]
    categorical_cols = pre.transformers_[0][2]
    cat_feature_names = one_hot_encoding.get_feature_names_out(categorical_cols)

    num_feature_names = pre.transformers_[1][2]

    all_features = list(cat_feature_names) + list(num_feature_names)

    importances = xgb_model.feature_importances_

    fi = pd.DataFrame({
        "feature": all_features,
        "importance": importances
    })

    return fi.sort_values("importance", ascending=False)


def get_top_errors(model, X_test, y_test, sample_weight_test, n = 10):

    y_pred = model.predict(X_test)

    print("X_test index:", X_test.index[:10])
    print("y_test index:", y_test.index[:10])
    print("y_pred prvih 10:", y_pred[:10])
    errors_df = pd.DataFrame({
        "y_true": y_test,
        "y_pred": y_pred
    }, index=y_test.index)

    errors_df["residual"] = errors_df["y_true"] - errors_df["y_pred"]
    errors_df["abs_error"] = errors_df["residual"].abs()
    errors_df["Exposure"] = sample_weight_test
    
    top_errors = errors_df.sort_values("abs_error", ascending=False).head(n)
    top_features = X_test.loc[top_errors.index]
    
    top_errors_full = top_features.copy()
    top_errors_full["y_true"] = top_errors["y_true"]
    top_errors_full["y_pred"] = top_errors["y_pred"]
    top_errors_full["residual"] = top_errors["residual"]
    top_errors_full["abs_error"] = top_errors["abs_error"]
    top_errors_full["Exposure"] = top_errors["Exposure"]
    return top_errors_full



def main():
    path = "data/freMTPL2freq.csv"
    X, y, sample_weight = prepare_model_data(path)
    

    X_train, X_temp, y_train, y_temp, sample_weight_train, sample_weight_temp = train_test_split(X, y, sample_weight, test_size=0.2, random_state=42)
    X_val, X_test, y_val, y_test, sample_weight_val, sample_weight_test = train_test_split(X_temp, y_temp, sample_weight_temp, test_size=0.5, random_state=42)
    preprocessor = build_preprocessor(X_train)

    model_poisson = tune_poisson(X_train, y_train, sample_weight_train, preprocessor)
    model_tweedie = tune_tweedie(X_train, y_train, sample_weight_train, preprocessor)
    model_xgb = tune_xgboost(X_train, y_train, sample_weight_train, preprocessor)

    print("----------Evaluation----------")
    evaluate_model("Poisson", model_poisson, X_val, y_val, sample_weight_val)
    evaluate_model("Tweedie", model_tweedie, X_val, y_val, sample_weight_val)
    evaluate_model("XGBoost", model_xgb, X_val, y_val, sample_weight_val)

    X_train_val = pd.concat([X_train, X_val], axis=0)
    y_train_val = pd.concat([y_train, y_val], axis=0)
    sw_train_val = np.concatenate([sample_weight_train, sample_weight_val])
    best_xgb = model_xgb.best_estimator_
    best_xgb.fit(X_train_val, y_train_val, xgb__sample_weight = sw_train_val)

    print("----------Final model----------")
    evaluate_model("XGBoost", best_xgb, X_test, y_test, sample_weight_test)

    ##save best model
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_xgb, "models/final_xgb_model.joblib")
    print("Final model saved")

    fi = get_feature_importance(best_xgb)
    print(fi.head(10))

    top10_errors = get_top_errors(best_xgb, X_test, y_test, sample_weight_test, n=10)
    print(top10_errors)
    

if __name__ == "__main__":
    main()