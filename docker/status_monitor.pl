#!/usr/bin/perl
use WebminCore;

do 'docker-lib.pl';

# status_monitor_list()
# Return a list of supported monitor types
sub status_monitor_list
{
    return ( [ "docker_up", "Docker Up"], [ "docker_containerup", "Docker Container Up"],  );
}

# status_monitor_status(type, &monitor, from-ui)
# Check the docker or container status
sub status_monitor_status
{
    my ($type, $monitor, $fromui) = @_;

    # Basic status check via running docker info and checking return
    # This gets around the various ways docker can be run (supervisor, systemctl etc)
    if ($type eq "docker_up") {
        my ($status, $result) = &get_status();
        return { 
            'up' => $status == 0 ? 1 : 0, # status code 0 means ok response
            "desc" => $status != 0 ? $result : ''
        };
    } elsif ($type eq "docker_containerup") {
        $container = $monitor->{'docker_container'};

        my ($status, $result) = &get_container_attr($container, "State.Status");
        my ($status2, $uptime) = &get_container_ps_info($container, "Status"); # append uptime to running status

        my $ok = ($status == 0 && $result eq "running") ? 1 : 0;  # status code 0 means ok response
        return { 
            'up' => $ok,
            'desc' => ucfirst($result) . ($uptime ne '' ? ' (' . $uptime . ')' : '')
        };
    } 
    return { 'up' => -1,
            'desc' => $text{'monitor_notype'} };
}

# status_monitor_dialog(type, &monitor)
# Return form for configuring monitors
sub status_monitor_dialog
{
    my ($type, $mon) = @_;
    
    if ($type eq "docker_up") {
        # Nada
    } elsif ($type eq "docker_containerup") {
        return &ui_table_row("Container", # $text{'monitor_container'},
		    &ui_textbox("docker_container", html_escape($mon->{'docker_container'}), 50)
        );
    } else {
        return undef;
    }
}

# status_monitor_parse(type, &monitor, &in)
# Parse form for selecting a rule
sub status_monitor_parse
{
    my ($type, $mon, $in) = @_;
    if ($type eq "docker_up") {
        # Nada
	} elsif ($type eq "docker_containerup") {
        $mon->{'docker_container'} = $in->{'docker_container'};
    }
}

1;