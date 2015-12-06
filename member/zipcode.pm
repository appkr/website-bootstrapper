##############################################################
# 우편번호 검색
##############################################################

##############################################################
# 사용방법
# (함수에 전달하는 값은 그냥 데이타 입력, 리턴받을때는 참조변수로 받음,
# 참조변수는 해쉬를 가리키고 있음)
#
### 주소의 일부분으로 검색 할 때
# require 'zipcode.pm';
# $ref = &zipcode_address("중구");
# for(sort keys %$ref) {
#		print "$_ $$ref{$_}\n";
# }
#
### 우편번호 전부 또는 일부분으로 검색 할 때
# require 'zipcode.pm';
#	$ref = &zipcode_code("151053");
#	for(sort keys %$ref) {
#		print "$_ $$ref{$_}\n";
#	}
##############################################################

##############################################################
# 주소 일부분을 이용해서 우편번호, 전체주소 검색
# 검색성공시, (우편번호, 주소) 의 해쉬 참조값 전달
sub zipcode_address {
	my %ZIPCODE;
	my $text = shift;
	return {'0', '검색어를 입력 하십시요!'} if $text eq '';

	open GIL, "zipcode.db"	or return {'0', '목록에 없습니다!'};
	while(<GIL>) {
		chomp;
		my ($z, $a) = split /\t/;
		(my $tmp = $a) =~ y/ //d;
		$ZIPCODE{$z} = $a if $tmp =~ /\Q$text/;
	}
	close GIL;

	\%ZIPCODE;
}





##############################################################
# 부정확한/정확한 우편번호로 주소 검색
# 검색성공시, (우편번호, 주소) 의 해쉬 참조값 전달
# 우편번호는 입력시에 151-053 처럼해도 되고 151053 처럽입력해도 가능함
sub zipcode_code {
	my %ZIPCODE;
	my $code = shift;
	return {'0', '검색어를 입력 하십시요!'} if $code eq '';
	$code =~ y/- //d;

	open GIL, "zipcode.db"	or return {'0', '목록에 없습니다!'};
	while(<GIL>) {
		chomp;
		my ($z, $a) = split /\t/;
		$ZIPCODE{$z} = $a if $z =~ /$code/;
	}
	close GIL;

	\%ZIPCODE;
}

1;

__END__

