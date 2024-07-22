#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;

require 'docker-lib.pl';

ui_print_header(undef, &text('index_title'), "", undef, undef, 1);

if (!&has_command('docker')) {
    &ui_print_endpage(&text('not_installed'));  #, "<tt>$config{'syslog_conf'}</tt>", "../config.cgi?$module_name"));
}

my @tabs = ( [ 'info', &text('tab_info') ],
            [ 'containers', &text('tab_containers') ] );

print ui_tabs_start(\@tabs, 'info', 'containers', 1);

# INFO TAB
print ui_tabs_start_tab('mode', 'info');
my($status_fail, $status) = get_status();
if ($status_fail) {
    print ui_alert_box($status_fail, 'danger');
} else {
    #print circular_grid($status);  # Ugly recursive output
    print "<pre>" . $status . "</pre>";
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
    print &ui_submit(text('label_refresh'));
    print &ui_form_end(),"<br>\n";

    print '<style>.panel-body tr td { padding: 5px 22px 7px 22px !important} </style>';
    print ui_columns_start([
        &text('label_name'), 
        &text('label_label'), 
        &text('label_running'), 
        &text('label_runningfor'), 
        &text('label_cpu'), 
        &text('label_mem'), 
        ' ' 
    ]);
    
    foreach my $u (@containers) {
        my ($status) = $u->{'status'};

        print ui_columns_row([
            html_escape($u->{'name'}),
            html_escape($u->{'image'}),
            get_status_icon($status),
            html_escape($status),
            html_escape($stats{$u->{'id'}}{'cpu'}),
            html_escape($stats{$u->{'id'}}{'memUsage'}) . " (" . html_escape($stats{$u->{'id'}}{'mem'}) . ")",
            get_container_up($status) ? 
                sprintf("<a href='command.cgi?c=stop&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_stop')) 
                : sprintf("<a href='command.cgi?c=start&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_start')),
            sprintf("<a href='command.cgi?c=restart&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_restart')),
            &ui_link('container.cgi?tab=log&container=' . urlize($u->{'id'}), &text('label_viewlog')),
            &ui_link('container.cgi?tab=inspect&container=' . urlize($u->{'id'}), &text('label_inspect'))
        ]);
    }
    print ui_columns_end();
}

print ui_tabs_end_tab('mode', 'containers');

print ui_tabs_end();

ui_print_footer("/", &text(('index')));

# if using authentic theme, enable codemirror for readability
print "<script type='text/javascript'>if (window.viewer_init) { viewer_init() }; </script>";

