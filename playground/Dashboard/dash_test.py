import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output, State

# Load data
df = pd.read_pickle("all_tickers_last_decade_features.pkl")

# call Dash object/app
app = dash.Dash()

# layout = html to be shown
app.layout = html.Div([

    html.H1('Stocks'),
    html.Label('Elegir especie:'),

    # dropdown with ID 
    dcc.Dropdown(id='ticker_dropdown', 
        # pass a list of ticker dicts
        options=[{'label': item, 'value': item} for item in df['Ticker'].unique()],
        # selection of multiple tickers possible
        multi=True, 
        value=[df['Ticker'].sort_values()[0]]),
    
    # graph
    html.Label('Gráfico'),
    html.Div(
        # dcc.Graph doesn't receive 'figure' as argument since it is passed with the callback function
        dcc.Graph(id='stock_chart')),

    # table
    html.Label('Tabla'),
    dash_table.DataTable(id='table',
        columns=[
        {"name": i, "id": i} for i in df.loc[:,['Adj Close','Ticker']].columns],
        page_current=0,
        page_size=5,
        page_action='custom'),
    ])

# get value from dropdown and draw it on the figure of the stock chart
@app.callback(Output('stock_chart','figure'),
            [Input('ticker_dropdown','value')])
def update_figure(selected_tickers):
    "keep the figure (id=stock_chart) updated with the human selection (input=ticker_dropdown)"

    # empty list to be filled with the scatter/candlestick of each ticker
    data=[]

    # two iterations: a list of scatter objects before a list of candlestick object
    for ticker in selected_tickers:
        data.append(go.Scatter(x=df[df['Ticker'] == ticker].index,
                                 y=df[df['Ticker'] == ticker]['Close'],
                                 mode='lines',
                                 opacity=0.7,
                                 name=ticker,
                                 textposition='bottom center'))
        
    for ticker in selected_tickers:
        data.append(go.Candlestick(x=df[df['Ticker'] == ticker].index,
                            open=df[df['Ticker'] == ticker]['Open'],
                            high=df[df['Ticker'] == ticker]['High'],
                            low=df[df['Ticker'] == ticker]['Low'],
                            close=df[df['Ticker'] == ticker]['Close'],
                            visible=False,
                            showlegend=False))
    
    updatemenus = list([
        dict(
            buttons=list([
                dict(
                    args=[{'visible': [True, False]}],
                    label='Line',
                    method='update'
                ),
                dict(
                    args=[{'visible': [False, True]}],
                    label='Candle',
                    method='update'
                ),
            ]),
            direction='down',
            pad={'r': 10, 't': 10},
            showactive=True,
            x=0,
            xanchor='left',
            y=1.05,
            yanchor='top'
        ),
    ])

    layout = dict(
        updatemenus=updatemenus,
        autosize=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )

    # data must be a list of objects and not a list of lists
    return {
        "data": data,
        "layout": layout
    }

# gets the value from the dropdown and the pagination
@app.callback(Output('table', 'data'),
            [Input('ticker_dropdown', "value"),
            Input('table', "page_current"),
            Input('table', "page_size")])
def update_table(selected_tickers,page_current,page_size):
    "cuts the dataframe with the chosen tickers and showa only the rows which fits in the pagination"
    data = df.loc[df['Ticker'].isin(selected_tickers),['Adj Close','Ticker']]
    return data.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)