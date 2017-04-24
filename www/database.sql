drop database if exists weppy;

create database weppy;

use weppy;

create table user (
    `id` varchar(50) not null comment 'id of the user',
    `password` varchar(50) not null comment 'password of the user',
    `is_admin` bool not null comment 'set 1 if the user is an admin',
    `name` varchar(50) not null comment 'name of user',
    `created_at` varchar(50) not null comment 'create time',
    unique key `name` (`name`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table blog (
    `id` bigint(20) not null auto_increment comment 'id of user',
    `title` varchar(50) not null comment 'title of the blog',
    `title_en` varchar(50) not null comment 'English title used in url',
    `summary` varchar(200) not null comment 'first few lines of the blog',
    `content` mediumtext not null comment 'content of the blog',
    `created_at` datetime not null comment 'create time',
    `categery_id` varchar(50) not null comment 'id of categery',
    unique key `title_en` (`title_en`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table categery (
    `id` bigint(20) not null auto_increment comment 'id of the categery',
    `name` varchar(50) not null comment 'name of the categery',
    unique key `name` (`name`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table tag (
    `id` bigint(20) not null auto_increment,
    `name` varchar(50) not null,
    unique key `name` (`name`),
    primary key (`id`)
) engine=innodb default charset=utf8;
