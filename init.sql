DROP TABLE IF EXISTS salaries;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- Create Departments Table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Create Employees Table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department_id INT,
    hire_date DATE,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Create Salaries Table
CREATE TABLE salaries (
    id SERIAL PRIMARY KEY,
    employee_id INT UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    pay_date DATE NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Insert data into Departments
INSERT INTO departments (name) VALUES
('Engineering'),
('Human Resources'),
('Sales'),
('Marketing');

-- Insert data into Employees
INSERT INTO employees (first_name, last_name, email, department_id, hire_date) VALUES
('Alice', 'Johnson', 'alice.j@example.com', 1, '2022-01-15'),
('Bob', 'Smith', 'bob.s@example.com', 1, '2021-11-20'),
('Charlie', 'Brown', 'charlie.b@example.com', 3, '2022-03-10'),
('Diana', 'Prince', 'diana.p@example.com', 4, '2023-06-01'),
('Eve', 'Adams', 'eve.a@example.com', 2, '2022-05-25');

-- Insert data into Salaries
INSERT INTO salaries (employee_id, amount, pay_date) VALUES
(1, 90000.00, '2024-07-28'),
(2, 85000.00, '2024-07-28'),
(3, 75000.00, '2024-07-28'),
(4, 78000.00, '2024-07-28'),
(5, 65000.00, '2024-07-28');

-- Grant read-only access to the default postgres user
GRANT USAGE ON SCHEMA public TO postgres;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;