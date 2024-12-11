import dash
from dash import dcc, html
from dash.dependencies import Input, Output , State
import pandas as pd
import plotly.graph_objects as go
from flask_cors import CORS
import random
import os
from flask import Flask, request 

# Load CSV data
csv_path = r"Test Try 2.csv"
df = pd.read_csv(csv_path, encoding='latin1')

# Convert 'date' column to datetime, handling errors gracefully
df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)

# Define colors for specific features
feature_colors = {
    'All-Wheel Drive': '#000000',
    'Steering': '#004aad',
    'Interior Quality': '#ff914d',
    'Engine': '#5ce1e6',
    'Brake': '#ff66c4',
    'Seats': '#98FB98',
    'Transmission': '#800080',
    'Electric Motor': '#006400'
}

# Initialize the Dash app
server = Flask(__name__)
app = dash.Dash(__name__, server=server)
CORS(app.server, resources={r"/": {"origins": ""}})

# Define styles with larger font sizes
dropdown_style = {
    'width': '200px',
    'min-width': '200px',
    'max-width': '200px',
    'color': 'black',
    'backgroundColor': '#fff',
    'margin-bottom': '10px',
    'padding': '8px 10px',
    'border': 'none',
    'border-radius': '20px',
    'cursor': 'pointer',
    'textAlign': 'center',
    'fontSize': '18px'  # Increased font size
}

date_picker_style = {
    'width': '200px',
    'min-width': '200px',
    'max-width': '200px',
    'color': 'black',
    'backgroundColor': '#fff',
    'margin-bottom': '10px',
    'padding': '8px 10px',
    'border': 'none',
    'border-radius': '20px',
    'cursor': 'pointer',
    'textAlign': 'center',
    'fontSize': '18px'  # Increased font size
}

label_style = {
    'fontSize': '18px',  # Increased font size for labels
    'fontWeight': 'bold'
}

# Define layouts
main_layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Label('Select Brand', style=label_style),
                dcc.Dropdown(
                    id='brand-dropdown',
                    multi=True,
                    style=dropdown_style
                )
            ], style={'margin-bottom': '20px'}),
            html.Div([
                html.Label('Select Model', style=label_style),
                dcc.Dropdown(
                    id='model-dropdown',
                    multi=True,
                    style=dropdown_style
                )
            ], style={'margin-bottom': '20px'}),
            html.Div([
                html.Label('Select Fact', style=label_style),
                dcc.Dropdown(
                    id='fact-dropdown',
                    multi=True,
                    style=dropdown_style
                )
            ], style={'margin-bottom': '20px'}),
            html.Div([
                html.Label('Select Country', style=label_style),
                dcc.Dropdown(
                    id='country-dropdown',
                    multi=True,
                    style=dropdown_style
                )
            ], style={'margin-bottom': '20px'}),
            html.Div([
                html.Label('Select Source', style=label_style),
                dcc.Dropdown(
                    id='source-dropdown',
                    multi=True,
                    style=dropdown_style
                )
            ], style={'margin-bottom': '20px'}),
            html.Div([
                html.Label('Select Date Range', style=label_style),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=df['date'].min().strftime('%Y-%m-%d'),
                    end_date=df['date'].max().strftime('%Y-%m-%d'),
                    display_format='DD-MM-YYYY',
                    style=date_picker_style
                )
            ], style={'margin-bottom': '20px'}),
        ], style={'flex': '1', 'padding': '20px'}),
        html.Div([
            dcc.Graph(id='bar-chart', figure={})
        ], style={'flex': '3', 'padding': '20px'}),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
])



feedback_layout = html.Div([
    html.H1(id='feedback-title', style={'fontSize': '24px'}),  # Increased font size for header
    html.Table(id='feedback-table')
])

# Initialize the Dash app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # URL handling
     dcc.Store(id='stored-dropdown-values', storage_type='local'),
    html.Div(id='page-content')  # Page content will be updated based on URL
])
@app.callback(
    Output('stored-dropdown-values', 'data'),
    [Input('brand-dropdown', 'value'),
     Input('model-dropdown', 'value'),
     Input('fact-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('source-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def save_dropdown_values(brand, model, fact, country, source, from_date, to_date):
    return {
        'brand': brand,
        'model': model,
        'fact': fact,
        'country': country,
        'source': source,
        'from_date': from_date,
        'to_date': to_date
    }

@app.callback(
    [Output('brand-dropdown', 'value'),
     Output('model-dropdown', 'value'),
     Output('fact-dropdown', 'value'),
     Output('country-dropdown', 'value'),
     Output('source-dropdown', 'value'),
     Output('date-picker-range', 'start_date'),
     Output('date-picker-range', 'end_date')],
    [Input('stored-dropdown-values', 'data')]
)
def load_dropdown_values(stored_values):
    if stored_values is None:
        return [None] * 7
    return (
        stored_values.get('brand'),
        stored_values.get('model'),
        stored_values.get('fact'),
        stored_values.get('country'),
        stored_values.get('source'),
        stored_values.get('from_date'),
        stored_values.get('to_date')
    )

# Other callback functions remain the same

# Callback to update brand dropdown with all available brands
@app.callback(
    Output('brand-dropdown', 'options'),
    [Input('brand-dropdown', 'value')]
)
def update_brand_dropdown(_):
    brands = df['brand'].unique()
    return [{'label': 'All', 'value': 'All'}] + [{'label': brand, 'value': brand} for brand in brands]

# Update model dropdown based on selected brand
@app.callback(
    Output('model-dropdown', 'options'),
    [Input('brand-dropdown', 'value')]
)
def update_model_dropdown(selected_brands):
    if not selected_brands or 'All' in selected_brands:
        models = df['model'].unique()
    else:
        models = df[df['brand'].isin(selected_brands)]['model'].unique()
    return [{'label': 'All', 'value': 'All'}] + [{'label': model, 'value': model} for model in models]

# Update fact dropdown based on selected model
@app.callback(
    Output('fact-dropdown', 'options'),
    [Input('model-dropdown', 'value')]
)
def update_fact_dropdown(selected_models):
    if not selected_models or 'All' in selected_models:
        facts = df['fact'].unique()
    else:
        facts = df[df['model'].isin(selected_models)]['fact'].unique()
    return [{'label': 'All', 'value': 'All'}] + [{'label': fact, 'value': fact} for fact in facts]

# Update country dropdown based on selected model and fact
@app.callback(
    Output('country-dropdown', 'options'),
    [Input('model-dropdown', 'value'),
     Input('fact-dropdown', 'value')]
)
def update_country_dropdown(selected_models, selected_facts):
    if not selected_models or not selected_facts or 'All' in selected_models or 'All' in selected_facts:
        countries = df['country'].unique()
    else:
        countries = df[(df['model'].isin(selected_models)) & (df['fact'].isin(selected_facts))]['country'].unique()
    return [{'label': 'All', 'value': 'All'}] + [{'label': country, 'value': country} for country in countries]

# Update source dropdown based on selected model, fact, and country
@app.callback(
    Output('source-dropdown', 'options'),
    [Input('model-dropdown', 'value'),
     Input('fact-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def update_source_dropdown(selected_models, selected_facts, selected_countries):
    if not selected_models or not selected_facts or not selected_countries or 'All' in selected_models or 'All' in selected_facts or 'All' in selected_countries:
        sources = df['source'].unique()
    else:
        sources = df[(df['model'].isin(selected_models)) & 
                     (df['fact'].isin(selected_facts)) & 
                     (df['country'].isin(selected_countries))]['source'].unique()
    return [{'label': 'All', 'value': 'All'}] + [{'label': source, 'value': source} for source in sources]

# Update bar chart based on selected features and date range
# Update bar chart based on selected features and date range
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('brand-dropdown', 'value'),
     Input('model-dropdown', 'value'),
     Input('fact-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('source-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_bar_chart(selected_brands, selected_models, selected_facts, selected_countries, selected_sources, start_date, end_date):
    if not all([selected_brands, selected_models, selected_facts, selected_countries, selected_sources]):
        return go.Figure()
    elif not start_date or not end_date:
        return go.Figure()
    else:
        # Handle "All" selections
        if 'All' in selected_brands:
            selected_brands = df['brand'].unique()
        if 'All' in selected_models:
            selected_models = df['model'].unique()
        if 'All' in selected_facts:
            selected_facts = df['fact'].unique()
        if 'All' in selected_countries:
            selected_countries = df['country'].unique()
        if 'All' in selected_sources:
            selected_sources = df['source'].unique()
        
        from_date = pd.to_datetime(start_date, format='%Y-%m-%d', errors='coerce')
        to_date = pd.to_datetime(end_date, format='%Y-%m-%d', errors='coerce')
        if pd.isnull(from_date) or pd.isnull(to_date) or from_date > to_date:
            return go.Figure()

        filtered_df = df[(df['model'].isin(selected_models)) & 
                         (df['fact'].isin(selected_facts)) & 
                         (df['country'].isin(selected_countries)) & 
                         (df['source'].isin(selected_sources)) & 
                         (pd.to_datetime(df['date'], errors='coerce').between(from_date, to_date))]

        all_features = pd.DataFrame({'Feature': df['Feature'].unique()})
        feature_counts = all_features.merge(filtered_df.groupby('Feature').size().reset_index(name='count'), 
                                            on='Feature', how='left').fillna(0)
        colors = [feature_colors.get(feature, '#{:06x}'.format(random.randint(0, 256**3-1))) for feature in feature_counts['Feature']]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=feature_counts['Feature'], y=feature_counts['count'], marker_color=colors))

        # Increase the size of the bar chart and straighten text
        fig.update_layout(
            xaxis=dict(title='Feature', tickangle=0),  # Straighten the text below the bars
            yaxis=dict(title='Count'),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            clickmode='event+select',
            height=650,  # Increase the height of the chart
            width=1500   # Increase the width of the chart
        )
        
        return fig


# Handle bar chart click event and redirect
@app.callback(
    Output('url', 'pathname'),
    [Input('bar-chart', 'clickData')],
    [State('brand-dropdown', 'value'),
     State('model-dropdown', 'value'),
     State('fact-dropdown', 'value'),
     State('country-dropdown', 'value'),
     State('source-dropdown', 'value'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date')]
)
def redirect_on_click(clickData, selected_brands, selected_models, selected_facts, selected_countries, selected_sources, start_date, end_date):
    if clickData:
        feature = clickData['points'][0]['x']
        start_date = start_date if start_date else 'None'
        end_date = end_date if end_date else 'None'
        return f'/feedback/{feature}/{start_date}/{end_date}'
    return dash.no_update

# Update page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return main_layout
    elif pathname.startswith('/feedback/'):
        parts = pathname.split('/')
        if len(parts) == 5:
            feature, start_date, end_date = parts[2], parts[3], parts[4]
            filtered_feedbacks = df[(df['Feature'] == feature) & 
                                    (df['model'].isin(df['model'])) & 
                                    (df['fact'].isin(df['fact'])) & 
                                    (df['country'].isin(df['country'])) & 
                                    (df['source'].isin(df['source'])) & 
                                    (pd.to_datetime(df['date'], format='%d-%m-%Y').between(pd.to_datetime(start_date, format='%Y-%m-%d', errors='coerce'), pd.to_datetime(end_date, format='%Y-%m-%d', errors='coerce')))]

            # Filter only necessary columns
            filtered_feedbacks = filtered_feedbacks[[ 'model', 'feedback']]
            
            # Display only top 10 rows
            top_feedbacks = filtered_feedbacks.head(10)

            # Define table styles
            table_style = {
                'width': '100%',
                'borderCollapse': 'collapse',
                'margin': '20px 0',
                'fontSize': '20px',
                'textAlign': 'left'
            }
            th_style = {
                'backgroundColor': '#f4f4f4',
                'padding': '10px',
                'borderBottom': '2px solid #ddd',
                'borderTop': '1px solid #ddd'
            }
            td_style = {
                'padding': '10px',
                'borderBottom': '1px solid #ddd',
                'borderTop': '1px solid #ddd'
            }

            # Create table headers
            table_header = [html.Th(col, style=th_style) for col in top_feedbacks.columns]
            
            # Create table rows
            table_rows = [
                html.Tr([
                    html.Td(top_feedbacks.iloc[i][col], style=td_style) for col in top_feedbacks.columns
                ]) for i in range(len(top_feedbacks))
            ]

            return html.Div([
                html.H1(f'Feedback for Feature: {feature}'),
                html.Table([
                    html.Thead(html.Tr(table_header)),
                    html.Tbody(table_rows)
                ], style=table_style)
            ])
    return 'Welcome! Click on a bar to see feedback.'

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8058))
    app.run_server(host='0.0.0.0', port=port, debug=False)