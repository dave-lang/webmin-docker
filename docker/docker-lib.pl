=head1
Libs for docker module
=cut

BEGIN { push(@INC, ".."); };

use strict;
use warnings;
use WebminCore;
use JSON::PP;

init_config();

sub get_context {
    our (%config);
    my $context = "";

    if ($config{'docker_context'}) {
        $context = ' --context "' . $config{'docker_context'} . '"';
    }

    return $context;
}

sub docker_command {
    my($command, $format, $safe) = @_;
    $format ||= "";
    $safe ||= 1;

    if ($format) {
        $format = ' --format "' . $format . '"'
    }

    # If there's a context set, use it
    my $context = &get_context();

    my ($result, $fail);
    my $code = execute_command('docker' . $context . ' ' . $command . $format, undef, \$result, \$fail, 0, $safe);

    if ($code != 0) {
        my $trimEnd = index($fail, "errors pretty printing info");
        if ($trimEnd > 0) {
            $fail = substr($fail, 0, $trimEnd);
        }
        return $code, $fail;
    }

    return 0, $result
}


sub get_status {
    my ($code, $result) = docker_command('info');
    if ($code != 0) {
        return $code, $result;
    }

    # my $json = decode_json($result);
    # if ($json->{ServerErrors}) {
    #     return $json->{ServerErrors}[0];
    # }

    return 0, $result;
}

sub get_containers
{
    my ($code, $result) = docker_command('container ls --all ', '{{.ID}},{{.Names}},{{.Image}},{{.Status}}');
    if ($code != 0) {
        return $result;
    }

    my @results;
    my @containers = split(/\n/, $result);
    foreach my $u (@containers) {
        my ($id, $name, $image, $status) = split(/,/, $u);
        push (@results, {
            'id' => $id,
            'name' => $name,
            'image' => $image,
            'status' => $status
        });
    }

    return 0, @results;
}

sub get_container_ps_info
{
    my($container, $attr) = @_;
    my ($code, $result) = docker_command('ps -f name=' . $container, '{{.' . $attr . '}}');
    $result =~ s/^\s+|\s+$//g; # whitespace occassionally pre/post
    return $code, $result;
}

sub get_container_attr
{
    my($container, $attr) = @_;
    my ($code, $result) = docker_command('inspect --type=container ' . $container, '{{.' . $attr . '}}');
    $result =~ s/^\s+|\s+$//g; # whitespace occassionally pre/post
    return $code, $result;}

sub get_stats
{
    my ($code, $result) = docker_command('stats --all --no-stream', '{{.ID}},{{.CPUPerc}},{{.MemPerc}},{{.MemUsage}}');
    if ($code != 0) {
        return $result;
    }

    my %results = ( );
    my @containers = split(/\n/, $result);

    foreach my $u (@containers) {
        my ($id, $cpu, $mem, $memUsage) = split(/,/, $u);
        $results{$id} = {
            'cpu' => $cpu,
            'mem' => $mem,
            'memUsage' => $memUsage
        };
    }

    return 0, %results;
}

sub inspect_container
{
    my($container) = @_;
    my ($code, $result) = docker_command('inspect ' . $container . ' --type=container --size');
    if ($code != 0) {
        return $result;
    }
    
    return 0, $result;
}

sub container_logs
{
    my($container, $max_lines, $filter, $basic_match) = @_;
    our (%gconfig);

    my ($maxCommand) = ' -n ' . $max_lines;

    if (length $filter) {
        my ($result, $fail, $code);
		# Are we supposed to filter anything? Then use grep.
		my $docker_command = "docker logs $container " . $maxCommand;
		my $eflag = $gconfig{'os_type'} =~ /-linux/ ? "-E" : "";
		my $dashflag = $gconfig{'os_type'} =~ /-linux/ ? "--" : "";

        my $flags = $basic_match == 1 ? ' -F ' : '-i -a ' . $eflag . ' ' . $dashflag;
	
        $code = execute_command(
            $docker_command . ' | grep '. $flags . ' "' . $filter . '"', 
            undef, \$result, \$fail, 0, 1);

        if ($code == 256) { # No results?
            return 0, "No matching logs found, try increasing max lines, escaping or ignoring special characters";
        }

        if ($code != 0) {
            return $code, "Failed to search logs: " . $fail;
        }

        return 0, $result;
	} else {
        my ($code, $result) = docker_command('logs ' . $container . $maxCommand);

        if ($code != 0) {
            return $code, $result;
        }

        return 0, $result;
    }
}


sub container_command
{
    my($container, $command) = @_;

    if (!($command !~~ ['start', 'stop', 'restart'])) {
        return "Command not allowed";
    }
    
    my ($code, $result) = docker_command('container ' . $command . ' ' . $container);
    if ($code != 0) {
        &webmin_log('Failed ' . $command, 'docker container', $in{'container'});
        return $result;
    }

    &webmin_log(ucfirst($command), 'docker container', $in{'container'});
    return "" # successful commands only return the container name
}

sub circular_grid
{
    my($statsRaw, $depth) = @_;
    $depth ||= 1;

   print  Dumper($statsRaw);
    my $result = ui_table_start($depth > 1 ? "" : "Info");

    my @stats;
    foreach my $field ( keys %{$statsRaw}) {
        if (ref $statsRaw->{$field} eq ref {}) {  # If hash down the rabbit hole we go
            $result = $result . ui_table_hr() . ui_table_span($field);
            $result = $result . ui_table_span(circular_grid($statsRaw->{$field}, $depth + 1));
            #push (@stats, sprintf("<b>%s</b>: %s", $field, circular_grid($statsRaw->{$field}, $depth + 1)));
        } elsif (ref $statsRaw->{$field} eq 'ARRAY') {  # Make the brave assumption we can flatten and join the array
            $result = $result . ui_table_row($field . "(ARR)", join(",", @{$statsRaw->{$field}})); #, [cols], [&td-tags])
            # push (@stats, sprintf("<b>%s</b>: %s<br />", $field, join(",", @{$statsRaw->{$field}})));
        } else {  # If hash down the rabbit hole we go
            $result = $result . ui_table_row($field, $statsRaw->{$field} eq "" ? "[N/A]" : $statsRaw->{$field}); #, [cols], [&td-tags])
            #push (@stats, sprintf("<b>%s</b>: %s<br />", $field, $statsRaw->{$field} ||= "N/A"));
        }
    }
    $result = $result . ui_table_end();

    # return ui_grid_table(\@stats, 1);
    return $result;
}

sub starts_with
{
    my ($str, $prefix) = @_;
    return substr($str, 0, length($prefix)) eq $prefix;
}

sub get_container_up
{
    my ($status) = @_;
    return starts_with($status, "Up ");
}

sub get_status_icon
{
    my ($status) = @_;

    my ($up) = get_container_up($status);
    my ($color) = $up ? 'green' : 'red';

    return '<span style="font-weight: bold; font-size: 140%; color: ' . $color . '; float: left; padding-right: 10px">' 
        . ($up ? "&check;" : "&cross;") . '</span>';
}