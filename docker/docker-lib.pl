=head1
Libs for docker module
=cut

BEGIN { push(@INC, ".."); };

use strict;
use warnings;
use WebminCore;
use JSON::PP;

init_config();

sub get_status {
    my $fail;
    my $status = "{}";
    my $code = execute_command('docker info --format "{{json .}}"', undef, \$status, \$fail, 0, 1);

    if ($code != 0) {
        return $fail;
    }

    my $json = decode_json($status);
    if ($json->{ServerErrors}) {
        return $json->{ServerErrors}[0];
    }

    return 0, $json;
}

sub get_containers
{
    my ($containers, $fail);
    my $code = execute_command('docker container ls --all --format {{.ID}},{{.Names}},{{.Image}},{{.Status}}', undef, \$containers, \$fail, 0, 1);

    if ($code != 0) {
        return $fail;
    }

    my @results;
    my @containers = split(/\n/, $containers);
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

sub get_stats
{
    my ($containers, $fail);
    my $code = execute_command('docker stats --all --no-stream --format "{{.ID}},{{.CPUPerc}},{{.MemPerc}},{{.MemUsage}}"', undef, \$containers, \$fail, 0, 1);

    if ($code != 0) {
        return $fail;
    }

    my %results = ( );
    my @containers = split(/\n/, $containers);

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
    my ($result, $fail);
    # my $code = execute_command('docker inspect ' . $container . ' --format "{{json .}}"', undef, \$result, \$fail, 0, 1);
    my $code = execute_command('docker inspect ' . $container, undef, \$result, \$fail, 0, 1);

    if ($code != 0) {
        return $fail;
    }

    # my $json = decode_json($result);
    # if ($json->{ServerErrors}) {
    #     return $json->{ServerErrors}[0];
    # }

    # return 0, $json, $result;
    return 0, $result;
}

sub container_logs
{
    my($container) = @_;
    my ($result, $fail);
    my $code = execute_command('docker logs ' . $container, undef, \$result, \$fail, 0, 1);

    if ($code != 0) {
        return $fail;
    }

    return 0, $result;
}


sub start_container
{
    my($container) = @_;
    my ($output, $fail);
    execute_command('docker start ' . $container, undef, \$output, \$fail, 0, 1);
}

sub stop_container
{
    my($container) = @_;
    my ($output, $fail);
    execute_command('docker stop ' . $container, undef, \$output, \$fail, 0, 1);
}

sub restart_container
{
    my($container) = @_;
    my ($output, $fail);
    execute_command('docker restart ' . $container, undef, \$output, \$fail, 0, 1);
}

sub circular_grid
{
    my($statsRaw, $depth) = @_;
    $depth ||= 1;

    my @stats;
    foreach my $field ( keys %{$statsRaw}) {
        if (ref $statsRaw->{$field} eq ref {}) {  # If hash down the rabbit hole we go
            push (@stats, sprintf("<b>%s</b>: %s", $field, circular_grid($statsRaw->{$field}, $depth + 1)));
        } elsif (ref $statsRaw->{$field} eq 'ARRAY') {  # Make the brave assumption we can flatten and join the array
            push (@stats, sprintf("<b>%s</b>: %s<br />", $field, join(",", @{$statsRaw->{$field}})));
        } else {  # If hash down the rabbit hole we go
            push (@stats, sprintf("<b>%s</b>: %s<br />", $field, $statsRaw->{$field} ||= "N/A"));
        }
    }

    return ui_grid_table(\@stats, $depth == 1 ? 2 : 1);
}