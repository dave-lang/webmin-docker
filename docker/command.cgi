#!/usr/bin/perl

require './docker-lib.pl';
#ui_print_header(undef, $text{'index_title'}, "", undef, 1, 1);
&ReadParse();
&error_setup($text{'command_err'});

$command = $in{'c'};

if ($command == 'start') {
    start_container($in{'container'});
}

if ($command == 'stop') {
    stop_container($in{'container'});
}

if ($command == 'restart') {
    restart_container($in{'container'})
}

#&error($err) if ($err);

#sleep(3);
&webmin_log(ucfirst($command), 'docker container', $in{'container'});
&redirect("");