"""
Core data processing module for the Analytics Engine.
Handles data cleaning, transformation, and validation.
"""

import io
import json
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import chardet
import numpy as np
import pandas as pd
from loguru import logger
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

warnings.filterwarnings('ignore')


class DataProcessor:
    """Main data processing class for cleaning and transforming data."""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json', '.parquet']
        self.encoding_detection_sample_size = 10000
    
    def load_data(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Load data from various file formats.
        
        Args:
            file_path: Path to the data file
            **kwargs: Additional arguments for pandas readers
            
        Returns:
            Loaded DataFrame
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        try:
            if file_extension == '.csv':
                return self._load_csv(file_path, **kwargs)
            elif file_extension in ['.xlsx', '.xls']:
                return self._load_excel(file_path, **kwargs)
            elif file_extension == '.json':
                return self._load_json(file_path, **kwargs)
            elif file_extension == '.parquet':
                return pd.read_parquet(file_path, **kwargs)
            else:
                raise ValueError(f"Handler not implemented for {file_extension}")
                
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            raise
    
    def _load_csv(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """Load CSV file with automatic encoding detection."""
        # Detect encoding
        encoding = self._detect_encoding(file_path)
        
        # Default CSV parameters
        csv_params = {
            'encoding': encoding,
            'low_memory': False,
            'na_values': ['', 'NULL', 'null', 'None', 'N/A', 'n/a', '#N/A'],
            'keep_default_na': True
        }
        csv_params.update(kwargs)
        
        try:
            df = pd.read_csv(file_path, **csv_params)
            logger.info(f"Loaded CSV file: {file_path} with encoding: {encoding}")
            return df
        except UnicodeDecodeError:
            # Fallback to different encodings
            for fallback_encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    csv_params['encoding'] = fallback_encoding
                    df = pd.read_csv(file_path, **csv_params)
                    logger.warning(f"Used fallback encoding {fallback_encoding} for {file_path}")
                    return df
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Could not decode file {file_path} with any encoding")
    
    def _load_excel(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """Load Excel file."""
        excel_params = {
            'na_values': ['', 'NULL', 'null', 'None', 'N/A', 'n/a', '#N/A'],
            'keep_default_na': True
        }
        excel_params.update(kwargs)
        
        df = pd.read_excel(file_path, **excel_params)
        logger.info(f"Loaded Excel file: {file_path}")
        return df
    
    def _load_json(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """Load JSON file."""
        json_params = {'orient': 'records'}
        json_params.update(kwargs)
        
        df = pd.read_json(file_path, **json_params)
        logger.info(f"Loaded JSON file: {file_path}")
        return df
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding."""
        with open(file_path, 'rb') as file:
            sample = file.read(self.encoding_detection_sample_size)
            result = chardet.detect(sample)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)
            
            logger.debug(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
            
            # Use utf-8 as fallback for low confidence
            if confidence < 0.7:
                encoding = 'utf-8'
                logger.warning(f"Low confidence in encoding detection, using utf-8")
            
            return encoding
    
    def profile_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive data profile.
        
        Args:
            df: DataFrame to profile
            
        Returns:
            Dictionary containing data profile information
        """
        profile = {
            'basic_info': self._get_basic_info(df),
            'column_info': self._get_column_info(df),
            'missing_data': self._get_missing_data_info(df),
            'data_types': self._get_data_types_info(df),
            'duplicates': self._get_duplicates_info(df),
            'memory_usage': self._get_memory_usage(df)
        }
        
        return profile
    
    def _get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic information about the DataFrame."""
        return {
            'shape': df.shape,
            'rows': len(df),
            'columns': len(df.columns),
            'size': df.size,
            'empty': df.empty
        }
    
    def _get_column_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed information about each column."""
        column_info = {}
        
        for col in df.columns:
            series = df[col]
            
            info = {
                'dtype': str(series.dtype),
                'non_null_count': series.count(),
                'null_count': series.isnull().sum(),
                'null_percentage': (series.isnull().sum() / len(series)) * 100,
                'unique_count': series.nunique(),
                'unique_percentage': (series.nunique() / len(series)) * 100
            }
            
            # Add statistics for numeric columns
            if is_numeric_dtype(series):
                info.update({
                    'mean': series.mean(),
                    'std': series.std(),
                    'min': series.min(),
                    'max': series.max(),
                    'median': series.median(),
                    'q25': series.quantile(0.25),
                    'q75': series.quantile(0.75)
                })
            
            # Add statistics for datetime columns
            elif is_datetime64_any_dtype(series):
                info.update({
                    'min_date': series.min(),
                    'max_date': series.max(),
                    'date_range': str(series.max() - series.min())
                })
            
            # Add statistics for object/string columns
            else:
                info.update({
                    'most_frequent': series.mode().iloc[0] if not series.mode().empty else None,
                    'most_frequent_count': series.value_counts().iloc[0] if not series.empty else 0
                })
            
            column_info[col] = info
        
        return column_info
    
    def _get_missing_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get missing data information."""
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        return {
            'total_missing': missing_counts.sum(),
            'missing_percentage': (missing_counts.sum() / df.size) * 100,
            'columns_with_missing': missing_counts[missing_counts > 0].to_dict(),
            'missing_percentages': missing_percentages[missing_percentages > 0].to_dict()
        }
    
    def _get_data_types_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get data types information."""
        dtype_counts = df.dtypes.value_counts()
        
        return {
            'dtype_counts': dtype_counts.to_dict(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist()
        }
    
    def _get_duplicates_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get duplicates information."""
        duplicate_rows = df.duplicated().sum()
        
        return {
            'duplicate_rows': int(duplicate_rows),
            'duplicate_percentage': (duplicate_rows / len(df)) * 100,
            'unique_rows': len(df) - duplicate_rows
        }
    
    def _get_memory_usage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get memory usage information."""
        memory_usage = df.memory_usage(deep=True)
        
        return {
            'total_memory_mb': memory_usage.sum() / (1024 * 1024),
            'memory_per_column': (memory_usage / (1024 * 1024)).to_dict()
        }
    
    def clean_data(self, df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Clean data based on configuration.
        
        Args:
            df: DataFrame to clean
            config: Cleaning configuration
            
        Returns:
            Cleaned DataFrame
        """
        if config is None:
            config = {}
        
        df_cleaned = df.copy()
        
        # Remove duplicates
        if config.get('remove_duplicates', True):
            initial_rows = len(df_cleaned)
            df_cleaned = df_cleaned.drop_duplicates()
            removed_rows = initial_rows - len(df_cleaned)
            if removed_rows > 0:
                logger.info(f"Removed {removed_rows} duplicate rows")
        
        # Handle missing values
        missing_strategy = config.get('missing_strategy', 'drop')
        if missing_strategy == 'drop':
            df_cleaned = self._drop_missing_values(df_cleaned, config)
        elif missing_strategy == 'fill':
            df_cleaned = self._fill_missing_values(df_cleaned, config)
        
        # Clean column names
        if config.get('clean_column_names', True):
            df_cleaned = self._clean_column_names(df_cleaned)
        
        # Remove outliers
        if config.get('remove_outliers', False):
            df_cleaned = self._remove_outliers(df_cleaned, config)
        
        # Convert data types
        if config.get('convert_types', True):
            df_cleaned = self._convert_data_types(df_cleaned, config)
        
        logger.info(f"Data cleaning completed. Shape: {df.shape} -> {df_cleaned.shape}")
        
        return df_cleaned
    
    def _drop_missing_values(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Drop missing values based on configuration."""
        threshold = config.get('missing_threshold', 0.5)
        
        # Drop columns with too many missing values
        missing_percentages = df.isnull().sum() / len(df)
        columns_to_drop = missing_percentages[missing_percentages > threshold].index
        
        if len(columns_to_drop) > 0:
            df = df.drop(columns=columns_to_drop)
            logger.info(f"Dropped columns with >{threshold*100}% missing values: {list(columns_to_drop)}")
        
        # Drop rows with missing values
        initial_rows = len(df)
        df = df.dropna()
        removed_rows = initial_rows - len(df)
        
        if removed_rows > 0:
            logger.info(f"Dropped {removed_rows} rows with missing values")
        
        return df
    
    def _fill_missing_values(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Fill missing values based on configuration."""
        fill_strategies = config.get('fill_strategies', {})
        
        for column in df.columns:
            if df[column].isnull().any():
                strategy = fill_strategies.get(column, 'auto')
                
                if strategy == 'auto':
                    if is_numeric_dtype(df[column]):
                        strategy = 'median'
                    else:
                        strategy = 'mode'
                
                if strategy == 'mean':
                    df[column] = df[column].fillna(df[column].mean())
                elif strategy == 'median':
                    df[column] = df[column].fillna(df[column].median())
                elif strategy == 'mode':
                    mode_value = df[column].mode()
                    if not mode_value.empty:
                        df[column] = df[column].fillna(mode_value.iloc[0])
                elif strategy == 'forward_fill':
                    df[column] = df[column].fillna(method='ffill')
                elif strategy == 'backward_fill':
                    df[column] = df[column].fillna(method='bfill')
                elif isinstance(strategy, (str, int, float)):
                    df[column] = df[column].fillna(strategy)
        
        return df
    
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean column names."""
        # Convert to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)
        return df
    
    def _remove_outliers(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Remove outliers using IQR method."""
        outlier_method = config.get('outlier_method', 'iqr')
        outlier_threshold = config.get('outlier_threshold', 1.5)
        
        if outlier_method == 'iqr':
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for column in numeric_columns:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - outlier_threshold * IQR
                upper_bound = Q3 + outlier_threshold * IQR
                
                initial_rows = len(df)
                df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                removed_rows = initial_rows - len(df)
                
                if removed_rows > 0:
                    logger.info(f"Removed {removed_rows} outliers from column '{column}'")
        
        return df
    
    def _convert_data_types(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Convert data types automatically or based on configuration."""
        type_conversions = config.get('type_conversions', {})
        
        for column in df.columns:
            if column in type_conversions:
                target_type = type_conversions[column]
                try:
                    if target_type == 'datetime':
                        df[column] = pd.to_datetime(df[column])
                    elif target_type == 'category':
                        df[column] = df[column].astype('category')
                    else:
                        df[column] = df[column].astype(target_type)
                    logger.debug(f"Converted column '{column}' to {target_type}")
                except Exception as e:
                    logger.warning(f"Failed to convert column '{column}' to {target_type}: {e}")
        
        return df
