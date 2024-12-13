#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;

require './docker-lib.pl';
&ReadParse();

our (%in);

my $container = $in{'container'};
my $tab = $in{'tab'};

my ($code, $result) = get_container_attr($container, 'Name');
if ($code) {  # Bad container id
    ui_print_header(undef, text('view_container_title', "not found"), "", undef, undef, $in{'nonavlinks'});
    &ui_print_endpage(ui_alert_box($result, 'danger'), "Back", "/");
}

# Trim leading /
my $container_name = substr($result, 1);
ui_print_header(undef, text('view_container_title', $container_name), "", undef, undef, $in{'nonavlinks'});

my @tabs = ( [ 'log', &text('tab_log') ],
            [ 'inspect', &text('tab_inspect') ] );

print ui_tabs_start(\@tabs, 'log', $tab, 1);

# LOGS TAB
my ($max_lines) = $in{'max-lines'} || 50;
print ui_tabs_start_tab('mode', 'log');
my ($failed, $result) = container_logs($container, $max_lines, $in{'filter'} || "", $in{'basic-search'} || 0);
if ($failed) {
    print ui_alert_box($result, 'danger');
}

print &ui_form_start("container.cgi");
print &ui_hidden("container", $container),"\n";
print &ui_hidden("tab", "log"),"\n";
print "Auto refresh: " . &ui_select("auto-refresh", html_escape($in{'auto-refresh'}), ["Never", 3, 10, 30, 60]);
print "Show max lines: " . &ui_textbox("max-lines", html_escape($max_lines), 4);
print "Filter: " . &ui_textbox("filter", html_escape($in{'filter'}), 50);
print ui_checkbox("basic-search", 1, "Ignore special", html_escape($in{'basic-search'}));

print &ui_submit(text('label_refresh'));
print &ui_form_end(),"<br>\n";


print '
<script type="text/javascript">
{
    let refresher;
    let selectElement = document.querySelector("select[name=\'auto-refresh\']");

    function refreshContainerLog() {
        $.get("container.cgi?tab=log&container=' . urlize($container) . '", function (resp) {
            let d = $($.parseHTML(resp)).find("pre#container-log");
            $("pre#container-log").text(d.text());
        });
    }

    function setupRefresh(refreshPeriod) {
        if (refresher) {
            clearInterval(refresher);
            refresher = null;
        }

        if (refreshPeriod == null) {
            return;
        }

        refresher = setInterval(refreshContainerLog, refreshPeriod * 1000); // Sec to milli
    }

    selectElement.addEventListener("change", (event) => {
        let refreshPeriod = event.target.value == "Never" ? null : event.target.value;

        if (!window.jQuery) {
            console.log("No jQuery found");
            return;
        }

        setupRefresh(refreshPeriod);
    });
}
</script>';

print "<pre id='container-log'>" . $result . "</pre>";

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
