=head1
Libs for docker module
=cut

BEGIN { push(@INC, ".."); };
use WebminCore;

init_config();

sub get_containers
{
    local $containers, $fail;
    my $code = execute_command('docker container ls --all --format {{.ID}},{{.Names}},{{.Image}},{{.Status}}', undef, \$containers, \$fail, 0, 1);

    if ($code != 0) {
        print $fail;
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

    return @results;
}

sub get_stats
{
    my $containers;
    my $fail;
    my $code = execute_command('docker stats --all --no-stream --format "{{.ID}},{{.CPUPerc}},{{.MemPerc}}"', undef, \$containers, \$fail, 0, 1);

    if ($code != 0) {
        print $fail;
    }

#{"BlockIO":"0B / 0B","CPUPerc":"0.00%","Container":"344327f11366","ID":"344327f11366","MemPerc":"0.00%","MemUsage":"0B / 0B","Name":"objective_dhawan","NetIO":"0B / 0B","PIDs":"0"}
    return $containers;

    %results = ( );
    my @containers = split(/\n/, $containers);

    foreach my $u (@containers) {
        my ($id, $cpu, $mem) = split(/,/, $u);
        $results{ $id } = {
            'id' => $id,
            'name' => $name,
            'image' => $image
        };
    }

    return %results;
}

sub start_container
{
    my($container) = @_;
    execute_command('docker start ' . $container, undef, \$containers, undef, 0, 1);
}

sub stop_container
{
    my($container) = @_;
    execute_command('docker stop ' . $container, undef, \$containers, undef, 0, 1);
}

sub restart_container
{
    my($container) = @_;
    execute_command('docker restart ' . $container, undef, \$containers, undef, 0, 1);
}