#!/usr/bin/perl

####################################################################
#�� ��ũ��Ʈ�� ���ֿ��� ���� ���Դϴ�.                             #
#�� ��ũ��Ʈ�� �������� ���Ƿ� ����ϰų� �����ϼŵ� �����մϴ�.   #
#�����Ͻ� ��쿡�� ������ ������ ������ �˷� �ֽø� �����ϰڽ��ϴ�.#
#�� �����Ͻ� ��쿡�� �����ڸ� ���� �ֽʽÿ�.                      #
#���ֿ� webweaver@webweaver.pe.kr                                  #
#                                      2000�� 6��                  #
####################################################################

#########################id�ߺ� üũ id_check.cgi###################
$cgi_url = $ENV{'SCRIPT_NAME'};
####################################################################
require "cgilib.pl";
&cgiReadInput;
&id_check;

#HEAD ��� �κ�######################################################
sub printHead {
print <<START;
Content-type: text/html

<!-------------------------------------------------------------->
<!-- Program by JuWon,Kim You can use this script Freely      -->
<!-- email : suchcool\@shinbiro.com                           -->
<!-------------------------------------------------------------->
<html>
<head><title>ID �ߺ� Ȯ�� �ϱ�</title>
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

#TAIL ��� �κ�######################################################
sub printFoot {
	print "</body></html>\n";
	exit;
}

#�ߺ� ID CHECK#####################################################
sub id_check{
	if ($FORM{'id'} eq "") {&idErrorMsg("ID (��)�� �Է����� �ʾҽ��ϴ�.")};

	$id_file = "./data/$FORM{'id'}";
	if (-e $id_file) {&idErrorMsg("$FORM{'id'} (��)�� �̹� �����ϴ� ID �Դϴ�.");}
	&printHead;
	print <<START;
<table width="98%" border="0" align="center" height="98%">
  <tr valign="middle"> 
    <td align="center"> 
      <form method="post" action="$cgi_url" name="checkForm">
        <input type="hidden" name="ok" value="$FORM{'id'}">
        <font size="3" color="#333399"><b>$FORM{'id'}</b></font> (��)�� ��� ������ ID �Դϴ�. <br>
        <br>
        <input type="button" value="ID ����ϱ�" class="button" onClick=Copy("$FORM{'id'}")>
        <input type="button" value=" �� �� " class="button" onClick="window.close()">
        <br>
        <br>
        <hr width="98%%" size="1" noshade>
        ���ο� ID �˻� �ϱ� : 
        <input type="text" name="id" size="10" maxlength="8" class="input">
        <input type="submit" value=" �� �� " class="button">
        <br>
      </form>
    </td></tr>
</table>
START
	&printFoot;
}

##########################�����޽����� ����ϴ� ����###########################
sub idErrorMsg {

  # ���� �޽��� ���
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
        ���ο� ID �˻� �ϱ� : 
        <input type="text" name="id" size="10" maxlength="8" class="input">
        <input type="submit" value=" �� �� " class="button">
        <br>
      </form>
    </td></tr>
</table>
START
	&printFoot;
}
