"""
Machine Learning endpoints for the Analytics Engine.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from ...core.ml_engine import MLEngine

router = APIRouter()
ml_engine = MLEngine()


class TrainingRequest(BaseModel):
    """Request model for training a machine learning model."""
    dataset_id: str
    target_column: str
    feature_columns: Optional[List[str]] = None
    algorithm: str
    model_params: Optional[Dict] = None
    test_size: float = 0.2
    scale_features: bool = True
    random_state: int = 42


class TrainingResponse(BaseModel):
    """Response model for model training."""
    success: bool
    message: str
    model_id: str
    model_info: Dict
    training_metrics: Dict


class PredictionRequest(BaseModel):
    """Request model for making predictions."""
    model_id: str
    data: List[Dict]
    return_probabilities: bool = False


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    success: bool
    predictions: List
    probabilities: Optional[List] = None
    model_id: str


class EvaluationResponse(BaseModel):
    """Response model for model evaluation."""
    success: bool
    model_id: str
    metrics: Dict


@router.get("/algorithms")
async def get_available_algorithms():
    """
    Get list of available machine learning algorithms.
    
    Returns:
        Dictionary of available algorithms by type
    """
    return {
        "classification": list(ml_engine.classification_algorithms.keys()),
        "regression": list(ml_engine.regression_algorithms.keys())
    }


@router.post("/train")
async def train_model(request: TrainingRequest) -> TrainingResponse:
    """
    Train a machine learning model.
    
    Args:
        request: Training request with dataset and model configuration
        
    Returns:
        Training results and model information
    """
    try:
        # TODO: Load dataset from database using dataset_id
        # For now, create mock data for demonstration
        
        import pandas as pd
        import numpy as np
        
        # Create mock dataset
        np.random.seed(request.random_state)
        n_samples = 1000
        
        if request.algorithm in ml_engine.classification_algorithms:
            # Classification dataset
            X = pd.DataFrame({
                'feature_1': np.random.normal(0, 1, n_samples),
                'feature_2': np.random.normal(0, 1, n_samples),
                'feature_3': np.random.normal(0, 1, n_samples),
                'feature_4': np.random.normal(0, 1, n_samples)
            })
            y = pd.Series(np.random.choice(['A', 'B', 'C'], n_samples))
            y.name = request.target_column
        else:
            # Regression dataset
            X = pd.DataFrame({
                'feature_1': np.random.normal(0, 1, n_samples),
                'feature_2': np.random.normal(0, 1, n_samples),
                'feature_3': np.random.normal(0, 1, n_samples),
                'feature_4': np.random.normal(0, 1, n_samples)
            })
            y = pd.Series(
                X['feature_1'] * 2 + X['feature_2'] * 1.5 + np.random.normal(0, 0.1, n_samples)
            )
            y.name = request.target_column
        
        # Prepare data
        X_train, X_test, y_train, y_test = ml_engine.prepare_data(
            pd.concat([X, y], axis=1),
            request.target_column,
            request.feature_columns,
            request.test_size,
            request.random_state
        )
        
        # Train model
        model_info = ml_engine.train_model(
            X_train,
            y_train,
            request.algorithm,
            request.model_params,
            request.scale_features
        )
        
        # Evaluate model
        evaluation_metrics = ml_engine.evaluate_model(
            model_info['model_id'],
            X_test,
            y_test
        )
        
        response = TrainingResponse(
            success=True,
            message="Model trained successfully",
            model_id=model_info['model_id'],
            model_info=model_info,
            training_metrics=evaluation_metrics
        )
        
        logger.info(f"Model trained successfully: {model_info['model_id']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


@router.post("/predict")
async def make_predictions(request: PredictionRequest) -> PredictionResponse:
    """
    Make predictions using a trained model.
    
    Args:
        request: Prediction request with model ID and data
        
    Returns:
        Predictions and optional probabilities
    """
    try:
        # Convert input data to DataFrame
        import pandas as pd
        df = pd.DataFrame(request.data)
        
        # Make predictions
        if request.return_probabilities:
            predictions, probabilities = ml_engine.predict(
                request.model_id,
                df,
                return_probabilities=True
            )
            
            response = PredictionResponse(
                success=True,
                predictions=predictions.tolist(),
                probabilities=probabilities.tolist() if probabilities is not None else None,
                model_id=request.model_id
            )
        else:
            predictions = ml_engine.predict(request.model_id, df)
            
            response = PredictionResponse(
                success=True,
                predictions=predictions.tolist(),
                model_id=request.model_id
            )
        
        logger.info(f"Predictions made for model {request.model_id}: {len(predictions)} samples")
        
        return response
        
    except Exception as e:
        logger.error(f"Error making predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Error making predictions: {str(e)}")


@router.get("/models")
async def list_models():
    """
    List all trained models.
    
    Returns:
        List of available models
    """
    try:
        model_ids = ml_engine.list_models()
        
        # TODO: Get additional model information from database
        models = []
        for model_id in model_ids:
            models.append({
                "model_id": model_id,
                "status": "trained",
                "created_at": "2024-01-01T00:00:00Z"  # Mock timestamp
            })
        
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")


@router.get("/models/{model_id}")
async def get_model_info(model_id: str):
    """
    Get detailed information about a specific model.
    
    Args:
        model_id: Model identifier
        
    Returns:
        Detailed model information
    """
    try:
        if model_id not in ml_engine.list_models():
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get feature importance if available
        feature_importance = ml_engine.get_feature_importance(model_id)
        
        # TODO: Get additional model information from database
        model_info = {
            "model_id": model_id,
            "status": "trained",
            "algorithm": "unknown",  # Would be stored in database
            "created_at": "2024-01-01T00:00:00Z",
            "feature_importance": feature_importance
        }
        
        return model_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")


@router.post("/models/{model_id}/evaluate")
async def evaluate_model(model_id: str, dataset_id: str) -> EvaluationResponse:
    """
    Evaluate a trained model on a dataset.
    
    Args:
        model_id: Model identifier
        dataset_id: Dataset identifier for evaluation
        
    Returns:
        Evaluation metrics
    """
    try:
        if model_id not in ml_engine.list_models():
            raise HTTPException(status_code=404, detail="Model not found")
        
        # TODO: Load evaluation dataset from database
        # For now, create mock evaluation data
        
        import pandas as pd
        import numpy as np
        
        # Create mock evaluation data
        np.random.seed(42)
        n_samples = 200
        
        X_test = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, n_samples),
            'feature_2': np.random.normal(0, 1, n_samples),
            'feature_3': np.random.normal(0, 1, n_samples),
            'feature_4': np.random.normal(0, 1, n_samples)
        })
        y_test = pd.Series(np.random.choice(['A', 'B', 'C'], n_samples))
        
        # Evaluate model
        metrics = ml_engine.evaluate_model(model_id, X_test, y_test)
        
        response = EvaluationResponse(
            success=True,
            model_id=model_id,
            metrics=metrics
        )
        
        logger.info(f"Model {model_id} evaluated successfully")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error evaluating model: {str(e)}")


@router.post("/models/{model_id}/save")
async def save_model(model_id: str, model_name: str):
    """
    Save a trained model to persistent storage.
    
    Args:
        model_id: Model identifier
        model_name: Name for the saved model
        
    Returns:
        Save confirmation
    """
    try:
        if model_id not in ml_engine.list_models():
            raise HTTPException(status_code=404, detail="Model not found")
        
        model_path = ml_engine.save_model(model_id, model_name)
        
        # TODO: Update database with model file path
        
        return {
            "success": True,
            "message": f"Model saved successfully as {model_name}",
            "model_path": model_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving model: {str(e)}")


@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """
    Delete a model from memory and storage.
    
    Args:
        model_id: Model identifier
        
    Returns:
        Deletion confirmation
    """
    try:
        if model_id not in ml_engine.list_models():
            raise HTTPException(status_code=404, detail="Model not found")
        
        ml_engine.remove_model(model_id)
        
        # TODO: Delete model from database and file system
        
        return {
            "success": True,
            "message": f"Model {model_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")


@router.get("/models/{model_id}/feature-importance")
async def get_feature_importance(model_id: str):
    """
    Get feature importance for a trained model.
    
    Args:
        model_id: Model identifier
        
    Returns:
        Feature importance scores
    """
    try:
        if model_id not in ml_engine.list_models():
            raise HTTPException(status_code=404, detail="Model not found")
        
        feature_importance = ml_engine.get_feature_importance(model_id)
        
        if feature_importance is None:
            return {
                "success": False,
                "message": "Feature importance not available for this model type"
            }
        
        # Sort by importance
        sorted_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            "success": True,
            "model_id": model_id,
            "feature_importance": sorted_importance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature importance for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting feature importance: {str(e)}")
