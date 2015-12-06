sub cgiReadInput {

  # CGI �Է°��� �о�鿩 �и��ϴ� �����ƾ

  if ($ENV{'REQUEST_METHOD'} eq 'POST') {	# POST �޼ҵ��� ���

    read(STDIN, $query_string, $ENV{'CONTENT_LENGTH'});
  }

  if ($ENV{'REQUEST_METHOD'} eq 'GET') {	# GET �޼ҵ��� ���
   
    $query_string = $ENV{'QUERY_STRING'};
  }

  @pairs = split(/&/, $query_string);		# &�� ���Ǿ �и�

  foreach $field(@pairs) {
  
    ($name, $value) = split(/=/, $field);	# =�� name, value �и�
    
    $name = &strURLDecode($name);
    $value = &strURLDecode($value);

    $FORM{$name} = $value;			# %FORM ���� �迭�� ����
  }

  # ��Ű�� �о����

  $cookie_string = $ENV{'HTTP_COOKIE'};
  @pairs = split(/; /, $cookie_string);

  foreach $field(@pairs) {

    ($name, $value) = split(/=/, $field);	# =�� name, value �и�
  
    $name = &strURLDecode($name);
    $value = &strURLDecode($value);

    $COOKIE{$name} = $value;                    # %COOKIE ���� �迭�� ����
  }

}


sub strURLEncode {

  # ���ڿ��� URL Encoding �Ѵ�.

  $str = '';

  for ($i = 0; $i < length($_[0]); $i++) {
    $tok = substr($_[0], $i, 1);		# �� ���ڸ� �о

    if ($tok =~ /[ 0-9A-Za-z@.]/) {		# ����, ����, ����

      if ($tok =~ / /) { $str .= "+"; }		# ����?
      else { $str .= $tok; }
    }
    else {					# Ư�� ������ ���

      $str .= "%";
      $str .= sprintf("%02X", ord($tok));
    }
  }

  $str;
}

sub strURLDecode {

  # ���ڿ��� URL Decoding �Ѵ�.

  $str = $_[0];

  $str =~ tr/+/ /;                       	# +�� �������� �ٲ�	 
  $str =~ s/%([A-F0-9][A-F0-9])/pack("C", hex($1))/egi;
						# %XX ���¸� ���� ���ڷ� �ٲ�
  $str;
}


sub cgiSetCookie {

  # ��Ű(Cookie) ����

  $name = $_[0];
  $value = $_[1];

  $name = &strURLEncode($name);			# URL Encoding
  $value = &strURLEncode($value); 

  # Print Cookie Setting

  print "Set-Cookie: $name=$value;\n";

} 
  

sub cgiErrorMsg {

  # ���� �޽��� ���

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


return 1;

