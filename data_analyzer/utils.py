# data_analyzer/utils.py
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

# data_analyzer/utils.py - Replace the extract_headers_and_data function

# data_analyzer/utils.py - Replace the extract_headers_and_data function

def extract_headers_and_data(file_path, sheet_name=None):
    """Extract headers, subheaders, and data from Excel file"""
    try:
        # First, try to read with multi-level headers
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=[0, 1])
        else:
            df = pd.read_excel(file_path, header=[0, 1])
        
        # Check if we actually have multi-level columns
        if isinstance(df.columns, pd.MultiIndex):
            # Get headers and subheaders
            headers_info = {}
            column_mapping = {}  # To store original multi-index to string mapping
            
            for col in df.columns:
                # Convert all parts to string to avoid type errors
                header = str(col[0]) if col[0] is not None and not pd.isna(col[0]) else 'Unnamed'
                subheader = str(col[1]) if col[1] is not None and not pd.isna(col[1]) else 'Unnamed'
                
                # Handle unnamed columns
                if 'Unnamed' in header:
                    header = f'Column_{df.columns.get_loc(col)}'
                
                if header not in headers_info:
                    headers_info[header] = []
                headers_info[header].append(subheader)
                
                # Create column name
                col_name = f"{header}_{subheader}" if subheader and subheader != 'Unnamed' else header
                column_mapping[col] = col_name
            
            # Convert multi-index columns to single level
            df.columns = [column_mapping[col] for col in df.columns]
            
            # Get first header (main column) and its subcolumns for X-axis
            first_header = list(headers_info.keys())[0] if headers_info else None
            x_columns = []
            if first_header:
                # Get all subcolumns of the first header
                for subheader in headers_info[first_header]:
                    col_name = f"{first_header}_{subheader}" if subheader and subheader != 'Unnamed' else first_header
                    if col_name in df.columns:
                        x_columns.append(col_name)
            
            # Get Y columns (all columns except first header columns)
            y_columns = [col for col in df.columns if not any(col == x_col for x_col in x_columns)]
            
            return {
                'headers_info': headers_info,
                'data': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'x_columns': x_columns,
                'y_columns': y_columns,
                'first_header': first_header
            }
    except Exception as e:
        print(f"Error reading multi-level headers: {e}")
    
    # If multi-level reading fails, try single level
    try:
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)
        
        # For single-level headers
        headers_info = {}
        
        # First column and its values become X options
        if len(df.columns) > 0:
            first_col = str(df.columns[0])
            headers_info[first_col] = ['value']  # Single subcolumn
            x_columns = [first_col]
            y_columns = [str(col) for col in df.columns[1:]]  # All other columns
        else:
            x_columns = []
            y_columns = []
        
        return {
            'headers_info': headers_info,
            'data': df.to_dict('records'),
            'columns': [str(col) for col in df.columns.tolist()],
            'x_columns': x_columns,
            'y_columns': y_columns,
            'first_header': str(df.columns[0]) if len(df.columns) > 0 else None
        }
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return {
            'headers_info': {},
            'data': [],
            'columns': [],
            'x_columns': [],
            'y_columns': [],
            'first_header': None
        }

def get_excel_sheets(file_path):
    """Get all sheet names from Excel file"""
    try:
        excel_file = pd.ExcelFile(file_path)
        return excel_file.sheet_names
    except Exception as e:
        print(f"Error getting sheets: {e}")
        return []

def create_plot(data, x_column, y_columns, plot_type='line', title='Data Visualization'):
    """Create plotly graph based on parameters"""
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    colors = ['#FF6B35', '#00A9E0', '#84BD00', '#FFD100', '#7C878E']  # NXP-inspired colors
    
    for i, y_col in enumerate(y_columns):
        color = colors[i % len(colors)]
        
        if plot_type == 'line':
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='lines+markers',
                name=y_col,
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))
        elif plot_type == 'bar':
            fig.add_trace(go.Bar(
                x=df[x_column],
                y=df[y_col],
                name=y_col,
                marker_color=color
            ))
        elif plot_type == 'scatter':
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[y_col],
                mode='markers',
                name=y_col,
                marker=dict(color=color, size=10)
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_column,
        yaxis_title='Values',
        hovermode='x unified',
        template='plotly_white',
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig.to_json()


def export_plot_as_image(fig_json, format='pdf'):
    """Export plotly figure as PDF or JPG"""
    import plotly.io as pio
    fig = go.Figure(json.loads(fig_json))
    
    if format == 'pdf':
        return pio.to_image(fig, format='pdf')
    else:
        return pio.to_image(fig, format='jpg')