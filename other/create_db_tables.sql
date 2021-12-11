CREATE TABLE IF NOT EXISTS users (
	id_user SERIAL,
	email VARCHAR(40) NOT NULL,
	pass_hash VARCHAR(100) NOT NULL,
	lastname VARCHAR(20) NOT NULL,
	firstname VARCHAR(20) NOT NULL,
	avatar BYTEA,
	CONSTRAINT user_pkey PRIMARY KEY(id_user),
	CONSTRAINT user_unique_email UNIQUE(email),
	CONSTRAINT user_check_strings CHECK(
		(email != '') AND (firstname != '') AND (lastname != '')
	)
);

CREATE TABLE IF NOT EXISTS conferences (
	id_conf SERIAL,
	title VARCHAR(60) NOT NULL,
	description TEXT,
	time_conf TIMESTAMP NOT NULL,
	period_conf INTERVAL,
	id_creator INTEGER,
	is_active BOOLEAN,
	CONSTRAINT conf_pkey PRIMARY KEY(id_conf),
	CONSTRAINT conf_check_strings CHECK(
		(title != '')
	)
);

CREATE TABLE IF NOT EXISTS user_conf (
	id_user INTEGER NOT NULL,
	id_conf INTEGER NOT NULL,
	in_conf BOOLEAN DEFAULT FALSE NOT NULL,
	FOREIGN KEY(id_user) REFERENCES users(id_user) ON DELETE CASCADE,
	FOREIGN KEY(id_conf) REFERENCES conferences(id_conf) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_invite (
	id_user INTEGER NOT NULL,
	id_conf INTEGER NOT NULL,
	time_send INTEGER NOT NULL,
	FOREIGN KEY(id_user) REFERENCES users(id_user) ON DELETE CASCADE,
	FOREIGN KEY(id_conf) REFERENCES conferences(id_conf) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_story (
	id_story SERIAL NOT NULL,
	id_user INTEGER,
	id_conf INTEGER,
	time_paste TIME NOT NULL,
	msg TEXT NOT NULL,
	PRIMARY KEY(id_story),
	FOREIGN KEY(id_user) REFERENCES users(id_user) ON DELETE SET NULL,
	FOREIGN KEY(id_conf) REFERENCES conferences(id_conf) ON DELETE CASCADE
);