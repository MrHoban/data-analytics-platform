"""
Machine Learning Engine for the Analytics Platform.
Handles model training, evaluation, and prediction.
"""

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from xgboost import XGBClassifier, XGBRegressor


class MLEngine:
    """Machine Learning Engine for training and managing models."""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Available algorithms
        self.classification_algorithms = {
            'logistic_regression': LogisticRegression,
            'random_forest': RandomForestClassifier,
            'decision_tree': DecisionTreeClassifier,
            'xgboost': XGBClassifier
        }
        
        self.regression_algorithms = {
            'linear_regression': LinearRegression,
            'random_forest': RandomForestRegressor,
            'decision_tree': DecisionTreeRegressor,
            'xgboost': XGBRegressor
        }
        
        # Model cache
        self._model_cache = {}
        self._scaler_cache = {}
        self._encoder_cache = {}
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Prepare data for machine learning.
        
        Args:
            df: Input DataFrame
            target_column: Name of the target column
            feature_columns: List of feature columns (if None, use all except target)
            test_size: Proportion of data for testing
            random_state: Random state for reproducibility
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in DataFrame")
        
        # Select features
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
        
        # Validate feature columns
        missing_features = [col for col in feature_columns if col not in df.columns]
        if missing_features:
            raise ValueError(f"Feature columns not found: {missing_features}")
        
        X = df[feature_columns].copy()
        y = df[target_column].copy()
        
        # Handle categorical variables
        X = self._encode_categorical_features(X)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y if self._is_classification_target(y) else None
        )
        
        logger.info(f"Data prepared: {X_train.shape[0]} training samples, {X_test.shape[0]} test samples")
        
        return X_train, X_test, y_train, y_test
    
    def _encode_categorical_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features."""
        X_encoded = X.copy()
        
        for column in X_encoded.columns:
            if X_encoded[column].dtype == 'object' or X_encoded[column].dtype.name == 'category':
                # Use label encoding for simplicity (could be enhanced with one-hot encoding)
                encoder = LabelEncoder()
                X_encoded[column] = encoder.fit_transform(X_encoded[column].astype(str))
                
                # Cache the encoder for future use
                self._encoder_cache[column] = encoder
                logger.debug(f"Encoded categorical column: {column}")
        
        return X_encoded
    
    def _is_classification_target(self, y: pd.Series) -> bool:
        """Determine if the target is for classification or regression."""
        # Simple heuristic: if target has few unique values relative to size, it's classification
        unique_ratio = y.nunique() / len(y)
        return unique_ratio < 0.05 or y.dtype == 'object' or y.dtype.name == 'category'
    
    def train_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        algorithm: str,
        model_params: Optional[Dict[str, Any]] = None,
        scale_features: bool = True
    ) -> Dict[str, Any]:
        """
        Train a machine learning model.
        
        Args:
            X_train: Training features
            y_train: Training target
            algorithm: Algorithm name
            model_params: Model parameters
            scale_features: Whether to scale features
            
        Returns:
            Dictionary containing model information and metrics
        """
        if model_params is None:
            model_params = {}
        
        # Determine problem type
        is_classification = self._is_classification_target(y_train)
        
        # Get the appropriate algorithm
        if is_classification:
            if algorithm not in self.classification_algorithms:
                raise ValueError(f"Unknown classification algorithm: {algorithm}")
            model_class = self.classification_algorithms[algorithm]
        else:
            if algorithm not in self.regression_algorithms:
                raise ValueError(f"Unknown regression algorithm: {algorithm}")
            model_class = self.regression_algorithms[algorithm]
        
        # Scale features if requested
        scaler = None
        X_train_processed = X_train.copy()
        
        if scale_features and algorithm in ['logistic_regression', 'linear_regression']:
            scaler = StandardScaler()
            X_train_processed = pd.DataFrame(
                scaler.fit_transform(X_train_processed),
                columns=X_train_processed.columns,
                index=X_train_processed.index
            )
            logger.info("Features scaled using StandardScaler")
        
        # Initialize and train the model
        model = model_class(**model_params)
        model.fit(X_train_processed, y_train)
        
        # Perform cross-validation
        cv_scores = cross_val_score(model, X_train_processed, y_train, cv=5)
        
        # Generate model info
        model_info = {
            'algorithm': algorithm,
            'model_type': 'classification' if is_classification else 'regression',
            'parameters': model_params,
            'feature_columns': list(X_train.columns),
            'target_column': y_train.name,
            'training_samples': len(X_train),
            'cv_scores': cv_scores.tolist(),
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'scaled': scale_features and scaler is not None
        }
        
        # Store model and scaler
        model_id = f"{algorithm}_{hash(str(model_params))}"
        self._model_cache[model_id] = model
        if scaler:
            self._scaler_cache[model_id] = scaler
        
        model_info['model_id'] = model_id
        
        logger.info(f"Model trained successfully: {algorithm} (CV Score: {cv_scores.mean():.4f} ± {cv_scores.std():.4f})")
        
        return model_info
    
    def evaluate_model(
        self,
        model_id: str,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict[str, Any]:
        """
        Evaluate a trained model.
        
        Args:
            model_id: Model identifier
            X_test: Test features
            y_test: Test target
            
        Returns:
            Dictionary containing evaluation metrics
        """
        if model_id not in self._model_cache:
            raise ValueError(f"Model not found: {model_id}")
        
        model = self._model_cache[model_id]
        
        # Apply scaling if used during training
        X_test_processed = X_test.copy()
        if model_id in self._scaler_cache:
            scaler = self._scaler_cache[model_id]
            X_test_processed = pd.DataFrame(
                scaler.transform(X_test_processed),
                columns=X_test_processed.columns,
                index=X_test_processed.index
            )
        
        # Make predictions
        y_pred = model.predict(X_test_processed)
        
        # Determine problem type
        is_classification = self._is_classification_target(y_test)
        
        # Calculate metrics
        if is_classification:
            metrics = self._calculate_classification_metrics(y_test, y_pred)
            
            # Add probability predictions if available
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_test_processed)
                metrics['probabilities_available'] = True
            else:
                metrics['probabilities_available'] = False
        else:
            metrics = self._calculate_regression_metrics(y_test, y_pred)
        
        metrics['model_id'] = model_id
        metrics['test_samples'] = len(X_test)
        
        logger.info(f"Model evaluated: {model_id}")
        
        return metrics
    
    def _calculate_classification_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculate classification metrics."""
        accuracy = accuracy_score(y_true, y_pred)
        
        # Classification report
        report = classification_report(y_true, y_pred, output_dict=True)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'precision': report['weighted avg']['precision'],
            'recall': report['weighted avg']['recall'],
            'f1_score': report['weighted avg']['f1-score']
        }
    
    def _calculate_regression_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculate regression metrics."""
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        return {
            'mean_absolute_error': mae,
            'mean_squared_error': mse,
            'root_mean_squared_error': rmse,
            'r2_score': r2
        }
    
    def predict(
        self,
        model_id: str,
        X: pd.DataFrame,
        return_probabilities: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions using a trained model.
        
        Args:
            model_id: Model identifier
            X: Features for prediction
            return_probabilities: Whether to return probabilities (classification only)
            
        Returns:
            Predictions or tuple of (predictions, probabilities)
        """
        if model_id not in self._model_cache:
            raise ValueError(f"Model not found: {model_id}")
        
        model = self._model_cache[model_id]
        
        # Apply scaling if used during training
        X_processed = X.copy()
        if model_id in self._scaler_cache:
            scaler = self._scaler_cache[model_id]
            X_processed = pd.DataFrame(
                scaler.transform(X_processed),
                columns=X_processed.columns,
                index=X_processed.index
            )
        
        # Make predictions
        predictions = model.predict(X_processed)
        
        if return_probabilities and hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X_processed)
            return predictions, probabilities
        
        return predictions
    
    def save_model(self, model_id: str, model_name: str) -> str:
        """
        Save a trained model to disk.
        
        Args:
            model_id: Model identifier
            model_name: Name for the saved model
            
        Returns:
            Path to the saved model file
        """
        if model_id not in self._model_cache:
            raise ValueError(f"Model not found: {model_id}")
        
        model = self._model_cache[model_id]
        
        # Create model package
        model_package = {
            'model': model,
            'scaler': self._scaler_cache.get(model_id),
            'encoders': {k: v for k, v in self._encoder_cache.items()},
            'metadata': {
                'model_id': model_id,
                'model_name': model_name,
                'algorithm': getattr(model, '__class__').__name__
            }
        }
        
        # Save to file
        model_path = self.model_dir / f"{model_name}.joblib"
        joblib.dump(model_package, model_path)
        
        logger.info(f"Model saved: {model_path}")
        
        return str(model_path)
    
    def load_model(self, model_path: str) -> str:
        """
        Load a saved model from disk.
        
        Args:
            model_path: Path to the saved model file
            
        Returns:
            Model identifier
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model package
        model_package = joblib.load(model_path)
        
        model_id = model_package['metadata']['model_id']
        
        # Store in cache
        self._model_cache[model_id] = model_package['model']
        
        if model_package['scaler']:
            self._scaler_cache[model_id] = model_package['scaler']
        
        if model_package['encoders']:
            self._encoder_cache.update(model_package['encoders'])
        
        logger.info(f"Model loaded: {model_path}")
        
        return model_id
    
    def get_feature_importance(self, model_id: str) -> Optional[Dict[str, float]]:
        """
        Get feature importance from a trained model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Dictionary of feature names and their importance scores
        """
        if model_id not in self._model_cache:
            raise ValueError(f"Model not found: {model_id}")
        
        model = self._model_cache[model_id]
        
        if hasattr(model, 'feature_importances_'):
            # For tree-based models
            feature_names = getattr(model, 'feature_names_in_', None)
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(len(model.feature_importances_))]
            
            importance_dict = dict(zip(feature_names, model.feature_importances_))
            return importance_dict
        
        elif hasattr(model, 'coef_'):
            # For linear models
            feature_names = getattr(model, 'feature_names_in_', None)
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(len(model.coef_))]
            
            # Use absolute values of coefficients as importance
            importance_dict = dict(zip(feature_names, np.abs(model.coef_)))
            return importance_dict
        
        return None
    
    def list_models(self) -> List[str]:
        """List all cached models."""
        return list(self._model_cache.keys())
    
    def remove_model(self, model_id: str):
        """Remove a model from cache."""
        if model_id in self._model_cache:
            del self._model_cache[model_id]
        
        if model_id in self._scaler_cache:
            del self._scaler_cache[model_id]
        
        logger.info(f"Model removed from cache: {model_id}")
