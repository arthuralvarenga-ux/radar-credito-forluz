# Radar de Estresse de Crédito Privado

Monitoramento semanal automatizado de notícias de estresse no mercado de
crédito privado brasileiro (recuperação judicial/extrajudicial, calote,
rebaixamento de rating, renegociação de dívida, covenant, fraude contábil
etc.), publicado como uma timeline em HTML.

Roda inteiramente no GitHub Actions — não precisa de servidor nem de você
lembrar de executar nada.

## Como funciona

Toda segunda-feira às 8h (horário de Brasília), o workflow:

1. Busca candidatos no Google News RSS para uma lista de palavras-chave de
   estresse de crédito (`scripts/fetch_news.py`).
2. Envia os candidatos para a API da Claude (modelo Haiku), que descarta o
   que não é relevante e extrai emissor, tipo de evento, severidade e um
   resumo curto (`scripts/classify.py`).
3. Funde os eventos novos no histórico acumulado (`data/eventos.json`, nunca
   perde o que já foi capturado) e regenera a timeline
   (`docs/index.html`) (`scripts/build_timeline.py`).
4. Commita e dá push automático das mudanças no próprio repositório.

## Passo a passo para colocar no ar

Eu não tenho acesso à sua conta do GitHub, então esses passos são pra você
rodar (leva uns 5 minutos):

### 1. Criar o repositório

```bash
# dentro da pasta creditwatch/ que você recebeu
git init
git add .
git commit -m "Setup inicial do radar de estresse de crédito"
```

Crie um repositório vazio no GitHub (pode ser público — o conteúdo é só
notícia pública, sem nenhum dado da Forluz) e depois:

```bash
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPO.git
git branch -M main
git push -u origin main
```

### 2. Adicionar a API key da Anthropic como secret

No repositório, vá em **Settings → Secrets and variables → Actions → New
repository secret**:
- Nome: `ANTHROPIC_API_KEY`
- Valor: sua chave (gerada em console.anthropic.com)

### 3. Ativar o GitHub Pages

Em **Settings → Pages**:
- Source: `Deploy from a branch`
- Branch: `main`, pasta `/docs`

Depois de alguns minutos, a timeline fica disponível em
`https://SEU_USUARIO.github.io/NOME_DO_REPO/`.

> Se o repositório for privado, o GitHub Pages só funciona em contas com
> plano pago. Nesse caso, ou o repo fica público (recomendado, já que os
> dados são só notícias públicas), ou você abre o `docs/index.html`
> localmente / via download do artifact do workflow.

### 4. Testar manualmente

Em **Actions → Monitor de Estresse de Crédito → Run workflow**, você pode
disparar a primeira execução sem esperar a segunda-feira.

### 5. Notificação de falha

Não precisa configurar nada extra: por padrão, o GitHub já envia e-mail
automaticamente para o dono do repositório quando uma execução agendada
falha.

## Ajustando as palavras-chave

A lista de gatilhos está em `scripts/fetch_news.py` (`KEYWORDS`). Pra
adicionar ou remover termos, edite essa lista e dê push — não precisa
mexer em mais nada.

## Rodando localmente (opcional, pra testar antes do push)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sua_chave_aqui
python scripts/main.py
```
