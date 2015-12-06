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
# 이것만은 꼭!!!!
#     이 스크립트가 실행되는 서버에 SMTP 서버가 설치되어 있어야만 동작합니다.
#
#
# 원본에서 바뀐 점 :
#     1. 보낸 이의 메일 주소를 받은 이의 Netscape Messenger 등에서
#        제대로 보이지 않는 문제 해결
#     2. 보낸 이의 이름을 같이 전송하도록 수정 (아래 예의 'My name')
#     3. 메일 받을 그룹을 지정 가능 (아래 예의 'group')
#        (group는 받을 이의 메일 주소가 기록된 텍스트 파일이며
#         생략 시는 받을 사람 주소로만 전송, 그룹 사용 시 받을 사람
#         주소는 ""로 설정)
#     4. HTML 메일을 보낼 수 있도록 함 (&setHtmlMail, &setTextMail)
#     5. 메일 인코딩을 한글(EUC-KR)로 보낼 수 있도록 함 (&setKoreanMail, &setEnglishMail)
#     6. $gMailOS 변수를 적지 않았을 경우 자동 선택 기능 추가
#     7. 에러 발생시 에러 메시지를 리턴, 에러가 없을시는 "0"을 리턴
#
# 사용법 :
#     $errorCode = &SendMail("My name", "me@myhouse.com", "Your name",
#                            "you@yourhouse.com", "My subject", "My message");
# 또는
#     $errorCode = &SendMail("My name", "me@myhouse.com", "Your name",
#                            "you@yourhouse.com", "My subject", "My message", "To group");
#
# 에러처리 예:
#     &error($errorCode) if ($errorCode ne "0");
#
# 사용 예:
#     1. 일반적 사용    : $errorCode = &send_mail("대석", "kndol@kndol.sarang.net", "you@yourhouse.com", "send_mail 사용법", "$message");
#     2. 메일 그룹 사용 : $errorCode = &send_mail("대석", "kndol@kndol.sarang.net", "", "send_mail 사용법", "$message", "C:\mail_list\group.txt");
#        받는 사람 메일 주소와 받는 그룹 동시 사용 가능
#
# 참고 :
#     1. HTML 메일을 보내기 위해서는 SendMail을 호출하기 전에 &setHtmlMail을 호출해야 합니다.
#        텍스트 메일은 &setTextMail입니다.
#     2. 한글 인코딩은 &setKoreanMail, 영문 메일은 &setEnglishMail을 먼저 호출해야 합니다.
#     3. set...Mail을 호출하지 않고 바로 SendMail을 사용하면 영문 텍스트 메일로 보냅니다.
#
#
#   GNU GPL(General Public License) 또는 the Artistic License에 의해
#   마음대로 복사 및 재배포, 수정이 가능합니다. Perl v5.x 용으로 제작되었으며,
#   수정 및 재배포시는 제작자 및 수정자의 이름을 포함하여 재배포하시기 바랍니다.
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

# 소켓 연결 실패시 재시도 회수
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