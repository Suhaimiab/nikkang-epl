"""
Enhanced Prediction Matrix with PNG Export
Adds matplotlib-based PNG generation capability
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.table import Table
import numpy as np
from io import BytesIO

def create_prediction_matrix_png(df, week, title="Nikkang KK EPL Prediction Matrix"):
    """
    Create a PNG image of the prediction matrix using matplotlib
    
    Args:
        df: DataFrame with prediction data
        week: Week number
        title: Chart title
    
    Returns:
        BytesIO object containing PNG image
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=(max(16, len(df.columns) * 1.2), max(10, len(df) * 0.5)))
    ax.axis('tight')
    ax.axis('off')
    
    # Add title
    fig.suptitle(f'{title}\nWeek {week}', 
                 fontsize=20, fontweight='bold', color='#2E7D32', y=0.98)
    
    # Add subtitle with date
    from datetime import datetime
    subtitle = f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')}"
    fig.text(0.5, 0.94, subtitle, ha='center', fontsize=10, color='#666')
    
    # Create table
    table_data = []
    
    # Headers
    headers = list(df.columns)
    table_data.append(headers)
    
    # Data rows
    for _, row in df.iterrows():
        table_data.append(list(row))
    
    # Create the table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     bbox=[0, 0, 1, 1])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Color header row
    for i in range(len(headers)):
        cell = table[(0, i)]
        cell.set_facecolor('#2E7D32')
        cell.set_text_props(weight='bold', color='white', fontsize=10)
        cell.set_edgecolor('white')
        cell.set_linewidth(2)
    
    # Style data rows
    for i in range(1, len(table_data)):
        for j in range(len(headers)):
            cell = table[(i, j)]
            
            # Alternate row colors
            if i % 2 == 0:
                cell.set_facecolor('#f9f9f9')
            else:
                cell.set_facecolor('white')
            
            # Special formatting for specific columns
            col_name = headers[j]
            
            if col_name == "Match":
                cell.set_facecolor('#E8F5E9')
                cell.set_text_props(weight='bold')
            
            elif col_name in ["Home", "Away"]:
                cell.set_text_props(ha='left')
            
            elif col_name == "GOTW" and cell.get_text().get_text() == "⭐":
                cell.set_text_props(color='#FFA000', weight='bold', fontsize=12)
            
            cell.set_edgecolor('#ddd')
            cell.set_linewidth(0.5)
    
    # Add footer
    footer_text = "⭐ = Game of the Week (Double Points) | Nikkang KK EPL Prediction Competition"
    fig.text(0.5, 0.02, footer_text, ha='center', fontsize=9, color='#666', style='italic')
    
    # Adjust layout
    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)
    
    # Save to BytesIO
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buf.seek(0)
    plt.close()
    
    return buf


def create_compact_matrix_png(df, week):
    """
    Create a more compact PNG for easier sharing
    
    Args:
        df: DataFrame with prediction data
        week: Week number
    
    Returns:
        BytesIO object containing PNG image
    """
    # Calculate dynamic size based on data
    n_cols = len(df.columns)
    n_rows = len(df)
    
    # Adjust figure size
    fig_width = min(20, max(12, n_cols * 0.8))
    fig_height = min(14, max(8, n_rows * 0.35 + 2))
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')
    
    # Title
    title_text = f'Week {week} Prediction Matrix'
    ax.text(0.5, 0.97, title_text, transform=ax.transAxes,
            fontsize=16, fontweight='bold', color='#2E7D32',
            ha='center', va='top')
    
    # Prepare data
    table_data = [list(df.columns)] + df.values.tolist()
    
    # Create table
    table = ax.table(cellText=table_data, cellLoc='center',
                     bbox=[0.05, 0.05, 0.9, 0.88])
    
    # Style
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    
    # Header styling
    for i in range(n_cols):
        cell = table[(0, i)]
        cell.set_facecolor('#2E7D32')
        cell.set_text_props(weight='bold', color='white', fontsize=9)
        cell.set_height(0.08)
    
    # Data styling
    for i in range(1, n_rows + 1):
        for j in range(n_cols):
            cell = table[(i, j)]
            cell.set_height(0.06)
            
            # Zebra striping
            if i % 2 == 0:
                cell.set_facecolor('#f5f5f5')
            
            # Match number column
            if j == 0:
                cell.set_facecolor('#E8F5E9')
    
    # Save
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                facecolor='white', pad_inches=0.3)
    buf.seek(0)
    plt.close()
    
    return buf
