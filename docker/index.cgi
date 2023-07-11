#!/usr/bin/perl
# use strict;
use warnings;
use Data::Dumper;

require 'docker-lib.pl';

my %text;

ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);

my($status_fail, @status) = get_status();
if ($status_fail) {
    print ui_alert_box($fail, 'danger');
} else {
    print Dumper($status);
}


my($fail, @containers) = get_containers();
my($stat_fail, %stats) = get_stats();
# print(get_status());

print Dumper(\%stats);

print ui_subheading($text{'index_containers_title'});
if ($fail) {
    print ui_alert_box($fail, 'danger');
} else {
    print ui_columns_start(['name', 'label', 'running for', ' ', ' ', ' ' ]);
    foreach my $u (@containers) {
        my $container_stats = \%stats{$u->{'id'}};
        print ui_columns_row([
            html_escape($u->{'name'}),
            html_escape($u->{'image'}),
            html_escape($u->{'status'}),
            html_escape($container_stats->{'cpu'}),
            html_escape($container_stats->{'mem'}),
            "<a href='command.cgi?c=start&container=" . urlize($u->{'name'}) . "'>Start</a>",
            "<a href='command.cgi?c=stop&container=" . urlize($u->{'name'}) . "'>Stop</a>",
            "<a href='command.cgi?c=restart&container=" . urlize($u->{'name'}) . "'>Restart</a>",
        ]);
    }
    print ui_columns_end();
}

print ui_hr();

print ui_subheading($text{'index_stats_title'});

if ($fail) {
    print ui_alert_box($stat_fail, 'danger');
} else {
    print $stats, "T";
}

ui_print_footer("/", $text{'index'});