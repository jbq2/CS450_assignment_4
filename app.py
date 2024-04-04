from dash import Dash, html, dcc, Output, Input, dash_table
import pandas as pd
import plotly.express as px

DATASET_PATH = './datasets/ProcessedTweets.csv'
DEFAULT_SLIDER_STEP = 0.1

app = Dash(__name__)
application = app.server

df = pd.read_csv(DATASET_PATH)
print(df['Month'].unique())

month_dropdown_options = df['Month'].unique()
month_dropdown = dcc.Dropdown(
    id='month_dropdown',
    options=month_dropdown_options,
    value=None
)

sentiment_rs_min = df['Sentiment'].min()
sentiment_rs_max = df['Sentiment'].max()
sentiment_rs = dcc.RangeSlider(
    id='sentiment_rs',
    min=sentiment_rs_min,
    max=sentiment_rs_max,
    step=None,
    value=[sentiment_rs_min, sentiment_rs_max]
)

subjectivity_rs_min = df['Subjectivity'].min()
subjectivity_rs_max = df['Subjectivity'].max()
subjectivity_rs = dcc.RangeSlider(
    id='subjectivity_rs',
    min=subjectivity_rs_min,
    max=subjectivity_rs_max,
    step=None,
    value=[subjectivity_rs_min, subjectivity_rs_max]
)

graph = dcc.Graph(
    id='graph',
    figure=px.scatter(data_frame=df, x='Dimension 1', y='Dimension 2')
)

table = dash_table.DataTable(
    id='table',
    columns=[{'name': 'Selected Tweets', 'id': 'RawTweet'}],
    data=[{'RawTweet': e['RawTweet']} for e in df.to_dict('records')],
    style_cell={'whiteSpace': 'normal', 'textAlign': 'center'},
    page_size=30
)

app.layout = html.Div(
    children=[
        html.Div(
            id='ctrl_panel',
            children=[
                html.Div(children=[html.Label(children=['Select Month:']), month_dropdown], style=dict(width='100%')),
                html.Div(children=[html.Label(children=['Select Sentiment Range:']), sentiment_rs], style=dict(width='100%')),
                html.Div(children=[html.Label(children=['Select Subjectivity Range:']), subjectivity_rs], style=dict(width='100%'))
            ]
        ),
        graph,
        table
    ]
)

@app.callback(
        Output('graph', 'figure'),
        [
            Input('month_dropdown', 'value'),
            Input('sentiment_rs', 'value'),
            Input('subjectivity_rs', 'value'),
        ]
)
def on_filter_changes(dropown_val, sent_rs_range, subj_rs_range):
    fdf = df
    sent_min = sent_rs_range[0]
    sent_max = sent_rs_range[1]
    subj_min = subj_rs_range[0]
    subj_max = subj_rs_range[1]
    if dropown_val:
        fdf = fdf[fdf['Month'] == dropown_val]
    fdf = fdf[(fdf['Sentiment'] >= sent_min) & (fdf['Sentiment'] <= sent_max)]
    fdf = fdf[(fdf['Subjectivity'] >= subj_min) & (fdf['Subjectivity'] <= subj_max)]
    return px.scatter(data_frame=fdf, x='Dimension 1', y='Dimension 2')

@app.callback(
        [
            Output('sentiment_rs', 'min'),
            Output('sentiment_rs', 'max'),
            Output('sentiment_rs', 'value'),
            Output('subjectivity_rs', 'min'),
            Output('subjectivity_rs', 'max'),
            Output('subjectivity_rs', 'value')
        ],
        Input('month_dropdown', 'value')
)
def on_dropdown_change(value):
    fdf = df
    if value:
        fdf = fdf[fdf['Month'] == value]
    sent_min = fdf['Sentiment'].min()
    sent_max = fdf['Sentiment'].max()
    subj_min = fdf['Subjectivity'].min()
    subj_max = fdf['Subjectivity'].max()
    return sent_min, sent_max, [sent_min, sent_max], subj_min, subj_max, [subj_min, subj_max]

@app.callback(
        Output('table', 'data'),
        Input('graph', 'selectedData')
)
def on_lasso_select(selected_data):
    if selected_data is not None:
        indices = [point['pointIndex'] for point in selected_data['points']]
        selected_df = df.iloc[indices]
        return [{'RawTweet': e['RawTweet']} for e in selected_df.to_dict('records')]
    return []