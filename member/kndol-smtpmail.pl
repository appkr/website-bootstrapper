############################################################
#                     KnDol-SMTPMAIL.PL
#
# This script was written by Gunther Birznieks.
# Date Created: 2-22-1996
# Date Last Modified: 5-5-1996
#
# Modified by Dae-Seok Kim.
# Date Last Modified: Apr.21.2000
# E-mail : kndol@kndol.sarang.net
#
#
# �̰͸��� ��!!!!
#     �� ��ũ��Ʈ�� ����Ǵ� ������ SMTP ������ ��ġ�Ǿ� �־�߸� �����մϴ�.
#
#
# �������� �ٲ� �� :
#     1. ���� ���� ���� �ּҸ� ���� ���� Netscape Messenger ���
#        ����� ������ �ʴ� ���� �ذ�
#     2. ���� ���� �̸��� ���� �����ϵ��� ���� (�Ʒ� ���� 'My name')
#     3. ���� ���� �׷��� ���� ���� (�Ʒ� ���� 'group')
#        (group�� ���� ���� ���� �ּҰ� ��ϵ� �ؽ�Ʈ �����̸�
#         ���� �ô� ���� ��� �ּҷθ� ����, �׷� ��� �� ���� ���
#         �ּҴ� ""�� ����)
#     4. HTML ������ ���� �� �ֵ��� �� (&setHtmlMail, &setTextMail)
#     5. ���� ���ڵ��� �ѱ�(EUC-KR)�� ���� �� �ֵ��� �� (&setKoreanMail, &setEnglishMail)
#     6. $gMailOS ������ ���� �ʾ��� ��� �ڵ� ���� ��� �߰�
#     7. ���� �߻��� ���� �޽����� ����, ������ �����ô� "0"�� ����
#
# ���� :
#     $errorCode = &SendMail("My name", "me@myhouse.com", "Your name",
#                            "you@yourhouse.com", "My subject", "My message");
# �Ǵ�
#     $errorCode = &SendMail("My name", "me@myhouse.com", "Your name",
#                            "you@yourhouse.com", "My subject", "My message", "To group");
#
# ����ó�� ��:
#     &error($errorCode) if ($errorCode ne "0");
#
# ��� ��:
#     1. �Ϲ��� ���    : $errorCode = &send_mail("�뼮", "kndol@kndol.sarang.net", "you@yourhouse.com", "send_mail ����", "$message");
#     2. ���� �׷� ��� : $errorCode = &send_mail("�뼮", "kndol@kndol.sarang.net", "", "send_mail ����", "$message", "C:\mail_list\group.txt");
#        �޴� ��� ���� �ּҿ� �޴� �׷� ���� ��� ����
#
# ���� :
#     1. HTML ������ ������ ���ؼ��� SendMail�� ȣ���ϱ� ���� &setHtmlMail�� ȣ���ؾ� �մϴ�.
#        �ؽ�Ʈ ������ &setTextMail�Դϴ�.
#     2. �ѱ� ���ڵ��� &setKoreanMail, ���� ������ &setEnglishMail�� ���� ȣ���ؾ� �մϴ�.
#     3. set...Mail�� ȣ������ �ʰ� �ٷ� SendMail�� ����ϸ� ���� �ؽ�Ʈ ���Ϸ� �����ϴ�.
#
#
#   GNU GPL(General Public License) �Ǵ� the Artistic License�� ����
#   ������� ���� �� �����, ������ �����մϴ�. Perl v5.x ������ ���۵Ǿ�����,
#   ���� �� ������ô� ������ �� �������� �̸��� �����Ͽ� ������Ͻñ� �ٶ��ϴ�.
#
#   You may copy this under the terms of the GNU General Public
#   License or the Artistic License which is distributed with
#   copies of Perl v5.x for UNIX.
#
# Purpose: Provides a set of library routines to send email
# over the internet.  It communicates using TCP/IP Sockets directly
# to SMTP (Simple Mail Transfer Protocol)
#
# Modified by Gunther Birznieks 3-19-96 to run on PERL 5 for Windows NT
# as well as the Solaris system it was originally written under
#
# Main Procedures:
#  RealSendMail - flexible way to send email
#  SendMail - easier to use version of RealSendMail
#
# Special Notes: Script is UNIX Specific and ties into the
# Sendmail Program which is usually located in /usr/lib or
# /usr/bin.
#
# Also, remember to escape @ signs with a backslash (\@)
# for compatibility with PERL 5.
#
# Change the $mail_program variable to change location of your
# sendmail program
#
# Set the $gMailOS variable equal to NT if you are on Windows NT perl
# Set it to UNIX for normal UNIX operations.
#
# If you do not have a version of PERL with the Socket.pm, you
# can manually define $AF_INET and $SOCK_STREAM to 2 and 1 respectively.
# On some systems, SOCK_STREAM may be 2.
#
# NOTE: This program does not support MX DNS records which is
# an important part of the internet mail standard.  Use sendmail_lib.pl
# if you can since the sendmail daemon on unix supports MX records.
############################################################

# FIGURE OUT THE OS WE'RE RUNNING UNDER
# Some systems support the $^O variable.  If not
# available then require() the Config library
unless ($gMailOS) {
    unless ($gMailOS = $^O) {
		require Config;
		$gMailOS = $Config::Config{'osname'};
    }
}
if ($gMailOS=~/Win/i) {
    $gMailOS = 'NT';
} elsif ($gMailOS=~/vms/i) {
    $gMailOS = 'VMS';
} elsif ($gMailOS=~/^MacOS$/i) {
    $gMailOS = 'MACINTOSH';
} elsif ($gMailOS=~/os2/i) {
    $gMailOS = 'OS2';
} else {
    $gMailOS = 'UNIX';
}

# ���� ���� ���н� ��õ� ȸ��
$gRetry = 30;

# Use the Sockets library for TCP/IP Communications
use Socket;

############################################################
#
# subroutine: RealSendMail
#   Usage:
#     &RealSendMail("my name", "me@myhouse.com","myhouse.com","you@yourhouse.com",
#     "yourhouse.com", "Mysubject", "My message"[, "group"]);
#
#   Parameters:
#     $fromname    = Name of sender
#     $fromuser    = Full Email address of sender
#     $fromsmtp    = Full Internet Address of sender's SMTP Server
#     $toname      = Name of receiver
#     $touser      = Full Email address of receiver
#     $tosmtp      = Full Internet Address of receiver's SMTP Server
#     $subject     = Subject of message
#     $messagebody = Body of message including newlines.
#     $group       = Group of receivrs
#
#   Output:
#     None
############################################################

sub RealSendMail {
	my($fromname, $fromuser, $fromsmtp, $toname, $touser, $tosmtp, $subject, $messagebody, $group) = @_;
	my($ipaddress, $fullipaddress, $packconnectip);
	my($packthishostip);
	my($AF_INET, $SOCK_STREAM, $SOCK_ADDR);
	my($PROTOCOL, $SMTP_PORT);
	my($buf, $message, $charset);
	my($i);

	# We start off by making the message that will be sent
	# By combining the subject with the message body text
	#
	my($charset) = ($gSMTP_KoreanMail == 1) ? "EUC-KR" : "ISO-8859-1";
	$message = "MIME-Version: 1.0\n";
	$message .= "Content-Transfer-Encoding: 8bit\n";
	$message .= ($gSMTP_HtmlMail == 1) ? "Content-Type: text/html; charset=$charset\n" : "Content-Type: text/plain; charset=$charset\n";
	$message .= "From: $fromname <$fromuser>\n";
	$message .= "Group: $group\n" if ($group);
	$message .= "To: $toname <$touser>\n";
	$message .= "X-Sender: $ENV{'SERVER_NAME'}\n";
	$message .= "X-Mailer: KnDol SMTP Perl Module v1.0\n";
	$message .= "Subject: $subject\n\n";
	$message .= $messagebody;

	# The following variables are set using values defined in
	# The sockets.pm library.  If your version of perl (v4) does
	# not have the sockets library, you can substitute some
	# default values such as 2 for AF_INIT, and 1 for SOCK_STREAM.
	# if 1 does not work for SOCK_STREAM, try using 2.
	#
	# AF_INET defines the internet class of addressing
	#
	# SOCK_STREAM is a variable telling the program to use
	# a socket connection.  This varies from using SOCK_DGRAM
	# which would send UDP datagrams using a connectionless paradigm
	# instead.
	#
	# PROTOCOL is TCPIP (6).
	#
	# PORT is 25 for SMTP service.
	#
	# SOCK_ADDR is the packeted format of the full socket address
	# including the AF_INIT value, SMTP_PORT, and IP ADDRESS in that order
	#


	$AF_INET = AF_INET;
	$SOCK_STREAM = SOCK_STREAM;

	$SOCK_ADDR = "S n a4 x8";

	# The following routines get the protocol information
	#

	$PROTOCOL = (getprotobyname('tcp'))[2];
	$SMTP_PORT = (getservbyname('smtp','tcp'))[2];

	$SMTP_PORT = 25 unless ($SMTP_PORT =~ /^\d+$/);
	$PROTOCOL = 6 unless ($PROTOCOL =~ /^\d+$/);

	# Ip address is the Address of the host that we need to connect
	# to
	$ipaddress = (gethostbyname($tosmtp))[4];

	$fullipaddress = join (".", unpack("C4", $ipaddress));

	$packconnectip = pack($SOCK_ADDR, $AF_INET, $SMTP_PORT, $ipaddress);
	$packthishostip = pack($SOCK_ADDR, $AF_INET, 0, "\0\0\0\0");

	# First we allocate the socket
	for ($i=0; $i<$gRetry; $i++) {
		socket (S, $AF_INET, $SOCK_STREAM, $PROTOCOL) && last;
	}
	return("Can't make socket: $!\n") if ($i == $gRetry);

	# Then we bind the socket to the local host
	for ($i=0; $i<$gRetry; $i++) {
		bind (S,$packthishostip) && last;
	}
	return("Can't bind: $!\n") if ($i == $gRetry);

	# Then we connect the socket to the remote host
	for ($i=0; $i<$gRetry; $i++) {
		connect(S, $packconnectip) && last;
	}
	return("Can't connect socket: $!\n") if ($i == $gRetry);

	# The following selects the socket handle and turns off
	# output buffering
	#
	select(S);
	$| = 1;
	select (STDOUT);

	# The following sends the information to the SMTP Server.

	# The first connect should give us information about the SMTP
	# server

	$buf = readSock(S, 6);

	print S "HELO $fromsmtp\n";

	$buf = readSock(S, 6);

	print S "MAIL From:<$fromuser>\n";
	$buf = readSock(S, 6);

	print S "RCPT To:<$touser>\n";
	$buf = readSock(S, 6);

	print S "DATA\n";
	$buf = readSock(S, 6);

	print S $message . "\n";

	print S ".\n";
	$buf = readSock(S, 6);

	print S "QUIT\n";

	close S;

	return("0");
} #end of RealSendMail

############################################################
#
# subroutine: SendMail
#   Usage:
#     &SendMail("My name", "me@myhouse.com", "Your name",
#       "you@yourhouse.com", "My subject", "My message"[, "To group"]);
#
#   Parameters:
#     $fromname    = Name of sender
#     $fromuser    = Full Email address of sender
#     $toname      = Name of receiver
#     $touser      = Full Email address of receiver
#     $subject     = Subject of message
#     $messagebody = Body of message including newlines.
#     $group       = Group of receivrs
#
#   Output:
#     None
#
############################################################

sub SendMail {
	my($fromname, $from, $toname, $to, $subject, $messagebody, $group) = @_;

	my($fromuser, $fromsmtp, $touser, $tosmtp);


	# This routine takes the simpler parameters of
	# send_mail and breaks them up into the parameters
	# to be sent to RealSendMail.
	#
	$fromuser = $from;
	$touser = $to;

	#
	# Split is used to break the address up into
	# user and hostname pairs.  The hostname is the
	# 2nd element of the split array, so we reference
	# it with a 1 (since arrays start at 0).
	#
	$fromsmtp = (split(/\@/,$from))[1];
	$tosmtp = (split(/\@/,$to))[1];

	# Actually call the sendmail routine with the
	# newly generated parameters
	#
	return(&RealSendMail($fromname, $fromuser, $fromsmtp, $toname, $touser, $tosmtp, $subject, $messagebody, $group));
} # End of send_mail

############################################################
#
# subroutine: readSock
#   Usage:
#     &readSocket(SOCKET_HANDLE, $timeout);
#
#   Parameters:
#     SOCKET_HANDLE = Handle to an allocated Socket
#     $timeout = amount of time readSock is allowed to
#                wait for input before timing out
#                (measured in seconds)
#
#   Output:
#     Buffer containing what was read from the socket
#
############################################################

sub readSock {
	my($handle, $endtime) = @_;
	my($localbuf,$buf);
	my($rin,$rout,$nfound);

	# Set endtime to be time + endtime.
	$endtime += time;

	# Clear buffer
	$buf = "";

	# Clear $rin (Read Input variable)
	$rin = '';
	# Set $rin to be a vector of the socket file handle
	vec($rin, fileno($handle), 1) = 1;

	# nfound is 0 since we have not read anything yet
	$nfound = 0;

	# Loop until we time out or something was read
	readSocket:
	while (($endtime > time) && ($nfound <= 0)) {
		# Read 1024 bytes at a time
		$length = 1024;
		# Preallocate buffer
		$localbuf = " " x 1025;
		# NT does not support select for polling to see if
		# There are characters to be received.  This is important
		# Because we dont want to block if there is nothing
		# being received.
		$nfound = 1;
		if ($gMailOS ne "NT") {
			# The following polls to see if there is anything in the input
			# buffer to read.  If there is, we will later call the sysread routine
			$nfound = select($rout=$rin, undef, undef,.2);
		}
	}

	# If we found something in the read socket, we should
	# get it using sysread.
	if ($nfound > 0) {
		$length = sysread($handle, $localbuf, 1024);
		if ($length > 0) {
			$buf .= $localbuf;
		}
	}

	# Return the contents of the buffer
	$buf;
}

sub setHtmlMail {
	$gSMTP_HtmlMail = 1;
}

sub setTextMail {
	$gSMTP_HtmlMail = 0;
}

sub setKoreanMail {
	$gSMTP_KoreanMail = 1;
}

sub setEnglishMail {
	$gSMTP_KoreanMail = 0;
}

1;