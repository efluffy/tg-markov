#!/usr/bin/perl -w 

use strict;
use CGI;
use JSON;
use Hailo;
use LWP::UserAgent;
use Net::Twitter;
use Data::Dumper;

my $DEBUG = 0;
my $die;

open( my $rfh, "<", "running.txt" );
$die = <$rfh>;
close($rfh);

my $brain        = "./tgbot.sqlite";

# Telegram Bot API/Channel Info
my $botkey       = "";
my $owner        = "";
my $chat         = "";
my $botname      = "";

# Twitter API Info
my $consumerkey  = "";
my $consumerskey = "";
my $token        = "";
my $tokens       = "";

my $sendURL =
"https://api.telegram.org/$botkey/sendMessage?chat_id=$chat&text=";
my $stickerURL =
"https://api.telegram.org/$botkey/sendSticker?chat_id=$chat&sticker=";

my $q;
my $json;
my $bot;
my $ua;
my $message;
my $id;
my $chatid;
my $update;
my $reply = "";

my @insults = (
    "no get fucked >:/",
    "nooope! c:",
    "eval fuck you! >:C",
    "not gonna happen! :3"
);

my @beeps = (
    "*beeps sadly*",
    "*furious beeping*",
    "*angry beep beep*",
    "*wink bloop beep wink*",
    "*beep-purr*",
    "*sleepy bloop*",
    "*beep wag beep*"
);

my %stickers = (
    hello         => "",
    vacant        => "",
    surprised     => "",
    excited       => "",
    confused      => "",
    angry         => "",
    flabbergasted => "",
    comforting    => ""
);

sub debug_log {
    my $toWrite = shift;
    if ($DEBUG) {
        open( my $fh, ">>", "logfile.txt" );
        print $fh $toWrite . "\n";
        close($fh);
    }
    return;
}

sub history {
    my $message = shift;
    my $fh;
    open( $fh, "<", "history.txt" );
    my @lines = <$fh>;
    close($fh);
    push( @lines, $message . "\n" );
    while ( $#lines > 9 ) {
        shift(@lines);
    }
    open( $fh, ">", "history.txt" );
    foreach my $line (@lines) {
        print $fh $line;
    }
    close($fh);
}

sub tweet {
    my $which = shift;
	
    if ( !$which ) { $which = 1; }
	if ( $which =~ m/[^0-9]+/ ) { $which = 1; }
	if ( $which > 10 ) { $which = 10; }
    $which = $which - 1;

    open( my $fh, "<", "history.txt" );
    my @lines = <$fh>;
    close($fh);

    @lines = reverse @lines;
    my $tweet = $lines[$which];
    chomp($tweet);

    my $nt = Net::Twitter->new(
        traits              => [qw/API::RESTv1_1/],
        consumer_key        => $consumerkey,
        consumer_secret     => $consumerskey,
        access_token        => $token,
        access_token_secret => $tokens,
    );

    if ( length($tweet) <= 140 ) {
        $nt->update($tweet);
        open( my $fht, ">", "time.txt" );
        print $fht time();
        close($fht);
        return $tweet;
    }

    else {
        $ua->get(
            $sendURL . "Tweet? Twat?! Twot! ...nope, too long, can't do it!" );
			return 0;
    }
}

$q = CGI->new;
print $q->header();
$json = decode_json( $q->param('POSTDATA') );
$bot  = Hailo->new( brain => $brain );
$ua   = LWP::UserAgent->new( ssl_opts => { verify_hostname => 1 } );

$message = $json->{message}->{text};
$id      = $json->{message}->{from}->{id};
$chatid  = $json->{message}->{chat}->{id};
$update  = $json->{update_id};

if ( $id == $owner ) {
    if ( $message =~ m/^!live/i ) {
        $die = 0;
        open( my $rfh, ">", "running.txt" );
        print $rfh $die;
        close($rfh);
        $ua->get( $stickerURL . $stickers{hello} );
    }
    elsif ( $message =~ m/^!die/i ) {
        $die = 1;
        open( my $rfh, ">", "running.txt" );
        print $rfh $die;
        close($rfh);
        $ua->get( $stickerURL . $stickers{surprised} );
    }
}

if ( $die == 1 ) { exit(0); }

if ( $chatid != $chat && $id != $owner ) { exit(0); }
if ( !defined $message ) { exit(0); }

if ( $message =~ m/.*$botname.*/i ) {
    if ( $message =~ m/\b(hello|helo|hi|hey|hola)\b/i ) {
        $ua->get( $stickerURL . $stickers{hello} );
    }
    elsif ( $message =~ m/\blove\b/i && rand(100) > 50 ) {
        $ua->get( $stickerURL . $stickers{flabbergasted} );
    }
    elsif ( $message =~ m/\b(dumb|stupid|retarded)\b/i && rand(100) > 50 ) {
        $ua->get( $stickerURL . $stickers{vacant} );
    }
    elsif ( $message =~ m/\bsticker\b/i ) {
        $ua->get( $stickerURL
              . $stickers{ ( keys %stickers )[ rand keys %stickers ] } );
    }
    else {
        my $random = rand(100);
        if ( $random <= 90 ) {
            $reply = $bot->reply($message);
            $ua->get( $sendURL . $reply );
        }
        else {
            $reply = $beeps[ rand @beeps ];
            $ua->get( $sendURL . $reply );
        }
    }
}

elsif ( $message =~ m/^!say/i && $id == $owner ) {
    $message =~ s/^!say //;
    $ua->get( $sendURL . $message );
}

elsif ( $message =~ m/^!ping/i ) {
    my $reply = `ping -c 4 -i 0.25 google.com | tail -1`;
    $ua->get( $sendURL . $reply );
}

elsif ( $message =~ m/^!stats/i ) {
    my $sreply = $bot->stats();
    $ua->get( $sendURL . $sreply );
}

elsif ( $message =~ m/^!tweet/i ) {
    open( my $fht, "<", "time.txt" );
    my $time = <$fht>;
    close($fht);
    if ( $time <= ( time() - 10 ) ) {
        my $tweet = tweet( ( split " ", $message )[1] );
		if($tweet) {
			$ua->get( $sendURL . "Tweeting: \"" . $tweet . "\"" );
		}
    }
    else {
        $ua->get( $sendURL . "I can't tweet that fast you twat!" );
    }
}

elsif ( $message =~ m/^!eval.*/i ) {
    my $result;
    $message =~ s/^!eval//i;

    if ( $id == $owner ) {
        $result = eval($message);
        $ua->get( $sendURL . $result );
    }

    elsif ( $message =~ m/.*[0-9].*/ ) {
        $message =~ tr/0-9+-\/*//dc;
        $result = eval($message);
        $ua->get( $sendURL . $result );
    }

    else {
        $ua->get( $sendURL . $insults[ rand @insults ] );
    }
}

elsif ( $message =~ m/^!roll.*/i ) {
	if( $message !~ m/^!roll +[0-9]d[0-9]{1,3}([+\-][0-9]{1,3})?/i ) {
		$ua->get( $sendURL . "Gonna roll my shiny metal ass into your face! >:/" );
		exit(0);
	}
	$message =~ s/[^0-9d\+\-]//g;
	chomp $message;
	my @tmp = split(/d/, $message);
	my $numRoll = $tmp[0];
	my $die = $tmp[1];
	my $modifier = 0;
	my $total = 0;
	my $addSub = 0;
	if( $die =~ m/\+/ ) {
		@tmp = split(/\+/, $die);
		$die = $tmp[0];
		$modifier = $tmp[1];
		$addSub = "a";
	}
	elsif( $die =~ m/\-/ ) {
		@tmp = split(/\-/, $die);
		$die = $tmp[0];
		$modifier = $tmp[1];
		$addSub = "s";
	}
	my @rolls;
	for(my $i = 0; $i < $numRoll; $i++) {
		push(@rolls, (1+int rand($die)));
	}
	my $reply = "Rolling $message... Result: (";
	for(my $j = 0; $j <= $#rolls; $j++) {
		if($j != ($#rolls) ) {
			$reply = $reply . "$rolls[$j] + ";
		}
		else {
			$reply = $reply . "$rolls[$j]";
		}
		$total += $rolls[$j];
	}
	if( $modifier != 0 ) {
		if($addSub eq "a") {
			$reply = $reply . ") = ($total + $modifier) = " . ($total + $modifier) . ".";
		}
		else {
			$reply = $reply . ") = ($total - $modifier) = " . ($total - $modifier) . ".";
		}
	}
	else {
		$reply = $reply . ") = " . $total . ".";
	}
	$reply =~ s/\+/%2B/g;
	$ua->get( $sendURL . $reply );
}

else {
    if ( $update % 100 == 0 ) {
        $reply = $bot->reply();
        $ua->get( $sendURL . $reply );
    }
    elsif ( $message =~ m/\b(angry|pissed|livid|mad)\b/i && rand(100) > 50 ) {
        $ua->get( $stickerURL . $stickers{angry} );
    }
    elsif ( $message =~ m/\b(sad|depressed|upset)\b/i && rand(100) > 50 ) {
        $ua->get( $stickerURL . $stickers{comforting} );
    }
    elsif ( $message =~ m/\b(fap|masturbate|sex|yiff|murr|moan)\b/i
        && rand(100) > 50 )
    {
        $ua->get( $stickerURL . $stickers{excited} );
    }

    $bot->learn($message);
}
if ( $reply ne "" ) {
    history($reply);
}
$bot->save();
exit(0);