# MemoList 

Sistema pessoal de repetição espaçada (SRS) desktop desenvolvido em Python + Flet, projetado especificamente para **memorização de listas ordenadas**.

**MemoList** você revisa e avalia a **sequência completa**, sendo ideal para:
- Sequência de eventos
- Sequências históricas e cronologias
- Listas de mnemônica / palácio da memória
- Procedimentos e passos ordenados

---

Como Executar

### Pré-requisitos e Instalação
- Python 3.10+
- Instale as dependências:
```bash
pip install -r requirements.txt
```

### Inicialização
Na raiz do projeto:
```bash
python main.py
```

---

## 🎯 Fluxo de Revisão

1. **Dashboard**: Mostra as listas prontas para revisão hoje (status *Devida hoje*).
2. **Item Oculto**: Exibe o título da lista, o número da posição (ex: *Posição #3*) e convida o usuário a recitar o item mentalmente ou em voz alta.
3. **Revelar Item**: Ao clicar em **"Mostrar Item"** (ou pressionar a tecla `Espaço`), o nome correto é exibido.
4. **Autoavaliação do Item**: Clique em **"Acertei (2)"** ou **"Errei (1)"** (ou use as teclas `1` ou `2`). O sistema avança imediatamente para a próxima posição oculta até o final da lista.
5. **Avaliação Geral Final**:
   - Exibe o resumo da sessão (ex: *12 acertos de 14 itens*), puramente para consulta/estatística.
   - O usuário escolhe a nota subjetiva que **alimenta exclusivamente** o algoritmo SM-2:
     - **Errei** (Grau $q=1$): reinicia o ciclo de repetições, penaliza o Ease Factor e agenda para 1 dia.
     - **Difícil** (Grau $q=3$): aprovado com esforço, crescimento lento de intervalo.
     - **Bom** (Grau $q=4$): aprovado confortavelmente.
     - **Fácil** (Grau $q=5$): memorização instantânea, maior intervalo.

---

Estrutura de Arquivos

```
MemoList/
├── data/
│   └── lists.json           # Armazenamento JSON local puro
├── memolist/
│   ├── models.py            # Modelos ItemList, SRSData, ReviewRecord
│   ├── storage.py           # Persistência atômica e segura em JSON
│   ├── srs.py               # Motor puro do algoritmo SM-2
│   └── ui/
│       ├── theme.py         # Tema escuro moderno e estilos visuais
│       └── views/
│           ├── dashboard_view.py   # Dashboard com listas devidas e contadores
│           ├── list_edit_view.py   # Criar/editar listas e reordenar itens
│           └── review_view.py      # Fluxo de revisão item a item + avaliação final
├── tests/
│   ├── test_srs.py          # Testes unitários do algoritmo SM-2
│   └── test_storage.py      # Testes de persistência em arquivo
├── main.py                  # Ponto de entrada da aplicação Flet desktop
└── README.md
```


