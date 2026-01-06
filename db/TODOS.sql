CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    due DATETIME NOT NULL,
    is_exam BOOLEAN DEFAULT FALSE,
    countdown_start INT DEFAULT NULL,
    silent_mode BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
