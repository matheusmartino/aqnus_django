# AQNUS - Sistema de Gestão Educacional

ERP escolar desenvolvido em Django, com foco em cadastros acadêmicos, estrutura escolar e operação do dia a dia.

## Visão geral das etapas

| Etapa | Escopo | Status |
|-------|--------|--------|
| 1 | Cadastros fundamentais (Pessoa, Aluno, Professor, Funcionário, Escola, Usuário) | **Concluída** |
| 2 | Estrutura acadêmica (AnoLetivo, Disciplina, Turma, ProfessorDisciplina, AlunoTurma) | **Concluída** |
| 3 | Operacao escolar (Matricula, Responsaveis, Historico) | **Concluida** |
| 4 | Biblioteca escolar (Acervo, Emprestimo, Devolucao) | **Concluida** |
| 5 | Grade horaria escolar (Horario, GradeHoraria, GradeItem) | **Concluida** |
| 6 | Front operacional (Dashboard, listagens de alunos/turmas/professores/biblioteca) | **Concluida** |
| 7 | Portal web (Painel do aluno, professor e responsavel) | Planejada |

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
    ├── library/            # Biblioteca escolar (Etapa 4)
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

### 9. Popular dados operacionais (seed Etapa 3)

```bash
python manage.py seed_operacional
```

Requer que os seeds das Etapas 1 e 2 ja tenham sido executados. Cria os dados operacionais:

| Entidade | Qtd | Exemplos |
|----------|-----|----------|
| Matriculas | 5+ | Matriculas formais para alunos existentes |
| Transferencia | 1 | Isabela transferida do 5o Ano B para 5o Ano A |
| Encerramento | 1 | Gabriel com matricula encerrada (conclusao) |
| Responsaveis | 4 | Pais dos alunos (Carlos, Ana Paula, Roberto, Maria Clara) |
| Aluno-Responsavel | 6 | Lucas e Julia como irmaos (mesmos pais) |
| Movimentacoes | 7+ | Historico gerado automaticamente pelo service |

Idempotente — pode rodar varias vezes sem duplicar dados.

### 10. Popular dados da biblioteca (seed Etapa 4)

```bash
python manage.py seed_biblioteca
```

Requer que o seed da Etapa 1 ja tenha sido executado. Cria os dados da biblioteca:

| Entidade | Qtd | Exemplos |
|----------|-----|----------|
| Autores | 5 | Machado de Assis, Monteiro Lobato, Clarice Lispector, Jorge Amado, Cecilia Meireles |
| Editoras | 3 | Companhia das Letras, Editora Atica, Editora Moderna |
| Assuntos | 4 | Literatura Brasileira, Ciencias, Historia, Infantojuvenil |
| Obras | 6 | Dom Casmurro, O Sitio do Picapau Amarelo, A Hora da Estrela, etc. |
| Exemplares | 10 | BIB-0001 a BIB-0010 (com estados fisicos variados) |
| Emprestimos | 3 | 1 ativo, 1 devolvido, 1 atrasado |

Idempotente — pode rodar varias vezes sem duplicar dados.

### 11. Popular dados da grade horaria (seed Etapa 5)

```bash
python manage.py seed_grade
```

Requer que os seeds das Etapas 1 e 2 ja tenham sido executados. Cria os dados da grade horaria:

| Entidade | Qtd | Exemplos |
|----------|-----|----------|
| Horarios | 11 | 6 matutino (07:30-13:20), 5 vespertino (13:30-18:20) |
| Grades | 1 | Grade ativa para 5o Ano A — 2025 |
| Itens (aulas) | 30 | 6 aulas por dia (seg a sex), sem conflitos |

Idempotente — pode rodar varias vezes sem duplicar dados.

### 12. Rodar o servidor

```bash
python manage.py runserver
```

### 13. Acessar

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

# Popular dados operacionais (Etapa 3)
python manage.py seed_operacional

# Popular dados da biblioteca (Etapa 4)
python manage.py seed_biblioteca

# Popular dados da grade horaria (Etapa 5)
python manage.py seed_grade

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

### O que NAO faz parte da Etapa 2

- Operacao escolar (Matricula formal, Responsaveis) — Etapa 3
- Notas e frequencia — Etapa futura
- Horarios de aula — futuro
- Boletim — Etapa futura
- Biblioteca — Etapa 4

## Etapa 3 — Escopo e status

A Etapa 3 esta **concluida**. Ela cobre a **operacao escolar e filiacao**:

### Conceitos-chave

- **Matricula (evento)**: ato administrativo formal. Representa HISTORICO — nunca e apagada. Um aluno so pode ter uma matricula ativa por ano letivo. Tipos: inicial, transferencia, remanejamento.
- **AlunoTurma (estado)**: continua representando o estado ATUAL do aluno numa turma. Atualizado pelo service de matricula.
- **MovimentacaoAluno (historico)**: registro de eventos na vida escolar (matricula, transferencia, encerramento). Criado automaticamente pelo service. Nunca e apagado.
- **Responsavel (filiacao)**: perfil de responsavel vinculado a Pessoa (mesmo padrao de Aluno/Professor). Um responsavel pode estar vinculado a varios alunos — irmaos compartilham responsaveis.
- **AlunoResponsavel (vinculo)**: relacionamento aluno-responsavel com tipo de vinculo, flag de responsavel principal e autorizacao de retirada.

### Entidades criadas

| Entidade | App | Descricao |
|----------|-----|-----------|
| Matricula | academic | Ato administrativo de matricula (evento/historico) |
| MovimentacaoAluno | academic | Registro de movimentacoes na vida escolar |
| Responsavel | people | Perfil de responsavel (pai/mae/responsavel legal) |
| AlunoResponsavel | people | Vinculo aluno-responsavel (filiacao) |

### Fluxos operacionais

1. **Matricula inicial**: `MatriculaService.matricular_aluno()` → cria Matricula + atualiza AlunoTurma + registra MovimentacaoAluno
2. **Transferencia**: `MatriculaService.transferir_aluno()` → encerra matricula atual + cria nova matricula na turma destino + atualiza AlunoTurma + registra movimentacoes (saida + entrada)
3. **Encerramento**: `MatriculaService.encerrar_matricula()` → encerra matricula + desativa AlunoTurma + registra movimentacao

### Regras de negocio (em `academic/services/matricula_service.py`)

- Um aluno so pode ter UMA matricula ativa por ano letivo (constraint parcial no banco + validacao no service)
- Transferencia encerra a matricula atual antes de criar a nova
- Historico (MovimentacaoAluno) nunca e apagado
- MovimentacaoAluno e readonly no admin (criado apenas via service)

### Seed

`python manage.py seed_operacional` — cria matriculas formais, uma transferencia, um encerramento, 4 responsaveis, e 2 alunos irmaos compartilhando os mesmos pais.

### O que NAO faz parte da Etapa 3

- Notas e frequencia — Etapa futura
- Horarios de aula — futuro
- Boletim — Etapa futura
- Financeiro — futuro
- Biblioteca — Etapa 4

## Etapa 4 — Escopo e status

A Etapa 4 esta **concluida**. Ela cobre a **biblioteca escolar**:

### Conceitos-chave

- **Obra (conteudo)**: titulo intelectual — livro, periodico, publicacao. Uma obra pode ter multiplos autores, uma editora e um assunto. Nao e emprestada diretamente.
- **Exemplar (objeto)**: copia fisica de uma obra. Tem codigo de patrimonio unico, estado fisico e situacao (disponivel/emprestado/indisponivel/baixado). A situacao e controlada exclusivamente pelo BibliotecaService.
- **Emprestimo (evento)**: registro de quando um exemplar e emprestado a um aluno. Tem status (ativo/devolvido/atrasado) controlado pelo service. Constraint parcial garante um emprestimo ativo por exemplar.

### Entidades criadas

| Entidade | App | Descricao |
|----------|-----|-----------|
| Autor | library | Autor de obras do acervo |
| Editora | library | Editora de publicacoes |
| Assunto | library | Categoria tematica (unica) |
| Obra | library | Titulo intelectual (conteudo) |
| Exemplar | library | Copia fisica de uma obra (objeto) |
| Emprestimo | library | Evento de emprestimo de exemplar |

### Fluxos operacionais

1. **Emprestimo**: `BibliotecaService.emprestar_exemplar()` → valida disponibilidade → cria Emprestimo → atualiza Exemplar.situacao para 'emprestado'
2. **Devolucao**: `BibliotecaService.devolver_exemplar()` → valida status → registra data_devolucao → atualiza Exemplar.situacao para 'disponivel'
3. **Atraso**: `BibliotecaService.atualizar_emprestimos_atrasados()` → busca emprestimos ativos com data prevista no passado → atualiza status para 'atrasado'

### Regras de negocio (em `library/services/biblioteca_service.py`)

- Um exemplar so pode ser emprestado se estiver disponivel e ativo
- Um exemplar so pode ter um emprestimo ativo por vez (constraint parcial no banco + validacao no service)
- A situacao do exemplar e derivada — controlada apenas pelo service, nunca editada manualmente
- Emprestimos devolvidos sao bloqueados para edicao e exclusao no admin
- Devolucao via admin action ("Devolver exemplar(es) selecionado(s)")
- Novo emprestimo via admin chama o service automaticamente

### Seed

`python manage.py seed_biblioteca` — cria autores, editoras, assuntos, obras, exemplares e emprestimos de demonstracao (ativo, devolvido, atrasado).

### O que NAO faz parte da Etapa 4

- Notas e frequencia — Etapa futura
- Reserva de exemplares — futuro
- Multas por atraso — futuro
- Portal web — Etapa 6

## Etapa 5 — Escopo e status

A Etapa 5 esta **concluida**. Ela cobre a **grade horaria escolar**:

### Conceitos-chave

- **Horario (slot)**: define um periodo de aula (ex: 1o horario das 07:30 as 08:20). Vinculado a um turno (matutino/vespertino/noturno). A ordem dentro do turno e unica.
- **GradeHoraria (estado)**: representa a grade de aulas de uma turma em um ano letivo. Apenas uma grade pode estar ativa por turma/ano. NAO e historica — se o horario mudar, a grade e editada, nao versionada.
- **GradeItem (alocacao)**: representa uma aula em um slot especifico (dia + horario) da grade. Vincula disciplina e professor ao slot.

### Por que a grade NAO e historica?

Diferente de Matricula e Emprestimo (que sao eventos), a grade horaria representa o **estado atual** do planejamento de aulas. Quando o horario muda (professor substituto, ajuste de carga), a grade e editada diretamente.

Versionar grades traria complexidade sem beneficio real — nao ha necessidade de consultar "como era a grade em marco". O historico relevante (presenças, aulas dadas) sera registrado em entidades proprias nas etapas futuras (Diario de Classe).

### Entidades criadas

| Entidade | App | Descricao |
|----------|-----|-----------|
| Horario | academic | Slot de tempo (ordem, hora_inicio, hora_fim, turno) |
| GradeHoraria | academic | Grade horaria de uma turma (vinculo turma + ano_letivo) |
| GradeItem | academic | Aula na grade (dia_semana + horario + disciplina + professor) |
| DiaSemana | academic | Enum com dias da semana (SEG, TER, QUA, QUI, SEX, SAB) |

### Regras de conflito (em `academic/services/grade_service.py`)

- **Conflito de professor**: um professor nao pode ter duas aulas no mesmo dia/horario em todo o ano letivo
- **Conflito de turma**: uma turma nao pode ter duas aulas no mesmo dia/horario (ja coberto por UniqueConstraint)
- **Habilitacao obrigatoria**: o professor deve estar cadastrado em ProfessorDisciplina para a disciplina no ano letivo

Todas as validacoes sao feitas pelo `GradeService` antes de salvar, tanto no admin quanto no seed.

### Seed

`python manage.py seed_grade` — cria horarios padrao (6 matutino, 5 vespertino), uma grade completa para 5o Ano A com 30 aulas (6 por dia, seg a sex) distribuidas sem conflitos.

### O que NAO faz parte da Etapa 5

- Chamada / frequencia — Etapa futura
- Notas e diario de classe — Etapa futura
- Substituicao de professor — futuro
- Portal web — Etapa 6

## Front Operacional

O AQNUS possui um **front operacional completo** que e a interface principal para uso diario. Ele oferece navegacao rapida, visual moderno, e telas de listagem, criacao e edicao para as entidades principais.

### Papel do front

- **Interface principal**: listagens, criacao e edicao de registros
- **Visual moderno**: Bootstrap 5 + CSS customizado (Inter font, paleta propria)
- **Forms reutilizados**: os mesmos ModelForms do Admin sao usados no front, com classes Bootstrap aplicadas via mixin
- **CBVs (Class-Based Views)**: ListView, CreateView, UpdateView — views finas, sem regra de negocio

### Papel do Admin

O Django Admin permanece funcional e pode ser usado para:
- **Manutencao**: operacoes em massa, debug, acesso a entidades auxiliares
- **Operacoes complexas**: matriculas (usa MatriculaService), emprestimos (usa BibliotecaService), grade horaria (usa GradeService)
- **Entidades de suporte**: Pessoa, Escola, Disciplina, Horario, etc.

### Front vs Admin — quando usar cada um

| Acao | Onde fazer |
|------|-----------|
| Listar, criar e editar Alunos | **Front** (`/alunos/`) |
| Listar, criar e editar Turmas | **Front** (`/turmas/`) |
| Listar, criar e editar Professores | **Front** (`/professores/`) |
| Listar, criar e editar Obras | **Front** (`/biblioteca/`) |
| Ver totais e emprestimos atrasados | **Front** (Dashboard `/`) |
| Matricular aluno (fluxo formal) | **Admin** |
| Emprestimo/devolucao de exemplar | **Admin** |
| Grade horaria (criar/editar aulas) | **Admin** |
| Cadastrar Pessoa, Escola, Disciplina | **Admin** |
| Operacoes em massa, debug | **Admin** |

### URLs disponiveis

| URL | Descricao |
|-----|-----------|
| `/` | Dashboard com totais e emprestimos atrasados |
| `/alunos/` | Listagem de alunos com busca |
| `/alunos/novo/` | Criar novo aluno |
| `/alunos/<id>/editar/` | Editar aluno |
| `/turmas/` | Listagem de turmas com contagem de alunos |
| `/turmas/nova/` | Criar nova turma |
| `/turmas/<id>/editar/` | Editar turma |
| `/professores/` | Listagem de professores |
| `/professores/novo/` | Criar novo professor |
| `/professores/<id>/editar/` | Editar professor |
| `/biblioteca/` | Listagem de obras com exemplares disponiveis |
| `/biblioteca/nova/` | Criar nova obra |
| `/biblioteca/<id>/editar/` | Editar obra |

### Padrao de criacao/edicao

Cada entidade segue o mesmo padrao:

1. **ListView** (CBV) — lista com busca, badges de status, link no nome para edicao
2. **CreateView** (CBV) — formulario reutilizando o ModelForm existente, com Bootstrap via `BootstrapFormMixin`
3. **UpdateView** (CBV) — mesmo formulario, pre-preenchido com dados atuais
4. **Template compartilhado** — `form.html` unico por entidade (mesmo template para criar e editar)
5. **Mensagens de feedback** — sucesso/erro via Django Messages framework
