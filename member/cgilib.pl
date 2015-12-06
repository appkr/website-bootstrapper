sub cgiReadInput {

  # CGI 입력값을 읽어들여 분리하는 서브루틴

  if ($ENV{'REQUEST_METHOD'} eq 'POST') {	# POST 메소드의 경우

    read(STDIN, $query_string, $ENV{'CONTENT_LENGTH'});
  }

  if ($ENV{'REQUEST_METHOD'} eq 'GET') {	# GET 메소드의 경우
   
    $query_string = $ENV{'QUERY_STRING'};
  }

  @pairs = split(/&/, $query_string);		# &로 질의어를 분리

  foreach $field(@pairs) {
  
    ($name, $value) = split(/=/, $field);	# =로 name, value 분리
    
    $name = &strURLDecode($name);
    $value = &strURLDecode($value);

    $FORM{$name} = $value;			# %FORM 결합 배열에 저장
  }

  # 쿠키를 읽어들임

  $cookie_string = $ENV{'HTTP_COOKIE'};
  @pairs = split(/; /, $cookie_string);

  foreach $field(@pairs) {

    ($name, $value) = split(/=/, $field);	# =로 name, value 분리
  
    $name = &strURLDecode($name);
    $value = &strURLDecode($value);

    $COOKIE{$name} = $value;                    # %COOKIE 결합 배열에 저장
  }

}


sub strURLEncode {

  # 문자열을 URL Encoding 한다.

  $str = '';

  for ($i = 0; $i < length($_[0]); $i++) {
    $tok = substr($_[0], $i, 1);		# 한 문자를 읽어냄

    if ($tok =~ /[ 0-9A-Za-z@.]/) {		# 문자, 공백, 숫자

      if ($tok =~ / /) { $str .= "+"; }		# 공백?
      else { $str .= $tok; }
    }
    else {					# 특수 문자일 경우

      $str .= "%";
      $str .= sprintf("%02X", ord($tok));
    }
  }

  $str;
}

sub strURLDecode {

  # 문자열을 URL Decoding 한다.

  $str = $_[0];

  $str =~ tr/+/ /;                       	# +를 공백으로 바꿈	 
  $str =~ s/%([A-F0-9][A-F0-9])/pack("C", hex($1))/egi;
						# %XX 형태를 원래 문자로 바꿈
  $str;
}


sub cgiSetCookie {

  # 쿠키(Cookie) 설정

  $name = $_[0];
  $value = $_[1];

  $name = &strURLEncode($name);			# URL Encoding
  $value = &strURLEncode($value); 

  # Print Cookie Setting

  print "Set-Cookie: $name=$value;\n";

} 
  

sub cgiErrorMsg {

  # 에러 메시지 출력

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

