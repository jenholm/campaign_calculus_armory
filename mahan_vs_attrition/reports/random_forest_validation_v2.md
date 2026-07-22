# Random Forest Reproducibility Audit (M63)

## Dataset

- **Number of samples**: 2137
- **Features**: 12
- **Target variable**: Short war (<365 days) vs Long war (>=365 days)
- **Class counts**: 1020 short, 1117 long
- **Class balance**: 47.7% short, 52.3% long
- **Random seed**: 42
- **CV folds**: 5

## Model: Random Forest

- **Estimator**: RandomForestClassifier
- **Number of trees**: 100
- **Max depth**: 5
- **Random state**: 42

## Evaluation

- **Accuracy (5-fold CV)**: 73.9% ± 1.1%
- **Balanced accuracy**: 73.8%
- **Precision**: 72.7%
- **Recall**: 72.7%
- **F1**: 72.7%
- **ROC-AUC**: 81.6%
- **Null baseline**: 52.3% (majority class 0)

### Confusion Matrix

```
                 Predicted Short  Predicted Long
Actual Short:                838            279
Actual Long:                 279            741
```

## Model: Logistic Regression (Baseline)

- **Accuracy (5-fold CV)**: 55.2% ± 1.5%
- **Balanced accuracy**: 54.8%
- **Precision**: 53.5%
- **Recall**: 46.5%
- **F1**: 49.7%
- **ROC-AUC**: 56.5%
- **Null baseline**: 52.3%

## Interpretation

The random forest classifier captures nonlinear interactions among material-capability features, 
achieving substantially higher accuracy than the logistic regression baseline. 
The logistic regression's limited performance indicates that linear relationships among these features 
contain limited predictive information, while nonlinear models capture additional interactions. 
This supports the argument that warfare dynamics involve complex structural interactions 
that simple additive models cannot represent.