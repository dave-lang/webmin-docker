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
    if ($json->{ ServerErrors }) {
        return $json->{ ServerErrors };
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
    my $code = execute_command('docker stats --all --no-stream --format "{{.ID}},{{.CPUPerc}},{{.MemPerc}}"', undef, \$containers, \$fail, 0, 1);

    if ($code != 0) {
        return $fail;
    }

#{"BlockIO":"0B / 0B","CPUPerc":"0.00%","Container":"344327f11366","ID":"344327f11366","MemPerc":"0.00%","MemUsage":"0B / 0B","Name":"objective_dhawan","NetIO":"0B / 0B","PIDs":"0"}
    # return 0, $containers;

    my %results = ( );
    my @containers = split(/\n/, $containers);

    foreach my $u (@containers) {
        my ($id, $cpu, $mem) = split(/,/, $u);
        $results{$id} = {
            'cpu' => $cpu,
            'mem' => $mem
        };
        # $results{$id} = $id;
    }

    return 0, %results;
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