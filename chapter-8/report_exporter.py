"""report_exporter.py

Once your data is cleaned and analysed you need to *share* it with auditors or
engineers.  This module focuses on getting `pandas` DataFrames **out of Python**
and into auditor-friendly file formats (CSV / Excel).

Key takeaways for beginners
--------------------------------------------------------------------
• **CSV** – plain-text, universally readable, but no formatting.
• **Excel** – richer format; we use `xlsxwriter` (via pandas) for auto-sizing
  columns and styling headers.
• We prepend metadata rows (timestamp, record count) so the recipient can
  quickly verify freshness and completeness.
"""

import pandas as pd
from datetime import datetime
import os

def export_to_csv(df: pd.DataFrame, path: str, include_metadata: bool = True) -> None:
    """
    Exports DataFrame to CSV with proper formatting for auditor consumption.
    """
    if df.empty:
        print(f"Warning: DataFrame is empty. Creating empty CSV at {path}")
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        with open(path, 'w') as f:
            pass # create empty file
        return
    
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        if include_metadata:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# Security Compliance Report\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Record Count: {len(df):,}\n")
                f.write(f"# Column Count: {len(df.columns)}\n")
                f.write("#\n")
            
            df.to_csv(path, mode='a', index=False, encoding='utf-8')
        else:
            df.to_csv(path, index=False, encoding='utf-8')
        
        file_size = os.path.getsize(path) / 1024
        print(f"✅ Exported {len(df):,} rows to {path} ({file_size:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")

def export_to_excel(df: pd.DataFrame, path: str, sheet_name: str = "Report") -> None:
    """
    Exports DataFrame to a formatted Excel file.
    Requires `pip install xlsxwriter`.
    """
    if df.empty:
        print(f"Warning: DataFrame is empty. Cannot create Excel file at {path}")
        return

    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': False,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)

        file_size = os.path.getsize(path) / 1024
        print(f"✅ Exported {len(df):,} rows to {path} ({file_size:.1f} KB)")

    except Exception as e:
        print(f"❌ Error exporting to Excel: {e}")
