#!/usr/bin/perl
$trust_unknown_referers = 1;
use strict;
use warnings;
use Data::Dumper;

require './docker-lib.pl';
&ReadParse();

our (%config, %in);

ui_print_header(undef, &text('index_title'), "", undef, 1, 1);

if (!&has_command('docker')) {
    &ui_print_endpage(&text('not_installed'));
}

if ($config{'docker_context'}) {
    print ui_alert_box('Using docker context: ' . 
        html_escape($config{'docker_context'}) . ' ' . &help_search_link("docker context", "google"), 'warn');
}

if ($in{'msg'}) {
    print ui_alert_box(html_escape($in{'msg'}), 'info');
}

if ($in{'err'}) {
    print ui_alert_box(html_escape($in{'err'}), 'danger');
}

my $active_tab = $in{'tab'} || 'info';

my @tabs = ( 
    [ 'info', &text('tab_info') ],
    [ 'containers', &text('tab_containers') ],
    [ 'images', &text('tab_images') ],
    [ 'compose', &text('tab_compose') ],
    [ 'storage', &text('tab_storage') ],
    [ 'registry', &text('tab_registry') ],
    [ 'security', &text('tab_security') ],
    [ 'contexts', &text('tab_contexts') ] 
);

print ui_tabs_start(\@tabs, 'info', $active_tab, 1);

# INFO TAB
print ui_tabs_start_tab('mode', 'info');
my($status_fail, $status) = get_status();
if ($status_fail) {
    print ui_alert_box($status, 'danger');
} else {
    print "<pre>" . html_escape($status) . "</pre>";
}
print ui_tabs_end_tab('mode', 'info');

# CONTAINERS TAB
print ui_tabs_start_tab('mode', 'containers');
my($fail, @containers) = get_containers();
my($stat_fail, %stats) = get_stats();

if ($fail) {
    print ui_alert_box($fail, 'danger');
} else {
    print &ui_form_start("");
    print &ui_hidden("tab", "containers");
    print &ui_submit(text('label_refresh'));
    print &ui_form_end(),"<br>\n";

    if (scalar(@containers) == 0) {
        print "No containers defined";
    } else {

    print '<style>
    .panel-body tr td { padding: 5px 10px 7px 10px !important} 
    .visible-xs,.visible-sm,.visible-md,.visible-lg { display: none !important }
    @media(max-width: 767px) { .visible-xs { display:block !important } }
    @media(max-width: 767px) { .hidden-xs { display:none !important } }
    @media(min-width: 768px) and (max-width:991px) { .hidden-sm { display:none !important } }
    @media(min-width: 992px) and (max-width:1199px) { .hidden-md { display:none !important } }
    @media(min-width: 1200px) { .hidden-lg { display:none !important } }
    </style>';
    
    print &ui_columns_start([
        &text('label_name'), 
        &text('label_label'),
        &text('label_runningfor'), 
        &text('label_cpu'), 
        &text('label_mem'), 
        ' ',
    ], undef, 0, [
        "", # name
        "class='hidden-xs hidden-sm'", #image
        "", # running
        "class='hidden-xs hidden-sm'", # CPU
        "class='hidden-xs'", # MEM
        "class='hidden-xs'" # actions
    ]);
    
    foreach my $u (@containers) {
        my $status = $u->{'status'};
        my $healthy = starts_with($status, "Up") && $status =~ /healthy/ ? "<span class='label label-success'>healthy</span> " : "";

        print ui_columns_row([
            &ui_link('container.cgi?tab=inspect&container=' . urlize($u->{'id'}), html_escape($u->{'name'})) . "<span class='display-none visible-xs visible-sm'>" . html_escape($u->{'image'}) . "</span>",
            html_escape($u->{'image'}),
            $healthy . get_status_icon($status) . " " . html_escape($status),
            html_escape($stats{$u->{'id'}}{'cpu'}),
            "<span class='display-none visible-xs visible-sm'>CPU: " . html_escape($stats{$u->{'id'}}{'cpu'}) . "<br /></span>" 
                . html_escape($stats{$u->{'id'}}{'memUsage'}) . " (" . html_escape($stats{$u->{'id'}}{'mem'}) . ")",
            (get_container_up($status) ? 
                sprintf("<a href='command.cgi?c=stop&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_stop')) . ' | ' . sprintf("<a href='command.cgi?c=restart&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_restart'))
                : sprintf("<a href='command.cgi?c=start&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_start'))) . ' | ' .
                &ui_link('container.cgi?tab=log&container=' . urlize($u->{'id'}), &text('label_viewlog')) . ' | ' .
                &ui_link('container.cgi?tab=exec&container=' . urlize($u->{'id'}), &text('label_exec'))
        ], [
            "", # name
            "class='hidden-xs hidden-sm'", #image
            "", # time
            "class='hidden-xs hidden-sm'", #CPU
            "class='hidden-xs'", #MEM
            "style='text-align: right; word-break: auto-phrase;' class='hidden-xs text-right'", #start/stop/restart
        ]);

        print ui_columns_row([
            "CPU: " . html_escape($stats{$u->{'id'}}{'cpu'}) . "<br />MEM: " 
                . html_escape($stats{$u->{'id'}}{'memUsage'}) . " (" . html_escape($stats{$u->{'id'}}{'mem'}) . ")",
            (get_container_up($status) ? 
                sprintf("<a href='command.cgi?c=stop&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_stop')) . ' | ' . sprintf("<a href='command.cgi?c=restart&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_restart'))
                : sprintf("<a href='command.cgi?c=start&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_start'))) . ' | ' .
                &ui_link('container.cgi?tab=log&container=' . urlize($u->{'id'}), &text('label_viewlog')) . ' | ' .
                &ui_link('container.cgi?tab=exec&container=' . urlize($u->{'id'}), &text('label_exec'))
        ], [
            "class='display-none visible-xs'", # Perf
            "style='word-break: auto-phrase;' class='display-none visible-xs'", #start/stop/restart
        ]);
    }
    print ui_columns_end();
    }
}

print ui_hr();
print &ui_form_start("command.cgi");
print &ui_hidden("c", "create");
print &ui_hidden("return_tab", "containers");
print &ui_table_start(text('label_create'));
print &ui_table_row(text('label_name'), &ui_textbox("name", "", 30));
print &ui_table_row(text('label_image'), &ui_textbox("image", "", 40));
print &ui_table_row(text('label_command'), &ui_textbox("cmd", "", 40));
print &ui_table_row(text('label_env'), &ui_textarea("env", "", 3, 60));
print &ui_table_row(text('label_ports'), &ui_textarea("ports", "", 3, 60));
print &ui_table_row(text('label_volumes'), &ui_textarea("volumes", "", 3, 60));
print &ui_table_row(text('label_restart'), &ui_select("restart", "", ["", "no", "on-failure", "always", "unless-stopped"]));
print &ui_table_row(text('label_health'), &ui_textbox("healthcheck", "", 40));
print &ui_table_end();
print &ui_submit(text('label_create'));
print &ui_form_end();

if (!$fail) {
    print ui_hr();
    print &ui_form_start("command.cgi");
    print &ui_hidden("c", "clone");
    print &ui_hidden("return_tab", "containers");
    print &ui_table_start(text('label_clone'));
    print &ui_table_row(text('label_source'), &ui_select("source", "", [ map { [ $_->{'name'}, $_->{'name'} ] } @containers ]));
    print &ui_table_row(text('label_name'), &ui_textbox("name", "", 30));
    print &ui_table_end();
    print &ui_submit(text('label_clone'));
    print &ui_form_end();
}
print ui_tabs_end_tab('mode', 'containers');

# IMAGES TAB
print ui_tabs_start_tab('mode', 'images');
my ($img_fail, @images) = list_images();
if ($img_fail) {
    print ui_alert_box($img_fail, 'danger');
} else {
    print &ui_columns_start([
        text('label_image'),
        text('label_size'),
        text('label_digest'),
        text('label_actions'),
    ]);

    foreach my $img (@images) {
        print ui_columns_row([
            html_escape($img->{'name'}),
            html_escape($img->{'size'}),
            html_escape($img->{'digest'}),
            sprintf("<a href='command.cgi?c=pull_image&image=%s&return_tab=images'>Pull</a> | <a href='command.cgi?c=push_image&image=%s&return_tab=images'>Push</a> | <a href='command.cgi?c=check_image&image=%s&return_tab=images'>Check updates</a>", urlize($img->{'name'}), urlize($img->{'name'}), urlize($img->{'name'}))
        ]);
    }
    print ui_columns_end();
}

print ui_hr();
print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "images");
print &ui_hidden("c", "pull_image");
print &ui_table_start(text('label_pull'));
print &ui_table_row(text('label_image'), &ui_textbox("image", "", 50));
print &ui_table_end();
print &ui_submit(text('label_pull'));
print &ui_form_end();

print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "images");
print &ui_hidden("c", "push_image");
print &ui_table_start(text('label_push'));
print &ui_table_row(text('label_image'), &ui_textbox("push_image", "", 50));
print &ui_table_end();
print &ui_submit(text('label_push'));
print &ui_form_end();

print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "images");
print &ui_hidden("c", "tag_image");
print &ui_table_start(text('label_tag'));
print &ui_table_row(text('label_from'), &ui_textbox("from", "", 30));
print &ui_table_row(text('label_to'), &ui_textbox("to", "", 30));
print &ui_table_end();
print &ui_submit(text('label_tag'));
print &ui_form_end();

print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "images");
print &ui_hidden("c", "build_image");
print &ui_table_start(text('label_build_tag'));
print &ui_table_row(text('label_tag'), &ui_textbox("tag", "", 30));
print &ui_table_row(text('label_dockerfile'), &ui_textarea("dockerfile", "", 6, 70));
print &ui_table_end();
print &ui_submit(text('label_build_tag'));
print &ui_form_end();

print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "images");
print &ui_hidden("c", "prune_images");
print &ui_submit(text('label_prune_images'));
print &ui_form_end();
print ui_tabs_end_tab('mode', 'images');

# COMPOSE TAB
print ui_tabs_start_tab('mode', 'compose');
print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "compose");
print &ui_hidden("c", "compose");
print &ui_table_start(text('label_compose'));
print &ui_table_row(text('label_compose_file'), &ui_textbox("compose_file", $config{'compose_file'} || "docker-compose.yml", 60));
print &ui_table_row(text('label_compose_cmd'), &ui_select("compose_action", "", ["up -d", "down", "ps", "logs"]));
print &ui_table_end();
print &ui_submit(text('label_run_compose'));
print &ui_form_end();
print ui_tabs_end_tab('mode', 'compose');

# STORAGE TAB
print ui_tabs_start_tab('mode', 'storage');
my ($vol_fail, @vols) = list_volumes();
my ($net_fail, @nets) = list_networks();
if ($vol_fail) { print ui_alert_box($vol_fail, 'danger'); }
else {
    print ui_subheading(text('label_volumes'));
    print &ui_columns_start([text('label_name'), text('label_driver'), text('label_mount'), text('label_actions')]);
    foreach my $v (@vols) {
        print ui_columns_row([
            html_escape($v->{'name'}),
            html_escape($v->{'driver'}),
            html_escape($v->{'mountpoint'}),
            sprintf("<a href='command.cgi?c=inspect_volume&volume=%s&return_tab=storage'>Inspect</a>", urlize($v->{'name'}))
        ]);
    }
    print ui_columns_end();
}

print ui_hr();
if ($net_fail) { print ui_alert_box($net_fail, 'danger'); }
else {
    print ui_subheading(text('label_networks'));
    print &ui_columns_start([text('label_name'), text('label_driver'), text('label_scope'), text('label_actions')]);
    foreach my $n (@nets) {
        print ui_columns_row([
            html_escape($n->{'name'}),
            html_escape($n->{'driver'}),
            html_escape($n->{'scope'}),
            sprintf("<a href='command.cgi?c=inspect_network&network=%s&return_tab=storage'>Inspect</a>", urlize($n->{'name'}))
        ]);
    }
    print ui_columns_end();
}

print ui_hr();
print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "storage");
print &ui_hidden("c", "volume_create");
print &ui_table_start(text('label_volume_create'));
print &ui_table_row(text('label_name'), &ui_textbox("volume_name", "", 30));
print &ui_table_row(text('label_driver'), &ui_textbox("volume_driver", "", 20));
print &ui_table_end();
print &ui_submit(text('label_create'));
print &ui_form_end();

print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "storage");
print &ui_hidden("c", "network_create");
print &ui_table_start(text('label_network_create'));
print &ui_table_row(text('label_name'), &ui_textbox("network_name", "", 30));
print &ui_table_row(text('label_driver'), &ui_textbox("network_driver", "", 20));
print &ui_table_end();
print &ui_submit(text('label_create'));
print &ui_form_end();

print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "storage");
print &ui_hidden("c", "volume_prune");
print &ui_submit(text('label_prune_volumes'));
print &ui_form_end();

print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "storage");
print &ui_hidden("c", "network_prune");
print &ui_submit(text('label_prune_networks'));
print &ui_form_end();
print ui_tabs_end_tab('mode', 'storage');

# REGISTRY TAB
print ui_tabs_start_tab('mode', 'registry');
print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "registry");
print &ui_hidden("c", "registry_login");
print &ui_table_start(text('label_registry'));
print &ui_table_row(text('label_registry_server'), &ui_textbox("registry_server", $config{'registry_server'}, 40));
print &ui_table_row(text('label_registry_user'), &ui_textbox("registry_user", $config{'registry_user'}, 30));
print &ui_table_row(text('label_registry_pass'), &ui_password("registry_pass", $config{'registry_pass'}, 30));
print &ui_table_end();
print &ui_submit(text('label_save_login'));
print &ui_form_end();
print ui_tabs_end_tab('mode', 'registry');

# SECURITY TAB
print ui_tabs_start_tab('mode', 'security');
print &ui_form_start("command.cgi");
print &ui_hidden("return_tab", "security");
print &ui_hidden("c", "scan_image");
print &ui_table_start(text('label_scan'));
print &ui_table_row(text('label_image'), &ui_textbox("image", "", 50));
print &ui_table_end();
print &ui_submit(text('label_scan'));
print &ui_form_end();
print ui_tabs_end_tab('mode', 'security');

# CONTEXT TAB
print ui_tabs_start_tab('mode', 'contexts');
my ($ctx_fail, @contexts) = get_contexts();
if ($ctx_fail) {
    print ui_alert_box($ctx_fail, 'danger');
} else {
    print &ui_form_start("command.cgi");
    print &ui_hidden("return_tab", "contexts");
    print &ui_hidden("c", "set_context");
    print &ui_table_start(text('label_context'));
    print &ui_table_row(text('label_current_context'), $config{'docker_context'} || 'default');
    print &ui_table_row(text('label_available_contexts'), &ui_select("context", $config{'docker_context'}, [ map { [ $_->{'Name'}, $_->{'Name'} . ($_->{'Current'} ? " (current)" : "") ] } @contexts ]));
    print &ui_table_end();
    print &ui_submit(text('label_switch_context'));
    print &ui_form_end();
}
print ui_tabs_end_tab('mode', 'contexts');

print ui_tabs_end();

ui_print_footer("/", &text(('index')));

print "<script type='text/javascript'>if (window.viewer_init) { viewer_init() }; </script>";

