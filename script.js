document.addEventListener("DOMContentLoaded", function() {
    // --- Referencias a los elementos del DOM (esto no cambia) ---
    const chatbotContainer = document.getElementById("chatbotContainer");
    const openChatBtn = document.getElementById("openChatBtn");
    const closeChatBtn = document.getElementById("closeChatBtn");
    const chatbotBody = document.getElementById("chatbotBody");
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");

    // --- NUEVO: ID de sesión único para la conversación ---
    // Dialogflow lo usa para recordar el contexto de lo que se está hablando.
    const sessionId = 'session_' + Date.now() + Math.random().toString(36).substring(2);

    // --- LÓGICA ANTIGUA ELIMINADA ---
    // La variable 'baseConocimiento' y la función 'obtenerRespuesta' ya no existen.

    // La función para añadir mensajes al chat no cambia.
    function addMessage(sender, message) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.classList.add(sender === "user" ? "user-message" : "bot-message");
        messageElement.innerHTML = message.replace(/\n/g, "<br>");
        chatbotBody.appendChild(messageElement);
        chatbotBody.scrollTop = chatbotBody.scrollHeight;
    }

    // --- FUNCIÓN PRINCIPAL MODIFICADA ---
    // Ahora es 'async' y usa 'fetch' para hablar con el backend de WordPress.
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        addMessage("user", message);
        userInput.value = "";
        
        // Pequeña mejora: Muestra que el bot está "pensando"
        userInput.setAttribute("placeholder", "Escribiendo...");
        userInput.disabled = true;
        sendButton.disabled = true;

        // Preparamos los datos para enviar a nuestro backend (el snippet PHP)
        const formData = new FormData();
        formData.append('action', 'enviar_pregunta_chatbot'); // El "departamento" que llamamos
        formData.append('question', message);
        formData.append('session', sessionId);
        formData.append('security', chatbot_vars.nonce); // El token de seguridad

        try {
            // Hacemos la llamada al "recepcionista" de WordPress (admin-ajax.php)
            const response = await fetch(chatbot_vars.ajax_url, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            // Si la respuesta del backend fue exitosa, mostramos la réplica de Dialogflow
            if (data.success) {
                addMessage("bot", data.data.reply);
            } else {
                addMessage("bot", "Lo siento, ocurrió un error al procesar tu pregunta. Inténtalo de nuevo.");
                console.error('Error del backend:', data.data.message);
            }

        } catch (error) {
            addMessage("bot", "No pude conectarme con el servidor. Por favor, revisa tu conexión a internet.");
            console.error('Error de red:', error);
        } finally {
            // Reactivamos el campo de texto, haya funcionado o no
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.setAttribute("placeholder", "Escribe tu pregunta...");
            userInput.focus();
        }
    }

    // --- Event Listeners (esto no cambia) ---
    openChatBtn.addEventListener("click", function() {
        chatbotContainer.classList.add("open");
        if (chatbotBody.children.length === 0) {
            addMessage("bot", "¡Hola! Soy tu asistente virtual Kumpi. ¿En qué puedo ayudarte hoy sobre las prácticas profesionales?");
        }
    });

    closeChatBtn.addEventListener("click", function() {
        chatbotContainer.classList.remove("open");
    });

    sendButton.addEventListener("click", sendMessage);

    userInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});