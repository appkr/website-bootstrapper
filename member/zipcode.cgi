#!/usr/bin/perl

##############################################################
# 우편번호 검색
##############################################################


&init;

if($FORM{'mode'} eq '') { &print_top; }
elsif($FORM{'mode'} eq 'top') { &show_top; }
elsif($FORM{'mode'} eq 'down') { &show_down; }
elsif($FORM{'mode'} eq 'search') { &search; }



##########################################################################
sub search {

	my $query = $FORM{'query'};

print "Content-type: text/html\n\n";
print<<END;
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=euc-kr">
<LINK rel="stylesheet" type="text/css" href="./ie4css.css">
<SCRIPT language="JavaScript">
function Copy(zip1,zip2,address) {
	// copy
	top.opener.document.$FORM{form}.$FORM{zip1}.value = zip1;
	top.opener.document.$FORM{form}.$FORM{zip2}.value = zip2;
	top.opener.document.$FORM{form}.$FORM{address}.value = address;

	// focus
	top.opener.document.$FORM{form}.address2.focus();

	// close this window
	parent.window.close();

}
</SCRIPT>
<TITLE>우편번호 검색</TITLE>
</head>
<body bgcolor=#EEEEEE leftmargin=0 topmargin=0 marginwidth=0 marginheight=0>
<center>
<table cellspacing=1 cellpadding=3 width=97% align=center><tr><td><hr size=1><ul>

END

	require 'zipcode.pm';

	if($FORM{searchmode} eq 'address') {
		$ref = &zipcode_address($query);
	} elsif($FORM{searchmode} eq 'code') {
		$ref = &zipcode_code($query);
	}

	for(sort keys %$ref) {
		my ($zip1, $zip2) = $_ =~ /(...)(...)/;
		print qq|<li>$zip1-$zip2\&nbsp;\&nbsp;\n<a href="Javascript:Copy('$zip1','$zip2','$$ref{$_}');">$$ref{$_}</a><br>\n|;
	}

print <<END;
</ul>
<hr size=1>
<center>검색을 완료했습니다.</center>
</table>

<FORM action=zipcode.cgi method=post name=gil>
<input type=hidden name=mode value=search>
<input type=hidden name=form value=$FORM{form}>
<input type=hidden name=zip1 value=$FORM{zip1}>
<input type=hidden name=zip2 value=$FORM{zip2}>
<input type=hidden name=address value=$FORM{address}>

<font color=#404040>
검색어: <input type=text name=query size=15 class=input>
<select name=searchmode size=1 onChange=document.gil.query.focus() class="input">
<option value=address>주소로 찾기
<option value=code>우편번호로 찾기
</select>
<input type=submit value="검색" class="button">
</FORM>
</body>
</html>

END

}


##########################################################################
sub print_top {
print "Content-type: text/html\n\n";
print<<END;
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=euc-kr">
<LINK rel="stylesheet" type="text/css" href="http://www.webweaver.pe.kr/css/ie4css.css">
<SCRIPT language="JavaScript">
</SCRIPT>
<TITLE>우편번호 검색</TITLE>

</head>
<body bgcolor=#EEEEEE onLoad=document.gil.query.focus() leftmargin=0 topmargin=0 marginwidth=0 marginheight=0>
<center>
<TABLE Width=97% CelLSpacing=0 CellPadding=2>
<TR>
   <TD align="center"><br>찾고자 하는 주소의 동/읍/면 이름을 입력하세요.<br><br>
   (예:압구정동/단양읍/수산면)<br><br>
   <hr size=1><br>
   </TD>
</TR>
<TR>
   <TD align="center">
<FORM action=zipcode.cgi method=post name=gil>
<input type=hidden name=mode value=search>

<input type=hidden name=form value=$FORM{form}>
<input type=hidden name=zip1 value=$FORM{zip1}>
<input type=hidden name=zip2 value=$FORM{zip2}>
<input type=hidden name=address value=$FORM{address}>

<font color=#404040>
END

if ($FORM{zip} eq "" || $FORM{zip} eq "-") {
	print "검색어: <input type=text name=query size=15 class=\"input\">\n";
	print "<select name=searchmode size=1 onChange=document.gil.query.focus() class=\"input\">\n";
	print "<option value=address selected>주소로 찾기</option>\n";
	print "<option value=code>우편번호로 찾기</option>\n";
	print "</select>\n";
}
else {
	print "검색어: <input type=text name=query size=15 class=\"input\" value=\"$FORM{zip}\">\n";
	print "<select name=searchmode size=1 onChange=document.gil.query.focus() class=\"input\">\n";
	print "<option value=address>주소로 찾기</option>\n";
	print "<option value=code selected>우편번호로 찾기</option>\n";
	print "</select>\n";
}
	
print<<END;
<input type=submit value="검색" class="button">
</FORM>
      </TD>
   </TR>
   </TABLE>
</center>
</body>
</html>

END

}





##########################################################################
sub init {
	if ($ENV{'REQUEST_METHOD'} eq "POST") { read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'}); } 
	else { $buffer = $ENV{'QUERY_STRING'}; }

	for (split '&', $buffer) { 
		my ($name, $value) = split '=';
		$name =~ tr/+/ /;  $name =~ s/%(..)/chr(hex($1))/ge;
		$value =~ tr/+/ /;  $value =~ s/%(..)/chr(hex($1))/ge;
		$FORM{$name} = $value;
	}

}


__END__
