=head1
Libs for docker module
=cut

BEGIN { push(@INC, ".."); };
use WebminCore;

init_config();

sub get_containers
{
    my $one = "Test";
    my $containers = "Test";
    my $fail;
    execute_command('docker container ls', \$one, \$containers, \$fail, 0, 1);

    return $containers, $fail;
}

sub start_container
{
    my($container) = @_;
}

sub stop_container
{
    my($container) = @_;
}

sub restart_container
{
    my($container) = @_;
    execute_command('docker restart ' . $container, undef, \$containers, undef, 0, 1);
}