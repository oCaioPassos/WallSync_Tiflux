# 📋 Changelog — WallSync Tiflux

Todas as alterações notáveis do projeto serão documentadas aqui.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [1.0.0] — 2026-05-05

### 🎉 Release Inicial

#### Adicionado
- **Interface gráfica completa** com tema escuro premium (Tailwind Zinc)
- **Agendamento em lote** de scripts de wallpaper via API Tiflux RMM
- **Seletor de scripts** com busca paginada e debounce
- **Seletor de datas** com calendário visual (tkcalendar)
- **Seletor de horário** personalizado (hora e minuto)
- **Filtro de expediente** — configuração de horário comercial (início e fim)
- **Filtro de dias da semana** — seleção individual (Seg-Dom)
- **Envio paralelo** com `ThreadPoolExecutor` (5 workers simultâneos)
- **Barra de progresso animada** de 0% a 100% durante o envio
- **Proteção contra horários passados** — slots anteriores ao momento atual são automaticamente ignorados
- **Preview do wallpaper** — miniatura da imagem extraída do conteúdo do script
- **Botão "Abrir em Tela Cheia"** — abre o wallpaper no visualizador de imagens padrão do Windows
- **Consultar Agendamentos** — modal com listagem completa paginada dos agendamentos existentes
- **Agrupamento por dia** — agendamentos organizados por data com seções colapsáveis (+/−)
- **Cancelamento seletivo** — seleção individual ou por dia com exclusão via `PUT /cancel_scripts`
- **Seleção em massa** — botão "Selecionar Todos" / "Desmarcar Todos"
- **Exportação de logs** — salvar console de execução em arquivo `.txt`
- **Cancelamento de processo** — botão para interromper envios em andamento
- **Persistência de configuração** — token e script selecionado salvos em `config.json`
- **Retry automático** — 3 tentativas com intervalo de 2s em caso de timeout
- **Thread-safety completo** — todas as atualizações de UI via `self.after(0, ...)`
- **Proteção contra crash** — verificação `winfo_exists()` ao fechar modais durante operações

#### Segurança
- Token Bearer armazenado apenas localmente
- `config.json` incluído no `.gitignore`
- Comunicação exclusivamente via HTTPS

#### Técnico
- Aplicação single-file (`main.py`) com ~1.300 linhas
- 5 classes de UI (App, ScriptPickerModal, ScheduleManagerModal, DatePickerModal, TimePicker)
- Compatível com Python 3.10+ e Windows 10/11

---

---

## [Docs] — 2026-05-05

### 📚 Atualização da Documentação

#### Corrigido
- **`docs/script-wallpaper.md`**: Caminho de navegação corrigido para `Configurações → Recursos → Scripts` (URL: `app.tiflux.com/v/configurations/scripts`) — antes estava incorreto como `Equipamentos → RMM → Scripts`
- **`docs/script-wallpaper.md`**: Botão de criação corrigido para `+ Script` — antes estava como `Criar Script`
- **`docs/script-wallpaper.md`**: Campos do formulário atualizados com valores reais: Timeout = 160s, Executar como usuário = OFF
- **`docs/script-wallpaper.md`**: Nota sobre extração de preview — o regex `DownloadFile` não bate no script real (usa variável `$wallpaperUrl`, não URL literal); o preview é extraído pelo padrão 2 (URL geral)

#### Adicionado
- **`docs/script-wallpaper.md`**: Template completo de produção substituiu o script simplificado — inclui compilação do helper C# (`SetWallpaperNow.exe`), Scheduled Task com SID do usuário, Active Setup, 3 métodos de detecção de sessão e dupla aplicação com 15s de intervalo
- **`docs/script-wallpaper.md`**: Tabela explicando cada etapa do script e a razão técnica do EXE compilado
- **`docs/script-wallpaper.md`**: Exemplo real de log de execução bem-sucedida
- **`docs/script-wallpaper.md`**: Seção "O que alterar a cada nova campanha" — apenas `$desiredWallpaperName` e `$wallpaperUrl`

---

## Roadmap Futuro

> Funcionalidades planejadas para próximas versões:

- [ ] Suporte a múltiplos scripts por agendamento
- [ ] Histórico de agendamentos realizados
- [ ] Empacotamento como executável (.exe) via PyInstaller
- [ ] Notificações de conclusão via sistema
- [ ] Agendamento recorrente (semanal/mensal)
- [ ] Dashboard com estatísticas de uso
