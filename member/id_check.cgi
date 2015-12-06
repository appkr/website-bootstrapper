#!/usr/bin/perl

####################################################################
#이 스크립트는 김주원이 만든 것입니다.                             #
#이 스크립트는 여러분은 임의로 사용하거나 수정하셔도 무방합니다.   #
#수정하실 경우에는 수정된 내용을 저에게 알려 주시면 감사하겠습니다.#
#재 배포하실 경우에는 원작자를 밝혀 주십시오.                      #
#김주원 webweaver@webweaver.pe.kr                                  #
#                                      2000년 6월                  #
####################################################################

#########################id중복 체크 id_check.cgi###################
$cgi_url = $ENV{'SCRIPT_NAME'};
####################################################################
require "cgilib.pl";
&cgiReadInput;
&id_check;

#HEAD 출력 부분######################################################
sub printHead {
print <<START;
Content-type: text/html

<!-------------------------------------------------------------->
<!-- Program by JuWon,Kim You can use this script Freely      -->
<!-- email : suchcool\@shinbiro.com                           -->
<!-------------------------------------------------------------->
<html>
<head><title>ID 중복 확인 하기</title>
<meta http-equiv="Content-Type" content="text/html; charset=euc-kr">

<LINK rel="stylesheet" type="text/css" href="http://www.webweaver.pe.kr/css/ie4css.css">

<script language=javascript>
function newin(width,height,url,name) {
	msgWindow=window.open(url,name,'statusbar=no,scrollbars=yes,status=yes,resizable=yes,width='+width+',height='+height)
}
function Copy(ok) {
	// copy
	top.opener.document.form.id.value = ok;

	// focus
	top.opener.document.form.passwd.focus();

	// close this window
	parent.window.close();

}
</script>
</head>
<BODY leftmargin=0 topmargin=0 marginwidth=0 marginheight=0 bgcolor="#EEEEEE">
<center>
START
}

#TAIL 출력 부분######################################################
sub printFoot {
	print "</body></html>\n";
	exit;
}

#중복 ID CHECK#####################################################
sub id_check{
	if ($FORM{'id'} eq "") {&idErrorMsg("ID (을)를 입력하지 않았습니다.")};

	$id_file = "./data/$FORM{'id'}";
	if (-e $id_file) {&idErrorMsg("$FORM{'id'} (은)는 이미 존재하는 ID 입니다.");}
	&printHead;
	print <<START;
<table width="98%" border="0" align="center" height="98%">
  <tr valign="middle"> 
    <td align="center"> 
      <form method="post" action="$cgi_url" name="checkForm">
        <input type="hidden" name="ok" value="$FORM{'id'}">
        <font size="3" color="#333399"><b>$FORM{'id'}</b></font> (은)는 사용 가능한 ID 입니다. <br>
        <br>
        <input type="button" value="ID 사용하기" class="button" onClick=Copy("$FORM{'id'}")>
        <input type="button" value=" 취 소 " class="button" onClick="window.close()">
        <br>
        <br>
        <hr width="98%%" size="1" noshade>
        새로운 ID 검색 하기 : 
        <input type="text" name="id" size="10" maxlength="8" class="input">
        <input type="submit" value=" 검 색 " class="button">
        <br>
      </form>
    </td></tr>
</table>
START
	&printFoot;
}

##########################에러메시지를 출력하는 서브###########################
sub idErrorMsg {

  # 에러 메시지 출력
	&printHead;
	print <<START;
<table width="98%" border="0" align="center" height="98%">
  <tr valign="middle"> 
    <td align="center"> 
      <form method="post" action="$cgi_url" name="checkForm">
        <input type="hidden" name="ok" value="$FORM{'id'}">
        <font size="3" color="#333399"><b>$_[0]</b></font><br>
        <br>
        <hr width="98%" size="1" noshade>
        새로운 ID 검색 하기 : 
        <input type="text" name="id" size="10" maxlength="8" class="input">
        <input type="submit" value=" 검 색 " class="button">
        <br>
      </form>
    </td></tr>
</table>
START
	&printFoot;
}
