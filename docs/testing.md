# Como testar localmente

## 1. Instalar dependencias do backend

```powershell
.\venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 2. Instalar dependencias do frontend

```powershell
cd frontend
npm install
cd ..
```

## 3. Configurar a chave da Groq

Copie `.env.example` para `.env` e preencha:

```dotenv
GROQ_API_KEY=sua_chave_da_groq
GROQ_MODEL=llama-3.3-70b-versatile
LANGCHAIN_VERBOSE=false
```

## 4. Validar sintaxe do backend

```powershell
python -m py_compile src\main.py src\__init__.py src\agent\__init__.py src\agent\executor.py
```

## 5. Subir a API

```powershell
uvicorn src.main:app --reload
```

## 6. Subir o frontend React

Em outro terminal:

```powershell
cd frontend
npm run dev
```

## 7. Abrir a aplicacao

Abra `http://localhost:5173`.

Perguntas uteis com a base sintetica em `data/sample/vendas.csv`:

- Quem vendeu mais Mouse no Nordeste?
- Qual vendedor teve o maior volume total?
- Qual produto teve a maior receita?
