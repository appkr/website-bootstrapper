##############################################################
# 우편번호 검색
##############################################################
# 파일에 '경기도' 처럼 해당 도 또는 광역시 이름이 없는 파일
%do = qw(
경기도 1
경상남도 1
경상북도 1
서울특별시 1
강원도 1
충청북도 1
충청남도 1
전라남도 1
전라북도 1
제주도 1
);

# 우편번호 DB 파일을 만들때 순서, 파일크기가 부족하나마 우선순위를 결정해주므로..
sub by_size { -s $b <=> -s $a }

open F, ">zipcode.pl";

opendir DIR, ".";
for $f (sort by_size readdir DIR) {
	next if $f =~ /^\./;
	next unless $f =~ /\.txt$/i;

	($do) = $f =~ /(.+)\./;
	unless($do{$do}) { $do = ''; }
	else { $do = "$do "; }

	open GIL, $f;
	while(<GIL>) {
		if(/^\s*(\d{6})\s*(\S.+?)\s{5,}(\S.+)/) {
			my ($zip, $town, $city) = ($1, $2, $3);
			$town =~ s/\s{2,}/ /g;
			$city =~ s/\s{2,}/ /g;
			print F "$zip\t$do$city $town\n";
		}
	}
	close GIL;
}
closedir DIR;

close F;
