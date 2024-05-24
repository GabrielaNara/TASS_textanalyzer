import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import io
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import re  

# Variável global para armazenar os dados do arquivo CSV
data = None
#tokens_text = None
tokens_text = "" 

def clean_text(text):
    stopwords_list = ['a', 'à', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'às', 'até', 'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'depois', 'do', 'dos', 'e', 'é', 'ela', 'elas', 'ele', 'eles', 'em', 'entre', 'era', 'eram', 'éramos', 'essa', 'essas', 'esse', 'esses', 'esta', 'está', 'estamos', 'estão', 'estar', 'estas', 'estava', 'estavam', 'estávamos', 'este', 'esteja', 'estejam', 'estejamos', 'estes', 'esteve', 'estive', 'estivemos', 'estiver', 'estivera', 'estiveram', 'estivéramos', 'estiverem', 'estivermos', 'estivesse', 'estivessem', 'estivéssemos', 'estou', 'eu', 'foi', 'fomos', 'for', 'fora', 'foram', 'fôramos', 'forem', 'formos', 'fosse', 'fossem', 'fôssemos', 'fui', 'há', 'haja', 'hajam', 'hajamos', 'hão', 'havemos', 'haver', 'hei', 'houve', 'houvemos', 'houver', 'houvera', 'houverá', 'houveram', 'houvéramos', 'houverão', 'houverei', 'houverem', 'houveremos', 'houveria', 'houveriam', 'houveríamos', 'houvermos', 'houvesse', 'houvessem', 'houvéssemos', 'isso', 'isto', 'já', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus', 'minha', 'minhas', 'muito', 'na', 'não', 'nas', 'nem', 'no', 'nos', 'nós', 'nossa', 'nossas', 'nosso', 'nossos', 'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por', 'qual', 'quando', 'que', 'quem', 'são', 'se', 'seja', 'sejam', 'sejamos', 'sem', 'ser', 'será', 'serão', 'serei', 'seremos', 'seria', 'seriam', 'seríamos', 'seu', 'seus', 'só', 'somos', 'sou', 'sua', 'suas', 'também', 'te', 'tem', 'tém', 'temos', 'tenha', 'tenham', 'tenhamos', 'tenho', 'terá', 'terão', 'terei', 'teremos', 'teria', 'teriam', 'teríamos', 'teu', 'teus', 'teve', 'tinha', 'tinham', 'tínhamos', 'tive', 'tivemos', 'tiver', 'tivera', 'tiveram', 'tivéramos', 'tiverem', 'tivermos', 'tivesse', 'tivessem', 'tivéssemos', 'tu', 'tua', 'tuas', 'um', 'uma', 'você', 'vocês', 'vos', "'", 'pra', 'eh', 'vcs', 'lá', 'né', 'q', 'o', 'tá', 'co', 't', 's', 'rt', 'pq', 'ta', 'tô', 'ihh', 'ih', 'otc', 'vc', 'https', 'n', 'parque', 'praça', 'local', 'lugar', 'ponto', 'pois', 'porque']
    letters = re.findall(r'\b[A-zÀ-úü]+\b', text.lower())
    filtered_words = [word for word in letters if word not in stopwords_list]
    
    return filtered_words

# Função para gerar uma nuvem de palavras fictícia
def generate_dummy_wordcloud():
    # Texto fictício
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    # Gerar a nuvem de palavras
    wordcloud = WordCloud(width=400, height=200, background_color='white').generate(text)
    # Salvar a imagem como base64
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    return 'data:image/png;base64,' + base64.b64encode(img.getvalue()).decode()

# Criar o aplicativo Dash
app = dash.Dash(__name__)

# Layout do aplicativo
app.layout = html.Div(children=[
    # Importação da fonte DIN do Google Fonts
    html.Link(
        rel='stylesheet',
        href='https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap'
    ),
   html.Div(
        style={
            'backgroundImage': 'url("https://img.freepik.com/fotos-gratis/fundo-preto-abstrato-da-grade-digital_53876-97647.jpg")', 
            'backgroundRepeat': 'no-repeat',  # Não repetir a imagem de fundo
            'backgroundSize': 'cover',  # Cobrir todo o espaço disponível
            'height': 'auto',  # Altura automática para cobrir o conteúdo
            'minHeight': '100vh',  # Altura mínima de 100% da tela visível
            'fontFamily': 'Montserrat', 
            'color': 'white',
        },
        children=[  
            html.Div(children=[
                html.Div(style={'height': '50px'}), 
                html.H1(children='Text Analyzer by TASS', style={'margin': '20px auto','textAlign': 'center', 'fontSize': '48px'}), 
                html.Div(style={'height': '30px'}), 
                #---------------------------------------------------- PASSO 1-------------------------------------------------------------------------------------
                html.H1(children='Passo 1: Aplicando a Linguagem Natural', style={'margin': '20px auto','textAlign': 'center'}),
                html.H1(children='Como requisito o arquivo deve ter o formato .xlsx e 1 coluna chamada text'
                        , style={'margin': '10px auto','textAlign': 'center', 'fontSize': '20px','fontFamily': 'Roboto'}), 
                dcc.Upload(
                    id='upload-data',children=html.Div(['Arraste ou ', html.A('selecione um arquivo CSV')]),
                    style={'width': '90%', 'maxWidth': '300px', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                        'textAlign': 'center', 'margin': '20px auto'},
                    multiple=False # Permitir o upload de vários arquivos
                ),
                #---------------------------------------------------- VISUALIZAR PASSO 1-------------------------------------------------------------------------------------
                html.Div(id='output-upload', style={'display': 'none'}, children=[
                    html.H2(children='Pré-visualizar Lematização do texto', style={'margin': '10px auto','marginLeft': '250px','fontSize': '20px'}),
                    html.Div(id='output-data-upload', style={'margin': '10px auto','marginLeft': '250px','marginRight': '250px','padding': '20px', 'border': '1px solid #ccc'}),
                    html.Button("Download CSV", id="btn_csv", style={'margin': '10px auto', 'marginLeft': '250px','padding': '10px', 'border': '1px solid #ccc'}),
                    dcc.Download(id="download_csv"),
                    html.Img(id='wordcloud-image', style={'width': '50%', 'margin': 'auto', 'display': 'block'}),]),
                #---------------------------------------------------- VISUALIZAR PASSO 2-------------------------------------------------------------------------------------
                #html.Hr(),
                html.H1("Passo 2: Atualizar a nuvem de palavras por uma lista", style={'margin': '20px auto','textAlign': 'center'}), 
                dcc.Textarea(id='input-lista', placeholder='Insira sua lista de palavras aqui...', style={'width': '50%', 'height': '100px', 'margin': 'auto', 'display': 'block'}),
                html.Div(html.Button('Atualizar Nuvem', id='btn-atualizar-nuvem-lista', n_clicks=0, style={'margin': '15px', 'padding': '15px','fontSize': '15px', 'textAlign': 'center'}), style={'text-align': 'center'}),
                html.Div(id='wordcloud-image-lista', style={'width': '50%', 'margin': 'auto', 'display': 'none'}),  
                html.H1("Criado e atualizado por: TASSProject. Mais informações em: https://github.com/GabrielaNara/translating-soundscape-descriptors", style={'margin': '200px auto','textAlign': 'center', 'fontSize': '20px','fontFamily': 'Roboto'}), 
                #html.Hr()
            ])
        ]
    )
])

# Callback para carregar os dados do arquivo CSV
def load_data(contents):
    global data
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8')
    data = pd.read_csv(io.StringIO(decoded))

# Callback para carregar o arquivo e exibir o DataFrame
@app.callback([Output('output-data-upload', 'children'), Output('wordcloud-image', 'src')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(contents, filename):
    global data  
    global tokens_text  

    if contents is not None:
        # Ler o conteúdo do arquivo
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Carregar os dados e organizando o dataframe
        data = pd.read_excel(io.BytesIO(decoded))
        # Criando a coluna tokens 
        strg = []
        for i in data['text']:
            words = clean_text(i)
            strg += [", ".join(words)]
        data['tokens'] = strg
        data = data[['text', 'tokens']]

        # Gerar a nuvem de palavras
        tokens_text = ' '.join(data['tokens'])
        wordcloud = WordCloud(width=600, height=300, background_color='white').generate(tokens_text)
        img = io.BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img.seek(0)
        
        # Exibir as 2 primeiras linhas do DataFrame em uma tabela HTML dentro de um quadro
        table_output = html.Div([
            html.H3('2 primeiras linhas do arquivo de saída:'),
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in data.columns],
                data=data.to_dict('records')[:2],
                style_table={'width': '100%', 'maxWidth': '1500px', 'margin': 'auto'},  
                style_cell={'textOverflow': 'ellipsis', 'textAlign': 'left', 'color': 'black'},
                style_data={'whiteSpace': 'normal', 'height': 'auto'}
            )
        ])
        
        # Retornar a exibição do DataFrame e a nuvem de palavras
        return table_output, 'data:image/png;base64,' + base64.b64encode(img.getvalue()).decode()
    else:
        return None, None

# Callback para mostrar a parte do layout após o upload do arquivo
@app.callback(
    Output('output-upload', 'style'),
    [Input('upload-data', 'contents')]
)
def show_upload_output(contents):
    if contents is not None:
        return {'display': 'block'}
    else:
        return {'display': 'none'}
    
# Callback para fazer download do arquivo CSV modificado
@app.callback(
    Output("download_csv", "data"),
    [Input("btn_csv", "n_clicks")]
)
def download_csv(n_clicks):
    global data  # Use a variável global 'data'
    if n_clicks is not None and data is not None:
        # Crie um buffer de memória para armazenar o CSV
        buffer = io.StringIO()
        # Salve o DataFrame no buffer como um arquivo CSV
        data.to_csv(buffer, index=False, encoding="utf-8", sep=";")
        # Volte para o início do buffer
        buffer.seek(0)
        # Retorne o arquivo CSV como uma resposta para download
        return dict(content=buffer.getvalue(), filename="tabela.csv")

# Rota para baixar o arquivo CSV
@app.server.route("/download_csv")
def download_csv_route():
    # Chame a função de callback para obter os dados do CSV
    csv_data = download_csv(1)["content"]
    return flask.send_file(
        io.BytesIO(csv_data.encode("utf-8")),
        mimetype="text/csv",
        attachment_filename="tabela.csv",
        as_attachment=True
    )

# MOSTRAR A NUVEM GERAL APENAS SE O CSV É INSERIDO
@app.callback(Output('wordcloud-image', 'style'),
              [Input('upload-data', 'contents')])
def update_image_style(contents):
    if contents is None:
        return {'display': 'none'}  # Ocultar a imagem
    else:
        return {'width': '50%', 'margin': 'auto', 'display': 'block'}  # Mostrar a imagem

# Callback para atualizar a nuvem de palavras por uma lista
@app.callback(Output('wordcloud-image-lista', 'children'), 
              [Input('btn-atualizar-nuvem-lista', 'n_clicks')],
              [State('input-lista', 'value')])
def update_wordcloud_by_list(n_clicks, lista):
    global tokens_text  

    if tokens_text and n_clicks > 0 and lista:
        # Obter palavras da lista e filtrar texto
        words = clean_text(lista)
        filtered_text = ' '.join([word for word in clean_text(tokens_text) if word in words])

        # Contagem das palavras no texto filtrado
        word_counts = Counter(filtered_text.split())
        top_10_words = word_counts.most_common(10)
        top_words_list = [html.Li(f"{word}: {count} vezes", style={'color': 'white'}) for word, count in top_10_words]
        
        # Construção da tabela com as 10 palavras mais frequentes
        table_frequencia = html.Div([
            html.H3('10 palavras mais frequentes:'),
            html.Ul(top_words_list)
        ])

        # Criar a nuvem de palavras com base no texto filtrado
        wordcloud = WordCloud(width=600, height=300, background_color='white').generate(filtered_text)
        img = io.BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img.seek(0)
        wordcloud_image = html.Img(src='data:image/png;base64,' + base64.b64encode(img.getvalue()).decode(), style={'width': '100%', 'margin': 'auto', 'display': 'block'})
        
        return [wordcloud_image,table_frequencia ]
    else:
        # Se nenhum clique ou lista vazia, retornar a nuvem de palavras fictícia
        return generate_dummy_wordcloud()

# MOSTRAR A NUVEM FILTRADA APENAS SE O BOTÃO DA LISTA É CLICADO
@app.callback(Output('wordcloud-image-lista', 'style'),
              [Input('btn-atualizar-nuvem-lista', 'n_clicks')])
def update_image_style(n_clicks):
    if n_clicks > 0:
        return {'width': '50%', 'margin': 'auto', 'display': 'block'}  # Mostrar a imagem
    else:
        return {'display': 'none'}  # Ocultar a imagem

# Executar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
