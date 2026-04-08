# Como testar localmente

## 1. Instalar dependências

```powershell
.\venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 2. Configurar a chave da Groq

Copie `.env.example` para `.env` e preencha a variável:

```dotenv
GROQ_API_KEY=sua_chave_da_groq
GROQ_MODEL=llama-3.3-70b-versatile
LANGCHAIN_VERBOSE=false
```

## 3. Validar sintaxe

```powershell
python -m py_compile src\main.py src\__init__.py src\agent\__init__.py src\agent\executor.py
```

## 4. Rodar a interface

```powershell
streamlit run src/main.py
```

Perguntas úteis com a base sintética em `data/sample/vendas.csv`:

- Quem vendeu mais Mouse no Nordeste?
- Qual vendedor teve o maior volume total?
- Qual a média de valor unitário dos produtos?
