DROP DATABASE IF EXISTS moneydatabase;
CREATE DATABASE moneydatabase;
USE moneydatabase;

/*Normal Tables*/
DROP TABLE IF EXISTS table_users;
CREATE TABLE table_users(
    user_id INT NOT NULL AUTO_INCREMENT,
    user_name TEXT  NOT NULL,
    user_pass TEXT NOT NULL,
    user_isAdmin BOOLEAN DEFAULT 0
    PRIMARY KEY(user_id)
);

DROP TABLE IF EXISTS table_settings;
CREATE TABLE table_settings(
    setting_id INT NOT NULL AUTO_INCREMENT,
    setting_monthly BOOLEAN DEFAULT 1,
    setting_del_prev BOOLEAN DEFAULT 0,
    setting_def_p_use BOOLEAN DEFAULT 30,
    setting_auto_month BOOLEAN DEFAULT 0,
    setting_auto_next_date DATE NOT NULL,
    PRIMARY KEY(setting_id)
);

DROP TABLE IF EXISTS table_months;
CREATE TABLE table_months(
    month_id INT NOT NULL AUTO_INCREMENT,
    month_income INT NOT NULL DEFAULT 0,
    month_p_use INT NOT NULL DEFAULT 30,
    month_pay_date DATE NOT NULL,
    month_setup_finalised BOOLEAN DEFAULT 0,
    month_success BOOLEAN DEFAULT 0,
    PRIMARY KEY(month_id)
);

DROP TABLE IF EXISTS table_monthly_expense;
CREATE TABLE table_monthly_expense(
    exp_id INT NOT NULL AUTO_INCREMENT,
    exp_name TEXT NOT NULL,
    exp_amount INT NOT NULL DEFAULT 0,
    exp_source TEXT NOT NULL,
    exp_reason TEXT,
    PRIMARY KEY(exp_id)
);

DROP TABLE IF EXISTS table_modifiers;
CREATE TABLE table_modifiers(
    mod_id INT NOT NULL AUTO_INCREMENT,
    mod_name TEXT NOT NULL,
    mod_amount INT NOT NULL DEFAULT 0,
    mod_source TEXT NOT NULL,
    mod_reason TEXT,
    mod_expense BOOLEAN DEFAULT 1,
    PRIMARY KEY(mod_id)
);

DROP TABLE IF EXISTS table_postpone_expense;
CREATE TABLE table_postpone_expense(
    post_id INT NOT NULL AUTO_INCREMENT,
    post_name TEXT NOT NULL,
    post_amount INTEGER NOT NULL DEFAULT 0,
    post_source TEXT NOT NULL,
    post_reason TEXT,
    post_times INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY(post_id)
);

DROP TABLE IF EXISTS table_actual;
CREATE TABLE table_actual(
    act_id INT NOT NULL AUTO_INCREMENT,
    act_name TEXT NOT NULL,
    act_amount INT NOT NULL DEFAULT 0,
    act_date DATE NOT NULL,
    act_p_type TEXT NOT NULL DEFAULT "contactless",
    act_week INT NOT NULL DEFAULT 1,
    act_reason TEXT,
    act_isExpense BOOLEAN DEFAULT 1,
    PRIMARY KEY(act_id)
);

DROP TABLE IF EXISTS table_sources;
CREATE TABLE table_sources(
    src_id INT NOT NULL,
    src_name TEXT NOT NULL,
    src_description TEXT,
    PRIMARY KEY(src_id)
);

/*Link Tables*/
DROP TABLE IF EXISTS link_user_settings;
CREATE TABLE link_user_settings(
    user_id INT NOT NULL,
    setting_id INT NOT NULL,
    PRIMARY KEY(user_id),
    FOREIGN KEY(user_id) REFERENCES table_users(user_id),
    FOREIGN KEY(setting_id) REFERENCES table_settings(setting_id)
);

DROP TABLE IF EXISTS link_user_month;
CREATE TABLE link_user_month(
    user_id INT NOT NULL,
    month_id INT NOT NULL,
    PRIMARY KEY(user_id),
    FOREIGN KEY(user_id) REFERENCES table_users(user_id),
    FOREIGN KEY(month_id) REFERENCES table_months(month_id)
);

DROP TABLE IF EXISTS link_month_expense;
CREATE TABLE link_month_expense(
    month_id INT NOT NULL,
    exp_id INT NOT NULL,
    PRIMARY KEY(month_id),
    FOREIGN KEY(month_id) REFERENCES table_months(month_id),
    FOREIGN KEY(exp_id) REFERENCES table_monthly_expense(exp_id)
);

DROP TABLE IF EXISTS link_month_modifier;
CREATE TABLE link_month_modifier(
    month_id INT NOT NULL,
    mod_id INT NOT NULL,
    PRIMARY KEY(month_id),
    FOREIGN KEY(month_id) REFERENCES table_months(month_id),
    FOREIGN KEY(mod_id) REFERENCES table_modifiers(mod_id)
);

DROP TABLE IF EXISTS link_month_postpone;
CREATE TABLE link_month_postpone(
    month_id INT NOT NULL,
    post_id INT  NOT NULL,
    PRIMARY KEY(month_id),
    FOREIGN KEY(month_id) REFERENCES table_months(month_id),
    FOREIGN KEY(post_id) REFERENCES table_postpone_expense(post_id)
);

DROP TABLE IF EXISTS link_month_actual;
CREATE TABLE link_month_actual(
    month_id INT NOT NULL,
    act_id INT NOT NULL,
    PRIMARY KEY(month_id),
    FOREIGN KEY(month_id) REFERENCES table_months(month_id),
    FOREIGN KEY(act_id) REFERENCES table_actual(act_id)
);