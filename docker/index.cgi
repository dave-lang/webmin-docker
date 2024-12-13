#!/usr/bin/perl
$trust_unknown_referers = 1;
use strict;
use warnings;
use Data::Dumper;

require './docker-lib.pl';

ui_print_header(undef, &text('index_title'), "", undef, 1, 1);

if (!&has_command('docker')) {
    &ui_print_endpage(&text('not_installed'));  #, "<tt>$config{'syslog_conf'}</tt>", "../config.cgi?$module_name"));
}

our (%config);

if ($config{'docker_context'}) {
    print ui_alert_box('Using docker context: ' . 
        html_escape($config{'docker_context'}) . ' ' . &help_search_link("docker context", "google"), 'warn');
}

my @tabs = ( [ 'info', &text('tab_info') ],
            [ 'containers', &text('tab_containers') ] );

print ui_tabs_start(\@tabs, 'info', 'containers', 1);

# INFO TAB
print ui_tabs_start_tab('mode', 'info');
my($status_fail, $status) = get_status();
if ($status_fail) {
    print ui_alert_box($status, 'danger');
} else {
    #print circular_grid($status);  # Ugly recursive output
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
    print &ui_submit(text('label_refresh'));
    print &ui_form_end(),"<br>\n";

    if (scalar(@containers) == 0) {
    print "No containers defined";
    } else {

    # Provide some basic responsive support across all themes
    print '<style>
    .panel-body tr td { padding: 5px 10px 7px 10px !important} 
    
    .visible-xs,.visible-sm,.visible-md,.visible-lg {
        display: none !important
    }

    @media(max-width: 767px) {
        .visible-xs {
            display:block !important
        }
    }
    @media(max-width: 767px) {
        .hidden-xs {
            display:none !important
        }
    }

    @media(min-width: 768px) and (max-width:991px) {
        .hidden-sm {
            display:none !important
        }
    }

    @media(min-width: 992px) and (max-width:1199px) {
        .hidden-md {
            display:none !important
        }
    }

    @media(min-width: 1200px) {
        .hidden-lg {
            display:none !important
        }
    }</style>';
    
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
        my ($status) = $u->{'status'};

        # columns will be consolidated/hidden across various screen sizes
        print ui_columns_row([
            &ui_link('container.cgi?tab=inspect&container=' . urlize($u->{'id'}), html_escape($u->{'name'})) . "<span class='display-none visible-xs visible-sm'>" . html_escape($u->{'image'}) . "</span>",
            html_escape($u->{'image'}),
            get_status_icon($status) . " " . html_escape($status),
            html_escape($stats{$u->{'id'}}{'cpu'}),
            "<span class='display-none visible-xs visible-sm'>CPU: " . html_escape($stats{$u->{'id'}}{'cpu'}) . "<br /></span>" 
                . html_escape($stats{$u->{'id'}}{'memUsage'}) . " (" . html_escape($stats{$u->{'id'}}{'mem'}) . ")",
            (get_container_up($status) ? 
                sprintf("<a href='command.cgi?c=stop&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_stop')) . ' | ' . sprintf("<a href='command.cgi?c=restart&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_restart'))
                : sprintf("<a href='command.cgi?c=start&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_start'))) . ' | ' .
                &ui_link('container.cgi?tab=log&container=' . urlize($u->{'id'}), &text('label_viewlog'))
        ], [
            "", # name
            "class='hidden-xs hidden-sm'", #image
            "", # time
            "class='hidden-xs hidden-sm'", #CPU
            "class='hidden-xs'", #MEM
            "style='text-align: right; word-break: auto-phrase;' class='hidden-xs text-right'", #start/stop/restart
        ]);

        # This row is shown on xs-devices only
        print ui_columns_row([
            "CPU: " . html_escape($stats{$u->{'id'}}{'cpu'}) . "<br />MEM: " 
                . html_escape($stats{$u->{'id'}}{'memUsage'}) . " (" . html_escape($stats{$u->{'id'}}{'mem'}) . ")",
            (get_container_up($status) ? 
                sprintf("<a href='command.cgi?c=stop&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_stop')) . ' | ' . sprintf("<a href='command.cgi?c=restart&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_restart'))
                : sprintf("<a href='command.cgi?c=start&container=%s'>%s</a>", urlize($u->{'name'}), &text('label_start'))) . ' | ' .
                &ui_link('container.cgi?tab=log&container=' . urlize($u->{'id'}), &text('label_viewlog'))
        ], [
            "class='display-none visible-xs'", # Perf
            "style='word-break: auto-phrase;' class='display-none visible-xs'", #start/stop/restart
        ]);

        

    }
    print ui_columns_end();
    }
}

print ui_tabs_end_tab('mode', 'containers');

print ui_tabs_end();

ui_print_footer("/", &text(('index')));

# if using authentic theme, enable codemirror for readability
print "<script type='text/javascript'>if (window.viewer_init) { viewer_init() }; </script>";

