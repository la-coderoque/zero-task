drop schema if exists markup cascade;
create schema markup;

create table markup.users (
	username varchar(50) unique primary key,
	password varchar(50)
);

create table markup.tg_users (
	id int unique primary key,
	authorized_as varchar(50),
	constraint fk_user foreign key(authorized_as) references markup.users(username)
);

create table markup.files (
	id uuid unique primary key not null,
	classes  varchar(50) not null,
	processed varchar(50),
	username varchar(50),
	constraint fk_user foreign key(username) references markup.users(username)
);
