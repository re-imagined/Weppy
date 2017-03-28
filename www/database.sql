drop database if exists weppy;

create database weppy;

use weppy;

create table user (
    `id` varchar(50) not null,
    `password` varchar(50) not null,
    `is_admin` bool not null,
    `name` varchar(50) not null,
    `created_at` varchar(50) not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table blog (
    `id` varchar(50) not null,
    `title` varchar(50) not null,
    `title_en` varchar(50) not null,
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `created_at` varchar(50) not null,
    `categery_id` int not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table Categery (
    `id` varchar(50) not null,
    `name` varchar(50) not null,
    primary key (`id`)
) engine=innodb default charset=utf8;

create table Tag (
    `id` varchar(50) not null,
    `name` varchar(50) not null,
    primary key (`id`)
) engine=innodb default charset=utf8;
