
# ======== IMPORTS ========
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np

# ======== CONFIGURATION ========
LIGHT_THEME = dbc.themes.BOOTSTRAP
DARK_THEME = dbc.themes.CYBORG
DEFAULT_THEME = 'dark'
DEFAULT_PORT = 8060

# ======== DATA LOADING ========
def load_data():
    """Load housing data."""
    df = pd.read_excel("HousePricePrediction.xlsx")
    # Remove Id column from the dataset
    if 'Id' in df.columns:
        df = df.drop('Id', axis=1)
    return df

df = load_data()

# ======== APP INITIALIZATION ========
app = dash.Dash(
    __name__, 
    use_pages=False,
    external_stylesheets=[DARK_THEME],
    suppress_callback_exceptions=True
)
app.title = 'Housing Price Analysis Dashboard'

# ======== HELPER FUNCTIONS ========
def get_template(theme):
    """Return appropriate plotly template based on theme."""
    return 'plotly_dark' if theme == 'dark' else 'plotly_white'

def create_filters(prefix=""):
    """Create reusable filter controls with optional ID prefix."""
    id_prefix = f"{prefix}-" if prefix else ""  # For unique component IDs
    
    return dbc.Row([
        # Zoning type filter (residential, commercial, etc.)
        dbc.Col([
            html.Label('MSZoning'),
            dcc.Dropdown(
                id=f'{id_prefix}zoning-filter',
                options=[{'label': zone, 'value': zone} for zone in df['MSZoning'].dropna().unique()],
                placeholder='Select zoning',
                clearable=True
            )
        ], width=6),
        # Building type filter (single family, duplex, etc.)
        dbc.Col([
            html.Label('BldgType'),
            dcc.Dropdown(
                id=f'{id_prefix}bldgtype-filter',
                options=[{'label': b, 'value': b} for b in df['BldgType'].dropna().unique()],
                placeholder='Select building type',
                clearable=True
            )
        ], width=6)
    ], className="mb-4")  # Bottom margin

def filter_dataframe(dataframe, zoning=None, bldgtype=None):
    """Filter dataframe based on zoning and building type selections."""
    filtered_df = dataframe.copy()  # Avoid modifying original
    
    if zoning:
        filtered_df = filtered_df[filtered_df['MSZoning'] == zoning]
    if bldgtype:
        filtered_df = filtered_df[filtered_df['BldgType'] == bldgtype]
        
    return filtered_df

# ======== VISUALIZATION FUNCTIONS ========
def create_correlation_heatmap(df, theme='dark'):
    """Create a correlation heatmap for numerical variables."""
    numeric_df = df.select_dtypes(include=['number'])
    numeric_df = numeric_df.dropna(axis=1, how='all')
    corr_matrix = numeric_df.corr()
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    masked_corr = corr_matrix.mask(mask)
    

    
    fig = px.imshow(
        masked_corr,
        
        text_auto='.2f',
        labels=dict(color="Correlation"),
        x=masked_corr.columns,
        y=masked_corr.columns,
        title='Feature Correlation Heatmap',
        template=get_template(theme),
        color_continuous_scale=px.colors.sequential.Plasma,
        
        zmin=-1,
        zmax=1
    )
    
    fig.update_layout(
        height=600,
        xaxis=dict(tickangle=45, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
        coloraxis_colorbar=dict(title="Correlation", thicknessmode="pixels", thickness=20)
    )
    
    return fig

def create_saleprice_correlation_chart(df, theme='dark'):
    """Create a horizontal bar chart showing correlations with SalePrice."""
    numeric_df = df.select_dtypes(include=['number'])
    correlations = numeric_df.corr()['SalePrice'].sort_values(ascending=False)
    correlations = correlations.drop('SalePrice', errors='ignore')
    
    top_correlations = pd.concat([
        correlations.head(10),
        correlations.tail(5)
    ])
    

    
    fig = px.bar(
        x=top_correlations.values,
        y=top_correlations.index,
        orientation='h',
        title='Top Correlations with Sale Price',
        template=get_template(theme),
        color=top_correlations.values,
        color_discrete_sequence=px.colors.sequential.Plasma,
        labels={'x': 'Correlation Coefficient', 'y': 'Feature'},
        range_color=[-1, 1]
    )
    
    fig.add_shape(
        type='line',
        x0=0, y0=-0.5,
        x1=0, y1=len(top_correlations)-0.5,
        line=dict(color='white' if theme == 'dark' else 'black', width=1, dash='dash')
    )
    
    fig.update_layout(
        height=600,
        coloraxis_showscale=False,
        yaxis=dict(title='', autorange="reversed"),
        xaxis=dict(title='Correlation with Sale Price', range=[-1, 1])
    )
    
    return fig

# ======== LAYOUT COMPONENTS ========
navbar = dbc.NavbarSimple(
    children=[
        # Navigation buttons
        dbc.NavItem(dcc.Link('Trends & Analysis', href='/', className="nav-link")),
        dbc.NavItem(dcc.Link('Market Overview', href='/insights', className="nav-link")),
        dbc.NavItem(dcc.Link('Data Table', href='/data', className="nav-link")),
        dbc.NavItem(dcc.Link('Insghts', href='/insghts', className="nav-link")),
        # Theme toggle
        dbc.Switch(id="theme-switch", label="Dark Mode", value=True, className="ms-3 text-white")
    ],
    brand="Housing Price Dashboard",
    brand_href="/",
    color="dark",
    dark=True
)

# ======== PAGE LAYOUTS ========
def dashboard1(theme):
    """Main dashboard with trend analysis charts."""
    return html.Div([
        create_filters(),
        
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='saleprice-distribution'), md=6),
                    dbc.Col(dcc.Graph(id='yearbuilt-saleprice'), md=6)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='condition-saleprice'), md=6),
                    dbc.Col(dcc.Graph(id='avg-basement-by-year'), md=6)
                ])
            ])
        ], className="mb-4", style={"backgroundColor": "#1e1e1e" if theme == 'dark' else 'white', 
                                   "borderRadius": "10px"})
    ])

def dashboard2(theme):
    """Market overview dashboard."""
    return html.Div([
        create_filters("insights"),
        
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='lotarea-saleprice'), md=6),
                    dbc.Col(dcc.Graph(id='yearremod-distribution'), md=6)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='mssubclass-saleprice'), md=6),
                    dbc.Col(dcc.Graph(id='lotconfig-saleprice'), md=6)
                ])
            ])
        ], style={"backgroundColor": "#1e1e1e" if theme == 'dark' else 'white', 
                 "borderRadius": "10px"})
    ])

def insghts(theme):
    """Insights page with correlation analyses."""
    text_color = 'white' if theme == 'dark' else 'black'
    
    return html.Div([
        create_filters("insghts"),
        
        # Correlation analysis card
        dbc.Card([
            dbc.CardHeader("Correlation Analysis"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5("Feature Correlation Matrix", className="text-center"),
                        dcc.Graph(id='insghts-correlation-heatmap')
                    ], md=6),
                    
                    dbc.Col([
                        html.H5("Features Most Correlated with Sale Price", className="text-center"),
                        dcc.Graph(id='insghts-correlation-chart')
                    ], md=6)
                ])
            ])
        ], style={"backgroundColor": "#1e1e1e" if theme == 'dark' else 'white', 
                 "borderRadius": "10px"}, className="mb-4"),
        
        # Dashboard descriptions
        dbc.Card([
            dbc.CardHeader("Dashboard Visualization Insights"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5("Sale Price Distribution", className="mt-2", style={"color": text_color}),
                        html.P([
                            "• The price distribution likely shows a right-skewed pattern typical of housing prices", html.Br(),
                            "• There may be a few high-value outliers stretching the upper end of the distribution", html.Br(),
                            "• The median price is likely a better metric than mean due to skewness"
                        ], style={"color": text_color}),
                        
                        html.H5("Year Built vs Sale Price", className="mt-4", style={"color": text_color}),
                        html.P([
                            "• Newer homes generally command higher prices", html.Br(),
                            "• There may be certain \"vintage\" periods where homes retain special value", html.Br(),
                            "• The relationship is likely non-linear, with recent construction showing steeper price increases"
                        ], style={"color": text_color}),
                    ], md=4),
                    
                    dbc.Col([
                        html.H5("Sale Price by Overall Condition", className="mt-2", style={"color": text_color}),
                        html.P([
                            "• Higher condition ratings likely correlate with higher prices", html.Br(),
                            "• The spread (variability) of prices probably increases with better condition ratings", html.Br(),
                            "• Condition 5 (average) likely has the most observations"
                        ], style={"color": text_color}),
                        
                        html.H5("Average Basement Area by Year Built", className="mt-4", style={"color": text_color}),
                        html.P([
                            "• Basement sizes have likely changed over time, reflecting changing construction trends", html.Br(),
                            "• Older homes may have smaller or larger basements depending on the region and era", html.Br(),
                            "• There may be noticeable \"jumps\" in basement sizes corresponding to significant changes in building codes or preferences"
                        ], style={"color": text_color})
                    ], md=4),
                    
                    dbc.Col([
                        html.H5("Lot Area vs Sale Price", className="mt-2", style={"color": text_color}),
                        html.P([
                            "• Larger lots generally command higher prices, but with diminishing returns", html.Br(),
                            "• Different zoning types show different price-to-lot-size relationships", html.Br(),
                            "• Some zones may show stronger correlation between lot size and price than others"
                        ], style={"color": text_color}),
                        
                        html.H5("Building Type Analysis", className="mt-4", style={"color": text_color}),
                        html.P([
                            "• Single-family detached homes likely command the highest average prices", html.Br(),
                            "• Townhomes and condos may show better price efficiency (price per square foot)", html.Br(),
                            "• Certain building types may be concentrated in specific neighborhoods or zoning areas"
                        ], style={"color": text_color})
                    ], md=4)
                ])
            ])
        ], style={"backgroundColor": "#1e1e1e" if theme == 'dark' else 'white', 
                 "borderRadius": "10px"}, className="mb-4")
    ])

def layout_table(theme):
    """Data table page showing raw data."""
    # Style based on current theme
    style = {
        'backgroundColor': '#1e1e1e' if theme == 'dark' else 'white',
        'color': 'white' if theme == 'dark' else 'black'
    }

    return html.Div([
        html.H4("Housing Data Table", style={'textAlign': 'center', **style}),
        # Interactive data table with pagination
        dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=10,  # Records per page
            style_table={'overflowX': 'auto'},  # Horizontal scroll
            style_header={
                'backgroundColor': '#111111' if theme == 'dark' else '#e1e1e1',
                'fontWeight': 'bold',
                'color': style['color']
            },
            style_data={
                'backgroundColor': style['backgroundColor'], 
                'color': style['color']
            }
        )
    ])

# Main application layout
app.layout = html.Div([
    dcc.Location(id='url'),  # For URL routing
    dcc.Store(id='theme-store', data=DEFAULT_THEME),  # Theme state storage
    navbar,  # Top navigation bar
    html.Div(id='page-content', className="container-fluid p-4")  # Content container
])

# ======== CALLBACKS ========
# Theme toggle callback
@app.callback(
    Output('theme-store', 'data'),
    Input('theme-switch', 'value')
)
def toggle_theme(value):
    """Toggle between light and dark theme."""
    return 'dark' if value else 'light'

# Routing callback
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),  # URL determines which page to show
    State('theme-store', 'data')  # Current theme to apply
)
def display_page(pathname, theme):
    """Route to the appropriate page based on URL pathname."""
    if pathname == '/data':
        return layout_table(theme)
    elif pathname == '/insights':
        return dashboard2(theme)
    elif pathname == '/insghts':
        return insghts(theme)
    return dashboard1(theme)  # Default to main dashboard

# ======== VISUALIZATION CALLBACKS ========
# Dashboard2 correlation charts callback
@app.callback(
    Output('correlation-heatmap', 'figure'),
    Output('saleprice-correlation-chart', 'figure'),
    Input('insights-zoning-filter', 'value'),
    Input('insights-bldgtype-filter', 'value'),
    State('theme-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_correlation_charts(zoning, bldgtype, theme):
    """Update correlation charts for dashboard2."""
    filtered_df = filter_dataframe(df, zoning, bldgtype)  # Apply filters
    heatmap_fig = create_correlation_heatmap(filtered_df, theme)
    barchart_fig = create_saleprice_correlation_chart(filtered_df, theme)
    return heatmap_fig, barchart_fig

# Insghts page correlation charts callback
@app.callback(
    Output('insghts-correlation-heatmap', 'figure'),
    Output('insghts-correlation-chart', 'figure'),
    Input('insghts-zoning-filter', 'value'),
    Input('insghts-bldgtype-filter', 'value'),
    State('theme-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_insghts_correlation_charts(zoning, bldgtype, theme):
    """Update correlation charts for insghts page."""
    filtered_df = filter_dataframe(df, zoning, bldgtype)  # Apply filters
    heatmap_fig = create_correlation_heatmap(filtered_df, theme)
    barchart_fig = create_saleprice_correlation_chart(filtered_df, theme)
    return heatmap_fig, barchart_fig

# Dashboard1 main graphs callback
@app.callback(
    Output('saleprice-distribution', 'figure'),
    Output('yearbuilt-saleprice', 'figure'),
    Output('condition-saleprice', 'figure'),
    Output('avg-basement-by-year', 'figure'),
    Input('zoning-filter', 'value'),
    Input('bldgtype-filter', 'value'),
    State('theme-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_graphs(zoning, bldgtype, theme):
    """Update main dashboard1 graphs."""
    filtered_df = filter_dataframe(df, zoning, bldgtype)
    template = get_template(theme)

    # Sale Price distribution histogram
    fig1 = px.histogram(
        filtered_df, x='SalePrice', nbins=50,
        title='Distribution of Sale Prices', template=template,
        color='MSZoning',  # Color by zoning type
        color_discrete_sequence=px.colors.sequential.Plasma_r,
    )
      # Year Built vs Sale Price scatter plot
    fig2 = px.scatter(
        filtered_df, x='YearBuilt', y='SalePrice',
        title='Year Built vs Sale Price', template=template,
        color='MSZoning',  # Color by zoning type
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        hover_data=['OverallCond'],  # Extra info on hover
    )

    # Box plot showing sale price by overall condition
    fig3 = px.box(
        filtered_df, x='OverallCond', y='SalePrice', color='OverallCond',
        title='Sale Price by Overall Condition', template=template,
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )
    
    # Line chart of average basement size by year built
    fig4 = px.line(
        filtered_df.groupby('YearBuilt')['TotalBsmtSF'].mean().reset_index(),
        x='YearBuilt', y='TotalBsmtSF',
        title='Average Basement Area by Year Built', template=template,
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )

    return fig1, fig2, fig3, fig4

# Dashboard2 additional graphs callback
@app.callback(
    Output('lotarea-saleprice', 'figure'),
    Output('yearremod-distribution', 'figure'),
    Output('mssubclass-saleprice', 'figure'),
    Output('lotconfig-saleprice', 'figure'),
    Input('insights-zoning-filter', 'value'),
    Input('insights-bldgtype-filter', 'value'),
    State('theme-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def update_additional_graphs(zoning, bldgtype, theme):
    """Update additional graphs for dashboard2."""
    filtered_df = filter_dataframe(df, zoning, bldgtype)  # Apply filters
    template = get_template(theme)    # LotArea vs SalePrice scatter plot
    fig5 = px.scatter(
        filtered_df, 
        x='LotArea',
        y='SalePrice',
        color='MSZoning',  # Color by zoning type
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        title='Lot Area vs Sale Price by Zoning', 
        template=template,
        hover_data=['YearBuilt'],  # Extra info on hover
        opacity=0.7  # Semi-transparent points
    )
    fig5.update_traces(marker={'size': 8})  # Adjust marker size
    fig5.update_layout(legend_title_text='Zoning Type')
    
    # Sale Prices histogram with box plot
    fig6 = px.histogram(
        filtered_df, 
        x='SalePrice',
        nbins=50,  # Number of bins
        marginal='box',  # Add box plot on side
        title='Sale Prices', 
        template=template,
        color='MSZoning',  # Color by zoning type
        color_discrete_sequence=px.colors.sequential.Plasma_r,
    )
    
    # Average Price by Building Type horizontal bar chart
    avg_price_by_bldg = filtered_df.groupby('BldgType')['SalePrice'].mean().sort_values().reset_index()
    fig7 = px.bar(
        avg_price_by_bldg, 
        x='SalePrice',  # Bar length = price
        y='BldgType',   # Categories on y-axis
        orientation='h',  # Horizontal bars
        title='Avg Price by Building Type', 
        template=template,
        text_auto=True,  # Show values on bars
        color='SalePrice',  # Color by price
        color_continuous_scale=px.colors.sequential.Plasma_r  # Color scale
    )
    
    # Building Type Share pie chart
    bldg_counts = filtered_df['BldgType'].value_counts().reset_index()
    bldg_counts.columns = ['BldgType', 'Count']
    fig8 = px.pie(
        bldg_counts, 
        names='BldgType',  # Categories
        values='Count',    # Slice size
        hole=0.6,          # Donut chart
        color='BldgType',  # Color by type
        color_discrete_sequence=px.colors.sequential.Plasma_r,  # Color palette
        title='Building Type Share', 
        template=template
    )

    return fig5, fig6, fig7, fig8

# ======== APP ENTRY POINT ========
if __name__ == '__main__':

    app.run(debug=True, port=DEFAULT_PORT)  # Run app in debug mode
