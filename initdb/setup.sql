CREATE TABLE task_settings (
    task_name varchar(32),
    hour         float(16),
    n_people     int
);

CREATE TABLE employee_settings (
    first_name  varchar(8),
    last_name   varchar(8),
    hour        float(16)
);

INSERT INTO employee_settings
  VALUES
    ('John', 'Smith', 12.5),
    ('Michael', 'Thomas', 11.2),
    ('Eric', 'Crueger', 10.4),
    ('Melissa', 'Gupta', 11.4),
    ('Maries', 'Lucas', 13.0),
    ('Kayla', 'Palmer', 12.1);

INSERT INTO task_settings
  VALUES
    ('Purchasing', 12.8, 2),
    ('Logistics', 15.3, 3),
    ('Distribution', 11.8, 2),
    ('Promotion', 18.8, 3),
    ('Accounting', 11.9, 1);
