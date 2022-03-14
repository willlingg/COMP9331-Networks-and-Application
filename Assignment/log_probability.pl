#!/usr/bin/perl

my $target_word = $ARGV[0];

sub total_words {
    die "total_words(FILENAME): incorrect num args" if scalar @_ != 1;
    open(text, "<", "$_[0]") or die "$!";
    my $count = 0;
    while ($line = <text>) {
        @words = split /[^a-zA-Z]/, $line;
        foreach $word (@words) {
            $count++ if $word =~ /[a-zA-Z]/;
        }
    }
    close(text);
    return $count;
}

sub count_word {
    my $word = lc $_[0];
    open(text, "<", "$_[1]") or die "$!";
    my $count = 0;
    while ($line = <text>) {
        @words = split /\b$word\b/i, $line;
        $count += scalar @words -1;
    }
    close(text);
    return $count;
}

foreach my $file (glob("lyrics/*.txt")) {
    my $n_lyrics = count_word($target_word, $file);
    my $total = total_words($file);
    my $frequency = log(($n_lyrics+1)/$total);
    $file =~ /lyrics\/(.*)\.[^.]*$/;
    my $artist = $1;
    $artist =~ tr/_/ /;
    printf("log((%d+1)/%6d) = %8.4f %s\n", $n_lyrics, $total, $frequency, $artist);
}
