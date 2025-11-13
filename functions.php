<?php
/*
 * All the functions are in the PHP files in the `functions/` folder.
 */

if ( ! defined('ABSPATH') ) {
  exit;
}
require get_template_directory() . '/functions/cleanup.php';
require get_template_directory() . '/functions/setup.php';
require get_template_directory() . '/functions/enqueues.php';
require get_template_directory() . '/functions/action-hooks.php';
require get_template_directory() . '/functions/navbar.php';
require get_template_directory() . '/functions/dimox-breadcrumbs.php';
require get_template_directory() . '/functions/widgets.php';
require get_template_directory() . '/functions/search-widget.php';
require get_template_directory() . '/functions/index-pagination.php';
require get_template_directory() . '/functions/split-post-pagination.php';

// require get_template_directory() . '/functions/custom-type-practice-bot.php';
require get_template_directory() . '/functions/custom-type-event.php';
require get_template_directory() . '/functions/custom-type-practice.php';
require get_template_directory() . '/functions/custom-type-post.php';
require get_template_directory() . '/functions/custom-type-sponsor.php';
require get_template_directory() . '/functions/custom-type-testimonial.php';

require get_template_directory() . '/functions/customizer.php';