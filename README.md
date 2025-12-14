# USB Safe Ejector Pro

Ferramenta avançada para ejetar pendrives e HDs externos com segurança e rapidez no Windows, com interface moderna, modo escuro e suporte a modos de ejeção rápido e seguro.

[Print](https://github.com/olverclock/USBSafeEjectorPro/blob/main/usb_eject_pro.png)
## ✨ Principais recursos

- Ejeção rápida ⚡ (~1s) e segura 🛡 (com verificações extras)  
- Detecção inteligente de pendrives e HDs externos  
- Verificação de processos que estão bloqueando a unidade  
- Forçar ejeção matando processos travados (uso opcional)  
- Montar dispositivos USB não montados com letra de unidade  
- Interface moderna com tema claro/escuro (modo escuro padrão)  
- Barra de progresso em tempo real durante a ejeção  
- Janela abre no canto inferior direito da tela (encostada na borda e barra de tarefas)  
- Menu de contexto com clique direito em cada dispositivo  
- Atalho “About” discreto com créditos ao desenvolvedor (olverclock)  

## 🛠 Tecnologias utilizadas

- Python 3.x  
- Tkinter / CustomTkinter (interface gráfica)  
- Módulos de sistema para acesso a dispositivos e volumes no Windows  

## 📦 Requisitos

- Windows 10 ou superior  
- Python 3.8+ instalado  
- Permissões para ejetar dispositivos USB no sistema  

Bibliotecas Python necessárias (exemplo de `pip install`):

```bash
pip install customtkinter
pip install psutil
pip install pywin32
pip install pillow
```

(Ajuste essa lista conforme as dependências reais do seu projeto.)

## 🚀 Como executar

1. Clone o repositório ou baixe os arquivos:

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o programa:

```bash
python usb_ejector.py
```

A janela será aberta em **modo escuro**, no **canto inferior direito** da tela.

## 🧭 Como usar

### Interface principal

- Lista todos os dispositivos USB detectados (pendrives, HDs externos etc).  
- Mostra nome, letra da unidade, uso de espaço e status.  
- Clique em um dispositivo para acompanhar a ejeção com barra de progresso.

### Barra de controles (topo)

- 👁 Mostrar/ocultar dispositivos não montados  
- ⚡ Alternar modo de ejeção (rápido ↔ seguro)  
- 🌙 Alternar tema (escuro ↔ claro)  
- ↻ Atualizar lista de dispositivos  
- ℹ️ Abrir janela “About” (créditos e informações)  
- ✕ Fechar o aplicativo  

### Modos de ejeção

- **Modo rápido (⚡)**  
  - Focado em velocidade (~1 segundo).  
  - Ideal para uso diário quando você sabe que não há cópias em andamento.

- **Modo seguro (🛡)**  
  - Executa verificações adicionais e operações de sistema antes de ejetar.  
  - Recomendo quando estiver manipulando dados importantes ou dispositivos mais sensíveis.

### Menu de contexto (clique direito em um dispositivo)

Ao clicar com o botão direito em um dispositivo USB, um menu é exibido com opções como:

- 📂 Abrir no Explorer  
- ⏏ Ejetar  
- 🔍 Ver processos que estão bloqueando a unidade  
- 💪 Forçar ejeção (tenta matar processos em uso)  
- ℹ️ About – by olverclock (informações e créditos)

## ⚠ Avisos importantes

- Forçar ejeção e matar processos pode causar perda de dados se ainda houver gravações pendentes.  
- Sempre que possível, use o modo seguro antes de recorrer à ejeção forçada.  
- Use por sua conta e risco, especialmente em ambientes de produção ou com dados críticos.

## 🧩 Estrutura sugerida do projeto

```text
.
├─ usb_ejector.py          # Script principal com a interface e lógica
├─ requirements.txt        # Dependências Python
├─ README.md               # Este arquivo
└─ assets/                 # Ícones, imagens, etc. (opcional)
```

## 🙋 Sobre / Créditos

- Desenvolvido por **olverclock**  
- Foco em: desempenho, segurança na ejeção e uma experiência visual agradável no Windows  

Se este projeto for útil para você, considere:

- ⭐ Dar uma estrela no repositório  
- Abrir issues com sugestões, bugs ou melhorias  
- Enviar pull requests com correções ou novos recursos  

## 📄 Licença

Adicione aqui a licença que você deseja utilizar, por exemplo:

- MIT, GPL-3.0, Apache-2.0, ou outra de sua preferência.

Exemplo (MIT):

```text
Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.
```
