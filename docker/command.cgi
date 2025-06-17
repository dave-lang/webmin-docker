#!/usr/bin/perl
use strict;
use warnings;

require './docker-lib.pl';

&ReadParse();
&error_setup(text('command_err'));

our (%in);

my $command = $in{'c'};

my $err;
if ($command eq 'start') {
    $err = container_command($in{'container'}, 'start');
}

if ($command eq 'stop') {
    $err = container_command($in{'container'}, 'stop');
}

if ($command eq 'restart') {
   $err = container_command($in{'container'}, 'restart')
}

&error($err) if ($err);

&redirect("");