#!/usr/bin/perl

require 'docker-lib.pl';

ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);

my($one, $container, $fail) = get_containers();

#$conf = get_foobar_config();
#$dir = find($conf, "root");
print "TEst<p>\n";
print $one,"<p>\n";
print $containers,"<p>\n";
print $fail,"<p>\n";

ui_print_footer("/", $text{'index'});