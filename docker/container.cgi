#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;

require './docker-lib.pl';
&ReadParse();

our (%in);

my $container = $in{'container'};
my $tab = $in{'tab'};

my ($code, $container_name) = get_container_attr($container, 'Name');
if ($code) {  # Bad container id
    ui_print_header(undef, text('view_container_title', "not found"), "", undef, undef, $in{'nonavlinks'});
    &ui_print_endpage(ui_alert_box($code, 'danger'), "Back", "/");
}

# Trim leading /
$container_name = substr $container_name, 1;
ui_print_header(undef, text('view_container_title', $container_name), "", undef, undef, $in{'nonavlinks'});

my @tabs = ( [ 'log', &text('tab_log') ],
            [ 'inspect', &text('tab_inspect') ] );

print ui_tabs_start(\@tabs, 'log', $tab, 1);

# LOGS TAB
print ui_tabs_start_tab('mode', 'log');
my ($failed, $result) = container_logs($container);
if ($failed) {
    print ui_alert_box($failed, 'danger');
} else {
    print &ui_form_start("container.cgi");
    print &ui_hidden("container", $container),"\n";
    print &ui_hidden("tab", "log"),"\n";
    print &ui_submit(text('label_refresh'));
    print &ui_form_end(),"<br>\n";

    print "<pre>" . $result . "</pre>";
}
print ui_tabs_end_tab('mode', 'log');

# INSPECT TAB
print ui_tabs_start_tab('mode', 'inspect');
my ($failedB, $resultB) = inspect_container($container);
if ($failedB) {
    print ui_alert_box($failedB, 'danger');
} else {
    print "<pre class='comment'>" . $resultB . "</pre>";
}
print ui_tabs_end_tab('mode', 'inspect');

print ui_tabs_end();

&ui_print_footer("", text('index_return'));

# if using authentic theme, enable codemirror for readability
print "<script type='text/javascript'>if (window.viewer_init) { viewer_init() }; </script>";
