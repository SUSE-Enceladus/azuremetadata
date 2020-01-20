#Copyright (C) 2020 SUSE LLC
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
package AzureDisk;

use strict;
use warnings;

use File::Basename;
use POSIX;


our @ISA    = qw (Exporter);
our @EXPORT_OK = qw (
    getVHDDiskTag
);

sub get_root_device {
    my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
        $atime,$mtime,$ctime,$blksize,$blocks) = stat('/');
    my $device_idh = sprintf("%X", $dev);
    my @block_devices = glob('/sys/block/*');
    for my $block_device (@block_devices) {
        my $found_root = 0;
        my $block_device_name = basename($block_device);
        my @partitions =
            glob("/sys/block/$block_device_name/$block_device_name*");
        for my $partition (@partitions) {
            open my $device_info, '<', "$partition/dev";
            read $device_info, my $device_data, -s $device_info;
            close $device_info;
            my @major_minor = split ':', $device_data;
            my $minor = pop @major_minor;
            my $major = pop @major_minor;
            my $majorh = sprintf("%X", $major);
            my $minorh = sprintf("%X", $minor);
            if (length $minorh < 2) {
                $minorh = '0' . $minorh;
            }
            my $current_device_ih = $majorh . $minorh;
            if ($current_device_ih eq $device_idh) {
                return "/dev/$block_device_name";
            }
        }
    }
}

sub getVHDDiskTag {
    my $file = shift;
    my $fh;
    my $read_bytes;
    my $junk;
    my $result;
    my $done;
    if (! $file) {
        $file = get_root_device();
    }
    if (! sysopen($fh,$file, O_RDONLY)) {
        die "open file $file failed: $!"
    }
    # Read the tag at 64K boundary
    seek $fh,65536,0;
    $read_bytes = sysread ($fh, $done, 4);
    if ($read_bytes != 4) {
        die "sysread failed, want 4 bytes got $read_bytes"
    }
    $junk = unpack 'l',  $done;
    $junk = pack   'l>', $junk;
    $junk = unpack 'H*', $junk;
    $result = "$junk-";
    $read_bytes = sysread ($fh, $done, 2);
    if ($read_bytes != 2) {
        die "sysread failed, want 2 bytes got $read_bytes"
    }
    $junk = unpack 'S',  $done;
    $junk = pack   'S>', $junk;
    $junk = unpack 'H*', $junk;
    $result.= "$junk-";
    $read_bytes = sysread ($fh, $done, 2);
    if ($read_bytes != 2) {
        die "sysread failed, want 2 bytes got $read_bytes"
    }
    $junk = unpack 'S',  $done;
    $junk = pack   'S>', $junk;
    $junk = unpack 'H*', $junk;
    $result.= "$junk-";
    $read_bytes = sysread ($fh, $done, 2);
    if ($read_bytes != 2) {
        die "sysread failed, want 2 bytes got $read_bytes"
    }
    $junk = unpack 'H*', $done;
    $result.= "$junk-";
    $read_bytes = sysread ($fh, $done, 6);
    if ($read_bytes != 6) {
        die "sysread failed, want 6 bytes got $read_bytes"
    }
    $junk = unpack 'H*', $done;
    $result.= $junk;
    close $fh;
    return $result;
}

1;
