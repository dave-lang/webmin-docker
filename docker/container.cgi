#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;

require './docker-lib.pl';
&ReadParse();

our (%in);

my $container = $in{'container'};
my $tab = $in{'tab'};
my $action = $in{'action'};

my ($code, $result) = get_container_attr($container, 'Name');
if ($code) {  # Bad container id
    ui_print_header(undef, text('view_container_title', "not found"), "", undef, undef, $in{'nonavlinks'});
    &ui_print_endpage(ui_alert_box($result, 'danger'), "Back", "/");
}

# Trim leading /
my $container_name = substr($result, 1);
ui_print_header(undef, text('view_container_title', $container_name), "", undef, undef, $in{'nonavlinks'});

my @tabs = ( [ 'log', &text('tab_log') ],
            [ 'inspect', &text('tab_inspect') ],
            [ 'exec', &text('tab_exec') ] );

print ui_tabs_start(\@tabs, 'log', $tab, 1);

# LOGS TAB
my ($max_lines) = $in{'max-lines'} || 50;
print ui_tabs_start_tab('mode', 'log');
my ($failed, $log_result) = container_logs($container, $max_lines, $in{'filter'} || "", $in{'basic-search'} || 0);
if ($failed) {
    print ui_alert_box($log_result, 'danger');
}

if ($in{'download'}) {
    print "Content-type: text/plain\n";
    print "Content-Disposition: attachment; filename=\"$container_name.log\"\n\n";
    print $log_result;
    exit;
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

print "<p><a href='container.cgi?tab=log&download=1&container=" . urlize($container) . "'>" . text('label_download_log') . "</a></p>";

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

print "<pre id='container-log'>" . $log_result . "</pre>";

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

# EXEC TAB
print ui_tabs_start_tab('mode', 'exec');
if ($action && $action eq 'exec') {
    my ($ecode, $exec_result) = exec_in_container($container, $in{'cmd'});
    if ($ecode) {
        print ui_alert_box($exec_result, 'danger');
    } else {
        print "<pre class='comment'>" . html_escape($exec_result) . "</pre>";
    }
}

if ($action && $action eq 'copy_to') {
    my ($ccode, $cresult) = copy_to_container($in{'host_path'}, $container, $in{'target_path'});
    if ($ccode) { print ui_alert_box($cresult, 'danger'); }
    else { print ui_alert_box(text('label_copy_ok'), 'info'); }
}

if ($action && $action eq 'copy_from') {
    my ($ccode, $cresult) = copy_from_container($container, $in{'source_path'}, $in{'host_dest'});
    if ($ccode) { print ui_alert_box($cresult, 'danger'); }
    else { print ui_alert_box(text('label_copy_ok'), 'info'); }
}

print &ui_form_start("container.cgi");
print &ui_hidden("container", $container);
print &ui_hidden("tab", "exec");
print &ui_hidden("action", "exec");
print &ui_table_start(text('label_exec'));
print &ui_table_row(text('label_command'), &ui_textbox("cmd", html_escape($in{'cmd'}), 50));
print &ui_table_end();
print &ui_submit(text('label_run'));
print &ui_form_end();

print ui_hr();
print &ui_form_start("container.cgi");
print &ui_hidden("container", $container);
print &ui_hidden("tab", "exec");
print &ui_hidden("action", "copy_to");
print &ui_table_start(text('label_copy_to'));
print &ui_table_row(text('label_host_path'), &ui_textbox("host_path", "", 40));
print &ui_table_row(text('label_target_path'), &ui_textbox("target_path", "/tmp", 30));
print &ui_table_end();
print &ui_submit(text('label_copy'));
print &ui_form_end();

print ui_hr();
print &ui_form_start("container.cgi");
print &ui_hidden("container", $container);
print &ui_hidden("tab", "exec");
print &ui_hidden("action", "copy_from");
print &ui_table_start(text('label_copy_from'));
print &ui_table_row(text('label_source_path'), &ui_textbox("source_path", "/", 30));
print &ui_table_row(text('label_host_dest'), &ui_textbox("host_dest", "/tmp", 30));
print &ui_table_end();
print &ui_submit(text('label_copy'));
print &ui_form_end();

print ui_tabs_end_tab('mode', 'exec');

print ui_tabs_end();

&ui_print_footer("", text('index_return'));

# if using authentic theme, enable codemirror for readability
print "<script type='text/javascript'>if (window.viewer_init) { viewer_init() }; </script>";
