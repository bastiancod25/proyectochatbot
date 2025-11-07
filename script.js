jQuery(document).ready(function($) {
    // Genera un ID de sesión único
    function generateSessionId() {
        return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    let sessionId = sessionStorage.getItem('chatbotSessionId');
    if (!sessionId) {
        sessionId = generateSessionId();
        sessionStorage.setItem('chatbotSessionId', sessionId);
    }
    
    // Variable para el temporizador de inactividad
    let inactivityTimer;

    // Función para añadir mensajes al chat
    function addMessage(message, sender) {
        const chatMessages = $('#chat-messages');
        const messageClass = sender === 'user' ? 'user-message' : 'bot-message';
        const formattedMessage = message.replace(/\n/g, '<br>');
        chatMessages.append('<div class="' + messageClass + '"><p>' + formattedMessage + '</p></div>');
        chatMessages.scrollTop(chatMessages.prop("scrollHeight"));
    }

    // --- NUEVO: Función para mostrar la burbuja "Hey" ---
    function showPingBubble() {
        // Solo mostrar si el chat ESTÁ CERRADO
        if (!$('#chatbot-container').hasClass('open')) {
            $('#chat-ping-bubble').addClass('show');
        }
    }

    // --- NUEVO: Función para iniciar el temporizador ---
    function startInactivityTimer() {
        // Limpia cualquier temporizador anterior
        if (inactivityTimer) {
            clearTimeout(inactivityTimer);
        }
        
        // Inicia un nuevo temporizador de 5 segundos (10000 milisegundos)
        inactivityTimer = setTimeout(showPingBubble, 10000);
    }


    // Función para enviar el mensaje al servidor
    function sendMessage() {
        const userInput = $('#chat-input').val();
        if (userInput.trim() === '') {
            return;
        }
        
        addMessage(userInput, 'user');
        $('#chat-input').val('');
        
        $('#chat-messages').append('<div class="bot-message typing-indicator"><p><span>.</span><span>.</span><span>.</span></p></div>');
        $('#chat-messages').scrollTop($('#chat-messages').prop("scrollHeight"));

        $.ajax({
            url: chatbot_vars.ajax_url, 
            type: 'POST',
            data: {
                action: 'enviar_pregunta_chatbot',
                question: userInput,
                session: sessionId
            },
            success: function(response) {
                $('.typing-indicator').remove();
                if (response.success && response.data.reply) {
                    addMessage(response.data.reply, 'bot');
                } else {
                    addMessage('Lo siento, ocurrió un error al procesar tu pregunta. Inténtalo de nuevo.', 'bot');
                }
            },
            error: function() {
                $('.typing-indicator').remove();
                addMessage('No pude conectarme con el servidor. Por favor, revisa tu conexión a internet.', 'bot');
            }
        });
    }

    // Eventos
    $('#chat-send-btn').on('click', sendMessage);
    $('#chat-input').on('keypress', function(e) {
        if (e.which === 13) {
            sendMessage();
        }
    });

    // Toggle del chat
    $('#chat-toggle-btn').on('click', function() {
        $('#chatbot-container').toggleClass('open');
        
        // --- NUEVO: Al abrir el chat, oculta la burbuja y detiene el temporizador ---
        $('#chat-ping-bubble').removeClass('show');
        clearTimeout(inactivityTimer);
    });

    $('.chat-close-btn').on('click', function() {
        $('#chatbot-container').removeClass('open');
        
        // --- NUEVO: Al cerrar el chat, reinicia el temporizador ---
        startInactivityTimer();
    });

    // Mensaje de bienvenida inicial
    const welcomeMessage = "¡Hola! Soy tu asistente virtual Kumpi. ¿En qué puedo ayudarte hoy sobre las prácticas profesionales?";
    addMessage(welcomeMessage, 'bot');
    
    // --- NUEVO: Inicia el temporizador de 5 segundos al cargar la página ---
    startInactivityTimer();
});