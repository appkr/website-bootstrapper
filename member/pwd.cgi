#!/usr/bin/perl 

$path = $0;
$path =~ s/\.cgi$//i;
$path =~ s/\.pl$//i;
$path =~ s/\\/\//g;
$path =~ s/\/pwd$//i;

print "Content-type: text/html\n\n"; 
print "절대 경로 = $path\n";