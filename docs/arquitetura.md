# 🏗️ Arquitetura Técnica — WallSync Tiflux

## Visão Geral

O WallSync Tiflux é uma aplicação **desktop monolítica** desenvolvida em Python, com interface gráfica moderna utilizando `customtkinter`. A aplicação se comunica diretamente com a API REST da plataforma Tiflux RMM para automatizar o agendamento de scripts de wallpaper.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                     WallSync Tiflux (main.py)               │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Sidebar    │  │  Main Content│  │    Modais        │  │
│  │              │  │              │  │                  │  │
│  │ - Iniciar    │  │ - Card API   │  │ - ScriptPicker   │  │
│  │ - Cancelar   │  │ - Card Sched │  │ - DatePicker     │  │
│  │ - Exportar   │  │ - Card Logs  │  │ - TimePicker     │  │
│  │ - Consultar  │  │ - Preview WP │  │ - ScheduleManager│  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Camada de Comunicação (API)              │   │
│  │                                                      │   │
│  │  - requests (HTTP Client)                            │   │
│  │  - ThreadPoolExecutor (envio paralelo)               │   │
│  │  - threading.Thread (operações assíncronas)          │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │ HTTPS
                             ▼
              ┌──────────────────────────┐
              │    API Tiflux RMM        │
              │  app.tiflux.com          │
              │                          │
              │  - GET  /scripts         │
              │  - GET  /batch_script_*  │
              │  - POST /batch_script_*  │
              │  - PUT  /{id}/cancel_*   │
              └──────────────────────────┘
```

## Classes Principais

### `App` (Classe Principal)
- **Responsabilidade:** Janela principal, sidebar, cards de configuração, logs, preview
- **Herda de:** `ctk.CTk`
- **Destaques:**
  - Gerencia o estado global (token, script selecionado, datas)
  - Orquestra o fluxo de agendamento em thread separada
  - Persiste configuração em `config.json`

### `ScriptPickerModal`
- **Responsabilidade:** Busca e seleção de scripts cadastrados na Tiflux
- **Herda de:** `ctk.CTkToplevel`
- **Destaques:**
  - Busca paginada com campo de pesquisa
  - Debounce de 500ms na busca para evitar requisições desnecessárias

### `ScheduleManagerModal`
- **Responsabilidade:** Consulta, visualização e cancelamento de agendamentos existentes
- **Herda de:** `ctk.CTkToplevel`
- **Destaques:**
  - Carregamento paginado completo (15 itens por página, conforme limite da API)
  - Agrupamento por dia com seções colapsáveis (+/−)
  - Seleção individual ou por dia inteiro
  - Cancelamento paralelo via `PUT /cancel_scripts`

### `DatePickerModal`
- **Responsabilidade:** Seleção de data via calendário visual
- **Herda de:** `ctk.CTkToplevel`

### `TimePicker`
- **Responsabilidade:** Seleção de horário (hora + minuto)
- **Herda de:** `ctk.CTkToplevel`

## Fluxo de Agendamento

```
1. Usuário configura parâmetros
       │
2. Clica em "▶ Iniciar Agendamentos"
       │
3. Validação de campos
       │
4. Geração dos slots de horário
   ├── Filtra por dia da semana
   ├── Filtra por horário de expediente
   └── Ignora horários que já passaram
       │
5. Envio paralelo (5 workers)
   ├── POST /batch_script_actions (para cada slot)
   ├── Atualização da barra de progresso
   └── Log de cada resultado
       │
6. Finalização
   ├── Resumo: X sucesso, Y falhas
   └── Barra de progresso → verde (100%)
```

## Threading e Thread-Safety

A aplicação utiliza threads para não bloquear a interface gráfica:

| Operação | Mecanismo | Thread-Safety |
|----------|-----------|---------------|
| Agendamento em lote | `ThreadPoolExecutor(max_workers=5)` | `self.after(0, callback)` |
| Busca de scripts | `threading.Thread(daemon=True)` | `self.after(0, callback)` |
| Busca de agendamentos | `threading.Thread(daemon=True)` | `self.after(0, callback)` + `winfo_exists()` |
| Cancelamento em lote | `ThreadPoolExecutor(max_workers=5)` | `self.after(0, callback)` |
| Download do wallpaper | `threading.Thread(daemon=True)` | `self.after(0, callback)` |

> **`self.after(0, callback)`** é o mecanismo do Tkinter para executar código na thread principal (UI thread), garantindo que widgets sejam atualizados de forma segura.

## Design System

A interface utiliza uma paleta de cores inspirada no **Tailwind CSS Zinc**:

| Variável | Hex | Uso |
|----------|-----|-----|
| `BG_COLOR` | `#09090b` | Fundo principal |
| `CARD_COLOR` | `#18181b` | Cards/containers |
| `BORDER_COLOR` | `#27272a` | Bordas |
| `ACCENT_COLOR` | `#3b82f6` | Botões primários, destaques |
| `TEXT_COLOR` | `#fafafa` | Texto principal |
| `MUTED_COLOR` | `#a1a1aa` | Texto secundário |
| `DANGER_COLOR` | `#ef4444` | Ações destrutivas |
| `SUCCESS_COLOR` | `#22c55e` | Sucesso/conclusão |

## Persistência

| Dado | Armazenamento | Formato |
|------|---------------|---------|
| Bearer Token | `config.json` | JSON |
| Script selecionado | `config.json` | JSON (id + name) |
| Logs de execução | Memória (TextBox) | Texto |
| Logs exportados | Arquivo `.txt` (manual) | Texto |
| Preview do wallpaper | Arquivo temporário | Imagem (PNG/JPG) |
