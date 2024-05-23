=head1
Libs for docker module
=cut

BEGIN { push(@INC, ".."); };

use strict;
use warnings;
use WebminCore;
use JSON::PP;

init_config();

sub docker_command {
    my($command, $format, $safe) = @_;
    $format ||= "";
    $safe ||= 1;

    if ($format) {
        $format = ' --format "' . $format . '"'
    }

    my ($result, $fail);
    my $code = execute_command('docker ' . $command . $format, undef, \$result, \$fail, 0, $safe);

    if ($code != 0) {
        return $code, $fail;
    }

    return 0, $result
}


sub get_status {
    my ($code, $result) = docker_command('info');
    if ($code != 0) {
        return $result;
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

sub get_container_attr
{
    my($container, $attr) = @_;
    my ($code, $result) = docker_command('inspect --type=container ' . $container, '{{.' . $attr . '}}');
    if ($code != 0) {
        print "Bang";
        return $result;
    }

    return 0, $result;
}

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
    my($container) = @_;
    my ($code, $result) = docker_command('logs ' . $container);
    if ($code != 0) {
        return $result;
    }

    return 0, $result;
}


sub container_command
{
    my($container, $command) = @_;

    if (!($command !~~ ['start', 'stop', 'restart'])) {
        return "Command not allowed";
    }
    
    my ($code, $result) = docker_command($command . ' ' . $container);
    if ($code != 0) {
        return $result;
    }

    return $result;
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