alter table ticketing_ticketitem add column badgeable tinyint(1) not null default 0;
alter table ticketing_ticketitem add column ticket_style varchar(50) NOT NULL;
