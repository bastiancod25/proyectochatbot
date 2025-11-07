function imprimir_variables_chatbot_footer() {
    ?>
    <script type="text/javascript">
        const chatbot_vars = {
            ajax_url: "<?php echo admin_url('admin-ajax.php'); ?>",
            nonce: "<?php echo wp_create_nonce('chatbot_nonce'); ?>"
        };
    </script>
    <?php
}
add_action('wp_footer', 'imprimir_variables_chatbot_footer', 5);