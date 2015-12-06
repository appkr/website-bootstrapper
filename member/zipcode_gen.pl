##############################################################
# �����ȣ �˻�
##############################################################
# ���Ͽ� '��⵵' ó�� �ش� �� �Ǵ� ������ �̸��� ���� ����
%do = qw(
��⵵ 1
��󳲵� 1
���ϵ� 1
����Ư���� 1
������ 1
��û�ϵ� 1
��û���� 1
���󳲵� 1
����ϵ� 1
���ֵ� 1
);

# �����ȣ DB ������ ���鶧 ����, ����ũ�Ⱑ �����ϳ��� �켱������ �������ֹǷ�..
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
