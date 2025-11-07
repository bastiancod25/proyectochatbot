// Registra la función para que pueda ser llamada por AJAX y por el Webhook de Dialogflow
add_action('wp_ajax_enviar_pregunta_chatbot', 'dialogflow_webhook_handler');
add_action('wp_ajax_nopriv_enviar_pregunta_chatbot', 'dialogflow_webhook_handler');

function dialogflow_webhook_handler() {
    // --- CONFIGURACIÓN ---
    $key_file_path = get_stylesheet_directory() . '/keys/bottesis-af40245ebb0b.json'; 
    $project_id = 'bottesis';
    // --- FIN DE LA CONFIGURACIÓN ---

    // Obtener la pregunta y la sesión del usuario desde nuestro chat en JS
    $user_question = isset($_POST['question']) ? sanitize_text_field($_POST['question']) : null;
    $session_id = isset($_POST['session']) ? sanitize_text_field($_POST['session']) : null;

    try {
        // 1. Obtener un token de acceso de Google (usando la función auxiliar de abajo)
        $access_token = get_google_dialogflow_access_token_v2($key_file_path);

        // 2. Preparar y enviar la petición a la API de Dialogflow
        $dialogflow_url = "https://dialogflow.googleapis.com/v2/projects/{$project_id}/agent/sessions/{$session_id}:detectIntent";
        $request_body = [
            'queryInput' => [
                'text' => [
                    'text' => $user_question,
                    'languageCode' => 'es'
                ]
            ]
        ];
        
        $response = wp_remote_post($dialogflow_url, [
            'headers' => [
                'Authorization' => 'Bearer ' . $access_token,
                'Content-Type'  => 'application/json; charset=utf-8'
            ],
            'body' => json_encode($request_body)
        ]);

        if (is_wp_error($response)) {
            throw new Exception('Error en la conexión con la API de Dialogflow: ' . $response->get_error_message());
        }

        $response_body = json_decode(wp_remote_retrieve_body($response), true);

        // 3. Revisar si Dialogflow necesita que le demos una respuesta (Fulfillment)
        $intent_name = $response_body['queryResult']['intent']['displayName'];
        $parameters = $response_body['queryResult']['parameters'];
        $bot_response_text = $response_body['queryResult']['fulfillmentText']; // Respuesta por defecto de Dialogflow

        // --- NUEVA LÓGICA CONDICIONAL ---
        // Si el intent es "Horas_creditos" y tenemos un parámetro "carrera"
        if ($intent_name === 'Horas_creditos' && !empty($parameters['carrera'])) {
            $carrera = $parameters['carrera'];
            
            if ($carrera === 'Ingeniería Civil Industrial') {
                $bot_response_text = "Para Ingeniería Civil Industrial, la práctica I tiene 4 créditos (120 horas) y la práctica II tiene 4 créditos (120 horas).";
            } elseif ($carrera === 'Ingeniería Civil Mecánica') {
                $bot_response_text = "Para Ingeniería Civil Mecánica, la práctica II tiene 8 créditos (240 horas).";
            } elseif ($carrera === 'Ingeniería Civil Eléctrica') {
                $bot_response_text = "Para Ingeniería Civil Eléctrica, la práctica II tiene 6 créditos (180 horas).";
            } elseif ($carrera === 'Ingeniería Civil en Automatización') {
                $bot_response_text = "Para Ingeniería Civil en Automatización, la práctica II tiene 6 créditos (180 horas).";
            } elseif ($carrera === 'Ingeniería Civil Química') {
                $bot_response_text = "Para Ingeniería Civil Química, la práctica II tiene 6 créditos (180 horas).";
            } elseif ($carrera === 'Ingeniería Civil') {
                $bot_response_text = "Para Ingeniería Civil, la práctica I tiene 3 créditos (180 horas) y la práctica II tiene 6 créditos (180 horas).";
            }
            // Si no coincide con ninguno, se usará la respuesta por defecto de Dialogflow.
        }
        
        // 4. Devolver la respuesta final al JavaScript del frontend
        wp_send_json_success(['reply' => $bot_response_text]);

    } catch (Exception $e) {
        wp_send_json_error(['message' => 'Error en el servidor: ' . $e->getMessage()]);
    }
    
    wp_die();
}

/**
 * Función auxiliar para obtener un token de acceso de Google (no necesita cambios).
 */
function get_google_dialogflow_access_token_v2($key_file_path) {
    if (!file_exists($key_file_path) || !is_readable($key_file_path)) {
        throw new Exception('No se pudo encontrar o leer el archivo de clave JSON.');
    }
    $key_file_data = json_decode(file_get_contents($key_file_path), true);
    if (!$key_file_data) {
        throw new Exception('El archivo de clave JSON está malformado o vacío.');
    }

    $header = [ 'alg' => 'RS256', 'typ' => 'JWT' ];
    $header_encoded = rtrim(strtr(base64_encode(json_encode($header)), '+/', '-_'), '=');

    $claim = [
        'iss'   => $key_file_data['client_email'],
        'scope' => 'https://www.googleapis.com/auth/dialogflow',
        'aud'   => 'https://oauth2.googleapis.com/token',
        'exp'   => time() + 3600,
        'iat'   => time()
    ];
    $claim_encoded = rtrim(strtr(base64_encode(json_encode($claim)), '+/', '-_'), '=');

    $signature = '';
    openssl_sign($header_encoded . '.' . $claim_encoded, $signature, $key_file_data['private_key'], 'SHA256');
    $signature_encoded = rtrim(strtr(base64_encode($signature), '+/', '-_'), '=');

    $jwt = $header_encoded . '.' . $claim_encoded . '.' . $signature_encoded;

    $response = wp_remote_post('https://oauth2.googleapis.com/token', [
        'body' => [
            'grant_type' => 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion'  => $jwt
        ]
    ]);

    if (is_wp_error($response)) {
        throw new Exception('No se pudo obtener el token de acceso de Google.');
    }

    $response_body = json_decode(wp_remote_retrieve_body($response), true);
    return $response_body['access_token'];
}