#!/usr/bin/perl

require 'docker-lib.pl';

ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);

my @containers = get_containers();
my @stats = get_stats();
my $num_containers = @containers;

print ui_subheading($text{'index_containers_title'} . " (" . $num_containers . ")");
print ui_columns_start(['name', 'label', 'running for', ' ', ' ', ' ' ]);

foreach my $u (@containers) {
    print ui_columns_row([
        html_escape($u->{'name'}),
        html_escape($u->{'image'}),
        html_escape($u->{'status'}),
        "<a href='command.cgi?c=start&container=" . urlize($u->{'name'}) . "'>Start</a>",
        "<a href='command.cgi?c=stop&container=" . urlize($u->{'name'}) . "'>Stop</a>",
        "<a href='command.cgi?c=restart&container=" . urlize($u->{'name'}) . "'>Restart</a>",
    ]);

    print ui_columns_row([
        @stats[$u->{'id'}]
    ]);
}
print ui_columns_end();

print ui_hr();

print ui_subheading($text{'index_stats_title'});
#print @stats['4e707a2c7215'];

ui_print_footer("/", $text{'index'});