#!/usr/local/bin/perl
# Show a form to renew a domain registration
use strict;
no strict 'refs';
use warnings;
our (%text, %in);
our $module_name;

require './virtualmin-registrar-lib.pl';
&ReadParse();
&error_setup($text{'renew_err'});

# Get the Virtualmin domain
&can_domain($in{'dom'}) && &virtual_server::can_use_feature($module_name) ||
	&error($text{'renew_ecannot'});
my $d = &virtual_server::get_domain_by("dom", $in{'dom'});
$d || &error(&text('contact_edom', $in{'dom'}));
my ($account) = grep { $_->{'id'} eq $d->{'registrar_account'} }
		  &list_registrar_accounts();
$account || &error(&text('contact_eaccount', $in{'dom'}));

# Get current registration period
my $efunc = "type_".$account->{'registrar'}."_get_expiry";
my ($ok, $exp) = &$efunc($account, $d);
$ok || &error($exp);

&ui_print_header(&virtual_server::domain_in($d), $text{'renew_title'}, "",
		 "renew");

print &ui_form_start("renew.cgi", "post");
print &ui_hidden("dom", $in{'dom'});
print &ui_table_start($text{'renew_header'}, undef, 2);

# Account
print &ui_table_row($text{'edit_desc'},
	$account->{'desc'});

# Expiry date
print &ui_table_row($text{'renew_expiry'},
	&make_date($exp, 1));

# Days till then
if ($exp < time()) {
	print &ui_table_row($text{'renew_days'},
		"<font color=#ff0000>".
		&text('renew_already', int((time() - $exp)/(24*60*60))).
		"</font>");
	}
else {
	print &ui_table_row($text{'renew_days'},
		int(($exp - time())/(24*60*60)));
	}

# Years to renew for
my $yfunc = "type_".$account->{'registrar'}."_renew_years";
print &ui_table_row($text{'renew_years'},
	&ui_textbox("years", &$yfunc($account, $d), 5));

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'renew_ok'} ] ]);

&ui_print_footer();
