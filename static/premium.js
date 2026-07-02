(function () {
  const toast = document.getElementById('toast');
  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2200);
  }

  document.querySelectorAll('[data-copy-text]').forEach((button) => {
    button.addEventListener('click', async () => {
      const text = button.getAttribute('data-copy-text') || '';
      try {
        await navigator.clipboard.writeText(text);
        showToast('Mensagem copiada.');
      } catch (e) {
        showToast('Copie manualmente: ' + text.slice(0, 80));
      }
    });
  });

  document.querySelectorAll('[data-filter-table]').forEach((input) => {
    input.addEventListener('input', () => {
      const target = document.getElementById(input.dataset.filterTable);
      if (!target) return;
      const q = input.value.toLowerCase().trim();
      target.querySelectorAll('.lead-result').forEach((row) => {
        const hay = (row.getAttribute('data-search') || '').toLowerCase();
        row.style.display = hay.includes(q) ? '' : 'none';
      });
    });
  });

  const form = document.getElementById('vitoria-form');
  const input = document.getElementById('vitoria-input');
  const thread = document.getElementById('chat-thread');
  const samples = document.querySelectorAll('[data-sample]');

  function addMessage(kind, text) {
    if (!thread) return;
    const message = document.createElement('div');
    message.className = `message ${kind}`;
    const avatar = document.createElement('span');
    avatar.className = kind === 'bot' ? 'avatar xsmall vitoria-avatar' : 'avatar xsmall';
    avatar.textContent = kind === 'bot' ? 'V' : 'LA';
    const box = document.createElement('div');
    const small = document.createElement('small');
    small.textContent = kind === 'bot' ? 'Vitória · agora' : 'Você · agora';
    const p = document.createElement('p');
    p.innerHTML = text.replace(/\n/g, '<br>').replace(/\*(.*?)\*/g, '<strong>$1</strong>');
    box.appendChild(small); box.appendChild(p);
    message.appendChild(avatar); message.appendChild(box);
    thread.appendChild(message);
    thread.scrollTop = thread.scrollHeight;
  }

  function localVitoriaReply(rawText) {
    const text = (rawText || '').toLowerCase();
    if (text.includes('lead')) {
      return '*Perfeito. Vamos cadastrar esse lead.*\n\nComece me dizendo: nome, origem, empreendimento de interesse, objetivo de compra e faixa de entrada.\n\nExemplo: Mariana, Instagram, Vila dos Ipês, quer morar, entrada de R$ 60 mil.';
    }
    if (text.includes('parado') || text.includes('follow')) {
      return '*Você tem 3 oportunidades que merecem atenção hoje.*\n\n1. Mariana Costa — enviar simulação personalizada.\n2. Fernando Almeida — retomar proposta enviada.\n3. Camila Ribeiro — confirmar visita ao decorado.\n\nSugestão: priorize primeiro os leads quentes com score acima de 85.';
    }
    if (text.includes('preço') || text.includes('caro') || text.includes('objeção')) {
      return '*Script para objeção de preço:*\n\n“Entendo sua preocupação. Só para eu te orientar melhor: você achou caro comparando com outro loteamento, com o valor da parcela ou com o investimento total? Pergunto porque localização, infraestrutura e condição de pagamento mudam bastante essa análise.”';
    }
    if (text.includes('meus') || text.includes('carteira')) {
      return '*Resumo da sua carteira:*\n\n8 leads ativos, 3 quentes, 2 visitas agendadas e 3 follow-ups pendentes.\n\nA melhor próxima ação é ligar para Juliana Ferreira hoje às 16h e enviar materiais para Patrícia Santana.';
    }
    return '*Estou em modo demo local.*\n\nPosso simular cadastro de lead, follow-up, script de objeção, recomendações de materiais e resumo da carteira. A integração real com WhatsApp/Meta entra na próxima fase.';
  }

  function sendToVitoria(text) {
    addMessage('user', text);
    if (input) input.value = '';
    setTimeout(() => {
      addMessage('bot', localVitoriaReply(text));
      showToast('Interação simulada pela Vitória.');
    }, 350);
  }

  if (form && input) {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      sendToVitoria(text);
    });
  }
  samples.forEach((button) => {
    button.addEventListener('click', () => {
      const text = button.getAttribute('data-sample');
      if (input) input.value = text;
      sendToVitoria(text);
    });
  });
})();
