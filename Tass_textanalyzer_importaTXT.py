import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import base64
import io
from wordcloud import WordCloud
from collections import Counter
import spacy
import spacy.cli

def load_spacy_model(model_name="pt_core_news_sm"):
    try:
        return spacy.load(model_name, exclude=["ner", "parser", "attribute_ruler", "tagger"])
    except OSError:
        spacy.cli.download(model_name)
        return spacy.load(model_name, exclude=["ner", "parser", "attribute_ruler", "tagger"])

# Carregar o modelo SpaCy uma vez
nlp = load_spacy_model()

# Variável global para armazenar os dados do arquivo CSV
tokens_list = ""

# Estilos utilizados
page_style = {'backgroundImage': 'url("https://img.freepik.com/fotos-gratis/fundo-preto-abstrato-da-grade-digital_53876-97647.jpg")', 
            'backgroundRepeat': 'no-repeat',  # Não repetir a imagem de fundo
            'backgroundSize': 'cover',  # Cobrir todo o espaço disponível
            'height': 'auto',  # Altura automática para cobrir o conteúdo
            'minHeight': '100vh',  # Altura mínima de 100% da tela visível
            'fontFamily': 'Montserrat', 
            'color': 'white'}
text_style = {'margin': '10px auto','textAlign': 'center', 'fontSize': '20px','fontFamily': 'Roboto','whiteSpace': 'pre-wrap','width': '80%','color': '#A9A9A9'}

stopwords_set = {'a', 'à', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aquele#s', 'aquilo', 'as', 'às', 'até', 'com', 
'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'depois', 'do', 'dos', 'e', 'é', 'ela', 'elas', 'ele', 
'eles', 'em', 'entre', 'eu', 'isso', 'isto', 'já', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus', 'minha', 'minhas', 'muito', 'na', 'não', 'nas', 'nem', 
'no', 'nos', 'nós', 'nossa', 'nossas', 'nosso', 'nossos', 'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 
'pelo', 'pelos', 'por', 'qual', 'quando', 'que', 'quem', 'são', 'se', 'seja', 'sem', 'seu', 'seus', 'só', 'somos', 'sou', 'sua', 'suas', 
'também', 'te', 'tem', 'tém', 'teu', 'teus',  'tu', 'tua', 'tuas', 'um', 'uma', 'você', 'vocês', 'vos', "'", 'pra', 'eh', 'vcs', 'lá', 'né', 'q', 'o', 'tá', 'co', 't', 's', 'rt', 'pq', 
'ta', 'tô', 'ihh', 'ih', 'otc', 'vc', 'https', 'n', 'pois', 'porque',"b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"}

def clean_text(text):
    doc = nlp(text.lower())
    filtered_words = []
    for token in doc:
        if token.is_alpha and token.text.lower() not in stopwords_set:
            if token.pos_ in ['ADJ', 'NOUN']:  # Lematizar apenas adjetivos e substantivos
                filtered_words.append(token.lemma_)
            else:
                filtered_words.append(token.text)  # Repetir a palavra para outras POS
    return ' '.join(filtered_words)

def clean_text_2(text):
    words = text.lower().split()
    filtered_words = [word for word in words if word not in stopwords_set]
    
    return ' '.join(filtered_words)

# Criar o aplicativo Dash
app = dash.Dash(__name__)
server = app.server

# Layout do aplicativo
app.layout = html.Div(children=[
    # Importação da fonte DIN do Google Fonts
    html.Link(
        rel='stylesheet',
        href='https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap'
    ),
   html.Div(
        style=page_style,
        children=[  
            html.Div(children=[
                html.Div(style={'height': '50px'}), 
                html.H1(children='TASS Analyzer', style={'margin': '20px auto','textAlign': 'center', 'fontSize': '48px'}), 
                html.Div(style={'height': '30px'}), 
                #---------------------------------------------------- PASSO 1-------------------------------------------------------------------------------------
                html.H1(children='Passo 1: Processamento de Linguagem Natural', style={'margin': '20px auto','textAlign': 'center'}),
                html.H1(children='Requisito: O arquivo deve ter o formato .TXT', style=text_style), 
                html.H1(children='O texto passará pelo processo de lematização, onde cada palavra é reduzida a sua forma básica do dicionário, chamada de Lema. A operação é realizada de acordo com o modelo para a língua portuguesa da bilbioteca Spacy do Python. Os verbos são convertidos ao infinitivo, os substantivos ao singular e os adjetivos ao masculino singular. Quando finalizado, você poderá visualizar a lematização em algumas palavras do texto, visualizar a nuvem de palavras e baixar o arquivo lematizado em formato .txt. ', 
                        style=text_style),
                html.H1(children='Exemplo: Gatos --> gato, gata --> gato, lojão --> loja, ladrão --> ladrão, gatinhos --> gatinho, golfinho --> golfinho', 
                        style={**text_style, 'margin-bottom': '30px'}),  
                html.H1(children='O processo de lematização pode demorar a depender do tamanho da base de dados. Nesses casos, recomenda-se uma filtragem simples por Tokenização, onde são eliminados caracteres e palavras sem significância, como "a", "ao", "vc". Escolha entre as 2 opções abaixo:', 
                        style=text_style),
                html.Div(style={'display': 'flex','justifyContent': 'center','alignItems': 'center' },
                        children=[dcc.RadioItems(id='cleaning-function',options=[
                                    {'label': 'Tokenização (processo simples)', 'value': 'clean_text_2'},
                                    {'label': 'Lematização (processo completo)', 'value': 'clean_text'}],
                                value='clean_text_2',  # default value
                                labelStyle={'display': 'block', 'margin': '10px auto', 'fontSize': '20px'})]),                    
                dcc.Upload(
                    id='upload-data',children=html.Div(['Arraste ou ', html.A('selecione um arquivo .TXT')]),
                    style={'width': '90%', 'maxWidth': '320px', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                        'textAlign': 'center', 'margin': '15px auto'},
                    multiple=False 
                ),
                #---------------------------------------------------- VISUALIZAR PASSO 1-------------------------------------------------------------------------------------
                html.Div(id='output-upload', style={'display': 'none'}, children=[
                    html.H2(children='Pré-visualizar Lematização do texto', style={'margin': '10px auto','marginLeft': '250px','fontSize': '20px'}),
                    html.Div(id='output-data-upload', style={'margin': '10px auto','marginLeft': '250px','marginRight': '250px','padding': '20px', 'border': '1px solid #ccc'}),
                    html.Button("Download TXT Lematizado", id="btn_txt", style={'margin': '10px auto', 'marginLeft': '250px','padding': '10px', 'border': '1px solid #ccc'}),
                    dcc.Download(id="download_txt"),
                    html.Img(id='wordcloud-image', style={'width': '50%', 'margin': 'auto', 'display': 'block'}),]),
                #---------------------------------------------------- VISUALIZAR PASSO 2-------------------------------------------------------------------------------------
                html.H1("Passo 2: Filtrando a nuvem de palavras", style={'margin': '100px auto 20px','textAlign': 'center'}), 
                html.H1(children='Requisito: Finalize a etapa 1', style=text_style), 
                html.H1('Você pode melhorar a visualização da nuvem de palavras ao filtrar somente palavras específicas. Para isso, adicione palavras separadas por vírgula na caixa de texto abaixo. Por exemplo, você pode utilizar Adjetivos e Advérbios de caráter positivo ou negativo que expressam a análise ou satisfação das pessoas. Ao clicar no botão Atualizar Nuvem, ficará visível uma nova nuvem de palavras filtrada, e abaixo da nuvem a quantidade de vezes que as 10 palavras mais frequentes apareceram no texto.',
                    style=text_style),
                html.H1('Exemplo: quente, frio, bom, ruim, agradável, amigável, excelente, péssimo',
                    style={**text_style, **{'margin-bottom': '30px'}}),  
                dcc.Textarea(id='input-lista', placeholder='Insira sua lista de palavras aqui...', style={'width': '50%', 'height': '100px', 'margin': 'auto', 'display': 'block'}),
                html.Div(html.Button('Atualizar Nuvem', id='btn-atualizar-nuvem-lista', n_clicks=0, style={'margin': '30px', 'padding': '15px','fontSize': '15px', 'textAlign': 'center'}), style={'text-align': 'center'}),
                html.Div(id='wordcloud-image-lista', style={'width': '50%', 'margin': 'auto', 'display': 'none'}),  
                html.H1("O TASS Analyzer é uma iniciativa acadêmica para processamento rápido de textos na língua portuguesa.Para mais informações, ou em caso de dúvidas e sugestões, acesse: https://github.com/GabrielaNara/TASS_textanalyzer", 
                        style={'margin': '200px auto', 'textAlign': 'center', 'fontSize': '25px','fontFamily': 'Roboto'}), 
                html.Hr()
            ])
        ]
    )
])

# Callback para carregar os dados do arquivo CSV e exibir o DataFrame
@app.callback([Output('output-data-upload', 'children'), Output('wordcloud-image', 'src')],
              [Input('upload-data', 'contents'), Input('cleaning-function', 'value')],
              [State('upload-data', 'filename')])
def update_output(contents, selected_cleaning_function, filename):
    global tokens_list

    if contents is not None:
        try:
            # Decodificar o conteúdo do arquivo TXT
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')

            # Verificar se há conteúdo válido no arquivo
            if len(decoded.strip()) == 0:
                return html.Div([
                    html.H3('Erro: Arquivo vazio.'),
                    html.P('O arquivo carregado não contém texto válido para processamento.')
                ]), None
            
            # Selecionar a função de limpeza com base na escolha do usuário
            if selected_cleaning_function == 'clean_text':
                cleaning_function = clean_text
            else:
                cleaning_function = clean_text_2

            # Aplicar a função de limpeza selecionada ao conteúdo do arquivo
            tokens_list = [cleaning_function(line.strip()) for line in decoded.splitlines() if line.strip()]

            # Aplicar a função clean_text ao conteúdo do arquivo
            # tokens_list = [clean_text(line.strip()) for line in decoded.splitlines() if line.strip()]

            # Verificar se há tokens após o processamento
            if not tokens_list or all(len(token) == 0 for token in tokens_list):
                return html.Div([
                    html.H3('Não há palavras suficientes para gerar uma nuvem de palavras.'),
                    html.P('Verifique o conteúdo do arquivo e tente novamente.')
                ]), None
            
            # Gerar a nuvem de palavras
            wordcloud = WordCloud(width=600, height=300, background_color='white').generate(' '.join(tokens_list))
            img = io.BytesIO()
            wordcloud.to_image().save(img, format='JPEG', quality=80)
            img.seek(0)
            
            # Exibir o processamento do texto
            table_output = html.Div([
                html.H3('Processamento do texto completo:'),
                html.P('Texto original:'),
                html.Pre(decoded[:1000] + '...', style={'whiteSpace': 'pre-wrap', 'wordBreak': 'break-all'}),
                html.P('Tokens após processamento:'),
                html.Pre('\n'.join(tokens_list[:8]) + '...', style={'whiteSpace': 'pre-wrap', 'wordBreak': 'break-all'})
            ])

            # Retornar a exibição do DataFrame e a nuvem de palavras
            return table_output, 'data:image/jpeg;base64,' + base64.b64encode(img.getvalue()).decode()

        except Exception as e:
            return html.Div([
                html.H3('Ocorreu um erro ao processar o arquivo:'),
                html.P(str(e))
            ]), None
    else:
        return html.Div(['Aguarde o processamento...']), None

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
    
# Callback para fazer download do arquivo TXT modificado com os novos tokens
@app.callback(
    Output("download_txt", "data"),
    [Input("btn_txt", "n_clicks")])
def download_txt(n_clicks):
    global tokens_list
    
    if n_clicks is not None and tokens_list:
        # Criar o conteúdo do arquivo TXT com os novos tokens
        txt_content = '\n'.join(tokens_list)
        # Retornar o arquivo TXT como uma resposta para download
        return dict(content=txt_content, filename="tokens.txt")

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
    global tokens_list

    if tokens_list  and n_clicks > 0 and lista:
        lista_set = set(lista.split())
        word_counter = Counter()

        filtered_text = []
        for tokens_string in tokens_list:
            tokens = tokens_string.split()
            filtered_tokens = [token for token in tokens if token in lista_set]
            word_counter.update(filtered_tokens)

        # Extraindo as palavras únicas que estão na lista original
        unique_filtered_tokens = [word for word in word_counter if word in lista_set]

        # Obtendo as 10 palavras mais comuns
        top_10_words = word_counter.most_common(10)
        top_words_list = [html.Li(f"{word}: {count} vezes", style={'color': 'white'}) for word, count in top_10_words]

        # Construção da tabela com as 10 palavras mais frequentes
        table_frequencia = html.Div([   html.H3('10 palavras mais frequentes:'),        
                                     html.Ul(top_words_list)  ])

        # Criar a nuvem de palavras com base no texto filtrado
        filtered_text = ' '.join(unique_filtered_tokens)
        wordcloud = WordCloud(width=600, height=300, background_color='white').generate(filtered_text)
        img = io.BytesIO()
        wordcloud.to_image().save(img, format='JPEG', quality=80)
        img.seek(0)
        wordcloud_image = html.Img(src='data:image/jpeg;base64,' + base64.b64encode(img.getvalue()).decode(), style={'width': '100%', 'margin': 'auto', 'display': 'block'})
        
        return [wordcloud_image,table_frequencia ]
    else:
        # Se nenhum clique ou lista vazia, retornar a nuvem de palavras fictícia
        return "error mensage"

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