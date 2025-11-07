// Agregar CSS del chatbot UBB
function agregar_chatbot_css_ubb() {
// Usamos la sintaxis Heredoc (<<<CSS ... CSS;) para imprimir el bloque de CSS
// Esto evita errores de comillas
echo <<<CSS
<style>

/* --- Animación de vibración para el botón --- */
@keyframes vibrate-pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 8px rgba(0, 123, 255, 0.5);
  }
  50% {
    transform: scale(1.08);
    box-shadow: 0 0 20px rgba(0, 123, 255, 1);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 8px rgba(0, 123, 255, 0.5);
  }
}

/* --- Estilos del nuevo botón del zorro --- */
#chat-toggle-btn {
  
  /* URL de tu imagen del zorro */
  background-image: url("http://practicas.fi.ubiobio.cl/wp-content/uploads/2025/11/kumpi_chat.png"); 
  
  background-size: cover;
  background-position: center;
  width: 70px;
  height: 70px;
  border-radius: 50%; /* Redondo */
  border: none;
  padding: 0;
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 998;
  cursor: pointer;
  box-shadow: 0 0 8px rgba(0, 123, 255, 0.5);
  transition: transform 0.2s ease;
  
  /* Aplicar la animación */
  animation: vibrate-pulse 2.5s infinite ease-in-out;
}

#chat-toggle-btn:hover {
  transform: scale(1.15);
  animation-play-state: paused;
}

/* --- ESTILO PARA LA BURBUJA DE "HEY!" --- */

.chat-ping-bubble {
  /* Oculto por defecto */
  display: block;
  opacity: 0;
  pointer-events: none; /* No se puede hacer clic en él */

  /* Posición */
  position: fixed;
  bottom: 100px; /* Justo encima del botón del zorro (70px + 20px + 10px) */
  right: 20px;
  z-index: 997; /* Debajo del botón por si acaso */
  
  /* Estilo de burbuja */
  background-color: white;
  color: #333;
  padding: 10px 15px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  font-size: 15px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  
  /* Transición */
  transform: translateY(10px);
  transition: all 0.3s ease-out;
}

/* Triángulo/flecha de la burbuja */
.chat-ping-bubble::after {
  content: '';
  position: absolute;
  bottom: -8px; /* Apunta hacia abajo */
  right: 25px; /* Alineado con el botón */
  width: 0; 
  height: 0; 
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid white; /* Triángulo hecho con bordes */
}

/* Clase que le pondrá el JavaScript para mostrarla */
.chat-ping-bubble.show {
  opacity: 1;
  transform: translateY(0);
}

/* --- ESTILOS DE LA VENTANA DEL CHAT --- */
.chatbot-container {
    position: fixed;
    bottom: 100px; /* Ajustado para que no choque con el nuevo botón */
    right: 20px;
    width: 350px;
    height: 500px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 999;
    transform: translateY(100%);
    opacity: 0;
    transition: transform 0.3s ease-out, opacity 0.3s ease-out;
    pointer-events: none;
}

.chatbot-container.open {
    transform: translateY(0);
    opacity: 1;
    pointer-events: auto;
}

.chatbot-header {
    background-color: #0056b3;
    color: white;
    padding: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}

.header-logo {
    height: 40px;
    width: auto;
    margin-right: 10px;
}

.header-info {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.header-title {
    font-weight: bold;
    font-size: 1.1em;
}

.header-status {
    font-size: 0.8em;
    opacity: 0.8;
}

.close-button {
    background: none;
    border: none;
    color: white;
    font-size: 1.5em;
    cursor: pointer;
    padding: 0 5px;
}

.chatbot-body {
    flex-grow: 1;
    padding: 15px;
    overflow-y: auto;
    background-color: #e5ddd5;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.message {
    max-width: 80%;
    padding: 10px 12px;
    border-radius: 8px;
    word-wrap: break-word;
}

.user-message {
    align-self: flex-end;
    background-color: #dcf8c6;
    color: #333;
}

.bot-message {
    align-self: flex-start;
    background-color: #ffffff;
    color: #333;
    border: 1px solid #e0e0e0;
}

.chatbot-footer {
    display: flex;
    padding: 10px 15px;
    border-top: 1px solid #eee;
    background-color: #f0f0f0;
}

.user-input {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 20px;
    margin-right: 10px;
    font-size: 1em;
}

.send-button {
    background-color: #0056b3;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 10px 15px;
    cursor: pointer;
    font-size: 1em;
}

/* --- VISTA EN MÓVILES --- */
@media (max-width: 600px) {
    #chat-toggle-btn {
        width: 60px; /* Botón un poco más pequeño en móviles */
        height: 60px;
    }
    
    .chat-ping-bubble {
        bottom: 90px; /* Ajustar posición en móviles */
    }

    .chatbot-container {
        width: 100%; /* Ancho completo en móviles */
        height: 100%; /* Alto completo en móviles */
        right: 0;
        bottom: 0;
        border-radius: 0;
    }
}
</style>
CSS;
}
add_action('wp_head', 'agregar_chatbot_css_ubb');
