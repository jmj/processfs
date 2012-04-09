# Welcome to the processfs wiki! #

## Design thoughts ##

*   Write (new file)

    Writting to a file, should create a new process, such that:

        echo "/usr/bin/myproc --config /etc/foo" > /my/pfs/myproc

    will execute /usr/bin/myproc with options --config /etc/foo, and create
    a "monitoring file" at myproc

    *   Interesting twist:  in normal circumstances, the above works.  The
        process will be started as the user running the fs daemon.  However,
        if the FS is mounted by root:

        The user (assuming they can write to the dir) can create an empty file
        (touch myproc), the change owner/group, then write process command
        line, and the process is started as that user/group.

        There for chown/chgrp need to be trapped, and only acted upon if
        FS daemon is running as root


*   Write (existing file)

    Write to an existing ("non-empty") file connectes to process stdin

*   Read

    File reads should be connected to stdin/stdout.  For memoring concerns, this
    can be facillitated by means of a ring buffer, with buffer length set
    by a command line/mount option (eaisily done with collections.deque).

*   Stat

    Can dump a bunch of usefull process information (runtime, mem, etc.)

*   rm

    Removing a file will cause the process to be terminated.
