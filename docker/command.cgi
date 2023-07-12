#!/usr/bin/perl
use strict;
use warnings;

require './docker-lib.pl';
#ui_print_header(undef, &text('index_title'), "", undef, 1, 1);
&ReadParse();
&error_setup(text('command_err'));

our (%in);

my $command = $in{'c'};

my $err;
if ($command == 'start') {
    $err = container_command($in{'container'}, 'start');
}

if ($command == 'stop') {
    $err = container_command($in{'container'}, 'stop');
}

if ($command == 'restart') {
   $err = container_command($in{'container'}, 'restart')
}

&error($err) if ($err);

&webmin_log(ucfirst($command), 'docker container', $in{'container'});
&redirect("");