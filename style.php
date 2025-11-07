// Agregar CSS del chatbot UBB
function agregar_chatbot_css_ubb() {
    echo '<style>
.chat-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #0056b3;
    color: white;
    border: none;
    border-radius: 50px;
    padding: 15px 20px;
    font-size: 16px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    z-index: 1000;
}

.chatbot-container {
    position: fixed;
    bottom: 80px;
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
/* Estilo para el botón del chat */
#botonChat {
    width: 50px; /* Ajusta el ancho según sea necesario */
    height: 50px; /* Ajusta la altura según sea necesario */
    position: fixed; /* Mantiene el botón en una posición fija */
    bottom: 20px; /* Distancia desde la parte inferior */
    right: 20px; /* Distancia desde la derecha */
    z-index: 1000; /* Asegúrate de que esté por encima de otros elementos */
}
/* Estilo para el contenedor del chat */
#contenedorChat {
    position: fixed; /* Mantiene el contenedor en una posición fija */
    bottom: 80px; /* Ajusta la distancia desde la parte inferior */
    right: 20px; /* Ajusta la distancia desde la derecha */
    width: 300px; /* Ajusta el ancho según sea necesario */
    max-height: 400px; /* Limita la altura máxima */
    overflow-y: auto; /* Permite el desplazamiento si el contenido es demasiado grande */
    z-index: 1000; /* Asegúrate de que esté por encima de otros elementos */
}


@media (max-width: 600px) {
    #botonChat {
        width: 40px; /* Tamaño más pequeño en pantallas pequeñas */
        height: 40px;
    }

    #contenedorChat {
        width: 90%; /* Ancho más amplio en pantallas pequeñas */
        right: 5%; /* Ajusta la posición */
    }
}

</style>';
}
add_action('wp_head', 'agregar_chatbot_css_ubb');
