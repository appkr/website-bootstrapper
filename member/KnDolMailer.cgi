#!/usr/bin/perl

########################     KnDolMailer Ver 1.0.3     ########################
###                                                                         ###
###    배포자 : 김대석 (kndol@kndol.sarang.net)                             ###
###                                                                         ###
### 이 스크립트는 http://kndol.sarang.net/~CgiMaker/ 에서 다운로드          ###
### 받으실 수 있습니다.                                                     ###
###                                                                         ###
### 이 스크립트에 사용된 이미지의 대부분은 위키 소프트의 WeekyMailer에서    ###
### 가져 왔습니다.                                                          ###
### 레이아웃은 위키 메일러를 참조하였습니다.                                ###
### 이미지와 레이아웃을 사용할 수 있도록 허락해 주신 위키 소프트 측에       ###
### 감사 드립니다.                                                          ###
### 위키 소프트의 주소는 http://weeky.pr.co.kr 입니다.                      ###
###                                                                         ###
### 상업적 목적이 아니라면 수정 및 재배포는 자유입니다.                     ###
### 수정 및 재배포시 가급적이면 원본을 밝혀주시면 감사하겠습니다.           ###
### 그리고, 에러 수정이나 개선 시에는 제가 참고할 수 있도록 알려 주시면     ###
### 아주 고맙지요.                                                          ###
###                                                                         ###
###############################################################################
###                                                                         ###
### 알려진 문제 :                                                           ###
###     NT서버에서 EMWAC의 IMS를 SMTP 서버로 사용시 가끔씩 소켓 연결에      ###
###   실패했다는 에러가 납니다. 이유는 제가 SMTP 서버의 프로토콜을 깊게     ###
###   연구해 보지 못한 관계로 아직 찾지 못했습니다.                         ###
###   이 문제에 대한 해결 방안을 아시는 분은 연락 주시기 바랍니다.          ###
###                                                                         ###
###############################################################################
###                                                                         ###
###            *************************************************            ###
###            *          Fight and Posses the Land!           *            ###
###            *                - Deut 2:24 -                  *            ###
###            *************************************************            ###
###            * Homepage : http://kndol.sarang.net/           *            ###
###            *          : http://kndol.sarang.net/~CgiMaker/ *            ###
###            * e-mail   : kndol@kndol.sarang.net             *            ###
###            *************************************************            ###
###            *                                               *            ###
###            *   ______ __        ________        ______     *            ###
###            *   ___  //_/_______ ___  __ \______ ___  /     *            ###
###            *   __  ,<   __  __ \__  / / /_  __ \__  /      *            ###
###            *   _  /| |  _  / / /_  /_/ / / /_/ /_  /       *            ###
###            *   /_/ |_|  /_/ /_/ /_____/  \____/ /_/        *            ###
###            *                                               *            ###
###            *************************************************            ###
###                                                                         ###
###                                                  2000. 4. 16, KnDol     ###
###                                                                         ###
###############################################################################

$gCgiUrl = $ENV{'SCRIPT_NAME'};
$gCgiVer = "1.0.3";

&getDefaultCfg;
&parseArgument;
&getConfig;

if($FORM{'act'} eq "") { &writeMail; }
elsif($FORM{'act'} eq "writeMail") { &writeMail; }
elsif($FORM{'act'} eq "Error") { &Error; }
elsif($FORM{'act'} eq "sendMail") { &sendMail; }
elsif($FORM{'act'} eq "Admin") { &Admin; }
elsif($FORM{'act'} eq "AdminMode") { &AdminMode; }
elsif($FORM{'act'} eq "saveValue") { &saveValue; }
else { &writeMail; }

exit;

sub getDefaultCfg {
	if (open(TEST, "KnDolMailer.config")) {
		close(TEST);
		require "KnDolMailer.config";
	}

	if ($gMailDir eq "") {
		my($path) = $0;
		$path =~ s/\\/\//g;
		$path =~ s/\/KnDolMailer.cgi$//i;
		$path =~ s/\/KnDolMailer.pl$//i;
		$gMailDir = $path;
	}
	if ($gImageUrl eq "") {
		my($CgiBinUrl) = $gCgiUrl;
		$CgiBinUrl =~ s/KnDolMailer.cgi$//i;
		$CgiBinUrl =~ s/KnDolMailer.pl$//i;
		$gImageUrl = "http://$ENV{'SERVER_NAME'}" . $CgiBinUrl . "images";
	}
	if ($gRootMail eq "") {
		$server = $ENV{'SERVER_NAME'};
		$gRootMail = 'webmaster@' . $server;
	}
}

sub parseArgument {
	my($buffer,$data,$name,$value);
	my(@data);

	if($ENV{'REQUEST_METHOD'} eq "GET") {
		$buffer = $ENV{'QUERY_STRING'};
	}
	else {
		read(STDIN,$buffer,$ENV{'CONTENT_LENGTH'});
	}
	@data = split(/&/,$buffer);
	foreach $data (@data) {
		($name,$value) = split(/=/,$data);
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
		$FORM{$name} = $value;
	}
}

sub getConfig {
	my(@data);
	$gConfigFile = ($FORM{'cfg'} ne "") ? "$gMailDir/$FORM{'cfg'}" : "$gMailDir/config.cfg";

	open(HANDLE,"$gConfigFile");
	@data = <HANDLE>;
	close(HANDLE);
	@gConfigValue = split(/\|/,$data[$i]);
	chomp($gConfigValue[$#gConfigValue]) if ($gConfigValue[$#gConfigValue] =~ /\n$/);
}

sub writeMail {
	if($gConfigValue[0] eq "") {
		&AdminMode;
		exit;
	}

	if ($FORM{'name'} ne "" && $FORM{'mail'} ne "") {
		$gConfigValue[0]="$FORM{'name'}";
		$gConfigValue[1]="$FORM{'mail'}";
	}

	$gOnLoad = " onload=\"form.fromname.focus();\"";
	&getCookie;

	$tastyle = ($ENV{'HTTP_USER_AGENT'}=~/ MSIE /) ? " style=\"border-color:black; background:rgb(240,255,240) url($gImageUrl/bg-picture.gif) no-repeat fixed right bottom;\""
	                                               : "";

	&header;
	print <<_BODY_;
<div align=$gConfigValue[3]><table border="3" cellpadding="4" cellspacing="0" width="560" bordercolordark="#C1E1F9" bordercolorlight="#0B446F">
<tr><form name=form method=post action=\"$gCgiUrl\"><input type=hidden name=act value=sendMail><input type=hidden name=cfg value=$FORM{'cfg'}><td>
	<table border=0 cellpadding=0 cellspacing=0 width=100%>
		<tr><td height=20 colspan=2 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>
		<tr><td width=222 valign=top rowspan=2>
			<table border=0 cellspacing=0 width=218 height=100>
				<tr><td valign=bottom colspan=2><p><img src=$gImageUrl/from.gif border=0></td></tr>
				<tr><td width=30><p><font size=2>이름</font></td>
				<td width=188><p><input type=text name=fromname size=22 style="background-color:rgb(225,255,255);border-color:black;" value="$gCookieName" tabindex="1"></td></tr>
				<tr><td width=30><p><font size=2>메일</font></td>
				<td width=188><p><input type=text name=frommail size=22 style="background-color:rgb(225,255,255);border-color:black;" value="$gCookieMail" tabindex="2"></td>
				</tr>
			</table><br>
			<table border=0 cellspacing=0 width=218 height=100>
				<tr><td valign=bottom colspan=2><p><font size=2><img src=$gImageUrl/to.gif border=0></font></td></tr>
				<tr><td width=30><p><font size=2>이름</font></td>
				<td width=188><p><input type=text name=toname size=22 style="color:navy;background-color:rgb(255,255,240);border-color:black;" value="$gConfigValue[0]" tabindex="3"></td></tr>
				<tr><td width=30><p><font size=2>메일</font></td>
				<td width=188><p><input type=text name=tomail size=22 style="color:navy;background-color:rgb(255,255,240);border-color:black;" value="$gConfigValue[1]" tabindex="4"></td>
				</tr>
			</table><br>
			<table border=0 cellpadding=0 cellspacing=0 width=200>
				<tr><td valign=bottom><br><br><br><p align=center><a href="$gCgiUrl?act=Admin&cfg=$FORM{'cfg'}" tabindex="8"><img src=$gImageUrl/admin.gif border=0 alt=관리자모드></a>
				<a href="http://kndol.sarang.net/~CgiMaker/" target=_blank tabindex="9"><font size=2>KnDol's CgiMaker!</font></a></td>
				</tr>
			</table>
		</td>
		<td width=322 valign=top>
			<table border=0 cellpadding=0 cellspacing=0 width=320>
				<tr><td width=206 valign=bottom><p align=left><img src=$gImageUrl/title.gif border=0></td>
				<td width=110 rowspan=3><p align=right><a href="http://kndol.sarang.net/~CgiMaker/" target=_blank tabindex="10"><img src=$gImageUrl/stamp.gif border=0></a></td></tr>
				<tr><td width=206><p><input type=text name=title size=27 style="color:black;background-color:rgb(255,238,255);border-color:black;" tabindex="5"></td></tr>
				<tr><td width=206 valign=bottom><p align=left><img src=$gImageUrl/message.gif border=0></td>
				</tr>
			</table>
		<p align=left><textarea name=contents rows=10 cols=42$tastyle tabindex="6"></textarea></td></tr>
		<tr><td width=322 height=40><center><p><input type=image src=$gImageUrl/send.gif border=0 tabindex="7"></center></td></tr>
		<tr><td height=20 colspan=2 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>
	</table>
</td></form></tr>
</table></div>
_BODY_

	&footer;
}

sub header {
	my($mode) = $_[0];

	$gConfigValue[6] =~ s/\\n/\n/g;
	print "Content-Type: text/html\n\n";
	print "<html><head><title>KnDolMailer Ver $gCgiVer";
	print " - $mode" if ($mode ne "");
	print "</title>\n";
	print "<style type=text/css>\n";
	print "<!--\n";
	print "A:link { text-decoration:none;color:blue;}\n";
	print "A:visited { text-decoration:none;color:blue;}\n";
	print "A:active { text-decoration:none;color:blue;}\n";
	print "A:hover { text-decoration:underline;color:red;}\n";
	print "-->\n";
	print "</style></head>\n";
	print "<body bgcolor=white text=black";
	print " background=\"$gConfigValue[5]\"" if ($gConfigValue[5] ne "");
	print "$gOnLoad>\n";
	print "$gConfigValue[6]\n";
}

sub footer {
	$gConfigValue[7] =~ s/\\n/\n/g;
	print "$gConfigValue[7]\n</body></html>";
}

sub sendMail {
	my($mailbody);

	$fromname="$FORM{'fromname'}";
	if($FORM{'frommail'} =~ /^.+\@.+(\..+)+/) {
		$frommail="$FORM{'frommail'}";
		$frommail =~ s/\|/&#124;/g;
	}
	else {
		&Error("보내는 사람 메일 주소가 틀리거나 입력하지 않았습니다.");
	}
	$toname=$FORM{'toname'};
	if($FORM{'tomail'} =~ /^.+\@.+(\..+)+/) {
		$tomail="$FORM{'tomail'}";
		$tomail =~ s/\|/&#124;/g;
	}
	else {
		&Error("받는 사람 메일 주소가 틀리거나 입력하지 않았습니다.");
	}
	if($FORM{'title'} ne "") {
		$title=$FORM{'title'};
		$title =~ s/\|/&#124;/g;
	}
	else {
		&Error("보낼 편지의 제목을 입력하지 않았습니다.");
	}

	if($FORM{'contents'} ne "") {
		$contents=$FORM{'contents'};
		$contents =~ s/\|/&#124;/g;
	}
	else {
		&Error("보낼 편지의 내용을 입력하지 않았습니다.");
	}

	$contents =~ s/\r\n\r\n/<p>/g;
	$contents =~ s/\r\n/<br>/g;
	$contents =~ s/\|/&#124;/g;

	require "kndol-smtpmail.pl";

	$mailbody = "<html>\n";
	$mailbody .= "<meta http-equiv=Content-Type content=text/html;charset=EUC-KR>\n";
	$mailbody .= "<head><title>KnDolMailer Ver $gCgiVer</title>\n";
	$mailbody .= "<style type=text/css>\n";
	$mailbody .= "<!--\n";
	$mailbody .= "A:link { text-decoration:none; color:blue;}\n";
	$mailbody .= "A:visited { text-decoration:none; color:blue;}\n";
	$mailbody .= "A:active { text-decoration:none; color:blue;}\n";
	$mailbody .= "A:hover { text-decoration:underline; color:red;}\n";
	$mailbody .= "-->\n";
	$mailbody .= "</style>\n";
	$mailbody .= "</head>\n";
	$mailbody .= "<body bgcolor=white text=black>\n";
	$mailbody .= "<div align=left><table border=\"3\" cellpadding=\"4\" cellspacing=\"0\" width=\"560\" bordercolordark=\"#C1E1F9\" bordercolorlight=\"#0B446F\"><tr><td>\n";
	$mailbody .= "<table border=0 cellpadding=0 cellspacing=0 width=100%>\n";
	$mailbody .= "<tr bgcolor=white><td colspan=3 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	$mailbody .= "<tr bgcolor=white><td width=100><p><img src=$gImageUrl/fromed.gif border=0></td>\n";
	$mailbody .= "<td width=334><p><font size=2>$fromname (<a href=mailto:$frommail>$frommail</a>)</font></td>\n";
	$mailbody .= "<td width=110 rowspan=3><p align=right><a href=\"http://kndol.sarang.net/~CgiMaker/\" target=_blank><img src=$gImageUrl/stamp.gif border=0></a></td></tr>\n";
	$mailbody .= "<tr bgcolor=white><td width=100><p><font size=2><img src=$gImageUrl/to.gif border=0></font></td>\n";
	$mailbody .= "<td width=334><p><font size=2>$toname (<a href=mailto:$tomail>$tomail</a>)</font></td></tr>\n";
	$mailbody .= "<tr bgcolor=white><td width=100><p align=left><img src=$gImageUrl/title.gif border=0></td>\n";
	$mailbody .= "<td width=334><p><font size=2>$title</font></td></tr>\n";
	$mailbody .= "<tr bgcolor=white><td colspan=3><br><p align=left><img src=$gImageUrl/messaged.gif border=0></p>\n";
	$mailbody .= "<p align=center><table cellpadding=\"7\" cellspacing=\"0\" width=\"520\" style=\"border:1 solid black; background:rgb(240,255,240) url($gImageUrl/bg-picture.gif) no-repeat fixed right bottom;\" align=\"center\"><tr><td align=\"left\">\n";
	$mailbody .= "<font style=\"line-height:140%; font-size: 10pt;\">$contents</font>\n</td></tr></table>\n</p></td></tr>\n";
	$mailbody .= "<tr bgcolor=white><td colspan=3 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	$mailbody .= "<tr><td colspan=3><br><p align=center><font size=2 color=red>KnDolMailer Ver $gCgiVer </font><font size=2>♧ </font><a href=\"$gConfigValue[8]\" target=_blank>\n";
	$mailbody .= "<font size=2>$gConfigValue[9]</font></a></td></tr>\n";
	$mailbody .= "</table></td></tr></table></div>\n";
	$mailbody .= "</body></html>\n";

	if ($gConfigValue[10] == 1) {
		&setHtmlMail;
		&setKoreanMail;
		$ErrorCode = &SendMail("$fromname", "$frommail", "$toname", "$tomail", "$title", "$mailbody");
		&Error("메일 서버에 문제가 있어서 메일을 보낼 수 없습니다.<br>$ErrorCode<br><br>문제가 계속 되면 <a href=\"mailto:$gRootMail\">서버 관리자</a>에게 연락 주십시오.") if ($ErrorCode ne "0");
	}
	else {
		&Error("환경 설정 오류입니다.<br><br>문제가 계속 되면 <a href=\"mailto:$gConfigValue[1]\">$gConfigValue[0]</a>님에게 연락 주십시오.") if ($gConfigValue[11] eq "");
		&Error("$gConfigValue[11]을(를) 실행할 수 없습니다.<br><br>문제가 계속 되면 <a href=\"mailto:$gRootMail\">서버 관리자</a>에게 연락 주십시오.") unless (-e $gConfigValue[11]);
		open (MAIL, "|$gConfigValue[11] -t $tomail") || &Error("$gConfigValue[11]을(를) 실행할 수 없습니다.<br><br>문제가 계속 되면 <a href=\"mailto:$gRootMail\">서버 관리자</a>에게 연락 주십시오.");
		my($message) = "MIME-Version: 1.0\n";
		$message .= "Content-Transfer-Encoding: 8bit\n";
		$message .= "Content-Type: text/html; charset=EUC-KR\n";
		$message .= "From: $fromname <$frommail>\n";
		$message .= "To: $toname <$tomail>\n";
		$message .= "Subject: $title\n";
		$message .= $mailbody;
		print MAIL $message;
		close (MAIL);
	}

	print "Set-Cookie: KnDolMailer=$fromname:$frommail; expires=Thu, 31-Dec-2099 00:00:00 GMT\n";

	&header("Transfer Completed - $gConfigValue[11]");
	print "<div align=$gConfigValue[3]><table border=\"3\" cellpadding=\"4\" cellspacing=\"0\" width=\"560\" bordercolordark=\"#C1E1F9\" bordercolorlight=\"#0B446F\"><tr><td>\n";
	print "<table border=0 cellpadding=0 cellspacing=0 width=100%>\n";
	print "<tr><td colspan=3 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	print "<tr><td width=100><p><img src=$gImageUrl/fromed.gif border=0></td>\n";
	print "<td width=334><p><font size=2>$fromname ($frommail)</font></td>\n";
	print "<td width=110 rowspan=3><p align=right><a href=\"http://kndol.sarang.net/~CgiMaker/\" target=_blank><img src=$gImageUrl/stamp.gif border=0></a></td></tr>\n";
	print "<tr><td width=100><p><font size=2><img src=$gImageUrl/to.gif border=0></font></td>\n";
	print "<td width=334><p><font size=2>$toname ($tomail)</font></td></tr>\n";
	print "<tr><td width=100><p align=left><img src=$gImageUrl/title.gif border=0></td>\n";
	print "<td width=334><p><font size=2>$title</font></td></tr>\n";
	print "<tr><td colspan=3><br><p align=left><img src=$gImageUrl/messaged.gif border=0></p>\n";
	print "<p align=center><table cellpadding=\"7\" cellspacing=\"0\" width=\"520\" style=\"border:1 solid black; background:rgb(240,255,240) url($gImageUrl/bg-picture.gif) no-repeat fixed right bottom;\" align=\"center\"><tr><td align=\"left\">\n";
	print "<font style=\"line-height:140%; font-size: 10pt;\">$contents</font>\n</td></tr></table>\n</p></td></tr>\n";
	print "<tr><td colspan=3 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	print "<tr><td colspan=3><br><p align=center><font size=2>$fromname($frommail)님의 메일을<br>$toname($tomail)님께 보냈습니다.</font></p>\n";
	print "<p align=center><a href=\"$gCgiUrl?cfg=$FORM{'cfg'}\"><font size=2>[ 새편지 쓰기 ]</font></a>&nbsp;&nbsp;&nbsp;\n";
	print "<a href=$gConfigValue[4]><font size=2>[ 홈으로 가기 ]</font></a>" if ($gConfigValue[4] ne "");
	print "</p>\n" ;
	print "<p align=center><font size=2 color=red>KnDolMailer Ver $gCgiVer </font><font size=2>♧ </font><a href=\"http://kndol.sarang.net/~CgiMaker/\" target=_blank>\n";
	print "<font size=2>KnDol's CgiMaker!</font></a></td></tr>\n";
	print "</table></td></tr></table></div>\n";
	&footer;
}

sub Error {
	my($errcode) = $_[0];

	&header("Error!");
	print "<div align=$gConfigValue[3]><table border=\"3\" cellpadding=\"4\" cellspacing=\"0\" width=\"560\" bordercolordark=\"#C1E1F9\" bordercolorlight=\"#0B446F\"><tr><td>\n";
	print "<table border=0 cellpadding=0 cellspacing=0 width=100%>\n";
	print "<tr><td background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	print "<tr><td><br><p align=center><font size=3 color=red><b>♧ Error! ♧</b></font></p>\n";
	print "<p align=center><font size=2>$errcode</font></p>\n";
	print "<p align=center><a href='javascript:history.back()'><font size=2>[ 다시입력 ]</font></a><br><br></td></tr>\n";
	print "<tr><td colspan=3 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	print "<tr><td colspan=3><br><p align=center><font size=2 color=red>KnDolMailer Ver $gCgiVer </font><font size=2>♧ </font><a href=\"http://kndol.sarang.net/~CgiMaker/\" target=_blank>\n";
	print "<font size=2>KnDol's CgiMaker!</font></a></td></tr>\n";
	print "</table></td></tr></table></div>\n";
	&footer;
	exit;
}

sub Admin {
	&header("관리자 접속");
	print "<form method=post action=\"$gCgiUrl\"><input type=hidden name=act value=AdminMode><input type=hidden name=cfg value=$FORM{'cfg'}>\n";
	print "<div align=$gConfigValue[3]><table border=\"3\" cellpadding=\"4\" cellspacing=\"0\" width=\"560\" bordercolordark=\"#C1E1F9\" bordercolorlight=\"#0B446F\"><tr><td>\n";
	print "<table border=0 cellpadding=0 cellspacing=0 width=100%>\n";
	print "<tr><td colspan=3 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";

	print "<tr><td colspan=3 align=center><br><p><font size=2 color=blue>관리자 비밀번호를 입력하세요.</font></p>\n";
	print "<p><input type=password name=pass size=17 maxlength=8 style=color:black;background-color:rgb(255,238,255);border-color:black;></p></td></tr>\n";
	print "<tr><td height=60 align=right width=260><input type=image src=$gImageUrl/ok.gif border=0></td><td width=24><p>&nbsp;</td>\n";
	print "<td align=left width=260><a href=\"$gCgiUrl\"><img src=$gImageUrl/cancel.gif border=0></a></td></tr>\n";
	print "<tr><td colspan=3 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	print "<tr><td colspan=3><br><p align=center><font size=2 color=red>KnDolMailer Ver $gCgiVer </font><font size=2>♧ </font><a href=\"http://kndol.sarang.net/~CgiMaker/\" target=_blank>\n";
	print "<font size=2>KnDol's CgiMaker!</font></a></td></tr>\n";
	print "</form></table></td></tr></table></div>\n";
	&footer;
}

sub AdminMode {
	if($FORM{'pass'} ne $gConfigValue[2]) {
		&Error("관리자 비밀번호가 틀립니다.");
		exit;
	}

	$gConfigValue[6] =~ s/\\n/\n/g;
	$gConfigValue[7] =~ s/\\n/\n/g;

	&header("관리자 모드");
	print "<form method=post action=\"$gCgiUrl\"><input type=hidden name=act value=saveValue><input type=hidden name=cfg value=$FORM{'cfg'}>\n";
	print "<div align=$gConfigValue[3]><table border=\"3\" cellpadding=\"4\" cellspacing=\"0\" width=\"560\" bordercolordark=\"#C1E1F9\" bordercolorlight=\"#0B446F\"><tr><td>\n";
	print "<table border=0 cellpadding=0 cellspacing=0 width=100%>\n";
	print "<tr><td background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	print "<tr><td><br><div align=center><table border=1 cellpadding=7 cellspacing=0 width=460 bordercolor=black><tr><td bgcolor=gray>\n";
	print "<p align=center><font size=2 color=white><b>KnDolMailer Ver $gCgiVer - 관리자 모드</b></font></td></tr></table></div><br>\n";
	if($gConfigValue[0] eq "") {
		print "<p align=center><font size=2 color=red><b>설치에 성공하셨군요. 아래의 모든 사항을 꼭 입력해 주세요.</b></font></p>\n";
		$gConfigValue[10] = 1;
		$gConfigValue[11] = "/usr/lib/sendmail";
	}
	print "<div align=center><table border=0 cellpadding=3 cellspacing=0 width=460>\n";
	print "<tr colspan=4><td width=100><p align=center><font size=2>비밀번호 변경</font></td>\n";
	print "<td width=130 align=center><p><input type=password name=pass1 size=17 maxlength=8 style=\"color:black;background-color:rgb(255,238,255);border-color:black;\"></td>\n";
	print "<td width=100><p align=center><font size=2>다시입력</font></td>\n";
	print "<td width=130 align=center><p><input type=password name=pass2 size=17 maxlength=8 style=\"color:black;background-color:rgb(255,238,255);border-color:black;\"></td></tr>\n";
	print "<tr><td width=100><p align=center><font size=2>관리자 이름</font></td>\n";
	print "<td width=130 align=center><p><input type=text name=name size=17 style=\"background-color:rgb(225,255,255);border-color:black;\" value=\"$gConfigValue[0]\"></td>\n";
	print "<td width=100><p align=center><font size=2>전자메일</font></td>\n";
	print "<td width=130 align=center><p><input type=text name=email size=17 style=\"background-color:rgb(225,255,255);border-color:black;\" value=\"$gConfigValue[1]\"></td></tr>\n";
	print "<tr><td width=100><p>&nbsp;</td><td width=130><p>&nbsp;</td><td width=100><p>&nbsp;</td><td width=130><p>&nbsp;</td></tr></table></div>\n";

	print "<div align=center><table border=0 cellpadding=3 cellspacing=0 width=460>\n";
	print "<tr><td bgcolor=#C0FFC0><p align=center><font size=2 color=blue>메일 보낼 때 필요한 홈페이지 정보 설정</font></td></tr></table></div>\n";

	print "<br><div align=center><table border=0 cellpadding=3 cellspacing=0 width=460>\n";
	print "<tr><td width=120><p align=center><font size=2>홈페이지 URL</font></td>\n";
	print "<td><p><input type=text name=homepage size=50 style=\"color:navy;background-color:rgb(255,240,255);border-color:black;\" value=\"$gConfigValue[8]\"></td></tr>\n";
	print "<tr><td width=120><p align=center><font size=2>홈페이지 이름</font></td>\n";
	print "<td><p><input type=text name=homename size=50 style=\"color:navy;background-color:rgb(240,255,255);border-color:black;\" value=\"$gConfigValue[9]\"></td></tr>\n";
	print "</table></div>\n";

	print "<br><div align=center><table border=0 cellpadding=3 cellspacing=0 width=460>\n";
	print "<tr><td bgcolor=#C0FFC0><p align=center><font size=2 color=blue>KnDolMailer의 위치 및 모양 지정</font></td></tr></table></div>\n";

	print "<br><div align=center><table border=0 cellpadding=3 cellspacing=0 width=460>\n";
	print "<tr><td width=100><p align=center><font size=2>메일러 정렬</font></td>\n";
	if($gConfigValue[3] eq "left") {
		print "<td width=120><p><input type=radio name=align value=left checked><font size=2> 왼쪽</font></td>\n";
	}
	else {
		print "<td width=120><p><input type=radio name=align value=left><font size=2> 왼쪽</font></td>\n";
	}
	if($gConfigValue[3] eq "center") {
		print "<td width=120><p><input type=radio name=align value=center checked><font size=2> 가운데</font></td>\n";
	}
	else {
		print "<td width=120><p><input type=radio name=align value=center><font size=2> 가운데</font></td>\n";
	}
	if($gConfigValue[3] eq "right") {
		print "<td width=120><p><input type=radio name=align value=right checked><font size=2> 오른쪽</font></td></tr>\n";
	}
	else {
		print "<td width=120><p><input type=radio name=align value=right><font size=2> 오른쪽</font></td></tr>\n";
	}
	print "<tr><td width=100><p align=center><font size=2>홈버튼 URL</font></td>\n";
	print "<td colspan=3 width=360><p><input type=text name=homeurl size=50 style=color:navy;background-color:rgb(255,255,240);border-color:black; value=\"$gConfigValue[4]\"></td></tr>\n";
	print "<tr><td width=100><p align=center><font size=2>배경그림</font></td>\n";
	print "<td colspan=3 width=360><p><input type=text name=bgimage size=50 style=color:navy;background-color:rgb(240,255,240);border-color:black; value=\"$gConfigValue[5]\"></td></tr>\n";
	print "</table></div>\n";
	print "<br><div align=center><table border=0 cellpadding=3 cellspacing=0 width=460>\n";
	print "<tr><td width=50%><p align=center><font size=2>BODY 앞부분</font></td>\n";
	print "<td width=50%><p align=center><font size=2>BODY 뒷부분</font></td></tr>\n";
	print "<tr><td width=50%><p align=center><font size=2><textarea name=header rows=5 cols=30 style=\"border-color:black; background:rgb(240,255,250);\">$gConfigValue[6]</textarea></font></td>\n";
	print "<td width=50%><p align=center><font size=2><textarea name=tailer rows=5 cols=30 style=\"border-color:black; background:rgb(240,250,255);\">$gConfigValue[7]</textarea></font></td></tr>\n";
	print "</table></div>\n";

	print "<br><div align=center><table border=0 cellpadding=3 cellspacing=0 width=460>\n";
	print "<tr><td bgcolor=#C0FFC0><p align=center><font size=2 color=blue>Sendmail 관련 정보 설정</font></td></tr></table></div>\n";

	print "<br><div align=center><table border=0 cellpadding=3 cellspacing=0 width=460>\n";
	print "<tr><td width=100><p align=center><font size=2>내장 메일 모듈</font></td>\n";

	$sel = ($gConfigValue[10] == 1) ? "<option value=1 selected>사용함</option><option value=0>사용 안함</option>"
	                                : "<option value=1>사용함</option><option value=0 selected>사용 안함</option>";

	print "<td><select name=useMailModule style=\"border:1 solid siver; background:rgb(255,255,240);\">$sel</select><font size=2> &nbsp;&nbsp;&nbsp;&nbsp;(사용 안할시 sendmail 사용)</font></td></tr>\n";

	print "<tr><td width=100><p align=center><font size=2>Sendmail 경로</font></td>\n";
	print "<td><input type=text name=pathSendmail size=46 style=\"color:navy;background-color:rgb(240,255,255);border-color:black;\" value=\"$gConfigValue[11]\"></td></tr>\n";
	print "</table></div>\n";

	print "</td></tr><tr><td height=50 align=center><p><input type=image src=$gImageUrl/save.gif border=0></td></tr>\n";
	print "<tr><td colspan=3 background=$gImageUrl/line.gif><p>&nbsp;</td></tr>\n";
	print "<tr><td colspan=3><br><p align=center><font size=2 color=red>KnDolMailer Ver $gCgiVer </font><font size=2>♧ </font><a href=\"http://kndol.sarang.net/~CgiMaker/\" target=_blank>\n";
	print "<font size=2>KnDol's CgiMaker!</font></a></td></tr>\n";
	print "</form></table></td></tr></table></div>\n";
	&footer;
}

sub saveValue {
	if($FORM{'pass1'} eq "" || $FORM{'pass1'} eq " ") { $pass=$gConfigValue[2]; }
	else { $pass=$FORM{'pass1'}; }
	if($FORM{'align'} eq "") { $align=$gConfigValue[3]; }
	else { $align=$FORM{'align'}; }
	$FORM{'header'} =~ s/\n/\\n/g;
	$FORM{'header'} =~ s/\r//g;
	$FORM{'tailer'} =~ s/\n/\\n/g;
	$FORM{'tailer'} =~ s/\r//g;
	open(HANDLE,">$gConfigFile") || &Error("환경 설정 파일($gConfigFile)을 저장할 수 없습니다.");
	print HANDLE "$FORM{'name'}|$FORM{'email'}|$pass|$align|$FORM{'homeurl'}|$FORM{'bgimage'}|$FORM{'header'}|$FORM{'tailer'}|$FORM{'homepage'}|$FORM{'homename'}|$FORM{'useMailModule'}|$FORM{'pathSendmail'}\n";
	close(HANDLE);

	print "Content-Type: text/html\n\n";
	print "<html><head><META http-equiv=refresh content='0; url=$gCgiUrl?cfg=$FORM{'cfg'}'></head></html>\n";
}

sub getCookie {
    my($cookie, $value);

	foreach (split(/; /, $ENV{'HTTP_COOKIE'})) {
		($cookie, $value) = split(/=/);
		($gCookieName, $gCookieMail)  = split(/:/, $value)  if ($cookie eq "KnDolMailer");
	}
}