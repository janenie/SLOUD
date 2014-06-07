CREATE TABLE `res` (

       `rid` int(11) unsigned NOT NULL auto_increment,
       `owner` varchar(60) NOT NULL,
       `short` varchar(60) NOT NULL,
       `utime` timestamp NOT NULL,
       `etime` timestamp NOT NULL,
       `flag` int(11) unsigned NOT NULL default 0,
       `description` varchar(140) NOT NULL,
       `lastfilename` varchar(140) NOT NULL,
       `visited` int(20) NOT NULL default 0,

       PRIMARY KEY (rid),
       KEY (owner),
       KEY (owner, short),
       KEY (etime)
) ENGINE=InnoDB  DEFAULT CHARSET=UTF8 ;

CREATE TABLE `file` (
       `pid` int(11) unsigned NOT NULL auto_increment,
       `rid` int(11) unsigned NOT NULL,
       `filename` varchar(60) NOT NULL,
       `savename` varchar(60) NOT NULL,
       `utime` timestamp NOT NULL,
       `etime` timestamp NOT NULL,
       `fflag` int(11) unsigned NOT NULL default 0,
       `download` int(20) NOT NULL default 0,

       PRIMARY KEY (pid),
       KEY (savename),
       KEY (rid),
       KEY (etime)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8 ;
