#!/usr/bin/perl
use strict;
use warnings;

require './docker-lib.pl';

&ReadParse();
&error_setup(text('command_err'));

our (%in, %config);

my $command = $in{'c'};
my $return_tab = $in{'return_tab'} || "";

my $err;

sub finish_redirect {
    my ($msg, $err) = @_;
    my @params;
    push @params, "tab=$return_tab" if $return_tab;
    push @params, "msg=" . &urlize($msg) if $msg;
    push @params, "err=" . &urlize($err) if $err;
    my $dest = "index.cgi";
    if (scalar(@params) > 0) {
        $dest .= "?" . join("&", @params);
    }
    &redirect($dest);
}

if ($command eq 'start') {
    $err = container_command($in{'container'}, 'start');
}
elsif ($command eq 'stop') {
    $err = container_command($in{'container'}, 'stop');
}
elsif ($command eq 'restart') {
   $err = container_command($in{'container'}, 'restart');
}
elsif ($command eq 'create') {
    my ($code, $result) = create_container_from_opts(
        'name' => $in{'name'},
        'image' => $in{'image'},
        'env' => $in{'env'},
        'ports' => $in{'ports'},
        'volumes' => $in{'volumes'},
        'restart' => $in{'restart'},
        'healthcheck' => $in{'healthcheck'},
        'command' => $in{'cmd'}
    );
    $err = $result if $code;
    finish_redirect(text('label_created'), $err);
}
elsif ($command eq 'clone') {
    my ($code, $result) = clone_container($in{'source'}, $in{'name'});
    $err = $result if $code;
    finish_redirect(text('label_cloned'), $err);
}
elsif ($command eq 'pull_image') {
    my ($code, $result) = pull_image($in{'image'});
    $err = $result if $code;
    finish_redirect(text('label_pulled'), $err);
}
elsif ($command eq 'push_image') {
    my ($code, $result) = push_image($in{'push_image'});
    $err = $result if $code;
    finish_redirect(text('label_pushed'), $err);
}
elsif ($command eq 'check_image') {
    my ($code, $result) = check_image_update($in{'image'});
    $err = $result if $code;
    finish_redirect(text('label_checked'), $err);
}
elsif ($command eq 'tag_image') {
    my ($code, $result) = tag_image($in{'from'}, $in{'to'});
    $err = $result if $code;
    finish_redirect(text('label_tagged'), $err);
}
elsif ($command eq 'build_image') {
    my ($code, $result) = build_image_from_dockerfile($in{'tag'}, $in{'dockerfile'});
    $err = $result if $code;
    finish_redirect(text('label_built'), $err);
}
elsif ($command eq 'prune_images') {
    my ($code, $result) = prune_images();
    $err = $result if $code;
    finish_redirect(text('label_pruned'), $err);
}
elsif ($command eq 'compose') {
    my ($code, $result) = compose_command($in{'compose_file'}, $in{'compose_action'});
    $err = $result if $code;
    $config{'compose_file'} = $in{'compose_file'};
    save_module_config(%config);
    finish_redirect(text('label_compose_ran'), $err);
}
elsif ($command eq 'volume_create') {
    my ($code, $result) = create_volume($in{'volume_name'}, $in{'volume_driver'});
    $err = $result if $code;
    finish_redirect(text('label_volume_created'), $err);
}
elsif ($command eq 'volume_prune') {
    my ($code, $result) = prune_volumes();
    $err = $result if $code;
    finish_redirect(text('label_prune_volumes'), $err);
}
elsif ($command eq 'inspect_volume') {
    my ($code, $result) = inspect_volume($in{'volume'});
    &ui_print_header(undef, text('label_volume'), "", undef, undef);
    if ($code) {
        print ui_alert_box($result, 'danger');
    } else {
        print "<pre class='comment'>" . html_escape($result) . "</pre>";
    }
    &ui_print_footer("/", text('index_return'));
    exit;
}
elsif ($command eq 'network_create') {
    my ($code, $result) = create_network($in{'network_name'}, $in{'network_driver'});
    $err = $result if $code;
    finish_redirect(text('label_network_created'), $err);
}
elsif ($command eq 'network_prune') {
    my ($code, $result) = prune_networks();
    $err = $result if $code;
    finish_redirect(text('label_prune_networks'), $err);
}
elsif ($command eq 'inspect_network') {
    my ($code, $result) = docker_command('network inspect ' . $in{'network'});
    &ui_print_header(undef, text('label_network'), "", undef, undef);
    if ($code) {
        print ui_alert_box($result, 'danger');
    } else {
        print "<pre class='comment'>" . html_escape($result) . "</pre>";
    }
    &ui_print_footer("/", text('index_return'));
    exit;
}
elsif ($command eq 'registry_login') {
    $config{'registry_server'} = $in{'registry_server'};
    $config{'registry_user'} = $in{'registry_user'};
    $config{'registry_pass'} = $in{'registry_pass'};
    save_module_config(%config);

    if ($in{'registry_user'} && $in{'registry_pass'}) {
        my $cmd = 'echo "' . $in{'registry_pass'} . '" | docker login ' . $in{'registry_server'} . ' -u "' . $in{'registry_user'} . '" --password-stdin';
        my ($out, $fail);
        my $code = execute_command($cmd, undef, \$out, \$fail, 0, 0);
        if ($code != 0) {
            $err = $fail;
        }
    }
    finish_redirect(text('label_registry_saved'), $err);
}
elsif ($command eq 'scan_image') {
    my ($code, $result) = scan_image($in{'image'});
    &ui_print_header(undef, text('label_scan'), "", undef, undef);
    if ($code) {
        print ui_alert_box($result, 'danger');
    } else {
        print "<pre class='comment'>" . html_escape($result) . "</pre>";
    }
    &ui_print_footer("/", text('index_return'));
    exit;
}
elsif ($command eq 'set_context') {
    my ($code, $result) = set_context($in{'context'});
    $err = $result if $code;
    finish_redirect(text('label_context_set'), $err);
}

if ($err) { &error($err); }

if ($return_tab) {
    finish_redirect("", "");
} else {
    &redirect("");
}
