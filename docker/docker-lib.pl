=head1
Libs for docker module
=cut

BEGIN { push(@INC, ".."); };

use strict;
use warnings;
use WebminCore;
use JSON::PP;
use File::Temp qw(tempdir tempfile);

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

# Prefer docker compose if present, fallback to docker-compose
sub get_compose_bin {
    my $compose_bin = 'docker compose';
    if (&has_command('docker-compose')) {
        $compose_bin = 'docker-compose';
    }
    return $compose_bin;
}

sub get_contexts {
    my ($code, $result) = docker_command('context ls', '{{json .}}');
    if ($code != 0) {
        return $result;
    }

    my @contexts;
    foreach my $line (split(/\n/, $result)) {
        my $ctx = decode_json($line);
        push @contexts, $ctx;
    }

    return 0, @contexts;
}

sub set_context {
    my ($context) = @_;
    our %config;
    $config{'docker_context'} = $context;
    &save_module_config(%config);
    return 0, "Context updated";
}

sub parse_lines {
    my ($value) = @_;
    return grep { $_ ne '' } map { s/^\s+|\s+$//g; $_ } split(/\r?\n/, $value || "");
}

sub build_run_args {
    my (%opts) = @_;
    my @args = ('run', '-d');

    push @args, '--name ' . $opts{'name'} if $opts{'name'};

    foreach my $env (parse_lines($opts{'env'})) {
        push @args, '-e "' . $env . '"';
    }

    foreach my $port (parse_lines($opts{'ports'})) {
        push @args, '-p ' . $port;
    }

    foreach my $vol (parse_lines($opts{'volumes'})) {
        push @args, '-v ' . $vol;
    }

    if ($opts{'restart'}) {
        push @args, '--restart ' . $opts{'restart'};
    }

    if ($opts{'healthcheck'}) {
        push @args, '--health-cmd "' . $opts{'healthcheck'} . '"';
    }

    push @args, $opts{'image'};

    if ($opts{'command'}) {
        push @args, $opts{'command'};
    }

    return @args;
}

sub create_container_from_opts {
    my (%opts) = @_;
    if (!$opts{'image'}) {
        return 1, "Image is required";
    }

    my @args = build_run_args(%opts);
    return docker_command(join(' ', @args), '', 0);
}

sub get_container_template {
    my ($container) = @_;
    my ($code, $raw) = docker_command('inspect ' . $container, '{{json .}}');
    if ($code != 0) {
        return $code, $raw;
    }

    my $decoded = decode_json($raw);
    return 0, {
        'name' => substr($decoded->{'Name'} || '', 1),
        'image' => $decoded->{'Config'}{'Image'},
        'env' => join("\n", @{$decoded->{'Config'}{'Env'} || []}),
        'ports' => join("\n", map {
            my $k = $_;
            my @bindings = @{$decoded->{'HostConfig'}{'PortBindings'}{$k} || []};
            join("\n", map { ($_->{'HostPort'} ? $_->{'HostPort'} : '') . ':' . $k } @bindings);
        } keys %{$decoded->{'HostConfig'}{'PortBindings'} || {}}),
        'volumes' => join("\n", @{$decoded->{'HostConfig'}{'Binds'} || []}),
        'restart' => $decoded->{'HostConfig'}{'RestartPolicy'}{'Name'} || '',
        'healthcheck' => $decoded->{'Config'}{'Healthcheck'}{'Test'} ? join(" ", @{$decoded->{'Config'}{'Healthcheck'}{'Test'}}) : ''
    };
}

sub clone_container {
    my ($source, $newname) = @_;
    my ($code, $template) = get_container_template($source);
    if ($code != 0) {
        return $code, $template;
    }

    $template->{'name'} = $newname if $newname;
    return create_container_from_opts(%{$template});
}

sub list_images {
    my ($code, $result) = docker_command('image ls --all', '{{.Repository}}:{{.Tag}},{{.ID}},{{.Size}},{{.Digest}}');
    if ($code != 0) {
        return $result;
    }

    my @images;
    foreach my $line (split(/\n/, $result)) {
        my ($name, $id, $size, $digest) = split(/,/, $line);
        push @images, {
            'name' => $name,
            'id' => $id,
            'size' => $size,
            'digest' => $digest
        };
    }
    return 0, @images;
}

sub pull_image {
    my ($image) = @_;
    return docker_command('pull ' . $image, '', 0);
}

sub push_image {
    my ($image) = @_;
    return docker_command('push ' . $image, '', 0);
}

sub prune_images {
    return docker_command('image prune -f', '', 0);
}

sub tag_image {
    my ($source, $target) = @_;
    return docker_command('tag ' . $source . ' ' . $target, '', 0);
}

sub build_image_from_dockerfile {
    my ($tag, $dockerfile) = @_;
    if (!$dockerfile) {
        return 1, "Dockerfile content required";
    }

    my $dir = tempdir(CLEANUP => 1);
    my $file = $dir . "/Dockerfile";
    open(my $fh, ">", $file) or return 1, "Unable to write temp Dockerfile";
    print $fh $dockerfile;
    close($fh);

    return docker_command('build -t ' . $tag . ' ' . $dir, '', 0);
}

sub image_history {
    my ($image) = @_;
    return docker_command('history ' . $image, '', 0);
}

sub compose_command {
    my ($file, $command) = @_;
    my $compose = get_compose_bin();
    my $cmd = $compose . ' -f ' . $file . ' ' . $command;
    my ($out, $fail);
    my $code = execute_command($cmd, undef, \$out, \$fail, 0, 1);
    if ($code != 0) {
        return $code, $fail;
    }
    return 0, $out;
}

sub list_volumes {
    my ($code, $result) = docker_command('volume ls', '{{.Name}},{{.Driver}},{{.Mountpoint}}');
    if ($code != 0) {
        return $result;
    }
    my @vols;
    foreach my $line (split(/\n/, $result)) {
        my ($name, $driver, $mp) = split(/,/, $line);
        push @vols, { 'name' => $name, 'driver' => $driver, 'mountpoint' => $mp };
    }
    return 0, @vols;
}

sub inspect_volume {
    my ($name) = @_;
    return docker_command('volume inspect ' . $name, '', 0);
}

sub create_volume {
    my ($name, $driver) = @_;
    my $cmd = 'volume create';
    $cmd = $cmd . ' --driver ' . $driver if $driver;
    $cmd = $cmd . ' ' . $name if $name;
    return docker_command($cmd, '', 0);
}

sub prune_volumes {
    return docker_command('volume prune -f', '', 0);
}

sub list_networks {
    my ($code, $result) = docker_command('network ls', '{{.Name}},{{.Driver}},{{.Scope}}');
    if ($code != 0) {
        return $result;
    }
    my @nets;
    foreach my $line (split(/\n/, $result)) {
        my ($name, $driver, $scope) = split(/,/, $line);
        push @nets, { 'name' => $name, 'driver' => $driver, 'scope' => $scope };
    }
    return 0, @nets;
}

sub create_network {
    my ($name, $driver) = @_;
    my $cmd = 'network create';
    $cmd = $cmd . ' --driver ' . $driver if $driver;
    $cmd = $cmd . ' ' . $name if $name;
    return docker_command($cmd, '', 0);
}

sub prune_networks {
    return docker_command('network prune -f', '', 0);
}

sub connect_network {
    my ($network, $container) = @_;
    return docker_command('network connect ' . $network . ' ' . $container, '', 0);
}

sub disconnect_network {
    my ($network, $container) = @_;
    return docker_command('network disconnect ' . $network . ' ' . $container, '', 0);
}

sub exec_in_container {
    my ($container, $cmd) = @_;
    return docker_command('exec ' . $container . ' ' . $cmd, '', 0);
}

sub copy_to_container {
    my ($host_path, $container, $target_path) = @_;
    return docker_command('cp ' . $host_path . ' ' . $container . ':' . $target_path, '', 0);
}

sub copy_from_container {
    my ($container, $source_path, $host_path) = @_;
    return docker_command('cp ' . $container . ':' . $source_path . ' ' . $host_path, '', 0);
}

sub check_image_update {
    my ($image) = @_;
    my ($code, $result) = docker_command('pull ' . $image, '', 0);
    if ($code != 0) {
        return $code, $result;
    }
    return 0, $result;
}

sub scan_image {
    my ($image) = @_;
    my ($code, $result) = docker_command('scan ' . $image, '', 0);
    if ($code == 0) {
        return $code, $result;
    }
    if (&has_command('trivy')) {
        my $cmd = 'trivy image ' . $image;
        return docker_command($cmd, '', 0);
    }
    return 1, "No scanner found (docker scan or trivy)";
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
