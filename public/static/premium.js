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
  const demoPhone = '5516999999999';

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

  async function sendToVitoria(text) {
    addMessage('user', text);
    if (input) input.value = '';
    try {
      const response = await fetch('/api/simulate-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ from_phone: demoPhone, text, profile_name: 'Lucas Andrade' })
      });
      if (!response.ok) throw new Error('Falha na simulação');
      const data = await response.json();
      addMessage('bot', data.reply || 'Pronto. Atualizei o fluxo.');
      showToast('Interação simulada via Vitória.');
    } catch (error) {
      const fallback = 'Estou em modo demonstração. Consigo simular cadastro, qualificação, follow-up e script, mas sem conexão real com a Meta por enquanto.';
      addMessage('bot', fallback);
      showToast('Simulação local exibida.');
    }
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
