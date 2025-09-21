"""
Statistical analysis endpoints for the Analytics Engine.
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import scipy.stats as stats
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

router = APIRouter()


class StatisticalTestRequest(BaseModel):
    """Request model for statistical tests."""
    dataset_id: str
    test_type: str
    column1: str
    column2: Optional[str] = None
    group_column: Optional[str] = None
    alpha: float = 0.05


class StatisticalTestResponse(BaseModel):
    """Response model for statistical tests."""
    success: bool
    test_type: str
    statistic: float
    p_value: float
    critical_value: Optional[float] = None
    confidence_interval: Optional[List[float]] = None
    interpretation: str
    significant: bool


class DescriptiveStatsResponse(BaseModel):
    """Response model for descriptive statistics."""
    success: bool
    column: str
    statistics: Dict


class CorrelationResponse(BaseModel):
    """Response model for correlation analysis."""
    success: bool
    correlation_matrix: Dict
    significant_correlations: List[Dict]


@router.post("/descriptive/{dataset_id}")
async def get_descriptive_statistics(
    dataset_id: str,
    column: Optional[str] = None
) -> Dict:
    """
    Get descriptive statistics for a dataset or specific column.
    
    Args:
        dataset_id: Dataset identifier
        column: Specific column (if None, analyze all numeric columns)
        
    Returns:
        Descriptive statistics
    """
    try:
        # TODO: Load dataset from database
        # For now, create mock data
        np.random.seed(42)
        n_samples = 1000
        
        df = pd.DataFrame({
            'numeric_col1': np.random.normal(50, 15, n_samples),
            'numeric_col2': np.random.exponential(2, n_samples),
            'numeric_col3': np.random.uniform(0, 100, n_samples),
            'category_col': np.random.choice(['A', 'B', 'C'], n_samples)
        })
        
        if column:
            if column not in df.columns:
                raise HTTPException(status_code=404, detail=f"Column '{column}' not found")
            
            if df[column].dtype in ['object', 'category']:
                # Categorical statistics
                stats_dict = {
                    'count': int(df[column].count()),
                    'unique': int(df[column].nunique()),
                    'top': df[column].mode().iloc[0] if not df[column].mode().empty else None,
                    'freq': int(df[column].value_counts().iloc[0]) if not df[column].empty else 0,
                    'value_counts': df[column].value_counts().to_dict()
                }
            else:
                # Numeric statistics
                desc = df[column].describe()
                stats_dict = {
                    'count': int(desc['count']),
                    'mean': float(desc['mean']),
                    'std': float(desc['std']),
                    'min': float(desc['min']),
                    'q25': float(desc['25%']),
                    'median': float(desc['50%']),
                    'q75': float(desc['75%']),
                    'max': float(desc['max']),
                    'skewness': float(df[column].skew()),
                    'kurtosis': float(df[column].kurtosis()),
                    'variance': float(df[column].var())
                }
            
            return DescriptiveStatsResponse(
                success=True,
                column=column,
                statistics=stats_dict
            )
        else:
            # All columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            
            all_stats = {}
            
            # Numeric columns
            for col in numeric_cols:
                desc = df[col].describe()
                all_stats[col] = {
                    'type': 'numeric',
                    'count': int(desc['count']),
                    'mean': float(desc['mean']),
                    'std': float(desc['std']),
                    'min': float(desc['min']),
                    'q25': float(desc['25%']),
                    'median': float(desc['50%']),
                    'q75': float(desc['75%']),
                    'max': float(desc['max']),
                    'skewness': float(df[col].skew()),
                    'kurtosis': float(df[col].kurtosis())
                }
            
            # Categorical columns
            for col in categorical_cols:
                all_stats[col] = {
                    'type': 'categorical',
                    'count': int(df[col].count()),
                    'unique': int(df[col].nunique()),
                    'top': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                    'freq': int(df[col].value_counts().iloc[0]) if not df[col].empty else 0
                }
            
            return {
                'success': True,
                'dataset_id': dataset_id,
                'statistics': all_stats
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting descriptive statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@router.post("/correlation/{dataset_id}")
async def get_correlation_analysis(
    dataset_id: str,
    method: str = "pearson",
    threshold: float = 0.5
) -> CorrelationResponse:
    """
    Perform correlation analysis on numeric columns.
    
    Args:
        dataset_id: Dataset identifier
        method: Correlation method ('pearson', 'spearman', 'kendall')
        threshold: Threshold for significant correlations
        
    Returns:
        Correlation matrix and significant correlations
    """
    try:
        # TODO: Load dataset from database
        # Create mock data
        np.random.seed(42)
        n_samples = 1000
        
        # Create correlated data
        x1 = np.random.normal(0, 1, n_samples)
        x2 = x1 + np.random.normal(0, 0.5, n_samples)  # Correlated with x1
        x3 = np.random.normal(0, 1, n_samples)  # Independent
        x4 = -x1 + np.random.normal(0, 0.3, n_samples)  # Negatively correlated with x1
        
        df = pd.DataFrame({
            'variable_1': x1,
            'variable_2': x2,
            'variable_3': x3,
            'variable_4': x4
        })
        
        # Calculate correlation matrix
        if method == "pearson":
            corr_matrix = df.corr(method='pearson')
        elif method == "spearman":
            corr_matrix = df.corr(method='spearman')
        elif method == "kendall":
            corr_matrix = df.corr(method='kendall')
        else:
            raise ValueError(f"Unsupported correlation method: {method}")
        
        # Find significant correlations
        significant_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                correlation = corr_matrix.iloc[i, j]
                
                if abs(correlation) >= threshold:
                    significant_correlations.append({
                        'variable_1': col1,
                        'variable_2': col2,
                        'correlation': float(correlation),
                        'strength': _interpret_correlation_strength(abs(correlation))
                    })
        
        return CorrelationResponse(
            success=True,
            correlation_matrix=corr_matrix.to_dict(),
            significant_correlations=significant_correlations
        )
        
    except Exception as e:
        logger.error(f"Error performing correlation analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error in correlation analysis: {str(e)}")


@router.post("/test")
async def perform_statistical_test(request: StatisticalTestRequest) -> StatisticalTestResponse:
    """
    Perform statistical tests.
    
    Args:
        request: Statistical test configuration
        
    Returns:
        Test results and interpretation
    """
    try:
        # TODO: Load dataset from database
        # Create mock data based on test type
        np.random.seed(42)
        n_samples = 100
        
        if request.test_type == "t_test_one_sample":
            # One-sample t-test
            data = np.random.normal(50, 10, n_samples)
            population_mean = 48  # Test against this value
            
            statistic, p_value = stats.ttest_1samp(data, population_mean)
            
            interpretation = _interpret_t_test(statistic, p_value, request.alpha, "one-sample")
            
        elif request.test_type == "t_test_two_sample":
            # Two-sample t-test
            group1 = np.random.normal(50, 10, n_samples)
            group2 = np.random.normal(52, 10, n_samples)
            
            statistic, p_value = stats.ttest_ind(group1, group2)
            
            interpretation = _interpret_t_test(statistic, p_value, request.alpha, "two-sample")
            
        elif request.test_type == "chi_square":
            # Chi-square test of independence
            # Create contingency table
            observed = np.array([[20, 30, 25], [15, 35, 30]])
            
            statistic, p_value, dof, expected = stats.chi2_contingency(observed)
            
            interpretation = _interpret_chi_square(statistic, p_value, request.alpha)
            
        elif request.test_type == "anova":
            # One-way ANOVA
            group1 = np.random.normal(50, 10, n_samples)
            group2 = np.random.normal(52, 10, n_samples)
            group3 = np.random.normal(48, 10, n_samples)
            
            statistic, p_value = stats.f_oneway(group1, group2, group3)
            
            interpretation = _interpret_anova(statistic, p_value, request.alpha)
            
        elif request.test_type == "normality_test":
            # Shapiro-Wilk normality test
            data = np.random.normal(50, 10, min(n_samples, 5000))  # Shapiro-Wilk has sample size limit
            
            statistic, p_value = stats.shapiro(data)
            
            interpretation = _interpret_normality_test(statistic, p_value, request.alpha)
            
        else:
            raise ValueError(f"Unsupported test type: {request.test_type}")
        
        return StatisticalTestResponse(
            success=True,
            test_type=request.test_type,
            statistic=float(statistic),
            p_value=float(p_value),
            interpretation=interpretation,
            significant=p_value < request.alpha
        )
        
    except Exception as e:
        logger.error(f"Error performing statistical test: {e}")
        raise HTTPException(status_code=500, detail=f"Error in statistical test: {str(e)}")


@router.get("/test-types")
async def get_available_tests():
    """
    Get available statistical tests.
    
    Returns:
        List of available statistical tests
    """
    tests = [
        {
            "type": "t_test_one_sample",
            "name": "One-Sample T-Test",
            "description": "Tests if sample mean differs from population mean",
            "required_columns": ["numeric_column"],
            "parameters": ["population_mean"]
        },
        {
            "type": "t_test_two_sample",
            "name": "Two-Sample T-Test",
            "description": "Tests if two groups have different means",
            "required_columns": ["numeric_column", "group_column"],
            "parameters": []
        },
        {
            "type": "chi_square",
            "name": "Chi-Square Test",
            "description": "Tests independence between categorical variables",
            "required_columns": ["categorical_column1", "categorical_column2"],
            "parameters": []
        },
        {
            "type": "anova",
            "name": "One-Way ANOVA",
            "description": "Tests if multiple groups have different means",
            "required_columns": ["numeric_column", "group_column"],
            "parameters": []
        },
        {
            "type": "normality_test",
            "name": "Normality Test (Shapiro-Wilk)",
            "description": "Tests if data follows normal distribution",
            "required_columns": ["numeric_column"],
            "parameters": []
        }
    ]
    
    return {"statistical_tests": tests}


def _interpret_correlation_strength(correlation: float) -> str:
    """Interpret correlation strength."""
    if correlation >= 0.8:
        return "very strong"
    elif correlation >= 0.6:
        return "strong"
    elif correlation >= 0.4:
        return "moderate"
    elif correlation >= 0.2:
        return "weak"
    else:
        return "very weak"


def _interpret_t_test(statistic: float, p_value: float, alpha: float, test_type: str) -> str:
    """Interpret t-test results."""
    if p_value < alpha:
        if test_type == "one-sample":
            return f"Reject null hypothesis (p={p_value:.4f} < α={alpha}). Sample mean significantly differs from population mean."
        else:
            return f"Reject null hypothesis (p={p_value:.4f} < α={alpha}). Groups have significantly different means."
    else:
        if test_type == "one-sample":
            return f"Fail to reject null hypothesis (p={p_value:.4f} ≥ α={alpha}). No significant difference from population mean."
        else:
            return f"Fail to reject null hypothesis (p={p_value:.4f} ≥ α={alpha}). No significant difference between groups."


def _interpret_chi_square(statistic: float, p_value: float, alpha: float) -> str:
    """Interpret chi-square test results."""
    if p_value < alpha:
        return f"Reject null hypothesis (p={p_value:.4f} < α={alpha}). Variables are significantly associated."
    else:
        return f"Fail to reject null hypothesis (p={p_value:.4f} ≥ α={alpha}). No significant association between variables."


def _interpret_anova(statistic: float, p_value: float, alpha: float) -> str:
    """Interpret ANOVA results."""
    if p_value < alpha:
        return f"Reject null hypothesis (p={p_value:.4f} < α={alpha}). At least one group mean is significantly different."
    else:
        return f"Fail to reject null hypothesis (p={p_value:.4f} ≥ α={alpha}). No significant difference between group means."


def _interpret_normality_test(statistic: float, p_value: float, alpha: float) -> str:
    """Interpret normality test results."""
    if p_value < alpha:
        return f"Reject null hypothesis (p={p_value:.4f} < α={alpha}). Data does not follow normal distribution."
    else:
        return f"Fail to reject null hypothesis (p={p_value:.4f} ≥ α={alpha}). Data appears to follow normal distribution."
