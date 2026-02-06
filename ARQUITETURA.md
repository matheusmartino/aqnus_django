# AQNUS - Arquitetura e Decisões de Projeto

## Princípios adotados

1. **Simplicidade acima de tudo** - Projeto Django monolítico, sem frameworks extras desnecessários. Nada de SPA, nada de API REST neste momento.

2. **Domínio bem modelado** - Os models representam fielmente as entidades do mundo real da gestão escolar. Cada app tem responsabilidade clara.

3. **Separação de responsabilidades** - Models contêm estrutura de dados e regras de domínio simples. Views são finas e chamam repositories/services. Regras complexas ficam em módulos de serviço (quando necessário). Admin é a interface principal.

6. **Organização por entidade** - Cada app é organizado internamente por entidade (um arquivo por model, um repository por entidade). Nada de arquivos únicos gigantes. Veja a seção "Organização interna dos apps" abaixo.

4. **Evolução incremental** - O sistema é construído em etapas bem definidas. Cada etapa entrega valor real e funciona de forma independente.

5. **Legibilidade** - Código em português (nomes de campos, verbose_name) alinhado ao domínio escolar brasileiro. Nomes de apps em inglês por convenção Django.

## Estrutura do projeto

Todo o codigo da aplicacao vive dentro de `src/`. Na raiz ficam apenas `manage.py`, documentacao e arquivos de configuracao. O `manage.py`, `wsgi.py` e `asgi.py` adicionam `src/` ao `sys.path`, entao os app labels e imports continuam inalterados (ex: `core.models`, `accounts.Usuario`).

## Organização interna dos apps

Todos os apps seguem uma estrutura **por entidade**. Isso é **padrão obrigatório** do projeto.

```
src/<app>/
├── models/
│   ├── __init__.py           # re-exporta todos os models do app
│   ├── <entidade>.py         # um arquivo por model
│   └── ...
├── views/
│   ├── __init__.py
│   └── <entidade>_views.py   # views separadas por entidade
├── repositories/
│   ├── __init__.py           # re-exporta todos os repositories
│   └── <entidade>_repository.py  # queries ORM por entidade
├── services/                 # regras de negócio (criado sob demanda)
│   └── __init__.py
├── admin.py                  # registro e configuração do admin
├── apps.py
└── urls.py
```

### Camadas e responsabilidades

| Camada | Responsabilidade | Exemplo |
|--------|-----------------|---------|
| **models/** | Estrutura de dados, campos, Meta, `__str__` | `people/models/aluno.py` |
| **repositories/** | Queries ORM encapsuladas (filtros, buscas, joins) | `people/repositories/aluno_repository.py` |
| **services/** | Regras de negócio que envolvem múltiplas entidades | `people/services/pessoa_service.py` |
| **views/** | Camada fina — chama repositories e services | `people/views/aluno_views.py` |
| **admin.py** | Apenas `@admin.register` e configuração | `people/admin.py` |

### Regras

- **models/__init__.py** deve re-exportar todos os models para que `from people.models import Aluno` funcione normalmente
- **repositories/** encapsulam acesso ao ORM — views **nunca** devem conter queries complexas
- **views/** são finas — chamam repositories e services, sem lógica pesada
- **services/** são criados sob demanda quando há regra de negócio que transcende um CRUD simples
- **Toda nova entidade deve seguir este padrão**

## Apps e responsabilidades

### `core`
- Modelo abstrato `ModeloBase` (campos de auditoria: `criado_em`, `atualizado_em`)
- Entidade `Escola` (unidade escolar / instituição)
- Futuramente: utilidades compartilhadas, validators, templatetags

### `accounts`
- Usuário customizado (`Usuario`) estendendo `AbstractUser`
- Campo `papel` para identificar o perfil do usuário (admin, secretaria, professor, biblioteca)
- Vínculo opcional com `Pessoa` via `OneToOneField`
- Futuramente: login/logout customizado, permissões por papel

### `people`
- `Pessoa` como entidade base (dados pessoais: nome, CPF, contato, endereco)
- `Aluno`, `Professor`, `Funcionario` como perfis vinculados via `OneToOneField`
- `Responsavel` — perfil de responsavel vinculado a Pessoa (pai, mae, responsavel legal)
- `AlunoResponsavel` — vinculo aluno-responsavel com tipo, principal, autorizacao de retirada
- Uma mesma Pessoa pode ter multiplos perfis (ex: funcionario que e aluno)
- Dois alunos irmaos compartilham os mesmos responsaveis (relacao N:N via tabela associativa)

### `academic`
- `AnoLetivo` — periodo letivo com datas de inicio/fim e status ativo
- `Disciplina` — componente curricular com codigo unico e carga horaria
- `Turma` — agrupamento de alunos, vinculada a ano letivo e escola (unique por trio)
- `ProfessorDisciplina` — vinculo professor-disciplina por ano letivo (unique por trio)
- `AlunoTurma` — estado atual do aluno na turma (unique por par, flag `ativo`)
- `Matricula` — evento formal de matricula com tipo (inicial/transferencia/remanejamento) e status (ativa/encerrada/cancelada)
- `MovimentacaoAluno` — historico imutavel de eventos (matricula, transferencia, encerramento)
- `MatriculaService` — regras de negocio para matricular, transferir e encerrar (em `academic/services/`)
- `Horario` — slot de tempo com ordem, hora_inicio, hora_fim e turno (unique por turno+ordem)
- `GradeHoraria` — grade de aulas de uma turma em um ano letivo (estado, nao historico)
- `GradeItem` — aula na grade, vinculando dia_semana + horario + disciplina + professor
- `GradeService` — regras de negocio para validar conflitos de professor e turma
- Admin com inlines: AlunoTurma e Matricula na Turma, ProfessorDisciplina na Disciplina, Movimentacoes na Matricula, GradeItem na GradeHoraria
- Futuramente: Frequencia, Notas, Boletim, Diario de Classe

### `library`
- `Autor` — autor de obras do acervo
- `Editora` — editora de publicacoes
- `Assunto` — categoria tematica (nome unico)
- `Obra` — titulo intelectual (conteudo). Vincula autores (M2M), editora (FK) e assunto (FK). ISBN unico quando preenchido.
- `Exemplar` — copia fisica de uma obra (objeto). Codigo de patrimonio unico. Situacao (disponivel/emprestado/indisponivel/baixado) controlada pelo BibliotecaService.
- `Emprestimo` — evento de emprestimo de exemplar a aluno. Status (ativo/devolvido/atrasado) controlado pelo service. Constraint parcial: um emprestimo ativo por exemplar.
- `BibliotecaService` — regras de negocio para emprestar, devolver e atualizar atrasos (em `library/services/`)
- Admin com ExemplarInline na Obra, devolucao via admin action, situacao do exemplar como readonly
- Futuramente: Reserva de exemplares, Multas por atraso

### `web`
- Portal web simples com Django Templates + Bootstrap
- Telas públicas e autenticadas
- Futuramente: painel do aluno, professor e responsável

## Padronizacao visual do Django Admin

O Admin padrao do Django exibe icones de acao (adicionar/editar/excluir/visualizar) ao lado de campos FK e O2O, e renderiza formularios largos e sem agrupamento. Para a operacao diaria de uma escola (secretaria, coordenacao), isso gera poluicao visual e erros de operacao.

O projeto aplica **tres camadas de padronizacao** que atuam em niveis diferentes:

### Camada 1 — Widget Python (`core/admin_mixins.py`, `core/widgets.py`)

O mixin `SemIconesRelacionaisMixin` sobrescreve `formfield_for_dbfield` — nao `formfield_for_foreignkey` — porque o Django aplica o `RelatedFieldWidgetWrapper` dentro de `formfield_for_dbfield`, DEPOIS de chamar `formfield_for_foreignkey`. Interceptar no ponto correto permite desabilitar as flags `can_add_related`, `can_change_related`, `can_delete_related` e `can_view_related` no wrapper ja criado.

O modulo `core/widgets.py` fornece `SemAcoesWidgetWrapper`, um `RelatedFieldWidgetWrapper` com todas as acoes forcadas para `False`, disponivel para uso direto quando necessario.

### Camada 2 — Template override (`templates/admin/widgets/related_widget_wrapper.html`)

Sobrescreve o template padrao do Django que renderiza os botoes ao lado de campos FK. O override renderiza **apenas o campo**, sem nenhum botao. Afeta todo o admin globalmente via `TEMPLATES['DIRS']`.

### Camada 3 — CSS (`static/admin/css/aqnus_admin.css`, `templates/admin/base_site.html`)

CSS minimalista que:
- Limita largura dos formularios (`max-width: 960px`)
- Compacta espacamento de fieldsets e inlines
- Controla largura de inputs e select2 (`max-width: 480px`)
- Esconde botoes residuais via `display: none !important` (fallback)
- Nao define cores — respeita as variaveis CSS do Django para compatibilidade com modo escuro

O CSS e carregado globalmente via override de `admin/base_site.html` no bloco `extrastyle`.

### Estrutura de arquivos

```
src/
├── core/
│   ├── admin_mixins.py              # SemIconesRelacionaisMixin (Camada 1)
│   └── widgets.py                   # SemAcoesWidgetWrapper (Camada 1)
├── templates/
│   └── admin/
│       ├── base_site.html           # Injeta CSS global (Camada 3)
│       └── widgets/
│           └── related_widget_wrapper.html  # Remove botoes (Camada 2)
└── static/
    └── admin/
        └── css/
            └── aqnus_admin.css      # Estilos compactos (Camada 3)
```

### Cuidados para nao perder o padrao

- Todo novo ModelAdmin e InlineModelAdmin **deve** herdar de `SemIconesRelacionaisMixin`
- Nunca usar `raw_id_fields` — usar `autocomplete_fields`
- Nunca adicionar botoes em `related_widget_wrapper.html`
- Nunca alterar `aqnus_admin.css` com cores hard-coded (usar variaveis CSS do Django)
- Ao atualizar o Django, verificar se o template `related_widget_wrapper.html` mudou

## Decisões arquiteturais

### Por que `Pessoa` é separada de `Aluno/Professor/Funcionario`?

Uma pessoa pode ter múltiplos papéis na escola. O professor de matemática pode ser pai de um aluno. O funcionário da secretaria pode estar cursando uma pós-graduação na mesma instituição. Centralizar dados pessoais em `Pessoa` evita duplicação e inconsistência.

### Por que Usuário customizado desde o início?

O Django recomenda definir `AUTH_USER_MODEL` antes da primeira migration. Mudar depois é trabalhoso. O `Usuario` customizado permite vincular ao modelo de `Pessoa` e ter campos extras (papel) sem gambiarras.

### Por que o Admin é a interface principal?

O Django Admin é robusto, testado e gratuito. Para a fase inicial (cadastros e gestão), ele atende perfeitamente. Investir em front customizado agora seria prematuro. O portal web será construído incrementalmente nas etapas futuras.

### Por que PostgreSQL desde o início?

A escolha do PostgreSQL como banco padrão é estratégica para um ERP escolar:

- **Integridade relacional robusta** — O domínio escolar é altamente relacional (Pessoa → Aluno → Matrícula → Turma → Disciplina → Nota). PostgreSQL oferece constraints, transações e foreign keys confiáveis, fundamentais para dados sensíveis como notas e frequência.
- **Crescimento do domínio** — Nas etapas futuras, recursos como campos JSON (configurações por escola), arrays (tags de acervo), full-text search (busca de livros na biblioteca) e índices parciais serão úteis sem precisar trocar de banco.
- **Paridade dev/produção** — Usar o mesmo banco em desenvolvimento e produção elimina bugs sutis de comportamento (collation, tipos de dados, transações). O que funciona localmente funciona em produção.
- **Padrão do ecossistema** — PostgreSQL é o banco mais recomendado pela comunidade Django e o mais adotado em ERPs e sistemas de gestão.

> SQLite pode ser usado para testes locais rápidos (bloco alternativo comentado no `src/aqnus/settings.py`), mas não é o banco oficial do projeto.

### Por que nomes de campos em português?

O domínio é escolar brasileiro. Os operadores do sistema (secretaria, coordenação) pensam em "matrícula", "aluno", "turma". Manter os `verbose_name` e nomes de campo em português torna o Admin e os formulários naturais para quem usa.

## Como o sistema deve evoluir

1. **Etapa 1** ✅: Cadastros fundamentais — Pessoa, Aluno, Professor, Funcionário, Escola, Usuário customizado. Admin completo, seeds, autenticação.

2. **Etapa 2** ✅: Estrutura acadêmica — AnoLetivo, Disciplina, Turma, ProfessorDisciplina, AlunoTurma. Admin com inlines, repositories, seed acadêmico.

3. **Etapa 3** ✅: Operacao escolar — Matricula (evento formal), MovimentacaoAluno (historico), Responsavel e AlunoResponsavel (filiacao). MatriculaService com regras de negocio. Seed operacional.

4. **Etapa 4** ✅: Biblioteca escolar — Autor, Editora, Assunto, Obra, Exemplar, Emprestimo. BibliotecaService com regras de emprestimo/devolucao. Seed da biblioteca.

5. **Etapa 5** ✅: Grade horaria escolar — Horario, GradeHoraria, GradeItem. GradeService com validacoes de conflito. Seed da grade.

6. **Etapa 6**: Frequencia, Notas, Boletim. Lancamentos pelo Admin e depois por telas proprias.

7. **Etapa 7**: Portal web com autenticacao, paineis por perfil.

8. **Futuramente**: API REST (Django REST Framework) se houver necessidade de integracao com apps mobile ou sistemas externos.

### Critérios de encerramento — Etapa 2

- [x] Models criados: AnoLetivo, Disciplina, Turma, ProfessorDisciplina, AlunoTurma
- [x] Todos estendem `ModeloBase` (campos de auditoria)
- [x] ForeignKeys com `on_delete=PROTECT` para segurança referencial
- [x] UniqueConstraints compostas: turma+ano+escola, professor+disciplina+ano, aluno+turma
- [x] Admin registrado com inlines (AlunoTurma na Turma, ProfessorDisciplina na Disciplina)
- [x] Repositories criados para todas as entidades
- [x] Migration gerada e aplicável (`0001_initial`)
- [x] Seed acadêmico (`seed_academic`) com validação de pré-requisitos da Etapa 1
- [x] Seed idempotente e atômico (`get_or_create` + `transaction.atomic`)
- [x] Organização por entidade (models/, repositories/ com arquivos separados)
- [x] Documentação atualizada (README.md, ARQUITETURA.md)

### Criterios de encerramento — Etapa 3

- [x] Models criados: Matricula, MovimentacaoAluno (academic), Responsavel, AlunoResponsavel (people)
- [x] Todos estendem `ModeloBase` (campos de auditoria)
- [x] ForeignKeys com `on_delete=PROTECT` para seguranca referencial
- [x] Partial UniqueConstraint: apenas uma matricula ativa por aluno/ano (`condition=Q(status='ativa')`)
- [x] UniqueConstraint composta: aluno+responsavel
- [x] `MatriculaService` com regras de negocio: matricular, transferir, encerrar
- [x] Service usa `@transaction.atomic` para consistencia
- [x] `MovimentacaoAluno` criado automaticamente pelo service (historico imutavel)
- [x] Admin readonly para MovimentacaoAluno (sem edicao manual)
- [x] Inlines: Movimentacoes na Matricula, Matriculas na Turma, Responsaveis no Aluno e na Pessoa
- [x] Repositories criados para todas as entidades novas
- [x] Forms com mensagens de erro humanas para constraints
- [x] Todos os admins herdam `SemIconesRelacionaisMixin`
- [x] Todos os campos FK usam `autocomplete_fields`
- [x] Migrations geradas e aplicaveis (`0002_etapa3_operacional` em ambos os apps)
- [x] Seed operacional (`seed_operacional`) com validacao de pre-requisitos das Etapas 1 e 2
- [x] Seed idempotente e atomico
- [x] Seed demonstra: matricula inicial, transferencia, encerramento, filiacao com irmaos
- [x] Nenhum model das Etapas 1 e 2 foi alterado
- [x] Seeds anteriores (`seed_data`, `seed_academic`) continuam funcionando
- [x] Documentacao atualizada (README.md, ARQUITETURA.md)

## Evolucao do dominio

O sistema cresce em camadas complementares. Cada etapa adiciona uma dimensao ao dominio sem alterar o que ja existe:

```
Etapa 1 — CADASTRO (quem existe)
┌─────────────────────────────────────────────────┐
│  Pessoa ──┬── Aluno                             │
│           ├── Professor                         │
│           └── Funcionario                       │
│  Escola                                         │
│  Usuario ── (papel: admin/secretaria/professor)  │
└─────────────────────────────────────────────────┘

Etapa 2 — ESTRUTURA (como a escola se organiza)
┌─────────────────────────────────────────────────┐
│  AnoLetivo                                       │
│  Disciplina                                      │
│  Turma ── (ano_letivo + escola)                  │
│  ProfessorDisciplina ── (professor + disciplina)  │
│  AlunoTurma ── (aluno + turma) [ESTADO ATUAL]    │
└─────────────────────────────────────────────────┘

Etapa 3 — OPERACAO (o que acontece no dia a dia)
┌─────────────────────────────────────────────────┐
│  Matricula ── evento formal (inicial/transf.)    │
│       └── MovimentacaoAluno ── historico imutavel │
│  Responsavel ── (pessoa com perfil de guardiao)   │
│  AlunoResponsavel ── (vinculo N:N de filiacao)    │
│  MatriculaService ── regras de negocio            │
└─────────────────────────────────────────────────┘

Etapa 4 — BIBLIOTECA (acervo e circulacao)
┌─────────────────────────────────────────────────┐
│  Autor / Editora / Assunto ── cadastros auxiliares │
│  Obra ── conteudo intelectual (titulo, ISBN)       │
│       └── Exemplar ── objeto fisico (patrimonio)   │
│              └── Emprestimo ── evento de circulacao │
│  BibliotecaService ── regras de emprestimo         │
└─────────────────────────────────────────────────┘

Etapa 5 — GRADE HORARIA (organizacao das aulas)
┌─────────────────────────────────────────────────┐
│  Horario ── slot de tempo (turno + ordem)          │
│  GradeHoraria ── grade de uma turma (ESTADO)       │
│       └── GradeItem ── aula alocada (dia/horario)  │
│  GradeService ── validacoes de conflito            │
└─────────────────────────────────────────────────┘
```

### Cadastro vs. Estrutura vs. Operacao

| Dimensao | Pergunta que responde | Muda com frequencia? | Exemplos |
|----------|----------------------|---------------------|----------|
| **Cadastro** | Quem sao as pessoas e a escola? | Raramente | Pessoa, Aluno, Professor, Escola |
| **Estrutura** | Como a escola esta organizada este ano? | Por ano letivo | Turma, Disciplina, AnoLetivo |
| **Operacao** | O que aconteceu com este aluno? | Diariamente | Matricula, Transferencia, Movimentacao |

### Matricula como evento vs. AlunoTurma como estado

A `Matricula` registra **o que aconteceu** (evento): quando o aluno foi matriculado, de que tipo (inicial, transferencia), qual o status resultante. E um registro historico — nunca e apagado, apenas encerrado ou cancelado.

O `AlunoTurma` registra **onde o aluno esta agora** (estado): em qual turma, se esta ativo. E atualizado pelo `MatriculaService` como consequencia de uma operacao.

```
Aluno matriculado    → Matricula(tipo=inicial, status=ativa)
                     → AlunoTurma(ativo=True)
                     → MovimentacaoAluno(tipo=matricula_inicial)

Aluno transferido    → Matricula antiga(status=encerrada)
                     → Matricula nova(tipo=transferencia, status=ativa)
                     → AlunoTurma antigo(ativo=False)
                     → AlunoTurma novo(ativo=True)
                     → MovimentacaoAluno(tipo=transferencia_saida)
                     → MovimentacaoAluno(tipo=transferencia_entrada)

Aluno encerrado      → Matricula(status=encerrada)
                     → AlunoTurma(ativo=False)
                     → MovimentacaoAluno(tipo=encerramento)
```

O `MatriculaService` e o unico ponto de mutacao — admin, views e seeds chamam o service, nunca alteram Matricula ou MovimentacaoAluno diretamente.

### Filiacao como relacao, nao como atributo

O vinculo entre aluno e responsavel e modelado como uma **relacao N:N** (tabela associativa `AlunoResponsavel`), nao como campos no model do aluno (ex: `nome_pai`, `nome_mae`). Isso permite:

- Um aluno ter multiplos responsaveis (pai, mae, tutor)
- Dois irmaos compartilharem os mesmos responsaveis sem duplicar dados
- Cada vinculo ter metadados proprios (principal, autorizado a retirar)
- Responsavel e uma Pessoa — pode ter perfil de Funcionario ou Professor simultaneamente

### Obra como conteudo vs. Exemplar como objeto vs. Emprestimo como evento

A separacao em tres camadas segue o mesmo padrao evento x estado da Matricula:

- **Obra** (conteudo): representa o titulo intelectual — "Dom Casmurro" de Machado de Assis. E um registro de catalogo. Nao e emprestada diretamente.
- **Exemplar** (objeto/estado): representa a copia fisica — o livro que esta na prateleira. Tem codigo de patrimonio unico e situacao (disponivel/emprestado). A situacao e derivada dos emprestimos ativos.
- **Emprestimo** (evento): representa o ato de emprestar — quando, para quem, com que prazo. E um registro historico. O status evolui: ativo → devolvido (ou atrasado → devolvido).

```
Exemplar emprestado  → Emprestimo(status=ativo)
                     → Exemplar(situacao=emprestado)

Exemplar devolvido   → Emprestimo(status=devolvido, data_devolucao=hoje)
                     → Exemplar(situacao=disponivel)

Emprestimo atrasado  → Emprestimo(status=atrasado)
                     → Exemplar(situacao=emprestado)
```

O `BibliotecaService` e o unico ponto de mutacao — admin e seeds chamam o service, nunca alteram Emprestimo ou Exemplar.situacao diretamente.

### Grade horaria como estado, nao historico

Diferente de Matricula e Emprestimo (que sao eventos), a `GradeHoraria` representa o **estado atual** do planejamento de aulas de uma turma. Quando o horario precisa ser ajustado (professor substituto, mudanca de sala, redistribuicao de carga horaria), a grade e editada diretamente.

Por que nao versionar grades?

- **Complexidade desnecessaria**: criar nova grade a cada alteracao exigiria migrar todos os itens, tratar grades sobrepostas, definir regras de vigencia
- **Historico irrelevante**: nao ha caso de uso real para consultar "como era a grade em abril" — o relevante e o horario atual
- **Historico em outro lugar**: se houver necessidade de auditoria (quem deu aula quando), sera registrado no Diario de Classe (Etapa futura), nao na grade

```
Grade alterada       → GradeItem editado diretamente
                     → GradeService valida conflitos
                     → Nenhum historico gerado

Necessidade futura   → Diario de Classe registra aulas efetivas
                     → Frequencia registra presencas
                     → Grade continua sendo ESTADO ATUAL
```

O `GradeService` valida conflitos antes de qualquer alteracao — admin e seeds chamam o service, nunca alteram GradeItem diretamente.

### Criterios de encerramento — Etapa 4

- [x] Models criados: Autor, Editora, Assunto, Obra, Exemplar, Emprestimo
- [x] Todos estendem `ModeloBase` (campos de auditoria)
- [x] ForeignKeys com `on_delete=PROTECT` para seguranca referencial
- [x] Partial UniqueConstraint: apenas um emprestimo ativo por exemplar
- [x] UniqueConstraint condicional: ISBN unico quando preenchido
- [x] Assunto com nome unico
- [x] `BibliotecaService` com regras de negocio: emprestar, devolver, atualizar atrasos
- [x] Service usa `@transaction.atomic` para consistencia
- [x] Situacao do exemplar derivada — controlada apenas pelo service (readonly no admin)
- [x] Admin: ExemplarInline na Obra, devolucao via admin action
- [x] Admin: emprestimos devolvidos bloqueados para edicao/exclusao
- [x] Admin: novo emprestimo via admin chama o service
- [x] Repositories criados para todas as entidades
- [x] Forms com mensagens de erro humanas para constraints
- [x] Todos os admins herdam `SemIconesRelacionaisMixin`
- [x] Todos os campos FK usam `autocomplete_fields`
- [x] Migration gerada e aplicavel
- [x] Seed da biblioteca (`seed_biblioteca`) com validacao de pre-requisitos da Etapa 1
- [x] Seed idempotente e atomico
- [x] Seed demonstra: emprestimo ativo, devolvido e atrasado
- [x] Nenhum model das Etapas 1, 2 e 3 foi alterado
- [x] Seeds anteriores (`seed_data`, `seed_academic`, `seed_operacional`) continuam funcionando
- [x] Documentacao atualizada (README.md, ARQUITETURA.md)

### Criterios de encerramento — Etapa 5

- [x] Models criados: Horario, GradeHoraria, GradeItem, DiaSemana (enum)
- [x] Todos estendem `ModeloBase` (campos de auditoria)
- [x] ForeignKeys com `on_delete=PROTECT` para seguranca referencial (exceto GradeItem->GradeHoraria que usa CASCADE)
- [x] UniqueConstraint: turno+ordem para Horario
- [x] UniqueConstraint: grade+dia+horario para GradeItem
- [x] Partial UniqueConstraint: apenas uma grade ativa por turma/ano
- [x] `GradeService` com regras de negocio: validar habilitacao professor, detectar conflitos
- [x] Service valida conflito de professor (mesmo dia/horario em qualquer turma do ano)
- [x] Service valida conflito de turma (mesmo dia/horario na mesma grade)
- [x] Admin: GradeItemInline na GradeHoraria
- [x] Admin: save_model e save_formset chamam GradeService para validacao
- [x] Admin: mensagens de erro humanas para conflitos
- [x] Forms com mensagens de erro humanas para constraints
- [x] Todos os admins herdam `SemIconesRelacionaisMixin`
- [x] Todos os campos FK usam `autocomplete_fields`
- [x] Migration gerada e aplicavel
- [x] Seed da grade (`seed_grade`) com validacao de pre-requisitos das Etapas 1 e 2
- [x] Seed idempotente e atomico
- [x] Seed cria: horarios padrao (matutino/vespertino), grade completa sem conflitos
- [x] Nenhum model das Etapas 1, 2, 3 e 4 foi alterado
- [x] Seeds anteriores (`seed_data`, `seed_academic`, `seed_operacional`, `seed_biblioteca`) continuam funcionando
- [x] Documentacao atualizada (README.md, ARQUITETURA.md)
- [x] Explicacao arquitetural: por que grade e estado e nao historico

## Papel do Django Admin vs. Portal Web

| Aspecto | Django Admin | Portal Web |
|---------|-------------|------------|
| Público | Secretaria, coordenação, TI | Alunos, professores, responsáveis |
| Funcionalidade | CRUD completo, gestão operacional | Consulta, lançamentos específicos |
| Quando | Desde a Etapa 1 | A partir da Etapa 5 |
| Customização | list_display, filters, inlines | Templates Bootstrap, views dedicadas |
