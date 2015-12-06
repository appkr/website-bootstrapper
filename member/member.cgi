#!/usr/bin/perl

#######################     ȸ������ member.cgi     ################################
# �� ��ũ��Ʈ�� �輼����(sepal.woorizip.com), ��뼮��(Kndol.sarang.net/~cgiMaker)��
# ����� �ּҷ��� �����Ͽ� ���ֿ�(www.webweaver.pe.kr)�� ���� ���α׷��Դϴ�.
#-----------------------------------------------------------------------------------
# �� ���α׷��� ������� ���Ͽ� �߻��ϴ� ���ؿ� ���Ͽ��� å������ �ʽ��ϴ�.
#
# �� ���α׷��� �����ڰ� ȸ���鿡�� ���������� �� ���̿������� ����ϰ�, 
# �� �ּ������� �� ������ ����ϱ� ���� ��������ϴ�.
# ������ �̾��Ͽ��� ���ȿ� �Ű����ϴ� �е��� ������� ���ʽÿ�.
# 
# �������� ���Ͻô� ��� ���� ��������������� �ϴ��� ���̼����� ������ ���� �ֽʽÿ�.
# ������� �뵵�δ� ����Ͻ� �� �����ϴ�.
#
# ����ó : http://www.webweaver.pe.kr
# ������ : 2000�� 8�� 31��
# ������ : ���ֿ� (webweaver@webweaver.pe.kr)
#
# ���׹߽߰ÿ��� �ݵ�� �˷� �ֽʽÿ�. ���������� ������ϰڽ��ϴ�.
####################################################################################


$gCgiVer = "beta_2";
$gCgiUrl = $ENV{'SCRIPT_NAME'};
$gCgiBinUrl = $gCgiUrl;
$gCgiBinUrl =~ s/\/member.cgi$//i;
$gCgiBinUrl =~ s/\/member.pl$//i;

#------ �����ϼ���

# ȸ�������� �Ǵ� ȸ������ ������ ������ ������
# �翬�� �α��� ���� �ִ� �������� �ؾ߰���?
$redirect_page = "../login_form.htm";

# �α׾ƿ����� �� ������ ������
$logout_page = "../login_form.htm";

# �α��ο� �������� ��� ������ ������
$Certified = "../success.htm";

# �������α׷� ��ġ
$mail_program = "/usr/sbin/sendmail";

# ������ id
$admin_id = "admin";

# ������ �����ּ�, ����� ���� \�� ������ ���ͳ� ���ϴ�.
$admin_main = "yourmail\@yourdomain.com";

#------ ������

# �Ʒ��� �������� ���ÿ�.
$gMailerCGI = "$gCgiBinUrl/KnDolMailer.cgi";
$gMailerOptName = "name";					# �̸��� ���� �� ����ϴ� �ɼ�
$gMailerOptMail = "mail";					# ���� �ּҸ� ���� �� ����ϴ� �ɼ�

&getDefaultCfg;
&parseArgument;
&getConf;
&readCookie;
&selectAction;


###############################################################################
sub getDefaultCfg {
	if (-e "family.config") {
		require "family.config";
	}
	if ($gMainDir eq "") {
		my($path) = $0;
		$path =~ s/\\/\//g;
		$path =~ s/\/member.cgi$//i;
		$path =~ s/\/member.pl$//i;
		$gMainDir = $path;
	}
	$gMainUrl = $gCgiBinUrl         if ($gMainUrl eq "");
	$gImageUrl = "$gMainUrl/images" if ($gImageUrl eq "");
}

###############################################################################
sub parseArgument {
	local($pair,$name,$value,$content_type,$content_length,$buffer,$dump,$boundary,$line,$array_value, $i);
    local(@pairs,@column);

	if ($ENV{'QUERY_STRING'}) {
		@pairs = split(/&/,$ENV{'QUERY_STRING'});

		foreach $pair (@pairs) {
			($name, $value) = split(/=/,$pair);

			$value =~ tr/+/ /;
			$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
			if ($name eq 'head' || $name eq 'foot') {
				$value =~ s/\n/\\n/g ;
				$value =~ s/\n/\\n/g ;
			}
			elsif ($name ne 'profile') {
				$value =~ s/\n//g ;
			}

			$FORM{$name} = $value;
		}
	}
	else {
		$content_type = $ENV{'CONTENT_TYPE'};
		$content_length = $ENV{'CONTENT_LENGTH'};

		binmode STDIN;
		read(STDIN,$buffer,$content_length);

		if ((!$content_type) || ($content_type eq 'application/x-www-form-urlencoded')) {
			@pairs = split(/&/, $buffer);

			foreach $pair (@pairs)  {
				($name, $value) = split(/=/,$pair);

				$value =~ tr/+/ /;
				$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
				$value =~ s/\n//g unless ($name eq 'body');

				$FORM{$name} = $value;
			}
		}
		elsif ($content_type =~ m#^multipart/form-data#) {
			($boundary = $content_type) =~ s/^.*boundary=(.*)$/\1/;
			@pairs = split(/--$boundary/, $buffer);
			@pairs = splice(@pairs,1,$#pairs-1);

			$i = 0;
			for $pair (@pairs)  {
				($dump,$line,$value) = split(/\r\n/,$pair,3);
				if ($line =~ /filename/) {
					$gRealFile[$i++] = $line;
				}

				next if $line =~ /filename=\"\"/;
				$line =~ s/^Content-Disposition: form-data; //;
				(@column) = split(/;\s+/, $line);
				($name = $column[0]) =~ s/^name="([^"]+)"$/\1/g;

				if ($#column > 0) {
					if($value =~ /^Content-Type:/)  {
						($dump,$dump,$value) = split(/\r\n/,$value,3);
					}
					else {
						($dump,$value) = split(/\r\n/,$value,2);
					}
				}
				else {
					($dump,$value) = split(/\r\n/,$value,2);
					if (grep(/^$name$/, keys(%CGI))) {
						if (@{$FORM{$name}} > 0) {
							push(@{$FORM{$name}}, $value);
						}
						else {
							$array_value = $FORM{$name};
							undef $FORM{$name};
							$FORM{$name}[0] = $array_value;
							push(@{$FORM{$name}}, $value);
						}
					}
					else {
						next if $value =~ /^\s*$/;
						$FORM{$name} = $value;
						chop($FORM{$name});
						chop($FORM{$name});
					}
					next;
				}
				$FORM{$name} = $value;
			}
		}
		else {
			print "Invalid content type!\n";
			exit(1);
		}
	}
}

###############################################################################
sub selectAction{
	if($FORM{'page'} eq ""){$page=1;}
	else{$page = $FORM{'page'};	}

	if($FORM{'action'} eq "") {
		#$admin_name = &strURLEncode ("$admin_id");
		if($COOKIE{'id'} ne "$admin_id") {cgiErrorMsg("�㰡���� ���� �ൿ�Դϴ�.");}
		else{&display;}
	}
	elsif($FORM{'action'} eq "login") {&login;}
	elsif($FORM{'action'} eq "logout") {&logout;}
	elsif($FORM{'action'} eq "form") {&input;}
	elsif($FORM{'action'} eq "write") {
		&write;
	}
	elsif($FORM{'action'} eq "modify") {&modify;}
	elsif($FORM{'action'} eq "adminLogin") {&adminLogin;}
	elsif($FORM{'action'} eq "erase") {&erase;}
	elsif($FORM{'action'} eq "loginok") {
		if($FORM{'passwd'} eq "") {&cgiErrorMsg("��й�ȣ�� �Է��ϼ���!!");}
		&loginok;
	}
	elsif($FORM{'action'} eq "modifyok") {
		if($FORM{'passwd'} eq "") {&cgiErrorMsg("��й�ȣ�� �Է��ϼ���!!");}
		&modifyok;
	}
	elsif($FORM{'action'} eq "eraseok") {
		if($FORM{'passwd'} eq "") {&cgiErrorMsg("��й�ȣ�� �Է��ϼ���!!");}
		&eraseok;
	}
	elsif($FORM{'action'} eq "changeConfig") {&changeConfig;}
	elsif($FORM{'action'} eq "viewDetail") {&viewDetail;}
	elsif($FORM{'action'} eq "search") {&search;}
	else {
		#$admin_name = &strURLEncode ("$admin_id");
		if($COOKIE{'id'} ne "$admin_id") {cgiErrorMsg("�㰡���� ���� �ൿ�Դϴ�.");}
		else{&display;}
	}
}

###############################################################################
sub getConf{
    if (open(CONF,"<$gMainDir/conf.txt")) {
	    my($conf_list) = <CONF>;
	    close(CONF);
	    @conf = split(/\|/,$conf_list);
		$gConfAdminPass = $conf[1];
		$gConfListNum = $conf[2];
		$gConfBgColor = $conf[3];
		$gConfBgImage = $conf[4];
		$gConfUseFormmail = $conf[5];
		$gConfClassExp = $conf[6];
		$gConfClassLongName = $conf[7];
		$gConfClassShortName = $conf[8];
		$gConfStartCls = $conf[9];
		$gConfEndCls = $conf[10];
		$gConfViewSpecial = $conf[11];
		$gConfPreBody = $conf[12];
		$gConfPostBody = $conf[13];
		$gConfListType = $conf[14];
		$gConfPreBody =~ s/\\n/\n/g;
		$gConfPostBody =~ s/\\n/\n/g;
		$gConfStartCls = &getCurYear - 4    if ($gConfStartCls !~ /\d{4,}/);
		$gConfEndCls = &getCurYear          if ($gConfEndCls !~ /\d{4,}/);
	}
	else {
		return if ($FORM{'action'} eq "changeConfig");

		$gConfAdminPass = "";
		$gConfListNum = "10";
		$gConfBgColor = "white";
		$gConfBgImage = "";
		$gConfUseFormmail = "1";
		$gConfClassExp = "0";
		$gConfClassLongName = "�й�";
		$gConfClassShortName = "�й�";
		$gConfPreBody = "<div align=\"center\">";
		$gConfPostBody = "<br><% COPY %></div>";
		$gConfListType = "0";
		&adminform;
	}
}

###############################################################################
sub putConf {
	$gConfPreBody =~ s/\|/&#124;/g;
	$gConfPostBody =~ s/\|/&#124;/g;

    open(CONF,">$gMainDir/conf.txt");
    print CONF "|$gConfAdminPass|$gConfListNum|$gConfBgColor|$gConfBgImage|$gConfUseFormmail|$gConfClassExp|$gConfClassLongName|$gConfClassShortName|$gConfStartCls|$gConfEndCls|$gConfViewSpecial|$gConfPreBody|$gConfPostBody|$gConfListType|";
    close(CONF);
}

###############################################################################
sub login{
	if (($FORM{'id'} eq "") || ($FORM{'passwd'} eq "")) {&cgiErrorMsg("ID �Ǵ� ��й�ȣ�� �Էµ��� �ʾҽ��ϴ�.");}
	open(LOGIN,"<$gMainDir/data/$FORM{'id'}") || &cgiErrorMsg("�������� �ʴ� ID �Դϴ�.");
	$data = <LOGIN>;
	@logindata= split(/\|/,$data);
	close (LOGIN);

	$pass = $FORM{'passwd'};
	$cryptpass = crypt($pass,sp);
	$FORM{'passwd'} =  $cryptpass;
	
	&getdate;

	if ($COOKIE{'visit_count'} eq "") {$visit_count = 0;}
	else {$visit_count = ++ $COOKIE{'visit_count'};}
	
	if ($FORM{'passwd'} eq $logindata[1]) {

#		print "Set-Cookie: tt=LogIn;expires=Thu, 31-Dec-2099 00:00:00 GMT;path=;domain=$ENV{SERVER_NAME};\r\n";
		print "Set-Cookie: tt=LogIn;expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
		print "Set-Cookie: id=$FORM{'id'};expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
		print "Set-Cookie: name=$logindata[3];expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
		print "Set-Cookie: email=$logindata[4];expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
		print "Set-Cookie: url=$logindata[5];expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
		print "Set-Cookie: visit_count=$visit_count;expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
		print "Location: $Certified\n\n";
		exit;
	}
	else {&cgiErrorMsg("ID �� ��й�ȣ�� ��ġ ���� �ʽ��ϴ�.")}
}

###############################################################################
sub logout{
	&getdate;
	print "Set-Cookie: id=guest;expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
	print "Set-Cookie: name=guest;expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
	print "Set-Cookie: tt=LogOut;expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
	print "Set-Cookie: last_visit=$short_date;expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";

	print "Location: $logout_page\n\n";
	exit;
}
###############################################################################
sub printHead {
	$ver = " Ver$gCgiVer" if ($gMode eq "admin");
print <<START;
Content-type: text/html

<!-------------------------------------------------------------->
<!-- ����, ū������ �ּҷ��� ���� ��ũ�����߽��ϴ�.           -->
<!-- Program by JuWon,Kim You can use this script Freely      -->
<!-- email : suchcool\@shinbiro.com                           -->
<!-------------------------------------------------------------->
<html>
<head>
<title>ȸ������ $ver</title>
<meta http-equiv="Content-Type" content="text/html; charset=euc-kr">

<LINK rel="stylesheet" type="text/css" href="./ie4css.css">

<script language=javascript>
	function newin(width,height,url,name) {
		msgWindow=window.open(url,name,'statusbar=no,scrollbars=yes,status=yes,resizable=yes,width='+width+',height='+height)
	}
</script>
$gJavaScript
</head>
<BODY bgcolor=$gConfBgColor $gOnLoad leftmargin=0 topmargin=0 marginwidth=0 marginheight=0>
$gConfPreBody
START
}

###############################################################################
sub printFoot {
	if ($gConfPostBody =~ /<% COPY %>/i) {
	$gConfPostBody = "<br><% COPY %></div>"
	if ($gConfPreBody eq "" || $gConfPostBody eq "");
		$gConfPostBody =~ s?<% COPY %>?<p align=center><font size=1 color=silver><a href="http://sepal.woorizip.com" target="_blank"><font size=1 color=silver>Powered by SPFAMILY</font></a>, <a href="http://www.webweaver.pe.kr" target="_blank"><font size=1 color=silver>Modified by JuWon,Kim</font></a></font>?i;
		print "\n$gConfPostBody\n";
		print "</body></html>\n";
	}
	else {
		print "\n$gConfPostBody\n";
		print "<p align=center><font size=1 color=silver><font size=1 color=silver><a href=\"http://sepal.woorizip.com\" target=\"_blank\">Powered by SPFAMILY</a></font>, <font size=1 color=silver><a href=\"http://www.webweaver.pe.kr\" target=\"_blank\">Modified by JuWon,Kim</a></font></font></body></html>\n";
	}

	exit;
}

###############################################################################
sub input {

	$gOnLoad = " onload=\"form.name.focus();\"";
	$gJavaScript = "<script language=\"JavaScript\">\n"
			. "<!-- JavaScript\n"
			. "function id_copy(){\n"
			. "a = null;\n"
			. "a = document.form.id.value;\n"
			. "return a;\n"
			. "}\n\n"
			. "function OpenZipcode(z1, z2) {\n"
			. "	window.open('$gCgiBinUrl/zipcode.cgi?form=form&zip1=zip1&zip2=zip2&address=address&zip='+z1+'-'+z2,'ZipWin','width=480,height=200,toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=yes,resizable=yes');\n"
			. "}\n\n"
			. "function check(form) {\n"
			. "	if ( isFieldBlank(form.name) ) {\n"
			. "		alert(\"�̸��� �Է��� �ּ���.\\n\\n�̸��� �ݵ�� �Է��ؾ� �մϴ�.\");\n"
			. "		form.name.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( !isFieldBlank(form.email) && form.email.value.indexOf(\"@\")==-1 ) {\n"
			. "		alert(\"�ùٸ� e-mail �ּҰ� �ƴմϴ�.\");\n"
			. "		form.email.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.email) ) {\n"
			. "		alert(\"e-mail �ּҸ� �Է��� �ּ���.\");\n"
			. "		form.email.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( !isUrlBlank(form.url, \"http://\") && !validateUrl(form.url, \"http://\") ) {\n"
			. "		alert(\"�ùٸ� Ȩ������ �ּҰ� �ƴմϴ�.\");\n"
			. "		form.url.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.id) ) {\n"
			. "		alert(\"ID�� �Է��� �ּ���.\\n\\nWebWeaver�� �α����ϱ� ���� �ʿ��մϴ�.\");\n"
			. "		form.id.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.passwd) ) {\n"
			. "		if (confirm(\"��й�ȣ�� �Է����� ������ ������ �ܿ���\\n���� �� ������ �Ұ����� ���ϴ�.\\n\\n��й�ȣ�� �Է��Ͻðڽ��ϱ�?\")) {\n"
			. "			form.passwd.focus();\n"
			. "			return;\n"
			. "		}\n"
			. "	}\n"
			. "	if (!( form.passwd.value == form.repasswd.value )) {\n"
			. "		alert(\"�Է��Ͻ� ��й�ȣ�� ���� ��ġ���� �ʽ��ϴ�.\");\n"
			. "		form.passwd.focus();\n"
			. "		return;\n"
			. "	}\n"			
			. "	if ( isFieldBlank(form.birth_year) ) {\n"
			. "		alert(\"��������� �Է��� �ּ���.\");\n"
			. "		form.birth_year.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.birth_mon) ) {\n"
			. "		alert(\"��������� �Է��� �ּ���.\");\n"
			. "		form.birth_mon.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.birth_day) ) {\n"
			. "		alert(\"��������� �Է��� �ּ���.\");\n"
			. "		form.birth_day.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.zip1) ) {\n"
			. "		alert(\"�����ȣ�� �Է��� �ּ���.\");\n"
			. "		form.zip1.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.zip2) ) {\n"
			. "		alert(\"�����ȣ�� �Է��� �ּ���.\");\n"
			. "		form.zip2.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.address) ) {\n"
			. "		alert(\"�ּҸ� �Է��� �ּ���.\");\n"
			. "		form.address.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.address2) ) {\n"
			. "		alert(\"������ �ּҸ� �Է��� �ּ���.\");\n"
			. "		form.address2.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.hp) ) {\n"
			. "		alert(\"�޴����� �Է��� �ּ���.\\n\\n���� ���� ����ȭ ��ȣ��..\");\n"
			. "		form.hp.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	form.submit();\n"
			. "}\n"
			. "function isFieldBlank(theField) {\n"
			. "	if (theField.value == \"\")\n"
			. "		return true;\n"
			. "	else\n"
			. "		return false;\n"
			. "}\n"
			. "function isUrlBlank(theField, url) {\n"
			. "   if ( theField.value == url || isFieldBlank(theField) )\n"
			. "		return true;\n"
			. "	else\n"
			. "		return false;\n"
			. "}\n"
			. "function validateUrl(theField, url) {\n"
			. "   if ( theField.value.indexOf(url)==0 && theField.value.indexOf(\".\")!=-1 ) {\n"
			. "		return true;\n"
			. "	}\n"
			. "	else {\n"
			. "		return false;\n"
			. "	}\n"
			. "}\n"
			. "// - JavaScript - -->\n"
			. "</script>\n";


	&printHead;
	if ($COOKIE{'id'} eq "$admin_id") {print "<form name=form enctype=multipart/form-data method=post action=$gCgiUrl>\n";}
	else {print "<form name=form enctype=multipart/form-data method=post action=$gCgiUrl target=_top>\n";}
	print <<START;
  <input type=hidden name=action value=write>
  <table border=0 cellpadding=1 cellspacing=1 width="550" align="center">
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�̸�</b></font></td>
      <td width=480> 
        <input type=text name=name size=15 value="$COOKIE{'name'}" maxlength=15 class=input> �ݵ�� �Ǹ��� ����ϼ���. </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>E-Mail</b></font></td>
      <td width=480> 
        <input type=text name=email size=34 value="$COOKIE{'email'}" maxlength=40 class=input>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>Ȩ������</b></font></td>
      <td width=480> 
START

	if($COOKIE{'UH'} eq "") {
		print "<input type=text name=url value=\"http://\" size=34 maxlength=40 class=input>\n";
	}
	else{
		print "<input type=text name=url value=\"$COOKIE{'url'}\" size=34 maxlength=40 class=input>\n";
	}
	
	print <<START;
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>ID</b></font></td>
      <td width=480> 
        <input type="text" name="id" size="8" maxlength="8" class=input> <input type="button" value="ID �ߺ� üũ" onClick="id_copy();newin(400,150,'./id_check.cgi?id=' + a,'id_check')" class="button"> �α��� ID
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>��й�ȣ</b></font></td>
      <td width=480> 
        <input type=password name=passwd size=8 class=input>
        �ٽ��Է� 
        <input type=password name=repasswd size=8 class=input>
        ���� �� ������ �ʿ�</td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�������</b></font></td>
      <td width=480> 
        <input type=text name=birth_year size=4 maxlength=4 class=input>
        �� 
        <input type=text name=birth_mon size=2 maxlength=2 class=input>
        �� 
        <input type=text name=birth_day size=2 maxlength=2 class=input>
        �� 
        <select name=solar class=input>
          <option value=plus selected>���</option>
          <option value=minus >����</option>
        </select>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�����ȣ</b></font></td>
      <td width=480> 
        <input type="text" name="zip1" maxlength="3" size="3" class=input>
        - 
        <input type="text" name="zip2" maxlength="3" size="3" class=input> 
        <input type="button" name="seekZip" value=" �����ȣã�� " onclick="OpenZipcode(this.form.zip1.value, this.form.zip2.value)" class=button>
      </td>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�ּ�</b></font></td>
      <td width=480> 
        <input type=text name=address size=34 maxlength=40 class=input>
        <select name=sel_address class=input>
          <option value=house selected>�� 
          <option value=company>���� 
        </select>
        <br>
        <input type=text name=address2 size=34 maxlength=40 class=input>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>����ȭ</b></font></td>
      <td width=480> 
        <input type=text name=home_tel size=14 maxlength=14 class=input>
        (��: 02-345-6789)</td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>������ȭ</b></font></td>
      <td width=480> 
        <input type=text name=job_tel size=14 maxlength=14 class=input>
      </td>
    </tr>      
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�޴���</b></font></td>
      <td width=480> 
        <input type=text name=hp size=14 maxlength=14 class=input>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�ڱ�Ұ�</b></font></td>
      <td width=480> 
        <textarea name=profile  rows=5 cols=42 class=input></textarea>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>����</b></font></td>
      <td width=480> 
        <input type=file name=photo size=17 maxlength=17 class=input>
        (120x150) <a href="javascript:newin(400, 400, './help.htm', 'help')">����</a></td>
    </tr>
    <tr> 
      <td width=439 align=center colspan=3> 
        <p><br>
          <font face=����ü> 
          <input type="button" value="ȸ�� ���" class=button onClick="check(this.form)" name="button">
          <input type=reset value="�ٽ� �ۼ�" class=button name="reset">
          </font> 
      </td>
    </tr>
  </table>
</form>
START
	&printFoot;
}

###############################################################################
sub modifyform {
	open(DATA,"<$gMainDir/data/$FORM{'number'}");
	$data = <DATA>;
	@wdata= split(/\|/,$data);
	close (DATA);
	$name=$wdata[3];
	$class=$wdata[2];
	$email=$wdata[4];
	$homepage=$wdata[5];
	$passwd=$wdata[1];

	@birth= split(/:/,$wdata[6]);
	$birth_year= $birth[0];
	$birth_mon=$birth[1];
	$birth_day=$birth[2];
	$solar=$birth[3];
	if($solar eq ( "+" || "" )){
		$plus="selected";
	}
	else{
		$minus="selected";
	}

	@address = split(/:/,$wdata[7]);
	if($address[0] eq "H"){
		$house_val="selected";
	}
	else{
		$comp_val="selected";
	}
	$address1=$address[1];
	$address2=$address[2];
	$address3=$address[3];
	$address4=$address[4];
	$home_tel = $wdata[8];
	$job_tel = $wdata[9];
	$hp = $wdata[10];
	$photo = $wdata[11];
	$profile = $wdata[12];
	$profile =~ s/<br>/\n/gi;
	$id = $wdata[13];

	$gOnLoad = " onload=\"form.email.focus();\"";
	$gJavaScript = "<script language=\"JavaScript\">\n"
			. "<!-- JavaScript\n"
			. "function OpenZipcode(z1, z2) {\n"
			. "	window.open('$gCgiBinUrl/zipcode.cgi?form=form&zip1=zip1&zip2=zip2&address=address&zip='+z1+'-'+z2,'ZipWin','width=480,height=200,toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=yes,resizable=yes');\n"
			. "}\n\n"
			. "function check(form) {\n"
			. "	if ( isFieldBlank(form.name) ) {\n"
			. "		alert(\"�̸��� �Է��� �ּ���.\\n\\n�̸��� �ݵ�� �Է��ؾ� �մϴ�.\");\n"
			. "		form.name.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( !isFieldBlank(form.email) && form.email.value.indexOf(\"@\")==-1 ) {\n"
			. "		alert(\"�ùٸ� e-mail �ּҰ� �ƴմϴ�.\");\n"
			. "		form.email.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.email) ) {\n"
			. "		alert(\"e-mail �ּҸ� �Է��� �ּ���.\");\n"
			. "		form.email.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( !isUrlBlank(form.url, \"http://\") && !validateUrl(form.url, \"http://\") ) {\n"
			. "		alert(\"�ùٸ� Ȩ������ �ּҰ� �ƴմϴ�.\");\n"
			. "		form.url.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.id) ) {\n"
			. "		alert(\"ID�� �Է��� �ּ���.\\n\\nWebWeaver�� �α����ϱ� ���� �ʿ��մϴ�.\");\n"
			. "		form.id.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.passwd) ) {\n"
			. "		if (confirm(\"��й�ȣ�� �Է����� ������ ������ �ܿ���\\n���� �� ������ �Ұ����� ���ϴ�.\\n\\n��й�ȣ�� �Է��Ͻðڽ��ϱ�?\")) {\n"
			. "			form.passwd.focus();\n"
			. "			return;\n"
			. "		}\n"
			. "	}\n"
			. "	if (!( form.passwd.value == form.repasswd.value )) {\n"
			. "		alert(\"�Է��Ͻ� ��й�ȣ�� ���� ��ġ���� �ʽ��ϴ�.\");\n"
			. "		form.passwd.focus();\n"
			. "		return;\n"
			. "	}\n"			
			. "	if ( isFieldBlank(form.birth_year) ) {\n"
			. "		alert(\"��������� �Է��� �ּ���.\");\n"
			. "		form.birth_year.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.birth_mon) ) {\n"
			. "		alert(\"��������� �Է��� �ּ���.\");\n"
			. "		form.birth_mon.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.birth_day) ) {\n"
			. "		alert(\"��������� �Է��� �ּ���.\");\n"
			. "		form.birth_day.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.zip1) ) {\n"
			. "		alert(\"�����ȣ�� �Է��� �ּ���.\");\n"
			. "		form.zip1.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.zip2) ) {\n"
			. "		alert(\"�����ȣ�� �Է��� �ּ���.\");\n"
			. "		form.zip2.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.address) ) {\n"
			. "		alert(\"�ּҸ� �Է��� �ּ���.\");\n"
			. "		form.address.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.address2) ) {\n"
			. "		alert(\"������ �ּҸ� �Է��� �ּ���.\");\n"
			. "		form.address2.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	if ( isFieldBlank(form.hp) ) {\n"
			. "		alert(\"�޴����� �Է��� �ּ���.\\n\\n���� ���� ����ȭ ��ȣ��..\");\n"
			. "		form.hp.focus();\n"
			. "		return;\n"
			. "	}\n"
			. "	form.submit();\n"
			. "}\n"
			. "function isFieldBlank(theField) {\n"
			. "	if (theField.value == \"\")\n"
			. "		return true;\n"
			. "	else\n"
			. "		return false;\n"
			. "}\n"
			. "function isUrlBlank(theField, url) {\n"
			. "   if ( theField.value == url || isFieldBlank(theField) )\n"
			. "		return true;\n"
			. "	else\n"
			. "		return false;\n"
			. "}\n"
			. "function validateUrl(theField, url) {\n"
			. "   if ( theField.value.indexOf(url)==0 && theField.value.indexOf(\".\")!=-1 ) {\n"
			. "		return true;\n"
			. "	}\n"
			. "	else {\n"
			. "		return false;\n"
			. "	}\n"
			. "}\n"
			. "// - JavaScript - -->\n"
			. "</script>\n";

	&printHead;
	
	if ($COOKIE{'id'} eq "$admin_id") {print "<form name=form enctype=multipart/form-data method=post action=$gCgiUrl>\n";}
	else {print "<form name=form enctype=multipart/form-data method=post action=$gCgiUrl target=_top>\n";}
	print <<START;
  <input type=hidden name=action value=write>
  <input type=hidden name=call value=modifyok>
  <input type=hidden name=number value="$FORM{'number'}">
  <table border=0 cellpadding=1 cellspacing=1 width="550" align="center">
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�̸�</b></font></td>
      <td width=480 height=25> 
        <input type=hidden name=name size=15 value="$name" maxlength=15 class=input><b>$name</b></td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>E-Mail</b></font></td>
      <td width=480> 
        <input type=text name=email value="$email" size=34 value="$COOKIE{'UM'}" maxlength=40 class="input">
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>Ȩ������</b></font></td>
      <td width=480> 
        <input type=text name=url value="$homepage" size=34 maxlength=40 class="input"></font>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>ID</b></font></td>
      <td width=480 height=25>
        <input type="hidden" name="id" value="$id"><b>$id</b>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>��й�ȣ</b></font></td>
      <td width=480> 
        <input type=password name=passwd size=8 value="$passwd" class="input">
        �ٽ��Է� 
        <input type=password name=repasswd size=8 value="$passwd" class="input">
        ���� �� ������ �ʿ�</td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�������</b></font></td>
      <td width=480> 
        <input type=text name=birth_year size=4 maxlength=4 value="$birth_year" class="input">
        �� 
        <input type=text name=birth_mon size=2 maxlength=2 value="$birth_mon" class="input">
        �� 
        <input type=text name=birth_day size=2 maxlength=2 value="$birth_day" class="input">
        �� 
        <select name=solar class="input">
          <option value=plus $plus>���</option>
          <option value=minus $minus>����</option>
        </select>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�����ȣ</b></font></td>
      <td width=480> 
        <input type="text" name="zip1" maxlength="3" size="3" value="$address3" class="input">
        - 
        <input type="text" name="zip2" maxlength="3" size="3" value="$address4" class="input"> 
        <input type="button" name="seekZip" value=" �����ȣã�� " onclick="OpenZipcode(this.form.zip1.value, this.form.zip2.value)" class=button>
      </td>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�ּ�</b></font></td>
      <td width=480> 
        <input type=text name=address size=34 maxlength=40 value="$address1" class="input">
        <select name=sel_address class=input>
          <option value=house $house_val>�� 
          <option value=company $comp_val>���� 
        </select>
        <br>
        <input type=text name=address2 size=34 maxlength=40 value="$address2" class="input">
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>����ȭ</b></font></td>
      <td width=480> 
        <input type=text name=home_tel size=14 maxlength=14 value="$home_tel" class="input">
        (��: 02-345-6789)</td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>������ȭ</b></font></td>
      <td width=480> 
        <input type=text name=job_tel size=14 maxlength=14 value="$job_tel" class=input>
      </td>
    </tr>        
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�޴���</b></font></td>
      <td width=480> 
        <input type=text name=hp size=14 maxlength=14 value="$hp" class="input">
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>�ڱ�Ұ�</b></font></td>
      <td width=480> 
        <textarea name=profile  rows=5 cols=42 class=input>$profile</textarea>
      </td>
    </tr>
    <tr> 
      <td width=70 align=right bgcolor=#5577AA><font color=white><b>����</b></font></td>
      <td width=480> 
        <input type=file name=photo size=17 maxlength=17 class=input>
        <br>
        <input type=checkbox name=del_photo value=y> ���� �����
        <input type=hidden name=old_photo value=$photo>
        (120x150) <a href="javascript:newin(400, 400, './help.htm', 'help')">����</a></td>
    </tr>
    <tr> 
      <td width=439 align=center colspan=3> 
        <p><br>
          <font face=����ü> 
          <input type="button" value="���� �ϱ�" class=button onClick="check(this.form)" name="button">
          <input type=reset value="�ٽ� �ۼ�" class=button name="reset">
          </font> 
      </td>
    </tr>
  </table>
</form>
START
	&printFoot;
}

###############################################################################
sub adminform {
	$message = ($gConfAdminPass eq "") ? "[ó�� �����Դϴ�. ������ ��й�ȣ�� �Է��� �ּ���.]"
	                               : "[��й�ȣ �����: ��ĭ �״�� �νø� ���� ��й�ȣ �����]";
	$gOnLoad = " onload=\"form.passad.focus();\"";
	$gMode = "admin";
	&printHead;
	print "<div align=center><form name=form method=post action=$gCgiUrl>\n";
	print "<input type=hidden name=action value=changeConfig>\n";
	print "<table width=400 border=0 align=center cellpadding=1 cellspacing=0 bgcolor=black><tr><td>\n";
	print "<table border=0 width=100% cellpadding=3 cellspacing=0 bgcolor=#FFDAEE>\n";
	print "<tr><td align=right><font color=000000>$message<br> ��й�ȣ</font> <input type=password name=passad size=8 style=\"border:1 solid silver; background:rgb(240,240,255);\">\n";
	print "&nbsp; <font color=000000>�ٽ��Է�</font> <input type=password name=repassad size=8 style=\"border:1 solid silver; background:rgb(240,240,255);\"></td></td></table>\n";
	print "<table border=0 width=100% cellpadding=3 cellspacing=0  bgcolor=#E2FFEF>\n";
	print "<tr><td align=right><font color=000000>�������� ��ǥ�� ����</font> <input type=text name=listNum size=8 value=\"$gConfListNum\" style=\"border:1 solid silver; background:rgb(255,240,240);\"></td></tr>\n";
	print "<tr><td align=right><font color=000000>����</font> <input type=text name=bgColor size=8 value=\"$gConfBgColor\" style=\"border:1 solid silver; background:rgb(255,240,240);\"></td></tr>\n";
	print "<tr><td align=right><font color=000000>��� �̹��� URL</font> <input type=text name=bgImage size=30 value=\"$gConfBgImage\" style=\"border:1 solid silver; background:rgb(255,240,240);\"></td></tr>\n";
	$fm_sel = ($gConfUseFormmail == 1) ? "<option value=1 selected>�����</option><option value=0>��� ����</option>"
	                                   : "<option value=1>�����</option><option value=0 selected>��� ����</option>";
	print "<tr><td align=right><font color=000000>�����Ϸ�</font> <select name=useFormmail style=\"border:1 solid silver; background:rgb(255,255,240);\">$fm_sel</select></td></tr>\n";
	print "</table>\n";
	print "<table border=0 width=100% cellpadding=3 cellspacing=0  bgcolor=#F2DFCF>\n";
	$exp_sel = ($gConfClassExp == 0) ? "<option value=0 selected>4�ڸ�</option><option value=1>2�ڸ�</option>"
	                                 : "<option value=0>4�ڸ�</option><option value=1 selected>2�ڸ�</option>";
	print "<tr><td colspan=2 align=right><font color=000000>$gConfClassLongName ǥ�� �ڸ���</font> <select name=ClassExp style=\"border:1 solid silver; background:rgb(255,255,240);\">$exp_sel</select></td></tr>\n";
	print "<tr><td width=50% align=right><font color=000000>$gConfClassLongName ǥ�� ���̸�</font> <input type=text name=ClassLongName size=6 value=\"$gConfClassLongName\" style=\"border:1 solid silver; background:rgb(255,255,240);\"></td>\n";
	print "<td width=50% align=right><font color=000000>ª���̸�</font> <input type=text name=ClassShortName size=6 value=\"$gConfClassShortName\" style=\"border:1 solid silver; background:rgb(255,255,240);\"></td></tr>\n";
	print "<tr><td width=50% align=right><font color=000000>�ְ� $gConfClassLongName(4�ڸ���)</font> <input type=text name=StartCls size=5 maxlength=4 value=\"$gConfStartCls\" style=\"border:1 solid silver; background:rgb(255,255,240);\"></td>\n";
	print "<td width=50% align=right><font color=000000>���� $gConfClassLongName(4�ڸ���)</font> <input type=text name=EndCls size=5 maxlength=4 value=\"$gConfEndCls\" style=\"border:1 solid silver; background:rgb(255,255,240);\"></td></tr>\n";
	print "<tr><td colspan=2 align=center><font color=000000>(�ְ�, ���� $gConfClassLongName��(��) �������� ������ �ڵ� ���õ�)</td></tr>\n";
	print "<tr><td width=50% align=right valign=top><font color=000000>Ư�� $gConfClassLongName (���� ��)<br><br>- ������ �� �׸����� ��<br>���� �׸��� �켱�� ����</font></td>\n";
	print "<td width=50% align=left><textarea name=SpecialClass cols=20 rows=5 style=\"border:1 solid silver; background:rgb(255,255,240);\">";
	for ($i = 0; $i <= $#gConfSpecialClass; $i++) {
		printf "$gConfSpecialClass[$i]";
	}
	print "</textarea></td></tr>\n";
	$spe_sel = ($gConfViewSpecial == 0) ? "<option value=0 selected>ǥ�� ����</option><option value=1>ǥ����</option>"
	                                    : "<option value=0>ǥ�� ����</option><option value=1 selected>ǥ����</option>";

	print "<tr><td colspan=2 align=right><font color=000000>��Ϻ��� $gConfClassLongName ���ÿ� Ư�� $gConfClassLongName</font> <select name=ViewSpecial style=\"border:1 solid silver; background:rgb(255,255,240);\">$spe_sel</select></td></tr>\n";
	$type_sel = ($gConfListType == 0) ? "<option value=0 selected>��ȭ/HP</option><option value=1>Ȩ������/����</option>"
	                                  : "<option value=0>��ȭ/HP</option><option value=1 selected>Ȩ������/����</option>";

	print "<tr><td colspan=2 align=right><font color=000000>��Ϻ��� ����ó�� ǥ���� �׸�</font> <select name=ListType style=\"border:1 solid silver; background:rgb(255,255,240);\">$type_sel</select></td></tr>\n";
	print "</table>\n";
	print "<table border=0 width=100% cellpadding=3 cellspacing=0  bgcolor=#DAEEFF>\n";
	print "<tr><td align=center><font color=000000>HTML �պκ� (&lt;BODY&gt; �±׿� �ּҷ� ����)</font></td></tr>\n";
	print "<tr><td align=right><textarea name=PreBody cols=44 rows=5 style=\"border:1 solid silver; background:rgb(240,250,255);\">$gConfPreBody</textarea></td></tr>\n";
	print "<tr><td align=center><font color=000000>HTML �޺κ� (�ּҷϰ� &lt;/BODY&gt; �±� ����)</font></td></tr>\n";
	print "<tr><td align=right><textarea name=PostBody cols=44 rows=5 style=\"border:1 solid silver; background:rgb(240,250,255);\">$gConfPostBody</textarea></td></tr></table>\n";
	print "</td></tr></table><br>\n";
	print "<input type=submit value=����ϱ� style=\"background-color:#FFE29D;border:1 solid silver;height:20\"> <input type=reset value=�ٽþ��� style=\"background-color:#FFE29D;border:1 solid silver;height:20\">\n";
	print "</form></div>\n";
	&printFoot;
}

###############################################################################
sub readCookie{
    if($ENV{'HTTP_COOKIE'}) {
        @cookies = split(/; /,$ENV{'HTTP_COOKIE'});
        foreach(@cookies) {
        ($name,$value) = split(/=/,$_);
        $COOKIE{$name} = $value;
        }
	}
}

###############################################################################
sub write {
	my($num);
	local($photo_name) = "";

	if ($FORM{'call'} ne "modifyok"){
		&id_check;
		$write_data = "$FORM{'id'}";
		$pass = $FORM{'passwd'};
		$cryptpass = crypt($pass,sp);
		$FORM{'passwd'} =  $cryptpass;
	}
	else {
		$write_data = $FORM{'number'};

		open(DATA,"<$gMainDir/data/$write_data");
		$data = <DATA>;
		@data_list = split(/\|/,$data);
		close(DATA);
		if($FORM{'passwd'} ne $data_list[1]){
			$pass = $FORM{'passwd'};
			$cryptpass = crypt($pass,sp);
			$FORM{'passwd'} =  $cryptpass;
		}
		if ($FORM{'del_photo'} eq "y") {
			unlink("$gMainDir/photos/$data_list[11]") if (-e "$gMainDir/photos/$data_list[11]" && $data_list[11] ne "");
			$photo_name = "";
		}
		elsif (-e "$gMainDir/photos/$data_list[11]" && $data_list[11] ne "") {
			my($name, $ext) = split(/\./,"$data_list[11]");
			$photo_name = "$write_data.$ext";
			rename("$gMainDir/photos/$name.$ext", "$gMainDir/photos/$photo_name");
		}
	}

	print "Set-Cookie: tt=LogIn;expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
	print "Set-Cookie: name=$FORM{'name'};expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
	print "Set-Cookie: email=$FORM{'email'};expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";			
	print "Set-Cookie: url=$FORM{'url'};expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";	
	print "Set-Cookie: id=$FORM{'id'};expires=Thu, 31-Dec-2099 00:00:00 GMT;\r\n";
	
	&savePhoto($write_data) if ($FORM{'photo'} ne "");

	$photo_name = $FORM{'old_photo'} if ($photo_name eq "" && $FORM{'del_photo'} ne "y");

	if($FORM{'solar'} eq "plus"){
			$solar = "+";
	}
	else{
		$solar = "-";
	}

	if($FORM{'sel_address'} eq "house"){
		$sel_address = "H";
	}
	else{
		$sel_address = "O";
	}

	$FORM{'profile'} =~ s/\r//g;
	$FORM{'profile'} =~ s/\n/<br>/g;

	open(WFILE,">$gMainDir/data/$write_data");
	print WFILE "|$FORM{'passwd'}|$FORM{'cls'}|$FORM{'name'}|$FORM{'email'}|$FORM{'url'}|$FORM{'birth_year'}:$FORM{'birth_mon'}:$FORM{'birth_day'}:$solar|$sel_address:$FORM{'address'}:$FORM{'address2'}:$FORM{'zip1'}:$FORM{'zip2'}|$FORM{'home_tel'}|$FORM{'job_tel'}|$FORM{'hp'}|$photo_name|$FORM{'profile'}|$FORM{'id'}|\n";
	close(WFILE);

	&send_mail;
	if ($FORM{'call'} ne "modifyok"){
		if ($COOKIE{'id'} eq "$admin_id") {&display;}
		else {
			print "Location: $redirect_page\n\n";
			exit;
		}
	}
	else {
		if ($COOKIE{'id'} eq "$admin_id") {&display;}
		else {
			print "Location: $redirect_page\n\n";
			exit;
		}		
	}

}

###############################################################################
sub getCurYear {
	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	$year += 1900 if (length($year) < 4);
	$year += 100 if ($year <= 1950);
	return $year;
}

###############################################################################
sub erase {
	$gOnLoad = " onload=\"form.passwd.focus();\"";
	&printHead;
print <<START;
<p>&nbsp;
<p align="center">
<font face=���� size="2" color="red">������ �ڷḦ �����մϴ�.<br> ��й�ȣ�� ���� �ֽð� ���� ��ư�� �����ּ���.</font>
</p>
<p align="center">&nbsp;
<form name=form method=post action=$gCgiUrl>
<input type=hidden name=action value=eraseok>
<input type=hidden name=number value="$FORM{'number'}">
<table><tr><td>��й�ȣ</td><td><input type=password name=passwd size=10 style="background-color:#F1F4FF;border:1 solid #000000"></td><td><input type=submit value=���� style="color:black;background-color:#FFCC66;border:1 solid black;height:21px"></td><td></form></td></tr></table>
START
	&printFoot;
}

###############################################################################
sub adminLogin {
	$gOnLoad = " onload=\"form.passwd.focus();\"";
	&printHead;
print <<START;
<br>
<table border="0" cellpadding="0" cellspacing="0" width="550" align="center">
  <tr>
    <td width="20" height="20"><img src="images/table_topleft.gif" width="20" height="20" border="0"></td>
    <td height="20" background="images/table_top.gif"><p>&nbsp;</td>
    <td width="20" height="20"><img src="images/table_topright.gif" width="20" height="20" border="0"></td>
  </tr>
  <tr>
    <td width="20" background="images/table_left.gif"><img src="images/null.gif" width="20" height="1" border="0"></td>
    <td align="center" bgcolor="#EADEB2">
      <table border="0" cellpadding="2" cellspacing="0" width="100%" align="center">
        <tr>
          <th align="center" bgcolor="#EADEB2"><font size="3">������ �α���</font></th>
        </tr>
        <tr>
          <td align="center" bgcolor="#FAFAE0">
            <form name="form" method="post" action="$gCgiUrl">
              <br>
              <font color="red">������ ���� �����մϴ�. <br> ��й�ȣ�� ���� �ֽð� Ȯ�� ��ư�� �����ּ���. <br><br></font>
              <input type=hidden name=action value=loginok>
              <input type=hidden name=number value="$FORM{'number'}">
              <input type="password" name="passwd" size="10" maxlength="10" style="background-color:ivory;border:1 solid #000000">
              <input type="submit" value=" Ȯ�� " style="color:black;background-color:#EADEB2;border:1 solid black;height:21px">
              <br>
              <br>
            </form>
          </td>
        </tr>
      </table>
    </td>
    <td width="20" background="images/table_right.gif"><img src="images/null.gif" width="20" height="1" border="0"></td>
  </tr>
  <tr>
    <td width="20" height="20"><p><img src="images/table_bottomleft.gif" width="20" height="20" border="0"></td>
    <td height="20" background="images/table_bottom.gif"><p>&nbsp;</td>
    <td width="20" height="20"><img src="images/table_bottomright.gif" width="20" height="20" border="0"></td>
  </tr>
</table>
START
	&printFoot;
}

###############################################################################
sub modify {
	$gOnLoad = " onload=\"form.passwd.focus();\"";
	&printHead;
print <<START;
<p>&nbsp;
<p align="center">
<font face=���� size="2" color="red">������ ���������� �����մϴ�.<br> ��й�ȣ�� ���� �ֽð� Ȯ�� ��ư�� �����ּ���.</font>
</p>
<p align=center>&nbsp;
<form name=form method=post action=$gCgiUrl>
<input type=hidden name=action  value=modifyok> &nbsp; &nbsp;
<input type=hidden name=number value="$FORM{'number'}">
<table><tr><td>��й�ȣ</td><td><input type=password name=passwd size=10 style="background-color:#F1F4FF;border:1 solid #000000"></td><td><input type=submit value=Ȯ�� style="color:black;background-color:#FFCC66;border:1 solid black;height:21px"></td><td></form></td></tr></table>
START
	&printFoot;
}

###############################################################################
sub eraseok {
	$pass = $FORM{'passwd'};
	$cryptpass = crypt($pass,sp);
	open(FILE,"<$gMainDir/data/$FORM{'number'}");
	$data = <FILE>;
	@wdata= split(/\|/,$data);
	close (FILE);

	if(($wdata[1] eq $cryptpass) || ($gConfAdminPass eq $cryptpass)) {
		unlink("$gMainDir/data/$FORM{'number'}");
		unlink("$gMainDir/photos/$wdata[11]");
		&erase_mailing;
		if ($COOKIE{'id'} eq "$admin_id") {&display;}
		else {&logout;}
	}
	else {
		&cgiErrorMsg("��й�ȣ�� Ʋ���ϴ�. �ٽ� �ѹ� Ȯ���� �ּ���!!");
	}
}

###############################################################################
sub loginok {
	$pass = $FORM{'passwd'};
	$cryptpass = crypt($pass,sp);
	if($gConfAdminPass eq $cryptpass) {
		&adminform;
	}

	else {
		&cgiErrorMsg("��й�ȣ�� Ʋ���ϴ�. �ٽ� �ѹ� Ȯ���� �ּ���!!");
	}
}

###############################################################################
sub modifyok {
	$pass = $FORM{'passwd'};
	$cryptpass = crypt($pass,sp);
	open(FILE,"<$gMainDir/data/$FORM{'number'}");
	$data = <FILE>;
	@wdata= split(/\|/,$data);
	close (FILE);
	if($wdata[1] eq $cryptpass || $gConfAdminPass eq $cryptpass) {
		&modifyform;
	}
	else {
		&cgiErrorMsg("��й�ȣ�� Ʋ���ϴ�. �ٽ� �ѹ� Ȯ���� �ּ���!!");
	}
}

###############################################################################
sub display {
	opendir(LIST, "$gMainDir/data");
	@list_data = readdir(LIST);
	closedir(LIST);

	$total_num = @list_data-2;
	if ($FORM{'sn'} ne "") {
		my(@temp) = @list_data;
		@list_data = (".", "..");
		for ($i=0, $j=2; $i<=$#temp; $i++) {
			$list_data[$j++] = $temp[$i] if ($temp[$i] =~ /$FORM{'sn'}/i);
		}
		$total_num = $j - 2;
	}
	$tot_pg = int($total_num/$gConfListNum);
	if (($tot_pg*$gConfListNum) < $total_num) { $tot_pg = $tot_pg + 1; }
	$start_num = ($page - 1) * $gConfListNum + 2;
	$end_num = ($class_select eq "" && $FORM{'sn'} eq "") ? $start_num + $gConfListNum -1 : @list_data;
	@list = sort{($a <=> $b) || ($a cmp $b)}(@list_data);

	&printHead;

	$FORM{'page'} = 1 if ($FORM{'page'} eq "");
	$d = 0;
	$pre_pg= $FORM{'page'} - 1;
	$next_pg = $FORM{'page'} + 1;
	if ($FORM{'sn'} eq "") {
		$message = "<font size=-1>���� <b><font color=red>$total_num</font></b>���� ȸ���� ��ϵǾ����ϴ�.</font>";
	}
	else {
		$message = ($total_num ne 0) ? "<font size=-1>�˻� ��� <b><font color=red>$total_num</font></b>���� �������� ã�ҽ��ϴ�.</font>"
		                             :" <font size=-1 color=red>ã���ô� �������� �����ϴ�.</font>";
	}


	if($class_select ne "") {
		$prev = "<img src=$gImageUrl/prev.gif border=0>";
		$next = "<a href=$gCgiUrl?page=$next_pg><img src=$gImageUrl/next.gif border=0></a>";

		if ($class_select <= $#gConfSpecialClass) {
			$cls_sel = "<b><font color=red>$gConfSpecialClass[$class_select]</font></b>";
		}
		else {
			$cls_sel = ($gConfClassExp == 0) ? "<b><font color=red>$class_select</font></b>$gConfClassShortName" : "<b><font color=red>" . substr($class_select,2,2) . "</font></b>$gConfClassShortName";
		}

		$message = "<font size=-1>$cls_sel ����Ʈ �Դϴ�.</font>";
	}
	elsif ($FORM{'page'} == 1) {
		if($tot_pg <= 1) {
			$prev = "<img src=$gImageUrl/prev.gif border=0>";
			$next = "<img src=$gImageUrl/next.gif border=0>";
		}
		else {
			$prev = "<img src=$gImageUrl/prev.gif border=0>";
			$next = "<a href=$gCgiUrl?page=$next_pg><img src=$gImageUrl/next.gif border=0></a>";
		}
	}
	else {
		#============================== 2page ����...
		if($next_pg <= $tot_pg) {
			$prev = "<a href=$gCgiUrl?page=$pre_pg><img src=$gImageUrl/prev.gif border=0></a>";
			$next = "<a href=$gCgiUrl?page=$next_pg><img src=$gImageUrl/next.gif border=0></a>";
		}
		else {
			$prev = "<a href=$gCgiUrl?page=$pre_pg><img src=$gImageUrl/prev.gif border=0></a>";
			$next = "<img src=$gImageUrl/next.gif border=0>";
		}
	}

print <<START;
<div align="center">
<table width="550" border="0" align="center">
<tr><td width="85" align="center"><a href=$gCgiUrl?action=adminLogin onMouseOver="window.status='������ ���� ����';return true;" onMouseOut="window.status='';return true;"><img src=$gImageUrl/admin.gif border=0></a></td>
<td align="center">$message</td><td width="85" align="right">$prev $next</td>
</tr></table></div>
<div align="center">
<table border="0" cellpadding="0" cellspacing="0" width="550" align="center">
    <tr>
        <td width="20" height="20"><p><img src="$gImageUrl/table_topleft.gif" width="20" height="20" border="0"></td>
        <td height="20" background="$gImageUrl/table_top.gif"><p>&nbsp;</td>
        <td width="20" height="20"><p><img src="$gImageUrl/table_topright.gif" width="20" height="20" border="0"></td>
    </tr>
    <tr>
        <td width="20" background="$gImageUrl/table_left.gif"><p><img src="$gImageUrl/null.gif" width="20" height="1" border="0"></td>
        <td width="510" bgcolor="#EADEB2" align="center">
	<table border="0" cellpadding="3" cellspacing="0" width="510" align="center">
	<tr>
		<th width="90" align="center"  bgcolor="#EADEB2">�� ��</th>
		<th width="50" align="center"  bgcolor="#EADEB2">&nbsp;</th>
START

	if ($gConfListType == 0) {
		print "		<th width=\"115\" align=\"left\" bgcolor=\"#EADEB2\">��&nbsp;&nbsp;&nbsp;��&nbsp;&nbsp;&nbsp;ó</th>\n";
		print "		<th width=\"115\" align=\"left\" bgcolor=\"#EADEB2\">&nbsp;</th>\n";
		print "		<th width=\"115\" align=\"left\" bgcolor=\"#EADEB2\">&nbsp;</th>\n";
	}
	else {
		print "		<th width=\"165\" align=\"left\" bgcolor=\"#EADEB2\">��&nbsp;&nbsp;&nbsp;��&nbsp;&nbsp;&nbsp;ó</th>\n";
		print "		<th width=\"165\" align=\"left\" bgcolor=\"#EADEB2\">&nbsp;</th>\n";
	}
	print "		<th width=\"35\" align=\"left\" bgcolor=\"#EADEB2\"><div align=\"center\">��</div></th>\n		</tr>";

#========================================
	$sel_num=0;
	for($start_num..$end_num){
		if (($list[$_] ne ".") && ($list[$_] ne "..")) {
			#===============================================================#
			#				��µ� ����Ÿ�� �� �κ�						#
			#===============================================================#
			if ($class_select eq "") {
				if ($list[$_] eq "") {
					$page= $FORM{'page'};
					last;
				}
			}
			&fileForm;
		}

	}

	if(($tot_pg <= 1) || ($FORM{'page'} eq "")){$page = 1; }
	else {$page= $FORM{'page'}; }

	if($sel_num eq "0"){
		$colspan = ($gConfListType == 0) ? 8 : 7;
		print "<tr bgcolor=\"#FFCC00\"><td colspan=\"$colspan\" align=\"center\">����Ÿ�� �������� �ʽ��ϴ�.</td></tr>\n";
	}
	print <<START;
			</table></div></td>
        <td width="20" background="$gImageUrl/table_right.gif"><p><img src="$gImageUrl/null.gif"
             width="20" height="1" border="0"></td>
    </tr>
    <tr>
        <td width="20" height="20"><img src="$gImageUrl/table_bottomleft.gif" width="20" height="20" border="0"></td>
        <td height="20" background="$gImageUrl/table_bottom.gif">&nbsp;</td>
        <td width="20" height="20"><img src="$gImageUrl/table_bottomright.gif" width="20" height="20" border="0"></td>
    </tr>
</table></div>
START

	if ($class_select eq "" && $FORM{'sn'} eq "") {
		&pagemove;
	}
	else {
		print "<center><a href=$gCgiUrl><img src=$gImageUrl/backtolist.gif border=0 alt=\"��ü����Ʈ ����\"></a></center>\n";
	}

	print <<SEARCH;
<!-- �̸��˻� ���ۺκ� -->
<div align="center">
<form method="post" action="$gCgiUrl">
  <table>
    <tr>
      <td><img src="$gImageUrl/icon_search.gif" width=20 height=20 border=0 alt="�̸����� ã��"></td>
      <td><input type=text name="sn" size=20 class="ipt"></td>
      <td><input value="�˻�" type="submit" class="btn"></td>
    </tr>
  </table>
</form>
</div>
<!-- �̸��˻� ���κ� -->
SEARCH
	&printFoot;
}

###############################################################################
sub fileForm{
	open(FILE,"<$gMainDir/data/$list[$_]");
	$data = <FILE>;
	@wdata= split(/\|/,$data);
	close (FILE);

	if($class_select ne ""){
		for($i=$gConfStartCls; $i <= $gConfEndCls; $i++) {
			if($class_select eq "$i") {
				if($wdata[2] eq "$i") {
					&dataView;
					$sel_num++;
				}
			}
		}
		for($i=0; $i <= $#gConfSpecialClass; $i++) {
			$cls = sprintf("%04d", $i);
			if($class_select eq "$cls") {
				if($wdata[2] eq "$cls") {
					&dataView;
					$sel_num++;
				}
			}
		}
	}
	else{
		&dataView;
		$sel_num++;
	}
}

###############################################################################
sub dataView{
	if ($wdata[2] <= $#gConfSpecialClass) {
		$class = &StringCutting($gConfSpecialClass[$wdata[2]], 4, "", "on");
	}
	else {
		$class = ($gConfClassExp == 0) ? "$wdata[2]" : substr($wdata[2],2,2);
	}
	$name = "<a href=\"javascript:newin(520, 340, '$gCgiUrl?action=viewDetail&number=$list[$_]', 'profile')\" onmouseover=\"window.status='$wdata[3]���� �ڼ��� ������ ����';return true\" onmouseout=\"window.status='';return true\">" . &StringCutting($wdata[3], 10, "��", "on") . "</a>";
	$homepage = ($wdata[5] ne "" && $wdata[5] ne "http://") ? "<a href=\"$wdata[5]\" target=\"_blank\" onmouseover=\"window.status='$wdata[3]���� Ȩ������ �湮';return true\" onmouseout=\"window.status='';return true\">" . &StringCutting($wdata[5], 22, "��", "on") . "</a>" : "<font color=\"teal\">Ȩ������ ���� �� ����!</font>";
	$homepage2 = ($wdata[5] ne "" && $wdata[5] ne "http://") ? "<a href=\"$wdata[5]\" target=\"_blank\" onmouseover=\"window.status='$wdata[3]���� Ȩ������ �湮';return true\" onmouseout=\"window.status='';return true\"><img src=\"$gImageUrl/home.gif\" width=\"11\" height=\"12\" border=\"0\" alt=\"$wdata[3]���� Ȩ������ �湮\"></a>" : "<img src=\"$gImageUrl/no_home.gif\" width=\"11\" height=\"12\" border=\"0\" alt=\"Ȩ������ ����\">";
	my($mailurl) = ($gConfUseFormmail) ? "javascript:newin(600, 400, '$gMailerCGI?cfg=familymail.cfg&$gMailerOptName=$wdata[3]&$gMailerOptMail=$wdata[4]', 'mail')" : "mailto:$wdata[3] <$wdata[4]>";
	$email = ($wdata[4] ne "") ? "<a href=\"$mailurl\" onmouseover=\"window.status='$wdata[3]�Բ� ���� ����';return true\" onmouseout=\"window.status='';return true\">" . &StringCutting($wdata[4], 22, "��", "on") . "</a>" : "<font color=\"teal\">�ݸ��̶�ϱ� -_-;;</font>";
	$email2 = ($wdata[4] ne "") ? "<a href=\"$mailurl\" onmouseover=\"window.status='$wdata[3]�Բ� ���� ����';return true\" onmouseout=\"window.status='';return true\"><img src=\"$gImageUrl/mail.gif\" width=\"14\" height=\"10\" border=\"0\" alt=\"$wdata[3]�Բ� ���� ����\"></a>" : "<img src=\"$gImageUrl/no_mail.gif\" width=\"14\" height=\"10\" border=\"0\" alt=\"���� ����\">";
	@birth = split(/:/,$wdata[6]);
	$birthday = ($birth[0] ne "") ? "$birth[0]/$birth[1]/$birth[2]($birth[3])" : "<font color=\"teal\">�� ������</font>";
	$home_tel = ($wdata[8] ne "") ? "$wdata[8]" : "����";
	$job_tel = ($wdata[9] ne "") ? "$wdata[9]" : "����";
	$hp = ($wdata[10] ne "") ? "$wdata[10]" : "����";

	$bg_color = ($sel_num % 2 == 0) ? "#FFFFF0" : "#FFFFD0";
	$cls_bg_color = ($sel_num % 2 == 0) ? "#FAFAE0" : "#FAFAC0";
print <<START;
	<tr>
		<td bgcolor="$bg_color" align="center">$name</td>
		<td bgcolor="$bg_color" align="center">$homepage2 $email2</td>
START

	if ($gConfListType == 0) {
		print "		<td bgcolor=\"$bg_color\" align=\"center\">$home_tel</td>\n";
		print "		<td bgcolor=\"$bg_color\" align=\"center\">$job_tel</td>\n";
		print "		<td bgcolor=\"$bg_color\" align=\"center\">$hp</td>\n";
	}
	else {
		print "		<td bgcolor=\"$bg_color\" align=\"center\">$homepage</td>\n";
		print "		<td bgcolor=\"$bg_color\" align=\"center\">$email</td>\n";
	}
	print "		<td align=center bgcolor=\"$bg_color\"><a href=\"$gCgiUrl?action=modify&number=$list[$_]\"><img src=$gImageUrl/mod.gif border=0 alt=\"�����ϱ�\"></a> <a href=\"$gCgiUrl?action=erase&number=$list[$_]\"><img src=$gImageUrl/del.gif border=0 alt=\"�����ϱ�\"></a></td>\n	</tr>\n";
}

###############################################################################
sub pagemove{
	print "<div align=center><table width=\"550\"><tr><td align=center>";

	$term = 10;
	$first = 1;
	$last = $term;
	while ($first <= $tot_pg) {
		if (($first <= $page) && ($page <= $last)) {
		$prevp = $first - 1;
			if ($prevp > 0) {
				print "[<a href=$gCgiUrl?page=$prevp onmouseover=\"window.status='���� ������ ����';return true\" onmouseout=\"window.status='';return true\">����</a>].....";
			}
			else {
				print "[<font color=C0C0C0>����</font>].....";
			}
		if ($last <= $tot_pg) {
			for ($pa = $first; $pa <= $last; $pa++) {
				if ($pa == $page) {
					print "[<font color=red><b>$pa</b></font>] ";
				}
				else {
					print "[<a href=$gCgiUrl?page=$pa onmouseover=\"window.status='$pa �������� �̵�';return true\" onmouseout=\"window.status='';return true\">$pa</a>] ";
				}
			}
		}
		else {
			for ($pa = $first; $pa <= $tot_pg; $pa++) {
				if ($pa == $page) {
					print "[<font color=red><b>$pa</b></font>] ";
				}
				else {
					print "[<a href=$gCgiUrl?page=$pa onmouseover=\"window.status='$pa �������� �̵�';return true\" onmouseout=\"window.status='';return true\">$pa</a>]  ";
				}
			}
		}
		$nextp = $last + 1;
		if ($nextp <= $tot_pg) {
			print ".....[<a href=$gCgiUrl?page=$nextp onmouseover=\"window.status='���� ������ ����';return true\" onmouseout=\"window.status='';return true\">����</a>]";
		}
		else {
			print ".....[<font color=C0C0C0>����</font>]";
		}
	}
	$first = $first + $term;
	$last = $last + $term;
	}
	print "</td></tr></table></div>";

}

###############################################################################
sub changeConfig {
	$class_select = $FORM{'class_select'};
	$passad = $FORM{'passad'};
	$repassad = $FORM{'repassad'};
	$gConfListNum = $FORM{'listNum'};
	$gConfBgColor = $FORM{'bgColor'};
	$gConfBgImage = $FORM{'bgImage'};
	$gConfUseFormmail = $FORM{'useFormmail'};
	$gConfClassExp = $FORM{'ClassExp'};
	$gConfClassLongName = $FORM{'ClassLongName'};
	$gConfClassShortName = $FORM{'ClassShortName'};
	$gConfStartCls = $FORM{'StartCls'};
	$gConfEndCls = $FORM{'EndCls'};
	$gConfViewSpecial = $FORM{'ViewSpecial'};
	$gConfPreBody = $FORM{'PreBody'};
	$gConfPostBody = $FORM{'PostBody'};
	$gConfListType = $FORM{'ListType'};
	$FORM{'SpecialClass'} =~ s/\r/\n/g;
	@gConfSpecialClass = split(/\n/, $FORM{'SpecialClass'});

	if ($passad ne ""){
		if ($passad eq $repassad){
			$gConfAdminPass = crypt($passad,sp);
		}
		else {
			&printHead;
			print "<center>\n";
			print "<form><hr width=300 noshade>\n";
			print "�� ��й�ȣ�� �ٸ��ϴ�.\n";
			print "<hr width=300 noshade>\n";
			print "<INPUT type=button value=�ٽ��ۼ� onClick=history.go(-1) style=\"background-color:#ffffff;border:1 solid black;height:20\"></form>\n";
			&printFoot
		}
	}

	&putConf;

	&printHead;
	print "<center>\n";
	print "<META HTTP-EQUIV=Refresh CONTENT=0;URL=$gCgiUrl>\n";
	print "<p>&nbsp;<p>&nbsp;<p>&nbsp;<hr width=300 noshade>\n";
	print "ȯ��ȭ���� ���� �Ǿ����ϴ�.\n";
	print "<hr width=300 noshade>\n";
	print "<a href=$gCgiUrl>�ּҷ����� ���ư���</a>\n";
	&printFoot
}

###############################################################################
sub viewDetail {
	open(DATA,"<$gMainDir/data/$FORM{'number'}");
	$data = <DATA>;
	close (DATA);
	@wdata = split(/\|/,$data);
	$name = $wdata[3];
	if ($wdata[2] <= $#gConfSpecialClass) {
		$class = $gConfSpecialClass[$wdata[2]];
	}
	else {
		$class = ($gConfClassExp == 0) ? "$wdata[2]$gConfClassShortName" : substr($wdata[2],2,2) . $gConfClassShortName;
	}

	my($mailurl) = ($gConfUseFormmail) ? "javascript:newin(600, 400, '$gMailerCGI?cfg=familymail.cfg&$gMailerOptName=$name&$gMailerOptMail=$wdata[4]', 'mail')" : "mailto:$name <$wdata[4]>";
	$email = ($wdata[4] ne "") ? "<a href=\"javascript:newin(600, 400, '$gMailerCGI?cfg=familymail.cfg&name=$name&mail=$wdata[4]', 'mail')\" onmouseover=\"window.status='$name�Բ� ���� ����';return true\" onmouseout=\"window.status='';return true\">$wdata[4]</a>" : "�ᵵ ���� ���� �ݸ��̿���.";
	$email2 = ($wdata[4] ne "") ? "<a href=\"javascript:newin(600, 400, '$gMailerCGI?cfg=familymail.cfg&name=$name&mail=$wdata[4]', 'mail')\" onmouseover=\"window.status='$name�Բ� ���� ����';return true\" onmouseout=\"window.status='';return true\"><img src=\"$gImageUrl/mail.gif\" width=\"14\" height=\"10\" border=\"0\" alt=\"e-mail\"></a>" : "";
	$homepage = ($wdata[5] ne "" && $wdata[5] ne "http://") ? "<a href=\"$wdata[5]\" target=\"_blank\" onmouseover=\"window.status='$name���� Ȩ������ �湮';return true\" onmouseout=\"window.status='';return true\">$wdata[5]</a>" : "��� ����!!! I'm the homeless.";
	$homepage2 = ($wdata[5] ne "" && $wdata[5] ne "http://") ? "<a href=\"$wdata[5]\" target=\"_blank\" onmouseover=\"window.status='$name���� Ȩ������ �湮';return true\" onmouseout=\"window.status='';return true\"><img src=\"$gImageUrl/home.gif\" width=\"11\" height=\"12\" border=\"0\" alt=\"Homepage\"></a>" : "";

	@birth= split(/:/,$wdata[6]);
	$birthday = ($birth[0] ne "") ? " - $birth[0]�� $birth[1]�� $birth[2]�� ($birth[3])" : "";
	@address = split(/:/,$wdata[7]);
	if($address[1] ne ""){
		$address = "$address[1] $address[2] ($address[3]-$address[4])";
		$address1 = ($address[0] eq "H") ? "��" : "����";
	}
	else{
		$address = "I am the real homeless. T_T";
	}
	$home_tel = ($wdata[8] ne "") ? "$wdata[8]" : "��ȭ�� ���� ������ ����Ӵ�.";
	$job_tel = ($wdata[9] ne "") ? "$wdata[9]" : "���� ��ȭ? �����.";
	$hp = ($wdata[10] ne "") ? "$wdata[10]" : "������ �ô� �������,";
	$profile = ($wdata[12] ne "") ? "$wdata[12]" : "�� ����!!";
	$photoStr = &strURLEncode($wdata[11]);
#	$photo = ($wdata[11] ne "") ? "<img src=\"$gMainUrl/photos/$wdata[11]\" width=\"120\" height=\"150\" border=\"0\" alt=\"���� $name���� �����Դϴ�.\">" : "<img src=\"$gImageUrl/no_picture.gif\" width=\"120\" height=\"150\" border=\"0\" alt=\"�����ڵ�. �� �� ���� �����Ұɿ�. -_-��\">";
	$photo = ($wdata[11] ne "") ? "<img src=\"$gMainUrl/photos/$photoStr\" width=\"120\" height=\"150\" border=\"0\" alt=\"���� $name���� �����Դϴ�.\">" : "<img src=\"$gImageUrl/no_picture.gif\" width=\"120\" height=\"150\" border=\"0\" alt=\"�����ڵ�. �� �� ���� �����Ұɿ�. -_-��\">";

print <<START;
Content-type: text/html

<html>
<head><title>ȸ�� �ּҷ� - $name</title>
<style type='text/css'>
<!--
	BODY, table, tr, td {
		font-family: ����, ����ü, ����, ����ü, verdana, arial, helvetica, sans-serif;
		font-size: 9pt;
		color: black;
	}
	td.odd {
		font-family: ����, ����ü, verdana, arial, helvetica, sans-serif;
		font-size: 9pt;
		color: #51570B;
	}
	td.even {
		font-family: ����, ����ü, verdana, arial, helvetica, sans-serif;
		font-size: 9pt;
		color: #FF9900;
	}
	A:link    { color:steelblue; text-decoration:none; }
	A:visited { color:steelblue; text-decoration:none; }
	A:active  { color:steelblue; text-decoration:none; }
	A:hover   { color:#FF9090; text-decoration:none; }
-->
</style>
<script language=javascript>
<!--
	function newin(width,height,url,name) {
		msgWindow=window.open(url,name,'statusbar=no,scrollbars=yes,status=yes,resizable=yes,width='+width+',height='+height)
	}
// -->
</script>
</head>
<body bgcolor="#FFFFE7" leftmargin="0" topmargin="10" marginwidth="0" marginheight="10">
<table border="0" cellpadding="0" cellspacing="0" width="480" align="center">
    <tr>
        <td width="15" height="15"><p><img src="$gImageUrl/dv_lt.gif" width="15" height="15" border="0"></td>
        <td width="450" height="15"><p><img src="$gImageUrl/dv_top.gif" width="450" height="15" border="0"></td>
        <td width="15" height="15"><p><img src="$gImageUrl/dv_rt.gif" width="15" height="15" border="0"></td>
    </tr>
    <tr>
        <td width="15" background="$gImageUrl/dv_lett.gif"><p><img src="$gImageUrl/null.gif" width="15" height="15" border="0"></td>
        <td width="450" bgcolor="#FFFFAC"><table border="0" width="450" cellspacing="0" cellpadding="2">
                <tr>
                    <td width="450" colspan="3">&nbsp;&nbsp;<b><!--font color="#777777">$class</font--> $name</b>$birthday</td>
                </tr>
                <tr>
                    <td width="130" align="center" valign="top" rowspan="9">$photo</td>
                    <td align="right" valign="top" class="odd" width="60" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;"><b>�̸���</b></p></td>
                    <td valign="top" class="odd" width="260" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;">: $email</p></td>
                </tr>
                <tr>
                    <td align="right"valign="top" class="even" width="60" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;"><b>Ȩ������</b></p></td>
                    <td valign="top" class="even" width="260" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;">: $homepage</p></td>
                </tr>
                <tr>
                    <td align="right"valign="top" class="odd" width="60" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;"><b>$address1�ּ�</b></p></td>
                    <td valign="top" class="odd" width="260" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="text-indent:-10pt; margin-left:10pt; margin-top:2pt; margin-bottom:0pt; ">: $address</p></td>
                </tr>
                <tr>
                    <td align="right"valign="top" class="even" width="60" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;"><b>$address1��ȭ</b></p></td>
                    <td valign="top" class="even" width="260" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;">: $home_tel</p></td>
                </tr>
                <tr>
                    <td align="right"valign="top" class="odd" width="60" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;"><b>������ȭ</b></p></td>
                    <td valign="top" class="odd" width="260" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;">: $job_tel</p></td>
                </tr>
                <tr>
                    <td align="right"valign="top" class="even" width="60" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;"><b>BP, HP</b></p></td>
                    <td valign="top" class="even" width="260" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;">: $hp</p></td>
                </tr>
                <tr>
                    <td align="right"valign="top" class="odd" width="60"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;"><b>�ڱ�Ұ�</b></p></td>
                    <td valign="top" class="odd" width="260"><p style="margin-top:2pt; margin-right:0pt; margin-bottom:0pt; margin-left:0pt;">:</p></td>
                </tr>
                <tr>
                    <td valign="top" class="even" width="320" colspan="2" style="border-bottom-width:1pt; border-bottom-color:rgb(243,204,53); border-bottom-style:solid;"><p style="text-align:justify; line-height:150%; margin-top:0pt; margin-right:13; margin-bottom:0pt; margin-left:15;">$profile</p></td>
                </tr>
                <tr>
                    <td width="320" colspan="2" align="right">$homepage2 &nbsp; $email2&nbsp; &nbsp; &nbsp;</td>
                </tr>
            </table></td>
        <td width="15" background="$gImageUrl/dv_right.gif"><p><img src="$gImageUrl/null.gif" width="15" height="15" border="0"></td>
    </tr>
    <tr>
        <td width="15" height="15"><p><img src="$gImageUrl/dv_lb.gif" width="15" height="15" border="0"></td>
        <td width="450" height="15"><p><img src="$gImageUrl/dv_bottom.gif" width="448" height="15" border="0"></td>
        <td width="15" height="15"><p><img src="$gImageUrl/dv_rb.gif" width="15" height="15" border="0"></td>
    </tr>
</table>
</body>
</html>

START
}

###############################################################################
sub savePhoto {
	my($file_name) = $_[0];
	my($t);
	my(@x,@y);
    my($name, $save_file, $photo_data);

	$photo_data = $FORM{'photo'};
	@x = split(/\"/,$gRealFile[0]);
	@y = split(/\\/,$x[3]);
	$t = @y;

	$name = ($y[$t-1]);
	$name =~ s?(\S+)\.(gif|jpg|jpeg|png|bmp)?$file_name\.\2?oi;

	if ($name ne "") {
		$save_file = "$gMainDir/photos/$name";

		open(HANDLE,">$save_file") || &fileErr($save_file, $!);
		binmode(HANDLE);
		print HANDLE $photo_data;
		close(HANDLE);
		$photo_name = $name;
	}
}

###############################################################################
sub fileErr{
	&printHead;
	print "<p align=\"center\"><b><font size=+2>���ε� ���� - <font color=red>���� ���� ������ Ȯ���ϼ���!</font></font></b><br><br>\n"
		. "������ : $_[1]<br><br>\n"
		. "���ϸ� : $_[0]<br><br>\n"
		. "���� ����/����⿡ ������ �ֽ��ϴ�.<br>\n"
		. "��δ� ���� ������ '777'�� ���־�� �մϴ�.<br><br>\n"
		. "���� ����⸦ ����Ϸ��� ���� �����ϴ� ������ ������ '666' ���� �Ͻʽÿ�.</p>";
	&printFoot;
}

###############################################################################
# �ѱ� ���� ���ڿ� �ڸ���
# ���� : StringCutting("��Ʈ��", 10, "...", "on");
sub StringCutting {
	my($string,$len,$trail,$using) = @_;

	$len -= length($trail);
	if ($using eq 'on' && $len > 0 && length($string) > $len) {
		$string = substr ($string, 0, $len);
		chop $string if (($string =~ y/[\xA1-\xFE]//) % 2 != 0);
		$string = "$string$trail";
	}
	return $string;
}

######################�ߺ��� ID �� üũ�� �ִ� �����ƾ########################
sub id_check{
	$id_file = "./data/$FORM{'id'}";
	if (-e $id_file) {&cgiErrorMsg ("�̹� �����ϴ� ID �Դϴ�.");}
}

##########################�����޽����� ����ϴ� ����###########################
sub cgiErrorMsg {

	print <<END_OF_MESSAGE;
Content-type: text/html

<HTML>
<HEAD> <TITLE> Error !! </TITLE> </HEAD>
<BODY onLoad=\"alert('$_[0]');history.back()\">
</BODY>
</HTML>
END_OF_MESSAGE

exit;
}

###################�θ��� ����� ���� ���� ���� Lock ��ƾ#####################
sub lock {
    local($LockFile) = "lock.txt";
    local($EndTime) = time+45;
    
    while (-s $LockFile && time < $EndTime) {
    	sleep(1);
    }
    open(LOCK, "./$LockFile");
    print LOCK "lock";
    close(LOCK);
}

sub unlock {
    local($LockFile) = "lock.txt";
    
    open(LOCK, ">./$LockFile");
    print LOCK "";
    close(LOCK);
}

###################URL�� Ư�����ڷ� ��ȯ#####################
sub strURLEncode {
	$str = '';

	for ($i = 0; $i < length($_[0]); $i++) {
		$tok = substr($_[0], $i, 1);

		if ($tok =~ /[ 0-9A-Za-z@.]/) {

			if ($tok =~ / /) { $str .= "+"; }
			else { $str .= $tok; }
		}
		else {
			$str .= "%";
			$str .= sprintf("%02X", ord($tok));
		}
	}

	$str;
}

###################�����λ�#####################
sub send_mail {
	if ($FORM{'solar'} eq "plus") {$solar = "���";}
	else {$solar = "����";}
	if ($FORM{'sel_address'} eq "house") {$sel_address = "��";}
	else {$sel_address = "����";}

	$mail_contents = "\n"
					."  <ul>\n"
					."    <li>���� ����Ʈ�� ����� �ּż� �����մϴ�.</li>\n"
					."    <li>������ ������ �����ϵ��� �ּ��� ���ϰڽ��ϴ�.</li>\n"
					."    <li>���ϲ��� ���/�����Ͻ� ������ ������ �����ϴ�.</li>\n"
					."  </ul>\n"
					."  <table border=0 cellpadding=1 cellspacing=1 width=\"75\%\">\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>�̸� :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'name'}</font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>E-Mail :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'email'} </font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>Ȩ������ :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'url'} </font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>ID :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'id'}</font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>��й�ȣ :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> ********</font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>������� :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'birth_year'}�� $FORM{'birth_mon'}�� $FORM{'birth_day'}�� ($solar) </font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>�����ȣ :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'zip1'} - $FORM{'zip2'}</font></td>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>�ּ� :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> ($sel_address)$FORM{'address'} $FORM{'address2'} </font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>����ȭ :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'home_tel'}</font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>������ȭ :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'job_tel'} </font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>�޴��� :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'hp'} </font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."    <td width=20\% align=right><font size=\"2\"><b>�ڱ�Ұ� :</b></font></td>\n"
					."    <td width=80\%><font size=\"2\"> $FORM{'profile'} </font></td>\n"
					."  </tr>\n"
					."  <tr> \n"
					."</table>\n";

	open (MAIL, "|$mail_program -t");

	print MAIL "To: $FORM{'email'}\n";
	print MAIL "From: $admin_mail\n";
	print MAIL "Subject: ���� ����Ʈ�� ����� �ּż� �����մϴ�.\n";
	print MAIL "Content-type: text/html\n\n";
	print MAIL "$mail_contents\n\n";
	close (MAIL);
}

sub getdate {

	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	$month=($mon+1);

	if($year ne "99"){
		if($year > 100){$year=($year-100)+2000;}
		elsif($year < 10){$year=2000+$year;	}
		else{$year="2000";}
	}
	else{$year="1999";}

	if($month < 10) { $month="0$month";}
	if($mday < 10) { $mday="0$mday";}
	if($hour < 10) { $hour = "0$hour";}
	if($min < 10) { $min="0$min";}

	$date = "$year�� $month�� $mday�� $hour�� $min��";
	$short_date = "$year/$month/$mday $hour:$min";
}