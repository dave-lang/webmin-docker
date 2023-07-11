#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;

require './docker-lib.pl';
&ReadParse();

our (%in);

my $container = $in{'container'};

ui_print_header("<tt>".&html_escape($container)."</tt>", text('index_title'), "", undef, undef, $in{'nonavlinks'});

my ($failed, $result) = inspect_container($container);
if ($failed) {
    &ui_print_endpage(ui_alert_box($failed, 'danger'), "Back", "/");
}

print &ui_form_start("inspect.cgi");
print &ui_hidden("container", $container),"\n";
print &ui_submit(text('label_refresh'));
print &ui_form_end(),"<br>\n";

print "<pre>" . $result . "</pre>";

&ui_print_footer("", text('index_return'));

# if using authentic theme, enable codemirror for readability
print "<script type='text/javascript'>if (window.viewer_init) { viewer_init() }; </script>";
