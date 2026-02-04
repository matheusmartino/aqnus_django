# AQNUS - Sistema de Gestão Educacional

ERP escolar desenvolvido em Django, com foco em cadastros acadêmicos, estrutura escolar e operação do dia a dia.

## Visão geral das etapas

| Etapa | Escopo | Status |
|-------|--------|--------|
| 1 | Cadastros fundamentais (Pessoa, Aluno, Professor, Funcionário, Escola, Usuário) | **Concluída** |
| 2 | Estrutura acadêmica (AnoLetivo, Disciplina, Turma, ProfessorDisciplina, AlunoTurma) | **Concluída** |
| 3 | Operação diária (Matrícula, Frequência, Notas, Boletim) | Planejada |
| 4 | Biblioteca escolar (Acervo, Empréstimo, Devolução) | Planejada |
| 5 | Portal web (Painel do aluno, professor e responsável) | Planejada |

## Tecnologia

- Python 3.12
- Django 6.0
- **PostgreSQL** (banco principal)
- psycopg 3 (driver PostgreSQL)
- Django Admin como interface principal
- Django Templates + Bootstrap (portal web futuro)

## Banco de dados

O projeto usa **PostgreSQL** como banco padrão. Configuração em `src/aqnus/settings.py`. Veja o passo a passo completo na seção "Como rodar o projeto".

> SQLite pode ser usado para testes locais rápidos — basta descomentar o bloco alternativo em `src/aqnus/settings.py`.

## Estrutura de pastas

```
aqnus_app/
├── manage.py               # Entry point Django (adiciona src/ ao sys.path)
├── requirements.txt
├── README.md
├── ARQUITETURA.md
├── .gitignore
└── src/                    # Todo o codigo da aplicacao
    ├── aqnus/              # Configuracao do projeto Django (settings, urls, wsgi, asgi)
    ├── core/               # Modelos base, utilidades e estrutura institucional (Escola)
    ├── accounts/           # Usuario customizado, autenticacao, perfis
    ├── people/             # Cadastro de pessoas (Pessoa, Aluno, Professor, Funcionario)
    ├── academic/           # Estrutura academica (Etapa 2)
    ├── library/            # (futuro) Biblioteca
    ├── web/                # Portal web simples (templates)
    ├── templates/          # Templates globais (base.html)
    └── static/             # Arquivos estaticos globais
```

> **Por que `src/`?** Separar o codigo-fonte dos arquivos de configuracao da raiz (`manage.py`, `requirements.txt`, docs) torna o projeto mais organizado. O `manage.py`, `wsgi.py` e `asgi.py` adicionam `src/` ao `sys.path`, entao os imports dos apps (`core.models`, `accounts.models`, etc.) continuam funcionando sem alteracao.

## Organizacao interna dos apps

Cada app segue uma estrutura **por entidade** — models, views e repositories ficam em arquivos separados por entidade, nunca em arquivos unicos gigantes.

```
src/people/                   # exemplo com o app people
├── models/
│   ├── __init__.py           # re-exporta todos os models
│   ├── pessoa.py             # model Pessoa
│   ├── aluno.py              # model Aluno
│   ├── professor.py          # model Professor
│   └── funcionario.py        # model Funcionario
├── views/
│   ├── __init__.py
│   └── (views por entidade)
├── repositories/
│   ├── __init__.py           # re-exporta todos os repositories
│   ├── pessoa_repository.py
│   ├── aluno_repository.py
│   ├── professor_repository.py
│   └── funcionario_repository.py
├── services/                 # regras de negocio (quando aplicavel)
│   └── __init__.py
├── admin.py                  # registro e configuracao do admin
├── apps.py
└── urls.py
```

**Regras:**

- **models/** — cada entidade em seu proprio arquivo; `__init__.py` re-exporta tudo para que `from people.models import Aluno` continue funcionando
- **repositories/** — encapsulam queries do ORM; views nunca contem queries complexas
- **views/** — finas, chamam repositories e services; sem regras de negocio
- **services/** — regras de negocio quando necessario (criado sob demanda)
- **admin.py** — apenas registro e configuracao do Django Admin

**Por que essa separacao?**

- **Legibilidade** — cada arquivo tem uma responsabilidade clara e um tamanho gerenciavel
- **Manutencao** — alteracoes numa entidade nao poluem arquivos de outras entidades
- **Escalabilidade** — o padrao se mantem organizado mesmo com dezenas de entidades

> **Toda nova entidade deve seguir este padrao.** Nao concentrar logica em arquivos unicos por conveniencia.

## Como rodar o projeto (passo a passo)

### 1. Clonar e criar ambiente virtual

```bash
git clone <url-do-repositorio>
cd aqnus_app
python -m venv venv
```

### 2. Ativar o ambiente virtual

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Criar o banco PostgreSQL

Com o PostgreSQL instalado e rodando, execute no terminal `psql` (conectado como superusuário):

```sql
CREATE USER aqnus WITH PASSWORD 'aqnus';
CREATE DATABASE aqnus OWNER aqnus;
GRANT ALL PRIVILEGES ON DATABASE aqnus TO aqnus;
```

Ou via Docker:

```bash
docker run -d --name aqnus-postgres -e POSTGRES_DB=aqnus -e POSTGRES_USER=aqnus -e POSTGRES_PASSWORD=aqnus -p 5432:5432 postgres:17
```

Ajuste `USER`, `PASSWORD`, `HOST` e `PORT` em `src/aqnus/settings.py` conforme seu ambiente.

### 5. Aplicar migrations

```bash
python manage.py migrate
```

### 6. Criar usuários de teste

```bash
python manage.py create_test_users
```

Isso cria os seguintes usuários (todos com acesso ao Admin):

| Usuário | Senha | Papel | Descrição |
|---------|-------|-------|-----------|
| `admin` | `admin123` | Administrador (superusuário) | Acesso total ao sistema |
| `secretaria` | `secretaria123` | Secretaria | Gestão de matrículas e cadastros |
| `professor` | `professor123` | Professor | Lançamento de notas e frequência (futuro) |
| `biblioteca` | `biblioteca123` | Biblioteca | Gestão do acervo e empréstimos (futuro) |

Cada usuário é vinculado a uma `Pessoa` no cadastro. O comando é idempotente — pode ser executado várias vezes sem duplicar dados.

> Para criar um superusuário manualmente: `python manage.py createsuperuser`

### 7. Popular dados de teste (seed)

```bash
python manage.py seed_data
```

Isso cria dados ficticios realistas para navegacao e teste no Django Admin:

| Entidade | Qtd | Exemplos |
|----------|-----|----------|
| Escola | 1 | Escola Modelo AQNUS |
| Pessoas | 11 | Dados completos (nome, CPF, telefone, endereco) |
| Alunos | 5 | Com matricula e data de ingresso |
| Professores | 3 | Matematica (USP), Lingua Portuguesa (PUC-SP), Historia (UNICAMP) |
| Funcionarios | 2 | Secretaria Escolar, Coordenador Pedagogico |

Os vinculos `Pessoa -> Aluno/Professor/Funcionario` sao criados automaticamente. O comando e idempotente — pode rodar varias vezes sem duplicar dados.

**Quando usar o seed:**
- Apos criar o banco e rodar `migrate`
- Sempre que o banco for recriado do zero
- Para ter dados de navegacao no Django Admin

> Todos os dados sao **ficticios**. Os CPFs passam no algoritmo de verificacao mas nao pertencem a pessoas reais.

### 8. Popular dados academicos (seed Etapa 2)

```bash
python manage.py seed_academic
```

Requer que o seed da Etapa 1 ja tenha sido executado. Cria a estrutura academica:

| Entidade | Qtd | Exemplos |
|----------|-----|----------|
| Ano Letivo | 1 | 2025 (fev a dez, ativo) |
| Disciplinas | 6 | Matematica, Lingua Portuguesa, Historia, Geografia, Ciencias, Educacao Fisica |
| Turmas | 2 | 5o Ano A, 5o Ano B (vinculadas a Escola Modelo AQNUS) |
| Professor-Disciplina | 6 | Cada professor leciona 2 disciplinas |
| Aluno-Turma | 5 | 3 alunos no 5o Ano A, 2 no 5o Ano B |

Idempotente — pode rodar varias vezes sem duplicar dados.

### 9. Rodar o servidor

```bash
python manage.py runserver
```

### 10. Acessar

- Portal: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

Use um dos usuários de teste (passo 6) para fazer login no Admin.

## Comandos úteis

```bash
# Verificar integridade do projeto
python manage.py check

# Aplicar migrations pendentes
python manage.py migrate

# Gerar migrations após alterar models
python manage.py makemigrations

# Criar usuários de teste
python manage.py create_test_users

# Popular dados de teste (Etapa 1)
python manage.py seed_data

# Popular dados academicos (Etapa 2)
python manage.py seed_academic

# Abrir shell Django
python manage.py shell

# Criar superusuário manualmente
python manage.py createsuperuser
```

## Padronizacao visual do Django Admin

O Django Admin e a interface principal do AQNUS. Para evitar a aparencia crua do admin padrao (icones de acao, formularios largos e vazios), o projeto aplica **tres camadas de padronizacao** que funcionam em conjunto:

### As 3 camadas

| Camada | O que faz | Arquivo |
|--------|-----------|---------|
| **1 — Widget Python** | Desabilita flags `can_add/change/delete/view_related` no `RelatedFieldWidgetWrapper` | `core/admin_mixins.py`, `core/widgets.py` |
| **2 — Template override** | Remove completamente os botoes do HTML renderizado | `templates/admin/widgets/related_widget_wrapper.html` |
| **3 — CSS** | Esconde botoes residuais + compacta formularios | `static/admin/css/aqnus_admin.css`, `templates/admin/base_site.html` |

As tres camadas sao **redundantes por design** — se uma falhar, as outras garantem o resultado.

### Regras adotadas

1. **`autocomplete_fields` universal** — todo campo FK e O2O usa autocomplete (busca por digitacao). Nunca usar `raw_id_fields` (mostra ID numerico) nem dropdown padrao (carrega todos os registros).
2. **Sem icones de acao em FK** — botoes de criar/editar/excluir/visualizar ao lado de campos relacionais sao removidos nas 3 camadas. Nenhum icone deve aparecer.
3. **Formularios compactos** — `max-width: 960px`, campos limitados a `480px`, espacamento reduzido. O CSS esta em `static/admin/css/aqnus_admin.css` e e carregado globalmente via `base_site.html`.
4. **`fieldsets` em todos os formularios** — campos agrupados logicamente (Identificacao, Contato, Vinculo, Status, etc.). Nenhum formulario deve ser plano.
5. **Mensagens de erro humanas** — cada entidade possui um `ModelForm` customizado (em `forms/`) que traduz erros de unique constraint para linguagem amigavel.

### Boas praticas para novos formularios

- Herdar de `SemIconesRelacionaisMixin` como **primeira** classe na heranca do Admin e de inlines
- Definir `fieldsets` agrupando os campos logicamente
- Usar `autocomplete_fields` para todo FK/O2O (o model-alvo precisa ter `search_fields` no seu Admin)
- Criar o form em `<app>/forms/<entidade>_form.py`, seguindo o padrao por entidade do projeto
- Re-exportar no `<app>/forms/__init__.py`
- Tratar mensagens de unique constraint no `validate_unique` do form
- **Nunca** adicionar `raw_id_fields` — usar `autocomplete_fields`
- **Nunca** alterar os templates/CSS sem atualizar esta documentacao

## Etapa 1 — Escopo e status

A Etapa 1 está **concluída**. Ela cobre:

- **Models**: Pessoa, Aluno, Professor, Funcionário, Escola, Usuário customizado
- **Admin**: Cadastro completo via Django Admin com filtros, busca e inlines
- **Autenticação**: Usuário customizado com campo `papel` (admin, secretaria, professor, biblioteca)
- **Vínculos**: Pessoa ↔ Aluno/Professor/Funcionário (OneToOne), Usuário ↔ Pessoa (opcional)
- **Dados de teste**: Management commands `create_test_users` e `seed_data`
- **Migrations**: Aplicáveis com `python manage.py migrate` sem ajustes manuais

### O que NÃO faz parte da Etapa 1

- Estrutura acadêmica — Etapa 2
- Operação diária (Frequência, Notas) — Etapa 3
- Biblioteca (Acervo, Empréstimo) — Etapa 4
- Portal web com painéis por perfil — Etapa 5
- API REST — futuro, se necessário

## Etapa 2 — Escopo e status

A Etapa 2 está **concluída**. Ela cobre a **estrutura acadêmica**:

- **AnoLetivo**: periodo letivo com datas de inicio/fim e status ativo
- **Disciplina**: componente curricular com codigo e carga horaria
- **Turma**: agrupamento de alunos, vinculada a ano letivo e escola
- **ProfessorDisciplina**: vinculo professor-disciplina por ano letivo (unique por trio)
- **AlunoTurma**: matricula de aluno em turma (unique por par)
- **Admin**: registro completo com inlines (matricular alunos na tela da Turma, vincular professores na tela da Disciplina)
- **Seed**: `python manage.py seed_academic` com dados realistas e vinculos
- **Repositories**: acesso a dados encapsulado por entidade

### O que NÃO faz parte da Etapa 2

- Notas e frequência — Etapa 3
- Horários de aula — futuro
- Boletim — Etapa 3
- Biblioteca — Etapa 4
