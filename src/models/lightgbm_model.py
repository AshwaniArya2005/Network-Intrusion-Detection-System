from src.models.sklearn_model import SklearnModel
import lightgbm as lgb


def lightgbm_classifier(params: dict) -> SklearnModel:
    return SklearnModel(
        lgb.LGBMClassifier(**params)
    )