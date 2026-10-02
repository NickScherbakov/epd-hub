/**
 * EPD-Hub: Виджет «Спросить по ЭПД»
 * Общается только с /api/ask — NotebookLM полностью скрыт от пользователя.
 *
 * Подключение: <script src="js/ask-widget.js"></script>
 * Монтирование: AskWidget.mount('#ask-container');
 */

const AskWidget = (() => {

  const API_BASE = window.EPD_API_BASE || '';
  const POLL_INTERVAL_MS = 2500;
  const MAX_POLLS = 40; // 40 × 2.5s = 100 секунд максимум

  // ─── HTML-шаблон ────────────────────────────────────────────────────────

  const TEMPLATE = `
    <div class="ask-widget" id="epd-ask-widget">
      <div class="ask-widget__header">
        <span class="ask-widget__icon">💬</span>
        <span class="ask-widget__title">Спросить по ЭПД</span>
        <span class="ask-widget__badge">База знаний</span>
      </div>

      <div class="ask-widget__body">
        <div class="ask-widget__messages" id="ask-messages"></div>

        <div class="ask-widget__input-row">
          <textarea
            id="ask-input"
            class="ask-widget__input"
            placeholder="Например: Какие документы нужны для ЭТрН при мультимодальной перевозке?"
            rows="2"
            maxlength="1000"
          ></textarea>
          <button id="ask-send" class="ask-widget__send-btn" type="button">
            Спросить
          </button>
        </div>

        <p class="ask-widget__hint">
          Ответы основаны на актуальной нормативной базе ЭПД
        </p>
      </div>
    </div>
  `;

  // ─── Стили ──────────────────────────────────────────────────────────────

  const STYLES = `
    .ask-widget {
      font-family: system-ui, -apple-system, sans-serif;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      overflow: hidden;
      background: #fff;
      box-shadow: 0 4px 24px rgba(0,0,0,.08);
      max-width: 680px;
      margin: 0 auto;
    }
    .ask-widget__header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 14px 20px;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: #fff;
    }
    .ask-widget__icon { font-size: 18px; }
    .ask-widget__title {
      font-size: 15px;
      font-weight: 600;
      flex: 1;
    }
    .ask-widget__badge {
      font-size: 11px;
      background: rgba(255,255,255,.15);
      border-radius: 20px;
      padding: 2px 10px;
      color: #a0aec0;
    }
    .ask-widget__body { padding: 16px 20px 12px; }
    .ask-widget__messages {
      min-height: 60px;
      max-height: 400px;
      overflow-y: auto;
      margin-bottom: 12px;
    }
    .ask-msg {
      padding: 10px 14px;
      border-radius: 8px;
      margin-bottom: 8px;
      font-size: 14px;
      line-height: 1.6;
      animation: fadeIn .25s ease;
    }
    .ask-msg--user {
      background: #eef2ff;
      color: #3730a3;
      text-align: right;
      margin-left: 40px;
    }
    .ask-msg--answer {
      background: #f0fdf4;
      color: #166534;
      margin-right: 40px;
      white-space: pre-wrap;
    }
    .ask-msg--error {
      background: #fef2f2;
      color: #991b1b;
    }
    .ask-msg--loading {
      background: #f8fafc;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .ask-spinner {
      width: 16px; height: 16px;
      border: 2px solid #cbd5e1;
      border-top-color: #3b82f6;
      border-radius: 50%;
      animation: spin .7s linear infinite;
      flex-shrink: 0;
    }
    .ask-citations {
      margin-top: 6px;
      font-size: 12px;
      color: #6b7280;
    }
    .ask-widget__input-row {
      display: flex;
      gap: 8px;
    }
    .ask-widget__input {
      flex: 1;
      padding: 10px 14px;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      font-size: 14px;
      resize: none;
      outline: none;
      transition: border-color .2s;
      font-family: inherit;
    }
    .ask-widget__input:focus { border-color: #3b82f6; }
    .ask-widget__send-btn {
      padding: 10px 18px;
      background: #3b82f6;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      align-self: flex-end;
      transition: background .2s;
      white-space: nowrap;
    }
    .ask-widget__send-btn:hover { background: #2563eb; }
    .ask-widget__send-btn:disabled {
      background: #94a3b8;
      cursor: not-allowed;
    }
    .ask-widget__hint {
      font-size: 11px;
      color: #94a3b8;
      margin: 8px 0 0;
      text-align: center;
    }
    @keyframes fadeIn { from { opacity:0; transform:translateY(4px) } to { opacity:1; transform:none } }
    @keyframes spin { to { transform: rotate(360deg) } }
  `;

  // ─── Логика ─────────────────────────────────────────────────────────────

  function injectStyles() {
    if (document.getElementById('ask-widget-styles')) return;
    const style = document.createElement('style');
    style.id = 'ask-widget-styles';
    style.textContent = STYLES;
    document.head.appendChild(style);
  }

  function mount(selector) {
    injectStyles();
    const container = document.querySelector(selector);
    if (!container) {
      console.error(`AskWidget: элемент "${selector}" не найден`);
      return;
    }
    container.innerHTML = TEMPLATE;
    bindEvents();
  }

  function bindEvents() {
    const sendBtn = document.getElementById('ask-send');
    const input   = document.getElementById('ask-input');
    if (!sendBtn || !input) return;

    sendBtn.addEventListener('click', handleSend);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });
  }

  function handleSend() {
    const input   = document.getElementById('ask-input');
    const sendBtn = document.getElementById('ask-send');
    const question = input.value.trim();

    if (!question || question.length < 3) return;

    // Блокируем повторную отправку
    sendBtn.disabled = true;
    input.value = '';

    // Показываем вопрос
    appendMessage(question, 'user');

    // Показываем индикатор загрузки
    const loadingId = 'loading-' + Date.now();
    appendLoading(loadingId);

    // Отправляем запрос
    sendQuestion(question, loadingId).finally(() => {
      sendBtn.disabled = false;
    });
  }

  async function sendQuestion(question, loadingId) {
    try {
      // POST /api/ask
      const res = await fetch(`${API_BASE}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { task_id } = await res.json();

      // Polling до получения ответа
      await pollResult(task_id, loadingId);

    } catch (err) {
      removeMessage(loadingId);
      appendMessage('Ошибка соединения. Проверьте подключение и попробуйте снова.', 'error');
      console.error('[AskWidget]', err);
    }
  }

  async function pollResult(taskId, loadingId) {
    for (let i = 0; i < MAX_POLLS; i++) {
      await sleep(POLL_INTERVAL_MS);

      const res = await fetch(`${API_BASE}/api/ask/${taskId}`);
      if (!res.ok) continue;
      const data = await res.json();

      if (data.status === 'done') {
        removeMessage(loadingId);
        appendAnswer(data.answer, data.citations || []);
        return;
      }

      if (data.status === 'error') {
        removeMessage(loadingId);
        appendMessage(data.answer || 'Не удалось получить ответ.', 'error');
        return;
      }
      // queued / processing — продолжаем polling
    }

    // Таймаут
    removeMessage(loadingId);
    appendMessage('Ответ занял слишком много времени. Попробуйте позже.', 'error');
  }

  // ─── Вспомогательные функции рендеринга ─────────────────────────────────

  function appendMessage(text, type) {
    const container = document.getElementById('ask-messages');
    if (!container) return;
    const div = document.createElement('div');
    div.className = `ask-msg ask-msg--${type}`;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  function appendAnswer(text, citations) {
    const container = document.getElementById('ask-messages');
    if (!container) return;
    const div = document.createElement('div');
    div.className = 'ask-msg ask-msg--answer';
    div.textContent = text;

    if (citations.length > 0) {
      const cite = document.createElement('div');
      cite.className = 'ask-citations';
      cite.textContent = `Источники: [${citations.join(', ')}]`;
      div.appendChild(cite);
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  function appendLoading(id) {
    const container = document.getElementById('ask-messages');
    if (!container) return;
    const div = document.createElement('div');
    div.className = 'ask-msg ask-msg--loading';
    div.id = id;
    div.innerHTML = `<div class="ask-spinner"></div><span>Ищем ответ в базе знаний...</span>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ─── Публичный API ───────────────────────────────────────────────────────

  return { mount };
})();
