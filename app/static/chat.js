'use strict';
const $ = id => document.getElementById(id);
const key = 'mistral-local-chats-v1';
let chats = [], current, busy = false;
try {
    const data = JSON.parse(localStorage.getItem(key) || '[]');
    if (Array.isArray(data)) chats = data.filter(c => c && typeof c.id === 'string' && Array.isArray(c.messages) && c.messages.every(m => ['user', 'assistant'].includes(m.role) && typeof m.content === 'string'));
} catch {
}

function save() {
    try {
        localStorage.setItem(key, JSON.stringify(chats));
    } catch {
        $('error').textContent = 'Stockage local plein : cette conversation ne sera pas conservée après fermeture.';
        $('error').hidden = false;
    }
}

function active() {
    return chats.find(c => c.id === current);
}

function newChat() {
    if (busy) return;
    current = crypto.randomUUID();
    chats.unshift({id: current, title: 'Nouveau chat', messages: []});
    save();
    render();
    $('prompt').focus();
    document.body.classList.remove('menu-open');
}

function renderHistory() {
    $('history').replaceChildren();
    const query = $('search').value.toLowerCase();
    chats.filter(c => String(c.title).toLowerCase().includes(query)).forEach(c => {
        const row = document.createElement('div');
        row.className = 'history-row' + (c.id === current ? ' active' : '');
        const button = document.createElement('button');
        button.textContent = c.title;
        button.onclick = () => {
            if (busy) return;
            current = c.id;
            render();
            document.body.classList.remove('menu-open');
        };
        const del = document.createElement('button');
        del.className = 'delete';
        del.textContent = '×';
        del.setAttribute('aria-label', 'Supprimer ' + c.title);
        del.onclick = () => {
            if (busy) return;
            chats = chats.filter(item => item.id !== c.id);
            if (current === c.id) {
                current = chats[0]?.id;
                if (!current) {
                    newChat();
                    return;
                }
            }
            save();
            render();
        };
        row.append(button, del);
        $('history').append(row);
    });
}

function contentNode(text) {
    const node = document.createElement('div');
    node.className = 'content';
    text.split(/```/).forEach((part, i) => {
        const block = document.createElement(i % 2 ? 'pre' : 'span');
        block.textContent = i % 2 ? part.replace(/^[\w+-]*\n/, '') : part;
        node.append(block);
    });
    return node;
}

function render() {
    renderHistory();
    const messages = active()?.messages || [];
    $('welcome').hidden = messages.length > 0;
    $('messages').style.display = messages.length ? 'block' : 'none';
    $('messages').replaceChildren();
    messages.forEach(m => {
        const node = document.createElement('article');
        node.className = 'message ' + m.role;
        if (m.role === 'assistant') {
            const label = document.createElement('div');
            label.className = 'speaker';
            label.append(document.querySelector('.hero-logo').cloneNode(true), document.createTextNode('Mistral'));
            node.append(label);
        }
        node.append(contentNode(m.content));
        if (m.role === 'assistant') {
            const copy = document.createElement('button');
            copy.className = 'copy';
            copy.textContent = 'Copier';
            copy.onclick = async () => {
                try {
                    await navigator.clipboard.writeText(m.content);
                    copy.textContent = 'Copié ✓';
                } catch {
                    copy.textContent = 'Copie indisponible';
                }
            };
            node.append(copy);
        }
        $('messages').append(node);
    });
    $('messages').scrollTop = $('messages').scrollHeight;
}

function resize() {
    $('prompt').style.height = 'auto';
    $('prompt').style.height = Math.min($('prompt').scrollHeight, 180) + 'px';
}

$('composer').addEventListener('submit', async event => {
    event.preventDefault();
    const text = $('prompt').value.trim();
    if (!text || busy) return;
    const chat = active();
    if (chat.messages.length >= 98) {
        $('error').textContent = 'Cette conversation est longue. Ouvrez un nouveau chat pour continuer.';
        $('error').hidden = false;
        return;
    }
    busy = true;
    $('send').disabled = true;
    $('prompt').disabled = true;
    $('error').hidden = true;
    chat.messages.push({role: 'user', content: text});
    if (chat.messages.length === 1) chat.title = text.slice(0, 45);
    $('prompt').value = '';
    resize();
    save();
    render();
    const typing = document.createElement('div');
    typing.className = 'message typing';
    typing.textContent = 'Mistral réfléchit…';
    $('messages').append(typing);
    $('messages').scrollTop = $('messages').scrollHeight;
    try {
        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({messages: chat.messages})
        });
        const result = await response.json();
        if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Conversation invalide ou trop longue. Essayez un nouveau chat.');
        if (typeof result.answer !== 'string') throw new Error('Réponse du serveur invalide.');
        chat.messages.push({role: 'assistant', content: result.answer});
        save();
    } catch (error) {
        chat.messages.pop();
        $('prompt').value = text;
        resize();
        save();
        $('error').textContent = error.message || 'Connexion impossible. Vérifiez que le serveur est démarré.';
        $('error').hidden = false;
    } finally {
        busy = false;
        $('send').disabled = false;
        $('prompt').disabled = false;
        render();
        $('prompt').focus();
    }
});
$('prompt').addEventListener('input', resize);
$('prompt').addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
        event.preventDefault();
        $('composer').requestSubmit();
    }
});
$('new-chat').onclick = newChat;
$('search').oninput = renderHistory;
$('menu').onclick = () => {
    document.body.classList.toggle('menu-open');
    $('menu').setAttribute('aria-expanded', String(document.body.classList.contains('menu-open')));
};
document.querySelectorAll('[data-prompt]').forEach(button => button.onclick = () => {
    $('prompt').value = button.dataset.prompt;
    resize();
    $('prompt').focus();
});
document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        newChat();
    }
});
if (chats.length) {
    current = chats[0].id;
    render();
} else newChat();
