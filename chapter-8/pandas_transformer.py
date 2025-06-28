"""pandas_transformer.py

After you have fetched raw JSON data from AWS, you usually need to *clean* and
*reshape* it before you can run analytics or build reports.  This module
contains small, focused functions that take plain Python lists / dicts and
return a `pandas.DataFrame` – the Swiss-army knife for data analysis in
Python.

What beginners should know
--------------------------------------------------------------------
• A **DataFrame** is like a spreadsheet in memory: rows + columns with powerful
  query capabilities.
• All functions are “pure” – they do not touch disk or network. They simply
  convert or augment data in memory.
• `pd.json_normalize()` is your friend when flattening deeply nested JSON
  structures returned by AWS APIs.
"""

import pandas as pd
from datetime import datetime

def findings_to_dataframe(findings: list[dict]) -> pd.DataFrame:
    """
    Converts a list of Security Hub findings into a flat DataFrame.
    """
    if not findings:
        return pd.DataFrame(columns=['Id', 'Title', 'CreatedAt', 'Severity_Label'])
    
    try:
        df = pd.json_normalize(
            data=findings,
            meta=["Id", "Title", "CreatedAt", "UpdatedAt", "Description"],
            sep="_"
        )

        column_mappings = {
            "Severity_Label": "Severity",
            "Workflow_Status": "WorkflowStatus", 
            "Compliance_Status": "ComplianceStatus",
            "ProductArn": "ProductName"
        }
        
        for old_col, new_col in column_mappings.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        datetime_columns = ['CreatedAt', 'UpdatedAt']
        for col in datetime_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
        return df
        
    except Exception as e:
        print(f"Error processing findings to DataFrame: {e}")
        return pd.DataFrame()

def expand_resources(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expands Security Hub findings that contain multiple resources into separate rows.
    """
    if "Resources" not in df.columns:
        return df
    
    if df.empty:
        return df
    
    try:
        exploded = df.explode("Resources")
        exploded = exploded.dropna(subset=["Resources"])
        
        if exploded.empty:
            return df
        
        resources_df = pd.json_normalize(exploded["Resources"], sep="_")
        resources_df.columns = ["Resource_" + col for col in resources_df.columns]
        
        result = exploded.drop(columns=["Resources"]).reset_index(drop=True).join(resources_df)
        return result
        
    except Exception as e:
        print(f"Error expanding resources: {e}")
        return df

def add_business_logic_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enhances the DataFrame with calculated columns for business analysis and reporting.
    """
    if df.empty:
        return df
        
    df = df.copy()
    
    try:
        if "CreatedAt" in df.columns:
            df["CreatedAt"] = pd.to_datetime(df["CreatedAt"], errors='coerce')
        
        severity_map = {
            "INFORMATIONAL": 0,
            "LOW": 1, 
            "MEDIUM": 2, 
            "HIGH": 3, 
            "CRITICAL": 4
        }
        
        if "Severity" in df.columns:
            df["SeverityLevel"] = df["Severity"].map(severity_map).fillna(0).astype(int)
        
        if "CreatedAt" in df.columns:
            now = pd.Timestamp.utcnow()
            df["AgeDays"] = (now - df["CreatedAt"]).dt.days
            
            if "SeverityLevel" in df.columns:
                sla_days = df["SeverityLevel"].map({4: 1, 3: 7, 2: 30, 1: 90, 0: 365})
                df["SLAViolation"] = df["AgeDays"] > sla_days
        
        if "Resource_Tags" in df.columns:
            df["Owner"] = df["Resource_Tags"].apply(
                lambda tags: extract_tag_value(tags, ["Owner", "owner", "Team", "team"])
            )
            df["Environment"] = df["Resource_Tags"].apply(
                lambda tags: extract_tag_value(tags, ["Environment", "Env", "Stage"])
            )
        
        return df
        
    except Exception as e:
        print(f"Error adding business logic columns: {e}")
        return df

def extract_tag_value(tags_dict: dict, possible_keys: list[str]) -> str:
    """
    Helper function to extract tag values using multiple possible key names.
    """
    if not isinstance(tags_dict, dict):
        return "Unknown"
    
    for key in possible_keys:
        if key in tags_dict:
            return str(tags_dict[key])
    
    return "Unknown"

def preview_dataframe_analysis(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Comprehensive preview of DataFrame structure and content for quality assurance.
    """
    if df.empty:
        print(f"⚠️  {name} is empty!")
        return
    
    print(f"\n=== {name} Analysis ===")
    print(f"Dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    if "Severity" in df.columns:
        print(f"\nSeverity Distribution:")
        print(df["Severity"].value_counts().to_string())
    
    if "Resource_Type" in df.columns:
        print(f"\nTop 5 Resource Types:")
        print(df["Resource_Type"].value_counts().head().to_string())
    
    print(f"\nFirst 3 rows:")
    print(df.head(3).to_string())
