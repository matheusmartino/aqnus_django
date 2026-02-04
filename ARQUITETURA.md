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
- `Pessoa` como entidade base (dados pessoais: nome, CPF, contato, endereço)
- `Aluno`, `Professor`, `Funcionario` como perfis vinculados via `OneToOneField`
- Uma mesma Pessoa pode ter múltiplos perfis (ex: funcionário que é aluno)
- Futuramente: Responsável, Contato de emergência

### `academic`
- `AnoLetivo` — período letivo com datas de início/fim e status ativo
- `Disciplina` — componente curricular com código único e carga horária
- `Turma` — agrupamento de alunos, vinculada a ano letivo e escola (unique por trio)
- `ProfessorDisciplina` — vínculo professor-disciplina por ano letivo (unique por trio)
- `AlunoTurma` — matrícula de aluno em turma (unique por par)
- Admin com inlines: matricular alunos na tela da Turma, vincular professores na tela da Disciplina
- Futuramente: Frequência, Notas, Boletim (Etapa 3), Horários de aula

### `library` (futuro)
- Acervo (livros, periódicos)
- Empréstimo, Devolução, Reserva
- Controle de multas

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

3. **Etapa 3**: Operação diária — Frequência, Notas, Boletim. Lançamentos pelo Admin e depois por telas próprias.

4. **Etapa 4**: App `library` com acervo e empréstimos.

5. **Etapa 5**: Portal web com autenticação, painéis por perfil.

6. **Futuramente**: API REST (Django REST Framework) se houver necessidade de integração com apps mobile ou sistemas externos.

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

## Papel do Django Admin vs. Portal Web

| Aspecto | Django Admin | Portal Web |
|---------|-------------|------------|
| Público | Secretaria, coordenação, TI | Alunos, professores, responsáveis |
| Funcionalidade | CRUD completo, gestão operacional | Consulta, lançamentos específicos |
| Quando | Desde a Etapa 1 | A partir da Etapa 5 |
| Customização | list_display, filters, inlines | Templates Bootstrap, views dedicadas |
